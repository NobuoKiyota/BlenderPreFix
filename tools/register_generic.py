import os
import sys
import json
import re

sys.path.append(os.path.dirname(__file__))
from catalog_manager import add_asset_to_catalog, encode_file_to_base64_uri

def parse_atomic_steps(md_path):
    steps = []
    if not os.path.exists(md_path):
        return steps
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if line.strip().startswith('| **#'):
            parts = [p.strip() for p in line.strip().split('|')[1:-1]]
            if len(parts) >= 4:
                steps.append({
                    "step": parts[0].replace('**', ''),
                    "action": parts[1],
                    "param": parts[2],
                    "why": parts[3]
                })
    return steps

def register_asset(
    asset_id,
    title,
    category,
    tags,
    description,
    glb_filename,
    cuts_info,
    audio_specs,
    steps_md_path,
    script_path,
    source_title,
    source_url
):
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    glb_full_path = os.path.join(assets_dir, glb_filename)
    data_uri = encode_file_to_base64_uri(glb_full_path)
    steps = parse_atomic_steps(steps_md_path)
    
    code_str = ""
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            code_str = f.read()

    asset = {
        "id": asset_id,
        "title": title,
        "category": category,
        "tags": tags,
        "thumb": cuts_info[0]["src"],
        "glbDataUri": data_uri,
        "cuts": cuts_info,
        "description": description,
        "atomicSteps": steps,
        "audioSpecs": audio_specs,
        "scriptPath": script_path,
        "codeSnippet": code_str,
        "source": {
            "title": source_title,
            "url": source_url
        }
    }
    add_asset_to_catalog(asset)

if __name__ == "__main__":
    print("Generic registration ready.")
