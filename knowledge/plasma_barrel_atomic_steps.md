# SFプラズマエナジーバレル (Sci-Fi Plasma Barrel) 最小単位モデリング手順 ＆ Why深層分析

近未来・サイバーパンクシューターゲームの定番破壊可能プロップ「SF爆発バレル（重装甲スチール＆発光プラズマコア＆スリット窓＆圧力弁）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` | Vertices: 32, Radius: 0.45m, Depth: 1.1m, Z: 0.55m | バレル本体の外殻（Outer Armor Shell）を生成。 |
| **#002** | `Ctrl + A` > `Apply All Transforms` | All Transforms | 今後のインセットやループカットが均等に動作するよう確定。 |
| **#003** | `Tab` (Edit Mode) > `Ctrl + R` > Cuts: 8 | 円筒側面の水平分割 | 上下キャップ、中央スリット、補強リブの境界エッジを作成。 |
| **#004** | 上下端のエッジループを選択 > `Alt + S` (Fatten) | Offset: 0.04m | 転倒や衝撃からバレルを守る上下のヘビーデューティー保護バンパーを形成。 |
| **#005** | 中央の帯フェースを選択 > `I` (Inset) | Thickness: 0.02m | 内部プラズマが露出する観察窓（スリット）のフレーム枠取り。 |
| **#006** | `Alt + E` > `Extrude Faces Along Normals` | Offset: -0.06m | 窓を装甲の奥深くへ凹ませ、ハードサーフェスの重厚感を強調。 |
| **#007** | `Material Assign` > `M_Barrel_Plasma` | 凹ませた底面フェースに適用 | 危険な高圧エネルギーがオレンジ色に脈動発光するコアシェーダーを分離。 |
| **#008** | `Shift + A` > `Mesh` > `Cylinder` (六角補強ボルト) | Vertices: 6, Radius: 0.02m, Depth: 0.02m | 装甲プレートを留めるインダストリアルな六角ボルト。 |
| **#009** | 上下バンパーの円周上に各8個配置 | Linked Duplicate (`Alt + D`) | SFメカニカルなディテール密度（Greeble）を向上。 |
| **#010** | `Tab` (Object Mode) > `Shift + A` > `Mesh` > `Cylinder` (上部バルブハッチ) | Vertices: 16, Radius: 0.18m, Depth: 0.08m, Z: 1.14m | バレルの注入・排気口となるトップハッチを配置。 |
| **#011** | `Shift + A` > `Mesh` > `Torus` (圧力逃がしバルブハンドル) | Major: 0.06m, Minor: 0.012m, Z: 1.2m | 作業員が手動で圧力を抜くための円形バルブノブ。 |
| **#012** | `Shift + A` > `Mesh` > `Cylinder` (圧力計ゲージ) | Vertices: 16, Radius: 0.05m, Depth: 0.03m, Location: (0.2m, -0.42m, 0.85m) | 危険度を示すアナログ圧力メーター（Pressure Gauge）を外付け。 |
| **#013** | ゲージ前面にガラスレンズを配置 | `M_Barrel_Glass` 適用 | 強化ガラスカバーの反射と指針の立体感を表現。 |
| **#014** | `Shift + A` > `Point Light` | Location: バレル内部中心 (0, 0, 0.55m), Energy: 150W | スリットから外の床や壁面にプラズマ光を漏らす内部光源。 |
| **#015** | `Modifier` > `Bevel` (全金属パーツ) | Width: 0.005m, Segments: 2, Limit: Angle (30°) | ハードサーフェス特有のエッジハイライト（スペキュラ）を際立たせる。 |
| **#016** | `Material Assign` > `M_Barrel_Armor` | 装甲シェルに適用 | 危険物を示す警告イエロー＆ガンメタル塗装。摩耗エッジノイズ。 |
| **#017** | `Material Assign` > `M_Barrel_Rubber` | 上下バンパーに適用 | 黒色合成ゴム。Roughness 0.9, 衝撃吸収ダンパー。 |
| **#018** | `Shade Auto Smooth` | 全パーツに適用 | 平坦な装甲プレートと円筒のなめらかな曲面を両立。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Barrel_Armor** | `Metal_Heavy` | `Sound_SciFi_Barrel_Hit` | 強化合金装甲。ガンメタル＆警戒イエロー。弾丸跳弾音、金属打撃音。 |
| **M_Barrel_Plasma** | `SciFi_Energy` | `Sound_Plasma_Core_Loop` | 高圧プラズマ。強烈なネオンオレンジ (RGB: 1.0, 0.35, 0.02, Strength: 12.0)。 |
| **M_Barrel_Rubber** | `Rubber_Synthetic` | `Sound_Rubber_Gasket` | 保護バンパー。無光沢ブラック、低反発な打撃吸収音。 |
| **M_Barrel_Glass** | `Glass_Reinforced` | `Sound_Gauge_Glass_Tap` | 圧力計強化ガラス。高い反射率、銃撃時のヒビ割れ音。 |
