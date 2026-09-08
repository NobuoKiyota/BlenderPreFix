# 【AAA シネマティック】ドワーフの戦闘斧 (AAA Cinematic Battleaxe) 最小単位モデリング手順 ＆ Why深層分析

映画シネマティック・ヒーロープロップ用アセット。積層鍛造ダマスカス鋼、微小な研ぎ傷、革巻きの縫い目、黄金に輝く古代ルーン象嵌を持つ双刃戦斧。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (八角形シャフト / Octagonal Shaft) | Vertices: 8, Radius: 0.035m, Depth: 1.2m, Location: (0, 0, 0.6m) | 手になじむ伝統的なドワーフ工芸の八角形木製柄を生成。 |
| **#002** | `Tab` (Edit Mode) > 上下に微小テーパー > ベベル（2分割） | 角の美しい面取り | 金属と結合する上部を太く、下部を握りやすく成形。 |
| **#003** | `Shift + A` > `Mesh` > `Cube` (ソケット金具 / Central Axe Eye) | Size: 0.16m, Location: (0, 0, 1.0m) | 刃を柄に固定する強固な鉄製ソケット。 |
| **#004** | `Tab` (Edit Mode) > 正面フェース選択 > `E` で双刃アックスブレードを押し出し | ワイドな三日月刃 | 左右対称に広がる肉厚なドワーフ特有のヘビーブレード。 |
| **#005** | 刃先に向かって多段ベベル押し出し > 鋭利なカッティングエッジ | 肉薄ベベル刃 | 研ぎ澄まされた刃先の鋭利さと、中央の肉厚な耐久性を両立。 |
| **#006** | `Modifier` > `Mirror` | Axis: X, Clipping: ON | 双刃（Double-bitted）ブレードの完全対称性。 |
| **#007** | 刃の表面に幾何学的なルーン文字溝をナイフツール (`K`) で彫り込み | 深さ: 0.006m の溝 | 魔法の力を込めるための古代ドワーフ文字のインレイ溝。 |
| **#008** | `Shift + A` > `Mesh` > `Cone` (頂点スパイク / Crown Spike) | Vertices: 8, Radius1: 0.028m, Depth: 0.22m, Location: (0, 0, 1.25m) | 刺突攻撃用の強固なスチールスパイク。 |
| **#009** | `Shift + A` > `Mesh` > `Cylinder` (革巻きグリップ / Leather Wrap) | Vertices: 16, Radius: 0.038m, Depth: 0.5m, Location: (0, 0, 0.4m) | 滑り止めの厚手レザーラップ。 |
| **#010** | 革巻きに沿ってスパイラル状のステッチ（縫い目）リブをモデリング | 縫い目の微細立体 | 使い込まれた本革の合わせ目と職人の手縫い感を表現。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (真鍮ポメル / Brass Pommel) | Vertices: 8, Radius: 0.055m, Depth: 0.08m, Location: (0, 0, 0.03m) | 重量を安定させる八角形の真鍮カウンターウェイト。 |
| **#012** | `Modifier` > `Bevel` (全金属エッジ) | Width: 0.002m, Segments: 3 | 実物の金属製品と同じ、リアルな光の反射ハイライトが入るラウンドエッジ。 |
| **#013** | `Material Assign` > `M_AAA_Axe_Damascus` | 双刃ブレード | 積層ダマスカス鋼（Metallic: 0.96, Roughness: 0.25, 波状Waveバンプ, 異方性反射）。 |
| **#014** | `Material Assign` > `M_AAA_Axe_RuneGold` | ルーン彫刻溝 | 黄金色に眩しく輝くルーン発光（Emission: 8.0, 暖色ゴールド）。 |
| **#015** | `Material Assign` > `M_AAA_Axe_OakWood` | 八角形シャフト | 深みのあるダークオーク古材。縦木目バンプ。 |
| **#016** | `Material Assign` > `M_AAA_Axe_StitchedLeather` | グリップ部 | 牛革（Roughness: 0.62, ステッチ縫い目バンプ, 暗褐色）。 |
| **#017** | `Material Assign` > `M_AAA_Axe_BrassPommel` | ポメル | 鈍く光る彫金真鍮。Metallic: 0.94, Roughness: 0.32。 |
| **#018** | 刃先に微小な研ぎ傷（Fine Scratches）と打痕バンプをプロシージャル合成 | 実戦の痕跡 | 工場出荷の新品ではなく、幾多の戦いをくぐり抜けた名兵器の説得力。 |
| **#019** | 3点スタジオ照明（金属のヘアライン反射を魅せる縦長エリアライト） | 映画ポスター構図 | 刃先のシャープな反射とルーンの金光を劇的に演出。 |
| **#020** | Cycles パストレーシングレンダリング (Samples: 32) | シネマティックCycles | ヒーロープロップ（主役武具）として完璧な画質を描写。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_AAA_Axe_Damascus** | Metal_Sharp_Heavy_Damascus | Sound_Axe_Blade_Heavy_Clash | 積層ダマスカス鋼。Metallic 0.96、波状Waveバンプ。 |
| **M_AAA_Axe_RuneGold** | Magic_Runic_Gold_Emission | Sound_Axe_Rune_Awaken_Chord | 黄金ルーン発光。Emission 8.0、金光。 |
| **M_AAA_Axe_OakWood** | Wood_Solid_Aged_Oak | Sound_Axe_Wood_Handle_Hit | オーク柄。Roughness 0.75。 |
| **M_AAA_Axe_StitchedLeather** | Leather_Heavy_Stitched | Sound_Axe_Leather_Grip_Tight | 縫製革。Roughness 0.62。 |
| **M_AAA_Axe_BrassPommel** | Metal_Brass_Heavy | Sound_Axe_Pommel_Strike | 真鍮ポメル。Metallic 0.94。 |
