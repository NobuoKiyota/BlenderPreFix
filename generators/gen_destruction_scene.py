"""
================================================================================
💥 GEN_DESTRUCTION_SCENE.PY - MULTI-SHAPE & REALISTIC BRICK WALL SIMULATOR
================================================================================
【機能概要】
1. 6大破壊形状プロシージャル生成:
   - 0: "RANDOM"     : 押すたびに完全ランダム選定
   - 1: "ROCK"       : 3Dプロシージャルノイズで歪んだ巨大なゴツゴツ天然巨岩 (Boulder)
   - 2: "WALL"       : 荒削りな岩肌・凹凸を持つゴツゴツ断崖石壁 (Craggy Cliff Wall)
   - 3: "BUILDING"   : 4本支柱＋各階スラブで構成された中空タワー（連鎖重力崩壊）
   - 4: "PILLAR"     : 古代装飾石柱の360度大爆散
   - 5: "GROUND"     : 巨大隕石垂直落下による放射状地割れ・奈落陥没
   - 6: "BRICK_WALL" : ★動画参考！本格千鳥積みレンガ壁＋モルタル接着破断＋漆喰細片デブリ
2. 🎬 スローモーション演出 (TIME_SCALE):
   - 物理演算タイムスケール制御により、激突〜破砕の瞬間を映画的スーパースローで再生
3. ⚡ 形状キープ ＆ 物理だけ即時調整 (Quick Re-Simulate):
   - Nパネルの専用スライダーとボタンで角度・サイズ・威力・スローを瞬時リベイク
================================================================================
"""

import bpy
import bmesh
import math
import os
import sys
import random
import mathutils
import addon_utils

# ==============================================================================
# 🎛️ 実行制御スイッチ (Execution Switches)
# ==============================================================================
# 形状タイプ (数字または文字列で指定可能)
# 0 = RANDOM     (押すたびにランダム選定)
# 1 = ROCK       (ゴツゴツ自然巨岩)
# 2 = WALL       (荒削り断崖岩壁)
# 3 = BUILDING   (中空多層タワー・連鎖崩壊)
# 4 = PILLAR     (古代装飾石柱)
# 5 = GROUND     (地割れ陥没地面)
# 6 = BRICK_WALL (本格千鳥積みレンガ壁 ＆ モルタル接着 ＆ 漆喰デブリ)
TARGET_SHAPE        = 6

# 乱数シード: None で毎回完全ランダム
SEED                = None

# ⚡ 形状キープモード: Trueにすると現在の破片形状を保ったまま、角度や威力だけ再計算
KEEP_SHAPE_MODE     = False

# 💥 破砕の細かさ・威力コントロール
SHARD_COUNT         = 160    # 破片の分割数 (ROCK, WALL, GROUND等で使用)
SHARD_NOISE         = 0.65   # 破片形状のギザギザ度
SHOCK_POWER         = 5500.0 # 爆散衝撃波の威力

# ⏱️ スローモーション倍率 (1.0 = 通常速度, 0.4 = 映画的ドラマチックスロー, 0.2 = スーパースロー)
TIME_SCALE          = 0.50

# 🧱 レンガ壁用パラメータ (TARGET_SHAPE=6)
BRICK_ROWS          = 11     # レンガの段数 (高さ方向)
BRICK_COLS          = 13     # レンガの列数 (横幅方向)
BRICK_W             = 0.42   # レンガ幅
BRICK_H             = 0.18   # レンガ高さ
BRICK_D             = 0.22   # レンガ奥行き
MORTAR_THRESHOLD    = 3.5    # モルタルの接着破断限界 (小さいと崩れやすく、大きいと頑丈)
ENABLE_PLASTER_DEBRIS = True # 表面漆喰・モルタルの微細破砕片を生成

# 💥 爆発エフェクト・パーティクル・粉砕追学習設定
ENABLE_EXPLOSION_SPARKS = True   # 衝突瞬間の爆散火花・火の粉パーティクル
SPARK_COUNT             = 350    # 火花パーティクル数
SPARK_SPEED             = 18.0   # 火花の初速
ENABLE_EXPLODE_DEBRIS   = True   # Explodeモディファイアによる瞬間粉砕メッシュ
EXPLODE_PIECE_COUNT     = 200    # Explode粉砕片数
ENABLE_MANTAFLOW_FIRE   = False  # Mantaflow火炎・煙ボリューム (重厚シミュレーション・動画レンダリング用)

# 🎲 物理挙動のランダム化コントロール
RANDOM_PHYSICS      = True
BALL_SIZE           = None   # None: 自動 (0.40〜0.85m)
IMPACT_ANGLE_H      = None   # None: 自動 (-35°〜+35°)
IMPACT_ANGLE_V      = None   # None: 自動 (0°〜15°)

EXPORT_UE_FBX       = True
EXPORT_CATALOG_GLB  = True
ANIM_TOTAL_FRAMES   = 100    # アニメーション総フレーム (約3.3秒)
FPS                 = 30

def ensure_cell_fracture_addon():
    """Blender 3.6 から 5.2 まですべてのバージョンで Cell Fracture を確実に利用可能にする"""
    if hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects'):
        return True
    try:
        addon_utils.enable("object_fracture_cell")
    except Exception:
        pass
    if hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects'):
        return True

    this_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"e:\BlenderPreFix\generators"
    proj_root = os.path.dirname(this_dir)
    candidate_paths = [
        os.path.join(proj_root, "addons"),
        r"e:\BlenderPreFix\addons",
        os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons"),
    ]
    for p in candidate_paths:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)

    try:
        import object_fracture_cell
        object_fracture_cell.register()
        return True
    except Exception as e:
        print("⚠️ Direct registration failed:", e)

    return hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects')

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def set_active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

# ------------------------------------------------------------------------------
# 🎨 1. マテリアル生成
# ------------------------------------------------------------------------------
def create_brick_material():
    mat = bpy.data.materials.new(name="Mat_RedBrick")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.62, 0.24, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.88
    return mat

def create_mortar_material():
    mat = bpy.data.materials.new(name="Mat_Mortar_Plaster")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.73, 0.70, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.95
    return mat

def create_outer_stone_material():
    mat = bpy.data.materials.new(name="Mat_Pillar_Stone")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.72, 0.69, 0.65, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85
    return mat

def create_inner_chipped_material():
    mat = bpy.data.materials.new(name="Mat_Chipped_Interior")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.42, 0.38, 0.35, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.92
    return mat

def create_cannonball_material():
    mat = bpy.data.materials.new(name="Mat_CannonBall")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.92
        bsdf.inputs['Roughness'].default_value = 0.28
    return mat

def create_spark_material():
    mat = bpy.data.materials.new(name="Mat_Explosion_Spark")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    emit = nodes.new(type='ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.45, 0.05, 1.0) # オレンジ〜黄色
    emit.inputs['Strength'].default_value = 25.0
    mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def create_fire_smoke_material():
    mat = bpy.data.materials.new(name="Mat_Mantaflow_FireSmoke")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    vol = nodes.new(type='ShaderNodeVolumePrincipled')
    vol.inputs['Density'].default_value = 4.0
    vol.inputs['Blackbody Intensity'].default_value = 1.5
    vol.inputs['Blackbody Tint'].default_value = (1.0, 0.5, 0.1, 1.0)
    vol.inputs['Temperature'].default_value = 1600.0
    mat.node_tree.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    return mat

def create_brick_mesh_obj(name, w, d, h, loc, mat, bevel_w=0.008):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    if bevel_w > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel_w, segments=2, profile=0.5, affect='EDGES')
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

# ------------------------------------------------------------------------------
# 🧱 2. 本格レンガ壁＆モルタル結合生成 (Granite Films スタイル)
# ------------------------------------------------------------------------------
def build_brick_wall_structure(brick_mat, mortar_mat, seed_val):
    random.seed(seed_val)
    print(f"🧱 Building realistic running-bond brick wall ({BRICK_ROWS}x{BRICK_COLS})...")

    wall_width = BRICK_COLS * BRICK_W
    wall_height = BRICK_ROWS * BRICK_H
    start_x = -wall_width / 2.0 + BRICK_W / 2.0
    start_z = BRICK_H / 2.0 + 0.10 # 台座の上

    brick_objs = []
    grid = {}

    # 1. レンガを千鳥積み (Running Bond) で配置 (bmeshで直接生成し原点を維持)
    for row in range(BRICK_ROWS):
        z = start_z + row * (BRICK_H + 0.005)
        is_odd = (row % 2 == 1)
        row_offset = (BRICK_W * 0.5) if is_odd else 0.0

        for col in range(BRICK_COLS):
            x = start_x + col * (BRICK_W + 0.005) + row_offset
            jitter_x = random.uniform(-0.003, 0.003)
            jitter_y = random.uniform(-0.003, 0.003)

            b_name = f"cell_brick_r{row:02d}_c{col:02d}"
            brick = create_brick_mesh_obj(
                b_name,
                BRICK_W * 0.98, BRICK_D, BRICK_H * 0.98,
                (x + jitter_x, jitter_y, z),
                brick_mat,
                bevel_w=0.008
            )
            brick_objs.append(brick)
            grid[(row, col)] = brick

    # 2. 台座地面の作成
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
    ground_obj = bpy.context.active_object
    ground_obj.name = "Scene_Ground"
    ground_obj.scale = (wall_width + 4.0, 7.0, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ground_obj.data.materials.append(mortar_mat)

    # 3. 剛体物理＆キーフレーム初期化
    for b in brick_objs:
        bpy.context.view_layer.objects.active = b
        if not b.rigid_body:
            bpy.ops.rigidbody.object_add(type='ACTIVE')
        b.rigid_body.collision_shape = 'BOX'
        b.rigid_body.mass = 6.0
        b.rigid_body.friction = 0.85
        b.rigid_body.restitution = 0.10
        b.rigid_body.linear_damping = 0.02
        b.rigid_body.angular_damping = 0.02

        b.rigid_body.kinematic = True
        b.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
        b.keyframe_insert(data_path='rigid_body.kinematic', frame=7)
        b.rigid_body.kinematic = False
        b.keyframe_insert(data_path='rigid_body.kinematic', frame=8)

    # 4. モルタル接着コンストレイント (Fixed Breakable Constraints) を直接接続
    mortar_count = 0
    for (r, c), b in grid.items():
        # 水平方向 (左右)
        if (r, c + 1) in grid:
            b_right = grid[(r, c + 1)]
            empty = bpy.data.objects.new(f"Mortar_H_r{r:02d}_c{c:02d}", None)
            bpy.context.scene.collection.objects.link(empty)
            empty.location = (b.location + b_right.location) * 0.5
            bpy.context.view_layer.objects.active = empty
            bpy.ops.rigidbody.constraint_add(type='FIXED')
            empty.rigid_body_constraint.object1 = b
            empty.rigid_body_constraint.object2 = b_right
            empty.rigid_body_constraint.use_breaking = True
            empty.rigid_body_constraint.breaking_threshold = MORTAR_THRESHOLD
            mortar_count += 1

        # 垂直方向 (上下)
        if (r + 1, c) in grid:
            b_up = grid[(r + 1, c)]
            empty = bpy.data.objects.new(f"Mortar_V_r{r:02d}_c{c:02d}", None)
            bpy.context.scene.collection.objects.link(empty)
            empty.location = (b.location + b_up.location) * 0.5
            bpy.context.view_layer.objects.active = empty
            bpy.ops.rigidbody.constraint_add(type='FIXED')
            empty.rigid_body_constraint.object1 = b
            empty.rigid_body_constraint.object2 = b_up
            empty.rigid_body_constraint.use_breaking = True
            empty.rigid_body_constraint.breaking_threshold = MORTAR_THRESHOLD
            mortar_count += 1

    print(f"🧱 Created {len(brick_objs)} bricks and {mortar_count} mortar fixed-breakable constraints!")

    # 5. 表面漆喰・微細破片 (Plaster / Debris Chips) レイヤー
    debris_objs = []
    if ENABLE_PLASTER_DEBRIS:
        debris_objs = build_plaster_debris_layer(wall_width, wall_height, mortar_mat, seed_val)

    all_shards = brick_objs + debris_objs
    hit_target = (0.0, 0.0, wall_height * 0.45)

    return all_shards, ground_obj, hit_target

def build_plaster_debris_layer(width, height, mortar_mat, seed_val):
    ensure_cell_fracture_addon()
    print("💥 Creating fine plaster & mortar debris layer...")

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, BRICK_D * 0.52, height * 0.5 + 0.10)
    )
    plaster = bpy.context.active_object
    plaster.name = "Plaster_Layer"
    plaster.scale = (width * 0.95, 0.02, height * 0.92)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    plaster.data.materials.append(mortar_mat)

    set_active(plaster)
    bpy.ops.object.add_fracture_cell_objects(
        source_limit=70,
        source_noise=0.85,
        margin=0.0,
        material_index=0,
        use_smooth_faces=False,
        use_sharp_edges=True,
        use_remove_original=True
    )

    debris = [o for o in bpy.context.scene.objects if 'plaster_layer_cell' in o.name.lower()]
    for d in debris:
        bpy.context.view_layer.objects.active = d
        d.name = f"cell_debris_{d.name}"
        if not d.rigid_body:
            bpy.ops.rigidbody.object_add(type='ACTIVE')
        d.rigid_body.collision_shape = 'CONVEX_HULL'
        d.rigid_body.mass = 0.8
        d.rigid_body.friction = 0.70
        d.rigid_body.restitution = 0.25
        d.rigid_body.linear_damping = 0.01

        d.rigid_body.kinematic = True
        d.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
        d.keyframe_insert(data_path='rigid_body.kinematic', frame=7)
        d.rigid_body.kinematic = False
        d.keyframe_insert(data_path='rigid_body.kinematic', frame=8)

    print(f"✅ Generated {len(debris)} fine plaster debris pieces!")
    return debris

# ------------------------------------------------------------------------------
# 🗿 3. 既存のプロシージャル形状ビルダー群 (ROCK, WALL, BUILDING, PILLAR, GROUND)
# ------------------------------------------------------------------------------
def build_craggy_rock_shape(outer_mat, inner_mat, seed_val):
    random.seed(seed_val)
    hit_pos = (0.0, 0.0, 1.40)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.65, location=hit_pos)
    rock = bpy.context.active_object
    rock.name = "Craggy_Rock_Solid"

    sx = random.uniform(1.05, 1.35)
    sy = random.uniform(0.85, 1.15)
    sz = random.uniform(0.95, 1.30)
    rock.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)

    bm = bmesh.new()
    bm.from_mesh(rock.data)
    n = mathutils.noise
    seed_offset = mathutils.Vector((
        random.uniform(-50.0, 50.0),
        random.uniform(-50.0, 50.0),
        random.uniform(-50.0, 50.0)
    ))
    for v in bm.verts:
        p = (v.co * 0.75) + seed_offset
        disp = n.fractal(p, 0.75, 2.2, 4) * 0.65 - n.noise(p * 1.8) * 0.35
        v.co += v.normal * disp
    bm.to_mesh(rock.data)
    bm.free()
    rock.data.update()

    bpy.ops.object.modifier_add(type='BEVEL')
    bev = rock.modifiers["Bevel"]
    bev.width = 0.06
    bev.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")

    rock.data.materials.append(outer_mat)
    rock.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
    ground = bpy.context.active_object
    ground.name = "Scene_Ground"
    ground.scale = (8.5, 8.5, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    ground.data.materials.append(outer_mat)
    return rock, ground, hit_pos

def build_craggy_wall_shape(outer_mat, inner_mat, seed_val):
    random.seed(seed_val)
    hit_pos = (0.0, 0.0, 1.65)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.70))
    wall = bpy.context.active_object
    wall.name = "Craggy_Wall_Solid"
    wall.scale = (4.6, 1.05, 3.4)
    bpy.ops.object.transform_apply(scale=True)

    sub = wall.modifiers.new("Subsurf", 'SUBSURF')
    sub.subdivision_type = 'SIMPLE'
    sub.levels = 4
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bm = bmesh.new()
    bm.from_mesh(wall.data)
    n = mathutils.noise
    seed_offset = mathutils.Vector((random.uniform(-30, 30), random.uniform(-30, 30), random.uniform(-30, 30)))
    for v in bm.verts:
        if abs(v.co.y) > 0.35:
            p = (v.co * 1.1) + seed_offset
            disp = n.fractal(p, 0.7, 2.0, 3) * 0.32 - n.noise(p * 2.2) * 0.16
            v.co += v.normal * disp
    bm.to_mesh(wall.data)
    bm.free()
    wall.data.update()

    wall.data.materials.append(outer_mat)
    wall.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
    ground = bpy.context.active_object
    ground.name = "Scene_Ground"
    ground.scale = (9.0, 9.0, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    ground.data.materials.append(outer_mat)
    return wall, ground, hit_pos

def build_building_shape(outer_mat, inner_mat):
    tower_parts = []
    col_offsets = [(-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)]
    for ox, oy in col_offsets:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy, 2.4))
        c = bpy.context.active_object
        c.scale = (0.45, 0.45, 4.8)
        bpy.ops.object.transform_apply(scale=True)
        tower_parts.append(c)

    for floor_z in [1.5, 3.0, 4.7]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, floor_z))
        slab = bpy.context.active_object
        slab.scale = (2.6, 2.6, 0.28)
        bpy.ops.object.transform_apply(scale=True)
        tower_parts.append(slab)

    set_active(tower_parts[0])
    for p in tower_parts[1:]:
        p.select_set(True)
    bpy.ops.object.join()
    tower = bpy.context.active_object
    tower.name = "Building_Tower_Solid"
    tower.data.materials.append(outer_mat)
    tower.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
    ground = bpy.context.active_object
    ground.name = "Scene_Ground"
    ground.scale = (8.5, 8.5, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    ground.data.materials.append(outer_mat)
    return tower, ground, (0.0, 0.0, 1.50)

def build_pillar_shape(outer_mat, inner_mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=3.6, location=(0, 0, 1.85))
    pillar = bpy.context.active_object
    pillar.name = "Stone_Pillar_Solid"
    pillar.data.materials.append(outer_mat)
    pillar.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
    pedestal = bpy.context.active_object
    pedestal.name = "Scene_Ground"
    pedestal.scale = (7.5, 7.5, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    pedestal.data.materials.append(outer_mat)
    return pillar, pedestal, (0, 0, 1.40)

def build_ground_shape(outer_mat, inner_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    ground_plate = bpy.context.active_object
    ground_plate.name = "Fracture_Ground_Solid"
    ground_plate.scale = (6.0, 6.0, 0.50)
    bpy.ops.object.transform_apply(scale=True)
    ground_plate.data.materials.append(outer_mat)
    ground_plate.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.17))
    pedestal = bpy.context.active_object
    pedestal.name = "Scene_Ground"
    pedestal.scale = (8.5, 8.5, 0.35)
    bpy.ops.object.transform_apply(scale=True)
    pedestal.data.materials.append(outer_mat)
    return ground_plate, pedestal, (0, 0, 0.30)

# ------------------------------------------------------------------------------
# 💥 4. 一般メッシュ破砕 (ROCK, WALL, TOWER, PILLAR, GROUND)
# ------------------------------------------------------------------------------
def fracture_and_setup_physics(target_obj, shape_type, seed_val):
    ensure_cell_fracture_addon()
    set_active(target_obj)

    random.seed(seed_val)
    print(f"🔨 Fracturing {shape_type} into high-density shards (Seed: {seed_val})...")

    bpy.ops.object.add_fracture_cell_objects(
        source_limit=int(SHARD_COUNT),
        source_noise=float(SHARD_NOISE),
        margin=0.0,
        material_index=1,
        use_smooth_faces=False,
        use_sharp_edges=True,
        use_remove_original=True
    )

    shards = [o for o in bpy.context.scene.objects if 'cell' in o.name.lower()]
    print(f"✅ Generated {len(shards)} high-density fracture shards for {shape_type}!")

    # 元の非破砕オブジェクトが残存している場合は確実に削除
    if target_obj.name in bpy.data.objects:
        bpy.data.objects.remove(target_obj, do_unlink=True)

    for s in shards:
        bpy.context.view_layer.objects.active = s
        if not s.rigid_body:
            bpy.ops.rigidbody.object_add(type='ACTIVE')
        s.rigid_body.collision_shape = 'CONVEX_HULL'
        s.rigid_body.mass = 4.5
        s.rigid_body.friction = 0.60
        s.rigid_body.restitution = 0.40
        s.rigid_body.linear_damping = 0.01
        s.rigid_body.angular_damping = 0.01

        s.rigid_body.kinematic = True
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=7)
        s.rigid_body.kinematic = False
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=8)

    bpy.ops.object.select_all(action='DESELECT')
    for s in shards:
        s.select_set(True)
    bpy.context.view_layer.objects.active = shards[0]
    bpy.ops.rigidbody.connect(con_type='FIXED', connection_pattern='CHAIN_DISTANCE')

    for o in bpy.data.objects:
        if o.rigid_body_constraint:
            o.rigid_body_constraint.use_breaking = True
            o.rigid_body_constraint.breaking_threshold = 2.0

    return shards

# ------------------------------------------------------------------------------
# 🚀 5. 衝突砲弾・衝撃波＆スローモーションセットアップ
# ------------------------------------------------------------------------------
def setup_collider_and_impact(ground_obj, cannon_mat, shape_type, hit_pos, seed_val, custom_params=None):
    set_active(ground_obj)
    if not ground_obj.rigid_body:
        bpy.ops.rigidbody.object_add(type='PASSIVE')
    ground_obj.rigid_body.collision_shape = 'BOX'
    ground_obj.rigid_body.friction = 0.85
    ground_obj.rigid_body.restitution = 0.15

    c_h = custom_params.get('impact_angle_h') if custom_params else IMPACT_ANGLE_H
    c_v = custom_params.get('impact_angle_v') if custom_params else IMPACT_ANGLE_V
    c_size = custom_params.get('ball_size') if custom_params else BALL_SIZE
    c_power = custom_params.get('shock_power') if custom_params else SHOCK_POWER

    random.seed(seed_val)

    if shape_type != "GROUND":
        deg_h = random.uniform(-35.0, 35.0) if (c_h is None and RANDOM_PHYSICS) else (0.0 if c_h is None else float(c_h))
        deg_v = random.uniform(2.0, 18.0) if (c_v is None and RANDOM_PHYSICS) else (6.0 if c_v is None else float(c_v))
        r_ball = random.uniform(0.42, 0.78) if (c_size is None and RANDOM_PHYSICS) else (0.54 if c_size is None else float(c_size))

        rad_h = math.radians(deg_h)
        rad_v = math.radians(deg_v)

        dir_x = math.sin(rad_h) * math.cos(rad_v)
        dir_y = -math.cos(rad_h) * math.cos(rad_v)
        dir_z = -math.sin(rad_v)

        dist_start = 9.0
        dist_end = 9.0

        hx, hy, hz = hit_pos
        start_pt = (hx - dir_x * dist_start, hy - dir_y * dist_start, hz - dir_z * dist_start)
        end_pt   = (hx + dir_x * dist_end,   hy + dir_y * dist_end,   hz + dir_z * dist_end)

        print(f"🚀 Collider Physics: Radius={r_ball:.2f}m, Angle H={deg_h:.1f}°, V={deg_v:.1f}° (Hit: {hx:.2f}, {hy:.2f}, {hz:.2f})")

        bpy.ops.mesh.primitive_uv_sphere_add(radius=r_ball, location=start_pt)
        ball = bpy.context.active_object
        ball.name = "Heavy_CannonBall"
        bpy.ops.object.shade_smooth()
        ball.data.materials.append(cannon_mat)

        set_active(ball)
        if not ball.rigid_body:
            bpy.ops.rigidbody.object_add(type='PASSIVE')
        ball.rigid_body.collision_shape = 'SPHERE'
        ball.rigid_body.kinematic = True

        ball.location = start_pt
        ball.keyframe_insert(data_path='location', frame=1)

        near_hit = (hx - dir_x * 0.25, hy - dir_y * 0.25, hz - dir_z * 0.25)
        ball.location = near_hit
        ball.keyframe_insert(data_path='location', frame=7)

        through_hit = (hx + dir_x * 0.50, hy + dir_y * 0.50, hz + dir_z * 0.50)
        ball.location = through_hit
        ball.keyframe_insert(data_path='location', frame=10)

        mid_pt = (hx + dir_x * 3.5, hy + dir_y * 3.5, hz + dir_z * 3.5)
        ball.location = mid_pt
        ball.keyframe_insert(data_path='location', frame=20)

        ball.location = end_pt
        ball.keyframe_insert(data_path='location', frame=75)

        size_factor = (r_ball / 0.50) ** 1.5
        shock_strength = float(c_power) * size_factor

    else:
        r_ball = 0.70 if c_size is None else float(c_size)
        hx, hy, hz = hit_pos
        start_pt = (hx, hy, 8.5)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r_ball, location=start_pt)
        ball = bpy.context.active_object
        ball.name = "Heavy_Meteor_Ball"
        bpy.ops.object.shade_smooth()
        ball.data.materials.append(cannon_mat)

        set_active(ball)
        if not ball.rigid_body:
            bpy.ops.rigidbody.object_add(type='PASSIVE')
        ball.rigid_body.collision_shape = 'SPHERE'
        ball.rigid_body.kinematic = True

        ball.location = start_pt
        ball.keyframe_insert(data_path='location', frame=1)
        ball.location = (hx, hy, 0.60)
        ball.keyframe_insert(data_path='location', frame=7)
        ball.location = (hx, hy, -0.40)
        ball.keyframe_insert(data_path='location', frame=10)
        ball.location = (hx, hy, -4.50)
        ball.keyframe_insert(data_path='location', frame=25)

        shock_strength = float(c_power) * 1.6

    # 💥 衝撃波フォースフィールド
    bpy.ops.object.effector_add(type='FORCE', location=hit_pos)
    force = bpy.context.active_object
    force.name = "Explosion_Shockwave"
    force.field.strength = 0.0
    force.field.shape = 'POINT'
    force.keyframe_insert(data_path='field.strength', frame=1)
    force.keyframe_insert(data_path='field.strength', frame=7)

    force.field.strength = shock_strength
    force.keyframe_insert(data_path='field.strength', frame=8)

    force.field.strength = shock_strength * 0.4
    force.keyframe_insert(data_path='field.strength', frame=10)

    force.field.strength = 0.0
    force.keyframe_insert(data_path='field.strength', frame=13)

    return ball

# ------------------------------------------------------------------------------
# 💥 5.5. 爆発エフェクト＆微細粉砕システム (YouTube学習: 火花・Explode・Mantaflow)
# ------------------------------------------------------------------------------
def setup_explosion_effects(hit_pos, spark_mat, fire_smoke_mat, custom_params=None):
    scene = bpy.context.scene
    fx_objs = []
    
    enable_sparks = custom_params.get('enable_sparks', ENABLE_EXPLOSION_SPARKS) if custom_params else ENABLE_EXPLOSION_SPARKS
    enable_explode = custom_params.get('enable_explode', ENABLE_EXPLODE_DEBRIS) if custom_params else ENABLE_EXPLODE_DEBRIS
    enable_mantaflow = custom_params.get('enable_mantaflow', ENABLE_MANTAFLOW_FIRE) if custom_params else ENABLE_MANTAFLOW_FIRE
    spark_cnt = custom_params.get('spark_count', SPARK_COUNT) if custom_params else SPARK_COUNT
    spark_spd = custom_params.get('spark_speed', SPARK_SPEED) if custom_params else SPARK_SPEED

    # 1. 火花・火の粉パーティクル用インスタンス形状 (超小型の輝くダイヤモンド形状)
    spark_instance = bpy.data.objects.get("Spark_Instance_Mesh")
    if not spark_instance:
        mesh = bpy.data.meshes.new("Spark_Instance_Mesh")
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.035)
        bm.to_mesh(mesh)
        bm.free()
        spark_instance = bpy.data.objects.new("Spark_Instance_Mesh", mesh)
        scene.collection.objects.link(spark_instance)
        spark_instance.data.materials.append(spark_mat)
        spark_instance.location = (0, 0, -20.0) # ビュー外に退避
        spark_instance.hide_render = True

    # 2. 衝突瞬間の爆散火花 (Sparks / Embers)
    if enable_sparks:
        print(f"✨ Creating explosion spark system ({spark_cnt} particles, speed {spark_spd})...")
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=hit_pos)
        emitter = bpy.context.active_object
        emitter.name = "Explosion_Spark_Emitter"
        emitter.display_type = 'WIRE'
        emitter.hide_render = True
        
        ps_mod = emitter.modifiers.new("Sparks", 'PARTICLE_SYSTEM')
        ps = emitter.particle_systems[0]
        setts = ps.settings
        setts.count = int(spark_cnt)
        setts.frame_start = 7.0
        setts.frame_end = 9.0
        setts.lifetime = 45.0
        setts.lifetime_random = 0.5
        setts.normal_factor = float(spark_spd)
        setts.factor_random = 8.0
        setts.effector_weights.gravity = 0.45
        setts.render_type = 'OBJECT'
        setts.instance_object = spark_instance
        setts.particle_size = 0.8
        setts.size_random = 0.75
        fx_objs.append(emitter)

    # 3. Explodeモディファイアによる瞬間粉砕メッシュ (Micro-Debris Blaster)
    if enable_explode:
        print("💥 Creating Explode Modifier micro-shatter layer...")
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.45, location=hit_pos)
        shatter_ball = bpy.context.active_object
        shatter_ball.name = "Explode_Micro_Debris"
        shatter_ball.data.materials.append(spark_mat)

        # パーティクルシステム追加
        bpy.ops.object.particle_system_add()
        shatter_ps = shatter_ball.particle_systems[0]
        s_set = shatter_ps.settings
        s_set.count = int(EXPLODE_PIECE_COUNT)
        s_set.frame_start = 7.0
        s_set.frame_end = 8.0
        s_set.lifetime = 60.0
        s_set.normal_factor = 14.0
        s_set.factor_random = 6.0
        s_set.effector_weights.gravity = 0.60
        s_set.render_type = 'NONE'

        # Explodeモディファイア追加 (衝突前は非表示、衝突後に爆散)
        exp_mod = shatter_ball.modifiers.new("Explode", 'EXPLODE')
        exp_mod.use_edge_cut = True
        exp_mod.show_unborn = False
        exp_mod.show_dead = True
        fx_objs.append(shatter_ball)

    # 4. Mantaflow本格火炎・煙ボリューム (トグルON時のみ)
    if enable_mantaflow:
        print("🔥 Creating Mantaflow Gas Fire & Smoke simulation...")
        # フローオブジェクト (火炎・煙発生源)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=hit_pos)
        flow_obj = bpy.context.active_object
        flow_obj.name = "Explosion_FireSmoke_Flow"
        flow_mod = flow_obj.modifiers.new("Fluid", 'FLUID')
        flow_mod.fluid_type = 'FLOW'
        flow_mod.flow_settings.flow_type = 'BOTH'
        flow_mod.flow_settings.flow_behavior = 'INFLOW'
        flow_mod.flow_settings.fuel_amount = 2.0
        # Frame 7〜11のみ燃料噴出
        flow_mod.flow_settings.use_inflow = True
        flow_obj.keyframe_insert(data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=1)
        flow_obj.keyframe_insert(data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=7)
        flow_mod.flow_settings.use_inflow = False
        flow_obj.keyframe_insert(data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=12)
        fx_objs.append(flow_obj)

        # ドメインオブジェクト
        hx, hy, hz = hit_pos
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, hy, hz + 0.8))
        domain = bpy.context.active_object
        domain.name = "Explosion_FireSmoke_Domain"
        domain.scale = (5.0, 5.0, 4.5)
        bpy.ops.object.transform_apply(scale=True)
        domain_mod = domain.modifiers.new("Fluid", 'FLUID')
        domain_mod.fluid_type = 'DOMAIN'
        domain_mod.domain_settings.domain_type = 'GAS'
        domain_mod.domain_settings.resolution_max = 64
        domain.data.materials.append(fire_smoke_mat)
        fx_objs.append(domain)

    return fx_objs

# ------------------------------------------------------------------------------
# 🎬 6. 物理ベイク処理 & スローモーション設定
# ------------------------------------------------------------------------------
def bake_simulation_to_keyframes(shards, ball=None, total_frames=ANIM_TOTAL_FRAMES, time_scale=TIME_SCALE):
    scene = bpy.context.scene
    print(f"🎬 Baking rigid body simulation (Frames 1 to {total_frames}, TimeScale={time_scale})...")

    if scene.rigidbody_world:
        scene.rigidbody_world.point_cache.frame_start = 1
        scene.rigidbody_world.point_cache.frame_end = total_frames
        scene.rigidbody_world.time_scale = float(time_scale)

    valid_shards = [s for s in shards if s.name in bpy.data.objects]
    all_target_objs = list(valid_shards)

    # 1. 物理シミュレーションを先頭から最後まで進めながら各オブジェクトのワールド行列を記録
    baked_matrices = {s: [] for s in all_target_objs}
    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        for s in all_target_objs:
            eval_s = s.evaluated_get(dg)
            baked_matrices[s].append((f, eval_s.matrix_world.copy()))

    # 2. 剛体物理シミュレーションを無効化
    for s in all_target_objs:
        if s.rigid_body:
            s.rigid_body.enabled = False
    if scene.rigidbody_world:
        scene.rigidbody_world.enabled = False

    # 3. 記録した行列を純粋なLocRotキーフレームとして適用
    for s in all_target_objs:
        if s.animation_data:
            s.animation_data_clear()
        for f, mat in baked_matrices[s]:
            loc, rot, sca = mat.decompose()
            s.location = loc
            s.rotation_euler = rot.to_euler()
            s.keyframe_insert(data_path='location', frame=f)
            s.keyframe_insert(data_path='rotation_euler', frame=f)

    # 3. 不要になったフォースフィールド・コンストレイントを削除
    for o in list(bpy.data.objects):
        if o.rigid_body_constraint or "Shockwave" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    # 4. NLA競合防止＆初期フレームへ復帰
    for obj in all_target_objs + ([ball] if ball else []):
        if obj.animation_data:
            obj.animation_data.use_nla = False
            for track in list(obj.animation_data.nla_tracks):
                obj.animation_data.nla_tracks.remove(track)

    scene.frame_set(1)
    scene.frame_current = 1
    print("✅ Successfully baked simulation to clean keyframe actions!")

# ------------------------------------------------------------------------------
# ⚡ 7. 【高速リシミュレーション】形状キープ物理のみ再計算
# ------------------------------------------------------------------------------
def resimulate_physics_only(custom_params=None):
    scene = bpy.context.scene
    shards = [o for o in scene.objects if 'cell' in o.name.lower()]
    if not shards:
        print("⚠️ No existing fracture shards found. Running full generation...")
        main()
        return

    print("\n⚡ ========================================================")
    print(f"⚡ QUICK RE-SIMULATE: Keeping {len(shards)} shards, re-baking physics only!")
    print("⚡ ========================================================")

    for o in list(scene.objects):
        if any(k in o.name.lower() for k in ['cannonball', 'meteor', 'shockwave', 'spark', 'explode_micro', 'firesmoke']):
            bpy.data.objects.remove(o, do_unlink=True)

    scene.frame_set(1)
    for s in shards:
        if s.animation_data:
            s.animation_data_clear()

    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    scene.rigidbody_world.enabled = True
    scene.rigidbody_world.point_cache.frame_start = 1
    scene.rigidbody_world.point_cache.frame_end = ANIM_TOTAL_FRAMES

    for s in shards:
        bpy.context.view_layer.objects.active = s
        if not s.rigid_body:
            bpy.ops.rigidbody.object_add(type='ACTIVE')
        s.rigid_body.enabled = True
        s.rigid_body.collision_shape = 'BOX' if 'brick' in s.name else 'CONVEX_HULL'
        s.rigid_body.mass = 6.0 if 'brick' in s.name else 4.0
        s.rigid_body.friction = 0.85
        s.rigid_body.restitution = 0.15
        s.rigid_body.linear_damping = 0.02
        s.rigid_body.angular_damping = 0.02

        s.rigid_body.kinematic = True
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=7)
        s.rigid_body.kinematic = False
        s.keyframe_insert(data_path='rigid_body.kinematic', frame=8)

    brick_shards = [s for s in shards if 'brick' in s.name.lower()]
    if brick_shards:
        # レンガ壁の場合は位置ベースで近接レンガをペアリングしてモルタルコンストレイントを生成
        c_count = 0
        for i in range(len(brick_shards)):
            for j in range(i + 1, len(brick_shards)):
                b1 = brick_shards[i]
                b2 = brick_shards[j]
                dist = (b1.location - b2.location).length
                # 隣接レンガ距離 (横0.43m以内 または 縦0.20m以内)
                if dist < 0.45:
                    empty = bpy.data.objects.new(f"Mortar_Resim_{c_count}", None)
                    bpy.context.scene.collection.objects.link(empty)
                    empty.location = (b1.location + b2.location) * 0.5
                    bpy.context.view_layer.objects.active = empty
                    bpy.ops.rigidbody.constraint_add(type='FIXED')
                    empty.rigid_body_constraint.object1 = b1
                    empty.rigid_body_constraint.object2 = b2
                    empty.rigid_body_constraint.use_breaking = True
                    empty.rigid_body_constraint.breaking_threshold = MORTAR_THRESHOLD
                    c_count += 1
    else:
        # その他の形状 (ROCK, WALL, BUILDING, PILLAR, GROUND)
        bpy.ops.object.select_all(action='DESELECT')
        for s in shards:
            s.select_set(True)
        bpy.context.view_layer.objects.active = shards[0]
        try:
            bpy.ops.rigidbody.connect(con_type='FIXED', connection_pattern='CHAIN_DISTANCE')
            for o in bpy.data.objects:
                if o.rigid_body_constraint:
                    o.rigid_body_constraint.use_breaking = True
                    o.rigid_body_constraint.breaking_threshold = 4.0
        except Exception as e:
            print("⚠️ resimulate connect warning:", e)

    ground_obj = bpy.data.objects.get("Scene_Ground")
    if not ground_obj:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.05))
        ground_obj = bpy.context.active_object
        ground_obj.name = "Scene_Ground"
        ground_obj.scale = (9.0, 9.0, 0.10)
        bpy.ops.object.transform_apply(scale=True)

    cannon_mat = create_cannonball_material()
    hit_center = (0, 0, 1.20)

    seed_val = random.randint(1, 999999)
    ball = setup_collider_and_impact(ground_obj, cannon_mat, "CUSTOM", hit_center, seed_val, custom_params)

    spark_mat = create_spark_material()
    fire_smoke_mat = create_fire_smoke_material()
    setup_explosion_effects(hit_center, spark_mat, fire_smoke_mat, custom_params)

    t_scale = custom_params.get('time_scale', TIME_SCALE) if custom_params else TIME_SCALE
    bake_simulation_to_keyframes(shards, ball=ball, total_frames=ANIM_TOTAL_FRAMES, time_scale=t_scale)

    select_export_objects()
    scene.frame_set(1)
    scene.frame_current = 1

    blend_path = r"e:\BlenderPreFix\destruction_pillar_current.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"💾 Updated state to: {blend_path}")
    print("🎉 Fast re-simulation finished! Press Shift+Space to play!")

# ------------------------------------------------------------------------------
# 💡 8. スタジオ照明
# ------------------------------------------------------------------------------
def setup_lighting(shape_type):
    bpy.ops.object.light_add(type='SUN', location=(4.0, -5.0, 6.0))
    sun = bpy.context.active_object
    sun.name = "KeySun"
    sun.data.energy = 4.5
    sun.data.color = (1.0, 0.96, 0.90)

    bpy.ops.object.light_add(type='POINT', location=(-3.5, 3.0, 4.0))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 220.0
    fill.data.color = (0.75, 0.85, 1.0)

# ------------------------------------------------------------------------------
# 📦 9. エクスポート処理 & NパネルUI
# ------------------------------------------------------------------------------
def select_export_objects():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

def export_ue_fbx(fbx_path):
    select_export_objects()
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        object_types={'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        bake_anim=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        embed_textures=False,
        path_mode='RELATIVE'
    )
    print(f"✅ Exported UE5 FBX: {fbx_path}")

def export_catalog_glb(glb_path):
    select_export_objects()
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_frame_range=True,
        export_frame_step=1,
        export_force_sampling=True
    )
    print(f"✅ Exported GLB: {glb_path}")

# --- Nパネル用 PropertyGroup ---
class DestructionControlProps(bpy.types.PropertyGroup):
    impact_angle_h: bpy.props.FloatProperty(
        name="水平進入角",
        description="砲弾の水平突入角度 (-60°〜+60°)",
        default=0.0,
        min=-60.0,
        max=60.0
    )
    impact_angle_v: bpy.props.FloatProperty(
        name="垂直進入角",
        description="砲弾の垂直撃ち下ろし角度 (0°〜35°)",
        default=6.0,
        min=0.0,
        max=35.0
    )
    ball_size: bpy.props.FloatProperty(
        name="球のサイズ",
        description="突入する球体の半径 (m)",
        default=0.54,
        min=0.25,
        max=1.20
    )
    shock_power: bpy.props.FloatProperty(
        name="衝撃波の強さ",
        description="直撃時の爆散衝撃波の強さ",
        default=5500.0,
        min=1000.0,
        max=15000.0
    )
    time_scale: bpy.props.FloatProperty(
        name="タイムスケール(スロー)",
        description="シミュレーション速度 (1.0=等速, 0.4=映画的スロー, 0.1=スーパースロー)",
        default=0.50,
        min=0.10,
        max=1.50
    )
    target_shape: bpy.props.EnumProperty(
        name="破壊ターゲット",
        description="再生成する破壊対象の形状タイプ",
        items=[
            ('0', "🎲 RANDOM (ランダム)", "毎回ランダムに形状を選定"),
            ('6', "🧱 BRICK_WALL (千鳥積みレンガ壁)", "モルタル接着と漆喰デブリ付き本格レンガ壁"),
            ('4', "🏛️ PILLAR (古代装飾石柱)", "円柱状の古代石柱"),
            ('1', "🪨 ROCK (ゴツゴツ自然巨岩)", "岩肌の巨岩"),
            ('2', "🧗 WALL (荒削り断崖岩壁)", "垂直な岩壁"),
            ('3', "🏢 BUILDING (多層タワー連鎖崩壊)", "多層構造の建築物"),
            ('5', "🌋 GROUND (地割れ陥没地面)", "地面の陥没破砕"),
        ],
        default='6'
    )
    enable_sparks: bpy.props.BoolProperty(
        name="火花パーティクル",
        description="衝突瞬間に飛び散る火花・火の粉パーティクル",
        default=True
    )
    spark_speed: bpy.props.FloatProperty(
        name="火花初速",
        description="火花パーティクルの飛び散るスピード",
        default=18.0,
        min=5.0,
        max=40.0
    )
    enable_explode: bpy.props.BoolProperty(
        name="瞬間粉砕スプラッター",
        description="Explodeモディファイアによる微細破片の高速爆散",
        default=True
    )
    enable_mantaflow: bpy.props.BoolProperty(
        name="火炎・煙ボリューム(流体)",
        description="Mantaflowによる本格ガス火炎・黒煙シミュレーション (Cycles/Eevee動画用)",
        default=False
    )

class OBJECT_OT_QuickResimulatePhysics(bpy.types.Operator):
    bl_idname = "object.quick_resimulate_physics"
    bl_label = "⚡ 形状キープで物理だけ再計算"
    bl_description = "現在の破片形状を保ったまま、設定した角度・サイズ・威力・スローで物理のみを瞬時再計算します"

    def execute(self, context):
        props = context.scene.destruction_props
        p = {
            'impact_angle_h': props.impact_angle_h,
            'impact_angle_v': props.impact_angle_v,
            'ball_size': props.ball_size,
            'shock_power': props.shock_power,
            'time_scale': props.time_scale,
            'enable_sparks': props.enable_sparks,
            'spark_speed': props.spark_speed,
            'enable_explode': props.enable_explode,
            'enable_mantaflow': props.enable_mantaflow,
        }
        resimulate_physics_only(custom_params=p)
        self.report({'INFO'}, "物理リベイク完了！Shift+Spaceで再生してください")
        return {'FINISHED'}

class OBJECT_OT_GenerateRandomDestruction(bpy.types.Operator):
    bl_idname = "object.generate_random_destruction"
    bl_label = "🎲 新規再生成 (Alt + P)"
    bl_description = "選択した形状・新しいシード値で破壊シーンを一から再生成します"

    def execute(self, context):
        props = context.scene.destruction_props
        shape_str = getattr(props, 'target_shape', '0')
        shape_code = int(shape_str) if str(shape_str).isdigit() else 0
        main(shape=shape_code, seed_input=None)
        self.report({'INFO'}, f"新しい破壊シーンを生成しました！(Shift+Spaceで再生)")
        return {'FINISHED'}

class OBJECT_OT_ExportDestructionUE5FBX(bpy.types.Operator):
    bl_idname = "object.export_destruction_ue_fbx"
    bl_label = "🎮 Export UE5 Destruction FBX"
    bl_description = "現在の破壊アニメーションをUE5最適化FBXとして出力します"

    def execute(self, context):
        assets_dir = r"e:\BlenderPreFix\catalog\assets"
        fbx_path = os.path.join(assets_dir, "destruction_scene_ue.fbx")
        export_ue_fbx(fbx_path)
        self.report({'INFO'}, f"UE5 FBX 出力完了: {fbx_path}")
        return {'FINISHED'}

class VIEW3D_PT_DestructionToolsPanel(bpy.types.Panel):
    bl_label = "💥 破壊シミュレーション ツール"
    bl_idname = "VIEW3D_PT_destruction_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Destruction Tools"

    def draw(self, context):
        layout = self.layout
        props = context.scene.destruction_props

        box2 = layout.box()
        box2.label(text="🎲 形状の新規生成", icon='PHYSICS')
        if hasattr(props, "target_shape"):
            box2.prop(props, "target_shape", text="")
        box2.operator("object.generate_random_destruction", icon='FILE_REFRESH')

        box = layout.box()
        box.label(text="⚡ リアルタイム物理調整 (形状キープ)", icon='FORCE_DRAG')
        col = box.column(align=True)
        col.prop(props, "impact_angle_h", slider=True)
        col.prop(props, "impact_angle_v", slider=True)
        col.prop(props, "ball_size", slider=True)
        col.prop(props, "shock_power", slider=True)
        col.prop(props, "time_scale", slider=True)

        box_fx = layout.box()
        box_fx.label(text="🔥 爆発・火花・破片エフェクト", icon='PARTICLES')
        col_fx = box_fx.column(align=True)
        col_fx.prop(props, "enable_sparks")
        if props.enable_sparks:
            col_fx.prop(props, "spark_speed", slider=True)
        col_fx.prop(props, "enable_explode")
        col_fx.prop(props, "enable_mantaflow")

        box.operator("object.quick_resimulate_physics", icon='PLAY')

        box3 = layout.box()
        box3.label(text="ゲームエンジン出力", icon='EXPORT')
        box3.operator("object.export_destruction_ue_fbx", icon='FILE_3D')

classes = (
    DestructionControlProps,
    OBJECT_OT_QuickResimulatePhysics,
    OBJECT_OT_GenerateRandomDestruction,
    OBJECT_OT_ExportDestructionUE5FBX,
    VIEW3D_PT_DestructionToolsPanel,
)

def register_ui():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # 既に登録済みの場合はスキップ
        except Exception as e:
            print(f"Warning registering {cls}: {e}")
    if not hasattr(bpy.types.Scene, "destruction_props") or not hasattr(bpy.context.scene.destruction_props, "target_shape"):
        try:
            del bpy.types.Scene.destruction_props
        except Exception:
            pass
        bpy.types.Scene.destruction_props = bpy.props.PointerProperty(type=DestructionControlProps)

# 形状番号マッピング
SHAPE_MAP = {
    0: "RANDOM",
    1: "ROCK",
    2: "WALL",
    3: "BUILDING",
    4: "PILLAR",
    5: "GROUND",
    6: "BRICK_WALL",
}

def resolve_shape_name(shape_arg):
    if isinstance(shape_arg, int):
        return SHAPE_MAP.get(shape_arg, "RANDOM")
    if isinstance(shape_arg, str):
        if shape_arg.isdigit():
            return SHAPE_MAP.get(int(shape_arg), "RANDOM")
        s = shape_arg.upper()
        if s in SHAPE_MAP.values():
            return s
    return "RANDOM"

# ------------------------------------------------------------------------------
# 🚀 10. メインエントリーポイント
# ------------------------------------------------------------------------------
def main(shape=TARGET_SHAPE, seed_input=SEED):
    if KEEP_SHAPE_MODE:
        resimulate_physics_only()
        return

    seed_val = random.randint(1, 999999) if seed_input is None else int(seed_input)
    random.seed(seed_val)

    shape_name = resolve_shape_name(shape)
    available_shapes = ["BRICK_WALL", "ROCK", "WALL", "BUILDING", "PILLAR", "GROUND"]
    if shape_name == "RANDOM" or shape_name not in available_shapes:
        chosen_shape = random.choice(available_shapes)
    else:
        chosen_shape = shape_name

    print(f"\n==================================================")
    print(f"💥 GENERATING DESTRUCTION SCENE: {chosen_shape} (Seed: {seed_val})")
    print(f"==================================================")

    clear_scene()

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = ANIM_TOTAL_FRAMES
    scene.render.fps = FPS

    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    scene.rigidbody_world.point_cache.frame_start = 1
    scene.rigidbody_world.point_cache.frame_end = ANIM_TOTAL_FRAMES
    scene.rigidbody_world.time_scale = TIME_SCALE

    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    os.makedirs(assets_dir, exist_ok=True)

    print("🎨 Step 1: Creating materials...")
    outer_mat  = create_outer_stone_material()
    inner_mat  = create_inner_chipped_material()
    cannon_mat = create_cannonball_material()
    brick_mat  = create_brick_material()
    mortar_mat = create_mortar_material()

    print(f"🏛️ Step 2: Building {chosen_shape} structure...")
    if chosen_shape == "BRICK_WALL":
        shards, ground_obj, hit_pos = build_brick_wall_structure(brick_mat, mortar_mat, seed_val)
    elif chosen_shape == "ROCK":
        solid_obj, ground_obj, hit_pos = build_craggy_rock_shape(outer_mat, inner_mat, seed_val)
        shards = fracture_and_setup_physics(solid_obj, chosen_shape, seed_val)
    elif chosen_shape == "WALL":
        solid_obj, ground_obj, hit_pos = build_craggy_wall_shape(outer_mat, inner_mat, seed_val)
        shards = fracture_and_setup_physics(solid_obj, chosen_shape, seed_val)
    elif chosen_shape == "BUILDING":
        solid_obj, ground_obj, hit_pos = build_building_shape(outer_mat, inner_mat)
        shards = fracture_and_setup_physics(solid_obj, chosen_shape, seed_val)
    elif chosen_shape == "PILLAR":
        solid_obj, ground_obj, hit_pos = build_pillar_shape(outer_mat, inner_mat)
        shards = fracture_and_setup_physics(solid_obj, chosen_shape, seed_val)
    else: # GROUND
        solid_obj, ground_obj, hit_pos = build_ground_shape(outer_mat, inner_mat)
        shards = fracture_and_setup_physics(solid_obj, chosen_shape, seed_val)

    print("🚀 Step 3: Setting up collider & angled trajectory...")
    ball = setup_collider_and_impact(ground_obj, cannon_mat, chosen_shape, hit_pos, seed_val)

    print("💥 Step 3.5: Adding explosion sparks & micro-shatter effects...")
    spark_mat = create_spark_material()
    fire_smoke_mat = create_fire_smoke_material()
    setup_explosion_effects(hit_pos, spark_mat, fire_smoke_mat)

    print("🎬 Step 4: Baking physics to keyframes...")
    bake_simulation_to_keyframes(shards, ball=ball, total_frames=ANIM_TOTAL_FRAMES, time_scale=TIME_SCALE)

    setup_lighting(chosen_shape)
    register_ui()

    if EXPORT_UE_FBX:
        fbx_path = os.path.join(assets_dir, "destruction_scene_ue.fbx")
        export_ue_fbx(fbx_path)

    if EXPORT_CATALOG_GLB:
        glb_path = os.path.join(assets_dir, "destruction_scene.glb")
        export_catalog_glb(glb_path)

    select_export_objects()
    scene.frame_set(1)
    scene.frame_current = 1

    blend_path = r"e:\BlenderPreFix\destruction_pillar_current.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"💾 Saved state to: {blend_path}")

    print(f"\n🎉 Destruction scene [{chosen_shape}] (Seed: {seed_val}, Shards: {len(shards)}) generated successfully!")
    print("💡 Press Shift+Space (or Space) in Blender to watch the destruction!")

if __name__ == "__main__":
    main()
