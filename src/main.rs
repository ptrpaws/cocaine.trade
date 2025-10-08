use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::num::ParseIntError;
use std::path::Path;
use tera::{Context, Tera};

const BUILD_DIR: &str = "build";
const STATIC_DIR: &str = "static";
const TEMPLATES_GLOB: &str = "templates/**/*.html";
const FIRMWARES_FILE: &str = "firmwares.yaml";
const KINDLE_FIRMWARES_FILE: &str = "kindle_firmwares.yaml";

const MODEL_ORDER: &[&str] = &["Quest", "Quest 2", "Quest Pro", "Quest 3", "Quest 3S"];
const KINDLE_MODEL_ORDER: &[&str] = &[
  "KS2", "KS", "CS", "PW6", "KT6", "KT5", "PW5", "KOA3", "KT4", "PW4", "KOA2", "KT3", "KOA",
  "PW3", "KV", "KT2", "PW2", "Legacy",
];


trait FirmwareData {
  fn model(&self) -> &str;
  fn incremental_as_u64(&self) -> Result<u64, ParseIntError>;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
struct Firmware {
  #[serde(rename = "Build_Date")]
  build_date: String,
  #[serde(rename = "Build_Date_UTC")]
  #[serde(default)]
  build_date_utc: String,
  #[serde(rename = "Codename")]
  #[serde(default)]
  codename: String,
  #[serde(rename = "Fingerprint")]
  fingerprint: String,
  #[serde(rename = "Incremental")]
  incremental: String,
  #[serde(rename = "Model")]
  model: String,
  #[serde(rename = "OS_Version")]
  #[serde(default)]
  os_version: String,
  #[serde(rename = "SystemUX_Version", default = "default_string")]
  system_ux_version: String,
  #[serde(rename = "SystemUtilities_Version", default = "default_string")]
  system_utilities_version: String,
  #[serde(rename = "VrShell_Version")]
  vr_shell_version: String,
  #[serde(rename = "name")]
  name: String,
  #[serde(rename = "sha256", default = "default_string")]
  sha256: String,
  #[serde(default)]
  version: String,
}

impl FirmwareData for Firmware {
  fn model(&self) -> &str {
    &self.model
  }
  fn incremental_as_u64(&self) -> Result<u64, ParseIntError> {
    self.incremental.parse()
  }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
struct KindleFirmware {
  #[serde(rename = "Incremental")]
  incremental: String,
  #[serde(rename = "Model")]
  model: String,
  #[serde(rename = "name")]
  name: String,
  #[serde(rename = "sha256", default = "default_string")]
  sha256: String,
  #[serde(default)]
  version: String,
}

impl FirmwareData for KindleFirmware {
  fn model(&self) -> &str {
    &self.model
  }
  fn incremental_as_u64(&self) -> Result<u64, ParseIntError> {
    self.incremental.parse()
  }
}

fn default_string() -> String {
  "N/A".to_string()
}

fn main() -> Result<(), Box<dyn Error>> {
  let build_path = Path::new(BUILD_DIR);
  setup_build_directory(build_path)?;

  generate_site(build_path)?;

  Ok(())
}

fn setup_build_directory(build_path: &Path) -> Result<(), Box<dyn Error>> {
  if build_path.exists() {
    fs::remove_dir_all(build_path)?;
  }
  fs::create_dir(build_path)?;
  println!("creating new build directory with static files...");

  let paths_to_copy: Vec<_> = fs::read_dir(STATIC_DIR)?
    .filter_map(Result::ok)
    .map(|entry| entry.path())
    .collect();

  let copy_options = fs_extra::dir::CopyOptions::new();
  fs_extra::copy_items(&paths_to_copy, build_path, &copy_options)?;

  Ok(())
}

fn generate_site(build_path: &Path) -> Result<(), Box<dyn Error>> {
  println!("loading and parsing data files...");
  let mut firmwares = load_firmwares_from_file::<Firmware>(FIRMWARES_FILE)?;
  println!("parsed {} meta firmwares", firmwares.len());
  let mut kindle_firmwares = load_firmwares_from_file::<KindleFirmware>(KINDLE_FIRMWARES_FILE)?;
  println!("parsed {} kindle firmwares", kindle_firmwares.len());

  process_meta_versions(&mut firmwares)?;
  process_kindle_versions(&mut kindle_firmwares);

  let models = get_and_sort_models(&firmwares, MODEL_ORDER);
  let kindle_models = get_and_sort_models(&kindle_firmwares, KINDLE_MODEL_ORDER);

  let tera = Tera::new(TEMPLATES_GLOB)?;

  generate_model_pages(&tera, build_path, &firmwares, "Meta", "firmware_page.html")?;
  generate_model_pages(&tera, build_path, &kindle_firmwares, "Kindle", "kindle_firmware_page.html")?;

  println!("generating core pages (index, 404, robots.txt)...");
  generate_core_pages(&tera, build_path, &models, &kindle_models)?;

  Ok(())
}

fn load_firmwares_from_file<T: DeserializeOwned>(filename: &str) -> Result<Vec<T>, Box<dyn Error>> {
  let content = fs::read_to_string(filename)
    .map_err(|e| format!("failed to read file '{}': {}", filename, e))?;
  let firmwares = serde_yml::from_str(&content)
    .map_err(|e| format!("failed to parse YAML from '{}': {}", filename, e))?;
  Ok(firmwares)
}

fn process_meta_versions(firmwares: &mut [Firmware]) -> Result<(), ParseIntError> {
  for fw in firmwares {
    let incremental_val = fw.incremental_as_u64()?;
    fw.version = if incremental_val <= 15280600195700000 {
      fw.system_utilities_version.clone()
    } else if incremental_val >= 15849800124700000 {
      fw.system_ux_version.clone()
    } else {
      "Unknown".to_string()
    };
  }
  Ok(())
}

fn process_kindle_versions(firmwares: &mut [KindleFirmware]) {
  for fw in firmwares {
    fw.version = fw.name.rsplit('_').next()
      .unwrap_or("N/A")
      .to_string();
  }
}

fn get_and_sort_models<T: FirmwareData>(firmwares: &[T], order: &[&str]) -> Vec<String> {
  let mut models: Vec<&str> = firmwares.iter().map(|fw| fw.model()).collect();
  models.sort_unstable();
  models.dedup();
  models.sort_by_key(|model| order.iter().position(|&r| r == *model).unwrap_or(order.len()));
  models.into_iter().map(String::from).collect()
}

fn generate_model_pages<T>(
  tera: &Tera,
  build_path: &Path,
  firmwares: &[T],
  log_prefix: &str,
  template_name: &str,
) -> Result<(), Box<dyn Error>>
where
  T: FirmwareData + Serialize + Clone,
{
  println!("generating {} firmware pages...", log_prefix);

  let mut firmwares_by_model: HashMap<String, Vec<T>> = HashMap::new();
  for fw in firmwares {
    firmwares_by_model.entry(fw.model().to_string()).or_default().push(fw.clone());
  }

  let minify_cfg = simple_minify_html::Cfg::default();

  for (model, mut model_firmwares) in firmwares_by_model {
    println!("generating page for {} ({} firmwares)...", model, model_firmwares.len());
    model_firmwares.sort_by_key(|fw| std::cmp::Reverse(fw.incremental_as_u64().unwrap_or(0)));

    let mut context = Context::new();
    context.insert("model", &model);
    context.insert("firmwares", &model_firmwares);

    let rendered_page = tera.render(template_name, &context)?;
    let title = format!("{} Firmware Update Archive", model);
    let final_html = render_template_with_base(tera, &title, &rendered_page)?;

    let minified_html = simple_minify_html::minify(final_html.as_bytes(), Some(minify_cfg.clone()));
    let filename = build_path.join(format!("{}_firmware.html", model.replace(' ', "_")));
    fs::write(filename, minified_html)?;
  }
  Ok(())
}

fn generate_core_pages(
  tera: &Tera,
  build_path: &Path,
  models: &[String],
  kindle_models: &[String],
) -> Result<(), Box<dyn Error>> {
  let minify_cfg = simple_minify_html::Cfg::default();

  let link_mapper = |m: &String| {
    format!("<a href='{}_firmware' class='link link-white'>{}</a>", m.replace(' ', "_"), m)
  };
  let meta_links: String = models.iter().map(link_mapper).collect::<Vec<_>>().join("\n");
  let kindle_links: String = kindle_models.iter().map(link_mapper).collect::<Vec<_>>().join("\n");

  let mut main_context = Context::new();
  main_context.insert("meta_links", &meta_links);
  main_context.insert("kindle_links", &kindle_links);

  let main_page_body = tera.render("index_body.html", &main_context)?;
  let final_main_page = render_template_with_base(tera, "Meta & Kindle Firmware Update Archive", &main_page_body)?;
  let minified_main_page = simple_minify_html::minify(final_main_page.as_bytes(), Some(minify_cfg.clone()));
  fs::write(build_path.join("index.html"), minified_main_page)?;

  let error_page_body = tera.render("404_body.html", &Context::new())?;
  let final_error_page = render_template_with_base(tera, "404 - Page Not Found", &error_page_body)?;
  let minified_error_page = simple_minify_html::minify(final_error_page.as_bytes(), Some(minify_cfg));
  fs::write(build_path.join("404.html"), minified_error_page)?;

  let robots_txt = generate_robots_txt(models, kindle_models);
  fs::write(build_path.join("robots.txt"), robots_txt)?;

  Ok(())
}

fn render_template_with_base(tera: &Tera, title: &str, body: &str) -> Result<String, tera::Error> {
  let mut context = Context::new();
  context.insert("title", title);
  context.insert("body", body);
  tera.render("html_page.html", &context)
}

fn generate_robots_txt(models: &[String], kindle_models: &[String]) -> String {
  let allowed_links: String = models.iter().chain(kindle_models.iter())
    .map(|m| format!("Allow: /{}_firmware", m.replace(' ', "_")))
    .collect::<Vec<_>>()
    .join("\n");
  format!("User-agent: *\nDisallow: /\nAllow: /$\n{}", allowed_links)
}