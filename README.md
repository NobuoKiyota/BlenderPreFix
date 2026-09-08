# 🌟 Blender 自走学習・一発生成・Webカタログポータル

Blenderのプロ技法（モデリング、VFX、Geometry Nodes、シェーダー）を継続的に学習・コード化し、いつでもブラウザから3Dプレビューと解説、一発生成コードを確認できる自律型ナレッジ基盤です。

---

## 🚀 クイックスタート

### 1. Webカタログをブラウザで開く
プロジェクト直下の `open_catalog.bat` をダブルクリックするか、`catalog/index.html` をブラウザで直接開きます。
- **3D インタラクティブプレビュー**: Google `<model-viewer>` により、生成されたGLBアセットを360度回転・ズーム・パン可能。
- **レンダリング画像**: Blender Cycles/EEVEE でレンダリングされた高画質サムネイル。
- **技法解説**: 使用されているモディファイア、ノードツリー、数式、物理パラメータの解説。
- **ゲーム ＆ サウンド連動**: Wwise / CRI / Unity / UE 向けの Surface ID / マテリアルスロット仕様。
- **ワンクリック一発生成**: BlenderのPythonコンソールで即座に実行できるコードのコピー。

### 2. Blender で一発生成スクリプトを実行する
Blender 5.2（または 3.6+）を起動し、Scripting ワークスペースで以下のいずれかを実行します：

```python
# 焚き火 VFX の一発生成
exec(open(r"e:/BlenderPreFix/generators/gen_campfire_vfx.py", encoding="utf-8").read())

# 水晶クラスタ の一発生成
exec(open(r"e:/BlenderPreFix/generators/gen_crystal_cluster.py", encoding="utf-8").read())
```

または、コマンドラインから Headless 実行＆アセット出力：
```bash
python tools/blender_runner.py generators/gen_campfire_vfx.py catalog/assets/my_fire.glb catalog/assets/my_fire.png
```

---

## 📁 ディレクトリ構成

- **`catalog/`**: HTML成果物ポータル
  - `index.html`: スタンドアロンWebカタログUI
  - `assets/`: 生成された GLB 3Dモデルおよび PNG レンダリング画像
- **`generators/`**: 一発生成 Python スクリプト群
  - `gen_campfire_vfx.py`: スタイライズド焚き火 VFX
  - `gen_crystal_cluster.py`: プロシージャル水晶クラスタ
- **`knowledge/`**: 各スキルの一次情報・ノード構成・パラメータ詳細レシピ（Markdown）
- **`tools/`**:
  - `blender_runner.py`: Blender Headless 実行・アセット出力ユーティリティ
  - `youtube_extractor.py`: YouTube 字幕・メタデータ抽出ツール（`yt-dlp` 連携）
  - `pipeline_manager.py`: 自走学習カタログ登録マネージャ
- **`open_catalog.bat`**: Webカタログ一発起動バッチ
