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
def create_armor_mat():
    mat = bpy.data.materials.new(name="M_Barrel_Armor")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 重厚な警告イエロー〜オリーブドラブ
    bsdf.inputs['Base Color'].default_value = (0.85, 0.55, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.35
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 60.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.1
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Metal_Heavy"
    mat["audio_tag"] = "Sound_SciFi_Barrel_Hit"
    return mat

def create_plasma_mat():
    mat = bpy.data.materials.new(name="M_Barrel_Plasma")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.3, 0.02, 1.0)
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.4, 0.05, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 10.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.4, 0.05, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 10.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "SciFi_Energy"
    mat["audio_tag"] = "Sound_Plasma_Core_Loop"
    return mat

def create_rubber_mat():
    mat = bpy.data.materials.new(name="M_Barrel_Rubber")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Rubber_Synthetic"
    mat["audio_tag"] = "Sound_Rubber_Gasket"
    return mat

def create_dark_metal_mat():
    mat = bpy.data.materials.new(name="M_Barrel_DarkMetal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.15, 0.16, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Heavy"
    mat["audio_tag"] = "Sound_Bolt_Tighten"
    return mat

def build_barrel():
    armor = create_armor_mat()
    plasma = create_plasma_mat()
    rubber = create_rubber_mat()
    dark_metal = create_dark_metal_mat()
    
    # 1. バレル外殻本体 (#001 ~ #003)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.45, depth=1.1, location=(0, 0, 0.6))
    body = bpy.context.active_object
    body.name = "Barrel_Body"
    body.data.materials.append(armor)
    
    bev = body.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.008
    bev.segments = 2
    
    # 2. 上下保護バンパー (ラバーリング #004)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.48, depth=0.12, location=(0, 0, 1.1))
    top_bumper = bpy.context.active_object
    top_bumper.name = "Top_Bumper"
    top_bumper.data.materials.append(rubber)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.48, depth=0.12, location=(0, 0, 0.1))
    bot_bumper = bpy.context.active_object
    bot_bumper.name = "Bottom_Bumper"
    bot_bumper.data.materials.append(rubber)
    
    # 3. プラズマ発光コアウィンドウ (4箇所 #005 ~ #007)
    for i in range(4):
        ang = i * (math.pi / 2)
        x = 0.44 * math.cos(ang)
        y = 0.44 * math.sin(ang)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 0.6))
        slit = bpy.context.active_object
        slit.name = f"Plasma_Slit_{i}"
        slit.scale = (0.06, 0.06, 0.45)
        slit.rotation_euler = (0, 0, ang)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        slit.data.materials.append(plasma)

    # 4. 六角ボルト (各8本 #008 ~ #009)
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        x = 0.45 * math.cos(ang)
        y = 0.45 * math.sin(ang)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.018, depth=0.02, location=(x, y, 1.16))
        bolt = bpy.context.active_object
        bolt.data.materials.append(dark_metal)

    # 5. 上部バルブハッチ ＆ 圧力逃がしハンドル (#010 ~ #011)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.18, depth=0.06, location=(0, 0, 1.18))
    hatch = bpy.context.active_object
    hatch.name = "Hatch_Cover"
    hatch.data.materials.append(dark_metal)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.06, minor_radius=0.012, location=(0, 0, 1.24))
    valve = bpy.context.active_object
    valve.name = "Pressure_Valve"
    valve.data.materials.append(dark_metal)
    
    # 6. 圧力計ゲージ (#012 ~ #013)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.06, depth=0.04, location=(0, -0.46, 0.85))
    gauge = bpy.context.active_object
    gauge.name = "Pressure_Gauge"
    gauge.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    gauge.data.materials.append(dark_metal)
    
    # ゲージ内面（発光）
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.05, depth=0.01, location=(0, -0.485, 0.85))
    dial = bpy.context.active_object
    dial.name = "Gauge_Dial"
    dial.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    dial.data.materials.append(plasma)

    # 7. 内部プラズマ点光源 (#014)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.6))
    plit = bpy.context.active_object
    plit.data.energy = 250
    plit.data.color = (1.0, 0.45, 0.08)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.5, -2.8, 2.8))
    key = bpy.context.active_object
    key.data.energy = 220
    key.data.size = 2.0
    key.rotation_euler = (math.radians(52), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -1.8, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 70
    fill.data.size = 2.5
    fill.data.color = (0.75, 0.85, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.5, 2.5))
    rim = bpy.context.active_object
    rim.data.energy = 180
    rim.data.spot_size = math.radians(65)
    rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.06, 0.07, 1.0)
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
    build_barrel()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "plasma_barrel.glb")
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
    
    render_cut(os.path.join(assets_dir, "plasma_barrel_cut1.png"), (2.2, -2.6, 1.4), (70, 0, 40), 50)
    render_cut(os.path.join(assets_dir, "plasma_barrel.png"), (2.2, -2.6, 1.4), (70, 0, 40), 50)
    render_cut(os.path.join(assets_dir, "plasma_barrel_cut2.png"), (0.5, -1.2, 0.85), (78, 0, 24), 70)
    render_cut(os.path.join(assets_dir, "plasma_barrel_cut3.png"), (1.8, -1.8, 2.4), (52, 0, 45), 45)
    render_cut(os.path.join(assets_dir, "plasma_barrel_cut4.png"), (2.0, -1.5, 0.5), (86, 0, 52), 40)

if __name__ == "__main__":
    main()
