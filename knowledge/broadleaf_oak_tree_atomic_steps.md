# 広葉樹・オークの木 (Broadleaf Oak Tree) 最小単位モデリング手順 ＆ Why深層分析

豊かな夏緑樹林の主役である、太く力強い分岐幹と、木漏れ日を通すボリューミーな葉冠を持つオーク大樹の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cylinder` (主幹基部 / Trunk Base) | Vertices: 12, Radius: 0.35m, Depth: 1.8m, Location: (0, 0, 0.9m) | 何百年も大地に根を張るオークの太い幹を作成。 |
| **#002** | `Tab` (Edit Mode) > 上端フェースを2つに分割 > 左右斜め上へ押し出し (`E`) | 2大主枝分岐 (Bifurcation) | 広葉樹特有の、幹が途中で複数に分かれて水平に広がる樹形を成形。 |
| **#003** | 各枝の先端をさらに2つに枝分かれ押し出し | 2次枝 (Secondary Branches) | 葉冠を支える広範なドーム状の枝骨格を構築。 |
| **#004** | 根元フェースを外側に放射状に引き伸ばす | 力強い板根 | 風圧を受け止める巨大な根張りを地面に定着。 |
| **#005** | `Shift + A` > `Mesh` > `Icosphere` (主葉塊 / Foliage Canopy Main) | Subdivisions: 3, Radius: 0.85m, Location: (0, 0, 2.6m) | 葉冠の中央ボリュームとなる葉のクラスターを作成。 |
| **#006** | `Modifier` > `Displace` > Cloud Texture (Size: 0.45, Strength: 0.18m) | 有機的雲状変形 | Icosphereの幾何学感を崩し、風に揺れるモコモコとした木の葉の塊に変換。 |
| **#007** | `Shift + D` で複製し、各枝の先端に大小5個配置 (半径 0.45m〜0.7m) | マルチクラスター葉冠 | 1つの巨大な球ではなく、複数の葉の房が重なり合うリアルな樹冠を形成。 |
| **#008** | 葉塊の間に適度な隙間（Sunlight Gaps）を空ける | 木漏れ日スリット | 枝の隙間から光が射し込む、絵画のような美しい抜け感を確保。 |
| **#009** | `Modifier` > `Decimate` (Planar or Collapse: 0.8) | スタイライズ最適化 | 光の明暗（シェーディングステップ）が美しく出るファセット感を演出。 |
| **#010** | `Right Click` > `Shade Smooth` (全葉塊) | なめらかシェード | 葉と葉の継ぎ目を滑らかに光らせる。 |
| **#011** | 法線転送モディファイア (`Data Transfer: Normals`) | 球体法線への統一 | 葉冠の内側の黒ずみを消し、木全体で大きなハイライトを受けるトポロジーに補正。 |
| **#012** | 幹メッシュに `Subdivision Surface` (Level: 1) | なめらかな樹皮幹 | 枝分かれ接合部のポリゴン角張りを滑らかに融合。 |
| **#013** | `Material Assign` > `M_Oak_Bark` | 幹・大枝 | 暗褐色のゴツゴツしたオーク樹皮。Roughness 0.85、ひび割れバンプ。 |
| **#014** | `Material Assign` > `M_Oak_Foliage` | 全葉塊クラスター | 明るい萌黄色〜濃緑（Subsurface: 0.25, Transmission: 0.1）、木漏れ日透過。 |
| **#015** | 全パーツ結合 (`Ctrl + J`) | 単一アセット化 | ゲーム配置用の統一ピボット設定。 |
| **#016** | 地面に落ち葉 (`Plane`, 8枚) を散布配置 | リアルな林床 | 季節感と木の下の生活感を演出。 |
| **#017** | `Material Assign` > `M_Oak_FallenLeaves` | 落ち葉 | 枯葉の黄褐色。Roughness 0.75。 |
| **#018** | サンライト照明 (角度 45°, 暖色 5500K) | 夏の太陽光 | 葉冠の隙間から幹へ美しい木漏れ日のシャドウを落とす。 |
| **#019** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | スケール・回転の初期化。 |
| **#020** | Cycles パストレーシングレンダリング | Samples: 32 | サブサーフェス・スキャッタリングによる葉の瑞々しい光の透け感をレンダリング。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Oak_Bark** | Wood_Bark_Oak | Sound_Wood_Trunk_Heavy_Thud | オーク樹皮。Roughness 0.85、暗褐色、樹皮溝バンプ。 |
| **M_Oak_Foliage** | Foliage_Leaves_Broad | Sound_Leaves_Rustle_Gentle | 広葉。SSS 0.25、BaseColor 鮮やかな黄緑、粗さ 0.5。 |
| **M_Oak_FallenLeaves** | Foliage_Leaves_Dry_Crunch | Sound_Footstep_Dry_Leaves | 枯葉。Roughness 0.75、乾いた茶褐色。 |
