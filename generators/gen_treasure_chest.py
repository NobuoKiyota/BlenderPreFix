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

def create_wood_mat():
    mat = bpy.data.materials.new(name='M_Chest_Wood')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.28, 0.15, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 25.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat['surface_type'] = 'Wood_Heavy'
    mat['audio_tag'] = 'Sound_Wood_Chest_Impact'
    return mat

def create_iron_mat():
    mat = bpy.data.materials.new(name='M_Chest_Iron')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.13, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.42
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat['surface_type'] = 'Metal_Heavy'
    mat['audio_tag'] = 'Sound_Iron_Band_Hit'
    return mat

def create_brass_mat():
    mat = bpy.data.materials.new(name='M_Chest_Brass')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.28
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat['surface_type'] = 'Metal_Light'
    mat['audio_tag'] = 'Sound_Lock_Latch_Click'
    return mat

def build_chest():
    wood_mat = create_wood_mat()
    iron_mat = create_iron_mat()
    brass_mat = create_brass_mat()
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.35))
    body = bpy.context.active_object
    body.name = 'Chest_Body'
    body.scale = (1.4, 0.9, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(wood_mat)
    bev = body.modifiers.new('Bevel', 'BEVEL')
    bev.width = 0.02
    bev.segments = 2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.4, vertices=32, location=(0, 0, 0.7))
    lid = bpy.context.active_object
    lid.name = 'Chest_Lid'
    lid.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(lid.data)
    verts_to_del = [v for v in bm.verts if v.co.z < 0.7]
    bmesh.ops.delete(bm, geom=verts_to_del, context='VERTS')
    bmesh.ops.edgeloop_fill(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.update_edit_mesh(lid.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    lid.data.materials.append(wood_mat)
    bev_lid = lid.modifiers.new('Bevel', 'BEVEL')
    bev_lid.width = 0.015
    bev_lid.segments = 2
    
    for x_offset in [-0.55, 0.0, 0.55]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_offset, 0, 0.35))
        band = bpy.context.active_object
        band.name = f'Iron_Band_Body_{x_offset}'
        band.scale = (0.08, 0.93, 0.73)
        bpy.ops.object.transform_apply(scale=True)
        band.data.materials.append(iron_mat)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.465, depth=0.08, vertices=32, location=(x_offset, 0, 0.7))
        lid_band = bpy.context.active_object
        lid_band.name = f'Iron_Band_Lid_{x_offset}'
        lid_band.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(lid_band.data)
        verts_to_del = [v for v in bm.verts if v.co.z < 0.7]
        bmesh.ops.delete(bm, geom=verts_to_del, context='VERTS')
        bmesh.update_edit_mesh(lid_band.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        lid_band.data.materials.append(iron_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.47, 0.65))
    hasp = bpy.context.active_object
    hasp.name = 'Chest_Hasp'
    hasp.scale = (0.1, 0.03, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    hasp.data.materials.append(brass_mat)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.50, 0.52))
    padlock = bpy.context.active_object
    padlock.name = 'Padlock_Body'
    padlock.scale = (0.09, 0.04, 0.11)
    bpy.ops.object.transform_apply(scale=True)
    padlock.data.materials.append(brass_mat)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.009, location=(0, -0.50, 0.60))
    shackle = bpy.context.active_object
    shackle.name = 'Padlock_Shackle'
    shackle.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    shackle.data.materials.append(iron_mat)

    for x in [-0.55, 0.0, 0.55]:
        for z in [0.15, 0.35, 0.55]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x, -0.47, z))
            riv = bpy.context.active_object
            riv.data.materials.append(iron_mat)

def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2.5, -2.5, 3.0))
    key = bpy.context.active_object
    key.data.energy = 250
    key.data.size = 2.0
    key.rotation_euler = (math.radians(50), 0, math.radians(45))
    
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -1.5, 2.0))
    fill = bpy.context.active_object
    fill.data.energy = 90
    fill.data.size = 2.5
    fill.data.color = (0.85, 0.9, 1.0)
    
    bpy.ops.object.light_add(type='SPOT', location=(0, 2.5, 2.5))
    rim = bpy.context.active_object
    rim.data.energy = 200
    rim.data.spot_size = math.radians(65)
    rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor_mat = bpy.data.materials.new('Floor_Mat')
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.5
    floor.data.materials.append(floor_mat)

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
    print(f'Rendered cut to: {filepath}')

def main():
    clear_scene()
    build_chest()
    setup_lighting()
    
    assets_dir = 'e:/BlenderPreFix/catalog/assets'
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, 'treasure_chest.glb')
    for obj in bpy.data.objects:
        if 'Plane' in obj.name:
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
    print(f'Exported GLB: {glb_path}')
    
    render_cut(os.path.join(assets_dir, 'treasure_chest_cut1.png'), (2.2, -2.6, 1.6), (68, 0, 40), 50)
    render_cut(os.path.join(assets_dir, 'treasure_chest.png'), (2.2, -2.6, 1.6), (68, 0, 40), 50)
    render_cut(os.path.join(assets_dir, 'treasure_chest_cut2.png'), (0.6, -1.3, 0.8), (78, 0, 25), 70)
    render_cut(os.path.join(assets_dir, 'treasure_chest_cut3.png'), (1.8, -1.8, 2.4), (52, 0, 45), 45)
    render_cut(os.path.join(assets_dir, 'treasure_chest_cut4.png'), (2.0, -1.5, 0.6), (85, 0, 50), 40)

if __name__ == '__main__':
    main()
