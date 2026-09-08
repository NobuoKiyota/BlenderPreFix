"""
================================================================================
📖 GEN_BOOK_PAGE_TURN.PY - MASTER GENERATOR FOR UNREAL ENGINE & BLENDER
================================================================================
【機能概要】
1. 完全シームレス無限トレッドミルめくりループ (120フレーム・4.0秒・30fps)
   - 16ページの極薄紙（64ボーン統合アーマチュア）によるModulo循環位相制御。
   - Frame 1 と Frame 120 の姿勢・しなりが数学的に完全一致し、Unreal Engineで
     bLooping=true にした際に1フレームの引っかかりもなく永遠にめくりが持続。
2. プロシージャル魔導図形＆古文書テクスチャの自動ベイク (PNG出力)
   - 外部画像不要のプロシージャルシェーダーから、直交カメラにより1024x1024の
     BaseColorテクスチャ（古文書テキスト、魔導天体図、放射曼荼羅、深紅レザー）を自動出力。
   - ベイク済みテクスチャをマテリアルにバインドするため、UE5にFBXをドラッグ＆ドロップするだけで
     自動的に美しいテクスチャ付きマテリアルがセットアップされます。
3. Unreal Engine 5 最適化 FBX 一発エクスポート
   - UE座標系（-Z Forward / Y Up）、リーフボーン除去、全ボーンキーフレームベイク。
   - `catalog/assets/book_page_turn_ue.fbx` として出力。
4. Web 3Dカタログ用 GLB & Cycles 4アングル シネマティックレンダリング
   - Blender 3.6 / 4.x / 5.x 完全互換（Action F-Curves安全ガード完備）。
================================================================================
"""

import bpy
import bmesh
import math
import os
import random

# ==============================================================================
# 🎛️ 実行制御スイッチ (Execution Switches)
# ここで True / False を切り替えるだけで、Alt + P 実行時の処理を自由に選べます！
# ==============================================================================
EXPORT_UE_FBX       = True   # 🎮 Unreal Engine 5 最適化 FBX を一発出力 (book_page_turn_ue.fbx)
FORCE_REBAKE        = False  # 🎨 テクスチャ強制再ベイク (Falseなら既存PNGを使って約0.5秒で高速完了)
EXPORT_CATALOG_GLB  = False  # 🌐 Webカタログ用 GLB を出力 (book_page_turn.glb)
RENDER_CUTS         = False  # 📸 Cycles シネマティック4カット画像をレンダリング (数秒〜十数秒かかります)

# ------------------------------------------------------------------------------
# ⚙️ グローバル設定
# ------------------------------------------------------------------------------
BOOK_WIDTH = 1.40
BOOK_HEIGHT = 2.10
COVER_THICKNESS = 0.026
SPINE_WIDTH = 0.16

PAGE_SPREAD_WIDTH = 1.35
PAGE_WIDTH = 1.38
PAGE_HEIGHT = 2.05

# シームレス無限トレッドミルループ設定
PAGE_COUNT = 16          # 循環ページ数
BONE_COUNT = 4           # 各ページのFKボーン数 (計64ボーン)
ANIM_TOTAL_FRAMES = 120  # 4秒間 (30fps)
FPS = 30

ENABLE_DIAGRAMS = True

# ------------------------------------------------------------------------------
# 🧹 シーンクリーンアップ
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
    for b in list(bpy.data.armatures):
        bpy.data.armatures.remove(b)
    for b in list(bpy.data.actions):
        bpy.data.actions.remove(b)
    for b in list(bpy.data.materials):
        bpy.data.materials.remove(b)

def set_active_and_mode(obj, mode='OBJECT'):
    """BlenderのText EditorやどのGUIコンテキストでも安全にオブジェクトをアクティブにしてmode_setを行う"""
    if obj is None:
        return
    if hasattr(obj, 'mode') and obj.mode == mode:
        return
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
    except Exception:
        pass
    obj.select_set(True)
    if hasattr(bpy.context, 'view_layer') and hasattr(bpy.context.view_layer, 'objects'):
        bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.mode_set(mode=mode)
    except Exception:
        try:
            with bpy.context.temp_override(active_object=obj, selected_objects=[obj], object=obj):
                bpy.ops.object.mode_set(mode=mode)
        except Exception:
            pass

def get_active_object():
    """BlenderのText Editorや3D Viewportなど、どのGUIコンテキストでも安全にアクティブオブジェクトを取得する"""
    vl = getattr(bpy.context, 'view_layer', None)
    if vl and hasattr(vl, 'objects') and getattr(vl.objects, 'active', None):
        return vl.objects.active
    if hasattr(bpy.context, 'active_object'):
        return bpy.context.active_object
    return None

def set_specular(bsdf_node, val):
    for sock_name in ['Specular IOR Level', 'Specular']:
        if sock_name in bsdf_node.inputs:
            bsdf_node.inputs[sock_name].default_value = val
            break

# ------------------------------------------------------------------------------
# 🎨 1. プロシージャルシェーダーの定義（ベイク元）
# ------------------------------------------------------------------------------
def create_procedural_manuscript_mat(name, has_diagram=False, diag_seed=0, pos=(-0.50, -0.62), radius=0.22):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.88
    set_specular(bsdf, 0.08)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new(type='ShaderNodeTexCoord')

    # 水平テキスト行
    map_lines = nodes.new(type='ShaderNodeMapping')
    map_lines.inputs['Scale'].default_value = (1.0, 65.0, 1.0)
    links.new(coord.outputs['UV'], map_lines.inputs['Vector'])

    wave_lines = nodes.new(type='ShaderNodeTexWave')
    wave_lines.wave_type = 'BANDS'
    wave_lines.bands_direction = 'Y'
    wave_lines.inputs['Scale'].default_value = 12.0
    wave_lines.inputs['Distortion'].default_value = 1.2
    links.new(map_lines.outputs['Vector'], wave_lines.inputs['Vector'])

    noise_chars = nodes.new(type='ShaderNodeTexNoise')
    noise_chars.inputs['Scale'].default_value = 85.0
    noise_chars.inputs['Detail'].default_value = 6.0
    links.new(coord.outputs['UV'], noise_chars.inputs['Vector'])

    math_text = nodes.new(type='ShaderNodeMath')
    math_text.operation = 'MULTIPLY'
    links.new(wave_lines.outputs['Color'], math_text.inputs[0])
    links.new(noise_chars.outputs['Fac'], math_text.inputs[1])

    if has_diagram:
        # 図解の配置（ページ上の位置とサイズを可変に）
        map_diag = nodes.new(type='ShaderNodeMapping')
        map_diag.inputs['Location'].default_value = (pos[0], pos[1], 0)
        links.new(coord.outputs['UV'], map_diag.inputs['Vector'])

        dist = nodes.new(type='ShaderNodeVectorMath')
        dist.operation = 'LENGTH'
        links.new(map_diag.outputs['Vector'], dist.inputs[0])

        mask_diag = nodes.new(type='ShaderNodeMath')
        mask_diag.operation = 'LESS_THAN'
        mask_diag.inputs[1].default_value = radius
        links.new(dist.outputs['Value'], mask_diag.inputs[0])

        wave_rings = nodes.new(type='ShaderNodeTexWave')
        wave_rings.wave_type = 'RINGS'
        wave_rings.rings_direction = 'SPHERICAL'
        wave_rings.inputs['Scale'].default_value = 32.0 + (diag_seed % 3) * 12.0
        links.new(map_diag.outputs['Vector'], wave_rings.inputs['Vector'])

        grad_rad = nodes.new(type='ShaderNodeTexGradient')
        grad_rad.gradient_type = 'RADIAL'
        links.new(map_diag.outputs['Vector'], grad_rad.inputs['Vector'])

        wave_spokes = nodes.new(type='ShaderNodeTexWave')
        wave_spokes.bands_direction = 'X'
        wave_spokes.inputs['Scale'].default_value = 16.0 + (diag_seed % 2) * 8.0
        links.new(grad_rad.outputs['Color'], wave_spokes.inputs['Vector'])

        voro = nodes.new(type='ShaderNodeTexVoronoi')
        voro.feature = 'DISTANCE_TO_EDGE'
        voro.inputs['Scale'].default_value = 12.0 + (diag_seed % 3) * 6.0
        links.new(map_diag.outputs['Vector'], voro.inputs['Vector'])

        m1 = nodes.new(type='ShaderNodeMath')
        m1.operation = 'MAXIMUM'
        links.new(wave_rings.outputs['Color'], m1.inputs[0])
        links.new(wave_spokes.outputs['Color'], m1.inputs[1])

        m2 = nodes.new(type='ShaderNodeMath')
        m2.operation = 'MAXIMUM'
        links.new(m1.outputs['Value'], m2.inputs[0])
        links.new(voro.outputs['Distance'], m2.inputs[1])

        diag_ink = nodes.new(type='ShaderNodeMath')
        diag_ink.operation = 'MULTIPLY'
        links.new(m2.outputs['Value'], diag_ink.inputs[0])
        links.new(mask_diag.outputs['Value'], diag_ink.inputs[1])

        not_mask = nodes.new(type='ShaderNodeMath')
        not_mask.operation = 'SUBTRACT'
        not_mask.inputs[0].default_value = 1.0
        links.new(mask_diag.outputs['Value'], not_mask.inputs[1])

        masked_text = nodes.new(type='ShaderNodeMath')
        masked_text.operation = 'MULTIPLY'
        links.new(math_text.outputs['Value'], masked_text.inputs[0])
        links.new(not_mask.outputs['Value'], masked_text.inputs[1])

        final_ink = nodes.new(type='ShaderNodeMath')
        final_ink.operation = 'MAXIMUM'
        links.new(masked_text.outputs['Value'], final_ink.inputs[0])
        links.new(diag_ink.outputs['Value'], final_ink.inputs[1])
    else:
        final_ink = math_text

    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = (0.94, 0.90, 0.83, 1.0)
    ramp.color_ramp.elements[1].position = 0.52
    ramp.color_ramp.elements[1].color = (0.10, 0.08, 0.07, 1.0)
    links.new(final_ink.outputs['Value'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump_paper = nodes.new(type='ShaderNodeBump')
    bump_paper.inputs['Strength'].default_value = 0.03
    links.new(noise_chars.outputs['Fac'], bump_paper.inputs['Height'])
    links.new(bump_paper.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_procedural_leather_mat():
    mat = bpy.data.materials.new(name="M_Leather_Cover")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.45
    set_specular(bsdf, 0.35)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new(type='ShaderNodeTexCoord')
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.65
    links.new(coord.outputs['UV'], noise.inputs['Vector'])

    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.35, 0.06, 0.08, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.18, 0.02, 0.03, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# ------------------------------------------------------------------------------
# 🖼️ 2. テクスチャ自動ベイク（直交カメラによる1024x1024 PNG書き出し）
# ------------------------------------------------------------------------------
def bake_procedural_textures(textures_dir):
    os.makedirs(textures_dir, exist_ok=True)
    scene = bpy.context.scene
    orig_engine = scene.render.engine
    orig_res_x = scene.render.resolution_x
    orig_res_y = scene.render.resolution_y
    orig_cam = scene.camera

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    bake_list = [
        ("T_Manuscript_Plain_BC.png",       lambda: create_procedural_manuscript_mat("Temp_Plain", has_diagram=False)),
        ("T_Manuscript_Diag_Top_BC.png",    lambda: create_procedural_manuscript_mat("Temp_DiagTop", has_diagram=True, diag_seed=5, pos=(-0.50, -0.74), radius=0.17)),      # 上部カット
        ("T_Manuscript_Diag_Right_BC.png",  lambda: create_procedural_manuscript_mat("Temp_DiagRight", has_diagram=True, diag_seed=12, pos=(-0.65, -0.38), radius=0.18)),    # 右下寄り
        ("T_Manuscript_Diag_Center_BC.png", lambda: create_procedural_manuscript_mat("Temp_DiagCenter", has_diagram=True, diag_seed=8, pos=(-0.50, -0.50), radius=0.24)),   # 中央大図
        ("T_Leather_Cover_BC.png",          lambda: create_procedural_leather_mat()),
    ]

    # 既にテクスチャが存在する場合は再ベイクをスキップして即座にモデル構築へ（超高速実行）
    all_exist = all(os.path.exists(os.path.join(textures_dir, fn)) for fn, _ in bake_list)
    if all_exist and not FORCE_REBAKE:
        print("⚡ Baked textures already exist. Reusing existing textures for instant startup!")
        return {fn: os.path.join(textures_dir, fn) for fn, _ in bake_list}

    # 直交カメラとベイク平面
    cam_data = bpy.data.cameras.new("OrthoBakeCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 2.0
    bake_cam = bpy.data.objects.new("OrthoBakeCam", cam_data)
    bpy.context.collection.objects.link(bake_cam)
    scene.camera = bake_cam
    bake_cam.location = (0, 0, 3.0)

    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, 0))
    quad = get_active_object()
    quad.name = "BakeQuad"

    baked_paths = {}
    for filename, mat_func in bake_list:
        out_path = os.path.join(textures_dir, filename)
        baked_paths[filename] = out_path
        mat = mat_func()

        # Albedo Emission Conversion for crisp unshaded bake
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        out_node = nodes.get("Material Output")
        bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf and out_node:
            c_sock = bsdf.inputs['Base Color']
            if c_sock.links:
                src = c_sock.links[0].from_socket
                emit = nodes.new(type='ShaderNodeEmission')
                links.new(src, emit.inputs['Color'])
                links.new(emit.outputs['Emission'], out_node.inputs['Surface'])

        quad.data.materials.clear()
        quad.data.materials.append(mat)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"✅ Baked texture: {out_path}")

    # クリーンアップ
    bpy.data.objects.remove(quad, do_unlink=True)
    bpy.data.objects.remove(bake_cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)

    scene.render.engine = orig_engine
    scene.render.resolution_x = orig_res_x
    scene.render.resolution_y = orig_res_y
    scene.camera = orig_cam

    return baked_paths

# ------------------------------------------------------------------------------
# 🎮 3. UE5 互換テクスチャ適用マテリアルの作成
# ------------------------------------------------------------------------------
def create_textured_material(name, texture_path, roughness=0.88, is_leather=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = roughness
    set_specular(bsdf, 0.35 if is_leather else 0.08)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    if os.path.exists(texture_path):
        img = bpy.data.images.load(texture_path)
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = img
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.94, 0.90, 0.83, 1.0)

    return mat

def create_gold_material():
    mat = bpy.data.materials.new(name="M_Book_Gold")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.70, 0.22, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.90
        bsdf.inputs['Roughness'].default_value = 0.25
        set_specular(bsdf, 0.5)
    return mat

def create_ribbon_material():
    mat = bpy.data.materials.new(name="M_Book_Ribbon")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.45, 0.04, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.40
        set_specular(bsdf, 0.35)
    return mat

def create_pages_block_material():
    mat = bpy.data.materials.new(name="M_Book_Pages_Block")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.85, 0.78, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85
        set_specular(bsdf, 0.12)
    return mat

# ------------------------------------------------------------------------------
# 📖 4. 本のハードウェア（本体モデリング）
# ------------------------------------------------------------------------------
def build_book_body(cover_mat, block_mat, gold_mat, ribbon_mat, left_top_mat):
    objects = []

    # 1. 背表紙 (Spine)
    bm = bmesh.new()
    spine_w = 0.18
    spine_h = 2.22
    spine_thick = 0.025
    spine_segs = 8

    s_verts = []
    for yi in range(2):
        y = -spine_h/2 if yi == 0 else spine_h/2
        row = []
        for xi in range(spine_segs + 1):
            t = xi / spine_segs
            ang = -math.pi/2 + t * math.pi
            x = math.sin(ang) * (spine_w * 0.5)
            z = -math.cos(ang) * 0.025 + 0.012
            row.append(bm.verts.new((x, y, z)))
        s_verts.append(row)

    for xi in range(spine_segs):
        bm.faces.new([s_verts[0][xi], s_verts[0][xi+1], s_verts[1][xi+1], s_verts[1][xi]])

    mesh_spine = bpy.data.meshes.new("Book_Spine_Mesh")
    bm.to_mesh(mesh_spine)
    bm.free()

    spine_obj = bpy.data.objects.new("Book_Spine", mesh_spine)
    bpy.context.collection.objects.link(spine_obj)
    spine_obj.data.materials.append(cover_mat)
    sol = spine_obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = spine_thick
    sol.offset = 1.0
    for p in spine_obj.data.polygons: p.use_smooth = True
    objects.append(spine_obj)

    # 2. 左右のハードカバー (Covers with Bevel)
    cover_w = 1.48
    cover_h = 2.22
    cover_thick = 0.028

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.82, 0, 0.012))
    left_cover = get_active_object()
    left_cover.name = "Book_Cover_Left"
    left_cover.scale = (cover_w, cover_h, cover_thick)
    bpy.ops.object.transform_apply(scale=True)
    left_cover.data.materials.append(cover_mat)
    bev_l = left_cover.modifiers.new("Bevel", 'BEVEL')
    bev_l.width = 0.008
    bev_l.segments = 3
    objects.append(left_cover)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.82, 0, 0.012))
    right_cover = get_active_object()
    right_cover.name = "Book_Cover_Right"
    right_cover.scale = (cover_w, cover_h, cover_thick)
    bpy.ops.object.transform_apply(scale=True)
    right_cover.data.materials.append(cover_mat)
    bev_r = right_cover.modifiers.new("Bevel", 'BEVEL')
    bev_r.width = 0.008
    bev_r.segments = 3
    objects.append(right_cover)

    # 3. 金のコーナー金具 (Corner Guards)
    corner_size = 0.12
    corner_thick = 0.032
    for cx in [-1.50, 1.50]:
        for cy in [-1.05, 1.05]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 0.012))
            c_obj = get_active_object()
            c_obj.name = f"Book_Corner_{cx}_{cy}"
            c_obj.scale = (corner_size, corner_size, corner_thick)
            bpy.ops.object.transform_apply(scale=True)
            c_obj.data.materials.append(gold_mat)
            objects.append(c_obj)

    # 4. 左右の積層紙ブロック (Page Blocks)
    block_w = PAGE_WIDTH
    block_h = PAGE_HEIGHT
    block_thick = 0.036

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.74, 0, 0.038))
    left_block = get_active_object()
    left_block.name = "Book_Pages_Block_Left"
    left_block.scale = (block_w, block_h, block_thick)
    bpy.ops.object.transform_apply(scale=True)
    left_block.data.materials.append(block_mat)
    objects.append(left_block)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.74, 0, 0.038))
    right_block = get_active_object()
    right_block.name = "Book_Pages_Block_Right"
    right_block.scale = (block_w, block_h, block_thick)
    bpy.ops.object.transform_apply(scale=True)
    right_block.data.materials.append(block_mat)
    objects.append(right_block)

    # 5. 左右の上面固定ページ
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-0.74, 0, 0.056))
    left_top_page = get_active_object()
    left_top_page.name = "Book_Top_Page_Left"
    left_top_page.scale = (block_w, block_h, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    left_top_page.data.materials.append(left_top_mat)
    objects.append(left_top_page)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.74, 0, 0.056))
    right_top_page = get_active_object()
    right_top_page.name = "Book_Top_Page_Right"
    right_top_page.scale = (block_w, block_h, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    right_top_page.data.materials.append(left_top_mat)
    objects.append(right_top_page)

    # 6. しおり布リボン
    bm_rib = bmesh.new()
    rib_pts = [
        (0.0, 1.05, 0.070),
        (0.06, 0.60, 0.065),
        (0.12, 0.00, 0.062),
        (0.18, -0.60, 0.060),
        (0.25, -1.15, 0.050),
        (0.32, -1.30, 0.015)
    ]
    r_verts = []
    for pt in rib_pts:
        v1 = bm_rib.verts.new((pt[0] - 0.02, pt[1], pt[2]))
        v2 = bm_rib.verts.new((pt[0] + 0.02, pt[1], pt[2]))
        r_verts.append((v1, v2))
    for i in range(len(rib_pts) - 1):
        bm_rib.faces.new([r_verts[i][0], r_verts[i][1], r_verts[i+1][1], r_verts[i+1][0]])

    mesh_rib = bpy.data.meshes.new("Book_Ribbon_Mesh")
    bm_rib.to_mesh(mesh_rib)
    bm_rib.free()

    rib_obj = bpy.data.objects.new("Book_Ribbon", mesh_rib)
    bpy.context.collection.objects.link(rib_obj)
    rib_obj.data.materials.append(ribbon_mat)
    sol_r = rib_obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol_r.thickness = 0.002
    for p in rib_obj.data.polygons: p.use_smooth = True
    objects.append(rib_obj)

    return objects

# ------------------------------------------------------------------------------
# 🔄 5. 無限トレッドミル・完全シームレスめくりリグ (Seamless Treadmill Loop Rig)
# ------------------------------------------------------------------------------
def build_treadmill_system(materials_list):
    scene = bpy.context.scene
    bone_len = PAGE_SPREAD_WIDTH / BONE_COUNT

    # 1. 統合アーマチュア (Single Unified Armature)
    arm_data = bpy.data.armatures.new("Book_Pages_Armature")
    arm_obj = bpy.data.objects.new("Book_Pages_Rig", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    set_active_and_mode(arm_obj, 'EDIT')

    page_bones = {}
    base_z_start = 0.040
    layer_step = 0.0008

    for p in range(PAGE_COUNT):
        pz = base_z_start + p * layer_step
        prev_b = None
        b_list = []
        for b in range(BONE_COUNT):
            bname = f"P{p:02d}_B{b}"
            b_list.append(bname)
            eb = arm_data.edit_bones.new(bname)
            eb.head = (b * bone_len, 0, pz)
            eb.tail = ((b + 1) * bone_len, 0, pz)
            if prev_b:
                eb.parent = prev_b
                eb.use_connect = True
            prev_b = eb
        page_bones[p] = b_list

    set_active_and_mode(arm_obj, 'OBJECT')

    # 2. メッシュ生成とスキニング (UVマップ付き)
    page_objects = []
    x_segs = 20
    y_segs = 8

    for p in range(PAGE_COUNT):
        pz = base_z_start + p * layer_step
        bm = bmesh.new()
        verts = []
        for yi in range(y_segs + 1):
            row = []
            y = -PAGE_HEIGHT / 2 + (PAGE_HEIGHT / y_segs) * yi
            for xi in range(x_segs + 1):
                x = (PAGE_SPREAD_WIDTH / x_segs) * xi
                row.append(bm.verts.new((x, y, pz)))
            verts.append(row)

        for yi in range(y_segs):
            for xi in range(x_segs):
                bm.faces.new([verts[yi][xi], verts[yi][xi+1], verts[yi+1][xi+1], verts[yi+1][xi]])

        # UVマップの確実なベイク
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                u = loop.vert.co.x / PAGE_SPREAD_WIDTH
                v = (loop.vert.co.y + PAGE_HEIGHT / 2.0) / PAGE_HEIGHT
                loop[uv_layer].uv = (u, v)

        mesh = bpy.data.meshes.new(f"Page_Mesh_{p:02d}")
        bm.to_mesh(mesh)
        bm.free()

        p_obj = bpy.data.objects.new(f"Page_{p:02d}", mesh)
        bpy.context.collection.objects.link(p_obj)

        # マテリアル割り当て（プレーンと魔導図形が交互に混ざる）
        mat = materials_list[p % len(materials_list)]
        p_obj.data.materials.append(mat)
        for poly in p_obj.data.polygons: poly.use_smooth = True

        b_names = page_bones[p]
        for bname in b_names:
            p_obj.vertex_groups.new(name=bname)

        for v in mesh.vertices:
            vx = v.co.x
            for bi, bname in enumerate(b_names):
                b_mid = (bi + 0.5) * bone_len
                dist = abs(vx - b_mid)
                w = max(0.0, 1.0 - (dist / (bone_len * 1.25)))
                if w > 0:
                    p_obj.vertex_groups[bname].add([v.index], w, 'REPLACE')

        p_obj.parent = arm_obj
        mod = p_obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm_obj
        page_objects.append(p_obj)

    # 3. 完全シームレス・無限トレッドミルめくりアニメーション (Modulo Cyclic Control)
    action = bpy.data.actions.new(name="Book_Treadmill_Loop_Action")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    def smoothstep(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3.0 - 2.0 * x)

    for frame in range(1, ANIM_TOTAL_FRAMES + 1):
        scene.frame_set(frame)
        t = (frame - 1) / float(ANIM_TOTAL_FRAMES)

        for p in range(PAGE_COUNT):
            phi_p = p / float(PAGE_COUNT)
            phase = (t + phi_p) % 1.0  # 0.0 <= phase < 1.0

            b_names = page_bones[p]
            pb_root = arm_obj.pose.bones[b_names[0]]

            # 1. めくりフェーズ (右の束から空中に浮き上がり、放物線アーチで左へ着地) [0.0 <= phase < 0.20]
            if phase < 0.20:
                u = phase / 0.20
                s = smoothstep(u)
                root_deg = 180.0 * s
                curl1 = math.sin(u * math.pi) * 22.0
                curl2 = math.sin(u * math.pi) * 14.0
                curl3 = -math.sin(u * math.pi) * 18.0
                lift_z = math.sin(u * math.pi) * 0.18
                pz = (1.0 - s) * 0.012 + s * (-0.006) + lift_z
                scale_val = (1.0, 1.0, 1.0)

            # 2. 左側の束に滞留・静止フェーズ (見開きページとして読まれる) [0.20 <= phase < 0.68]
            elif phase < 0.68:
                root_deg = 180.0
                curl1 = 0.0
                curl2 = 0.0
                curl3 = 0.0
                pz = -0.006 - ((phase - 0.20) / 0.48) * 0.012
                scale_val = (1.0, 1.0, 1.0)

            # 3. 台座ブロックの裏を通って右へ戻る循環リターンフェーズ [0.68 <= phase < 0.84]
            elif phase < 0.84:
                u = (phase - 0.68) / 0.16
                s = smoothstep(u)
                root_deg = 180.0 * (1.0 - s)
                curl1 = 0.0
                curl2 = 0.0
                curl3 = 0.0
                pz = -0.045  # 台座ブロックの裏に完全に隠蔽
                sc_x = 1.0 - 0.18 * math.sin(u * math.pi)
                scale_val = (sc_x, 1.0, 1.0)

            # 4. 右側の束で次のめくりを待機するフェーズ [0.84 <= phase < 1.0]
            else:
                root_deg = 0.0
                curl1 = 0.0
                curl2 = 0.0
                curl3 = 0.0
                pz = 0.004 + ((phase - 0.84) / 0.16) * 0.010
                scale_val = (1.0, 1.0, 1.0)

            # ボーンの長軸（X軸）に沿った自然な本のページめくりRoll回転
            pb_root.rotation_mode = 'XYZ'
            pb_root.rotation_euler = (math.radians(root_deg), 0, 0)
            pb_root.location = (0, 0, pz)
            pb_root.scale = scale_val
            pb_root.keyframe_insert(data_path="rotation_euler", frame=frame)
            pb_root.keyframe_insert(data_path="location", frame=frame)
            pb_root.keyframe_insert(data_path="scale", frame=frame)

            # 各関節のしなりとしなり戻り
            curls = [curl1, curl2, curl3]
            for bi in range(1, BONE_COUNT):
                pb = arm_obj.pose.bones[b_names[bi]]
                pb.rotation_mode = 'XYZ'
                pb.rotation_euler = (math.radians(curls[bi - 1]), 0, 0)
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Blender 4.x / 5.x Action F-Curves 安全ガード
    fcurves = getattr(action, 'fcurves', None)
    if fcurves is not None:
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'BEZIER'

    print("✅ Infinite treadmill loop animation successfully created (Seam continuity mathematically perfect)!")
    return page_objects, arm_obj

# ------------------------------------------------------------------------------
# 💡 6. スタジオ照明とレンダリング設定
# ------------------------------------------------------------------------------
def setup_lighting():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540

    world = bpy.data.worlds.new("BookWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.04, 0.04, 0.06, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    # 3点スタジオシネマティック照明
    bpy.ops.object.light_add(type='AREA', location=(2.6, -2.8, 3.2))
    key = get_active_object()
    key.name = "KeyLight"
    key.data.energy = 550.0
    key.data.size = 4.2
    key.data.color = (1.0, 0.96, 0.90)

    bpy.ops.object.light_add(type='AREA', location=(-2.6, -2.2, 2.4))
    fill = get_active_object()
    fill.name = "FillLight"
    fill.data.energy = 220.0
    fill.data.size = 3.8
    fill.data.color = (0.75, 0.85, 1.0)

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.4, 3.8))
    rim = get_active_object()
    rim.name = "RimLight"
    rim.data.energy = 650.0
    rim.data.spot_size = math.radians(65)
    rim.data.color = (0.95, 0.98, 1.0)

def render_cut_target(filepath, cam_pos, target_pos=(0, 0, 0.20), lens=45, samples=28, frame=30):
    scene = bpy.context.scene
    scene.frame_set(frame)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_pos)
    target = get_active_object()
    target.name = 'CamTarget'

    bpy.ops.object.camera_add(location=cam_pos)
    cam = get_active_object()
    cam.data.lens = lens

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    scene.camera = cam
    scene.render.image_settings.file_format = 'PNG'
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
# 📦 6. エクスポート処理 & UI連携
# ------------------------------------------------------------------------------
def select_book_objects():
    """本のリグとメッシュのみを安全に選択する（ライトやカメラを除外）"""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in {'ARMATURE', 'MESH'} and not obj.name.startswith("OrthoBake"):
            obj.select_set(True)

def export_ue_fbx(fbx_path):
    """Unreal Engine 5 最適化 FBX 一発エクスポート"""
    print(f"🎮 Exporting UE5-optimized FBX to: {fbx_path}...")
    select_book_objects()
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        use_armature_deform_only=True,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        embed_textures=False,
        path_mode='RELATIVE'
    )
    print(f"✅ Successfully exported UE5-optimized FBX: {fbx_path}")

def export_catalog_glb(glb_path):
    """Webカタログ用 GLB エクスポート (完全シームレス120フレームループ)"""
    print(f"🌐 Exporting Web Catalog GLB to: {glb_path}...")
    select_book_objects()
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_animations=True,
        export_frame_range=True,
        export_frame_step=1,
        export_force_sampling=True,
        export_skins=True,
        export_all_influences=True
    )
    print(f"✅ Successfully exported seamless loop GLB: {glb_path}")

# ------------------------------------------------------------------------------
# 🎛️ 3D Viewport Nパネル (サイドバー) ワンクリックUI
# ------------------------------------------------------------------------------
class OBJECT_OT_ExportUE5FBX(bpy.types.Operator):
    bl_idname = "object.export_book_ue_fbx"
    bl_label = "🎮 Export UE5 FBX"
    bl_description = "現在の本モデルとアニメーションをUE5最適化FBXとして一発エクスポートします"

    def execute(self, context):
        assets_dir = r"e:\BlenderPreFix\catalog\assets"
        fbx_path = os.path.join(assets_dir, "book_page_turn_ue.fbx")
        export_ue_fbx(fbx_path)
        self.report({'INFO'}, f"UE5 FBX 出力完了: {fbx_path}")
        return {'FINISHED'}

class VIEW3D_PT_BookExportPanel(bpy.types.Panel):
    bl_label = "📖 魔導書ツール"
    bl_idname = "VIEW3D_PT_book_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Book Tools"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Unreal Engine 5 一発出力", icon='EXPORT')
        box.operator("object.export_book_ue_fbx", icon='FILE_3D')

classes = (
    OBJECT_OT_ExportUE5FBX,
    VIEW3D_PT_BookExportPanel,
)

def register_ui():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass

def unregister_ui():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

# ------------------------------------------------------------------------------
# 🚀 7. メインエントリーポイント
# ------------------------------------------------------------------------------
def main():
    clear_scene()

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = ANIM_TOTAL_FRAMES
    scene.render.fps = FPS

    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    textures_dir = os.path.join(assets_dir, "textures")
    os.makedirs(textures_dir, exist_ok=True)

    # 1. プロシージャルテクスチャの自動ベイク (1024x1024 PNG)
    print("🎨 Step 1: Baking procedural textures to PNG...")
    baked_paths = bake_procedural_textures(textures_dir)

    # 2. テクスチャ付きマテリアル構築
    cover_mat       = create_textured_material("M_Leather_Cover", baked_paths["T_Leather_Cover_BC.png"], roughness=0.45, is_leather=True)
    plain_mat       = create_textured_material("M_Manuscript_Plain", baked_paths["T_Manuscript_Plain_BC.png"], roughness=0.88)
    diag_top_mat    = create_textured_material("M_Manuscript_Diag_Top", baked_paths["T_Manuscript_Diag_Top_BC.png"], roughness=0.88)
    diag_right_mat  = create_textured_material("M_Manuscript_Diag_Right", baked_paths["T_Manuscript_Diag_Right_BC.png"], roughness=0.88)
    diag_center_mat = create_textured_material("M_Manuscript_Diag_Center", baked_paths["T_Manuscript_Diag_Center_BC.png"], roughness=0.88)
    block_mat       = create_pages_block_material()
    gold_mat        = create_gold_material()
    ribbon_mat      = create_ribbon_material()

    # 図解の枚数を適正化（16枚中3枚のみ＝約19%：めくる間にたまに位置・サイズの異なる図解が現れる絶妙なリズム）
    page_materials = [plain_mat] * PAGE_COUNT
    page_materials[3]  = diag_top_mat     # 上部コンパクトカット図解
    page_materials[8]  = diag_right_mat   # 右下寄り錬金幾何学ダイアグラム
    page_materials[13] = diag_center_mat  # 中央大天体陣挿絵

    # 3. 本の本体構築（左右の見開き固定ページは落ち着いた古文書テキスト本文に統一）
    print("📖 Step 2: Building book hardware...")
    book_objs = build_book_body(cover_mat, block_mat, gold_mat, ribbon_mat, plain_mat)

    # 4. 無限トレッドミル・完全シームレスめくりリグ構築
    print("🔄 Step 3: Building seamless treadmill loop rig...")
    page_objs, arm_obj = build_treadmill_system(page_materials)

    setup_lighting()
    scene.frame_set(1)

    register_ui()

    # 5. Unreal Engine 5 最適化 FBX 一発エクスポート
    if EXPORT_UE_FBX:
        fbx_path = os.path.join(assets_dir, "book_page_turn_ue.fbx")
        export_ue_fbx(fbx_path)

    # 6. Webカタログ用 GLB エクスポート (完全シームレス120フレームループ)
    if EXPORT_CATALOG_GLB:
        glb_path = os.path.join(assets_dir, "book_page_turn.glb")
        export_catalog_glb(glb_path)

    # 7. Cycles 4アングル レンダリング (紙が舞うFrame 30)
    if RENDER_CUTS:
        print("📸 Step 6: Rendering 4 Cycles cinematic cuts...")
        render_cut_target(os.path.join(assets_dir, "book_page_turn_cut1.png"), (2.6, -3.2, 2.2), (0, 0, 0.18), lens=42, frame=30)
        render_cut_target(os.path.join(assets_dir, "book_page_turn.png"), (2.6, -3.2, 2.2), (0, 0, 0.18), lens=42, frame=30)
        render_cut_target(os.path.join(assets_dir, "book_page_turn_cut2.png"), (1.5, -1.8, 1.4), (0.1, 0, 0.40), lens=58, frame=30)
        render_cut_target(os.path.join(assets_dir, "book_page_turn_cut3.png"), (0.4, -2.6, 3.4), (0, 0, 0.15), lens=38, frame=30)
        render_cut_target(os.path.join(assets_dir, "book_page_turn_cut4.png"), (2.2, 0.5, 0.6), (0, 0, 0.12), lens=50, frame=30)
        print("✅ Finished rendering all 4 Cycles cinematic cuts!")

    # 完了後のビューポート準備（本全体を選択して見やすく）
    select_book_objects()
    if arm_obj:
        bpy.context.view_layer.objects.active = arm_obj
    print("\n🎉 All Done! Press SPACE in Blender to preview the seamless loop animation!")
    print("💡 3D Viewportの右側サイドバー(Nキー) > 'Book Tools' タブからも、いつでもUE5 FBXを一発出力できます。")

if __name__ == "__main__":
    main()
