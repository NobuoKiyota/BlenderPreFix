# 💎 プロシージャル水晶クラスタ (Crystal Cluster) レシピ

## 1. 概要と一次情報
- **カテゴリ**: 3Dオブジェクト / 鉱石
- **参照元**: Blender Procedural Crystal Cluster Tutorial (Sacoche Ito & Mdesign 技法統合)
- **対象バージョン**: Blender 5.2 / 3.6+

## 2. 幾何学とモディファイア設計
1. **結晶（Crystal Prism）Bmesh生成**:
   - 底面6頂点（六角柱, Segments=6）。
   - 高さ80%まで垂直に柱を伸ばし、残り20%で先端トップ頂点に向かってピラミッド状に収束。
   - 先端頂点を微小に偏心させることで、天然水晶の有機的な結晶成長を表現。
   - `poly.use_smooth = False` によりファセット（シャープなカット面）を維持。
2. **群生（Clustering）**:
   - 中央のメイン結晶（高さ3.2, 半径0.45）を配置。
   - 周囲に10〜12本のサブ結晶を外向きの傾き（Tilt: 15〜35度）とランダム回転をつけて配置。
3. **台座（Base Rock）**:
   - Cube を押し出し、Subdivision Modifier (Level 2) ＋ Voronoi Texture Displace Modifier (Strength 0.35) により凹凸岩石を形成。

## 3. シェーダー設計
- **Crystal_Gem_Mat**:
  - `Base Color`: 水晶シアン `(0.2, 0.7, 1.0)`
  - `Roughness`: 0.08（滑らかな鏡面反射）
  - `IOR`: 1.544（石英・水晶の物理屈折率）
  - `Transmission`: 0.92（内部光透過）
  - `Emission`: `(0.1, 0.5, 0.9)`, Strength: 0.8
- **Base_Rock_Mat**:
  - `Base Color`: `(0.12, 0.12, 0.13)`, `Roughness`: 0.85
  - Procedural Noise + Bump Modifier による岩肌質感

## 4. ゲーム ＆ サウンド連動 (Wwise / CRI / Unity / UE)
| マテリアルスロット | Surface ID | オーディオタグ | イベント内容 |
|---|---|---|---|
| `Crystal_Gem_Mat` | Crystal | `Footstep_Glass` | 高硬度クリスタル接触音・硬質反射 |
| `Base_Rock_Mat` | Stone | `Footstep_Stone` | 硬い岩石の足音・破砕音 |

## 5. 一発生成スクリプト
- スクリプト: `e:/BlenderPreFix/generators/gen_crystal_cluster.py`
