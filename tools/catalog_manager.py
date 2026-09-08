import os
import sys
import json
import base64
import re

CATALOG_HTML = "e:/BlenderPreFix/catalog/index.html"

def load_catalog_html():
    with open(CATALOG_HTML, "r", encoding="utf-8") as f:
        return f.read()

def save_catalog_html(content):
    with open(CATALOG_HTML, "w", encoding="utf-8") as f:
        f.write(content)

def encode_file_to_base64_uri(file_path, mime_type="model/gltf-binary"):
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def add_asset_to_catalog(asset_dict):
    html = load_catalog_html()
    match = re.search(r"const CATALOG_DATA = \[\s*", html)
    if not match:
        raise ValueError("Could not find const CATALOG_DATA in index.html")
    
    insert_pos = match.end()
    asset_json = json.dumps(asset_dict, ensure_ascii=False, indent=2)
    indented = "\n".join("      " + line for line in asset_json.split("\n")) + ",\n"
    
    new_html = html[:insert_pos] + "\n" + indented + html[insert_pos:]
    save_catalog_html(new_html)
    print(f"Successfully added asset {asset_dict['id']} to catalog!")

if __name__ == "__main__":
    print("Catalog manager ready.")
