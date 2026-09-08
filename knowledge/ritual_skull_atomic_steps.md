# 儀式の古代頭骨 (Ritual Skull Prop) 最小単位モデリング手順 ＆ Why深層分析

ダークファンタジーの祭壇に安置された、風化した骨質、額に刻印された呪詛ルーン、眼窩に輝くエメラルド発光を持つ頭蓋骨の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `UV Sphere` (頭蓋骨頭頂 / Cranium) | Segments: 24, Rings: 16, Radius: 0.18m, Location: (0, 0, 0.25m) | 脳を包む頭蓋上部の滑らかな卵型ドームを作成。 |
| **#002** | `Tab` (Edit Mode) > `S` > `Y: 1.15, X: 0.85` | 前後に長く左右に狭い頭蓋比率 | 人間の解剖学的な頭蓋骨プロポーションにアライン。 |
| **#003** | `Shift + A` > `Mesh` > `Cube` (顔面・上顎 / Facial Bones) | Scale: (0.12m, 0.1m, 0.14m), Location: (0, -0.08m, 0.12m) | 頬骨（Zygomatic）と上顎（Maxilla）の土台ブロックを作成。 |
| **#004** | `Ctrl + J` で頭頂と顔面を結合 > `Modifier` > `Voxel Remesh` | Voxel Size: 0.015m | 2つの形状を滑らかに融合し、1つの連続したメッシュに再構築。 |
| **#005** | スカルプトモード (`Ctrl + Tab` > Sculpt) > ブラシ `Draw` & `Clay Strips` | 頬骨の隆起とこめかみの窪み | 解剖学的なランドマーク（頬骨弓と側頭窩）を彫り出し。 |
| **#006** | ブラシ `Grab` > 左右対称（Symmetry: X）で眼窩（Eye Sockets）を深く押し込む | 左右2つの深い凹み | 頭蓋骨の象徴である暗い眼窩キャビティを作成。 |
| **#007** | 鼻腔（Nasal Cavity）の逆ハート型スリットを押し込み彫刻 | 逆三角形の深い穴 | 梨状口（鼻の骨開口部）を成形。 |
| **#008** | `Shift + A` > `Mesh` > `Cube` (歯列 / Teeth Block) | Scale: (0.012m, 0.012m, 0.022m) | 上顎の門歯・犬歯・小臼歯の個別モデルの土台。 |
| **#009** | 歯をU字型アーチに沿って8本配置 > わずかに不揃いに傾ける | 不揃いな歯列 | 長年埋没していたアンデッド・頭骨の不気味なリアルさを強調。 |
| **#010** | `Shift + A` > `Mesh` > `UV Sphere` (眼窩のエメラルドオーブ / Soul Gem) | Radius: 0.035m, 左右の眼窩の奥深くに配置 | 眼窩の暗闇の中で怪しく輝くエメラルドグリーンの魂の光彩。 |
| **#011** | 額部分にナイフツール (`K`) で古代ルーン刻印のスリットを刻む | 星型/三日月型の幾何学ルーン | 暗黒魔術の儀式で刻み込まれた呪詛の文様をジオメトリ化。 |
| **#012** | `Modifier` > `Displace` (微細Voronoiノイズ) | Strength: 0.002m | 骨の表面にある微細な多孔質（Porous Bone）のザラザラ感を生成。 |
| **#013** | `Modifier` > `Subdivision Surface` | Level: 1 | スカルプト面の角張りを抑え、滑らかな有機的骨質に仕上げる。 |
| **#014** | `Material Assign` > `M_Skull_Bone` | 頭蓋骨本体・歯 | 風化骨（Subsurface: 0.22, アイボリー褐色, Roughness: 0.65）。 |
| **#015** | `Material Assign` > `M_Skull_RuneGlow` | 額のルーン溝 | 脈動するエメラルド発光（Emission: 8.0, 鮮やかなグリーン）。 |
| **#016** | `Material Assign` > `M_Skull_SoulEye` | 眼窩オーブ | 神秘的な発光（Emission: 5.0）。 |
| **#017** | `Material Assign` > `M_Skull_DarkSocket` | 眼窩・鼻腔の内壁 | 影を強調する完全な暗闇ブラック（Roughness: 0.95）。 |
| **#018** | キーライト配置 (真上斜め前方からの冷たい月光) | Color: 薄青, Energy: 150W | 骨の彫刻的な陰影と眼窩の落ち込みを際立たせるドラマチック照明。 |
| **#019** | アンビエントオクルージョン設定 | Distance: 0.2m | 歯の間や骨の裂け目に深い自然な影を落とす。 |
| **#020** | Cycles レンダリング (デノイズ ON) | Samples: 32 | サブサーフェス・スキャッタリング（SSS）による骨の奥深い透け感を計算。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Skull_Bone** | Bone_Aged_Solid | Sound_Skull_Roll_Bone_Hit | 風化骨。SSS 0.22、Roughness 0.65、アイボリー褐色。 |
| **M_Skull_RuneGlow** | Magic_Necromancy_Green | Sound_Rune_Whisper_Loop | 呪詛エメラルド発光。Emission 8.0、高輝度グリーン。 |
| **M_Skull_DarkSocket** | Shadow_Cavity_Dark | Sound_Dark_Ambiance | 陰影。BaseColor (0.02, 0.02, 0.03)、粗さ 0.95。 |
