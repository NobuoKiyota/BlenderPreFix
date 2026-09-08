# 段瀑・滝 (Flowing Waterfall) 最小単位モデリング手順 ＆ Why深層分析

崖から勢いよく落下する高速流速ベクトル、着水点に泡立つ白波フォーム、水煙ミストを持つダイナミックな滝の全行程レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Cube` (岩崖 / Cliff Rock) | Scale: (2.4m, 1.2m, 2.8m), Location: (0, 0.4m, 1.4m) | 滝が流れ落ちる急峻な岩壁のベース。 |
| **#002** | `Tab` (Edit Mode) > 崖の前面を2段ステップ状に掘り込み | 段瀑（Tiered Drops） | 1本の直線ではなく、途中の岩棚にぶつかって激しく跳ねる立体的な滝壺を成形。 |
| **#003** | `Shift + A` > `Curve` > `Bezier` (滝の流水パス / Water Flow Curve) | 崖の上から滝壺へ向かうS字落水カーブ | 重力に従って岩棚を舐め、空中に放物線を描いて落下する水流の軌跡を定義。 |
| **#004** | Curve Data > `Bevel Depth: 0.35m` > `S: X=2.0, Y=0.15` | 幅広の扁平落水シート | 厚みのあるリボン状の迫力ある流水メッシュを作成。 |
| **#005** | `Alt + C` or `Convert to Mesh` | メッシュ化 | テクスチャのUVマッピングを流速方向に沿わせる。 |
| **#006** | UVエディタでUVを縦長ストリップに展開 (`Follow Active Quads`) | 流速UV整列 | 水流ノイズテクスチャが落水方向に綺麗に流れるようにする。 |
| **#007** | `Shift + A` > `Mesh` > `Cylinder` (滝壺プール / Plunge Pool) | Vertices: 24, Radius: 1.4m, Depth: 0.3m, Location: (0, -0.4m, 0.15m) | 落下した水を受け止める円形の滝壺。 |
| **#008** | `Shift + A` > `Mesh` > `Torus` (着水白波リング / Impact Foam Ring) | Major: 0.45m, Minor: 0.08m, Location: (0, -0.3m, 0.3m) | 滝が滝壺に激突して激しく泡立つ環状の白波（Foam）。 |
| **#009** | `Modifier` > `Displace` (白波リング) > Cloud Texture | Strength: 0.04m | 激しい水しぶきと泡の不規則な飛び散りを表現。 |
| **#010** | `Shift + A` > `Mesh` > `Icosphere` (跳ね水滴クラスター / Splash Droplets) | 半径 0.015m の水滴を空中に複数散布 | 激突の瞬間に宙に舞い上がる水滴パーティクル。 |
| **#011** | 崖の左右に飛沫で濡れた側壁岩 (`Displace` 適用) を配置 | 濡れた黒岩 | 水とのコントラストで岩の重厚感を強調。 |
| **#012** | `Material Assign` > `M_Waterfall_Stream` | 落下水流メッシュ | 高速流れる縦筋バンプ、Transmission 0.92, IOR 1.333, 白筋ブレンド。 |
| **#013** | `Material Assign` > `M_Waterfall_Foam` | 着水白波・泡 | 真っ白な高輝度気泡（BaseColor: 白, Roughness: 0.7, 微弱発光）。 |
| **#014** | `Material Assign` > `M_Waterfall_Pool` | 滝壺水面 | 深緑色の静かな水面。粗さ 0.03。 |
| **#015** | `Material Assign` > `M_Waterfall_WetRock` | 岩壁 | 水しぶきで黒く濡れ光る玄武岩。Roughness 0.22。 |
| **#016** | 水煙ミスト用ボリューム (`Cube` + Principled Volume, Density: 0.04) | 滝壺の靄（もや） | 滝の轟音とともに立ち上るマイナスイオンの水煙を演出。 |
| **#017** | リムライトを水流の背後から斜めに照射 | 逆光透過光 | 激しく泡立つ流水の白い筋とエッジを鮮烈に浮き上がらせる。 |
| **#018** | 全トランスフォーム適用 (`Ctrl + A`) | All Transforms | スケール統一。 |
| **#019** | アニメーション準備 (#frameドライバによるテクスチャオフセット) | 自動流速スクロール | リアルタイム・ループ再生可能な流速シェーダー仕様。 |
| **#020** | Cycles レンダリング (モーションブラー ON/OFF 選択可) | 水の運動感 | 白波の激しさと岩肌の濡れ感をハイクオリティにレンダリング。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Waterfall_Stream** | Water_Fast_Current | Sound_Water_Roar_Stream_Loop | 落水流。Transmission 0.92、縦筋Waveバンプ、IOR 1.333。 |
| **M_Waterfall_Foam** | Water_Foam_Splash | Sound_Foam_Churn_White | 白波。BaseColor 純白、Roughness 0.7、微小Emission 1.2。 |
| **M_Waterfall_WetRock** | Stone_Wet_Basalt | Sound_Wet_Rock_Impact | 濡れ岩。Roughness 0.22、Metallic 0.1、深黒。 |
