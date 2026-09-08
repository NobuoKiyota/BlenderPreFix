# 🔥 スタイライズド焚き火 VFX (Stylized Campfire) レシピ

## 1. 概要と一次情報
- **カテゴリ**: VFX / エフェクト
- **参照元**: Blender Stylized Fire & Campfire Tutorial (E:\BlenderVFX 資産統合)
- **対象バージョン**: Blender 5.2 / 3.6+

## 2. 幾何学とモディファイア設計
1. **薪（Logs）**:
   - Cylinder（半径0.12, 高さ1.6）を 6 本放射状に配置。
   - 傾き（Tilt: 15〜25度）とランダム回転をつけて中央でクロスするよう交差。
2. **火炎メッシュ（Flame Core & Sub）**:
   - Cone（底面半径0.45, 先端0.02, 高さ1.5）を変形。
   - `Subdivision Modifier` (Level 2) でメッシュを細分化。
   - `Displace Modifier` (Clouds Texture, Noise Scale 0.5, Strength 0.25) により有機的な炎の揺らめきをプロシージャル付与。
3. **火花（Sparks）**:
   - Icosphere（Subdivision 1）を炎の上部（高さ0.8〜2.2）にランダム散布。

## 3. シェーダー設計
- **Stylized_Flame_Mat**:
  - Principled BSDF の `Base Color` に暖色オレンジ `(1.0, 0.35, 0.05)`
  - `Emission Color`: `(1.0, 0.45, 0.05)`, `Emission Strength`: `3.5`
- **Spark_Emission_Mat**:
  - `Emission Color`: `(1.0, 0.8, 0.1)`, `Emission Strength`: `8.0`
- **Charred_Wood_Mat**:
  - 焦げた木材表現: `Base Color`: `(0.05, 0.03, 0.02)`, `Roughness`: `0.9`

## 4. ゲーム ＆ サウンド連動 (Wwise / CRI / Unity / UE)
| マテリアルスロット | Surface ID | オーディオタグ | イベント内容 |
|---|---|---|---|
| `Stylized_Flame_Mat` | Fire | `Sound_Campfire_Loop` | 焚き火ループ環境音 |
| `Charred_Wood_Mat` | Wood | `Footstep_Wood_Charred` | 木材接触・炭化足音 |
| `Spark_Emission_Mat` | Fire | `Sound_Ember_Crack` | パチパチ爆ぜる火花音 |

## 5. 一発生成スクリプト
- スクリプト: `e:/BlenderPreFix/generators/gen_campfire_vfx.py`
