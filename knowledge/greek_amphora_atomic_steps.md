# 古代ギリシャ風アンフォラ壺 (Ancient Greek Amphora Vase) 最小単位モデリング手順 ＆ Why深層分析

遺跡探索・地中海ファンタジー・破壊可能オブジェクトの定番「双耳アンフォラ陶器壺（卵型ボディ＆S字湾曲取っ手＆素焼きテラコッタ＆空洞構造）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` | Vertices: 32, Radius: 0.2m, Depth: 0.1m, Z: 0.05m | 壺を支える円形フットベース（台座 / Base Foot）を生成。 |
| **#002** | `Tab` (Edit Mode) > 上面フェースを選択 > `E` (Extrude) | Z: 0.15m, `S: 1.8` | 壺の下部から胴体にかけて急激に広がるフレア形状を形成。 |
| **#003** | `E` (Extrude) | Z: 0.35m, `S: 1.3` (最大径 Radius: 0.45m) | ワインや油を大量に蓄えるアンフォラ特有の最も太い「肩（Shoulder）」を作成。 |
| **#004** | `E` (Extrude) | Z: 0.25m, `S: 0.45` | 首（Neck）に向かってすぼまる流線型の絞り込みを定義。 |
| **#005** | `E` (Extrude) | Z: 0.25m, `S: 1.0` (直立円筒) | 細長い注ぎ口の筒（Neck）を形成。 |
| **#006** | `E` (Extrude) | Z: 0.08m, `S: 1.4` | 液体を注ぎやすく、封蝋しやすい外側に反った口縁（Lip / Rim）を形成。 |
| **#007** | `I` (Inset Faces) | Thickness: 0.03m | 陶器の肉厚（厚み）を定義。 |
| **#008** | `E` (Extrude) > `Z` | -0.9m (内部空洞へ深掘り) | 内部に空洞（Cavity）をくり抜き、本物の容器メッシュにする。 |
| **#009** | `Tab` (Object Mode) > `Modifier` > `Subdivision Surface` | Levels: 2 | ろくろ（旋盤）で回転成型されたような滑らかな曲面美を実現。 |
| **#010** | `Shift + A` > `Mesh` > `Torus` (S字ハンドル用母材) | Major: 0.18m, Minor: 0.024m, Location: (0.35m, 0, 0.72m) | 首と肩を繋ぐ双耳取っ手（Loop Handle）を作成。 |
| **#011** | `R` > `X: 90` | 縦向きに配置 | 壺の側面に沿う垂直ループにする。 |
| **#012** | `Tab` (Edit Mode) > 内側の頂点を選択し、壺の壁面にスナップ結合 | 密着 | 口縁直下から肩の最太部にかけてS字に接地する古代特有のアーチハンドル。 |
| **#013** | `Tab` (Object Mode) > `Modifier` > `Mirror` | Axis: X | 左右対称に完全なツインハンドル（双耳）を自動生成。 |
| **#014** | `Apply Mirror` | 一体化 | 将来的な非対称の傷やヒビ割れ加工を可能にする。 |
| **#015** | `Modifier` > `Displace` | Texture: Voronoi / Noise, Strength: 0.006m | 素焼きテラコッタのざらつきと、手びねり・焼成時の自然な歪みを付与。 |
| **#016** | `Material Assign` > `M_Amphora_Clay` | 全体に適用 | 赤土・テラコッタ（Terracotta）。粗さ 0.82、微細な砂粒バンプ。 |
| **#017** | `Material Assign` > `M_Amphora_Pattern` | 胴体中央帯フェースに適用 | 黒絵式・赤絵式の古代ギリシャ幾何学模様帯（Black-figure glaze）。 |
| **#018** | `Shade Smooth` | 全体に適用 | 光沢のないマットな陶器の質感を演出。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Amphora_Clay** | `Ceramic` | `Sound_Pottery_Smash_Break` | 素焼きテラコッタ (0.62, 0.32, 0.18), Roughness 0.82。割れ・破壊音。 |
| **M_Amphora_Pattern** | `Ceramic_Glaze` | `Sound_Pottery_Slide` | 施釉ブラック (0.08, 0.07, 0.06), Roughness 0.35。床引き摺り音。 |
| **M_Amphora_Inside** | `Dirt_Dry` | `Sound_Vase_Dust_Echo` | 内部の乾燥土・埃。壺内部の空洞に響く反響音（Reverb/Resonance）。 |
