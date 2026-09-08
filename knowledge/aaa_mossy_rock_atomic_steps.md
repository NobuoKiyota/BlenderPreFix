# 🪨 【AAA フォトリアル】プロシージャル巨岩 (Sacoche Ito 3D Geometry Nodes Rock) 最小単位手順 ＆ Why深層分析

本手順書は、**サコッシュ伊藤3D様** のYouTubeチュートリアル動画（`https://www.youtube.com/watch?v=vFSOf9zAY_I`）：
『【Blender】ジオメトリーノードで簡単に作れるプロシージャルな岩のモデリング解説!初心者向け丁寧解説!』
を完全学習・分解した、ジオメトリーノード（Geometry Nodes）によるプロシージャル岩石モデリングの技術仕様書です。

---

## 📺 出典元情報 (Primary Source)
- **動画タイトル**: 【Blender】ジオメトリーノードで簡単に作れるプロシージャルな岩のモデリング解説!初心者向け丁寧解説!
- **クリエイター**: サコッシュ伊藤3D
- **YouTube URL**: [https://www.youtube.com/watch?v=vFSOf9zAY_I](https://www.youtube.com/watch?v=vFSOf9zAY_I)
- **核心技法**: Distribute Points on Faces → Instance on Points (Cube) → Realize Instances → **Convex Hull (凸包)** → Subdivide Mesh → Set Position (Noise Texture) → Normal Z Shader

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` (ベース立方体作成) | Size: 1.0m, Scale: (1.8, 1.3, 0.85) | 巨岩の原点となるバウンディングボリュームを作成。トランスフォームを適用 (`Ctrl + A`)。 |
| **#002** | `Modifier` > `Geometry Nodes` を追加 | 新規ノードツリー作成 | パラメータ変更で無限のバリエーションを生み出すプロシージャル基盤を構築。 |
| **#003** | `Shift + A` > `Point` > `Distribute Points on Faces` | Density: 18.0 | キューブの表面全体にランダムな散布ポイントを生成。岩の凸凹の起点とする。 |
| **#004** | `Shift + A` > `Mesh Primitives` > `Cube` | Size: (0.75, 0.75, 0.75) | ポイント上にインスタンス配置するための素片ブロックを定義。 |
| **#005** | `Shift + A` > `Utilities` > `Random Value` (Rotation) | Data Type: Vector, Min: -π, Max: +π | インスタンスの回転を完全ランダム化し、規則的なグリッド感を破壊。 |
| **#006** | `Shift + A` > `Utilities` > `Random Value` (Scale) | Data Type: Vector, Min: 0.4, Max: 1.4 | インスタンスの大きさに大小のランダムなばらつきを与える。 |
| **#007** | `Shift + A` > `Instances` > `Instance on Points` | Points, Instance, Rotation, Scale 接続 | 散布ポイント上にランダムな立方体群を一斉配置。 |
| **#008** | `Shift + A` > `Instances` > `Realize Instances` | Instances → Geometry | バラバラの仮想インスタンスを、実体を持った1つの編集可能メッシュデータへ変換。 |
| **#009** | **`Shift + A` > `Mesh` > `Convex Hull` (凸包)** | Geometry 接続 | **サコッシュ伊藤3D式の核心技法**。散布されたブロック群の外側を隙間なく包み込み、100%ソリッドでシャープな多面体岩石ベースを瞬時に生成。 |
| **#010** | `Shift + A` > `Mesh` > `Subdivide Mesh` | Level: 3 | 凸包の粗い多面体を細分化し、滑らかなディスプレイスメントを受け止める高密度頂点を確保。 |
| **#011** | `Shift + A` > `Texture` > `Noise Texture` | Scale: 2.8, Detail: 4.0, Roughness: 0.6 | 岩肌特有のゴツゴツした地質学的断層・微小凹凸パターンを計算。 |
| **#012** | `Shift + A` > `Vector Math` (Subtract) | Vector: (0.5, 0.5, 0.5) | ノイズの基準値(0〜1)から0.5を減算し、頂点の変位を内外均等にセンタリング。 |
| **#013** | `Shift + A` > `Vector Math` (Scale) | Scale: 0.22 | 表面の凹凸の深さ（変位量）を適切にコントロール。 |
| **#014** | `Shift + A` > `Geometry` > `Set Position` | Offset に Scale ベクトルを接続 | ノイズ値に従ってメッシュ頂点を変位させ、自然界の岩肌の起伏を直接彫刻。 |
| **#015** | `Shift + A` > `Mesh` > `Set Shade Smooth` | Geometry 接続 | ファセット面を滑らかにし、リアルな陰影グラデーションを付与。 |
| **#016** | シェーダーエディタで花崗岩PBRマテリアルを作成 | BaseColor: 暗灰色, Roughness: 0.85 | 深みのある玄武岩〜花崗岩の硬質岩肌マテリアルを定義。 |
| **#017** | `Geometry` > `Separate XYZ` (Normal Z) を構築 | ColorRamp: Pos 0.45〜0.70 | 上を向いている面（日当たりと雨露を受ける上面）だけに苔を生やす法線Zマスク。 |
| **#018** | `MixRGB` で岩肌とエメラルド青苔をブレンド | Color2: (0.14, 0.28, 0.08) | 1つのプロシージャルマテリアル内で上面の苔と側面の岩肌をシームレス結合。 |
| **#019** | ジオメトリーノードの末尾に `Set Material` を追加 | 作成したマテリアルを割り当て | ジオメトリーノード内で生成されたメッシュにPBRシェーダーを自動適用。 |
| **#020** | `Group Output` に接続して完成 | All Transforms 適用 | Seed値やパラメータを変えるだけで無限の形状が生まれるプロシージャル岩石アセットが完成。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Sacoche_Rock_PBR** | Stone_Granite_Weathered | Sound_Rock_Massive_Impact | サコッシュ伊藤3D式。法線Zマスク上面苔、直列多重バンプ（大割れ目＋微細粒）。 |
