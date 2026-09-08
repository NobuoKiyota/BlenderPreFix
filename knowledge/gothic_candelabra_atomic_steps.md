# ゴシック真鍮燭台 (Gothic Candelabra) 最小単位モデリング手順 ＆ Why深層分析

中世の大聖堂や洋館に灯る、溶け落ちた蝋と揺らめく3本炎を持つアンティーク真鍮燭台の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (台座ベース / Base) | Vertices: 24, Radius: 0.18m, Depth: 0.04m | 重い真鍮鋳造の低重心ベースを作成し、燭台の安定を確保。 |
| **#002** | `Tab` (Edit Mode) > 上面フェース選択 > `I` (Inset) > `E` (Extrude) > `Z: 0.06m` | 3段ステップ台座 | ゴシック建築の柱頭のような階層的な段差装飾を形成。 |
| **#003** | `Shift + A` > `Mesh` > `Cylinder` (主支柱 / Central Stem) | Vertices: 16, Radius: 0.035m, Depth: 0.5m, Location: (0, 0, 0.35m) | 中央の蝋燭へ垂直に伸びるセンターピラー。 |
| **#004** | `Ctrl + R` > 支柱に4分割カット > スケール拡縮 | くびれとバルジ（膨らみ） | バロック・ゴシック様式特有の優美なくびれと装飾リングを作成。 |
| **#005** | `Shift + A` > `Curve` > `Bezier` (アームカーブ / Arm Curve) | S字型カーブ、Radius: 0.15m | 左右に広がる優美なS字枝アームのパスを定義。 |
| **#006** | Curve Data > `Bevel` > `Depth: 0.012m`, Resolution: 4 | 丸パイプ化 | ベジェカーブを立体的な真鍮パイプアームへ変換。 |
| **#007** | `Alt + C` or `Convert to Mesh` | メッシュ化 | モディファイアと結合可能にする。 |
| **#008** | `Shift + A` > `Mesh` > `Cylinder` (受け皿 / Bobeche) | Vertices: 24, Radius: 0.075m, Depth: 0.02m | 溶けた蝋を受け止める浅い皿を作成。 |
| **#009** | `Tab` (Edit Mode) > `I` > `E: -0.015m` | くぼみ形成 | 蝋がこぼれ落ちないボウル状の受け皿に成形。 |
| **#010** | アーム先端と支柱中央に受け皿を配置 (計3箇所) | Location: 中央 (Z:0.65m), 左右 (X:±0.22m, Z:0.58m) | クラシックな3灯式（3-candle）レイアウトを構築。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (蝋燭 / Wax Candle) | Vertices: 16, Radius: 0.024m, Depth: 0.22m | 各受け皿の上に立つ円柱蝋燭の土台。 |
| **#012** | `Tab` (Edit Mode) > 上端頂点を不揃いに歪ませる | ランダムZ移動 | 火の熱で不均一に溶け窪んだ蝋燭のトップ面を表現。 |
| **#013** | `Shift + A` > `Mesh` > `Icosphere` (蝋の滴り / Wax Drips) | Subdivisions: 1, Radius: 0.008m | 側面を受け皿に向かって垂れ流れる溶け蝋のしずくを作成。 |
| **#014** | 蝋燭の側面に沿って複数複製配置 > `Ctrl + J` で結合 | スヌーズな滴り結合 | 長時間灯り続けたヴィンテージ燭台のドラマチックな経年変化。 |
| **#015** | `Shift + A` > `Mesh` > `Cylinder` (芯 / Candle Wick) | Vertices: 8, Radius: 0.002m, Depth: 0.025m | 炭化した黒い木綿の芯を蝋燭頂点に配置。 |
| **#016** | `Shift + A` > `Mesh` > `UV Sphere` (炎メッシュ / Flame) | Segments: 12, Rings: 8, Radius: 0.02m | 炎のティアドロップ形状。上端頂点を `G + Z` で引っ張り尖らせる。 |
| **#017** | `Modifier` > `Subdivision Surface` (蝋燭と皿) | Level: 1 | 蝋のなめらかな曲面と真鍮の丸みを強調。 |
| **#018** | `Material Assign` > `M_Candle_Brass` | 台座・支柱・アーム・受け皿 | 鈍い黄金光沢を放つアンティーク真鍮。Roughness 0.32。 |
| **#019** | `Material Assign` > `M_Candle_Wax` | 蝋燭・溶け蝋 | 半透明の蜜蝋（Subsurface Scattering: 0.35）。 |
| **#020** | `Material Assign` > `M_Candle_Flame` | 炎メッシュ | 内側が白熱、外側が暖色オレンジのグラデーション発光（Emission: 12.0）。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Candle_Brass** | Metal_Brass_Resonant | Sound_Candelabra_Chime | 真鍮。Metallic 0.92、Roughness 0.32、わずかな酸化バンプ。 |
| **M_Candle_Wax** | Wax_Soft_Translucent | Sound_Wax_Drop_Thud | 蝋。BaseColor 薄黄クリーム、SSS 0.35、Roughness 0.45。 |
| **M_Candle_Flame** | Fire_Candle_Flicker | Sound_Candle_Flicker_Loop | 炎発光。Emission 12.0、ColorRamp (白熱芯〜濃オレンジ)。 |
