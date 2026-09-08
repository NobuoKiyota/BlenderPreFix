# 🪨 【AAA フォトリアル】断崖岩肌サーフェス (ChuckCG Rocky Surfaces) 最小単位手順 ＆ Why深層分析

本手順書は、海外の人気3Dアーティスト **ChuckCG** 氏のYouTubeチュートリアル動画（`https://www.youtube.com/watch?v=g9T3vDtTAPk`）：
『How To Create Rocky Surfaces in Blender』
を完全学習・分解した、スカルプト不要・モディファイア多重積層によるリアルな断崖・岩肌（Rocky Surfaces）の完全技術仕様書です。

---

## 📺 出典元情報 (Primary Source)
- **動画タイトル**: How To Create Rocky Surfaces in Blender
- **クリエイター**: ChuckCG
- **YouTube URL**: [https://www.youtube.com/watch?v=g9T3vDtTAPk](https://www.youtube.com/watch?v=g9T3vDtTAPk)
- **核心技法**: Subdivide → Displace (Large Clouds) → Displace (Voronoi Fracture) → Voxel Remesh → Displace (Micro Noise) → PBR Serial Bump Shading

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` (岩塊ベース作成) | Location: (0, 0, 0.7m), Scale: (1.6, 1.2, 0.8) | 断崖巨岩の原型となるボリュームを作成。トランスフォーム適用 (`Ctrl + A`)。 |
| **#002** | `Tab` (Edit Mode) > 面を選択して粗く押し出し (`E`) | 不規則な断崖シルエット | 真四角の箱感を崩し、地殻変動による隆起・傾斜をつける。 |
| **#003** | `Modifier` > `Subdivision Surface` (細分化第1層) | Type: Simple, Levels: 3 (ビュー・レンダー) | ディスプレイスメントの頂点変位を受け止める均一な基盤トポロジーを作成。 |
| **#004** | `Shift + A` でテクスチャ新規作成 (大うねり地層) | Type: `Clouds`, Size: 0.65, Depth: 2 | 巨石全体を大きく歪ませるメガスケールの起伏を定義。 |
| **#005** | `Modifier` > `Displace` (大構造断層変位) | Texture: 大うねりClouds, Strength: 0.38m | 丸みを帯びた形状を岩特有の力強い多面体ブロックへと変形。 |
| **#006** | `Shift + A` でテクスチャ新規作成 (節理・割れ目) | Type: `Voronoi`, Metric: Distance, Size: 0.35 | 石工がタガネで割ったような鋭利な節理（Joint Fracture）パターンを生成。 |
| **#007** | `Modifier` > `Displace` (鋭角節理変位) | Texture: Voronoi, Strength: 0.16m | 大うねりの上にシャープなエッジと平坦な割れ断面を多層合成。 |
| **#008** | `Modifier` > `Remesh` (ボクセルリメッシュ) | Mode: Voxel, Voxel Size: 0.04m | 多重ディスプレイスで過度に伸びたポリゴンを均一な四角面メッシュにリセット。 |
| **#009** | `Modifier` > `Subdivision Surface` (細分化第2層) | Type: Catmull-Clark, Levels: 1 | リメッシュ後の微細な角を丸め、滑らかな自然風化エッジへ移行。 |
| **#010** | `Shift + A` でテクスチャ新規作成 (微小岩肌ノイズ) | Type: `Clouds`, Size: 0.06, Depth: 4 | 花崗岩の石英・雲母粒子が持つザラザラした微細テクスチャ。 |
| **#011** | `Modifier` > `Displace` (微細風化粗さ) | Texture: 微小Clouds, Strength: 0.035m | スカルプトブラシでも描けない高周波なリアル岩肌ディテールを付与。 |
| **#012** | `Object` > `Shade Smooth` (スムーズシェード) | - | ファセット面を滑らかにし、光と影のグラデーションを自然に表現。 |
| **#013** | `Tab` (Edit Mode) > `U` > `Smart UV Project` | Angle Limit: 66°, Margin: 0.002 | シームレスにテクスチャを投影するための歪みのないUV展開。 |
| **#014** | シェーダーエディタで断崖PBRマテリアル作成 | Principled BSDF, Roughness: 0.88 | 水分を吸わない乾いた硬質天然岩石の光沢プロファイルを定義。 |
| **#015** | ノイズテクスチャ（大構造）から直列第1バンプを構築 | Scale: 3.5, Strength: 0.40 | ジオメトリ変位と連動した深い陰影と陰影コントラストを強調。 |
| **#016** | ノイズテクスチャ（微細砂利）から直列第2バンプを接続 | Scale: 32.0, Strength: 0.25 (直列Normal) | **ChuckCG式の直列バンプ**。Normalを連続接続して二重の凹凸を深度合成。 |
| **#017** | `ColorRamp` でエッジ風化カラーパレットを構築 | Pos 0.2: 暗灰岩, Pos 0.8: 明るい砂質岩 | 凸部（擦れて風化した明るいエッジ）と凹部（影と汚れ）の階調を表現。 |
| **#018** | `Ambient Occlusion` (AO) ノードで深い亀裂を暗化 | ColorRamp: 窪み暗色乗算 | 雨水や埃が溜まる裂け目の深部を自然なシャドウで引き締め。 |
| **#019** | スタジオキーライト（AREA: 550W）＋青色フィルライト（220W） | 45度斜光セッティング | 岩肌の陰影凹凸（Chiaroscuro）が最も立体的に浮き立つライティング。 |
| **#020** | Cycles パストレーシングレンダリング ＆ GLBエクスポート | Samples: 28, Denoise ON | 非破壊モディファイアによる完全プロシージャル断崖岩肌アセットの完成。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_ChuckCG_CliffRock** | Stone_Cliff_Rough_Slate | Sound_Rock_Crag_Step | ChuckCG式。直列多重バンプ（大うねり＋微細砂利）、ColorRampエッジ風化、AO窪み暗化。 |
