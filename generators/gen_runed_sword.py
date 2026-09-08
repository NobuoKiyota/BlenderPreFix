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
def create_steel_mat():
    mat = bpy.data.materials.new(name="M_Sword_Steel")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.22
    
    # 微細なヘアライン金属ノイズ
    tex = nodes.new(type='ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 120.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    links.new(tex.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Metal_Heavy"
    mat["audio_tag"] = "Sound_Sword_Clang"
    return mat

def create_rune_mat():
    mat = bpy.data.materials.new(name="M_Sword_Rune")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.6, 1.0, 1.0)
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (0.1, 0.75, 1.0, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 4.5
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (0.1, 0.75, 1.0, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 4.5
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Magic_Light"
    mat["audio_tag"] = "Sound_Rune_Hum"
    return mat

def create_leather_mat():
    mat = bpy.data.materials.new(name="M_Sword_Leather")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.22, 0.12, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Fabric_Leather"
    mat["audio_tag"] = "Sound_Leather_Grip"
    return mat

def create_gold_mat():
    mat = bpy.data.materials.new(name="M_Sword_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.76, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Metal_Light"
    mat["audio_tag"] = "Sound_Pommel_Strike"
    return mat

def build_sword():
    steel = create_steel_mat()
    rune = create_rune_mat()
    leather = create_leather_mat()
    gold = create_gold_mat()
    
    # 1. 刀身 (Blade: 1.1m 長)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.05))
    blade = bpy.context.active_object
    blade.name = "Sword_Blade"
    blade.scale = (0.09, 0.015, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    blade.data.materials.append(steel)
    blade.data.materials.append(rune)
    
    # 刃の先端尖らせ ＆ フラー溝のモデリング
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(blade.data)
    
    # 先端の頂点（Z最高部）を中央に寄せて切っ先化
    max_z = max(v.co.z for v in bm.verts)
    top_verts = [v for v in bm.verts if abs(v.co.z - max_z) < 0.05]
    for v in top_verts:
        v.co.x *= 0.1
        v.co.y *= 0.1
        v.co.z += 0.15
        
    bmesh.update_edit_mesh(blade.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bev = blade.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.004
    bev.segments = 2
    
    # 2. 刀身中央のルーン発光ストリップ（フラー内部）
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.95))
    fuller_rune = bpy.context.active_object
    fuller_rune.name = "Sword_Fuller_Rune"
    fuller_rune.scale = (0.016, 0.018, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    fuller_rune.data.materials.append(rune)
    
    # 3. 鍔 (Crossguard)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    guard = bpy.context.active_object
    guard.name = "Sword_Guard"
    guard.scale = (0.34, 0.045, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    guard.data.materials.append(gold)
    bev_g = guard.modifiers.new("Bevel", "BEVEL")
    bev_g.width = 0.006
    bev_g.segments = 2
    
    # 4. 柄 (Grip)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.26, vertices=20, location=(0, 0, 0.40))
    grip = bpy.context.active_object
    grip.name = "Sword_Grip"
    grip.data.materials.append(leather)
    
    # 革巻きのリングディテール
    for i in range(5):
        z_pos = 0.30 + i * 0.05
        bpy.ops.mesh.primitive_torus_add(major_radius=0.023, minor_radius=0.003, location=(0, 0, z_pos))
        ring = bpy.context.active_object
        ring.name = f"Grip_Ring_{i}"
        ring.data.materials.append(gold)
        
    # 5. ポメル (Pommel)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.05, vertices=8, location=(0, 0, 0.24))
    pommel = bpy.context.active_object
    pommel.name = "Sword_Pommel"
    pommel.data.materials.append(gold)
    bev_p = pommel.modifiers.new("Bevel", "BEVEL")
    bev_p.width = 0.008
    bev_p.segments = 2
    
    # ポメル中央の宝玉（ルーンコア）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(0, 0, 0.24))
    gem = bpy.context.active_object
    gem.name = "Pommel_Gem"
    gem.data.materials.append(rune)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.0, -2.5, 2.8))
    key = bpy.context.active_object
    key.data.energy = 200
    key.data.size = 2.0
    key.rotation_euler = (math.radians(55), 0, math.radians(40))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.0, -1.8, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 80
    fill.data.size = 2.5
    fill.data.color = (0.8, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.0, 2.5))
    rim = bpy.context.active_object
    rim.data.energy = 220
    rim.data.spot_size = math.radians(60)
    rim.rotation_euler = (math.radians(-50), 0, math.radians(180))

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
    build_sword()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "runed_sword.glb")
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
    
    # 4カットレンダリング
    render_cut(os.path.join(assets_dir, "runed_sword_cut1.png"), (1.8, -2.4, 1.3), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "runed_sword.png"), (1.8, -2.4, 1.3), (72, 0, 38), 50)
    render_cut(os.path.join(assets_dir, "runed_sword_cut2.png"), (0.6, -1.0, 0.7), (78, 0, 30), 75)
    render_cut(os.path.join(assets_dir, "runed_sword_cut3.png"), (1.2, -1.4, 1.9), (52, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "runed_sword_cut4.png"), (1.4, -1.2, 0.4), (88, 0, 50), 40)

if __name__ == "__main__":
    main()
