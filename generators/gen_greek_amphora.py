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
def create_clay_mat():
    mat = bpy.data.materials.new(name="M_Amphora_Clay")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 温かみのある素焼きテラコッタ
    bsdf.inputs['Base Color'].default_value = (0.65, 0.35, 0.20, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.82
    
    # 陶器の微細な砂粒・凹凸
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 55.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.22
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Ceramic"
    mat["audio_tag"] = "Sound_Pottery_Smash_Break"
    return mat

def create_glaze_mat():
    mat = bpy.data.materials.new(name="M_Amphora_Pattern")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 黒絵式の施釉（ブラック・グレーズ）
    bsdf.inputs['Base Color'].default_value = (0.10, 0.08, 0.07, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Ceramic_Glaze"
    mat["audio_tag"] = "Sound_Pottery_Slide"
    return mat

def build_amphora():
    clay = create_clay_mat()
    glaze = create_glaze_mat()
    
    # 1. アンフォラ本体（輪郭スピン成型）
    # 断面プロファイルを定義して Screw / Spin
    bm = bmesh.new()
    # (Radius, Z) のプロファイル座標
    profile = [
        (0.0, 0.0),
        (0.20, 0.0),      # 台座底
        (0.22, 0.06),     # 台座リム
        (0.12, 0.16),     # 足のくびれ
        (0.26, 0.32),     # 下部膨らみ
        (0.44, 0.58),     # 胴体最大径（肩）
        (0.38, 0.74),     # 肩の絞り
        (0.16, 0.88),     # 首
        (0.15, 1.05),     # 首上部
        (0.24, 1.12),     # 口縁フレア
        (0.21, 1.13),     # 内側リム
        (0.12, 1.05),     # 内側首
        (0.34, 0.70),     # 内側空洞
        (0.20, 0.35),     # 内側下部
        (0.0, 0.10)       # 内側底
    ]
    
    verts = [bm.verts.new((r, 0, z)) for r, z in profile]
    for i in range(len(verts) - 1):
        bm.edges.new((verts[i], verts[i+1]))
        
    mesh = bpy.data.meshes.new("Amphora_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    body = bpy.data.objects.new("Amphora_Body", mesh)
    bpy.context.collection.objects.link(body)
    bpy.context.view_layer.objects.active = body
    
    # スクリューモディファイアで360度回転ソリッド化
    screw = body.modifiers.new("Screw", "SCREW")
    screw.angle = math.radians(360)
    screw.steps = 36
    screw.render_steps = 36
    screw.use_smooth_shade = True
    
    sub = body.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    
    body.data.materials.append(clay)
    
    # 2. 双耳取っ手（ツインハンドル #010 ~ #013）
    for side in [1, -1]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.024, location=(side * 0.28, 0, 0.90))
        hnd = bpy.context.active_object
        hnd.name = f"Handle_{'R' if side > 0 else 'L'}"
        hnd.rotation_euler = (math.radians(90), 0, 0)
        hnd.scale = (0.7, 1.0, 1.4)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        hnd.data.materials.append(clay)
        
    # 3. 胴体中央の黒絵式装飾バンド
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.442, depth=0.15, location=(0, 0, 0.58))
    band = bpy.context.active_object
    band.name = "Amphora_Deco_Band"
    band.data.materials.append(glaze)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.5, -2.8, 3.0))
    key = bpy.context.active_object
    key.data.energy = 220
    key.data.size = 2.2
    key.rotation_euler = (math.radians(52), 0, math.radians(42))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -1.8, 2.0))
    fill = bpy.context.active_object
    fill.data.energy = 80
    fill.data.size = 2.5
    fill.data.color = (0.8, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.5, 2.6))
    rim = bpy.context.active_object
    rim.data.energy = 200
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
    build_amphora()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "greek_amphora.glb")
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
    
    render_cut(os.path.join(assets_dir, "greek_amphora_cut1.png"), (2.2, -2.8, 1.4), (70, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "greek_amphora.png"), (2.2, -2.8, 1.4), (70, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "greek_amphora_cut2.png"), (0.7, -1.2, 0.95), (78, 0, 30), 70)
    render_cut(os.path.join(assets_dir, "greek_amphora_cut3.png"), (1.4, -1.8, 2.2), (52, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "greek_amphora_cut4.png"), (1.8, -1.5, 0.4), (88, 0, 52), 40)

if __name__ == "__main__":
    main()
