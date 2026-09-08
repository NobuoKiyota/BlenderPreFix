import bpy
import bmesh
import math
import random
import sys
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

def create_crystal_material():
    mat = bpy.data.materials.new(name='Crystal_Gem_Mat')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['IOR'].default_value = 1.544
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.92
        
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (0.1, 0.5, 0.9, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.8
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (0.1, 0.5, 0.9, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.8
        
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat['surface_type'] = 'Crystal'
    mat['audio_tag'] = 'Footstep_Glass'
    return mat

def create_rock_material():
    mat = bpy.data.materials.new(name='Base_Rock_Mat')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.13, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 12.0
    tex_noise.inputs['Detail'].default_value = 4.0
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.1
    
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    mat['surface_type'] = 'Stone'
    mat['audio_tag'] = 'Footstep_Stone'
    return mat

def create_single_crystal(name='CrystalPrism', height=2.0, radius=0.3, tip_ratio=0.3):
    bm = bmesh.new()
    segments = 6
    angles = [i * (2 * math.pi / segments) for i in range(segments)]
    
    bottom_verts = [bm.verts.new((radius * math.cos(a), radius * math.sin(a), 0)) for a in angles]
    column_height = height * (1.0 - tip_ratio)
    mid_verts = [bm.verts.new((radius * math.cos(a) * 0.95, radius * math.sin(a) * 0.95, column_height)) for a in angles]
    top_vert = bm.verts.new((radius * 0.1, radius * 0.05, height))
    
    bm.faces.new(reversed(bottom_verts))
    for i in range(segments):
        i_next = (i + 1) % segments
        bm.faces.new([bottom_verts[i], bottom_verts[i_next], mid_verts[i_next], mid_verts[i]])
    for i in range(segments):
        i_next = (i + 1) % segments
        bm.faces.new([mid_verts[i], mid_verts[i_next], top_vert])
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def generate_crystal_cluster(seed=42, crystal_count=12):
    random.seed(seed)
    crystal_mat = create_crystal_material()
    rock_mat = create_rock_material()
    
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, -0.6))
    rock_obj = bpy.context.active_object
    rock_obj.name = 'Crystal_Base_Rock'
    rock_obj.scale = (1.4, 1.2, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    
    subsurf = rock_obj.modifiers.new(name='Subsurf', type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    
    disp = rock_obj.modifiers.new(name='Displace', type='DISPLACE')
    tex = bpy.data.textures.new('RockNoise', type='VORONOI')
    tex.noise_scale = 0.8
    disp.texture = tex
    disp.strength = 0.35
    
    rock_obj.data.materials.append(rock_mat)
    
    crystal_objs = []
    main_c = create_single_crystal('Crystal_Main', height=3.2, radius=0.45, tip_ratio=0.35)
    main_c.rotation_euler = (math.radians(8), math.radians(-10), math.radians(25))
    main_c.location = (0, 0, -0.2)
    main_c.data.materials.append(crystal_mat)
    crystal_objs.append(main_c)
    
    for i in range(crystal_count):
        angle = (2 * math.pi / crystal_count) * i + random.uniform(-0.3, 0.3)
        dist = random.uniform(0.5, 1.3)
        x = math.cos(angle) * dist
        y = math.sin(angle) * dist
        h = random.uniform(1.2, 2.4)
        r = random.uniform(0.18, 0.32)
        
        c = create_single_crystal(f'Crystal_Sub_{i+1}', height=h, radius=r, tip_ratio=random.uniform(0.25, 0.4))
        tilt = random.uniform(15, 35)
        c.rotation_euler = (
            math.radians(math.sin(angle) * tilt + random.uniform(-10, 10)),
            math.radians(-math.cos(angle) * tilt + random.uniform(-10, 10)),
            random.uniform(0, 6.28)
        )
        c.location = (x, y, -0.3 + random.uniform(0, 0.2))
        c.data.materials.append(crystal_mat)
        crystal_objs.append(c)
        
    bpy.ops.object.select_all(action='DESELECT')
    for obj in crystal_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = crystal_objs[0]
    bpy.ops.object.join()
    combined_crystal = bpy.context.active_object
    combined_crystal.name = 'Crystal_Formation'
    
    for poly in combined_crystal.data.polygons:
        poly.use_smooth = False
        
    return combined_crystal, rock_obj

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new(name='Cam')
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new(name='Cam', object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (3.8, -4.2, 3.0)
    cam_obj.rotation_euler = (math.radians(64), 0, math.radians(42))
    bpy.context.scene.camera = cam_obj
    
    light_key = bpy.data.lights.new(name='Light_Key', type='SUN')
    light_key.energy = 3.5
    light_key.color = (1.0, 0.95, 0.9)
    light_key_obj = bpy.data.objects.new(name='Light_Key', object_data=light_key)
    bpy.context.collection.objects.link(light_key_obj)
    light_key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))
    
    light_rim = bpy.data.lights.new(name='Light_Rim', type='POINT')
    light_rim.energy = 250.0
    light_rim.color = (0.3, 0.8, 1.0)
    light_rim_obj = bpy.data.objects.new(name='Light_Rim', object_data=light_rim)
    bpy.context.collection.objects.link(light_rim_obj)
    light_rim_obj.location = (-2.5, 2.0, 3.0)

def main():
    clear_scene()
    crystal, rock = generate_crystal_cluster(seed=77, crystal_count=10)
    setup_camera_and_lighting()
    
    args = sys.argv
    export_glb = None
    render_png = None
    if '--export-glb' in args:
        export_glb = args[args.index('--export-glb') + 1]
    if '--render-png' in args:
        render_png = args[args.index('--render-png') + 1]
        
    if export_glb:
        os.makedirs(os.path.dirname(os.path.abspath(export_glb)), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(
            filepath=export_glb,
            export_format='GLB',
            use_selection=False,
            export_materials='EXPORT',
            export_apply=True
        )
        print(f'Successfully exported GLB: {export_glb}')
        
    if render_png:
        os.makedirs(os.path.dirname(os.path.abspath(render_png)), exist_ok=True)
        scene = bpy.context.scene
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = render_png
        scene.render.resolution_x = 800
        scene.render.resolution_y = 600
        # 繝ｬ繝ｳ繝繝ｩ繝ｼ險ｭ螳・
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 32
        scene.cycles.device = 'CPU'
        bpy.ops.render.render(write_still=True)
        print(f'Successfully rendered PNG: {render_png}')

if __name__ == '__main__':
    main()


