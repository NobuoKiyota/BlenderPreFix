# 古びた木樽 (Rustic Wooden Barrel) 最小単位モデリング手順 ＆ Why深層分析

酒場やダンジョンに山積みされる、中央が美しく膨らんだオーク板材と鍛造鉄タガ（フープ）を持つ中世木樽の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (樽本体ブロック / Barrel Body) | Vertices: 16, Radius: 0.42m, Depth: 1.1m | 16枚の縦板（Stave）で構成される木樽の外径ベース。 |
| **#002** | `Tab` (Edit Mode) > `Ctrl + R` (Loop Cut) > 横方向に6分割 | 分割数: 6 | 樽特有の「中央が膨らんだ樽型カーブ（Bilge）」を作るためのエッジ。 |
| **#003** | プロポーショナル編集 (`O`, Falloff: Sphere) > 中央エッジループ選択 > `S` (Scale) | `S: 1.25` (Z軸以外) | 中央部をなだらかに太らせ、液体を転がして運搬しやすい樽型カーブを成形。 |
| **#004** | `3` (Face) > 上面と底面のフェースを選択 > `I` (Inset: 0.04m) > `E` (Extrude: -0.06m) | 天板・底板の掘り下げ | 蓋が樽の縁（チャイム）の内側に一段深く沈み込んだ構造を表現。 |
| **#005** | `Tab` (Edit Mode) > 縦の全エッジループを選択 > `Ctrl + B` (Bevel) | Width: 0.003m, Profile: 0.1 | 16枚の木の板（ステーブ）が組み合わさる継ぎ目の溝（スリット）を形成。 |
| **#006** | `Shift + A` > `Mesh` > `Cylinder` (上部鉄タガ / Top Iron Hoop) | Vertices: 24, Radius: 0.43m, Depth: 0.035m, Location: (0, 0, 0.45m) | 樽の上端を締め上げる一番上の鍛造鉄バンド（Head Hoop）。 |
| **#007** | `Modifier` > `Solidify` | Thickness: 0.004m | ペラペラ感を消し、頑丈な帯鉄の肉厚を付与。 |
| **#008** | `Shift + D` で複製 > `Z: 0.22m` に配置 (Quarter Hoop) | スケール調整 | 樽の膨らみに合わせて半径を 1.15 倍に調整。 |
| **#009** | 上部2本のタガを選択 > `Shift + D` > `S > Z: -1` (下部に反転複製) | 下部2本のタガ完成 | 樽全体を強固に結束する合計4本の鉄タガ構造を完成。 |
| **#010** | `Shift + A` > `Mesh` > `Icosphere` (リベット鋲 / Rivets) | Radius: 0.008m | 各鉄タガの継ぎ目を固定する鍛造リベットを配置。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (注ぎ口の木栓 / Bung) | Vertices: 12, Radius: 0.025m, Depth: 0.04m, Location: (0.52m, 0, 0) | 樽の腹の中央にあるワイン・エール酒の注入口（Bung Hole）と栓。 |
| **#012** | `R > Y: 90 deg` | 水平差し込み | 樽の横腹からクイッと突き出る木栓を配置。 |
| **#013** | `Modifier` > `Bevel` (樽本体) | Width: 0.004m, Segments: 2 | 木板のエッジを柔らかく丸め、リアルな手作業の木工感を演出。 |
| **#014** | `Right Click` > `Shade Auto Smooth` (Angle: 35°) | 全オブジェクト | 曲面の滑らかさと板の境界線のシャープさを両立。 |
| **#015** | `Material Assign` > `M_Barrel_Oak` | 樽本体・天板・底板 | 経年変化したオーク古材。Roughness 0.78、微細バンプ。 |
| **#016** | `Material Assign` > `M_Barrel_IronHoop` | 4本の鉄タガ | 黒錆の浮いた鍛造鉄。Metallic 0.92, Roughness 0.52。 |
| **#017** | `Material Assign` > `M_Barrel_TapWood` | 木製栓 | 乾いた赤褐色木材。Roughness 0.85。 |
| **#018** | ランダム頂点揺らぎ (Displace Modifier 微弱) | Strength: 0.003m | 工業製品のような完全な幾何学を崩し、中世の手作り感を付与。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | 将来の物理シミュレーション（樽転がし・破壊）に備えてスケール初期化。 |
| **#020** | スタジオライティング ＆ Cycles レンダリング | 3点照明セットアップ | 木目の質感と金属タガのハイライトを際立たせるコントラスト照明。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Barrel_Oak** | Wood_Hollow_Stave | Sound_Barrel_Roll_Loop | 中空木材。Roughness 0.78、縦木目Noise、暗褐色オーク。 |
| **M_Barrel_IronHoop** | Metal_Rusty_Iron | Sound_Iron_Band_Clank | 錆びた鉄帯。Metallic 0.92、Roughness 0.52。 |
| **M_Barrel_TapWood** | Wood_Solid_Dry | Sound_Bung_Tap_Wood | 乾いた木栓。Roughness 0.85。 |
