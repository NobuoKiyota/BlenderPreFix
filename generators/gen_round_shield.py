import bpy
import bmesh
import math
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

# 1. PBR マテリアル
def create_wood_mat():
    mat = bpy.data.materials.new(name="M_Shield_Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.35, 0.22, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.72
    
    # 縦方向アッシュ木目ノイズ
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 30.0
    tex_noise.inputs['Detail'].default_value = 5.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.28
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Wood_Medium"
    mat["audio_tag"] = "Sound_Shield_Wood_Block"
    return mat

def create_iron_mat():
    mat = bpy.data.materials.new(name="M_Shield_Iron")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.14, 0.15, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.35
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Heavy"
    mat["audio_tag"] = "Sound_Shield_Iron_Deflect"
    return mat

def create_leather_mat():
    mat = bpy.data.materials.new(name="M_Shield_Leather")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.24, 0.13, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Fabric_Leather"
    mat["audio_tag"] = "Sound_Shield_Equip"
    return mat

def build_shield():
    wood = create_wood_mat()
    iron = create_iron_mat()
    leather = create_leather_mat()
    
    # 1. 盾本体ディスク (#001 ~ #007)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.03, vertices=48, location=(0, 0, 0.7))
    shield = bpy.context.active_object
    shield.name = "Shield_Body"
    shield.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    shield.data.materials.append(wood)
    
    # ドーム状に前方にわずかに湾曲
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(shield.data)
    for v in bm.verts:
        dist = math.sqrt(v.co.x**2 + (v.co.z - 0.7)**2)
        curve = max(0, 0.55 - dist) * 0.08
        if v.co.y < 0:
            v.co.y -= curve
        else:
            v.co.y += curve * 0.5
    bmesh.update_edit_mesh(shield.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bev = shield.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.005
    bev.segments = 2
    
    # 2. 外周鉄リム (#011)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.02, location=(0, 0, 0.7))
    rim = bpy.context.active_object
    rim.name = "Shield_Iron_Rim"
    rim.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    rim.data.materials.append(iron)
    
    # 3. 中央ボス (Umbo #008 ~ #010)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, -0.04, 0.7))
    boss = bpy.context.active_object
    boss.name = "Shield_Boss"
    boss.scale = (1.0, 0.7, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    boss.data.materials.append(iron)
    
    # ボス外周フランジ (Torus)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.015, location=(0, -0.02, 0.7))
    flange = bpy.context.active_object
    flange.name = "Shield_Boss_Flange"
    flange.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    flange.data.materials.append(iron)
    
    # 4. リベット (外周16個 ＋ ボス6個 #012 ~ #013)
    for i in range(16):
        angle = i * (2 * math.pi / 16)
        x = 0.52 * math.cos(angle)
        z = 0.7 + 0.52 * math.sin(angle)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(x, -0.02, z))
        riv = bpy.context.active_object
        riv.data.materials.append(iron)
        
    for i in range(6):
        angle = i * (2 * math.pi / 6)
        x = 0.15 * math.cos(angle)
        z = 0.7 + 0.15 * math.sin(angle)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, location=(x, -0.03, z))
        riv = bpy.context.active_object
        riv.data.materials.append(iron)

    # 5. 裏面ハンドル ＆ 革ストラップ (#014 ~ #016)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.36, vertices=16, location=(0, 0.04, 0.7))
    handle = bpy.context.active_object
    handle.name = "Shield_Handle"
    handle.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    handle.data.materials.append(wood)
    
    # 革ストラップ
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.14, 0.04, 0.7))
    strap = bpy.context.active_object
    strap.name = "Shield_Arm_Strap"
    strap.scale = (0.05, 0.01, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    strap.data.materials.append(leather)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.8, 2.5))
    key = bpy.context.active_object
    key.data.energy = 220
    key.data.size = 2.0
    key.rotation_euler = (math.radians(55), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.4, -1.8, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 80
    fill.data.size = 2.5
    fill.data.color = (0.8, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.5, 2.2))
    rim = bpy.context.active_object
    rim.data.energy = 190
    rim.data.spot_size = math.radians(65)
    rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.06, 0.07, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.5
    floor.data.materials.append(fmat)

def setup_camera(pos, rot_deg, lens=50):
    bpy.ops.object.camera_add(location=pos)
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    cam.data.lens = lens
    bpy.context.scene.camera = cam
    return cam

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
    build_shield()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "round_shield.glb")
    for obj in bpy.data.objects:
        if "Studio_Floor" in obj.name:
            obj.select_set(False)
        else:
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"Exported GLB: {glb_path}")
    
    render_cut(os.path.join(assets_dir, "round_shield_cut1.png"), (1.8, -2.4, 1.1), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "round_shield.png"), (1.8, -2.4, 1.1), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "round_shield_cut2.png"), (0.5, -1.2, 0.72), (78, 0, 24), 70)
    render_cut(os.path.join(assets_dir, "round_shield_cut3.png"), (1.4, -1.8, 1.8), (55, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "round_shield_cut4.png"), (1.6, -1.2, 0.4), (88, 0, 52), 40)

if __name__ == "__main__":
    main()
