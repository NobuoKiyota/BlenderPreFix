# 蓮の葉と水滴 (Lotus Leaf & Droplets) 最小単位モデリング手順 ＆ Why深層分析

水辺に浮かぶ、超撥水ロータス効果を持つ放射状傘型の蓮の葉と、表面を球状に転がる完全屈折水滴群の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Circle` (蓮の葉輪郭 / Leaf Disc) | Vertices: 24, Radius: 0.55m, Location: (0, 0, 0.15m) | 円形に近い蓮の葉の外周境界を作成。 |
| **#002** | `Tab` (Edit Mode) > `F` で面張り > 外周の一部にV字の切り込み（スリット）を入れる | 蓮の葉の象徴的スリット | 葉の中心から縁に向かって入る伝統的なV字スリットを成形。 |
| **#003** | 中央の葉柄接合部（中心点）を選択 > `G > Z: -0.06m` で沈める | すり鉢状（漏斗型）の窪み | 雨水を中心のくぼみに集める蓮の葉特有のカップ形状を形成。 |
| **#004** | 外周エッジを選択 > プロポーショナル編集でわずかに上下に波打たせる | 優美なフリル輪郭 | 完全な平面を崩し、水面に浮かぶ柔らかい葉の有機的なたわみを表現。 |
| **#005** | `Modifier` > `Solidify` | Thickness: 0.003m | 薄くもしっかりとした生体組織の肉厚を付与。 |
| **#006** | `Shift + A` > `Mesh` > `UV Sphere` (主水滴 / Main Water Drop) | Segments: 20, Rings: 16, Radius: 0.035m, Location: (0, -0.02m, 0.12m) | 葉の中心の窪みに溜まった大粒の水滴を作成。 |
| **#007** | `S > Z: 0.7` (扁平球化) | 接触角の大きい水滴 | 超撥水（Lotus Effect）により、濡れ広がらず表面張力で丸く保たれる水滴を再現。 |
| **#008** | `Shift + D` で小粒水滴（半径 0.008m〜0.015m）を複製し葉の上に6個ランダム散布 | 玉状の水滴群 | 転がるように散らばる朝露・雨粒の清涼感を演出。 |
| **#009** | `Shift + A` > `Mesh` > `Cylinder` (葉柄 / Leaf Stem) | Vertices: 12, Radius: 0.018m, Depth: 0.4m, Location: (0, 0, -0.05m) | 葉の底面中心から水底へ伸びる棘のある円柱茎。 |
| **#010** | `Shift + A` > `Mesh` > `Plane` (水面 / Water Plane) | Size: 1.8m, Location: (0, 0, 0.08m) | 蓮の葉が浮かぶベース水面。 |
| **#011** | 全水滴を選択して結合 (`Ctrl + J`) | 水滴オブジェクト統合 | マテリアル一括制御とレンダリング効率化。 |
| **#012** | `Right Click` > `Shade Smooth` (全パーツ) | スムースシェード | 水滴のガラスのような反射と葉の滑らかな曲面を保証。 |
| **#013** | `Material Assign` > `M_Lotus_Leaf` | 蓮の葉本体 | ビロードのような青緑（Subsurface: 0.25, Sheen: 0.6, Roughness: 0.35）。 |
| **#014** | `Material Assign` > `M_Lotus_Droplets` | 全水滴 | 純粋な水（Transmission: 1.0, IOR: 1.333, Roughness: 0.01）。 |
| **#015** | `Material Assign` > `M_Water_Surface` | 水面プレーン | 暗緑色の池水（Transmission: 0.85, Roughness: 0.04）。 |
| **#016** | 放射状の葉脈バンプ（葉の中心から外へ走る細い溝）をプロシージャル付与 | 放射状葉脈 | 葉の幾何学的中心から広がるリアルな維管束ディテール。 |
| **#017** | 水滴の底面にわずかな接地面平坦化 | 接触界面 | 葉の上に自然に乗っている物理的接地感を向上。 |
| **#018** | 真上からの柔らかなディフューズ光＋斜めハイライト光 | 朝の清澄な光 | 水滴の表面に丸い小さなハイライトを灯し、みずみずしさを極大化。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | スケール統一。 |
| **#020** | Cycles レンダリング (デノイズ ON) | Samples: 32 | 水滴レンズが葉の表面の葉脈を拡大屈折して見せる光学現象を完璧に描写。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Lotus_Leaf** | Organic_Lotus_Hydrophobic | Sound_Lotus_Leaf_Rustle | 超撥水葉。BaseColor 青緑、Sheen 0.6、SSS 0.25。 |
| **M_Lotus_Droplets** | Water_Droplet_Puddle | Sound_Water_Drop_Plink | 水滴。Transmission 1.0、IOR 1.333、粗さ 0.01。 |
| **M_Pond_Water** | Water_Calm_Pond | Sound_Pond_Water_Ripples | 水面。Transmission 0.85、暗青緑。 |
