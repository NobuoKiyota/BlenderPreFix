# 🌲 【AAA ハイエンド】プロシージャル樹木 (Hiranoji Tree Generator) 最小単位手順 ＆ Why深層分析

本手順書は、国内屈指のジオメトリーノード作家 **平の字（Hiranoji）** 様のYouTubeチュートリアル動画（https://www.youtube.com/watch?v=LN83TYP9okk）：
『Blenderチュートリアル ジオメトリノードで木ジェネレータを０から作る』
を完全学習・分解した、カーブとジオメトリーノード（Geometry Nodes）による本格プロシージャル樹木システムの技術仕様書です。

---

## 📺 出典元情報 (Primary Source)
- **動画タイトル**: Blenderチュートリアル ジオメトリノードで木ジェネレータを０から作る
- **クリエイター**: 平の字 (Hiranoji / 平沢下戸)
- **YouTube URL**: [https://www.youtube.com/watch?v=LN83TYP9okk](https://www.youtube.com/watch?v=LN83TYP9okk)
- **核心技法**: Curve Line → Spline Parameter Tapering (Curve Radius) → Organic Noise Bend → Fibonacci Branching → Sub-branching (Twigs) → Feathered Leaf Mesh Instancing → SSS Sunlight Translucency → Procedural Sky

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | Shift + A > Mesh > Cube (樹木ジェネレーター原点) | Location: (0, 0, 0) | ジオメトリーノードモディファイアを保持するコンテナオブジェクトを作成。 |
| **#002** | Modifier > Geometry Nodes を追加 | 新規ツリー Hiranoji_Tree_Generator | プロシージャルツリー生成のためのノードグラフ環境を構築。 |
| **#003** | Shift + A > Curve Primitives > Curve Line | Start: (0, 0, 0), End: (0, 0, 5.0m) | 樹木の主軸となる幹（Trunk）の中心パスを生成。 |
| **#004** | Shift + A > Curve > Resample Curve | Mode: Count, Count: 32 | スプラインに均一な制御点を与え、滑らかな湾曲と先細り計算を可能にする。 |
| **#005** | Shift + A > Curve > Read > Spline Parameter | Output: Factor (0.0〜1.0) | 根元（0.0）から先端（1.0）へ向かう相対位置を取得。 |
| **#006** | Shift + A > Utilities > Map Range (幹の先細りテーパー) | From: 0〜1, To: 0.18m 〜 0.012m | 自然界の樹木力学に則り、根元が太く梢へ向けて急峻に細くなるプロファイルを算出。 |
| **#007** | Shift + A > Curve > Set Curve Radius | Radius に Map Range の Result 接続 | 算出したテーパー厚みをカーブの半径アトリビュートへ反映。 |
| **#008** | Shift + A > Texture > Noise Texture ＋ Vector Math | Scale: 0.8, Distortion: 0.5, Scale Factor: 0.18 | 幹に風や重力で生じる緩やかな「有機的うねり・曲がり」を計算。 |
| **#009** | Shift + A > Geometry > Set Position | Offset に Noise ベクトルを接続 | 直線的だった幹カーブに生命感あふれる自然なS字の歪みを彫刻。 |
| **#010** | 幹の中間〜上部（Factor 0.20〜0.95）のポイント抽出 | Selection: Factor > 0.20 | 根元付近（下枝のないクリアランス）を避け、枝が生える領域を厳密に限定。 |
| **#011** | Shift + A > Curve Primitives > Curve Line (枝カーブ) | Length: 2.1m 〜 0.45m (高さに反比例) | 樹頂ほど枝が短くなる円錐形樹冠（Canopy Conical Silhouette）を定義。 |
| **#012** | Instance on Points で幹の周囲に黄金角（137.5°）螺旋散布 | Rotation: Normal沿い＋上向き傾斜 25°〜55° | 葉同士が日光を遮り合わない植物学的な「フィボナッチ葉序」で大枝48本を展開。 |
| **#013** | 各大枝から左右・上向きに小枝（Twigs）を多段分岐 | Branch Factor: 3〜4 twigs per segment | 幹→枝→小枝の樹木階層構造を作り、葉が茂る土台を緻密に形成。 |
| **#014** | Shift + A > Curve > Curve to Mesh | Profile: Curve Circle (Resolution: 6) | 大枝・小枝のカーブを先端テーパーのついたリアルな木質ポリゴンへ立体化。 |
| **#015** | 葉プロトタイプ（Leaf Blade）の作成 | 菱形/羽状・中央葉脈折り目・先端下垂れ | 平の字様モデルに準拠した、光を美しく受ける有機的な曲面を持つリーフメッシュ。 |
| **#016** | 小枝・枝先端に葉を互生（Alternate）で密着インスタンス化 | 枝あたり20〜35枚、木全体で数千枚 | 枝先を完全に葉で覆い尽くし、動画同様のふさふさとした豊かな樹冠を形成。 |
| **#017** | 重力による葉と枝の先端下垂れ（Drooping）計算 | Z Offset: -0.07m * sin(curve_factor) | 雨露や葉自身の重みでしなやかに垂れ下がる優美な枝ぶりを再現。 |
| **#018** | 樹皮シェーダー（縦溝バークPBR）の構築 | BaseColor: (0.18, 0.14, 0.11), Roughness: 0.88 | 縦方向に走る深い樹皮の筋と繊維の質感をバンプ合成。 |
| **#019** | 葉シェーダー（透過光 SSS ＆ 新緑グラデーション）の構築 | BaseColor: 黄緑〜濃緑, Subsurface: 0.60 | 太陽光が差し込んだ際に葉の裏側が鮮やかに若草色に透け光るSSS効果。 |
| **#020** | 屋外太陽光＆青空・白雲プロシージャル環境の統合 | Sun Energy: 4.8, Sky Blue + Noise Clouds | 単色背景ではなく、青空と白い雲が広がるリアルな屋外空気感を再現。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Hiranoji_Bark** | Wood_Bark_Organic_Tree | Sound_Bark_Wood_Impact | 樹皮。縦木目ストライプバンプ、粗さ0.88。 |
| **M_Hiranoji_Leaves** | Foliage_Broadleaf_SSS | Sound_Foliage_Leaves_Rustle | 有機リーフ。Subsurface 0.60、風にざわめく葉擦れ音（Mid-high 1.8kHz-4.5kHz）。 |
