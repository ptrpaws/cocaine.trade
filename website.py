import yaml
from urllib.parse import quote
from pathlib import Path

def read_file(filename):
    return Path(filename).read_text()

HTML_PAGE_TEMPLATE = read_file("html_page_template.html")
FIRMWARE_PAGE_TEMPLATE = read_file("firmware_page_template.html")

def generate_main_page(models):
    model_links = "\n".join(f"<a href='{model.replace(' ', '_')}_firmware.html' class='link link-white'>{model}</a>" for model in models)
    return HTML_PAGE_TEMPLATE.format(title="Cocaine Trade", body=build_body(model_links))

def generate_firmware_page(model, firmwares):
    table_rows = generate_table_rows(firmwares, model)
    body = FIRMWARE_PAGE_TEMPLATE.format(model=model, table_rows=table_rows)
    return HTML_PAGE_TEMPLATE.format(title=f"{model} Firmware Updates", body=body)

def generate_table_rows(firmwares, model):
    return "\n".join(
        f"<tr><td><a href='{build_download_link(model, fw['name'])}'>{fw['Incremental']}</a></td><td>{fw['SystemUX_Version']}</td><td>{fw['VrShell_Version']}</td><td>{fw['Build_Date']}</td><td>{fw['Fingerprint']}</td></tr>"
        for fw in firmwares)

def generate_site(firmware_file):
    try:
        firmwares = yaml.safe_load(Path(firmware_file).read_text())
    except yaml.YAMLError as exc:
        print(exc)
        return

    models = {fw['Model'] for fw in firmwares}

    for model in models:
        model_firmwares = [fw for fw in firmwares if fw['Model'] == model]
        Path(f"{model.replace(' ', '_')}_firmware.html").write_text(generate_firmware_page(model, model_firmwares))

    Path("index.html").write_text(generate_main_page(models))

def build_body(model_links):
    return f"""
        <h2 class="monospace"><span class="link-white">Welcome to </span><span class='link-red'>Cocaine</span><span class='link-blue'>.Trade</span></h2>
        <p class="author-notice monospace"><span class="link-white">by </span><a href="https://twitter.com/basti564" class='link link-gold'>basti564</a></p>
        <h3 class="monospace">Firmware</h3>
        {model_links}
        <h3 class="monospace">Blog</h3>
        <a href='https://blahaj.life' class='link link-white'>Blahaj Life</a>
    """

def build_download_link(model, firmware_name):
    return f"https://aquavmcorp-my.sharepoint.com/personal/basti_aqualabs_xyz/_layouts/15/download.aspx?SourceUrl=/personal/basti_aqualabs_xyz/Documents/firmware/{quote(model)}/PTC/{firmware_name}.zip"

generate_site('firmwares.yaml')