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
def create_brass_mat():
    mat = bpy.data.materials.new(name="M_Compass_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.88, 0.72, 0.28, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.25
    
    # 旋盤の同心円微小ヘアラインノイズ
    tex = nodes.new(type='ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 80.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.05
    links.new(tex.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Metal_Light"
    mat["audio_tag"] = "Sound_Brass_Click"
    return mat

def create_needle_n_mat():
    mat = bpy.data.materials.new(name="M_Compass_Needle_N")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.08, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.6
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Light"
    mat["audio_tag"] = "Sound_Needle_Jiggle"
    return mat

def create_needle_s_mat():
    mat = bpy.data.materials.new(name="M_Compass_Needle_S")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.32, 0.65, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.7
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Light"
    mat["audio_tag"] = "Sound_Needle_Jiggle"
    return mat

def create_dial_mat():
    mat = bpy.data.materials.new(name="M_Compass_Dial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 0.82, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Ceramic_Paper"
    mat["audio_tag"] = "Sound_Compass_Open"
    return mat

def create_glass_mat():
    mat = bpy.data.materials.new(name="M_Compass_Glass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.98, 0.99, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.52
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 1.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Glass"
    mat["audio_tag"] = "Sound_Glass_Tap_Sharp"
    return mat

def build_compass():
    brass = create_brass_mat()
    needle_n = create_needle_n_mat()
    needle_s = create_needle_s_mat()
    dial_mat = create_dial_mat()
    glass = create_glass_mat()
    
    # 1. 真鍮ケース本体 (#001 ~ #004)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.25, depth=0.08, location=(0, 0, 0.04))
    case = bpy.context.active_object
    case.name = "Compass_Case"
    case.data.materials.append(brass)
    
    # 内部キャビティをインセット＋押し込み
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(case.data)
    top_face = max(bm.faces, key=lambda f: f.normal.z)
    res = bmesh.ops.inset_individual(bm, faces=[top_face], thickness=0.025, depth=-0.045)
    bmesh.update_edit_mesh(case.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bev = case.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.005
    bev.segments = 2
    
    # 2. 文字盤プレート (#005 ~ #006)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.22, depth=0.005, location=(0, 0, 0.025))
    dial = bpy.context.active_object
    dial.name = "Compass_Dial"
    dial.data.materials.append(dial_mat)
    
    # 方位マーカー（星型羅針図 8方向）
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        rad = 0.16
        x = rad * math.cos(ang)
        y = rad * math.sin(ang)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 0.028))
        pt = bpy.context.active_object
        pt.scale = (0.012, 0.012, 0.002)
        pt.rotation_euler = (0, 0, ang + math.pi/4)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        pt.data.materials.append(brass)
    
    # 3. 中央ピボット軸 (#007)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.012, depth=0.035, location=(0, 0, 0.04))
    pivot = bpy.context.active_object
    pivot.name = "Compass_Pivot"
    pivot.data.materials.append(brass)
    
    # 4. 磁針 (北・南 #008 ~ #013)
    # 北針 (赤)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.024, depth=0.17, location=(0, 0.09, 0.045))
    needle_north = bpy.context.active_object
    needle_north.name = "Needle_North"
    needle_north.scale = (1.0, 1.0, 0.12)
    needle_north.rotation_euler = (math.radians(-90), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    needle_north.data.materials.append(needle_n)
    
    # 南針 (青)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.024, depth=0.17, location=(0, -0.09, 0.045))
    needle_south = bpy.context.active_object
    needle_south.name = "Needle_South"
    needle_south.scale = (1.0, 1.0, 0.12)
    needle_south.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    needle_south.data.materials.append(needle_s)
    
    # 5. ガラス風防カバー (#014 ~ #015)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.222, depth=0.006, location=(0, 0, 0.065))
    gcover = bpy.context.active_object
    gcover.name = "Compass_Glass_Cover"
    gcover.data.materials.append(glass)
    
    # 6. 上部吊り下げリング (#016 ~ #017)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.009, location=(0, 0.28, 0.04))
    ring = bpy.context.active_object
    ring.name = "Compass_Ring"
    ring.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    ring.data.materials.append(brass)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(1.8, -2.2, 2.2))
    key = bpy.context.active_object
    key.data.energy = 160
    key.data.size = 1.8
    key.rotation_euler = (math.radians(52), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.0, -1.5, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 60
    fill.data.size = 2.0
    fill.data.color = (0.85, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.0, 2.0))
    rim = bpy.context.active_object
    rim.data.energy = 160
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
        bsdf.inputs['Roughness'].default_value = 0.45
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
    build_compass()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "brass_compass.glb")
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
    
    render_cut(os.path.join(assets_dir, "brass_compass_cut1.png"), (1.2, -1.5, 1.2), (55, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "brass_compass.png"), (1.2, -1.5, 1.2), (55, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "brass_compass_cut2.png"), (0.3, -0.6, 0.6), (62, 0, 26), 75)
    render_cut(os.path.join(assets_dir, "brass_compass_cut3.png"), (0.01, -0.01, 1.5), (0, 0, 0), 50)
    render_cut(os.path.join(assets_dir, "brass_compass_cut4.png"), (1.1, -0.9, 0.25), (82, 0, 50), 40)

if __name__ == "__main__":
    main()
