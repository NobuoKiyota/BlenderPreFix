import bpy
import bmesh
import math
import random
import sys
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

# 1. PBR マテリアル定義
def create_glass_material():
    mat = bpy.data.materials.new(name="Potion_Glass_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.50
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 1.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Glass"
    mat["audio_tag"] = "Sound_Glass_Clink"
    return mat

def create_liquid_material():
    mat = bpy.data.materials.new(name="Potion_Liquid_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 幻想的なエメラルドグリーン〜シアン
    bsdf.inputs['Base Color'].default_value = (0.05, 0.85, 0.65, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 1.333
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.92
        
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (0.02, 0.95, 0.75, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 2.2
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (0.02, 0.95, 0.75, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 2.2
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Liquid"
    mat["audio_tag"] = "Sound_Potion_Slosh"
    return mat

def create_cork_material():
    mat = bpy.data.materials.new(name="Potion_Cork_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.38, 0.22, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 50.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.5
    
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Cork"
    mat["audio_tag"] = "Sound_Cork_Pop"
    return mat

def create_bubble_material():
    mat = bpy.data.materials.new(name="Potion_Bubble_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (0.3, 1.0, 0.9, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 12.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (0.3, 1.0, 0.9, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 12.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "MagicFX"
    mat["audio_tag"] = "Sound_Magic_Sparkle"
    return mat

def create_gold_band_material():
    mat = bpy.data.materials.new(name="Potion_Gold_Band_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.9, 0.72, 0.2, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.22
    mat["surface_type"] = "Metal"
    mat["audio_tag"] = "Sound_Metal_Ring"
    return mat

# 2. 幾何学モデリング
def build_potion_bottle_scene():
    glass_mat = create_glass_material()
    liquid_mat = create_liquid_material()
    cork_mat = create_cork_material()
    bubble_mat = create_bubble_material()
    gold_mat = create_gold_band_material()
    
    # 1. 丸底ガラス瓶の Bmesh モデリング
    bm = bmesh.new()
    segments = 32
    rings = 24
    
    # 球状胴体 + ネック + リップ の断面プロファイル
    profile = []
    # 底部の凹み
    profile.append((0.0, -0.02))
    profile.append((0.2, 0.0))
    # 球体胴体 (角度 -70度 から +60度)
    for i in range(16):
        ang = -math.pi/2.5 + (math.pi/1.3 / 15) * i
        r = 0.75 * math.cos(ang)
        z = 0.65 + 0.65 * math.sin(ang)
        profile.append((r, z))
    # 首（ネック）
    profile.append((0.24, 1.35))
    profile.append((0.24, 1.75))
    # 注ぎ口の縁（リップフランジ）
    profile.append((0.32, 1.78))
    profile.append((0.32, 1.86))
    profile.append((0.25, 1.88))
    
    # 旋回（Revolve / Lathe）
    prev_ring = None
    for r, z in profile:
        cur_ring = []
        for s in range(segments):
            angle = s * (2 * math.pi / segments)
            v = bm.verts.new((r * math.cos(angle), r * math.sin(angle), z))
            cur_ring.append(v)
        if prev_ring:
            for s in range(segments):
                s_next = (s + 1) % segments
                bm.faces.new([prev_ring[s], prev_ring[s_next], cur_ring[s_next], cur_ring[s]])
        prev_ring = cur_ring
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh_bottle = bpy.data.meshes.new("Potion_Glass_Bottle_Mesh")
    bm.to_mesh(mesh_bottle)
    bm.free()
    
    bottle = bpy.data.objects.new("Potion_Glass_Bottle", mesh_bottle)
    bpy.context.collection.objects.link(bottle)
    bottle.data.materials.append(glass_mat)
    for p in bottle.data.polygons:
        p.use_smooth = True
        
    # ガラスの厚み付け (Solidify)
    sol = bottle.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.035
    sub = bottle.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    
    # 2. 内部の液体（7分目まで満たされたソリッド形状）
    bm_liq = bmesh.new()
    liq_profile = []
    liq_profile.append((0.0, 0.02))
    liq_profile.append((0.19, 0.04))
    for i in range(12):
        ang = -math.pi/2.5 + (math.pi/1.3 / 15) * i
        r = 0.72 * math.cos(ang)
        z = 0.65 + 0.63 * math.sin(ang)
        liq_profile.append((r, z))
    # 液面の中心頂点
    top_z = liq_profile[-1][1]
    top_r = liq_profile[-1][0]
    
    prev_lring = None
    for r, z in liq_profile:
        cur_ring = []
        for s in range(segments):
            angle = s * (2 * math.pi / segments)
            # 液面に微小な波打ち
            wave = 0.008 * math.sin(angle * 3.0) if z == top_z else 0.0
            v = bm_liq.verts.new((r * math.cos(angle), r * math.sin(angle), z + wave))
            cur_ring.append(v)
        if prev_lring:
            for s in range(segments):
                s_next = (s + 1) % segments
                bm_liq.faces.new([prev_lring[s], prev_lring[s_next], cur_ring[s_next], cur_ring[s]])
        prev_lring = cur_ring
        
    # 液面のフタ（Cap）
    center_top = bm_liq.verts.new((0.0, 0.0, top_z + 0.005))
    for s in range(segments):
        s_next = (s + 1) % segments
        bm_liq.faces.new([prev_lring[s], prev_lring[s_next], center_top])
        
    bmesh.ops.recalc_face_normals(bm_liq, faces=bm_liq.faces)
    mesh_liq = bpy.data.meshes.new("Potion_Liquid_Mesh")
    bm_liq.to_mesh(mesh_liq)
    bm_liq.free()
    
    liquid = bpy.data.objects.new("Potion_Liquid", mesh_liq)
    bpy.context.collection.objects.link(liquid)
    liquid.data.materials.append(liquid_mat)
    for p in liquid.data.polygons:
        p.use_smooth = True
    sub_l = liquid.modifiers.new("Subsurf", 'SUBSURF')
    sub_l.levels = 1
    
    # 3. コルク栓（テーパー円柱）
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.25, 
        radius2=0.21, 
        depth=0.38, 
        location=(0, 0, 1.82)
    )
    cork = bpy.context.active_object
    cork.name = "Potion_Cork_Stopper"
    cork.data.materials.append(cork_mat)
    for p in cork.data.polygons:
        p.use_smooth = True
        
    # 4. 発光気泡（Bubbles）
    random.seed(101)
    bubble_objs = []
    for i in range(20):
        sz = random.uniform(0.018, 0.055)
        # 液体内部の半径範囲内に配置
        b_ang = random.uniform(0, 2*math.pi)
        b_dist = random.uniform(0.05, 0.52)
        bz = random.uniform(0.2, top_z - 0.08)
        bx = math.cos(b_ang) * b_dist
        by = math.sin(b_ang) * b_dist
        
        bpy.ops.mesh.primitive_ico_sphere_add(radius=sz, subdivisions=1, location=(bx, by, bz))
        b = bpy.context.active_object
        b.name = f"Bubble_{i+1}"
        b.data.materials.append(bubble_mat)
        bubble_objs.append(b)
        
    bpy.ops.object.select_all(action='DESELECT')
    for b in bubble_objs:
        b.select_set(True)
    bpy.context.view_layer.objects.active = bubble_objs[0]
    bpy.ops.object.join()
    all_bubbles = bpy.context.active_object
    all_bubbles.name = "Potion_Glowing_Bubbles"
    
    # 5. 金具バンド（首の装飾）
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.255, 
        minor_radius=0.025, 
        location=(0, 0, 1.55)
    )
    gold_ring = bpy.context.active_object
    gold_ring.name = "Potion_Gold_Neck_Ring"
    gold_ring.data.materials.append(gold_mat)
    for p in gold_ring.data.polygons:
        p.use_smooth = True
        
    return bottle, liquid, cork, all_bubbles, gold_ring

def setup_lighting():
    # キーライト（斜め前方から、ガラスの縦ハイライトを演出）
    light_key = bpy.data.lights.new(name="KeyLight", type='AREA')
    light_key.energy = 550.0
    light_key.size = 2.2
    light_key.color = (1.0, 0.98, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", light_key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (2.2, -2.4, 2.5)
    key_obj.rotation_euler = (math.radians(52), math.radians(12), math.radians(40))
    
    # リムライト（真後ろ少し上からの強い逆光透過光。液体の透過感・コースティクス感を激写）
    light_rim = bpy.data.lights.new(name="RimLight", type='AREA')
    light_rim.energy = 420.0
    light_rim.size = 1.8
    light_rim.color = (0.2, 0.85, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", light_rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-1.2, 2.8, 1.8)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(20), math.radians(-150))
    
    # フィルライト（柔らかな下からの反射）
    light_fill = bpy.data.lights.new(name="FillLight", type='POINT')
    light_fill.energy = 120.0
    light_fill.color = (0.1, 0.4, 0.8)
    fill_obj = bpy.data.objects.new("FillLight", light_fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-2.0, -1.5, 0.5)
    
    # 暗闇スタジオワールド
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioDark")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.012, 0.016, 0.024, 1.0)
        bg.inputs['Strength'].default_value = 0.3

def setup_camera(pos, rot_deg, lens=50):
    cam_data = bpy.data.cameras.new(name="Cam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name="Cam", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = pos
    cam_obj.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    bpy.context.scene.camera = cam_obj
    return cam_obj

def render_cut(filepath, pos, rot_deg, lens=50, samples=32):
    cam = setup_camera(pos, rot_deg, lens)
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.device = 'CPU'
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    print(f"Rendered cut to: {filepath}")

def main():
    clear_scene()
    bottle, liquid, cork, bubbles, ring = build_potion_bottle_scene()
    setup_lighting()
    
    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. 3D GLB エクスポート
    glb_path = os.path.join(assets_dir, "magic_potion.glb")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"Exported high quality GLB: {glb_path}")
    
    # 2. Cycles 4カットレンダリング
    # Cut 1: 正面シネマティック全体像（エメラルドの輝きとクリアなガラス）
    render_cut(
        os.path.join(assets_dir, "magic_potion_cut1.png"),
        pos=(2.2, -2.5, 1.2),
        rot_deg=(75, 0, 42),
        lens=50
    )
    # サムネイル用
    render_cut(
        os.path.join(assets_dir, "magic_potion.png"),
        pos=(2.2, -2.5, 1.2),
        rot_deg=(75, 0, 42),
        lens=50
    )
    
    # Cut 2: 液体と気泡のクローズアップ（内部の発光バブルと屈折）
    render_cut(
        os.path.join(assets_dir, "magic_potion_cut2.png"),
        pos=(1.2, -1.3, 0.75),
        rot_deg=(82, 0, 42),
        lens=75
    )
    
    # Cut 3: 45°斜め上俯瞰（液面のメニスカスとコルク栓、金具）
    render_cut(
        os.path.join(assets_dir, "magic_potion_cut3.png"),
        pos=(1.5, -1.8, 2.2),
        rot_deg=(55, 0, 38),
        lens=45
    )
    
    # Cut 4: 注ぎ口とコルク栓のローアングル
    render_cut(
        os.path.join(assets_dir, "magic_potion_cut4.png"),
        pos=(1.6, -1.2, 1.75),
        rot_deg=(88, 0, 52),
        lens=40
    )

if __name__ == "__main__":
    main()
