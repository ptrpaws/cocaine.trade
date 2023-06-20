import yaml
from pathlib import Path
from htmlmin import minify as minify_html

HTML_PAGE_TEMPLATE = Path("html_page_template.html").read_text()
FIRMWARE_PAGE_TEMPLATE = Path("firmware_page_template.html").read_text()

def generate_404_page():
    body = """
    <h2 class="monospace"><span class="link-red">404 ERROR:</span> <span class='link-white'>PAGE NOT FOUND</span></h2>
    <p class="monospace link-white">The document you are trying to access is highly classified.</p>
    <p class="monospace link-white">Access to this document requires special clearance.</p>
    <p class="monospace link-white">Please contact the site administrator for further instructions.</p>
    <a href="/" class='link link-gold monospace'>[RETURN TO HOMEPAGE]</a>
    """
    return HTML_PAGE_TEMPLATE.format(title="404 - Page Not Found", body=body)

def generate_main_page(models):
    model_links = "\n".join(
        f"<a href='{model.replace(' ', '_')}_firmware' class='link link-white'>{model}</a>"
        for model in models
    )
    return HTML_PAGE_TEMPLATE.format(title="Cocaine.Trade", body=build_body(model_links))

def generate_firmware_page(model, firmwares):
    def generate_table_rows():
        return "\n".join(
            f"<tr><td><a href='{fw['url']}' class='fw-link'>{fw['Incremental']}</a></td><td>{get_version(fw)}</td><td>{fw['VrShell_Version']}</td><td>{fw['Build_Date']}</td><td>{fw['Fingerprint']}</td></tr>"
            for fw in firmwares
        )

    table_rows = generate_table_rows()
    body = FIRMWARE_PAGE_TEMPLATE.format(model=model, table_rows=table_rows)
    return HTML_PAGE_TEMPLATE.format(title=f"{model} Firmware Archive", body=body)

def get_version(fw):
    incremental = int(fw['Incremental'])
    if incremental <= 15280600195700000:
        version = fw.get('SystemUtilities_Version')
    elif incremental >= 15849800124700000:
        version = fw.get('SystemUX_Version')
    else:
        raise ValueError(f"Unexpected version number: {incremental}")
    return version

def build_body(model_links):
    return f"""
        <h2 class="monospace"><span class="link-white">Welcome to </span><span class='link-red'>Cocaine</span><span class='link-blue'>.Trade</span></h2>
        <p class="author-notice monospace"><span class="link-white">by </span><a href="https://twitter.com/basti564" class='link link-gold'>basti564</a></p>
        <h3 class="monospace">Firmware</h3>
        {model_links}
        <h3 class="monospace">Blog</h3>
        <a href='https://blahaj.life' class='link link-white'>Blahaj Life</a>
    """

def generate_site(firmware_file):
    try:
        firmwares = yaml.safe_load(Path(firmware_file).read_text())
    except yaml.YAMLError as exc:
        print(exc)
        return

    models = list(set(fw['Model'] for fw in firmwares))

    model_order = ['Quest', 'Quest 2', 'Quest Pro']
    models.sort(key=lambda model: model_order.index(model) if model in model_order else len(model_order))

    for model in models:
        model_firmwares = [fw for fw in firmwares if fw['Model'] == model]
        Path(f"{model.replace(' ', '_')}_firmware.html").write_text(minify_html(generate_firmware_page(model, model_firmwares)))

    Path("index.html").write_text(minify_html(generate_main_page(models)))
    Path("404.html").write_text(minify_html(generate_404_page()))

generate_site('firmwares.yaml')