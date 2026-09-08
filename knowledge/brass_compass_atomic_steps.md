# アンティーク真鍮コンパス (Antique Brass Compass) 最小単位モデリング手順 ＆ Why深層分析

航海・冒険・スチームパンクゲームの象徴アイテム「アンティーク真鍮コンパス（段差切削真鍮ケース＆ガラス風防＆ダイヤ型磁針＆吊り下げリング）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` | Vertices: 48, Radius: 0.25m, Depth: 0.08m, Z: 0.04m | 真鍮削り出しの本体ケース（Housing）となる円筒を生成。 |
| **#002** | `Tab` (Edit Mode) > 上面フェースを選択 > `I` (Inset) | Thickness: 0.025m | ガラス蓋と文字盤を納める内側キャビティの枠取り。 |
| **#003** | `E` (Extrude) > `Z` | -0.05m | 磁針が自由に回転するための内部空間（チャンバー）を掘り下げる。 |
| **#004** | `Ctrl + B` (Bevel) | 外周エッジを選択, Width: 0.008m, Segments: 3 | 旋盤で滑らかに面取りされたクラシック真鍮工芸の質感を演出。 |
| **#005** | `Shift + A` > `Mesh` > `Cylinder` (文字盤プレート) | Vertices: 48, Radius: 0.22m, Depth: 0.005m, Z: 0.015m | 方位目盛り（Compass Rose）が刻まれる底板。 |
| **#006** | `Material Assign` > `M_Compass_Dial` | 文字盤に適用 | 経年変化したヴィンテージ紙/エナメル陶器のオフホワイト質感。 |
| **#007** | `Shift + A` > `Mesh` > `Cylinder` (中央ピボット軸) | Vertices: 16, Radius: 0.012m, Depth: 0.035m, Z: 0.03m | 磁針を1点で支える中央軸受（Pivot Pin）。 |
| **#008** | `Shift + A` > `Mesh` > `Cube` (磁針 - 北側) | Size: 1.0m, Location: (0, 0.09m, 0.045m) | 赤く染められた北針（North Pointer）の素材。 |
| **#009** | `S` > `X: 0.028, Y: 0.18, Z: 0.004` | 薄い菱形（Diamond Needle） | 空気抵抗が少なく、磁力で鋭敏に揺れる極薄金属板。 |
| **#010** | `Tab` (Edit Mode) > 先端頂点を中央集約 (`M > At Center`) | 矢印型切っ先 | 北を指し示すシャープなポインターを形成。 |
| **#011** | `Material Assign` > 赤色真鍮 (`M_Compass_Needle_N`) | 北針に適用 | ヴィンテージの深紅ラッカー塗装。 |
| **#012** | `Shift + D` > `R` > `Z: 180` (南針) | Location: (0, -0.09m, 0.045m) | 南を指し示す対向針（South Pointer）を複製配置。 |
| **#013** | `Material Assign` > 磨き真鍮/青色 (`M_Compass_Needle_S`) | 南針に適用 | 北と南の視認性を分ける伝統的なツートンデザイン。 |
| **#014** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (ガラス風防) | Vertices: 48, Radius: 0.225m, Depth: 0.008m, Z: 0.065m | 内部を埃や風から守る透明ガラスカバー。 |
| **#015** | `Material Assign` > `M_Compass_Glass` | ガラス円盤に適用 | 高透過率（Transmission 1.0）、IOR 1.52、微細なフレネル反射。 |
| **#016** | `Shift + A` > `Mesh` > `Torus` (吊り下げリング) | Major: 0.06m, Minor: 0.009m, Location: (0, 0.28m, 0.04m) | ポケットウォッチチェーンや革紐を通すための上部吊り環。 |
| **#017** | `R` > `X: 90` | 縦向きにリングを配置 | 携帯用羅針盤の本格的な外観を完成。 |
| **#018** | `Modifier` > `Bevel` (ケース・リング) | Width: 0.003m, Segments: 2 | 真鍮エッジに上品なゴールドの光の筋（スペキュラ）を付与。 |
| **#019** | `Material Assign` > `M_Compass_Brass` | ケース、軸、リングに適用 | 経年変化によるわずかなパティナ（くすみ）を含む本物の真鍮シェーダー。 |
| **#020** | `Shade Auto Smooth` | 全パーツに適用 | 滑らかな真鍮の曲面と文字盤のフラット感を完璧に両立。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Compass_Brass** | `Metal_Light` | `Sound_Brass_Click` | 磨き真鍮 (RGB: 0.88, 0.72, 0.28), Metallic 0.98, Roughness 0.26。 |
| **M_Compass_Needle** | `Metal_Light` | `Sound_Needle_Jiggle` | 磁針。回転・揺れ時の微細な金属擦れ・ピボットチクタク音。 |
| **M_Compass_Glass** | `Glass` | `Sound_Glass_Tap_Sharp` | 高透明度ガラス。爪や指先で軽くタップした時の高いピン音。 |
| **M_Compass_Dial** | `Ceramic_Paper` | `Sound_Compass_Open` | 文字盤。エナメル白 (0.92, 0.90, 0.82), 粗さ 0.55。 |
