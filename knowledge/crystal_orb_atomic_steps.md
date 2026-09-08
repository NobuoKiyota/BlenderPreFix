# 予言者のクリスタルオーブ (Prophet's Crystal Orb) 最小単位モデリング手順 ＆ Why深層分析

真球の完全無欠な水晶球、内部に渦巻く星雲プラズマ、三叉のドラゴンクロー青銅台座を持つ神秘の占いオーブの全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `UV Sphere` (水晶球 / Crystal Sphere) | Segments: 48, Rings: 32, Radius: 0.35m, Location: (0, 0, 0.65m) | 物理屈折（IOR）を完全に均一に計算するため、高解像度の完全真球を生成。 |
| **#002** | `Right Click` > `Shade Smooth` | スムーズシェード | 面の分割線を完全に消去し、光学レンズ並みのクリアな鏡面を担保。 |
| **#003** | `Shift + A` > `Mesh` > `Icosphere` (星雲コア / Nebula Core) | Subdivisions: 3, Radius: 0.18m, Location: (0, 0, 0.65m) | 球の内部でフワフワと渦を巻く魔法の銀河・プラズマエミッターを作成。 |
| **#004** | `Modifier` > `Displace` > Texture: Clouds | Strength: 0.08m, Size: 0.25m | 完全な球を崩し、有機的な星雲ガスのような不規則なうねりを付与。 |
| **#005** | `Shift + A` > `Mesh` > `Cylinder` (台座ベース / Stand Base) | Vertices: 24, Radius: 0.26m, Depth: 0.05m, Location: (0, 0, 0.025m) | 重厚な青銅台座のベースリングを作成。 |
| **#006** | `Tab` (Edit Mode) > `I` > `E` でステップモールディング成形 | 段差ベベル | ルネサンス期の天文機器のようなクラシカルな多段ステップ形状を形成。 |
| **#007** | `Shift + A` > `Curve` > `Bezier` (ドラゴンクロー脚 / Dragon Claw Leg) | 3Dカーブ、S字湾曲 | 台座から立ち上がり水晶球を下から抱え込む3本のアームの1本を定義。 |
| **#008** | Curve Data > `Bevel Geometry` > `Depth: 0.022m` | 肉厚化 | 鋳造ブロンズの太い爪アームを作成。 |
| **#009** | 爪の先端に円錐（クロー）を追加して結合 | スパイク爪 | 球の赤道直下をしっかり支える爪先のアクセント。 |
| **#010** | `Modifier` > `Array` (Object Offset: 120°回転Empty) | Count: 3 | 120度間隔で完全な3点支持トライポッドアームを生成。 |
| **#011** | `Shift + A` > `Mesh` > `Torus` (支持リング / Support Ring) | Major: 0.28m, Minor: 0.018m, Location: (0, 0, 0.42m) | 3本の爪を中間で結束し剛性を高める真鍮リング。 |
| **#012** | `Shift + A` > `Mesh` > `Icosphere` (台座の宝石鋲 / Gem Studs) | Radius: 0.015m, 6箇所に配置 | 台座の周囲に埋め込まれたカボションカットの小さなルビー宝石。 |
| **#013** | `Modifier` > `Bevel` (全金属パーツ) | Segments: 2, Amount: 0.003m | 金属角を落とし、鋳造品の丸みと反射ハイライトを強化。 |
| **#014** | 全パーツのトランスフォーム適用 (`Ctrl + A`) | All Transforms | スケール統一。 |
| **#015** | `Material Assign` > `M_Orb_Glass` | 外側UV球 | 物理屈折ガラス。Transmission 1.0, Roughness 0.015, IOR 1.52。 |
| **#016** | `Material Assign` > `M_Orb_Nebula` | 内側Icosphere | 宇宙ガス発光。ColorRamp (マゼンタ〜エレクトリックシアン), Emission 7.0。 |
| **#017** | `Material Assign` > `M_Orb_BronzeStand` | 台座・爪・リング | 古代青銅。Metallic 0.92, Roughness 0.38, 緑青（パティナ）混じり。 |
| **#018** | `Material Assign` > `M_Orb_RubyStud` | 台座鋲 | 真紅のルビー。Transmission 0.85, IOR 1.76。 |
| **#019** | 光源セットアップ (球体内部ポイントライト配置) | Color: シアン, Energy: 80W | ガラス球の内側から周囲の爪と床を美しく照らし出す間接光。 |
| **#020** | Cycles パストレーシング設定 | Samples: 32, Denoise: ON | ガラス球内部の二重屈折と集光模様（コースティクス）を正しくパストレース。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Orb_Glass** | Glass_Heavy_Crystal | Sound_Orb_Glass_Tap | 水晶ガラス。Transmission 1.0、IOR 1.52、Roughness 0.015。 |
| **M_Orb_Nebula** | Energy_Plasma_Arcane | Sound_Orb_Hum_Loop | 秘術プラズマ。Emission 7.0、波状ノイズブレンド。 |
| **M_Orb_BronzeStand** | Metal_Bronze_Cast | Sound_Bronze_Heavy_Clang | 鋳造青銅。Metallic 0.92、Roughness 0.38。 |
| **M_Orb_RubyStud** | Gem_Ruby_Refractive | Sound_Gem_Sparkle_Click | ルビー宝石。Transmission 0.85、IOR 1.76。 |
