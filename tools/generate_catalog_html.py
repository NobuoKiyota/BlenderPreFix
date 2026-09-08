import json
import base64
import re
from pathlib import Path

BASE_DIR = Path(r"e:\BlenderPreFix")
ASSETS_DIR = BASE_DIR / "catalog" / "assets"

with open(ASSETS_DIR / "kasahara_campfire.b64.txt", "r") as f:
    campfire_b64 = f.read().strip()

with open(ASSETS_DIR / "crystal_cluster.b64.txt", "r") as f:
    crystal_b64 = f.read().strip()

with open(ASSETS_DIR / "book_page_turn.b64.txt", "r") as f:
    book_b64 = f.read().strip()

def parse_atomic_markdown(md_path):
    content = Path(md_path).read_text(encoding="utf-8")
    steps = []
    # ## 001 - Title ...
    matches = re.split(r'##\s+(\d+)\s+-\s+([^\n]+)', content)
    for i in range(1, len(matches), 3):
        num = matches[i]
        title = matches[i+1].strip()
        body = matches[i+2].strip()
        
        how_m = re.search(r'-\s+\*\*操作\*\*:\s+([^\n]+)', body)
        why_m = re.search(r'-\s+\*\*Why\*\*:\s+([^\n]+)', body)
        
        how = how_m.group(1).strip() if how_m else ""
        why = why_m.group(1).strip() if why_m else ""
        
        steps.append({
            "num": num,
            "title": title,
            "how": how,
            "why": why
        })
    return steps

book_atomic = parse_atomic_markdown("knowledge/book_page_turn_atomic_steps.md")
campfire_atomic = parse_atomic_markdown("knowledge/kasahara_campfire_atomic_steps.md")
crystal_atomic = [
    {"num": "001", "title": "Bmesh初期化", "how": "bm = bmesh.new()", "why": "プログラマブルに六角柱頂点を動的配置するため"},
    {"num": "002", "title": "六角柱底面頂点生成", "how": "bm.verts.new(radius*cos(a), radius*sin(a), 0)", "why": "三方晶系/六方晶系の自然界の水晶の対称幾何学を形成"},
    {"num": "003", "title": "80%柱部押し出し", "how": "bm.verts.new(x*0.95, y*0.95, h*0.8)", "why": "柱状結晶の垂直伸びを再現"},
    {"num": "004", "title": "ピラミッド先端収束", "how": "bm.verts.new(offset_x, offset_y, h)", "why": "自然なオフセットを持つ先端錐体を形成"},
    {"num": "005", "title": "ファセット維持", "how": "poly.use_smooth = False", "why": "宝石・結晶特有のシャープなカット面反射を表現"},
    {"num": "006", "title": "物理屈折シェーダー設定", "how": "Principled BSDF > IOR: 1.544, Transmission: 0.92", "why": "石英ガラスの実測屈折率1.544による本物の光屈折"}
]

print(f"Loaded {len(book_atomic)} book steps, {len(campfire_atomic)} campfire steps.")

html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blender Skill & Procedural Catalog - 自走学習成果ポータル</title>
  <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
  <style>
    :root {{
      --bg-dark: #0f1115;
      --bg-panel: #161820;
      --bg-card: #1e212b;
      --bg-card-hover: #262a37;
      --accent: #ea7600; /* Blender Orange */
      --accent-hover: #ff8e24;
      --accent-cyan: #00d2ff;
      --accent-green: #10b981;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --border: #2b2f3e;
      --border-accent: rgba(234, 118, 0, 0.4);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-logo {{
      width: 32px;
      height: 32px;
      background: var(--accent);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 18px;
      color: #fff;
    }}
    .brand h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .badge {{
      background: rgba(234, 118, 0, 0.2);
      color: var(--accent);
      border: 1px solid var(--accent);
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 600;
    }}
    .badge-cyan {{
      background: rgba(0, 210, 255, 0.15);
      color: var(--accent-cyan);
      border: 1px solid var(--accent-cyan);
    }}
    .stats {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .main-container {{
      display: flex;
      flex: 1;
      overflow: hidden;
    }}
    /* Left Sidebar */
    .sidebar {{
      width: 330px;
      background: var(--bg-panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
    }}
    .search-box {{
      padding: 14px;
      border-bottom: 1px solid var(--border);
    }}
    .search-box input {{
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 8px 12px;
      border-radius: 6px;
      outline: none;
      font-size: 0.9rem;
    }}
    .item-list {{
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .item-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      gap: 12px;
    }}
    .item-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
      background: var(--bg-card-hover);
    }}
    .item-card.active {{
      border-color: var(--accent);
      background: rgba(234, 118, 0, 0.12);
    }}
    .item-thumb {{
      width: 72px;
      height: 72px;
      border-radius: 6px;
      object-fit: cover;
      background: #000;
    }}
    .item-meta {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .item-category {{
      font-size: 0.7rem;
      text-transform: uppercase;
      color: var(--accent-cyan);
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .item-title {{
      font-size: 0.92rem;
      font-weight: 600;
      line-height: 1.25;
      margin-bottom: 6px;
    }}
    .item-tags {{
      display: flex;
      gap: 6px;
      font-size: 0.72rem;
      color: var(--text-muted);
    }}

    /* Right Main Content */
    .content-area {{
      flex: 1;
      overflow-y: auto;
      padding: 24px 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .detail-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .detail-title h2 {{
      font-size: 1.65rem;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .detail-title p {{
      color: var(--text-muted);
      font-size: 0.95rem;
    }}

    /* Visual Grid: 3D Viewer & Multi-Cut Gallery */
    .visual-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      height: 440px;
    }}
    .viewer-panel {{
      background: #090a0f;
      border: 1px solid var(--border);
      border-radius: 10px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .panel-header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 14px;
      background: rgba(20, 22, 30, 0.9);
      border-bottom: 1px solid var(--border);
      font-size: 0.8rem;
      font-weight: 600;
      z-index: 10;
    }}
    .viewer-body {{
      flex: 1;
      position: relative;
      width: 100%;
      height: 100%;
    }}
    model-viewer {{
      width: 100%;
      height: 100%;
      --poster-color: transparent;
      outline: none;
    }}

    /* Multi-Cut Render Gallery */
    .gallery-panel {{
      background: #090a0f;
      border: 1px solid var(--border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .main-render-view {{
      flex: 1;
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #000;
    }}
    .main-render-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.2s;
    }}
    .cut-label-overlay {{
      position: absolute;
      bottom: 10px;
      left: 12px;
      background: rgba(0,0,0,0.75);
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.78rem;
      color: #fff;
    }}
    .thumbnails-strip {{
      display: flex;
      gap: 8px;
      padding: 10px 12px;
      background: var(--bg-panel);
      border-top: 1px solid var(--border);
      overflow-x: auto;
    }}
    .thumb-btn {{
      border: 2px solid transparent;
      border-radius: 6px;
      cursor: pointer;
      overflow: hidden;
      width: 72px;
      height: 48px;
      flex-shrink: 0;
      background: #000;
      transition: all 0.2s;
      position: relative;
    }}
    .thumb-btn img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .thumb-btn.active {{
      border-color: var(--accent);
      transform: scale(1.05);
    }}

    /* Section Cards */
    .section-card {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 22px;
    }}
    .section-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Atomic Step-by-Step Table */
    .atomic-step-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 8px;
    }}
    .atomic-step-row {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 6px;
      transition: all 0.2s;
    }}
    .atomic-step-row:hover {{
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
    }}
    .step-num-col {{
      padding: 12px 14px;
      width: 70px;
      font-family: "Fira Code", monospace;
      font-weight: 700;
      font-size: 0.85rem;
      color: var(--accent);
      border-radius: 6px 0 0 6px;
      border-left: 3px solid var(--accent);
      vertical-align: top;
    }}
    .step-how-col {{
      padding: 12px 14px;
      width: 45%;
      font-size: 0.88rem;
      line-height: 1.5;
      vertical-align: top;
    }}
    .step-how-title {{
      font-weight: 700;
      color: #fff;
      margin-bottom: 4px;
    }}
    .step-how-cmd {{
      font-family: "Fira Code", Consolas, monospace;
      background: rgba(0,0,0,0.35);
      border: 1px solid var(--border);
      padding: 4px 8px;
      border-radius: 4px;
      color: var(--accent-cyan);
      font-size: 0.82rem;
      display: inline-block;
      margin-top: 2px;
    }}
    .step-why-col {{
      padding: 12px 14px;
      font-size: 0.86rem;
      line-height: 1.5;
      color: #cfd3dc;
      border-radius: 0 6px 6px 0;
      vertical-align: top;
      background: rgba(234, 118, 0, 0.03);
    }}
    .why-tag {{
      display: inline-block;
      font-size: 0.72rem;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 4px;
    }}

    /* Audio Table */
    .audio-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
      margin-top: 10px;
    }}
    .audio-table th, .audio-table td {{
      border: 1px solid var(--border);
      padding: 10px 14px;
      text-align: left;
    }}
    .audio-table th {{
      background: var(--bg-card);
      color: var(--accent-cyan);
    }}

    /* Code Block */
    .code-container {{
      position: relative;
      background: #090a0d;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }}
    .code-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 14px;
      background: #14161d;
      border-bottom: 1px solid var(--border);
      font-size: 0.8rem;
      color: var(--text-muted);
    }}
    .copy-btn {{
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .copy-btn:hover {{
      background: var(--accent-hover);
    }}
    pre code {{
      display: block;
      padding: 14px;
      font-family: "Fira Code", Consolas, Monaco, monospace;
      font-size: 0.82rem;
      line-height: 1.5;
      color: #e2e8f0;
      overflow-x: auto;
      max-height: 260px;
    }}

    .source-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--accent-cyan);
      text-decoration: none;
      font-size: 0.88rem;
      margin-top: 12px;
      font-weight: 600;
    }}
    .source-link:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-logo">B</div>
      <div>
        <h1>Blender Procedural Knowledge & VFX Vault</h1>
      </div>
      <span class="badge">自走学習成果ポータル</span>
    </div>
    <div class="stats" id="catalog-stats">
      登録スキル: 4件 | Blender 5.2.1 LTS | 最小単位全工程完備
    </div>
  </header>

  <div class="main-container">
    <div class="sidebar">
      <div class="search-box">
        <input type="text" id="search-input" placeholder="スキル・エフェクトを検索..." oninput="filterItems()">
      </div>
      <div class="item-list" id="item-list"></div>
    </div>

    <div class="content-area" id="detail-view"></div>
  </div>

  <script>
    const BOOK_ATOMIC = {json.dumps(book_atomic, ensure_ascii=False)};
    const CAMPFIRE_ATOMIC = {json.dumps(campfire_atomic, ensure_ascii=False)};
    const CRYSTAL_ATOMIC = {json.dumps(crystal_atomic, ensure_ascii=False)};

    const CATALOG_DATA = [
      {{
        id: "book_page_turn",
        title: "本を開いてページをめくるアニメーション (Book Page Turn)",
        category: "アニメーション ＆ リグ / オブジェクト",
        tags: ["Simple Deform (Bend)", "Hook Modifier", "Hinge Pivot", "Multi-Page Offset"],
        thumb: "assets/book_page_turn_cut1.png",
        glbBase64: "data:model/gltf-binary;base64,{book_b64}",
        cuts: [
          {{ label: "🎬 Cut 1: 正面斜めシネマティック（しなるめくりページ全体像）", src: "assets/book_page_turn_cut1.png" }},
          {{ label: "📖 Cut 2: ページのしなり曲面クローズアップ（美しいアーチ湾曲）", src: "assets/book_page_turn_cut2.png" }},
          {{ label: "📐 Cut 3: 45°斜め上俯瞰（左右ページブロックと本全体の構造）", src: "assets/book_page_turn_cut3.png" }},
          {{ label: "🔍 Cut 4: 綴じ目と背表紙のローアングル（ヒンジ幾何学）", src: "assets/book_page_turn_cut4.png" }}
        ],
        summary: "Blender Made Easy様のチュートリアルを完全コード化。ハードカバーの開閉ヒンジリグ、厚みのある用紙ブロック、Simple Deform (Bend) と Hook による滑らかで有機的な紙のしなりアニメーションを一発生成。",
        source: {{
          title: "Blender Made Easy: Blender Tutorial - Book Opening Animation",
          url: "https://www.youtube.com/watch?v=geyC6FfMFf8"
        }},
        atomicSteps: BOOK_ATOMIC,
        soundMapping: [
          {{ slot: "Book_Cover_Leather_Mat", surface: "Leather", audio: "Sound_Book_Close_Thud", event: "本の開閉・バタンと閉じる重厚な革接触音" }},
          {{ slot: "Book_Page_Paper_Mat", surface: "Paper", audio: "Sound_Page_Turn_Whoosh", event: "ページが風をはらんでめくれるパサッという紙音" }},
          {{ slot: "Book_Pages_Block_Mat", surface: "PaperBlock", audio: "Sound_Page_Riffle", event: "本の小口をパラパラ弾く連続紙擦れ音" }}
        ],
        scriptPath: "generators/gen_book_page_turn.py",
        codeSnippet: `import bpy, sys\\n# Blender 5.2/3.6 のスクリプトエディタで実行するだけで一発生成\\nexec(open(r"e:/BlenderPreFix/generators/gen_book_page_turn.py", encoding="utf-8").read())`
      }},
      {{
        id: "kasahara_campfire",
        title: "リアル焚き火シミュレーション ＆ シェーダー (MantaFlow 火炎)",
        category: "VFX / 物理シミュレーション",
        tags: ["MantaFlow", "Principled Volume", "Heat Attribute", "Driver Animation"],
        thumb: "assets/kasahara_campfire_cut1.png",
        glbBase64: "data:model/gltf-binary;base64,{campfire_b64}",
        cuts: [
          {{ label: "🎬 Cut 1: 正面シネマティック全体像", src: "assets/kasahara_campfire_cut1.png" }},
          {{ label: "🔥 Cut 2: 炎クローズアップ（有機的ゆらめき）", src: "assets/kasahara_campfire_cut2.png" }},
          {{ label: "📐 Cut 3: 45°斜め上俯瞰（薪のクロス構造）", src: "assets/kasahara_campfire_cut3.png" }},
          {{ label: "🌟 Cut 4: ローアングル・ドラマチック", src: "assets/kasahara_campfire_cut4.png" }}
        ],
        summary: "カサハラCG様の焚き火チュートリアルを完全コード化。MantaFlow火炎シミュレーション、ヒート属性連動ColorRamp、#frameドライバによる有機的な炎の揺らめき、薪の配置からCyclesレンダリングまでの全行程を一発構築。",
        source: {{
          title: "カサハラ CG: 【Blender】初めての炎！【焚き火篇】リアルな炎を簡単に作れます！",
          url: "https://www.youtube.com/watch?v=lodqjYDXIxk"
        }},
        atomicSteps: CAMPFIRE_ATOMIC,
        soundMapping: [
          {{ slot: "Kasahara_Fire_Volume_Mat", surface: "Fire", audio: "Sound_Campfire_Loop", event: "リアル焚き火環境ループ音 (Wwise/ADX2)" }},
          {{ slot: "Charred_Wood_Mat", surface: "Wood", audio: "Footstep_Wood_Charred", event: "炭化薪の接触音・足音" }},
          {{ slot: "Ember_Spark_Mat", surface: "Fire", audio: "Sound_Fire_Crackle", event: "火の粉のパチパチ爆ぜ音 (One-shot)" }}
        ],
        scriptPath: "generators/gen_kasahara_campfire_v2.py",
        codeSnippet: `import bpy, sys\\n# Blender 5.2/3.6 のスクリプトエディタで実行するだけで一発生成\\nexec(open(r"e:/BlenderPreFix/generators/gen_kasahara_campfire_v2.py", encoding="utf-8").read())`
      }},
      {{
        id: "crystal_cluster",
        title: "プロシージャル水晶クラスタ (Crystal Cluster)",
        category: "3Dオブジェクト / 鉱石",
        tags: ["Procedural Bmesh", "IOR 1.54", "Transmission", "Rock Base"],
        thumb: "assets/crystal_cluster.png",
        glbBase64: "data:model/gltf-binary;base64,{crystal_b64}",
        cuts: [
          {{ label: "💎 結晶クラスタ全体ビュー", src: "assets/crystal_cluster.png" }}
        ],
        summary: "Bmeshによる六角柱ピラミッド結晶のプロシージャル生成、ランダムクラスタリング、岩石台座と物理屈折シェーダーを備えた鉱石アセット。",
        source: {{
          title: "Blender Procedural Crystal Cluster Tutorial (Sacoche Ito & Mdesign 技法統合)",
          url: "https://www.youtube.com/results?search_query=blender+procedural+crystals"
        }},
        atomicSteps: CRYSTAL_ATOMIC,
        soundMapping: [
          {{ slot: "Crystal_Gem_Mat", surface: "Crystal", audio: "Footstep_Glass", event: "高硬度クリスタル接触音・硬質反射" }},
          {{ slot: "Base_Rock_Mat", surface: "Stone", audio: "Footstep_Stone", event: "硬い岩石の足音・破砕音" }}
        ],
        scriptPath: "generators/gen_crystal_cluster.py",
        codeSnippet: `import bpy, sys\\n# Blender 5.2/3.6 のスクリプトエディタで実行するだけで一発生成\\nexec(open(r"e:/BlenderPreFix/generators/gen_crystal_cluster.py", encoding="utf-8").read())`
      }}
    ];

    let currentItem = CATALOG_DATA[0];
    let currentCutIdx = 0;

    function renderList(items) {{
      const listContainer = document.getElementById("item-list");
      listContainer.innerHTML = "";
      items.forEach(item => {{
        const card = document.createElement("div");
        card.className = `item-card ${{item.id === currentItem.id ? 'active' : ''}}`;
        card.onclick = () => selectItem(item);
        card.innerHTML = `
          <img class="item-thumb" src="${{item.thumb}}" alt="${{item.title}}">
          <div class="item-meta">
            <div class="item-category">${{item.category}}</div>
            <div class="item-title">${{item.title}}</div>
            <div class="item-tags">${{item.tags.join(" • ")}}</div>
          </div>
        `;
        listContainer.appendChild(card);
      }});
    }}

    function selectItem(item) {{
      currentItem = item;
      currentCutIdx = 0;
      renderList(CATALOG_DATA);
      renderDetail(item);
    }}

    function switchCut(idx) {{
      currentCutIdx = idx;
      const cut = currentItem.cuts[idx];
      document.getElementById("main-render-img").src = cut.src;
      document.getElementById("cut-label").innerText = cut.label;
      
      document.querySelectorAll(".thumb-btn").forEach((btn, i) => {{
        btn.classList.toggle("active", i === idx);
      }});
    }}

    function renderDetail(item) {{
      const detailContainer = document.getElementById("detail-view");
      
      const soundRows = item.soundMapping.map(s => `
        <tr>
          <td><code>${{s.slot}}</code></td>
          <td><span class="badge badge-cyan">${{s.surface}}</span></td>
          <td><code>${{s.audio}}</code></td>
          <td>${{s.event}}</td>
        </tr>
      `).join("");

      const stepRows = (item.atomicSteps || []).map(st => `
        <tr class="atomic-step-row">
          <td class="step-num-col">#${{st.num}}</td>
          <td class="step-how-col">
            <div class="step-how-title">${{st.title}}</div>
            <div class="step-how-cmd">${{st.how}}</div>
          </td>
          <td class="step-why-col">
            <div class="why-tag">💡 なぜこの操作を行うのか (Why)</div>
            <div>${{st.why}}</div>
          </td>
        </tr>
      `).join("");

      const cutThumbs = item.cuts.map((c, i) => `
        <button class="thumb-btn ${{i === 0 ? 'active' : ''}}" onclick="switchCut(${{i}})">
          <img src="${{c.src}}" alt="${{c.label}}">
        </button>
      `).join("");

      detailContainer.innerHTML = `
        <div class="detail-header">
          <div class="detail-title">
            <h2>${{item.title}}</h2>
            <p>${{item.summary}}</p>
          </div>
          <span class="badge">${{item.category}}</span>
        </div>

        <div class="visual-grid">
          <div class="viewer-panel">
            <div class="panel-header-bar">
              <span>🎮 3D インタラクティブ (ドラッグ回転 / ホイール拡縮)</span>
              <span class="badge badge-cyan" style="font-size:0.7rem;">CORSフリー</span>
            </div>
            <div class="viewer-body">
              <model-viewer 
                src="${{item.glbBase64}}" 
                alt="${{item.title}}" 
                auto-rotate 
                camera-controls 
                shadow-intensity="1.5" 
                exposure="1.1"
                camera-target="0m 0.3m 0m">
              </model-viewer>
            </div>
          </div>

          <div class="gallery-panel">
            <div class="panel-header-bar">
              <span>📷 Cycles 高画質レンダリング (マルチカット切り替え)</span>
              <span class="badge" style="font-size:0.7rem;">全 ${{item.cuts.length}} カット</span>
            </div>
            <div class="main-render-view">
              <img id="main-render-img" class="main-render-img" src="${{item.cuts[0].src}}" alt="${{item.title}}">
              <div id="cut-label" class="cut-label-overlay">${{item.cuts[0].label}}</div>
            </div>
            <div class="thumbnails-strip">
              ${{cutThumbs}}
            </div>
          </div>
        </div>

        <!-- Atomic Step-by-Step Analysis (Most Important) -->
        <div class="section-card">
          <div class="section-title">
            <span>🔬 最小単位・全行程レシピ (Atomic Step-by-Step)</span>
            <span class="badge" style="font-size:0.75rem;">全 ${(item.atomicSteps || []).length} 手番</span>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 16px;">
            キー入力・ショートカット・寸法入力レベルの最小単位で全行程を完全分解。1手ごとの操作（How）と、なぜその数値や操作を行うのか（Why）を事細かに記録しています。
          </p>
          <table class="atomic-step-table">
            <tbody>
              ${{stepRows}}
            </tbody>
          </table>
          <a class="source-link" href="${{item.source.url}}" target="_blank">
            🔗 一次情報チュートリアル元動画: ${{item.source.title}} ↗
          </a>
        </div>

        <!-- Audio & Surface ID Section -->
        <div class="section-card">
          <div class="section-title">🔊 ゲームエンジン ＆ サウンド連動仕様 (Wwise / CRI / Unity / UE)</div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
            各マテリアルスロットはゲームエンジン内の Surface ID に直接マッピングされ、足音・衝突音・環境音イベントを即座に紐付け可能です。
          </p>
          <table class="audio-table">
            <thead>
              <tr>
                <th>マテリアルスロット</th>
                <th>Surface ID</th>
                <th>オーディオタグ</th>
                <th>連動サウンド機能</th>
              </tr>
            </thead>
            <tbody>
              ${{soundRows}}
            </tbody>
          </table>
        </div>

        <!-- One-Click Code Section -->
        <div class="section-card">
          <div class="section-title">⚡ 一発生成コード (One-Click Python Generator)</div>
          <div class="code-container">
            <div class="code-header">
              <span>実行ファイル: ${{item.scriptPath}} (Blender 5.2.1 LTS)</span>
              <button class="copy-btn" onclick="copyCode()">📋 コードをコピー</button>
            </div>
            <pre><code id="code-snippet">${{item.codeSnippet}}</code></pre>
          </div>
        </div>
      `;
    }}

    function copyCode() {{
      const code = document.getElementById("code-snippet").innerText;
      navigator.clipboard.writeText(code).then(() => {{
        const btn = document.querySelector(".copy-btn");
        const orig = btn.innerText;
        btn.innerText = "✅ コピー完了！";
        setTimeout(() => btn.innerText = orig, 2000);
      }});
    }}

    function filterItems() {{
      const q = document.getElementById("search-input").value.toLowerCase();
      const filtered = CATALOG_DATA.filter(item => 
        item.title.toLowerCase().includes(q) || 
        item.category.toLowerCase().includes(q) || 
        item.tags.some(t => t.toLowerCase().includes(q))
      );
      renderList(filtered);
    }}

    renderList(CATALOG_DATA);
    renderDetail(currentItem);
  </script>
</body>
</html>
'''

output_path = BASE_DIR / "catalog" / "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Successfully generated ultimate atomic catalog at: {output_path}")
print(f"HTML File Size: {output_path.stat().st_size / 1024:.1f} KB")
