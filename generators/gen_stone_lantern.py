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
def create_stone_mat():
    mat = bpy.data.materials.new(name="M_Lantern_Stone")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.42, 0.43, 0.44, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    
    # 御影石の微細粒子ノイズ
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 45.0
    tex_noise.inputs['Detail'].default_value = 6.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Stone"
    mat["audio_tag"] = "Sound_Stone_Impact_Heavy"
    return mat

def create_moss_mat():
    mat = bpy.data.materials.new(name="M_Lantern_Moss")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.28, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Organic_Foliage"
    mat["audio_tag"] = "Sound_Moss_Brush"
    return mat

def create_flame_mat():
    mat = bpy.data.materials.new(name="M_Lantern_Flame")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.5, 0.1, 1.0)
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.45, 0.08, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 8.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.45, 0.08, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 8.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Fire_Soft"
    mat["audio_tag"] = "Sound_Candle_Flicker"
    return mat

def build_lantern():
    stone = create_stone_mat()
    moss = create_moss_mat()
    flame = create_flame_mat()
    
    # 1. 基礎 (Base #001)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.6, depth=0.22, location=(0, 0, 0.11))
    base = bpy.context.active_object
    base.name = "Lantern_Base"
    base.data.materials.append(stone)
    bev1 = base.modifiers.new("Bevel", "BEVEL")
    bev1.width = 0.02
    bev1.segments = 2
    
    # 2. 竿 (Post #003)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.24, depth=0.75, location=(0, 0, 0.58))
    post = bpy.context.active_object
    post.name = "Lantern_Post"
    post.data.materials.append(stone)
    
    # 3. 中台 (Middle Platform #005)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.54, depth=0.16, location=(0, 0, 1.02))
    chudai = bpy.context.active_object
    chudai.name = "Lantern_Chudai"
    chudai.data.materials.append(stone)
    chudai.data.materials.append(moss)
    
    # 4. 火袋 (Fire Box #007 - 窓付き)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.42, depth=0.45, location=(0, 0, 1.32))
    hibukuro = bpy.context.active_object
    hibukuro.name = "Lantern_Hibukuro"
    hibukuro.data.materials.append(stone)
    
    # 火袋の窓をインセット＋押し込み
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(hibukuro.data)
    side_faces = [f for f in bm.faces if abs(f.normal.z) < 0.2]
    for f in side_faces:
        bmesh.ops.inset_individual(bm, faces=[f], thickness=0.06, depth=-0.12)
    bmesh.update_edit_mesh(hibukuro.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 内部の蝋燭と炎 (#016, #017)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.035, depth=0.14, location=(0, 0, 1.22))
    candle = bpy.context.active_object
    candle.name = "Candle_Wax"
    cmat = bpy.data.materials.new("Candle_Wax_Mat")
    cmat.use_nodes = True
    cmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (0.9, 0.88, 0.8, 1.0)
    candle.data.materials.append(cmat)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(0, 0, 1.34))
    flame_obj = bpy.context.active_object
    flame_obj.name = "Candle_Flame"
    flame_obj.scale = (0.8, 0.8, 1.5)
    flame_obj.data.materials.append(flame)
    
    # 炎ポイントライト (#018)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 1.34))
    plight = bpy.context.active_object
    plight.data.energy = 80
    plight.data.color = (1.0, 0.65, 0.2)
    plight.data.shadow_soft_size = 0.05
    
    # 5. 笠 (Roof #010 - 六角反り屋根)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.88, depth=0.24, location=(0, 0, 1.66))
    kasa = bpy.context.active_object
    kasa.name = "Lantern_Kasa"
    kasa.data.materials.append(stone)
    kasa.data.materials.append(moss)
    
    # 笠のテーパー
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(kasa.data)
    top_faces = [f for f in bm.faces if f.normal.z > 0.8]
    for f in top_faces:
        for v in f.verts:
            v.co.x *= 0.42
            v.co.y *= 0.42
            v.co.z += 0.08
    bmesh.update_edit_mesh(kasa.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 6. 宝珠 (Jewel #014)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0, 0, 1.90))
    hoju = bpy.context.active_object
    hoju.name = "Lantern_Hoju"
    hoju.data.materials.append(stone)
    
    # 宝珠の先端尖り
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(hoju.data)
    top_v = max(bm.verts, key=lambda v: v.co.z)
    top_v.co.z += 0.07
    bmesh.update_edit_mesh(hoju.data)
    bpy.ops.object.mode_set(mode='OBJECT')

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.5, -2.8, 3.2))
    key = bpy.context.active_object
    key.data.energy = 220
    key.data.size = 2.5
    key.rotation_euler = (math.radians(52), 0, math.radians(42))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.8, -1.8, 2.0))
    fill = bpy.context.active_object
    fill.data.energy = 70
    fill.data.size = 3.0
    fill.data.color = (0.75, 0.85, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.8, 2.8))
    rim = bpy.context.active_object
    rim.data.energy = 200
    rim.data.spot_size = math.radians(65)
    rim.rotation_euler = (math.radians(-50), 0, math.radians(180))

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
    build_lantern()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "stone_lantern.glb")
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
    
    render_cut(os.path.join(assets_dir, "stone_lantern_cut1.png"), (2.8, -3.2, 1.8), (72, 0, 42), 50)
    render_cut(os.path.join(assets_dir, "stone_lantern.png"), (2.8, -3.2, 1.8), (72, 0, 42), 50)
    render_cut(os.path.join(assets_dir, "stone_lantern_cut2.png"), (1.1, -1.4, 1.35), (80, 0, 36), 75)
    render_cut(os.path.join(assets_dir, "stone_lantern_cut3.png"), (1.8, -2.0, 2.8), (52, 0, 42), 45)
    render_cut(os.path.join(assets_dir, "stone_lantern_cut4.png"), (2.2, -1.8, 0.6), (88, 0, 52), 40)

if __name__ == "__main__":
    main()
