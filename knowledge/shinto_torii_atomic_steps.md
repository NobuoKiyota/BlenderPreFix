# 朱塗りの鳥居 (Shinto Torii Gate) 最小単位モデリング手順 ＆ Why深層分析

神社・和風ゲーム・異世界転生ファンタジーの象徴的ランドマーク「明神鳥居（笠木・島木・柱・貫・額束・亀腹台石・反り増し）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (台石 / 亀腹) | Vertices: 24, Radius: 0.28m, Depth: 0.15m, X: -1.2m, Z: 0.075m | 柱が腐らないように地面から浮かせる基礎石（亀腹 / Kamebara）を作成。 |
| **#002** | `Modifier` > `Mirror` | Axis: X | 左右の柱・台石を完全対称にモデリング。 |
| **#003** | `Shift + A` > `Mesh` > `Cylinder` (左柱 / Hashira) | Vertices: 24, Radius: 0.18m, Depth: 2.8m, X: -1.2m, Z: 1.55m | 鳥居を支える主柱を配置。 |
| **#004** | `R` > `Y: -2.5 deg` | 内転び（Uchikorobi） | 左右の柱を上に向かってわずかにハの字（内側）に傾け、耐震構造と安定した視覚美を付与。 |
| **#005** | `Tab` (Edit Mode) > 上端フェースを選択 > `S: 0.9` | わずかなテーパー | 上に向かって柱が細くなる伝統的な木造建築の円柱表現。 |
| **#006** | `Shift + A` > `Mesh` > `Cube` (貫 / Nuki) | Size: 1.0m, Location: (0, 0, 2.1m) | 左右の柱を水平に貫通して固定する貫（Nuki）を作成。 |
| **#007** | `S` > `X: 3.2, Y: 0.14, Z: 0.22` | 水平角材 | 柱の外側までしっかり突き出る長さを確保。 |
| **#008** | `Shift + A` > `Mesh` > `Cube` (島木 / Shimaki) | Size: 1.0m, Location: (0, 0, 2.95m) | 最上部の笠木を支える島木を作成。 |
| **#009** | `S` > `X: 3.6, Y: 0.22, Z: 0.16` | 幅広の横木 | 柱の上部に載り、屋根の荷重を分散。 |
| **#010** | `Shift + A` > `Mesh` > `Cube` (笠木 / Kasagi) | Size: 1.0m, Location: (0, 0, 3.12m) | 鳥居の最上部に載る大棟（笠木）。 |
| **#011** | `S` > `X: 3.9, Y: 0.26, Z: 0.18` | 島木より一回り大きいサイズ | 雨露を防ぐ庇（ひさし）の役割を果たす。 |
| **#012** | `Tab` (Edit Mode) > `Ctrl + R` > Cuts: 8 | 笠木・島木の中央分割 | 反り増し（Sorimashi）を作るための分割エッジ。 |
| **#013** | `Proportional Editing` (`O`) > 左右端を選択 > `G` > `Z: 0.18` | Falloff: Smooth | 明神鳥居の最大の特徴である「左右両端の優美な反り上がり」を成形。 |
| **#014** | `3` (Face) > 笠木・島木の左右端面を選択 > `R` > `Y: ±25 deg` (木鼻) | 斜めカット | 雨水を外へ流す木鼻（Kibana）の伝統的な斜め切り落とし。 |
| **#015** | `Shift + A` > `Mesh` > `Cube` (額束 / Gakuzuka) | Location: (0, 0, 2.52m) | 笠木と貫の間を中央で垂直に繋ぐ束柱。 |
| **#016** | `S` > `X: 0.16, Y: 0.08, Z: 0.65` | 垂直角柱 | 中央の剛性を高める補強部材。 |
| **#017** | `Shift + A` > `Mesh` > `Cube` (神額 / Plaque) | Location: (0, -0.06m, 2.52m) | 神社名が記される額（Plaque）。黒漆枠と金文字。 |
| **#018** | `S` > `X: 0.32, Y: 0.02, Z: 0.45` | 扁額 | 参拝者を迎える象徴的な表札。 |
| **#019** | `Modifier` > `Bevel` (全木製パーツ) | Width: 0.008m, Segments: 2 | 鉋（かんな）で削られた木角の美しい面取り。 |
| **#020** | `Material Assign` > `M_Torii_Vermilion` | 柱・貫・島木・額束に適用 | 魔除けの朱塗り（丹塗り / Vermilion Red）。木目と漆塗膜のツヤ。 |
| **#021** | `Material Assign` > `M_Torii_BlackLacquer` | 笠木・神額枠に適用 | 腐食を防ぐ黒漆塗り（Black Lacquer）。深みのある黒光り。 |
| **#022** | `Material Assign` > `M_Torii_StoneBase` | 台石（亀腹）に適用 | 荒削りの御影石。Roughness 0.9。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Torii_Vermilion** | `Wood_Heavy` | `Sound_Wood_Temple_Resonance` | 朱塗り木材 (0.85, 0.12, 0.05), Roughness 0.38。巨大木造建築の重厚な打撃共鳴音。 |
| **M_Torii_BlackLacquer** | `Wood_Hard` | `Sound_Wood_Footstep_Deep` | 黒漆 (0.05, 0.05, 0.05), Metallic 0.1, Roughness 0.22。硬質漆塗膜の引き締まった高音。 |
| **M_Torii_StoneBase** | `Stone` | `Sound_Stone_Base_Solid` | 御影石亀腹。Roughness 0.92, 微細ボロノイノイズ。地面接地の揺るぎない石材音。 |
