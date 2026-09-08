# 宝箱 (Treasure Chest) 最小単位モデリング手順 ＆ Why深層分析

ファンタジー・ダンジョン系ゲームの最重要プロップである「開閉式木製宝箱（鉄補強バンド＆リベット＆南京錠）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | Shift + A > Mesh > Cube | Size: 1.0m, Location: (0, 0, 0.4) | 宝箱の本体ベース（下部チェストボックス）を作成する原点メッシュ。 |
| **#002** | S > X | Scale: 1.4 | 宝箱らしいワイドで安定感のある横幅プロポーションを定義。 |
| **#003** | S > Y | Scale: 0.9 | 奥行きを若干絞り、正面から見た際の黄金比（1.4 : 0.9）を形成。 |
| **#004** | S > Z | Scale: 0.6 | 蓋が載るスペースを残すため、下部ベースの高さを抑える。 |
| **#005** | Ctrl + A > Apply All Transforms | All Transforms | 今後のベベルやモディファイアが縦横均等に働くようスケールを初期化。 |
| **#006** | Tab (Edit Mode) > 3 (Face) | 上面フェースを選択 | 蓋と合わさる開口部および内部キャビティ（空洞）の加工準備。 |
| **#007** | I (Inset Faces) | Thickness: 0.05m | 宝箱の木板の「厚み（肉厚）」を定義。ゲーム内での頑丈さを表現。 |
| **#008** | E (Extrude) > Z | -0.5m | 内部の空洞を掘り下げ、蓋を開けた際に宝物を収納できる深さを確保。 |
| **#009** | Tab (Object Mode) > Shift + A > Mesh > Cylinder | Vertices: 24, Radius: 0.45m, Depth: 1.4m | 宝箱の象徴であるアーチ状（円弧型）の上蓋を作成するための素材。 |
| **#010** | R > Y > 90 | Angle: 90 deg | シリンダーを横倒しにし、チェストの横幅方向に軸を合わせる。 |
| **#011** | Tab (Edit Mode) > 1 (Vertex) | 下半分（Z < 0）の頂点をボックス選択 > X > Delete Vertices | 完全な円筒から「半円（アーチ）」を切り出し、蓋のトップ形状を生成。 |
| **#012** | F (Fill) | 下面の開口エッジを選択して面貼り | 半円筒の底面を塞ぎ、閉じたソリッドメッシュにする。 |
| **#013** | G > Z | Location Z: 0.7m | 本体の真上にぴったり噛み合うように高さをアライン。 |
| **#014** | Tab (Object Mode) | 名前を Lid に変更、原点を後ろエッジに設定 | 将来的な開閉アニメーション（ヒンジ回転）を1軸（X軸回転）で可能にする。 |
| **#015** | Shift + A > Mesh > Cube (Iron Bands) | Size: 1.0m | 木板を締め上げる補強用の鉄バンド（帯金）を作成。 |
| **#016** | S > X: 0.08, Y: 0.94, Z: 0.64 | 木枠より全方向に 0.02m 大きく設定 | 木材の外側にぴったり巻き付く金属フレームの厚みを演出。 |
| **#017** | Tab (Edit Mode) > 内部フェースをくり抜き | フレーム形状化 | 無駄なポリゴンを排除し、外枠のみの鉄帯メッシュに最適化。 |
| **#018** | Shift + D > G > X | 左右両端（X: ±0.5m）および中央（X: 0）に複製配置 | クラシックな3連鉄バンド構造を完成。 |
| **#019** | Modifier > Bevel | Segments: 2, Amount: 0.008m | 金属エッジの鋭利さを丸め、ハイライト（光の筋）が入るゲーム品質に向上。 |
| **#020** | Shift + A > Mesh > Icosphere (Rivets) | Subdivisions: 1, Radius: 0.02m | 鉄バンドを木板に留めるリベット（鋲/角鋲）を作成。 |
| **#021** | Array Modifier or Linked Duplicate | 鉄バンドの稜線に沿って等間隔配置 | 無骨な中世の鍛造感を演出し、シルエットの情報密度を高める。 |
| **#022** | Shift + A > Mesh > Cube (Lock Hasp) | Front Center (Y: -0.47m, Z: 0.68m) | 蓋から垂れ下がる鍵留め金具（ハスプ）のベース。 |
| **#023** | Shift + A > Mesh > Torus (Padlock Shackle) | Major Radius: 0.04m, Minor Radius: 0.008m | 南京錠の掛け金（ツル）を作成。ハスプの穴に通す。 |
| **#024** | Shift + A > Mesh > Cube (Padlock Body) | Z: 下部に配置、Bevel付与 | 真鍮/重厚鉄の南京錠本体。 |
| **#025** | Shade Smooth + Auto Smooth (Angle 35°) | 全オブジェクト | 平面と曲面のメリハリを維持しつつ、なめらかなシェーディングを実現。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Chest_Wood** | Wood_Heavy | Sound_Wood_Chest_Impact | 暗めのオーク木材。粗さ 0.75。縦方向の木目プロシージャルノイズ。 |
| **M_Chest_Iron** | Metal_Heavy | Sound_Iron_Band_Hit | 鍛造黒鉄。Metallic 0.95、Roughness 0.45、わずかなバンプ凹凸。 |
| **M_Chest_Brass** | Metal_Light | Sound_Lock_Latch_Click | 南京錠・金具。真鍮ゴールド (RGB: 0.85, 0.65, 0.2)。Metallic 1.0。 |
