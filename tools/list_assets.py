import re

with open("catalog/index.html", "r", encoding="utf-8") as f:
    content = f.read()

ids = re.findall(r'["\']?id["\']?\s*:\s*"([^"]+)"', content)
print(f"=== Registered Assets in Catalog: Total {len(ids)} ===")
for i, asset_id in enumerate(ids, 1):
    print(f"{i:02d}. {asset_id}")
