# ファンタジーラウンドシールド (Viking Round Shield) 最小単位モデリング手順 ＆ Why深層分析

北欧バイキングや中世戦士の主装備「木製ラウンドシールド（スラット木板組み＆中央鉄ボス＆外周鉄リム＆リベット）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` | Vertices: 32, Radius: 0.55m, Depth: 0.025m | 円形盾（Shield Body）の基本となる木板ディスクを生成。 |
| **#002** | `R` > `X` > `90` | Angle: 90 deg | 盾を立て、Y軸方向を法線（正面）に向ける。 |
| **#003** | `Ctrl + A` > `Apply All Transforms` | Rotation & Scale | 回転とスケールを確定し、以降のプロシージャル木目やベベルの歪みを防止。 |
| **#004** | `Tab` (Edit Mode) > `Ctrl + R` | Cuts: 6 (縦方向) | 一枚板ではなく、複数の木板（Planks）を並べて張り合わせた構造を再現。 |
| **#005** | `2` (Edge) > 縦の分割線を選択 > `Ctrl + B` (Bevel Edge) | Width: 0.004m, Segments: 2 | 木板と木板の合わせ目（目地）にわずかな溝を掘るためのベース作成。 |
| **#006** | `Alt + E` > `Extrude Faces Along Normals` | Offset: -0.003m | 木板の接合部にリアルな溝（シーム）を刻み、立体感を演出。 |
| **#007** | `Proportional Editing` (`O`) > 頂点選択 > `G` > `Y: 0.04` | Falloff: Sphere, Radius: 0.6m | 盾全体をわずかにドーム状（中央が前に出た凸面）に湾曲させ、矢や剣を受け流す実戦形状を形成。 |
| **#008** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `UV Sphere` (中央ボス) | Segments: 32, Rings: 16, Radius: 0.16m, Y: 0.02m | 握り拳を守る中央金属カップ（Shield Boss / Umbo）を作成。 |
| **#009** | `Tab` (Edit Mode) > 奥半分（Y < 0）を削除 | 半球化 | 盾の前面に密着する半球シェル形状にする。 |
| **#010** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Torus` (ボス外周フランジ) | Major: 0.16m, Minor: 0.015m, Y: 0.02m | ボスを木板に鋲留めするための金属つば（Flange）を形成。 |
| **#011** | `Shift + A` > `Mesh` > `Torus` (外周鉄リム) | Major: 0.55m, Minor: 0.018m, Y: 0 | 盾の縁を補強し、斧の直撃で木が割れるのを防ぐ鉄リム（Iron Rim）を配置。 |
| **#012** | `Shift + A` > `Mesh` > `Icosphere` (リベット) | Subdivisions: 1, Radius: 0.012m | リムおよびボスを固定する鍛造リベットを作成。 |
| **#013** | `Linked Duplicate` (`Alt + D`) | 外周に沿って16箇所、ボス周りに6箇所配置 | リベットが規則正しく並ぶことで、職人の手打ち工芸感を演出。 |
| **#014** | `Shift + A` > `Mesh` > `Cube` (裏面ハンドル) | Size: 1.0m, Y: -0.03m | 盾の裏側にある持ち手（グリップ木製バー）を配置。 |
| **#015** | `S` > `X: 0.35, Y: 0.03, Z: 0.03` | 横バー形状 | 戦士が片手で握るための強固なグリップバー。 |
| **#016** | `Shift + A` > `Mesh` > `Cube` (腕通し革ストラップ) | Y: -0.03m, X: 0.15m | 前腕を固定する革ベルト（Arm Strap）を作成。 |
| **#017** | `Material Assign` > `M_Shield_Wood` | 木板ディスクに適用 | オークまたはアッシュ材。縦方向の明瞭な木目と使い古された擦れ傷。 |
| **#018** | `Material Assign` > `M_Shield_Iron` | ボス、リム、リベットに適用 | 鍛造黒鉄。Metallic 0.95, Roughness 0.38。 |
| **#019** | `Material Assign` > `M_Shield_Leather` | 裏面ストラップに適用 | 頑丈な牛革。深みのある茶褐色。 |
| **#020** | `Shade Auto Smooth` | 全パーツに適用 | 金属リムの滑らかなハイライトと木板のエッジをシャープに保つ。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Shield_Wood** | `Wood_Medium` | `Sound_Shield_Wood_Block` | 盾用アッシュ材。粗さ 0.72。打撃による繊維の凹みプロシージャルノイズ。 |
| **M_Shield_Iron** | `Metal_Heavy` | `Sound_Shield_Iron_Deflect` | 鉄ボス・リム。Metallic 0.96, Roughness 0.35。矢を弾く甲高い金属響き。 |
| **M_Shield_Leather** | `Fabric_Leather` | `Sound_Shield_Equip` | 腕固定用ストラップ。粗さ 0.88。装備時・構え時の革のきしみ音。 |
