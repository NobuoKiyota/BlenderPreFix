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
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)

def create_wood_material():
    mat = bpy.data.materials.new(name="Charred_Wood_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.025, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    # 炭化テクスチャバンプ
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 24.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    mat["surface_type"] = "Wood"
    mat["audio_tag"] = "Footstep_Wood_Charred"
    return mat

def create_kasahara_volume_material():
    """カサハラCG動画準拠の Principled Volume シェーダー"""
    mat = bpy.data.materials.new(name="Kasahara_Fire_Volume_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    volume = nodes.new(type='ShaderNodeVolumePrincipled')
    
    # 煙を消す（Density = 0）
    volume.inputs['Density'].default_value = 0.0
    
    # 1. Attribute ノード ("heat")
    attr_heat = nodes.new(type='ShaderNodeAttribute')
    attr_heat.attribute_name = "heat"
    
    # 2. 放射強度（Emission Strength）制御
    ramp_strength = nodes.new(type='ShaderNodeValToRGB')
    # 黒 -> 白 -> 濃いグレー
    ramp_strength.color_ramp.elements[0].position = 0.0
    ramp_strength.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_strength.color_ramp.elements[1].position = 0.45
    ramp_strength.color_ramp.elements[1].color = (1, 1, 1, 1)
    e3 = ramp_strength.color_ramp.elements.new(0.7)
    e3.color = (0.15, 0.15, 0.15, 1)
    
    math_mult1 = nodes.new(type='ShaderNodeMath')
    math_mult1.operation = 'MULTIPLY'
    math_mult1.inputs[1].default_value = 50.0
    
    # 3. ノイズテクスチャ + #frame ドライバ
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    # Z位置にドライバを付加（#frame）
    driver = mapping.inputs['Location'].driver_add('default_value', 2).driver
    driver.expression = "frame * 0.05"
    
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 8.0
    tex_noise.inputs['Detail'].default_value = 9.2
    tex_noise.inputs['Distortion'].default_value = 1.0
    
    ramp_noise = nodes.new(type='ShaderNodeValToRGB')
    ramp_noise.color_ramp.elements[0].position = 0.2
    ramp_noise.color_ramp.elements[1].position = 0.8
    
    math_mult2 = nodes.new(type='ShaderNodeMath')
    math_mult2.operation = 'MULTIPLY'
    
    # 4. 放射カラー（Emission Color）制御
    ramp_color = nodes.new(type='ShaderNodeValToRGB')
    ramp_color.color_ramp.elements[0].position = 0.1
    ramp_color.color_ramp.elements[0].color = (1.0, 0.25, 0.02, 1) # 炎オレンジ
    ramp_color.color_ramp.elements[1].position = 0.7
    ramp_color.color_ramp.elements[1].color = (1.0, 0.85, 0.1, 1)  # 炎イエロー
    
    # リンク接続
    links.new(attr_heat.outputs['Fac'], ramp_strength.inputs['Fac'])
    links.new(ramp_strength.outputs['Color'], math_mult1.inputs[0])
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_noise.inputs['Vector'])
    links.new(tex_noise.outputs['Fac'], ramp_noise.inputs['Fac'])
    
    links.new(math_mult1.outputs['Value'], math_mult2.inputs[0])
    links.new(ramp_noise.outputs['Color'], math_mult2.inputs[1])
    links.new(math_mult2.outputs['Value'], volume.inputs['Emission Strength'])
    
    links.new(attr_heat.outputs['Fac'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], volume.inputs['Emission Color'])
    
    links.new(volume.outputs['Volume'], output.inputs['Volume'])
    
    mat["surface_type"] = "Fire"
    mat["audio_tag"] = "Sound_Campfire_Loop"
    return mat

def build_kasahara_campfire():
    wood_mat = create_wood_material()
    volume_mat = create_kasahara_volume_material()
    
    # 1. 薪（Logs）配置
    log_count = 6
    log_objs = []
    for i in range(log_count):
        angle = (2 * math.pi / log_count) * i + random.uniform(-0.15, 0.15)
        tilt = random.uniform(18, 26)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.11, 
            depth=1.5, 
            location=(math.cos(angle)*0.4, math.sin(angle)*0.4, 0.22)
        )
        log = bpy.context.active_object
        log.name = f"Kasahara_Log_{i+1}"
        log.rotation_euler = (
            math.radians(math.sin(angle) * tilt),
            math.radians(-math.cos(angle) * tilt),
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
    
    # 2. 炎のエミッター球（UV Sphere, Scale 0.4）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 0.2))
    emitter = bpy.context.active_object
    emitter.name = "Fire_Emitter_Sphere"
    
    # 炎のフロー用テクスチャ（Clouds, Size: 0.1, Contrast: 5.0）
    tex_clouds = bpy.data.textures.new("FireCloudsTex", type='CLOUDS')
    tex_clouds.noise_scale = 0.1
    tex_clouds.contrast = 5.0
    
    # 物理演算: Fluid Flow (FIRE)
    mod_flow = emitter.modifiers.new(name="Fluid", type='FLUID')
    mod_flow.fluid_type = 'FLOW'
    mod_flow.flow_settings.flow_type = 'FIRE'
    mod_flow.flow_settings.flow_behavior = 'INFLOW'
    mod_flow.flow_settings.fuel_amount = 2.0
    mod_flow.flow_settings.surface_distance = 1.0
    mod_flow.flow_settings.use_texture = True
    mod_flow.flow_settings.noise_texture = tex_clouds
    
    # 3. 乱流フォースフィールド（Turbulence, Strength: 0.4, Noise: 0.4）
    bpy.ops.object.effector_add(type='TURBULENCE', location=(0, 0, 0.5))
    field = bpy.context.active_object
    field.name = "Fire_Turbulence"
    field.field.strength = 0.4
    field.field.noise = 0.4
    
    # 4. ドメイン（Domain: Box）
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.2))
    domain = bpy.context.active_object
    domain.name = "Fire_Domain_Gas"
    domain.scale = (1.8, 1.8, 2.4)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_domain = domain.modifiers.new(name="Fluid", type='FLUID')
    mod_domain.fluid_type = 'DOMAIN'
    mod_domain.domain_settings.domain_type = 'GAS'
    mod_domain.domain_settings.resolution_max = 64  # 高速自動テスト用 (本番は128)
    mod_domain.domain_settings.use_adaptive_domain = True
    mod_domain.domain_settings.vorticity = 0.1
    mod_domain.domain_settings.burning_rate = 1.0 # 反応速度
    mod_domain.domain_settings.cache_type = 'MODULAR'
    mod_domain.domain_settings.cache_frame_end = 200
    
    domain.data.materials.append(volume_mat)
    
    # 5. GLBエクスポート用スタイライズド炎コア（Webビューアでリアルタイム表示可能にするためのメッシュ）
    bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0.01, depth=1.4, location=(0, 0, 0.75))
    flame_proxy = bpy.context.active_object
    flame_proxy.name = "Fire_Visual_Proxy"
    sub = flame_proxy.modifiers.new(name="Sub", type='SUBSURF')
    sub.levels = 2
    disp = flame_proxy.modifiers.new(name="Disp", type='DISPLACE')
    disp.texture = tex_clouds
    disp.strength = 0.2
    
    # 炎プロキシマテリアル
    proxy_mat = bpy.data.materials.new(name="Fire_Stylized_Proxy_Mat")
    proxy_mat.use_nodes = True
    p_bsdf = proxy_mat.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (1.0, 0.4, 0.05, 1.0)
        if 'Emission Color' in p_bsdf.inputs:
            p_bsdf.inputs['Emission Color'].default_value = (1.0, 0.45, 0.05, 1.0)
            p_bsdf.inputs['Emission Strength'].default_value = 4.0
        elif 'Emission' in p_bsdf.inputs:
            p_bsdf.inputs['Emission'].default_value = (1.0, 0.45, 0.05, 1.0)
            p_bsdf.inputs['Emission Strength'].default_value = 4.0
    flame_proxy.data.materials.append(proxy_mat)
    
    return combined_logs, domain, flame_proxy

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new(name='Cam')
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new(name='Cam', object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (2.6, -3.0, 1.6)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(40))
    bpy.context.scene.camera = cam_obj
    
    # 夜間環境光
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("NightWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1.0)
        bg.inputs['Strength'].default_value = 0.5
        
    # 炎の照射光（ポイントライト）
    light = bpy.data.lights.new(name='Fire_Point_Light', type='POINT')
    light.energy = 600.0
    light.color = (1.0, 0.45, 0.1)
    light_obj = bpy.data.objects.new(name='Fire_Point_Light', object_data=light)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (0, 0, 0.7)

def main():
    clear_scene()
    logs, domain, proxy = build_kasahara_campfire()
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
        # GLB には薪と視覚プロキシメッシュを出力（ドメインのボクセルはGLB非対応のため）
        bpy.ops.object.select_all(action='DESELECT')
        logs.select_set(True)
        proxy.select_set(True)
        bpy.context.view_layer.objects.active = logs
        bpy.ops.export_scene.gltf(
            filepath=export_glb,
            export_format='GLB',
            use_selection=True,
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
