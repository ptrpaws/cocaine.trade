import yaml
from urllib.parse import quote

SORTING_SCRIPT = """
<script>
function sortTable() {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("firmwareTable");
  switching = true;
  dir = "asc";

  while (switching) {
    switching = false;
    rows = table.rows;

    for (i = 1; i < (rows.length - 1); i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[0];
      y = rows[i + 1].getElementsByTagName("TD")[0];

      if (dir === "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      } else if (dir === "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      }
    }

    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount === 0 && dir === "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }

  // Reset the arrow classes
  var ascArrow = document.getElementById("ascArrow");
  var descArrow = document.getElementById("descArrow");
  ascArrow.style.display = (dir === "asc") ? "" : "none";
  descArrow.style.display = (dir === "desc") ? "" : "none";
}
</script>
"""

HTML_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="main">
        {body}
    </div>
    {sorting_script}
</body>
</html>
"""

def generate_firmware_page(model, firmwares):
    body = f"""
        <h2>{model} Firmware Updates</h2>
        <div class='table-container'>
            <table id="firmwareTable">
                <thead>
                    <tr>
                        <th onclick="sortTable()"><span class="sortable">Incremental <span id="ascArrow">&#x25B2;</span><span id="descArrow" style="display: none;">&#x25BC;</span></span></th>
                        <th>Version</th>
                        <th>Runtime Version</th>
                        <th>Fingerprint</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(firmwares, model)}
                </tbody>
            </table>
        </div>
        <a class="back-button" href='/'>[Back to main]</a>
    """
    return HTML_PAGE_TEMPLATE.format(title=f"{model} Firmware Updates", body=body, sorting_script=SORTING_SCRIPT)

def generate_main_page(models):
    model_links = "\n".join(f"<a href='{model.replace(' ', '_')}_firmware.html' class='link link-white'>{model}</a>" for model in models)
    body = f"""
        <h2 class="monospace"><span class="link-white">Welcome to </span><span class='link-red'>Cocaine</span><span class='link-blue'>.Trade</span></h2>
        <p class="author-notice monospace"><span class="link-white">by </span><a href="https://twitter.com/basti564" class='link link-gold'>basti564</a></p>
        <h3 class="monospace">Firmware</h3>
        {model_links}
        <h3 class="monospace">Blog</h3>
        <a href='https://blahaj.life' class='link link-white'>Blahaj Life</a>
    """
    return HTML_PAGE_TEMPLATE.format(title="Cocaine Trade", body=body, sorting_script="")

def generate_table_rows(firmwares, model):
    rows = ""
    for fw in firmwares:
        download_link = f"https://aquavmcorp-my.sharepoint.com/personal/basti_aqualabs_xyz/_layouts/15/download.aspx?SourceUrl=/personal/basti_aqualabs_xyz/Documents/firmware/{quote(model)}/PTC/{fw['name']}.zip"
        rows += f"<tr><td><a href='{download_link}'>{fw['Incremental']}</a></td><td>{fw['SystemUX_Version']}</td><td>{fw['VrShell_Version']}</td><td>{fw['Fingerprint']}</td></tr>\n"
    return rows

def generate_site(firmware_file):
    try:
        with open(firmware_file, 'r') as stream:
            firmwares = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        return

    models = set(fw['Model'] for fw in firmwares)

    for model in models:
        model_firmwares = [fw for fw in firmwares if fw['Model'] == model]
        page_content = generate_firmware_page(model, model_firmwares)
        with open(f"{model.replace(' ', '_')}_firmware.html", "w") as f:
            f.write(page_content)

    main_page_content = generate_main_page(models)
    with open("index.html", "w") as f:
        f.write(main_page_content)

generate_site('firmwares.yaml')