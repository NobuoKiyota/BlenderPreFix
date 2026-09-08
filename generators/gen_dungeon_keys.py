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
def create_iron_mat():
    mat = bpy.data.materials.new(name="M_Key_ForgedIron")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.17, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.42
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 50.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Metal_Heavy"
    mat["audio_tag"] = "Sound_Key_Clink_Heavy"
    return mat

def create_brass_key_mat():
    mat = bpy.data.materials.new(name="M_Key_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.82, 0.65, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.32
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Light"
    mat["audio_tag"] = "Sound_Key_Jingle_Light"
    return mat

def create_single_key(name, bow_radius, shaft_len, bit_w, bit_h, loc, rot, mat):
    # 1. 軸 (Shaft)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.012, depth=shaft_len, location=(0, 0, -shaft_len/2))
    shaft = bpy.context.active_object
    shaft.name = f"{name}_Shaft"
    
    # 2. 頭部 (Bow)
    bpy.ops.mesh.primitive_torus_add(major_radius=bow_radius, minor_radius=0.008, location=(0, 0, 0))
    bow = bpy.context.active_object
    bow.name = f"{name}_Bow"
    bow.rotation_euler = (math.radians(90), 0, 0)
    
    # 3. 鍵山 (Bit)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bit_w/2, 0, -shaft_len + bit_h/2))
    bit = bpy.context.active_object
    bit.name = f"{name}_Bit"
    bit.scale = (bit_w, 0.012, bit_h)
    bpy.ops.object.transform_apply(scale=True)
    
    # ビットにスリット切り込みを入れる
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(bit.data)
    # 中央のフェイスを少し削る
    bmesh.ops.inset_individual(bm, faces=bm.faces, thickness=0.002, depth=-0.002)
    bmesh.update_edit_mesh(bit.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 結合して1つのキーにする
    bpy.ops.object.select_all(action='DESELECT')
    shaft.select_set(True)
    bow.select_set(True)
    bit.select_set(True)
    bpy.context.view_layer.objects.active = shaft
    bpy.ops.object.join()
    
    key = bpy.context.active_object
    key.name = name
    key.data.materials.append(mat)
    
    key.location = loc
    key.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
    
    bev = key.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.002
    bev.segments = 2
    return key

def build_keys():
    iron = create_iron_mat()
    brass = create_brass_key_mat()
    
    # 1. 大ホルダーリング (#001)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.012, location=(0, 0, 0.45))
    ring = bpy.context.active_object
    ring.name = "Dungeon_Key_Ring"
    ring.rotation_euler = (math.radians(85), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    ring.data.materials.append(iron)
    
    # 2. 鍵A (マスターキー / 大アイアンキー)
    key_a = create_single_key(
        name="Key_Master",
        bow_radius=0.045,
        shaft_len=0.36,
        bit_w=0.065,
        bit_h=0.075,
        loc=(0.02, -0.05, 0.45),
        rot=(15, -8, 20),
        mat=iron
    )
    
    # 3. 鍵B (牢獄牢名キー / 中アイアンキー)
    key_b = create_single_key(
        name="Key_Cell",
        bow_radius=0.038,
        shaft_len=0.28,
        bit_w=0.055,
        bit_h=0.060,
        loc=(-0.04, -0.03, 0.45),
        rot=(-10, 18, -15),
        mat=iron
    )
    
    # 4. 鍵C (宝物庫の鍵 / 小ブラスキー)
    key_c = create_single_key(
        name="Key_Treasure",
        bow_radius=0.032,
        shaft_len=0.22,
        bit_w=0.045,
        bit_h=0.050,
        loc=(0.06, 0.02, 0.45),
        rot=(5, 30, 45),
        mat=brass
    )

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.5, 2.5))
    key = bpy.context.active_object
    key.data.energy = 200
    key.data.size = 2.0
    key.rotation_euler = (math.radians(55), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.2, -1.8, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 70
    fill.data.size = 2.5
    fill.data.color = (0.8, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.2, 2.2))
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
    build_keys()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "dungeon_keys.glb")
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
    
    render_cut(os.path.join(assets_dir, "dungeon_keys_cut1.png"), (1.5, -2.0, 1.0), (70, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "dungeon_keys.png"), (1.5, -2.0, 1.0), (70, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "dungeon_keys_cut2.png"), (0.4, -0.9, 0.4), (78, 0, 24), 70)
    render_cut(os.path.join(assets_dir, "dungeon_keys_cut3.png"), (1.2, -1.4, 1.6), (55, 0, 42), 45)
    render_cut(os.path.join(assets_dir, "dungeon_keys_cut4.png"), (1.4, -1.0, 0.2), (86, 0, 52), 40)

if __name__ == "__main__":
    main()
