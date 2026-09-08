# エルフの宝飾王冠 (Elven Circlet Crown) 最小単位モデリング手順 ＆ Why深層分析

エルフの森の王侯貴族が戴く、蔦（ツタ）の銀線細工（フィリグリー）、有機的リーフモチーフ、大粒のサファイア宝石を持つティアラの全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Curve` > `Circle` (ヘッドリングパス / Circlet Ring) | Radius: 0.12m, Location: (0, 0, 0.1m) | 頭部を包み込む基本の環状リングパスを定義。 |
| **#002** | `Shift + A` > `Curve` > `Bezier` (編み込み蔦 / Vine Filigree) | 2本の波打つ螺旋S字カーブ | エルフ工芸を象徴する、2本の植物の蔦が絡み合う有機的フィリグリーを作成。 |
| **#003** | Curve Data > `Bevel Geometry` > `Depth: 0.003m` | 極細銀線パイプ化 | 熟練の銀細工師が編み上げた繊細な純銀ワイヤーを成形。 |
| **#004** | `Curve Deform Modifier` (Circleをターゲットにバインド) | 環状巻き付け | 絡み合うツタが頭部リングに沿って360度綺麗に周回するように変形。 |
| **#005** | `Shift + A` > `Mesh` > `Plane` (額のセンターリーフ / Center Leaf) | Scale: (0.02m, 0.04m, 0.001m) | 額の中央で上に向かって優美に立ち上がる象徴的な木の葉（リーフ）モチーフ。 |
| **#006** | `Tab` (Edit Mode) > 中央稜線を押し出し > 葉脈カーブ成形 | なめらかな葉脈立体化 | 単なる平たい板ではなく、葉脈の起伏と先端の尖りを持たせる。 |
| **#007** | `Shift + D` で複製し左右に段階的に縮小配置 (左右各3枚) | 扇状ティアラ展開 | 額の中央からこめかみに向かって広がる王冠のメインクラウンを形成。 |
| **#008** | `Shift + A` > `Mesh` > `Cylinder` (宝石座金 / Gem Bezel Setting) | Vertices: 16, Radius: 0.018m, Depth: 0.008m, Location: (0, -0.12m, 0.13m) | 中央のサファイア宝石を強固かつ美しく爪留めするシルバー台座。 |
| **#009** | 台座の周囲に4本の留め爪（プロング / Prongs）を作成 | 微小円柱の爪 | ハイジュエリーとしての精緻な宝石留め構造。 |
| **#010** | `Shift + A` > `Mesh` > `Icosphere` (カットサファイア / Cut Sapphire) | Subdivisions: 2, Radius: 0.016m | 額の中央に輝く主役のオーバルカット・サファイア宝石。 |
| **#011** | `S` > `Y: 0.6, Z: 1.2` | ファセット維持オーバル化 | 楕円カット宝石のシャープな屈折面反射を表現。 |
| **#012** | `Shift + A` > `Mesh` > `Icosphere` (サイド小粒ダイヤ / Accent Diamonds) | Radius: 0.005m, 左右リーフの付け根に4個配置 | サファイアの両脇に散りばめられた星屑のようなダイヤモンドアクセント。 |
| **#013** | `Modifier` > `Mirror` | Axis: X | 左右のリーフ・ワイヤー・宝石配置の完全対称性を担保。 |
| **#014** | `Right Click` > `Shade Smooth` (宝石以外) | 宝石はフラットシェード | 金属部はつるりとしたシルバートーン、宝石は鋭いカット面を維持。 |
| **#015** | `Material Assign` > `M_Crown_Silver` | 蔦ワイヤー・リーフ・台座 | 純銀。Metallic 1.0, Roughness 0.12, 高貴なシルバーホワイト。 |
| **#016** | `Material Assign` > `M_Crown_Sapphire` | センター宝石 | 深青サファイア。Transmission 0.94, IOR 1.77, 深いコバルトブルー。 |
| **#017** | `Material Assign` > `M_Crown_Diamond` | 小粒ダイヤ | クリアダイヤ。Transmission 0.98, IOR 2.42, 虹色の分散輝き。 |
| **#018** | 多灯スタジオライティング (3点キー＋真上ハイライト) | 白色ハイパワーライト | 銀線細工と宝石のファセット（切削面）に輝く無数のきらめきを抽出。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | キャラクターの頭部モデルに即座にペアレント可能なスケール統一。 |
| **#020** | Cycles パストレーシングレンダリング | Samples: 32, Denoise: ON | 高屈折率宝石（IOR 1.77/2.42）のリアルな内部反射・屈折を忠実に再現。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Crown_Silver** | Metal_Silver_Polished | Sound_Silver_Chime_Light | 純銀。Metallic 1.0、Roughness 0.12、明るい銀白色。 |
| **M_Crown_Sapphire** | Gem_Sapphire_Brilliant | Sound_Sapphire_Resonance | サファイア。Transmission 0.94、IOR 1.77、深青。 |
| **M_Crown_Diamond** | Gem_Diamond_Hard | Sound_Diamond_Tinkle | ダイヤモンド。Transmission 0.98、IOR 2.42、クリア。 |
