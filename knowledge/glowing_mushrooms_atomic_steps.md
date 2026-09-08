# 発光キノコ群生 (Bioluminescent Mushrooms) 最小単位モデリング手順 ＆ Why深層分析

ファンタジー・洞窟探索ゲームの幻想的な環境プロップ「発光キノコ群生（半透明有機SSS＆傘・柄・発光ドット＆浮遊胞子＆苔岩）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Icosphere` (岩台座) | Subdivisions: 2, Radius: 0.6m, Z: 0.15m | キノコが生える母体となる洞窟の苔岩（Rock Base）を生成。 |
| **#002** | `S` > `X: 1.2, Y: 0.9, Z: 0.4` | 不均等スケール | 自然界の平たい濡れ岩の形状にする。 |
| **#003** | `Modifier` > `Displace` | Texture: Clouds, Strength: 0.12m | 機械的な球体感を消し、風化・浸食された有機的凹凸を付与。 |
| **#004** | `Shift + A` > `Mesh` > `Cylinder` (親キノコの柄) | Vertices: 16, Radius: 0.04m, Depth: 0.45m, Z: 0.4m | 主幹となる太いキノコの茎（Stem）を配置。 |
| **#005** | `Tab` (Edit Mode) > `Ctrl + R` > Cuts: 4 | 縦分割 | 茎をS字にしなやかに曲げるための関節エッジを作成。 |
| **#006** | `Proportional Editing` > 頂点を傾斜移動 | スムーズフォールオフ | 重力や光に向かって伸びるキノコ特有の有機的カーブを形成。 |
| **#007** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (傘) | Vertices: 24, Radius: 0.22m, Depth: 0.15m, Z: 0.65m | キノコの頭部（Cap）となる基本円筒を作成。 |
| **#008** | `Tab` (Edit Mode) > 上面フェースを選択 > `M` > `At Center` | 円錐コーン化 | 傘の頂点を尖らせ、鐘型（Bell Shape）のシルエットを作る。 |
| **#009** | `Ctrl + R` > 傘の側面にループカット 2本 | 下部を外側へフレア展開 (`S > X,Y`) | キノコの傘の縁がスカート状にふんわりと広がる曲線をモデリング。 |
| **#010** | `3` (Face) > 下面フェースを選択 > `I` (Inset) > `E` (押し込み) | 深さ: -0.05m | 傘の裏側に空洞（ひだ収容部）を掘り込む。 |
| **#011** | `Tab` (Object Mode) > `Modifier` > `Subdivision Surface` | Levels: 2 | カクつきのない滑らかで柔らかい有機メッシュに昇華。 |
| **#012** | `Shift + D` > `S: 0.6` | 複製・縮小 | 親キノコを取り囲む中型・小型のキノコ（子株群）を岩上に3〜4本散布。 |
| **#013** | `R` (Rotate) | それぞれ異なる方向へ傾斜配置 | 人工的クローン感を排除し、自然界の群生コロニーを再現。 |
| **#014** | `Shift + A` > `Mesh` > `Icosphere` (傘の発光ドット) | Radius: 0.008m | キノコの傘表面に点在するバイオルミネセンス発光胞子粒。 |
| **#015** | 傘の表面に複数配置 | Emission Material | 暗闇でドット状に燐光を放つ幻想的な視覚アクセント。 |
| **#016** | `Shift + A` > `Point Light` | Location: 傘の直下 (Z: 0.55m), Color: シアンブルー | キノコ自身が光源となり、下の岩や柄を照らし出す光を配置。 |
| **#017** | `Material Assign` > `M_Mushroom_Cap` | 傘に割り当て | エメラルド〜シアンの半透明SSS（Subsurface Scattering）有機体。 |
| **#018** | `Material Assign` > `M_Mushroom_Stem` | 柄に割り当て | 乳白色〜淡い水色。繊維感のある微細縦ノイズ。 |
| **#019** | `Material Assign` > `M_Mushroom_Glow` | ドット・胞子に割り当て | 蒼く鮮烈な自発光 (RGB: 0.05, 0.9, 0.8, Strength: 7.0)。 |
| **#020** | `Material Assign` > `M_Cluster_Rock` | 岩に割り当て | 暗い洞窟岩石。水気を含んだしっとりとした質感（Roughness 0.4）。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Mushroom_Cap** | `Organic_Soft` | `Sound_Mushroom_Squish` | 傘の半透明SSS。Subsurface Weight 0.35, 粗さ 0.28, ゼリーのような弾力感。 |
| **M_Mushroom_Glow** | `Magic_Light` | `Sound_Spore_Glow_Hum` | 胞子発光。Emission Strength 7.0。暗闇で幻想的な自発光共鳴音を想起。 |
| **M_Mushroom_Stem** | `Organic_Flesh` | `Sound_Fungi_Rustle` | 柄の繊維質。乳白色 (0.85, 0.95, 0.95), 粗さ 0.65, 踏んだ時のサクサク感。 |
| **M_Cluster_Rock** | `Stone` | `Sound_Rock_Scrape` | 濡れた洞窟岩。暗灰 (0.12, 0.14, 0.15), 粗さ 0.35 (濡れテカリ)。 |
