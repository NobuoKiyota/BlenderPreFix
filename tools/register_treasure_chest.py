import os
import re
from catalog_manager import add_asset_to_catalog, encode_file_to_base64_uri

def parse_atomic_steps(md_path):
    steps = []
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

def main():
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    glb_path = os.path.join(assets_dir, "treasure_chest.glb")
    data_uri = encode_file_to_base64_uri(glb_path)
    
    steps = parse_atomic_steps("e:/BlenderPreFix/knowledge/treasure_chest_atomic_steps.md")
    
    with open("e:/BlenderPreFix/generators/gen_treasure_chest.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    asset = {
        "id": "treasure_chest",
        "title": "🪙 古代のダンジョン宝箱 (Treasure Chest)",
        "category": "ダンジョンプロップ / 木材＆鍛造鉄",
        "tags": ["Wood PBR", "Forged Iron", "Brass Padlock", "Rig Ready"],
        "thumb": "assets/treasure_chest_cut1.png",
        "glbDataUri": data_uri,
        "cuts": [
            { "label": "シネマティック全体像", "src": "assets/treasure_chest_cut1.png", "desc": "オーク木材と3連鉄バンド、真鍮南京錠の重厚な佇まい" },
            { "label": "ロック金具ディテール", "src": "assets/treasure_chest_cut2.png", "desc": "真鍮製ハスプとTorus製シャックル、リベットの立体感" },
            { "label": "45°木目天板俯瞰", "src": "assets/treasure_chest_cut3.png", "desc": "アーチ蓋に這う鉄バンドとプロシージャル木目の陰影" },
            { "label": "迫力ローアングル", "src": "assets/treasure_chest_cut4.png", "desc": "フロアから見上げるダンジョン内の存在感と重み" }
        ],
        "description": "ファンタジー・ダンジョン系ゲームの象徴的な宝箱。外装のオーク木材、頑丈な鍛造鉄バンド、リベット鋲、真鍮南京錠を精巧にモデリング。蓋の開閉ヒンジ軸を考慮した原点配置と、ゲームエンジン（Unity/UE）での物理衝撃音・鍵解除音に連動する3系統マテリアル分離を完備。",
        "atomicSteps": steps,
        "audioSpecs": [
            { "slot": "M_Chest_Wood", "surface": "Wood_Heavy", "tag": "Sound_Wood_Chest_Impact", "feature": "開閉時の重い木板鳴り、打撃・設置時の鈍い低音" },
            { "slot": "M_Chest_Iron", "surface": "Metal_Heavy", "tag": "Sound_Iron_Band_Hit", "feature": "剣撃・矢の弾き音、外枠鉄バンドの金属衝突響き" },
            { "slot": "M_Chest_Brass", "surface": "Metal_Light", "tag": "Sound_Lock_Latch_Click", "feature": "ピッキング成功音、南京錠の開錠ラッチ・ジングル" }
        ],
        "scriptPath": "generators/gen_treasure_chest.py",
        "codeSnippet": code_str,
        "source": {
            "title": "ゲームアセット自走学習 - ダンジョンプロップ #01 (Treasure Chest)",
            "url": "https://www.youtube.com/results?search_query=blender+treasure+chest+tutorial"
        }
    }
    
    add_asset_to_catalog(asset)

if __name__ == "__main__":
    main()
