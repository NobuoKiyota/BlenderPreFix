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

def create_wood_material():
    mat = bpy.data.materials.new(name="Charred_Wood_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.03, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat["surface_type"] = "Wood"
    mat["audio_tag"] = "Footstep_Wood_Charred"
    return mat

def create_flame_material():
    mat = bpy.data.materials.new(name="Stylized_Flame_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # 鮮やかなスタイライズド炎の発光
    bsdf.inputs['Base Color'].default_value = (1.0, 0.35, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.2
    
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.45, 0.05, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 3.5
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.45, 0.05, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 3.5
        
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat["surface_type"] = "Fire"
    mat["audio_tag"] = "Sound_Campfire_Loop"
    return mat

def create_spark_material():
    mat = bpy.data.materials.new(name="Spark_Emission_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.8, 0.1, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 8.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.8, 0.1, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 8.0
        
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat["surface_type"] = "Fire"
    mat["audio_tag"] = "Sound_Ember_Crack"
    return mat

def generate_campfire(seed=42):
    random.seed(seed)
    wood_mat = create_wood_material()
    flame_mat = create_flame_material()
    spark_mat = create_spark_material()
    
    # 1. 薪（Logs）の生成
    log_count = 6
    log_objs = []
    for i in range(log_count):
        angle = (2 * math.pi / log_count) * i + random.uniform(-0.2, 0.2)
        tilt = random.uniform(15, 25)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12, 
            depth=1.6, 
            location=(math.cos(angle)*0.45, math.sin(angle)*0.45, 0.25)
        )
        log = bpy.context.active_object
        log.name = f"Campfire_Log_{i+1}"
        log.rotation_euler = (
            math.radians(math.sin(angle) * tilt + random.uniform(-5, 5)),
            math.radians(-math.cos(angle) * tilt + random.uniform(-5, 5)),
            angle + math.pi/2
        )
        log.data.materials.append(wood_mat)
        log_objs.append(log)
        
    bpy.ops.object.select_all(action='DESELECT')
    for obj in log_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = log_objs[0]
    bpy.ops.object.join()
    combined_logs = bpy.context.active_object
    combined_logs.name = "Campfire_Wood_Logs"
    
    # 2. スタイライズド炎（Flame Mesh）
    # 円錐をベースに変形
    bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0.02, depth=1.5, location=(0, 0, 0.85))
    flame_main = bpy.context.active_object
    flame_main.name = "Campfire_Flame_Core"
    
    subsurf = flame_main.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    
    disp = flame_main.modifiers.new(name="Displace", type='DISPLACE')
    tex = bpy.data.textures.new("FlameNoise", type='CLOUDS')
    tex.noise_scale = 0.5
    disp.texture = tex
    disp.strength = 0.25
    flame_main.data.materials.append(flame_mat)
    
    # 小さな揺らめく炎のツイン
    bpy.ops.mesh.primitive_cone_add(radius1=0.28, radius2=0.02, depth=1.1, location=(0.15, -0.1, 0.7))
    flame_sub = bpy.context.active_object
    flame_sub.name = "Campfire_Flame_Sub"
    flame_sub.rotation_euler = (math.radians(10), math.radians(-15), 0)
    flame_sub.data.materials.append(flame_mat)
    
    # 3. 火の粉（Sparks）
    spark_objs = []
    for i in range(16):
        sz = random.uniform(0.02, 0.05)
        pos = (
            random.uniform(-0.4, 0.4),
            random.uniform(-0.4, 0.4),
            random.uniform(0.8, 2.2)
        )
        bpy.ops.mesh.primitive_ico_sphere_add(radius=sz, subdivisions=1, location=pos)
        sp = bpy.context.active_object
        sp.name = f"Spark_{i+1}"
        sp.data.materials.append(spark_mat)
        spark_objs.append(sp)
        
    bpy.ops.object.select_all(action='DESELECT')
    for obj in spark_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = spark_objs[0]
    bpy.ops.object.join()
    combined_sparks = bpy.context.active_object
    combined_sparks.name = "Campfire_Sparks"
    
    return combined_logs, flame_main, combined_sparks

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new(name='Cam')
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new(name='Cam', object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (2.8, -3.2, 1.8)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(40))
    bpy.context.scene.camera = cam_obj
    
    # 夜間環境光（少し青みのある暗い夜空）
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("NightWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.01, 0.015, 0.03, 1.0)
        bg.inputs['Strength'].default_value = 0.5
        
    # 焚き火自身の光源（ポイントライト）
    light_fire = bpy.data.lights.new(name='Light_Fire', type='POINT')
    light_fire.energy = 800.0
    light_fire.color = (1.0, 0.45, 0.1)
    light_fire_obj = bpy.data.objects.new(name='Light_Fire', object_data=light_fire)
    bpy.context.collection.objects.link(light_fire_obj)
    light_fire_obj.location = (0, 0, 0.8)

def main():
    clear_scene()
    generate_campfire(seed=101)
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
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 32
        scene.cycles.device = 'CPU'
        bpy.ops.render.render(write_still=True)
        print(f'Successfully rendered PNG: {render_png}')

if __name__ == '__main__':
    main()
