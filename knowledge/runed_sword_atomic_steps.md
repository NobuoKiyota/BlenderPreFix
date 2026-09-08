# 古代のルーン聖剣 (Ancient Runed Broadsword) 最小単位モデリング手順 ＆ Why深層分析

ファンタジーRPGの主役武器「両刃ロングソード（フラー溝＆古代ルーン発光＆革巻きグリップ＆金属ポメル）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` | Size: 1.0m, Location: (0, 0, 1.0) | 刀身（Blade）の基本断面となる直方体を生成。 |
| **#002** | `S` > `X: 0.12, Y: 0.02, Z: 0.8` | X: 0.12, Y: 0.02, Z: 0.8 | 両刃刀身の薄さと幅、長さの基本プロポーションを定義。 |
| **#003** | `Ctrl + A` > `Apply All Transforms` | All Transforms | 今後のインセットや押し出しが均等スケールで動作するように初期化。 |
| **#004** | `Tab` (Edit Mode) > `Ctrl + R` | Cuts: 1 (中央縦方向) | 刀身の中央稜線（Ridge）を作成し、ダイヤモンド断面への変形準備。 |
| **#005** | `2` (Edge) > 左右のサイドエッジを選択 > `S` > `Y` | Scale Y: 0.1 | 左右の刃（Edge）を極限まで薄く尖らせ、鋭利な刃先形状を形成。 |
| **#006** | `1` (Vertex) > 先端頂点を選択 > `M` > `At Center` | Merge at Center | 刀身の先端を一点に集約し、刺突用の切っ先（Tip）を完成。 |
| **#007** | `3` (Face) > 刀身中央の縦ライン面を選択 | 両面の中央フェース | フラー（血溝 / Fuller）となる窪み領域を指定。 |
| **#008** | `I` (Inset Faces) | Thickness: 0.01m | フラーの枠取りを行い、エッジのシャープさを保護。 |
| **#009** | `Alt + E` > `Extrude Along Normals` | Offset: -0.005m | 刀身内部に浅い溝を掘り込み、軽量化と剛性を両立するフラーを立体化。 |
| **#010** | `Material Assign` > `M_Sword_Rune` | フラー溝の底面フェースに割り当て | 溝の内部に古代魔術のルーン文字が青白く発光するシェーダー領域を分離。 |
| **#011** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cube` | Crossguard | 鍔（ツバ / Crossguard）を作成するメッシュ。 |
| **#012** | `S` > `X: 0.35, Y: 0.05, Z: 0.05` | Location: (0, 0, 0.48) | 刀身と柄を隔て、相手の刃を受け止める横幅と厚みを設定。 |
| **#013** | `Tab` (Edit Mode) > `Ctrl + R` > 左右対称ループカット | 左右端を選択 > `G` > `Z: 0.04` | 鍔の両端をやや刀身側へ湾曲させ、クラシックな騎士剣の優雅さを演出。 |
| **#014** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` | Vertices: 16, Radius: 0.022m, Depth: 0.28m | 握り手（Grip）となる円筒を鍔の直下 (Z: 0.32) に配置。 |
| **#015** | `Tab` (Edit Mode) > `Ctrl + R` > Cuts: 8 | リング状分割 | 革紐を巻きつけた際の凹凸（リブ）を作るガイドエッジ。 |
| **#016** | `Alt + S` (Shrink/Fatten) | 交互に選択して拡大/縮小 | 手に吸い付くようなエルゴノミクスグリップの凹凸形状をモデリング。 |
| **#017** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` | Vertices: 8, Radius: 0.045m, Depth: 0.05m | 柄頭（ポメル / Pommel）となる八角形パーツを柄の末端 (Z: 0.15) に配置。 |
| **#018** | `Tab` (Edit Mode) > `Bevel` (`Ctrl + B`) | Segments: 2, Width: 0.01m | ポメルのエッジを面取りし、打撃武器としても機能する重厚感を付与。 |
| **#019** | `Modifier` > `Bevel` (刀身・鍔) | Limit Method: Angle (30°), Width: 0.003m | 金属光沢のハイライトエッジを際立たせるベベルモディファイア。 |
| **#020** | `Shade Auto Smooth` | 全パーツに適用 | 鋭利な刃と滑らかな柄の曲面を同一モデル内で自然に両立。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Sword_Steel** | `Metal_Heavy` | `Sound_Sword_Clang` | ダマスカス風の微細な波紋。Metallic 0.98, Roughness 0.22。 |
| **M_Sword_Rune** | `Magic_Light` | `Sound_Rune_Hum` | 神秘的な青白発光 (RGB: 0.1, 0.6, 1.0), Emission Strength 4.5。 |
| **M_Sword_Leather** | `Fabric_Leather` | `Sound_Leather_Grip` | 褐色の使い込まれた革。粗さ 0.85, バンプによる細かなシワ。 |
| **M_Sword_Gold** | `Metal_Light` | `Sound_Pommel_Strike` | 鍔とポメルの装飾金 (RGB: 0.9, 0.75, 0.2), Metallic 1.0。 |
