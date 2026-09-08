# ダンジョンの鍵束 (Antique Dungeon Keys & Ring) 最小単位モデリング手順 ＆ Why深層分析

牢獄・ダンジョン探索・脱出ゲームの定番クエストアイテム「看守の鍵束（鍛造鉄リング＆装飾ボウ＆中空シャフト＆ビット鍵山）」の最小単位全手番レシピ。

---

## 最小単位全手番レシピ (Atomic Steps)

| Step | 操作 (Key / Action) | パラメータ / 設定値 | 手順の目的・理由 (Why) |
| :--- | :--- | :--- | :--- |
| **#001** | `Shift + A` > `Mesh` > `Torus` (大キーリング) | Major: 0.14m, Minor: 0.012m, Location: (0, 0, 0.5m) | 複数の鍵を束ねる太い鍛造鉄のホルダーリングを作成。 |
| **#002** | `Shift + A` > `Mesh` > `Cylinder` (鍵Aの軸 / Shaft) | Vertices: 16, Radius: 0.012m, Depth: 0.38m, Location: (0, 0, 0.22m) | メインマスターキーのシャンク（軸棒）を配置。 |
| **#003** | `Shift + A` > `Mesh` > `Torus` (鍵Aの頭部 / Bow) | Major: 0.045m, Minor: 0.009m, Location: (0, 0, 0.42m) | 指でつまむための円形・クローバー装飾の持ち手（Bow）。 |
| **#004** | `Ctrl + J` (Join) | 軸とBowを結合 | 単一の剛体キーメッシュとして一体化。 |
| **#005** | `Shift + A` > `Mesh` > `Cube` (鍵Aの鍵山 / Bit) | Size: 1.0m, Location: (0.035m, 0, 0.06m) | 錠前のピンを押し上げる歯（ビット）の母材。 |
| **#006** | `S` > `X: 0.06, Y: 0.016, Z: 0.08` | 直方体ビット | シャフト下部に突き出る鍵山プレート。 |
| **#007** | `Tab` (Edit Mode) > `Ctrl + R` > スリット切り込み | 面を削除して鍵山の凹凸（Ward Cut）を成形 | 複雑な防犯機構を想起させるクラシックな階段状カット。 |
| **#008** | `Ctrl + J` | ビットをシャフトに結合 | 鍵A（牢獄の主鍵）の基本ソリッドが完成。 |
| **#009** | `R` > `Y: 12 deg, X: -8 deg` | リングに通した自然な傾き | リングから重力でぶら下がった際のリアルな角度をつける。 |
| **#010** | `Shift + D` > 複製して鍵B（中型チェストキー）を作成 | Scale: 0.82, Location: (-0.05m, -0.02m, 0.02m) | 長さや形状の異なる2本目の鍵を配置。 |
| **#011** | 鍵BのBowをハート型/ダブルリングに変形 | `R` > `Y: -15 deg, X: 10 deg` | 鍵同士がぶつかり合ってジャラリと擦れ合うランダムな角度差を付与。 |
| **#012** | `Shift + D` > 複製して鍵C（小型扉キー）を作成 | Scale: 0.65, Location: (0.05m, 0.03m, 0.04m) | 3本目の小さな真鍮鍵。 |
| **#013** | `Modifier` > `Bevel` (全オブジェクト) | Width: 0.003m, Segments: 2 | 鍛造鉄の角が削れ、長年の使用で丸みを帯びた摩耗感を再現。 |
| **#014** | `Material Assign` > `M_Key_ForgedIron` | リングおよび鍵A・Bに適用 | 黒錆と鉄光沢が混ざり合う重厚な中世アイアンシェーダー。 |
| **#015** | `Material Assign` > `M_Key_Brass` | 鍵Cに適用 | 特別の部屋を開ける古びたアンティーク真鍮。 |
| **#016** | `Material Assign` > `M_Key_Rust` | 溝やビットの隙間にブレンド | 湿った地下牢で浮き出た茶褐色の赤錆プロシージャルノイズ。 |
| **#017** | `Shade Auto Smooth` | 角度 35° | 金属の円筒ハイライトとビットの切り込みエッジをクッキリ両立。 |

---

## マテリアル ＆ サウンド設計 (Audio & Physics)

| スロット名 | 材質分類 (Surface Type) | Wwise / CRI Audio Tag | シェーダー設定の要点 |
| :--- | :--- | :--- | :--- |
| **M_Key_ForgedIron** | `Metal_Heavy` | `Sound_Key_Clink_Heavy` | 鍛造鉄。Metallic 0.95, Roughness 0.42。重い鉄同士のガシャリ衝突音。 |
| **M_Key_Brass** | `Metal_Light` | `Sound_Key_Jingle_Light` | 真鍮。Metallic 0.98, Roughness 0.32。歩行時にジャラジャラ鳴る高い鈴鳴り音。 |
| **M_Key_Rust** | `Metal_Rust` | `Sound_Key_Insert_Lock` | 赤錆。Metallic 0.2, Roughness 0.95。鍵穴に差し込んだ際のザラリとした摩擦音。 |
