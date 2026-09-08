# 魔導書と羽ペン (Spellbook & Quill) 最小単位モデリング手順 ＆ Why深層分析

魔法使いの書斎に広げられた、金箔押し装丁の開いた厚い古書、ガラスインク壺、精緻な羽ペンの全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` (表紙ベース / Cover) | Size: 1.0m, Scale: (0.42m, 0.32m, 0.008m) | 大型の魔導書（グリモワール）の革製ハードカバーの寸法を決定。 |
| **#002** | `Tab` (Edit Mode) > `2` (Edge) > 綴じ目側エッジ選択 > 3Dカーソルへ原点移動 | 回転ピボット設定 | 本を開閉できる蝶番（ヒンジ）の回転軸を定義。 |
| **#003** | `Shift + D` で複製 > `R > Z: 165 deg` で見開き配置 | 見開き角度: 165° | 机の上にどっしりと平らに開かれた読書・詠唱ポーズを作成。 |
| **#004** | `Shift + A` > `Mesh` > `Cube` (ページ束 / Page Block) | Scale: (0.38m, 0.28m, 0.04m) | 数百ページに及ぶ古文書の厚みブロックを両カバーの内側に配置。 |
| **#005** | `Tab` (Edit Mode) > ページ上面を湾曲成形 | `Ctrl + R` 4分割 > 中央を窪ませる | 開いた本特有の、背表紙に向かって緩やかに沈み込むページのしなりを表現。 |
| **#006** | `Shift + A` > `Mesh` > `Cube` (コーナー金箔金具 / Corner Filigree) | Size: 0.06m, 厚み: 0.004m | 表紙四隅を摩耗から保護し、豪奢に見せる装飾金具。 |
| **#007** | `Tab` (Edit Mode) > L字型に押し出し > 三角形カット | 彫金コーナー金具 | ファンタジー魔導書らしいヴィクトリア調/ゴシック調の透かし彫り金具を作成。 |
| **#008** | 表紙の4つの角に配置 > `Ctrl + J` | 4隅コーナー保護 | カバーの視覚的シルエットを重厚化。 |
| **#009** | `Shift + A` > `Mesh` > `Cylinder` (インク壺 / Inkpot) | Vertices: 16, Radius: 0.045m, Depth: 0.07m, Location: (0.35m, 0.25m, 0.035m) | 書斎のデスク上でインクを湛える八角形/円筒のガラス壺。 |
| **#010** | `Tab` (Edit Mode) > ネックと注ぎ口の押し出し | 半径 0.02m に絞り > リップ押し出し | インクが乾かない細口のボトルネックを成形。 |
| **#011** | `Shift + A` > `Mesh` > `Cylinder` (インク液面 / Ink Liquid) | Radius: 0.042m, Depth: 0.05m | 壺の内部に満たされた漆黒の魔法インク。 |
| **#012** | `Shift + A` > `Curve` > `Bezier` (羽軸 / Feather Rachis) | 長さ: 0.35m, なだらかな弓なりカーブ | 大型鳥（フクロウ/鷲）の羽ペンのしなやかな羽軸を定義。 |
| **#013** | Curve Data > `Bevel Depth: 0.003m` > 先端テーパー | 先細り管状 | インクを吸い上げる硬質ケラチン質の透明な羽根軸を作成。 |
| **#014** | `Shift + A` > `Mesh` > `Plane` (羽弁 / Feather Vane) | Length: 0.25m, Width: 0.06m | 羽軸の両脇に広がる左右非対称の羽毛フラップを作成。 |
| **#015** | `Tab` (Edit Mode) > 端部に切り込み（バーブ）を入れる | ナイフツール (`K`) | 自然な羽毛の割れ目と風合いを表現。 |
| **#016** | 羽ペンをインク壺の中に斜めに差し込む | Rotation: (15°, -25°, 40°) | 今まさに執筆を中断したような臨場感のあるプロップ配置。 |
| **#017** | `Material Assign` > `M_Book_LeatherCover` | 表紙カバー | 深紅のエンボス本革。Roughness 0.55。 |
| **#018** | `Material Assign` > `M_Book_GoldFiligree` | コーナー金具・バックル | 磨かれたゴールド。Metallic 1.0, Roughness 0.2。 |
| **#019** | `Material Assign` > `M_Book_Parchment` | ページ束 | 経年劣化した黄ばみ羊皮紙と古文書テキストのテクスチャ。 |
| **#020** | `Material Assign` > `M_Inkpot_Glass` & `M_Quill_Feather` | インク壺・羽ペン | 透明厚底ガラス（IOR 1.52）と純白のシルキーフェザー。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Book_LeatherCover** | Leather_Hard_Bound | Sound_Book_Cover_Close | 硬質本革。Roughness 0.55、深紅色、微細エンボス。 |
| **M_Book_GoldFiligree** | Metal_Gold_Foil | Sound_Metal_Buckle_Click | 金箔金具。Metallic 1.0、Roughness 0.2。 |
| **M_Book_Parchment** | Paper_Aged_Parchment | Sound_Parchment_Page_Turn | 黄ばみ羊皮紙。Roughness 0.82、Subsurface 0.15。 |
| **M_Inkpot_Glass** | Glass_Heavy_Flask | Sound_Glass_Inkpot_Clink | 厚底ガラス。Transmission 1.0、IOR 1.52、深緑/透明。 |
