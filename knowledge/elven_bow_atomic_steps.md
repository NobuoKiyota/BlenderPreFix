# エルフの狩猟長弓 (Elven Recurve Longbow) 最小単位モデリング手順 ＆ Why深層分析

森のエルフ猟兵が愛用する、優美なリカーブ湾曲を描くイチイ木材、彫金銀製ティップ、革巻きグリップ、ピンと張られた細い弦を持つ名弓の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Curve` > `Bezier` (弓幹カーブ / Bow Limb Curve) | 長さ: 1.4m (Z軸), S字リカーブ湾曲 | 矢を放つ際の強い反発力を生み出す伝統的リカーブボウの美しい曲線を定義。 |
| **#002** | カーブ上端を前方へ少し反り返らせる (`Recurve Tip`) | 弦のテンション保持 | リカーブ弓特有の弓弭（ゆはず）の逆反り形状。 |
| **#003** | Curve Data > `Bevel Geometry` > `Depth: 0.016m` | 楕円断面化 | 弦の張力方向（前後）に強く、横揺れを防ぐ扁平な弓幹断面を作成。 |
| **#004** | `Alt + C` or `Convert to Mesh` | メッシュ化 | モディファイアとグリップ詳細加工の準備。 |
| **#005** | `Shift + A` > `Mesh` > `Cylinder` (革巻きグリップ / Handle Grip) | Vertices: 16, Radius: 0.022m, Depth: 0.16m, Location: (0, 0, 0) | 弓の中心で射手が強く握り込むハンドルライザー部。 |
| **#006** | `Tab` (Edit Mode) > 中央部を指に合わせてわずかにくびれ成形 | 人間工学的グリップ | 長時間の狙撃でもブレない安定したエルゴノミクス形状。 |
| **#007** | `Modifier` > `Solidify` (薄手革巻き) | Thickness: 0.002m | 木材の上に巻き付けられた本革の厚みを表現。 |
| **#008** | `Shift + A` > `Mesh` > `Cone` (銀製弓弭 / Silver Limb Tip) | Vertices: 12, Radius1: 0.015m, Depth: 0.06m, Location: (0, 0.03m, 0.7m) | 弦を掛けるための銀製装飾ティップ金具。 |
| **#009** | `Tab` (Edit Mode) > 弦掛け溝（ストリングノッチ / Nock）を切り込み | 細いスリット凹み | 弦が外れないよう確実に保持するノッチ。 |
| **#010** | `Modifier` > `Mirror` (弓幹・ティップ) | Axis: Z, Clipping: ON | 上下の弓幹（Upper/Lower Limb）を完全対称にミラーリング。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (弓弦 / Bowstring) | Vertices: 8, Radius: 0.0015m, Depth: 1.36m, Location: (0, -0.06m, 0) | 上下のノッチを結んでピンと一直線に張られた強化麻/シルクの弓弦。 |
| **#012** | `Tab` (Edit Mode) > 弦の中央に矢番え用の補強巻き（サービング / Serving）作成 | 直径 0.003m に局所太らせ | 矢の矢筈（ノック）を正確に番えるセンターマーカー。 |
| **#013** | `Shift + A` > `Mesh` > `Plane` (弓幹のリーフ彫刻金具) | 銀製リーフプレート | グリップ上下の木幹に嵌め込まれたエルフ族のシンボル装飾。 |
| **#014** | `Modifier` > `Bevel` (全木製・金属エッジ) | Width: 0.002m, Segments: 2 | エッジを滑らかに丸め、曲線の美しさを極限まで引き出す。 |
| **#015** | `Material Assign` > `M_Bow_YewWood` | 弓幹本体 | 磨き上げられたイチイ（Yew）の銘木。Roughness 0.42、流麗な木目。 |
| **#016** | `Material Assign` > `M_Bow_SilverFittings` | ティップ金具・彫刻 | 彫金シルバー。Metallic 0.95, Roughness 0.22。 |
| **#017** | `Material Assign` > `M_Bow_GripLeather` | グリップ部 | ダークオリーブ色の柔らかいバックスキン革。Roughness 0.68。 |
| **#018** | `Material Assign` > `M_Bow_String` | 弓弦 | 高張力撚り糸。Roughness 0.55、わずかな繊維凹凸。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | 将来のアニメーション（弦引きボーンリグ）に備えて原点・スケールを正規化。 |
| **#020** | Cycles レンダリング (被写界深度 / DOF セットアップ) | F-Stop: 2.8, グリップにフォーカス | 美しい弓のカーブが背景に向かって優美にボケるシネマティック構図。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Bow_YewWood** | Wood_Flexible_Yew | Sound_Bow_Bend_Stress | 弾力性イチイ木材。Roughness 0.42、流れる木目ノイズ。 |
| **M_Bow_SilverFittings** | Metal_Silver_Chased | Sound_Silver_Ornament_Tap | 銀金具。Metallic 0.95、Roughness 0.22。 |
| **M_Bow_GripLeather** | Leather_Soft_Suede | Sound_Leather_Grip_Creak | 柔らかい革。Roughness 0.68、スエード微細バンプ。 |
| **M_Bow_String** | Fiber_High_Tension | Sound_Bowstring_Twang_Release | 高張力弦。Roughness 0.55、極細繊維ノイズ。 |
