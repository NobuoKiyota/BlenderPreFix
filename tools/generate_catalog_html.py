import json
import base64
from pathlib import Path

BASE_DIR = Path(r"e:\BlenderPreFix")
ASSETS_DIR = BASE_DIR / "catalog" / "assets"

# Base64 読み込み
with open(ASSETS_DIR / "kasahara_campfire.b64.txt", "r") as f:
    campfire_b64 = f.read().strip()

with open(ASSETS_DIR / "crystal_cluster.b64.txt", "r") as f:
    crystal_b64 = f.read().strip()

# 全行程詳細解説 Markdown / HTML
kasahara_steps = [
    {
        "step": 1,
        "title": "球体エミッターの追加 ＆ クイック煙の適用",
        "time": "00:23 - 00:58",
        "how": "初期オブジェクトを削除後、Shift+A で『UV球』を追加し Sキーで 0.4 に縮小。オブジェクトメニュー ＞ クイックエフェクト ＞『クイック煙』を実行。",
        "why": "【球体の理由】焚き火の火床はある程度の体積を持った熱源であるため、全方位に均等に燃焼ガスを噴出させるのに最適。【0.4縮小の理由】デフォルトの直径2mだと大爆発になるため、キャンプ用焚き火の火床サイズ（直径約40cm）に合わせる。【クイック煙の理由】ドメイン（計算領域外枠）と初期ボリュームマテリアルが一発で自動生成され、面倒な初期設定を大幅短縮できる。"
    },
    {
        "step": 2,
        "title": "乱流フォースフィールド（Turbulence）の付加",
        "time": "00:58 - 01:15",
        "how": "Shift+A ＞ フォースフィールド ＞『乱流』を追加。物理演算プロパティで 強さ: 0.4、ノイズ量: 0.4 に設定。",
        "why": "【無風の弊害】フォースが無いと熱気流が真上に垂直上昇するだけの不自然な円柱炎になる。【乱流の理由】一定方向の『風』ではなく、空間全域でランダムな渦を発生させる『乱流』を使うことで、炎の先端がチラチラと舞い上がる自然なゆらめきが生まれる。【0.4の理由】1.0以上だと吹き散らされて形が崩れ、0.1だと直線的すぎる。0.4が穏やかな焚き火の黄金比。"
    },
    {
        "step": 3,
        "title": "発生源（フロー）の詳細設定（火炎化 ＆ Cloudsテクスチャ）",
        "time": "01:15 - 02:10",
        "how": "球体のフロータイプを『火炎』に変更。燃料: 2.0、表面からの発生距離: 1.0。テクスチャにチェックを入れ『クラウド（Clouds）』テクスチャ（サイズ: 0.1, コントラスト: 5.0）を割り当て。",
        "why": "【火炎化の理由】初期値の煙を止め、純粋な燃焼ガスシミュレーションに集中。【燃料2.0の理由】燃焼持続時間を伸ばし、炎が勢いよく上部まで伸びるようにする。【表面距離1.0の理由】球体内部〜周囲1mの空間からガスを発生させ火の根元に厚みを出す。【Cloudsテクスチャ（超重要）】ツルッとした球体型の炎を打破するため、高コントラストなノイズで『ガスが出る場所・出ない場所』の激しいムラを作り、幾筋にも千切れて立ち上る有機的な炎の形状を生み出す。"
    },
    {
        "step": 4,
        "title": "ドメインの解像度 ＆ 物理挙動チューニング",
        "time": "02:10 - 03:01",
        "how": "ドメインの『分割の解像度』を 128 に設定。『適応ドメイン』にチェック。火炎タブで『渦度』を 0.1、『反応速度』を 1.0 に設定。",
        "why": "【解像度128の理由】ボクセルサイズを微細化し、炎のブロック状モザイク感を解消して滑らかな流体ディテールを再現。【適応ドメインの理由】炎が存在する空間のみバウンディングボックスを自動伸縮させ、無駄な空間計算を省きメモリ消費とベイク時間を大幅削減。【渦度0.1・反応速度1.0】激しい爆発ではなく、焚き火らしいゆったりとした渦巻き速度に抑える。"
    },
    {
        "step": 5,
        "title": "シミュレーションデータのベイク（事前計算）",
        "time": "03:01 - 03:50",
        "how": "キャッシュタイプを『モジュール』、リジューム可にチェック、終了フレームを 200 に設定し『データをベイク』を実行。",
        "why": "【ベイクの必要性】流体計算は超高負荷なため、リアルタイム再生ではコマ落ちし正確な形状確認ができない。ディスクにフレームごとの物理データを固定保存することで、レンダリング時の安定性を担保。【リジューム可】途中でクラッシュしても中断したフレームから再開できる。"
    },
    {
        "step": 6,
        "title": "背景暗闇化 ＆ Cycles パストレーシング設定",
        "time": "03:50 - 04:13",
        "how": "ワールドカラーを完全な黒（RGB 0,0,0）に設定。レンダーエンジンを『Cycles』、デバイス『GPU』、サンプル数『64』、デノイズON。",
        "why": "【黒背景の理由】炎は自発光オブジェクトであるため、周囲が明るいと発光感が白飛び・減衰する。暗闇にすることで鮮烈な炎のグラデーションを際立たせる。【Cyclesの理由】Eeveeでは難しい『炎の光が薪や地面を物理的に照らし出す間接光（GI）』をパストレーシングで忠実に計算するため。"
    },
    {
        "step": 7,
        "title": "Principled Volume 核心シェーダーの構築（heat属性 ＆ #frame）",
        "time": "04:13 - 07:17",
        "how": "ドメインのマテリアルで、Attributeノード（name: 'heat'）を追加。ColorRamp（黒→白→濃灰）× 50.0 に、Mapping（Z位置に #frame ドライバ）連動の Noise Texture（Scale 8, Detail 9.2, Distort 1）を乗算合成して放射強度へ接続。別ColorRamp（橙→黄）を放射色へ接続。Densityは0.0。",
        "why": "【heat属性の役割】シミュレーション内部の熱量データ（0〜1）を取り出し、温度が高い中心部を強く発光させる。【濃灰を挟む理由】白の右に濃灰を置くことで、炎の芯がピーク発光し、表面に向かって滑らかに透明へフェードアウトする。【乗算50の理由】CyclesのHDR空間で十分な発光強度を確保。【#frameドライバ（神技法）】シミュレーションの動きに加え、シェーダー内部のノイズがZ軸方向に高速スクロールすることで、炎の内部にチラチラと動く超微細な繊維ディテールが付加される。"
    },
    {
        "step": 8,
        "title": "薪（土台）の配置 ＆ 炎中心ポイントライト ＆ 最終仕上げ",
        "time": "07:17 - 10:48",
        "how": "炎の足元に薪を井桁・円錐状にクロス配置。炎の中心やや高めに暖色ポイントライト（500〜850W）を配置。ドメインの Density を 0.0 にして煙を消去。",
        "why": "【ポイントライト追加の理由】ボリューム自体の発光はCyclesでノイズ（ファイアフライ）が出やすく照り返し計算が重い。中心にライトを置くことで、薪の表面をクリアかつ高速に照らしドラマチックな陰影を作る。【Density 0.0の理由】微量に発生する黒煙（煤）を完全に透明化し、透き通るような美しい炎の光だけを抽出するため。"
    }
]

html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blender Skill & Procedural Catalog - 自走学習成果ポータル</title>
  <!-- Google model-viewer for 3D GLB preview -->
  <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
  <style>
    :root {{
      --bg-dark: #101216;
      --bg-panel: #171922;
      --bg-card: #202330;
      --bg-card-hover: #282c3c;
      --accent: #ea7600; /* Blender Orange */
      --accent-hover: #ff8e24;
      --accent-cyan: #00d2ff;
      --accent-green: #10b981;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --border: #2d3142;
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
      width: 340px;
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

    /* Step-by-Step Deep Analysis Table/Cards */
    .step-list {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .step-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      transition: border-color 0.2s;
    }}
    .step-card:hover {{
      border-color: rgba(234, 118, 0, 0.4);
    }}
    .step-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}
    .step-number {{
      background: var(--accent);
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      margin-right: 8px;
    }}
    .step-title-text {{
      font-size: 1.02rem;
      font-weight: 700;
      color: var(--text-main);
    }}
    .step-time {{
      font-size: 0.75rem;
      color: var(--accent-cyan);
      font-family: monospace;
      background: rgba(0, 210, 255, 0.1);
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid rgba(0, 210, 255, 0.2);
    }}
    .step-body {{
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 14px;
      font-size: 0.88rem;
      line-height: 1.55;
    }}
    .step-how {{
      background: rgba(0,0,0,0.25);
      border: 1px solid var(--border);
      padding: 12px;
      border-radius: 6px;
    }}
    .step-how-title {{
      font-size: 0.78rem;
      color: var(--accent-cyan);
      font-weight: 700;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .step-why {{
      background: rgba(234, 118, 0, 0.05);
      border: 1px solid rgba(234, 118, 0, 0.25);
      padding: 12px;
      border-radius: 6px;
    }}
    .step-why-title {{
      font-size: 0.78rem;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    /* Audio / Game Integration Table */
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
      登録スキル: 3件 | Blender 5.2.1 LTS | スタンドアロン動作
    </div>
  </header>

  <div class="main-container">
    <!-- Left Sidebar -->
    <div class="sidebar">
      <div class="search-box">
        <input type="text" id="search-input" placeholder="スキル・エフェクトを検索..." oninput="filterItems()">
      </div>
      <div class="item-list" id="item-list">
        <!-- JS renders cards -->
      </div>
    </div>

    <!-- Right Content Area -->
    <div class="content-area" id="detail-view">
      <!-- Detailed item content renders here -->
    </div>
  </div>

  <script>
    const KASAHARA_STEPS = {json.dumps(kasahara_steps, ensure_ascii=False)};

    const CATALOG_DATA = [
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
        steps: KASAHARA_STEPS,
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
        steps: [
          {{
            step: 1,
            title: "Bmesh による六角柱ピラミッド結晶のプログラマブル生成",
            time: "Bmesh Algorithm",
            how: "Segments=6 の底面頂点を配置し、高さ80%まで垂直押し出し後、先端トップ頂点に向かってピラミッド状に収束させて多面体を閉じる。",
            why: "天然の水晶（石英）は三方晶系／六方晶系の幾何学的対称性を持つため、六角柱をベースにすることで自然界の結晶構造を物理的に再現できる。"
          }},
          {{
            step: 2,
            title: "放射状クラスタリング ＆ ファセット角の維持",
            time: "Cluster Gen",
            how: "中心の巨大結晶を軸に、周囲に10〜12本の結晶を15〜35度の外向き傾斜とランダム回転をつけて配置。poly.use_smooth = False を維持。",
            why: "宝石や鉱石はカット面（ファセット）のエッジが鋭利に光を反射することで美しく見えるため、スムースシェードをあえてオフにする。"
          }},
          {{
            step: 3,
            title: "物理屈折率 (IOR 1.544) ＆ Transmission ガラスシェーダー",
            time: "PBR Shader",
            how: "Principled BSDF の IOR を 1.544（水晶の屈折率）、Transmission を 0.92、Roughness 0.08、微弱なEmissionを付与。",
            why: "石英ガラスの実測屈折率 1.544 に設定することで、背後の光が本物の水晶と同じ比率で屈折・集光する。"
          }}
        ],
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

      const stepCards = item.steps.map(st => `
        <div class="step-card">
          <div class="step-head">
            <div>
              <span class="step-number">STEP ${{st.step}}</span>
              <span class="step-title-text">${{st.title}}</span>
            </div>
            <span class="step-time">⏱ ${{st.time}}</span>
          </div>
          <div class="step-body">
            <div class="step-how">
              <div class="step-how-title">🛠 具体的操作手順 (How)</div>
              <div>${{st.how}}</div>
            </div>
            <div class="step-why">
              <div class="step-why-title">💡 その手順の意味・理由 (Why / 効果)</div>
              <div>${{st.why}}</div>
            </div>
          </div>
        </div>
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

        <!-- 3D Viewer & Multi-Cut Gallery Grid -->
        <div class="visual-grid">
          <!-- 3D Interactive (Base64 direct embedded, zero CORS issue) -->
          <div class="viewer-panel">
            <div class="panel-header-bar">
              <span>🎮 3D インタラクティブ (ドラッグ回転 / ホイール拡縮)</span>
              <span class="badge badge-cyan" style="font-size:0.7rem;">CORS制限解除済み</span>
            </div>
            <div class="viewer-body">
              <model-viewer 
                src="${{item.glbBase64}}" 
                alt="${{item.title}}" 
                auto-rotate 
                camera-controls 
                shadow-intensity="1.5" 
                exposure="1.1"
                camera-target="0m 0.6m 0m">
              </model-viewer>
            </div>
          </div>

          <!-- Multi-Cut Cycles Gallery -->
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

        <!-- Deep Step-by-Step Analysis Section (Most Important) -->
        <div class="section-card">
          <div class="section-title">
            <span>🔬 全制作工程 ＆「その手順の意味・Why」の徹底分析</span>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 16px;">
            動画内の単なるパラメータ値だけでなく、「なぜその形状なのか」「なぜその数値なのか」「なぜそのノードを繋ぐのか」の制作理論と物理背景を事細かに体系化しています。
          </p>
          <div class="step-list">
            ${{stepCards}}
          </div>
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

    // Initial render
    renderList(CATALOG_DATA);
    renderDetail(currentItem);
  </script>
</body>
</html>
'''

output_path = BASE_DIR / "catalog" / "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Successfully generated ultimate catalog at: {output_path}")
print(f"HTML File Size: {output_path.stat().st_size / 1024:.1f} KB")
