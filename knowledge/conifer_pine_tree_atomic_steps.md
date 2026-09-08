# 常緑針葉樹 (Conifer Pine Tree) 最小単位モデリング手順 ＆ Why深層分析

高山や北欧の森に自生する、テーパーした木製幹と多層の針葉樹冠（コーン枝葉レイヤー）を持つ松・モミの木の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (樹幹 / Tree Trunk) | Vertices: 12, Radius: 0.16m, Depth: 3.2m, Location: (0, 0, 1.6m) | まっすぐ天に向かって伸びる針葉樹の主幹を作成。 |
| **#002** | `Tab` (Edit Mode) > 上端フェース選択 > `S: 0.25` | 先細りテーパー | 根元が太く梢に向かって細くなる自然な樹木の重力バランスを表現。 |
| **#003** | `Ctrl + R` (Loop Cut) > 幹に6分割カット > わずかにX/Yをジッター移動 | 有機的曲がり | 直線的すぎる人工感を消し、風雪に耐えた自然な幹のうねりを付与。 |
| **#004** | 根元フェースを選択 > `E` (Extrude) > 外側下向きに4方向に張り出し | 根張り (Buttress Roots) | 地面にしっかりと根を下ろす大樹の安定感を演出。 |
| **#005** | `Shift + A` > `Mesh` > `Cone` (最下層枝葉 / Tier 1 Foliage) | Vertices: 10, Radius1: 1.1m, Depth: 0.85m, Location: (0, 0, 1.3m) | 最も幅広く傘状に広がる最下段の針葉コーンを作成。 |
| **#006** | `Tab` (Edit Mode) > 底面エッジループを選択 > `Alt + S` (Shrink/Fatten) | 傘の垂れ下がり | 雪や重みで枝葉の外周が下垂したリアルなモミの木のシルエット。 |
| **#007** | コーン下端の頂点を1つ飛ばしで内側に窪ませる (Star-shape) | ギザギザ枝先 | 円錐の滑らかな輪郭を壊し、放射状に突き出る枝葉の塊を表現。 |
| **#008** | `Shift + D` で複製 > `Z: 1.9m`, `S: 0.85` (Tier 2 Foliage) | 第2段枝葉 | 上に向かって段階的に直径を絞りながら重ねる。 |
| **#009** | `Shift + D` で複製 > `Z: 2.45m`, `S: 0.7` (Tier 3 Foliage) | 第3段枝葉 | 中層の針葉レイヤーを密に配置。 |
| **#010** | `Shift + D` で複製 > `Z: 2.9m`, `S: 0.55` (Tier 4 Foliage) | 第4段枝葉 | 梢手前の密な枝葉。 |
| **#011** | `Shift + D` で複製 > `Z: 3.3m`, `S: 0.38` (Tier 5 Foliage Top) | 梢のトップスパイク | 針葉樹特有の鋭利な頂点（Apex）を完成。 |
| **#012** | 各層のZ軸回転を少しずつずらす (`R > Z: 18 deg`) | 不揃いな重なり | 下層と上層の枝が一直線に並ばず、日光を均等に浴びる互生配置を再現。 |
| **#013** | `Modifier` > `Displace` (葉群全体) > Voronoi Texture | Strength: 0.04m | 個々の針葉の束（Needle Clusters）の細かな凹凸をプロシージャル生成。 |
| **#014** | `Modifier` > `Bevel` (幹エッジ) | Width: 0.005m | 樹皮の筋の角張りを適度に丸める。 |
| **#015** | `Material Assign` > `M_Pine_Bark` | 樹幹・根 | 深い赤褐色の松樹皮。Roughness 0.88、深い縦溝バンプ。 |
| **#016** | `Material Assign` > `M_Pine_Needles` | 5層の枝葉コーン | 深緑の針葉（BaseColor: 0.08, 0.22, 0.1）、Subsurface 0.15、葉の光透過。 |
| **#017** | 幹と全枝葉を選択 > `Ctrl + J` | 単一メッシュ結合 | ゲームエンジンでのドローコール削減とLOD管理の最適化。 |
| **#018** | 地面に落ちた松ぼっくり (`Icosphere`, 半径 0.03m) を足元に配置 | 自然な環境アクセント | 樹木単体だけでなく、周囲の生態系を感じさせるプロップ配置。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | 原点を地面設置面 (Z=0) に固定。 |
| **#020** | Cycles レンダリング (順光＋半逆光リムライト) | サブサーフェス透過光 | 逆光によって針葉のエッジが明るく輝く自然光ライティング。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Pine_Bark** | Wood_Bark_Rough | Sound_Bark_Pine_Impact | 松樹皮。Roughness 0.88、縦溝Noiseバンプ、赤褐色。 |
| **M_Pine_Needles** | Foliage_Needles_Dry | Sound_Pine_Branch_Rustle | 針葉。深緑、Subsurface 0.15、粗さ 0.55。 |
| **M_Forest_Ground** | Organic_Soil_PineNeedles | Sound_Footstep_PineNeedles | 落葉土壌。Roughness 0.95。 |
