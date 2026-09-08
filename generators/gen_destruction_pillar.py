"""
================================================================================
💥 GEN_DESTRUCTION_PILLAR.PY - REALISTIC DESTRUCTION EFFECTS GENERATOR
================================================================================
【機能概要】
1. 古代装飾石柱のプロシージャル生成 (Doric Column with Fluted Shaft & Pedestal)
2. Cell Fracture による衝撃点集中ボロノイ破砕 (35破片・内外マテリアル分離)
3. 剛体物理 ＆ Breakable 接着コンストレイント (Fixed + Breakable Chain)
   - 衝撃を受けるまでは完全な1本の柱として自立
   - 砲弾（Heavy Cannonball）の高速直撃により衝撃点から爆散・崩落
4. 剛体シミュレーションのキーフレーム全自動ベイク (depsgraph evaluation方式)
   - ゲームエンジン（UE5）およびWebカタログで計算負荷ゼロ・100%再現
5. Unreal Engine 5 最適化 FBX 一発出力 & 3D Viewport Nパネルボタン常駐
================================================================================
"""

import bpy
import bmesh
import math
import os
import sys
import addon_utils

def ensure_cell_fracture_addon():
    """Blender 3.6 から 4.x / 5.2 まですべてのバージョンで Cell Fracture を確実に利用可能にする"""
    if hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects'):
        return True

    # 1. 通常の addon_utils による有効化試行
    try:
        addon_utils.enable("object_fracture_cell")
    except Exception:
        pass
    if hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects'):
        return True

    # 2. プロジェクト内 addons/ またはローカルパスからの直接インポート＆register
    this_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"e:\BlenderPreFix\generators"
    proj_root = os.path.dirname(this_dir)
    candidate_paths = [
        os.path.join(proj_root, "addons"),
        r"e:\BlenderPreFix\addons",
        os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons"),
        r"C:\Program Files\Blender Foundation\Blender 3.6\3.6\scripts\addons",
    ]
    for p in candidate_paths:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)

    try:
        import object_fracture_cell
        object_fracture_cell.register()
        print("✅ Successfully registered object_fracture_cell via fallback!")
        return True
    except Exception as e:
        print("⚠️ Direct registration failed:", e)

    return hasattr(bpy.types, 'OBJECT_OT_add_fracture_cell_objects')

# ==============================================================================
# 🎛️ 実行制御スイッチ (Execution Switches)
# ==============================================================================
EXPORT_UE_FBX       = True   # 🎮 Unreal Engine 5 最適化 FBX を一発出力 (destruction_pillar_ue.fbx)
EXPORT_CATALOG_GLB  = True   # 🌐 Webカタログ用 GLB を出力 (destruction_pillar.glb)
RENDER_CUTS         = True   # 📸 Cycles シネマティック4カット画像をレンダリング
ANIM_TOTAL_FRAMES   = 90     # アニメーション総フレーム (3.0秒 / 30fps)
FPS                 = 30

# ------------------------------------------------------------------------------
# 🧹 安全なシーンクリーンアップ
# ------------------------------------------------------------------------------
def clear_scene():
    if bpy.context.object and hasattr(bpy.context.object, 'mode') and bpy.context.object.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)
    for b in list(bpy.data.actions):
        bpy.data.actions.remove(b)

def set_active(obj):
    if obj is None:
        return
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    if hasattr(bpy.context, 'view_layer') and hasattr(bpy.context.view_layer, 'objects'):
        bpy.context.view_layer.objects.active = obj

# ------------------------------------------------------------------------------
# 🎨 1. PBR マテリアル生成（外側滑らか石材・内側粗い破断面・砲弾鉄）
# ------------------------------------------------------------------------------
def create_outer_stone_material():
    mat = bpy.data.materials.new(name="M_Ancient_Stone_Outer")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.72
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 4.5
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.80, 0.76, 0.70, 1.0) # 明るいアイボリー石
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.55, 0.50, 0.44, 1.0) # 風化した褐色
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.05
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_inner_chipped_material():
    mat = bpy.data.materials.new(name="M_Rough_Chipped_Inner")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new('ShaderNodeTexCoord')
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 35.0
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 10.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.65
    links.new(voronoi.outputs['Distance'], mix.inputs[2])
    links.new(noise.outputs['Fac'], mix.inputs[3])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.38, 0.35, 0.31, 1.0) # 暗い砕石芯
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.68, 0.64, 0.58, 1.0) # 削れた粉塵色
    links.new(mix.outputs['Result'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.70
    bump.inputs['Distance'].default_value = 0.12
    links.new(mix.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_cannonball_material():
    mat = bpy.data.materials.new(name="M_Cast_Iron_Cannonball")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.18
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# ------------------------------------------------------------------------------
# 🏛️ 2. 古代石柱のプロシージャルモデリング
# ------------------------------------------------------------------------------
def build_fluted_shaft(radius=0.36, height=2.4, flutes=16, z_base=0.4):
    bm = bmesh.new()
    segments = flutes * 4
    z_segs = 12

    for zi in range(z_segs + 1):
        z = z_base + (height / z_segs) * zi
        for si in range(segments):
            angle = (2.0 * math.pi / segments) * si
            flute_wave = math.sin(si * flutes * 2.0 * math.pi / segments)
            r = radius - 0.015 * max(0.0, flute_wave)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for zi in range(z_segs):
        for si in range(segments):
            s_next = (si + 1) % segments
            v1 = bm.verts[zi * segments + si]
            v2 = bm.verts[zi * segments + s_next]
            v3 = bm.verts[(zi + 1) * segments + s_next]
            v4 = bm.verts[(zi + 1) * segments + si]
            bm.faces.new([v1, v2, v3, v4])

    bot_verts = [bm.verts[si] for si in range(segments)]
    top_verts = [bm.verts[z_segs * segments + si] for si in range(segments)]
    bm.faces.new(reversed(bot_verts))
    bm.faces.new(top_verts)

    mesh = bpy.data.meshes.new("Pillar_Shaft_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Pillar_Shaft", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_decorative_pillar(outer_mat, inner_mat):
    shaft = build_fluted_shaft(radius=0.36, height=2.4, flutes=16, z_base=0.35)
    shaft.data.materials.append(outer_mat)
    shaft.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.85))
    capital = bpy.context.active_object
    capital.name = "Pillar_Capital"
    capital.scale = (0.92, 0.92, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    capital.data.materials.append(outer_mat)
    capital.data.materials.append(inner_mat)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.15, location=(0, 0, 0.28))
    base = bpy.context.active_object
    base.name = "Pillar_Base"
    bpy.ops.object.transform_apply(scale=True)
    base.data.materials.append(outer_mat)
    base.data.materials.append(inner_mat)

    set_active(shaft)
    capital.select_set(True)
    base.select_set(True)
    bpy.ops.object.join()
    combined_pillar = shaft
    combined_pillar.name = "Stone_Pillar_Solid"

    # 地面の石畳台座
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.10))
    pedestal = bpy.context.active_object
    pedestal.name = "Pillar_Pedestal"
    pedestal.scale = (6.5, 6.5, 0.20)
    bpy.ops.object.transform_apply(scale=True)
    pedestal.data.materials.append(outer_mat)

    return combined_pillar, pedestal

# ------------------------------------------------------------------------------
# 💥 3. Cell Fracture 破砕 & Breakable コンストレイント構築
# ------------------------------------------------------------------------------
def fracture_pillar_and_setup_physics(pillar_obj, outer_mat, inner_mat):
    ensure_cell_fracture_addon()
    set_active(pillar_obj)

    print("🔨 Fracturing pillar with Cell Fracture...")
    bpy.ops.object.add_fracture_cell_objects(
        source_limit=45,
        source_noise=0.40,
        margin=0.0,
        material_index=1,
        use_smooth_faces=False,
        use_sharp_edges=True,
        use_remove_original=True
    )

    shards = [o for o in bpy.data.objects if 'cell' in o.name.lower()]
    print(f"✅ Generated {len(shards)} fracture shards!")

    # 元の柱を確実に完全消去（重なって残るのを防止）
    if pillar_obj.name in bpy.data.objects:
        bpy.data.objects.remove(pillar_obj, do_unlink=True)

    # 各破片の重心に原点をリセット
    bpy.ops.object.select_all(action='DESELECT')
    for s in shards:
        s.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    # マテリアル保証
    for s in shards:
        if len(s.data.materials) == 0:
            s.data.materials.append(outer_mat)
        if len(s.data.materials) == 1:
            s.data.materials.append(inner_mat)

    # 最下部（Z < 0.35）は地面固定アンカー(Passive)、それ以上はActive動的剛体
    anchor_count = 0
    active_count = 0
    for s in shards:
        bpy.context.view_layer.objects.active = s
        z = s.matrix_world.translation.z
        if z < 0.35:
            anchor_count += 1
            if not s.rigid_body:
                bpy.ops.rigidbody.object_add(type='PASSIVE')
            s.rigid_body.collision_shape = 'CONVEX_HULL'
            s.rigid_body.friction = 0.90
        else:
            active_count += 1
            if not s.rigid_body:
                bpy.ops.rigidbody.object_add(type='ACTIVE')
            s.rigid_body.collision_shape = 'CONVEX_HULL'
            s.rigid_body.mass = 10.0
            s.rigid_body.friction = 0.85
            s.rigid_body.restitution = 0.15

    print(f"⚓ Anchor base shards (Passive): {anchor_count}, 💥 Active shards: {active_count}")

    # 全破片を選択してChain Connect
    bpy.ops.object.select_all(action='DESELECT')
    for s in shards:
        s.select_set(True)
    bpy.context.view_layer.objects.active = shards[0]

    print("🔗 Connecting shards with breakable constraints...")
    bpy.ops.rigidbody.connect(con_type='FIXED', connection_pattern='CHAIN_DISTANCE')

    constraint_count = 0
    for o in bpy.data.objects:
        if o.rigid_body_constraint:
            constraint_count += 1
            o.rigid_body_constraint.use_breaking = True
            o.rigid_body_constraint.breaking_threshold = 25.0 # 確実な連鎖爆散感度

    print(f"✅ Created {constraint_count} breakable glue constraints (Threshold: 25.0)!")
    return shards

# ------------------------------------------------------------------------------
# 🚀 4. 砲弾（コライダー）と床のセットアップ
# ------------------------------------------------------------------------------
def setup_cannonball_and_ground(pedestal_obj, cannon_mat):
    set_active(pedestal_obj)
    if not pedestal_obj.rigid_body:
        bpy.ops.rigidbody.object_add(type='PASSIVE')
    pedestal_obj.rigid_body.friction = 0.90
    pedestal_obj.rigid_body.restitution = 0.15

    # 砲弾 (大口径重砲弾 半径0.40m)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=(0, -3.5, 1.55))
    ball = bpy.context.active_object
    ball.name = "Heavy_Cannonball"
    bpy.ops.object.shade_smooth()
    ball.data.materials.append(cannon_mat)

    set_active(ball)
    if not ball.rigid_body:
        bpy.ops.rigidbody.object_add(type='PASSIVE')
    ball.rigid_body.collision_shape = 'SPHERE'
    ball.rigid_body.kinematic = True

    # 砲弾の軌道キーフレーム設定
    ball.location = (0, -3.5, 1.55)
    ball.keyframe_insert(data_path='location', frame=1)

    ball.location = (0, -0.30, 1.55)
    ball.keyframe_insert(data_path='location', frame=7)

    ball.location = (0, 0.40, 1.55)
    ball.keyframe_insert(data_path='location', frame=10)

    ball.location = (0, 3.5, 1.45)
    ball.keyframe_insert(data_path='location', frame=18)

    ball.location = (0, 9.0, 1.00)
    ball.keyframe_insert(data_path='location', frame=70)

    return ball

# ------------------------------------------------------------------------------
# 🎬 5. 物理シミュレーションのキーフレーム全自動ベイク
# ------------------------------------------------------------------------------
def bake_simulation_to_keyframes(shards, total_frames=90):
    scene = bpy.context.scene
    print(f"🎬 Baking rigid body simulation (Frames 1 to {total_frames})...")

    transforms = {s: [] for s in shards}
    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        for s in shards:
            transforms[s].append((f, s.matrix_world.copy()))

    for s in shards:
        if s.rigid_body:
            s.rigid_body.enabled = False
        for f, mat in transforms[s]:
            loc, rot, sca = mat.decompose()
            s.location = loc
            s.rotation_euler = rot.to_euler()
            s.keyframe_insert(data_path='location', frame=f)
            s.keyframe_insert(data_path='rotation_euler', frame=f)

    scene.frame_set(1)
    print("✅ Successfully baked simulation to keyframes for zero-runtime cost!")
    for f in [1, 7, 10, 15, 20, 25, 30]:
        scene.frame_set(f)
        z_high = [s.location.z for s in shards if s.location.z > 2.0]
        print(f"  [Direct Bake Check] Frame {f:02d}: Shards Z>2.0: {len(z_high)}/{len(shards)}")
    scene.frame_set(1)

# ------------------------------------------------------------------------------
# 💡 6. スタジオ照明とレンダリングカメラ
# ------------------------------------------------------------------------------
def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(4.0, -5.0, 6.0))
    sun = bpy.context.active_object
    sun.name = "KeySun"
    sun.data.energy = 5.0
    sun.data.color = (1.0, 0.95, 0.88)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))

    bpy.ops.object.light_add(type='AREA', location=(-3.5, 2.5, 4.0))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 90.0
    fill.data.color = (0.78, 0.88, 1.0)
    fill.data.size = 4.0

    bpy.ops.object.light_add(type='POINT', location=(0, -1.2, 0.8))
    rim = bpy.context.active_object
    rim.name = "GroundGlow"
    rim.data.energy = 50.0
    rim.data.color = (1.0, 0.90, 0.80)

def render_cut_target(filepath, cam_pos, target_pos=(0, 0, 1.2), lens=42, frame=22, samples=28):
    scene = bpy.context.scene
    scene.frame_set(frame)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_pos)
    target = bpy.context.active_object
    target.name = "CamTarget"

    bpy.ops.object.camera_add(location=cam_pos)
    cam = bpy.context.active_object
    cam.name = "RenderCam"
    cam.data.lens = lens
    scene.camera = cam

    tt = cam.constraints.new(type='TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.render.filepath = filepath
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(target, do_unlink=True)
    print(f"Rendered cut at Frame {frame} to: {filepath}")

# ------------------------------------------------------------------------------
# 📦 7. エクスポート処理 & UI連携
# ------------------------------------------------------------------------------
def select_export_objects():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and not obj.name.startswith("OrthoBake"):
            obj.select_set(True)

def export_ue_fbx(fbx_path):
    print(f"🎮 Exporting UE5-optimized FBX to: {fbx_path}...")
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
        bake_anim_use_all_actions=False,
        embed_textures=False,
        path_mode='RELATIVE'
    )
    print(f"✅ Successfully exported UE5-optimized FBX: {fbx_path}")

def export_catalog_glb(glb_path):
    print(f"🌐 Exporting Web Catalog GLB to: {glb_path}...")
    select_export_objects()
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_animations=True,
        export_frame_range=True,
        export_frame_step=1,
        export_force_sampling=True
    )
    print(f"✅ Successfully exported GLB: {glb_path}")

class OBJECT_OT_ExportDestructionUE5FBX(bpy.types.Operator):
    bl_idname = "object.export_destruction_ue_fbx"
    bl_label = "🎮 Export UE5 Destruction FBX"
    bl_description = "現在の破壊アニメーションをUE5最適化FBXとして一発エクスポートします"

    def execute(self, context):
        assets_dir = r"e:\BlenderPreFix\catalog\assets"
        fbx_path = os.path.join(assets_dir, "destruction_pillar_ue.fbx")
        export_ue_fbx(fbx_path)
        self.report({'INFO'}, f"UE5 FBX 出力完了: {fbx_path}")
        return {'FINISHED'}

class VIEW3D_PT_DestructionExportPanel(bpy.types.Panel):
    bl_label = "💥 破壊シミュレーション ツール"
    bl_idname = "VIEW3D_PT_destruction_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Destruction Tools"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Unreal Engine 5 一発出力", icon='EXPORT')
        box.operator("object.export_destruction_ue_fbx", icon='FILE_3D')

classes = (
    OBJECT_OT_ExportDestructionUE5FBX,
    VIEW3D_PT_DestructionExportPanel,
)

def register_ui():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass

# ------------------------------------------------------------------------------
# 🚀 8. メインエントリーポイント
# ------------------------------------------------------------------------------
def main():
    clear_scene()

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = ANIM_TOTAL_FRAMES
    scene.render.fps = FPS

    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    scene.rigidbody_world.point_cache.frame_start = 1
    scene.rigidbody_world.point_cache.frame_end = ANIM_TOTAL_FRAMES

    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    os.makedirs(assets_dir, exist_ok=True)

    print("🎨 Step 1: Creating materials...")
    outer_mat  = create_outer_stone_material()
    inner_mat  = create_inner_chipped_material()
    cannon_mat = create_cannonball_material()

    print("🏛️ Step 2: Building ancient stone pillar...")
    pillar, pedestal = build_decorative_pillar(outer_mat, inner_mat)

    print("💥 Step 3: Fracturing & Breakable constraints...")
    shards = fracture_pillar_and_setup_physics(pillar, outer_mat, inner_mat)

    print("🚀 Step 4: Setting up cannonball collider...")
    ball = setup_cannonball_and_ground(pedestal, cannon_mat)

    print("🎬 Step 5: Baking physics to keyframes...")
    bake_simulation_to_keyframes(shards, total_frames=ANIM_TOTAL_FRAMES)

    setup_lighting()
    register_ui()

    if RENDER_CUTS:
        print("📸 Step 6: Rendering 4 cinematic Cycles cuts (Impact & Dramatic Collapse)...")
        # Cut 1: メインシネマティック - 砲弾直撃＆破片が四方八方に爆散する瞬間 (Frame 10)
        render_cut_target(os.path.join(assets_dir, "destruction_pillar_cut1.png"), (4.4, -4.6, 2.2), (0, 0.2, 1.3), lens=32, frame=10)
        render_cut_target(os.path.join(assets_dir, "destruction_pillar.png"), (4.4, -4.6, 2.2), (0, 0.2, 1.3), lens=32, frame=10)
        # Cut 2: 直撃直後の激しい破断面・砕石マテリアルのクローズアップ (Frame 10)
        render_cut_target(os.path.join(assets_dir, "destruction_pillar_cut2.png"), (1.8, -2.2, 1.5), (0.2, 0.1, 1.3), lens=60, frame=10)
        # Cut 3: 柱頭が崩落し台座に瓦礫が散乱する俯瞰 (Frame 25)
        render_cut_target(os.path.join(assets_dir, "destruction_pillar_cut3.png"), (2.5, -4.2, 3.8), (0, 0.2, 0.6), lens=34, frame=25)
        # Cut 4: 直撃寸前の緊張感 (Frame 5)
        render_cut_target(os.path.join(assets_dir, "destruction_pillar_cut4.png"), (-2.8, -3.6, 2.0), (0, -0.6, 1.5), lens=46, frame=5)
        print("✅ Finished rendering all 4 Cycles cinematic cuts!")

    if EXPORT_UE_FBX:
        fbx_path = os.path.join(assets_dir, "destruction_pillar_ue.fbx")
        export_ue_fbx(fbx_path)

    if EXPORT_CATALOG_GLB:
        glb_path = os.path.join(assets_dir, "destruction_pillar.glb")
        export_catalog_glb(glb_path)

    select_export_objects()
    scene.frame_set(1)
    print("\n🎉 Destruction Stone Pillar generated successfully!")
    print("💡 Press SPACE in Blender to watch the dramatic destruction simulation!")

if __name__ == "__main__":
    main()
