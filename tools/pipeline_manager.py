import json
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_INDEX = BASE_DIR / "catalog" / "index.html"
ASSETS_DIR = BASE_DIR / "catalog" / "assets"

def register_to_catalog(item_data: dict):
    """
    catalog/index.html 内の CATALOG_DATA 配列に新しいアイテムを挿入・更新する
    """
    if not CATALOG_INDEX.exists():
        print(f"Catalog index not found: {CATALOG_INDEX}")
        return False
        
    content = CATALOG_INDEX.read_text(encoding="utf-8")
    
    # 簡易的なパースと挿入
    marker = "const CATALOG_DATA = ["
    if marker not in content:
        print("Marker not found in index.html")
        return False
        
    start_pos = content.find(marker) + len(marker)
    # JSON 文字列を作成
    item_json_str = "\n      " + json.dumps(item_data, ensure_ascii=False, indent=6).replace("\n", "\n    ") + ","
    
    # 重複チェック（IDで存在確認）
    if f'"id": "{item_data["id"]}"' in content:
        print(f"Item {item_data['id']} already exists in catalog. Skipping insertion.")
        return True
        
    new_content = content[:start_pos] + item_json_str + content[start_pos:]
    CATALOG_INDEX.write_text(new_content, encoding="utf-8")
    print(f"Registered '{item_data['title']}' to catalog successfully!")
    return True

if __name__ == "__main__":
    print("Pipeline Manager ready.")
