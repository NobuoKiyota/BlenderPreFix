# ドワーフの戦闘斧 (Dwarven Battleaxe) 最小単位モデリング手順 ＆ Why深層分析

重厚なドワーフ鍛冶による双刃バトルアックス（ダマスカス鋼、ルーン刻印、八角形シャフト、革巻きグリップ、真鍮ポメル）の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (柄 / Shaft) | Vertices: 8, Radius: 0.035m, Depth: 1.1m, Location: (0, 0, 0.55m) | 手になじむ伝統的な八角形断面（Octagonal）の木製シャフトを生成。 |
| **#002** | `Ctrl + A` > `Apply All Transforms` | All Transforms | スケールと原点を固定し、後続のモディファイアの歪みを防止。 |
| **#003** | `Tab` (Edit Mode) > `2` (Edge) > 上下端のエッジループ選択 > `Ctrl + B` (Bevel) | Width: 0.005m, Segments: 2 | シャフト両端の角張りを落とし、握りやすさと耐久性を表現。 |
| **#004** | `Shift + A` > `Mesh` > `Cube` (アックスヘッド基部 / Center Block) | Size: 0.12m, Location: (0, 0, 0.95m) | 刃を柄に強固に結合するアイ（目）とソケットの土台。 |
| **#005** | `S` > `X: 1.4, Y: 0.8, Z: 1.8` | 寸法微調整 | 柄を包み込む縦長の頑丈な鉄製ソケット形状を形成。 |
| **#006** | `Tab` (Edit Mode) > `3` (Face) > 正面フェース選択 > `E` (Extrude) > `X: 0.25m` | 右刃の押し出し | 片側のワイドな三日月型ブレードの土台を押し出し。 |
| **#007** | `S` > `Z: 1.8, Y: 0.3` | 先端の扇状拡大と薄型化 | 薪割りではなく戦闘用の鋭利なカーブブレードのテーパーを形成。 |
| **#008** | `E` > `X: 0.15m` > `S` > `Y: 0.05, Z: 1.3` | 刃先（Bevel Edge）の押し出し | 肉薄な鋭利エッジ（Cutting Edge）を作成。 |
| **#009** | `Ctrl + R` (Loop Cut) > 刃の胴体に2本カット | 分割数: 2 | 刃の背面にドワーフ特有の幾何学的なステップ（段差）を成形。 |
| **#010** | `Modifier` > `Mirror` | Axis: X, Bisect: X, Clipping: ON | 双刃（Double-bitted）アックスとして左右対称にミラー複製。 |
| **#011** | `Shift + A` > `Mesh` > `Cone` (中央スパイク / Top Spike) | Vertices: 8, Radius1: 0.025m, Depth: 0.18m, Location: (0, 0, 1.15m) | 柄の頂点から突き出る刺突用スチールスパイクを配置。 |
| **#012** | `Shift + A` > `Mesh` > `Cylinder` (革巻きグリップ / Leather Wrap) | Vertices: 12, Radius: 0.038m, Depth: 0.45m, Location: (0, 0, 0.35m) | 握り位置の滑り止めとなるレザーラップの土台を作成。 |
| **#013** | `Modifier` > `Screw` or `Curve Deform` | バンプ・スパイラル帯 | 革紐を斜めに幾重にも巻き付けた立体的な重なりを再現。 |
| **#014** | `Shift + A` > `Mesh` > `Icosphere` (柄頭 / Pommel) | Subdivisions: 2, Radius: 0.05m, Location: (0, 0, 0.02m) | 斧の重量バランスを取り、手からすっぽ抜けるのを防ぐカウンターウェイト。 |
| **#015** | `S` > `Z: 0.7` | 扁平球化 | 掌の付け根に干渉しないクラシックな真鍮ポメル形状に調整。 |
| **#016** | `Modifier` > `Bevel` (全金属部) | Width: 0.003m, Segments: 2 | 金属エッジにリアルなハイライトの光を走らせる。 |
| **#017** | `Material Assign` > `M_Axe_Damascus` | 双刃ブレード | 積層鍛造ダマスカス鋼の波状文様とシャープな金属反射。 |
| **#018** | `Material Assign` > `M_Axe_WoodShaft` | 八角形シャフト | 深みのあるダークオーク木材とオイルフィニッシュ。 |
| **#019** | `Material Assign` > `M_Axe_Leather` | グリップ部 | 使い込まれた牛革のシボ感と擦れ。 |
| **#020** | `Material Assign` > `M_Axe_RuneGlow` | 刃のルーン溝 | 鍛冶神の加護を宿すシアンブルーのルーン自発光（Emission: 5.0）。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Axe_Damascus** | Metal_Sharp_Heavy | Sound_Axe_Blade_Slash | ダマスカス鋼。Metallic 0.95、Roughness 0.28、波状Waveバンプ。 |
| **M_Axe_WoodShaft** | Wood_Solid_Ash | Sound_Axe_Shaft_Block | 硬質木材。Roughness 0.72、縦木目プロシージャルノイズ。 |
| **M_Axe_Leather** | Leather_Wrap | Sound_Axe_Grip_Squeeze | 革巻き。Roughness 0.65、微細Voronoiバンプ。 |
| **M_Axe_RuneGlow** | Magic_Runic_Cyan | Sound_Axe_Rune_Hum | 秘術ルーン発光。BaseColor (0.1, 0.8, 1.0)、Emission 5.0。 |
