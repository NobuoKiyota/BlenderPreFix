# スチームパンク気圧計 (Steampunk Pressure Gauge) 最小単位モデリング手順 ＆ Why深層分析

真鍮製ハウジング、アイボリーの目盛り盤、極細の赤銅指針、背面露出ギア、接続パイプを持つヴィクトリア朝蒸気圧計の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (メーター本体 / Main Casing) | Vertices: 32, Radius: 0.25m, Depth: 0.08m | 真鍮鋳造の丸型メーター外郭ケースを作成。 |
| **#002** | `Tab` (Edit Mode) > 正面フェース選択 > `I` (Inset: 0.025m) > `E` (Extrude: -0.04m) | ガラス嵌め込み溝 | 文字盤と指針を収めるキャビティ（空洞）を掘り下げ。 |
| **#003** | 外周リムに `Ctrl + B` (Bevel: 3分割) | リム面取り | 高級精密機器特有の美しいラウンドエッジを形成。 |
| **#004** | 外周に等間隔で6本の六角ボルト (`Cylinder`, Verts: 6) を配置 | 配列配置 | 高圧蒸気パイプラインに耐える強固なボルト締め構造。 |
| **#005** | `Shift + A` > `Mesh` > `Circle` (文字盤プレート / Dial Face) | Vertices: 32, Radius: 0.22m, Location: (0, -0.015m, 0) | 目盛り（PSI/BAR）が刻まれる金属文字盤。 |
| **#006** | `F` (Fill) で面張り > スムースシェード | 平坦フェース | 針の回転の背景となるクリーンな円形プレート。 |
| **#007** | `Shift + A` > `Mesh` > `Cylinder` (指針ピボット / Center Pin) | Radius: 0.012m, Depth: 0.02m | 指針を回転可能に支持するセンターシャフト。 |
| **#008** | `Shift + A` > `Mesh` > `Cube` (気圧指針 / Needle Pointer) | Scale: (0.004m, 0.16m, 0.002m) | 蒸気圧を指し示す長針。 |
| **#009** | `Tab` (Edit Mode) > 先端を三角形にテーパー > 後端にひし形カウンターウェイト | 矢印型精密針 | 繊細なアンティーク懐中時計・計器らしい優美な針シルエット。 |
| **#010** | 原点をピボット中心に設定 > `R > Z: -45 deg` | 危険域手前ポーズ | 針が現在の気圧値（中高圧）をリアルに指し示すようにセット。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (ガラスカバー / Glass Lens) | Vertices: 32, Radius: 0.225m, Depth: 0.005m, Location: (0, 0.02m, 0) | 指針を埃と蒸気から守る前面の凸レンズ型ガラス風防。 |
| **#012** | `Tab` (Edit Mode) > 前面をわずかにドーム状に押し出し | 凸レンズ曲面 | 周囲のスタジオライトを美しく反射・屈折させる。 |
| **#013** | `Shift + A` > `Mesh` > `Cylinder` (接続銅パイプ / Inlet Pipe) | Vertices: 16, Radius: 0.035m, Depth: 0.2m, Location: (0, 0, -0.3m) | ボイラーから蒸気を導く下部インレットパイプ。 |
| **#014** | `Shift + A` > `Mesh` > `Torus` (パイプ継手フランジ / Pipe Flange) | Major: 0.048m, Minor: 0.01m | メーター本体と配管を接続する重厚なフランジ結合部。 |
| **#015** | `Shift + A` > `Mesh` > `Cylinder` (背面歯車 / Brass Gear) | Vertices: 12, Radius: 0.08m, Depth: 0.015m, Location: (0, -0.06m, 0.05m) | 内部機構を露出させるスチームパンク特有の露出メカディテール。 |
| **#016** | 歯車エッジに押し出しで歯（Teeth）を作成 | 12枚歯のギア | 機械的な情報密度と説得力を劇的に向上。 |
| **#017** | `Material Assign` > `M_Gauge_Brass` | 本体ケース・ボルト・歯車 | 磨かれた真鍮。Metallic 0.95, Roughness 0.25。 |
| **#018** | `Material Assign` > `M_Gauge_Copper` | 接続パイプ・フランジ | 赤みのある銅パイプ。Metallic 0.95, Roughness 0.32。 |
| **#019** | `Material Assign` > `M_Gauge_Dial` & `M_Gauge_Needle` | 文字盤・指針 | アイボリー白文字盤（目盛り線バンプ）と深紅の塗装指針。 |
| **#020** | `Material Assign` > `M_Gauge_Glass` | 前面レンズ | クリアガラス。Transmission 1.0, IOR 1.50, Roughness 0.02。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Gauge_Brass** | Metal_Brass_Machined | Sound_Gauge_Tick_Mechanical | 精密真鍮。Metallic 0.95、Roughness 0.25。 |
| **M_Gauge_Copper** | Metal_Copper_Pipe | Sound_Steam_Hiss_Pipe | 銅パイプ。Metallic 0.95、Roughness 0.32、赤銅色。 |
| **M_Gauge_Glass** | Glass_Thin_Lens | Sound_Gauge_Glass_Tap | 薄手レンズ。Transmission 1.0、IOR 1.50、クリア。 |
| **M_Gauge_Needle** | Metal_Coated_Red | Sound_Needle_Jitter_Twitch | 赤塗装針。Roughness 0.4、BaseColor (0.8, 0.1, 0.05)。 |
