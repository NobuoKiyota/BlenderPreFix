# オリエンタル石灯籠 (Japanese Stone Lantern / Toro) 最小単位モデリング手順 ＆ Why深層分析

日本庭園や神社・オリエンタル神社仏閣ゲームの象徴的プロップ「六角石灯籠（宝珠・笠・火袋・中台・竿・基礎）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` | Vertices: 6, Radius: 0.6m, Depth: 0.2m | 基礎（Kiso / 地面接地面）となる六角形の堅牢な土台を生成。 |
| **#002** | `Modifier` > `Bevel` | Segments: 2, Width: 0.02m | 荒削りの石材らしいエッジの欠け・面取り感を表現。 |
| **#003** | `Shift + A` > `Mesh` > `Cylinder` (竿) | Vertices: 6, Radius: 0.25m, Depth: 0.8m, Z: 0.5m | 基礎から伸びる主柱（竿 / Sao）を配置。 |
| **#004** | `Tab` (Edit Mode) > `Ctrl + R` > Cuts: 2 | 中央部をわずかに `S > (X,Y)` で膨らませる | 直線的な柱ではなく、エンタシス（わずかな中央膨らみ）を持たせて伝統美を再現。 |
| **#005** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (中台) | Vertices: 6, Radius: 0.55m, Depth: 0.15m, Z: 0.95m | 火袋を支える受け皿（中台 / Chudai）を配置。 |
| **#006** | `Tab` (Edit Mode) > 底面フェースを選択 > `S: 0.7` | 逆台形テーパー | 下に向かって窄まる蓮華座の傾斜をつける。 |
| **#007** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (火袋) | Vertices: 6, Radius: 0.45m, Depth: 0.4m, Z: 1.25m | 光を灯す中心部（火袋 / Hibukuro）を配置。 |
| **#008** | `Tab` (Edit Mode) > 側面の各フェースを選択 > `I` (Inset) | Thickness: 0.06m | 灯籠の窓枠（格子枠）となる外枠を残す。 |
| **#009** | `Alt + E` > `Extrude Faces Along Normals` | Offset: -0.2m (内部へ貫通) | 内部に空洞をくり抜き、光が外へ漏れ出す開口窓（日輪・月輪）を形成。 |
| **#010** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (笠) | Vertices: 6, Radius: 0.85m, Depth: 0.25m, Z: 1.55m | 雨風を凌ぐ大屋根（笠 / Kasa）を配置。 |
| **#011** | `Tab` (Edit Mode) > 上面フェースを選択 > `S: 0.4` | 台形コーン形状 | 屋根の急勾配をつくり、水はけの良い屋根形状を定義。 |
| **#012** | `2` (Edge) > 六角の角エッジを選択 > `G` > `Z: 0.05` | 端部の跳ね上げ（反り） | 和風建築特有の「軒先の反り（Soridashi）」を表現し、優美さを演出。 |
| **#013** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (請花) | Vertices: 6, Radius: 0.25m, Depth: 0.08m, Z: 1.72m | 笠の上に載る宝珠受け座（請花 / Ukebana）を作成。 |
| **#014** | `Shift + A` > `Mesh` > `UV Sphere` (宝珠) | Radius: 0.12m, Z: 1.85m | 頂点を飾る仏教伝来の宝珠（Hoju）を配置。 |
| **#015** | `Tab` (Edit Mode) > 先端頂点を選択 > `G` > `Z: 0.08` | 宝珠の先端尖り | 雫型・玉ねぎ型の神聖なプロポーションに整形。 |
| **#016** | `Shift + A` > `Mesh` > `Cylinder` (内部蝋燭) | Vertices: 12, Radius: 0.04m, Depth: 0.15m, Z: 1.15m | 火袋の内部中央に置く蝋燭（Candle）を作成。 |
| **#017** | `Shift + A` > `Mesh` > `Ico Sphere` (炎) | Subdivisions: 2, Radius: 0.025m, Z: 1.26m | 揺らめく灯火。発光シェーダー（Warm Amber）を適用。 |
| **#018** | `Point Light` | Location: (0, 0, 1.26), Energy: 60W, Color: 橙色 | 火袋の中から周囲の石壁や地面へ漏れ出す物理ライト。 |
| **#019** | `Material Assign` > `M_Lantern_Stone` | 石材パーツ全体に割り当て | 御影石・花崗岩の粗い粒子感と自然な風化をプロシージャルノイズで再現。 |
| **#020** | `Material Assign` > `M_Lantern_Moss` | 上面・くぼみフェースにブレンド割り当て | 雨露の溜まりやすい笠や中台の上面に生えるリアルな苔（Moss）を表現。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Lantern_Stone** | `Stone` | `Sound_Stone_Impact_Heavy` | 花崗岩（グラナイト）。粗さ 0.85、微細ボロノイノイズによる石粒バンプ。 |
| **M_Lantern_Moss** | `Organic_Foliage` | `Sound_Moss_Brush` | 深緑の苔。Base Color (0.08, 0.22, 0.05), Roughness 0.95, ベルベット感。 |
| **M_Lantern_Flame** | `Fire_Soft` | `Sound_Candle_Flicker` | 暖色炎 (RGB: 1.0, 0.45, 0.05), Emission 8.0。 |
