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
def create_cap_mat():
    mat = bpy.data.materials.new(name="M_Mushroom_Cap")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # エメラルド〜ターコイズブルーの半透明有機体
    bsdf.inputs['Base Color'].default_value = (0.05, 0.75, 0.65, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.4
        bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.8, 0.6)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.4
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Organic_Soft"
    mat["audio_tag"] = "Sound_Mushroom_Squish"
    return mat

def create_stem_mat():
    mat = bpy.data.materials.new(name="M_Mushroom_Stem")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.82, 0.92, 0.95, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Organic_Flesh"
    mat["audio_tag"] = "Sound_Fungi_Rustle"
    return mat

def create_glow_mat():
    mat = bpy.data.materials.new(name="M_Mushroom_Glow")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.1, 0.95, 0.85, 1.0)
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (0.1, 0.95, 0.85, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 6.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (0.1, 0.95, 0.85, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 6.0
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Magic_Light"
    mat["audio_tag"] = "Sound_Spore_Glow_Hum"
    return mat

def create_rock_mat():
    mat = bpy.data.materials.new(name="M_Cluster_Rock")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.14, 0.16, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 25.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Stone"
    mat["audio_tag"] = "Sound_Rock_Scrape"
    return mat

def build_single_mushroom(x, y, z_base, scale=1.0, tilt=(0, 0), cap_mat=None, stem_mat=None, glow_mat=None):
    # 茎
    stem_h = 0.45 * scale
    stem_r = 0.04 * scale
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=stem_r, depth=stem_h, location=(x, y, z_base + stem_h/2))
    stem = bpy.context.active_object
    stem.rotation_euler = (tilt[0], tilt[1], 0)
    stem.data.materials.append(stem_mat)
    
    # 傘 (鐘型)
    cap_r = 0.22 * scale
    cap_h = 0.14 * scale
    cap_z = z_base + stem_h * 0.95
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=cap_r, depth=cap_h, location=(x, y, cap_z))
    cap = bpy.context.active_object
    cap.rotation_euler = (tilt[0], tilt[1], 0)
    
    # 頂点をすぼめて鐘型化
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(cap.data)
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= 0.2
            v.co.y *= 0.2
            v.co.z += 0.04 * scale
        else:
            v.co.x *= 1.15
            v.co.y *= 1.15
    bmesh.update_edit_mesh(cap.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    sub = cap.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    cap.data.materials.append(cap_mat)
    
    # 傘表面の発光ドット
    for d in range(8):
        ang = d * (2 * math.pi / 8)
        rad = cap_r * 0.65
        dx = x + rad * math.cos(ang)
        dy = y + rad * math.sin(ang)
        dz = cap_z + 0.03 * scale
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008 * scale, location=(dx, dy, dz))
        dot = bpy.context.active_object
        dot.data.materials.append(glow_mat)
        
    # 傘直下の淡い自発光ライト
    bpy.ops.object.light_add(type='POINT', location=(x, y, cap_z - 0.02))
    lit = bpy.context.active_object
    lit.data.energy = 15 * scale
    lit.data.color = (0.1, 0.95, 0.8)

def build_scene():
    cap_mat = create_cap_mat()
    stem_mat = create_stem_mat()
    glow_mat = create_glow_mat()
    rock_mat = create_rock_mat()
    
    # 1. 苔岩ベース (#001 ~ #003)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.65, location=(0, 0, 0.2))
    rock = bpy.context.active_object
    rock.name = "Cluster_Rock_Base"
    rock.scale = (1.3, 1.0, 0.45)
    bpy.ops.object.transform_apply(scale=True)
    rock.data.materials.append(rock_mat)
    
    # 2. キノコ群生 (親株 + 子株4本)
    build_single_mushroom(0, 0, 0.35, scale=1.3, tilt=(0.08, -0.05), cap_mat=cap_mat, stem_mat=stem_mat, glow_mat=glow_mat)
    build_single_mushroom(-0.25, 0.15, 0.32, scale=0.85, tilt=(-0.12, 0.1), cap_mat=cap_mat, stem_mat=stem_mat, glow_mat=glow_mat)
    build_single_mushroom(0.28, -0.12, 0.30, scale=0.95, tilt=(0.15, 0.12), cap_mat=cap_mat, stem_mat=stem_mat, glow_mat=glow_mat)
    build_single_mushroom(0.12, 0.28, 0.28, scale=0.6, tilt=(-0.05, -0.18), cap_mat=cap_mat, stem_mat=stem_mat, glow_mat=glow_mat)
    build_single_mushroom(-0.22, -0.22, 0.25, scale=0.5, tilt=(0.18, -0.15), cap_mat=cap_mat, stem_mat=stem_mat, glow_mat=glow_mat)

def setup_lighting():
    # 洞窟のダークな環境光
    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.5, 2.5))
    key = bpy.context.active_object
    key.data.energy = 90
    key.data.size = 2.5
    key.data.color = (0.5, 0.6, 0.8)
    key.rotation_euler = (math.radians(50), 0, math.radians(42))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.0, -1.8, 1.5))
    fill = bpy.context.active_object
    fill.data.energy = 40
    fill.data.size = 3.0
    fill.data.color = (0.2, 0.4, 0.6)
    
    # 床
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.03, 0.04, 1.0)
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
    build_scene()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "glowing_mushrooms.glb")
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
    
    render_cut(os.path.join(assets_dir, "glowing_mushrooms_cut1.png"), (1.8, -2.2, 1.2), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "glowing_mushrooms.png"), (1.8, -2.2, 1.2), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "glowing_mushrooms_cut2.png"), (0.6, -1.0, 0.8), (78, 0, 30), 75)
    render_cut(os.path.join(assets_dir, "glowing_mushrooms_cut3.png"), (1.4, -1.5, 1.8), (55, 0, 42), 45)
    render_cut(os.path.join(assets_dir, "glowing_mushrooms_cut4.png"), (1.6, -1.1, 0.4), (88, 0, 52), 40)

if __name__ == "__main__":
    main()
