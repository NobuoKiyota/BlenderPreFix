# 🔥 カサハラCG式 リアル焚き火シミュレーション ＆ シェーダー レシピ

## 1. 概要と一次情報
- **チュートリアル名**: 【Blender】初めての炎！【焚き火篇】リアルな炎を簡単に作れます！
- **チャンネル**: カサハラ CG
- **URL**: https://www.youtube.com/watch?v=lodqjYDXIxk
- **対象バージョン**: Blender 5.2.1 LTS / 3.6+

## 2. 物理シミュレーション（MantaFlow）パラメータ
1. **発生源（Flow: UV Sphere）**:
   - スケール: `0.4`
   - Flow Type: `FIRE`（火炎）
   - Fuel（燃料）: `2.0`
   - Flow Source: Surface Distance = `1.0`
   - Flow Texture: `Clouds`, Size = `0.1`, Contrast = `5.0`
2. **フォースフィールド（Turbulence）**:
   - Type: `TURBULENCE`
   - Strength: `0.4`
   - Noise Amount: `0.4`
3. **ドメイン（Domain: Box）**:
   - Domain Type: `GAS`
   - Resolution Divisions: `128` (プレビューテストは `64`)
   - Adaptive Domain: `True`（計算量削減）
   - Vorticity（渦度）: `0.1`
   - Reaction Speed（反応速度）: `1.0`
   - Cache: Type = `MODULAR`, Is Resumable = `True`, End Frame = `200`

## 3. Principled Volume シェーダー設計（核心技法）
ドメインに適用するボリュームマテリアル：
- **入力ノード**: `ShaderNodeAttribute` (Name: `"heat"`)
- **放射強度（Emission Strength）制御**:
  - `Attribute ("heat") Fac` → `ColorRamp` (0.0: 黒, 0.45: 白, 0.7: 濃いグレー)
  - `Math Node` (Type: `MULTIPLY`, Value: `50.0`)
  - `Texture Coordinate (Generated)` → `Mapping (Location Z に #frame ドライバ)`
  - `Noise Texture` (Scale: `8.0`, Detail: `9.2`, Distortion: `1.0`) → `ColorRamp`
  - `Math Node` (Type: `MULTIPLY`) で結合し `Principled Volume (Emission Strength)` へ入力
- **放射色（Emission Color）制御**:
  - `Attribute ("heat") Fac` → `ColorRamp` (黒 → 鮮やかなオレンジ `(1.0, 0.35, 0.05)` → 黄色 `(1.0, 0.85, 0.1)`) → `Emission Color`
- **煙の非表示**:
  - `Density`: `0.0`（煙を消して炎のみを強調）

## 4. ゲーム ＆ サウンド連動 (Wwise / CRI / Unity / UE)
| マテリアルスロット | Surface ID | オーディオタグ | イベント内容 |
|---|---|---|---|
| `Kasahara_Fire_Volume_Mat` | Fire | `Sound_Campfire_Loop` | リアル焚き火ループ環境音 |
| `Charred_Wood_Mat` | Wood | `Footstep_Wood_Charred` | 薪の炭化・接触音 |
| `Fire_Light_Emitter` | Fire | `Sound_Fire_Crackle` | 火の粉爆ぜ音 |

## 5. 一発生成スクリプト
- `e:/BlenderPreFix/generators/gen_kasahara_campfire.py`
