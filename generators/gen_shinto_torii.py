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
def create_vermilion_mat():
    mat = bpy.data.materials.new(name="M_Torii_Vermilion")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 魔除けの朱丹色（朱塗り）
    bsdf.inputs['Base Color'].default_value = (0.85, 0.14, 0.04, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 40.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Wood_Heavy"
    mat["audio_tag"] = "Sound_Wood_Temple_Resonance"
    return mat

def create_black_lacquer_mat():
    mat = bpy.data.materials.new(name="M_Torii_BlackLacquer")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Roughness'].default_value = 0.22
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Wood_Hard"
    mat["audio_tag"] = "Sound_Wood_Footstep_Deep"
    return mat

def create_stone_base_mat():
    mat = bpy.data.materials.new(name="M_Torii_StoneBase")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.38, 0.40, 0.42, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.90
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Stone"
    mat["audio_tag"] = "Sound_Stone_Base_Solid"
    return mat

def create_gold_mat():
    mat = bpy.data.materials.new(name="M_Torii_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.80, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_torii():
    vermilion = create_vermilion_mat()
    lacquer = create_black_lacquer_mat()
    stone = create_stone_base_mat()
    gold = create_gold_mat()
    
    # 1. 左右の台石（亀腹 #001）
    for side in [1, -1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.28, depth=0.18, location=(side * 1.25, 0, 0.09))
        base = bpy.context.active_object
        base.name = f"Torii_Kamebara_{'R' if side > 0 else 'L'}"
        base.data.materials.append(stone)
        bev = base.modifiers.new("Bevel", "BEVEL")
        bev.width = 0.02
        bev.segments = 2
        
    # 2. 左右の柱（内転び #003 ~ #005）
    for side in [1, -1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.18, depth=2.8, location=(side * 1.25, 0, 1.55))
        pillar = bpy.context.active_object
        pillar.name = f"Torii_Pillar_{'R' if side > 0 else 'L'}"
        # 内側へ2.5度傾斜（内転び）
        pillar.rotation_euler = (0, math.radians(-side * 2.5), 0)
        bpy.ops.object.transform_apply(rotation=True)
        pillar.data.materials.append(vermilion)
        
    # 3. 貫 (Nuki #006 ~ #007)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.15))
    nuki = bpy.context.active_object
    nuki.name = "Torii_Nuki"
    nuki.scale = (3.4, 0.14, 0.20)
    bpy.ops.object.transform_apply(scale=True)
    nuki.data.materials.append(vermilion)
    bev_n = nuki.modifiers.new("Bevel", "BEVEL")
    bev_n.width = 0.008
    bev_n.segments = 2
    
    # クサビ（左右貫の留め具）
    for side in [1, -1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.45, 0, 2.15))
        wedge = bpy.context.active_object
        wedge.scale = (0.04, 0.18, 0.26)
        bpy.ops.object.transform_apply(scale=True)
        wedge.data.materials.append(lacquer)
        
    # 4. 島木 (Shimaki #008 ~ #009)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.92))
    shimaki = bpy.context.active_object
    shimaki.name = "Torii_Shimaki"
    shimaki.scale = (3.7, 0.22, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    shimaki.data.materials.append(vermilion)
    
    # 5. 笠木 (Kasagi - 反り増し #010 ~ #014)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 3.10))
    kasagi = bpy.context.active_object
    kasagi.name = "Torii_Kasagi"
    kasagi.scale = (4.0, 0.28, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    kasagi.data.materials.append(lacquer)
    
    # 笠木と島木の両端を反り上がらせる
    for obj in [shimaki, kasagi]:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            bend = (v.co.x / 2.0)**2 * 0.14
            v.co.z += bend
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # 6. 額束 ＆ 神額 (#015 ~ #018)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.55))
    gakuzuka = bpy.context.active_object
    gakuzuka.name = "Torii_Gakuzuka"
    gakuzuka.scale = (0.16, 0.08, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    gakuzuka.data.materials.append(vermilion)
    
    # 神額
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 2.55))
    plaque = bpy.context.active_object
    plaque.name = "Torii_Plaque"
    plaque.scale = (0.34, 0.02, 0.46)
    bpy.ops.object.transform_apply(scale=True)
    plaque.data.materials.append(lacquer)
    
    # 額の金文字シンボル
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.01, location=(0, -0.075, 2.55))
    symbol = bpy.context.active_object
    symbol.name = "Torii_Gold_Crest"
    symbol.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    symbol.data.materials.append(gold)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(3.5, -4.5, 4.5))
    key = bpy.context.active_object
    key.data.energy = 320
    key.data.size = 3.5
    key.rotation_euler = (math.radians(50), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-3.5, -2.5, 2.5))
    fill = bpy.context.active_object
    fill.data.energy = 110
    fill.data.size = 4.0
    fill.data.color = (0.8, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 3.5, 4.0))
    rim = bpy.context.active_object
    rim.data.energy = 260
    rim.data.spot_size = math.radians(65)
    rim.rotation_euler = (math.radians(-50), 0, math.radians(180))

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
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
    build_torii()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "shinto_torii.glb")
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
    
    render_cut(os.path.join(assets_dir, "shinto_torii_cut1.png"), (3.8, -5.5, 2.5), (68, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "shinto_torii.png"), (3.8, -5.5, 2.5), (68, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "shinto_torii_cut2.png"), (0.8, -2.4, 2.6), (78, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "shinto_torii_cut3.png"), (2.6, -3.5, 4.2), (52, 0, 38), 45)
    render_cut(os.path.join(assets_dir, "shinto_torii_cut4.png"), (3.2, -3.2, 0.6), (86, 0, 48), 35)

if __name__ == "__main__":
    main()
