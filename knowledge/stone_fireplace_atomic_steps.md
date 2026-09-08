# 古城の石造り暖炉 (Castle Stone Fireplace) 最小単位モデリング手順 ＆ Why深層分析

中世の古城大広間に築かれた、荒削りの石積みアーチ、重厚なマントルピース天板、鋳鉄の薪受け格子、燃える薪と熾火を持つ暖炉の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` (暖炉主外郭 / Fireplace Frame) | Scale: (1.6m, 0.6m, 1.4m), Location: (0, 0, 0.7m) | 石造り暖炉全体のバウンディングボックスを作成。 |
| **#002** | `Tab` (Edit Mode) > 正面フェース選択 > `I` > `E: -0.45m` (火室の掘り込み) | 開口部: (1.0m x 0.9m) | 薪を組んで燃やす燃焼室（Firebox）の内部キャビティを形成。 |
| **#003** | 開口部上端に `Ctrl + B` (Bevel: 6分割) | 半円アーチ化 | 中世ゴシック建築の堅牢な石造りアーチ（Arch Vault）を成形。 |
| **#004** | `Shift + A` > `Mesh` > `Cube` (マントルピース天板 / Mantel Shelf) | Scale: (1.8m, 0.7m, 0.12m), Location: (0, 0.05m, 1.46m) | 燭台や時計を飾る暖炉最上部の重厚な飾り棚天板。 |
| **#005** | 天板の下部エッジにモールディング面取り (`Ctrl + B`: 3段) | 伝統的モールディング | 宮廷や貴族邸の格式高いクラシック装飾を表現。 |
| **#006** | `Shift + A` > `Mesh` > `Cube` (炉床ベース / Hearth Stone) | Scale: (1.9m, 0.9m, 0.08m), Location: (0, 0.15m, 0.04m) | 火の粉から床を守るため前方に張り出した石畳の炉床。 |
| **#007** | ナイフツール (`K`) で正面の石柱とアーチに石積み目地を分割 | ブロック目地溝 | 1つの塊ではなく、個別に切り出された石材が積み上がっている構造を表現。 |
| **#008** | 目地エッジを選択して `Ctrl + B` > 内側押し出し (`E`) | 深さ 0.008m の目地窪み | 石と石の間のモルタル目地（Mortar Seams）の立体感を形成。 |
| **#009** | `Shift + A` > `Mesh` > `Cube` (薪受け格子 / Cast Iron Andiron) | Scale: (0.6m, 0.35m, 0.18m), Location: (0, -0.15m, 0.15m) | 薪を床から浮かせて下から空気を通す鋳鉄製の薪置き台（ファイアドッグ）。 |
| **#010** | 格子状にバーを抜き、前面に装飾フィニアル（鉄球スパイク）を追加 | 頑丈な鉄格子 | 火力と薪の重量を支える無骨な鍛造鉄の機能美。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (燃える薪 / Firewood Logs) | Vertices: 12, Radius: 0.06m, Depth: 0.5m | 井桁（いげた）状にクロスして組まれた割薪の丸太。 |
| **#012** | 3本の薪を角度を変えて自然に交差配置 (`Shift + D` & Rotate) | ランダム交差 | 崩れ落ちそうに燃えるリアルな焚火の組み方。 |
| **#013** | `Shift + A` > `Mesh` > `Icosphere` (熾火の炭床 / Embers Bed) | Scale: (0.4m, 0.25m, 0.06m), Location: (0, -0.15m, 0.1m) | 薪の真下で赤熱する木炭・灰・熾火（おきび）の塊。 |
| **#014** | `Modifier` > `Displace` (石表面の荒削りノイズ) | Strength: 0.008m, Noise Texture | つるりとしたCG感を消し、ノミで削られた天然石のざらつきを再現。 |
| **#015** | `Material Assign` > `M_Fireplace_Stone` | 暖炉本体・天板・炉床 | 風化した石灰岩ブロック。Roughness 0.92、モルタル目地バンプ。 |
| **#016** | `Material Assign` > `M_Fireplace_CastIron` | 薪受け格子 | 煤（すす）けた黒鋳鉄。Metallic 0.9、Roughness 0.62。 |
| **#017** | `Material Assign` > `M_Fireplace_CharredLogs` | 薪丸太 | 表面が黒焦げに炭化した木肌。Roughness 0.88。 |
| **#018** | `Material Assign` > `M_Fireplace_Embers` | 熾火の炭床 | 内部から赤橙色に高温発光（Emission: 12.0, Color: オレンジ〜深紅）。 |
| **#019** | 火室中心にポイントライトを配置 (暖色 2000K, 450W) | 暖かい火の光 | 暖炉の火室の壁と部屋の床を赤く照らし出すリアルな間接照明。 |
| **#020** | Cycles パストレーシングレンダリング | Samples: 32, Denoise: ON | 熾火の間接光が石積みの凹凸に落とす温かな陰影を正確に計算。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Fireplace_Stone** | Stone_Masonry_Heavy | Sound_Stone_Fireplace_Impact | 粗削り石材。Roughness 0.92、岩肌プロシージャルバンプ。 |
| **M_Fireplace_CastIron** | Metal_Cast_Iron_Black | Sound_Grate_Iron_Rattle | 黒鋳鉄。Metallic 0.9、Roughness 0.62。 |
| **M_Fireplace_CharredLogs** | Wood_Charred_Burnt | Sound_Firewood_Crack_Snap | 炭化木材。Roughness 0.88、ひび割れ炭化バンプ。 |
| **M_Fireplace_Embers** | Fire_Embers_Glow | Sound_Fire_Crackling_Loop | 熾火発光。Emission 12.0、赤橙グラデーション。 |
