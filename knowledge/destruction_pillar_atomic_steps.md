# 💥 古代石柱の剛体破壊シミュレーション＆UE5最適化ベイク 完全構築ガイド（アトミック35ステップ）

本ドキュメントは、YouTubeチュートリアル（FxForge: *Realistic destruction effects in blender*）で実証された高度な破壊物理パイプラインを完全解剖し、初心者からテクニカルアーティストまでが再現・応用できるように設計された全35ステップの詳細解説です。

---

## 🏗️ 全体アーキテクチャ概要

```
[プロシージャル古代石柱モデリング (Doric Column)]
          ↓
[Cell Fracture ボロノイ破砕 (内外マテリアル分離)]
          ↓
[地面アンカー (Passive) ＆ 上部動的剛体 (Active)]
          ↓
[Rigid Body Connect: Breakable 接着コンストレイント (Threshold: 25.0)]
          ↓
[Kinematic 重砲弾コライダー (キーフレーム衝突)]
          ↓
[Bullet Physics 剛体シミュレーション評価 (Frame 1〜90)]
          ↓
[Decompose による純粋キーフレーム全自動ベイク (Zero-Runtime Cost)]
          ↓
[UE5最適化 FBX 一発出力 (Nパネル常駐) ＆ Webカタログ GLB]
```

---

## 📋 全35アトミックステップ解説

### Phase 1: シーン構築＆PBRマテリアル設計
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **01** | シーン初期化 | `bpy.ops.object.select_all(action='SELECT')`<br>`bpy.ops.object.delete()` | 既存メッシュやキャッシュの混入を防ぎ、決定論的再現性を担保する。 |
| **02** | 剛体ワールドの構築 | `bpy.ops.rigidbody.world_add()`<br>`scene.rigidbody_world.point_cache.frame_end = 90` | Bullet Physics エンジンをシーンに登録し、計算フレーム範囲を定義。 |
| **03** | 外側石材マテリアル生成 | `create_outer_stone_material()`<br>Color: `(0.86, 0.84, 0.80)`, Roughness: `0.42` | 風化した古代大理石の質感を Principled BSDF で表現。 |
| **04** | 微細凹凸のノイズ合成 | `ShaderNodeTexNoise(Scale=24, Detail=8)`<br>`ShaderNodeBump(Strength=0.18)` | 石材表面の微細な研磨痕と経年変化をノーマルマップとして注入。 |
| **05** | 内側破断面マテリアル生成 | `create_inner_chipped_material()`<br>Voronoi + Noise Mix | 破壊された断面に現れる粗い砂岩・骨材・砕石の荒々しい質感をプロシージャル生成。 |
| **06** | 破断面カラーランプ設定 | `ColorRamp`: 暗い砕石芯 `(0.38, 0.35, 0.31)` 〜 粉塵色 `(0.68, 0.64, 0.58)` | 破砕された中心部ほど暗く、外縁部ほど削れて白っぽくなる現実の物理現象を模倣。 |
| **07** | 破断面ディスプレイスメント | `ShaderNodeBump(Strength=0.70, Distance=0.12)` | 外側大理石と対比的な激しい凹凸をノーマルに反映し、二重マテリアル分離を強調。 |
| **08** | 鋳鉄砲弾マテリアル生成 | `create_cannonball_material()`<br>BaseColor: `(0.08, 0.08, 0.09)`, Metallic: `0.95` | 重厚な黒色鋳鉄の光沢と微小な鍛造ノイズバンプを設定。 |

### Phase 2: プロシージャル古代装飾石柱の生成
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **09** | 溝付き柱身 (Fluted Shaft) の生成 | `build_fluted_shaft(radius=0.36, height=2.4, flutes=16)` | BMesh で 16 本のフルート溝を持つドリス式石柱を数式から自動生成。 |
| **10** | マテリアルスロットの二重割り当て | `shaft.data.materials.append(outer_mat)`<br>`shaft.data.materials.append(inner_mat)` | Slot 0 に外側、Slot 1 に破断面を事前登録し、Cell Fracture 時に即座に割り当て可能にする。 |
| **11** | 柱頭 (Capital) の追加 | `primitive_cube_add`, Scale: `(0.92, 0.92, 0.18)` | 正方形のアバカス（盤石）を柱頂上に配置し、古典建築の重厚感を付与。 |
| **12** | 柱座 (Base) の追加 | `primitive_cylinder_add(radius=0.48, depth=0.15)` | 円柱状のトールス（円環）を柱の足元に配置。 |
| **13** | メッシュの一体結合 | `bpy.ops.object.join()`<br>Name: `Stone_Pillar_Solid` | 単一のソリッドメッシュに統合することで、Cell Fracture が全体を跨いで破砕可能にする。 |
| **14** | 石畳台座 (Pedestal) の追加 | `primitive_cube_add`, Scale: `(6.5, 6.5, 0.20)` | 瓦礫を受け止める広い地面を生成し、Passive 剛体を付与。 |

### Phase 3: Cell Fracture 破砕 ＆ 剛体接着コンストレイント
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **15** | Cell Fracture アドオン有効化 | `addon_utils.enable("object_fracture_cell")` | Blender 組み込みのボロノイ破砕アドオンを Python からオンにする。 |
| **16** | ボロノイ破砕の実行 | `source_limit=45, source_noise=0.40`<br>`margin=0.0, material_index=1` | 45 個のランダムな破片に細分化し、破断面に自動で Slot 1（砕石）を割り当てる。 |
| **17** | 元メッシュの完全消去 | `bpy.data.objects.remove(pillar_obj, do_unlink=True)` | **【超重要】** 元メッシュが重なって破片を覆い隠す致命的な不具合を 100% 防止する。 |
| **18** | 重心への原点リセット | `bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')` | **【剛体物理の黄金律】** 原点が親メッシュのままだと Bullet 物理が正しく計算されず静止するため、各破片の幾何中心に原点を強制再配置。 |
| **19** | 地面アンカー破片の分離 (Passive) | `if z < 0.35: rigidbody.add(type='PASSIVE')` | **【自立の秘密】** 最下部の破片を地面アンカー（Passive）とすることで、直撃前の自重崩壊を完全に防ぐ。 |
| **20** | 動的破片の設定 (Active) | `if z >= 0.35: rigidbody.add(type='ACTIVE')`<br>Mass: `10.0kg`, Shape: `CONVEX_HULL` | 上部破片を動的剛体にし、衝撃で吹き飛ぶように質量と反発係数を調整。 |
| **21** | 破片群の選択とアクティブ指定 | `shards[0].select_set(True)`<br>`context.view_layer.objects.active = shards[0]` | 全破片を選択しつつ、先頭オブジェクトを Active にして Connect の準備を整える。 |
| **22** | Breakable 接着コンストレイント構築 | `bpy.ops.rigidbody.connect(con_type='FIXED', connection_pattern='CHAIN_DISTANCE')` | 隣接する破片同士を接着剤（Glue）のように Fixed コンストレイントで連結。 |
| **23** | 破壊閾値 (Breaking Threshold) の注入 | `c.use_breaking = True`<br>`c.breaking_threshold = 25.0` | **【FxForge 極意】** 衝撃を受けると接着が解除され、連鎖的に破片が分離する閾値を設定。 |

### Phase 4: 砲弾コライダー＆キーフレーム軌道
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **24** | 大口径重砲弾の生成 | `primitive_uv_sphere_add(radius=0.40)`<br>Location: `(0, -3.5, 1.55)` | 柱の中央部（Z=1.55m）を正確に撃ち抜く大質量砲弾を配置。 |
| **25** | Kinematic Passive 剛体化 | `ball.rigid_body.kinematic = True` | アニメーションキーフレームに従って動きつつ、接触した Active 剛体に無限の衝撃力を与える。 |
| **26** | 衝突軌道キーフレーム設定 | Frame 1 `(-3.5m)` → Frame 7 `(-0.3m)` → Frame 10 `(+0.4m 貫通)` → Frame 70 `(+9.0m)` | 直撃から貫通、飛び去るまでの超高速弾道をキーフレームで制御。 |

### Phase 5: 物理演算評価＆純粋キーフレーム全自動ベイク
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **27** | 順送りシミュレーション評価 | `for f in range(1, 91): scene.frame_set(f)` | Bullet Physics はフレーム飛び越えで計算が破綻するため、1 フレームずつ連続評価して行列を収集。 |
| **28** | ワールド行列の数学的分解 | `loc, rot, sca = mat.decompose()` | **【クリティカル技術】** `matrix_world` の代入だけでは `location` プロパティが更新されないため、Decompose して純粋なローカル移動・回転を抽出。 |
| **29** | キーフレームへの直接刻印 | `s.location = loc; s.keyframe_insert('location', frame=f)`<br>`s.rotation_euler = rot.to_euler(); s.keyframe_insert('rotation_euler', frame=f)` | 破片ごとに 90 フレーム分の座標・回転を F-Curve に焼き込み、実行時計算コストを完全ゼロ化。 |
| **30** | 剛体コンポーネントの安全無効化 | `s.rigid_body.enabled = False` | ベイク完了後に剛体を無効化し、メモリ解放クラッシュ（`removeConstraintRef`）を完全に回避。 |

### Phase 6: レンダリング・エクスポート・UI常駐
| Step | 操作内容 | Python API / 設定値 | 技術的理由・Tips (Why & How) |
|---|---|---|---|
| **31** | スタジオ 3 点照明の配置 | KeySun (5.0), FillLight (90.0), GroundGlow (50.0) | 破片の影と破断面の陰影を際立たせるドラマチックなライティングを構築。 |
| **32** | 4 アングル シネマティックレンダリング | Frame 10 (メインサムネ＆接写), Frame 25 (崩落俯瞰), Frame 5 (直撃前) | 衝撃の瞬間・破断面・崩落の物語を表現する 4 枚の Cycles 画像を出力。 |
| **33** | Unreal Engine 5 最適化 FBX 出力 | `apply_scale_options='FBX_SCALE_ALL'`, `bake_anim=True` | UE5 インポート時にアニメーション付き Skeletal/Static Mesh として即座に動作する FBX を出力。 |
| **34** | Web カタログ用 GLB 出力 | `export_animations=True`, `export_force_sampling=True` | Web 3D カタログ（Three.js）でユーザーがマウスで 360 度回転・破壊再生できる GLB を出力。 |
| **35** | 3D Viewport N パネル UI ボタン常駐 | `OBJECT_OT_ExportDestructionUE5FBX`<br>`VIEW3D_PT_DestructionExportPanel` | Blender UI のサイドバーに「Unreal Engine 5 一発出力」ボタンを常駐させ、ワンクリック運用を実現。 |

---

## 💡 ゲームエンジン（UE5 / Unity）運用のベストプラクティス

1. **UE5 へのインポート手順**:
   - `destruction_pillar_ue.fbx` をコンテンツブラウザにドラッグ＆ドロップ。
   - **Import Animations** にチェックを入れる。
   - レベルに配置し、シーケンサー（Level Sequence）で再生、またはブループリントから「被弾イベント」として再生可能。
2. **サウンドデザイナー向け連携 Tips**:
   - Frame 7（直撃時）: 大砲着弾・金属衝撃音（Heavy Impact Sub-bass + Metallic Clang）
   - Frame 10〜15（破砕時）: 石材破砕・粉塵音（Stone Crack + Gravel Scatter）
   - Frame 20〜30（崩落時）: 重量瓦礫落下の重低音（Rumble & Thud）
   - このベイクアニメーションのタイムラインと DAW / Wwise / CRI のキューをミリ秒単位で完全に同期させることが可能です。
