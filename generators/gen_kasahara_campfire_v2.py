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
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)

# 1. マテリアル群
def create_charred_wood_material():
    mat = bpy.data.materials.new(name="Charred_Wood_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.025, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    
    # 炭化亀裂バンプ
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 35.0
    tex_noise.inputs['Detail'].default_value = 6.0
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.05
    
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Wood"
    mat["audio_tag"] = "Footstep_Wood_Charred"
    return mat

def create_fire_core_material():
    """炎の超高温・高輝度コア（白〜イエロー）"""
    mat = bpy.data.materials.new(name="Flame_Core_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.1
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.95, 0.6, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 12.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.95, 0.6, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 12.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_fire_outer_material():
    """炎の外郭・グラデーション（オレンジ〜クリムゾン赤）"""
    mat = bpy.data.materials.new(name="Flame_Outer_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.28, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.2
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.32, 0.02, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 5.5
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.32, 0.02, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 5.5
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_ember_spark_material():
    """舞い上がる火の粉（超高輝度イエローオレンジ）"""
    mat = bpy.data.materials.new(name="Ember_Spark_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.75, 0.1, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 25.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.75, 0.1, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 25.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_ground_ash_material():
    """焚き火台座の灰・地面"""
    mat = bpy.data.materials.new(name="Ash_Ground_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# 2. メッシュ生成
def create_organic_flame_mesh(name="Flame_Tongue", height=1.6, base_r=0.35, seed=42):
    """有機的にねじれて尖る炎の舌メッシュ"""
    random.seed(seed)
    bm = bmesh.new()
    layers = 10
    rad_steps = 12
    
    vert_rings = []
    for l in range(layers):
        h_ratio = l / (layers - 1)
        z = h_ratio * height
        # 先細り + 中腹が少し膨らむ teardrop / flame 形状
        r = base_r * (1.0 - h_ratio**1.2) * (1.0 + 0.3 * math.sin(h_ratio * math.pi))
        
        # 炎のねじれと揺らぎ
        twist_angle = h_ratio * 1.5
        offset_x = 0.15 * math.sin(h_ratio * math.pi * 1.5)
        offset_y = 0.1 * math.cos(h_ratio * math.pi * 1.2)
        
        ring = []
        for s in range(rad_steps):
            angle = s * (2 * math.pi / rad_steps) + twist_angle
            # 周囲の有機的なデコボコ
            local_r = r * (1.0 + 0.15 * math.sin(angle * 3.0 + h_ratio * 5.0))
            x = offset_x + local_r * math.cos(angle)
            y = offset_y + local_r * math.sin(angle)
            vert = bm.verts.new((x, y, z))
            ring.append(vert)
        vert_rings.append(ring)
        
    # 最上部の先端頂点
    top_v = bm.verts.new((offset_x * 1.2, offset_y * 1.2, height * 1.05))
    
    # 側面フェース
    for l in range(layers - 1):
        for s in range(rad_steps):
            s_next = (s + 1) % rad_steps
            v1 = vert_rings[l][s]
            v2 = vert_rings[l][s_next]
            v3 = vert_rings[l+1][s_next]
            v4 = vert_rings[l+1][s]
            bm.faces.new([v1, v2, v3, v4])
            
    # 先端トップ面の接続
    for s in range(rad_steps):
        s_next = (s + 1) % rad_steps
        bm.faces.new([vert_rings[-1][s], vert_rings[-1][s_next], top_v])
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # スムースシェード + 細分化モディファイア
    for p in mesh.polygons:
        p.use_smooth = True
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    return obj

def build_campfire_scene():
    wood_mat = create_charred_wood_material()
    core_mat = create_fire_core_material()
    outer_mat = create_fire_outer_material()
    spark_mat = create_ember_spark_material()
    ground_mat = create_ground_ash_material()
    
    # 地面（灰・炭のベース）
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=0.1, location=(0, 0, -0.05))
    ground = bpy.context.active_object
    ground.name = "Campfire_Ground_Bed"
    ground.data.materials.append(ground_mat)
    
    # 薪（6本、自然な角度でクロス配置）
    log_objs = []
    log_count = 6
    for i in range(log_count):
        angle = (2 * math.pi / log_count) * i + random.uniform(-0.15, 0.15)
        tilt = random.uniform(20, 28)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=random.uniform(0.09, 0.13), 
            depth=1.5, 
            location=(math.cos(angle)*0.45, math.sin(angle)*0.45, 0.28)
        )
        log = bpy.context.active_object
        log.name = f"Log_{i+1}"
        log.rotation_euler = (
            math.radians(math.sin(angle) * tilt),
            math.radians(-math.cos(angle) * tilt),
            angle + math.pi/2
        )
        log.data.materials.append(wood_mat)
        log_objs.append(log)
        
    bpy.ops.object.select_all(action='DESELECT')
    for obj in log_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = log_objs[0]
    bpy.ops.object.join()
    all_logs = bpy.context.active_object
    all_logs.name = "Campfire_Wood_Logs"
    
    # 炎（外郭・メイン炎、複数の揺らめく炎の束）
    flame_main = create_organic_flame_mesh("Flame_Main_Tongue", height=1.7, base_r=0.38, seed=12)
    flame_main.location = (0, 0, 0.15)
    flame_main.data.materials.append(outer_mat)
    
    flame_sub1 = create_organic_flame_mesh("Flame_Sub_Tongue1", height=1.3, base_r=0.25, seed=34)
    flame_sub1.location = (0.12, -0.08, 0.18)
    flame_sub1.rotation_euler = (math.radians(10), math.radians(-12), math.radians(45))
    flame_sub1.data.materials.append(outer_mat)
    
    flame_sub2 = create_organic_flame_mesh("Flame_Sub_Tongue2", height=1.1, base_r=0.22, seed=56)
    flame_sub2.location = (-0.1, 0.1, 0.16)
    flame_sub2.rotation_euler = (math.radians(-8), math.radians(15), math.radians(-60))
    flame_sub2.data.materials.append(outer_mat)
    
    # 炎の超高温コア（中心の白熱発光メッシュ）
    flame_core = create_organic_flame_mesh("Flame_White_Core", height=0.9, base_r=0.2, seed=78)
    flame_core.location = (0.02, 0.01, 0.22)
    flame_core.data.materials.append(core_mat)
    
    # 舞い上がる火の粉（Sparks）
    spark_objs = []
    for i in range(24):
        sz = random.uniform(0.015, 0.045)
        pos = (
            random.uniform(-0.4, 0.4),
            random.uniform(-0.4, 0.4),
            random.uniform(0.6, 2.4)
        )
        bpy.ops.mesh.primitive_ico_sphere_add(radius=sz, subdivisions=1, location=pos)
        sp = bpy.context.active_object
        sp.name = f"Spark_{i+1}"
        sp.data.materials.append(spark_mat)
        spark_objs.append(sp)
        
    bpy.ops.object.select_all(action='DESELECT')
    for sp in spark_objs:
        sp.select_set(True)
    bpy.context.view_layer.objects.active = spark_objs[0]
    bpy.ops.object.join()
    all_sparks = bpy.context.active_object
    all_sparks.name = "Campfire_Flying_Sparks"
    
    # 照明設定（暖色ポイントライトで周囲の薪と地面をドラマチックに照らす）
    light_fire = bpy.data.lights.new(name="Fire_Glow_Light", type='POINT')
    light_fire.energy = 850.0
    light_fire.color = (1.0, 0.42, 0.08)
    light_fire.shadow_soft_size = 0.35
    light_fire_obj = bpy.data.objects.new("Fire_Glow_Light", light_fire)
    bpy.context.collection.objects.link(light_fire_obj)
    light_fire_obj.location = (0, 0, 0.75)
    
    # 青暗い夜の環境光（リムライト）
    light_rim = bpy.data.lights.new(name="Night_Rim_Light", type='SUN')
    light_rim.energy = 0.4
    light_rim.color = (0.2, 0.35, 0.7)
    light_rim_obj = bpy.data.objects.new("Night_Rim_Light", light_rim)
    bpy.context.collection.objects.link(light_rim_obj)
    light_rim_obj.rotation_euler = (math.radians(65), math.radians(25), math.radians(-110))
    
    # ワールド背景（完全な暗闇）
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("NightWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.005, 0.008, 0.015, 1.0)
        bg.inputs['Strength'].default_value = 0.3
        
    return all_logs, flame_main, flame_sub1, flame_sub2, flame_core, all_sparks

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
    # カメラを削除して次へ
    bpy.data.objects.remove(cam, do_unlink=True)
    print(f"Rendered cut to: {filepath}")

def main():
    clear_scene()
    logs, f_main, f_s1, f_s2, f_core, sparks = build_campfire_scene()
    
    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. 3D GLB エクスポート（全オブジェクトを含める）
    glb_path = os.path.join(assets_dir, "kasahara_campfire.glb")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"Exported high quality GLB: {glb_path}")
    
    # 2. 4枚のマルチカットレンダリング
    # Cut 1: シネマティック全体像（正面やや斜め、ドラマチックな暖色と暗闇）
    render_cut(
        os.path.join(assets_dir, "kasahara_campfire_cut1.png"),
        pos=(2.5, -2.8, 1.4),
        rot_deg=(74, 0, 42),
        lens=45
    )
    # デフォルトのサムネイルにも Cut 1 をコピー保存
    render_cut(
        os.path.join(assets_dir, "kasahara_campfire.png"),
        pos=(2.5, -2.8, 1.4),
        rot_deg=(74, 0, 42),
        lens=45
    )
    
    # Cut 2: 炎のクローズアップ（火炎の有機的な舌と火の粉）
    render_cut(
        os.path.join(assets_dir, "kasahara_campfire_cut2.png"),
        pos=(1.3, -1.5, 0.9),
        rot_deg=(78, 0, 40),
        lens=65
    )
    
    # Cut 3: 斜め上からの俯瞰アングル（薪の組み方と火床構造が明瞭）
    render_cut(
        os.path.join(assets_dir, "kasahara_campfire_cut3.png"),
        pos=(1.8, -2.0, 2.5),
        rot_deg=(52, 0, 42),
        lens=40
    )
    
    # Cut 4: ローアングル・ドラマチックショット
    render_cut(
        os.path.join(assets_dir, "kasahara_campfire_cut4.png"),
        pos=(2.2, -1.8, 0.4),
        rot_deg=(85, 0, 50),
        lens=35
    )

if __name__ == "__main__":
    main()
