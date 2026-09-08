import bpy
import math
import random
import os
import mathutils

# ==============================================================================
# 🪨 ユーザー設定パラメータ (User Parameters)
# Blenderのテキストエディタでここをお好みに変更して「▶」を押してください！
# ==============================================================================
USE_RANDOM_SEED = True   # ← 【True】: 「▶」(Alt+P)を押すたびに完全ランダムで毎回違う岩が生成されます！
                         #   【False】: 下の ROCK_SEED で指定した固定形状になります
ROCK_SEED = 777          # 固定シード値 (USE_RANDOM_SEED = False の場合に使用)
ROCK_STYLE = 'AUTO'      # 'AUTO'(Seedで自動決定) / 'BOULDER'(丸み巨礫) / 'SLATE'(板状平岩) / 'MONOLITH'(巨石柱) / 'RUGGED'(ゴツゴツ険石)
ROCK_SCALE = 1.0         # 岩全体のスケール倍率
MOSS_DENSITY = 1.0       # 苔の繁茂度 (0.0=乾いた岩 / 1.0=標準 / 2.0=深い森の苔むし岩)
# ==============================================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.node_groups: bpy.data.node_groups.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)

def get_rock_dna(seed, style):
    rng = random.Random(seed)
    styles = ['BOULDER', 'SLATE', 'MONOLITH', 'RUGGED']
    chosen_style = style if style in styles else rng.choice(styles)

    if chosen_style == 'SLATE':
        dims = (rng.uniform(1.8, 2.4), rng.uniform(1.3, 1.8), rng.uniform(0.35, 0.55))
        points_count = rng.randint(14, 22)
        noise_scale = rng.uniform(2.5, 4.0)
        disp_scale = rng.uniform(0.12, 0.18)
    elif chosen_style == 'MONOLITH':
        dims = (rng.uniform(0.7, 1.1), rng.uniform(0.8, 1.2), rng.uniform(1.8, 2.6))
        points_count = rng.randint(16, 26)
        noise_scale = rng.uniform(2.0, 3.2)
        disp_scale = rng.uniform(0.18, 0.26)
    elif chosen_style == 'RUGGED':
        dims = (rng.uniform(1.4, 2.0), rng.uniform(1.1, 1.5), rng.uniform(0.8, 1.3))
        points_count = rng.randint(24, 38)
        noise_scale = rng.uniform(3.5, 5.5)
        disp_scale = rng.uniform(0.24, 0.35)
    else: # BOULDER
        dims = (rng.uniform(1.3, 1.7), rng.uniform(1.1, 1.4), rng.uniform(0.85, 1.15))
        points_count = rng.randint(16, 24)
        noise_scale = rng.uniform(2.2, 3.5)
        disp_scale = rng.uniform(0.16, 0.24)

    return {
        'style': chosen_style,
        'dims': dims,
        'points_count': points_count,
        'noise_scale': noise_scale,
        'disp_scale': disp_scale,
        'seed_offset': (rng.uniform(-100, 100), rng.uniform(-100, 100), rng.uniform(-100, 100)),
        'rng': rng
    }

def create_rock_material(seed, dna):
    mat = bpy.data.materials.new(name='M_Sacoche_Rock_PBR')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    coord = nodes.new(type='ShaderNodeTexCoord')
    map_node = nodes.new(type='ShaderNodeMapping')
    map_node.inputs['Location'].default_value = dna['seed_offset']
    links.new(coord.outputs['Object'], map_node.inputs['Vector'])

    # 1. Base Rock Colors (Weathered granite with subtle moss/dirt)
    noise_lg = nodes.new(type='ShaderNodeTexNoise')
    noise_lg.inputs['Scale'].default_value = dna['noise_scale']
    noise_lg.inputs['Detail'].default_value = 5.0
    links.new(map_node.outputs['Vector'], noise_lg.inputs['Vector'])

    ramp_col = nodes.new(type='ShaderNodeValToRGB')
    ramp_col.color_ramp.elements[0].position = 0.2
    ramp_col.color_ramp.elements[0].color = (0.12, 0.13, 0.15, 1.0)
    ramp_col.color_ramp.elements[1].position = 0.8
    ramp_col.color_ramp.elements[1].color = (0.38, 0.36, 0.33, 1.0)
    links.new(noise_lg.outputs['Fac'], ramp_col.inputs['Fac'])

    # Subtle green moss on upward faces (+Z)
    geom = nodes.new(type='ShaderNodeNewGeometry')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    links.new(geom.outputs['Normal'], sep_xyz.inputs['Vector'])

    ramp_moss = nodes.new(type='ShaderNodeValToRGB')
    ramp_moss.color_ramp.elements[0].position = max(0.1, 0.55 - MOSS_DENSITY * 0.15)
    ramp_moss.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_moss.color_ramp.elements[1].position = min(0.95, 0.75 + MOSS_DENSITY * 0.1)
    ramp_moss.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(sep_xyz.outputs['Z'], ramp_moss.inputs['Fac'])

    # Blender 3.x / 4.x / 5.x 互換 Mix ノード
    try:
        mix_moss = nodes.new(type='ShaderNodeMixRGB')
        links.new(ramp_moss.outputs['Color'], mix_moss.inputs['Fac'])
        links.new(ramp_col.outputs['Color'], mix_moss.inputs['Color1'])
        mix_moss.inputs['Color2'].default_value = (0.14, 0.28, 0.08, 1.0)
        links.new(mix_moss.outputs['Color'], bsdf.inputs['Base Color'])
    except Exception:
        mix_moss = nodes.new(type='ShaderNodeMix')
        mix_moss.data_type = 'RGBA'
        links.new(ramp_moss.outputs['Color'], mix_moss.inputs[0])
        links.new(ramp_col.outputs['Color'], mix_moss.inputs[6])
        mix_moss.inputs[7].default_value = (0.14, 0.28, 0.08, 1.0)
        links.new(mix_moss.outputs[2], bsdf.inputs['Base Color'])

    # Dual Bumps (Large cracks + fine micro-grain)
    bump_lg = nodes.new(type='ShaderNodeBump')
    bump_lg.inputs['Strength'].default_value = 0.45
    links.new(noise_lg.outputs['Fac'], bump_lg.inputs['Height'])

    noise_sm = nodes.new(type='ShaderNodeTexNoise')
    noise_sm.inputs['Scale'].default_value = 24.0
    noise_sm.inputs['Detail'].default_value = 4.0
    links.new(map_node.outputs['Vector'], noise_sm.inputs['Vector'])

    bump_sm = nodes.new(type='ShaderNodeBump')
    bump_sm.inputs['Strength'].default_value = 0.25
    links.new(noise_sm.outputs['Fac'], bump_sm.inputs['Height'])

    links.new(bump_lg.outputs['Normal'], bump_sm.inputs['Normal'])
    links.new(bump_sm.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.88
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.25

    return mat

def create_geometry_nodes_rock(obj, mat, seed, dna):
    mod = obj.modifiers.new(name='Sacoche_Rock_GN', type='NODES')
    nt = bpy.data.node_groups.new(name='GN_Sacoche_Procedural_Rock', type='GeometryNodeTree')
    mod.node_group = nt

    if hasattr(nt, 'interface'):
        nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        nt.inputs.new('NodeSocketGeometry', 'Geometry')
        nt.outputs.new('NodeSocketGeometry', 'Geometry')

    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    node_in = nodes.new(type='NodeGroupInput')
    node_out = nodes.new(type='NodeGroupOutput')
    node_in.location = (-800, 0)
    node_out.location = (1100, 0)

    # 1. Distribute Points in Volume / on Faces
    node_dist = nodes.new(type='GeometryNodeDistributePointsOnFaces')
    node_dist.inputs['Density'].default_value = float(dna['points_count'])
    node_dist.inputs['Seed'].default_value = seed % 10000
    node_dist.location = (-600, 0)
    links.new(node_in.outputs['Geometry'], node_dist.inputs['Mesh'])

    # 2. Instance on Points (Multiple Cubes with Random rotation/scale)
    node_inst = nodes.new(type='GeometryNodeInstanceOnPoints')
    node_inst.location = (-350, 0)

    node_inst_cube = nodes.new(type='GeometryNodeMeshCube')
    node_inst_cube.inputs['Size'].default_value = (0.55 * ROCK_SCALE, 0.55 * ROCK_SCALE, 0.55 * ROCK_SCALE)
    node_inst_cube.location = (-600, -200)

    node_rand_rot = nodes.new(type='FunctionNodeRandomValue')
    node_rand_rot.data_type = 'FLOAT_VECTOR'
    node_rand_rot.inputs['Min'].default_value = (0, 0, 0)
    node_rand_rot.inputs['Max'].default_value = (math.pi * 2, math.pi * 2, math.pi * 2)
    node_rand_rot.inputs['Seed'].default_value = (seed + 11) % 10000
    node_rand_rot.location = (-600, -400)

    node_rand_scale = nodes.new(type='FunctionNodeRandomValue')
    node_rand_scale.data_type = 'FLOAT_VECTOR'
    node_rand_scale.inputs['Min'].default_value = (0.4, 0.4, 0.4)
    node_rand_scale.inputs['Max'].default_value = (1.4, 1.4, 1.4)
    node_rand_scale.inputs['Seed'].default_value = (seed + 22) % 10000
    node_rand_scale.location = (-600, -600)

    links.new(node_dist.outputs['Points'], node_inst.inputs['Points'])
    links.new(node_inst_cube.outputs['Mesh'], node_inst.inputs['Instance'])
    links.new(node_rand_rot.outputs['Value'], node_inst.inputs['Rotation'])
    links.new(node_rand_scale.outputs['Value'], node_inst.inputs['Scale'])

    # 3. Realize Instances
    node_realize = nodes.new(type='GeometryNodeRealizeInstances')
    node_realize.location = (-150, 0)
    links.new(node_inst.outputs['Instances'], node_realize.inputs['Geometry'])

    # 4. Convex Hull (Sacoche Ito 3D core technique)
    node_convex = nodes.new(type='GeometryNodeConvexHull')
    node_convex.location = (50, 0)
    links.new(node_realize.outputs['Geometry'], node_convex.inputs['Geometry'])

    # 5. Subdivide Mesh
    node_subdiv = nodes.new(type='GeometryNodeSubdivideMesh')
    node_subdiv.inputs['Level'].default_value = 3
    node_subdiv.location = (250, 0)
    links.new(node_convex.outputs['Convex Hull'], node_subdiv.inputs['Mesh'])

    # 6. Set Position with Dynamic Noise Texture Offset
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = dna['noise_scale']
    node_noise.inputs['Detail'].default_value = 4.0
    node_noise.inputs['Roughness'].default_value = 0.6
    node_noise.location = (250, -300)

    # Offset noise based on seed
    node_add_seed = nodes.new(type='ShaderNodeVectorMath')
    node_add_seed.operation = 'ADD'
    node_add_seed.inputs[1].default_value = dna['seed_offset']
    node_add_seed.location = (50, -300)
    node_pos = nodes.new(type='GeometryNodeInputPosition')
    node_pos.location = (-150, -300)
    links.new(node_pos.outputs['Position'], node_add_seed.inputs[0])
    links.new(node_add_seed.outputs['Vector'], node_noise.inputs['Vector'])

    node_sub = nodes.new(type='ShaderNodeVectorMath')
    node_sub.operation = 'SUBTRACT'
    node_sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    node_sub.location = (450, -300)
    links.new(node_noise.outputs['Color'], node_sub.inputs[0])

    node_scale_disp = nodes.new(type='ShaderNodeVectorMath')
    node_scale_disp.operation = 'SCALE'
    node_scale_disp.inputs['Scale'].default_value = dna['disp_scale'] * ROCK_SCALE
    node_scale_disp.location = (650, -300)
    links.new(node_sub.outputs['Vector'], node_scale_disp.inputs['Vector'])

    node_setpos = nodes.new(type='GeometryNodeSetPosition')
    node_setpos.location = (500, 0)
    links.new(node_subdiv.outputs['Mesh'], node_setpos.inputs['Geometry'])
    links.new(node_scale_disp.outputs['Vector'], node_setpos.inputs['Offset'])

    # 7. Set Shade Smooth
    node_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
    node_smooth.location = (700, 0)
    links.new(node_setpos.outputs['Geometry'], node_smooth.inputs['Geometry'])

    # 8. Set Material
    node_setmat = nodes.new(type='GeometryNodeSetMaterial')
    node_setmat.inputs['Material'].default_value = mat
    node_setmat.location = (900, 0)
    links.new(node_smooth.outputs['Geometry'], node_setmat.inputs['Geometry'])

    links.new(node_setmat.outputs['Geometry'], node_out.inputs['Geometry'])

def setup_lighting():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    bpy.ops.object.light_add(type='AREA', location=(3.5, -4.0, 3.5))
    key = bpy.context.active_object
    key.data.energy = 550
    key.data.size = 3.5
    key.data.color = (1.0, 0.98, 0.92)

    bpy.ops.object.light_add(type='AREA', location=(-3.5, -2.5, 2.2))
    fill = bpy.context.active_object
    fill.data.energy = 240
    fill.data.size = 4.0
    fill.data.color = (0.68, 0.82, 1.0)

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.5, 3.5))
    rim = bpy.context.active_object
    rim.data.energy = 650
    rim.data.spot_size = math.radians(60)
    rim.data.color = (0.9, 0.95, 1.0)

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Studio_Floor'
    fmat = bpy.data.materials.new('Floor_Mat')
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.03, 0.038, 0.048, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.75
    floor.data.materials.append(fmat)

def render_cut_target(filepath, cam_pos, target_pos=(0, 0, 0.45), lens=42, samples=28):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_pos)
    target = bpy.context.active_object
    target.name = 'CamTarget'

    bpy.ops.object.camera_add(location=cam_pos)
    cam = bpy.context.active_object
    cam.data.lens = lens

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam
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
    bpy.data.objects.remove(target, do_unlink=True)
    print(f'Rendered cut to: {filepath}')

def main():
    actual_seed = random.randint(1, 999999) if USE_RANDOM_SEED else ROCK_SEED
    dna = get_rock_dna(actual_seed, ROCK_STYLE)

    clear_scene()

    # Base Icosphere mesh shaped by DNA proportions
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.9 * ROCK_SCALE, location=(0, 0, dna['dims'][2] * 0.5))
    rock_obj = bpy.context.active_object
    rock_obj.scale = dna['dims']
    bpy.ops.object.transform_apply(scale=True)
    rock_obj = bpy.context.active_object
    rock_obj.name = 'Sacoche_Procedural_Rock'

    mat = create_rock_material(actual_seed, dna)
    create_geometry_nodes_rock(rock_obj, mat, actual_seed, dna)
    setup_lighting()

    if bpy.app.background:
        assets_dir = 'e:/BlenderPreFix/catalog/assets'
        os.makedirs(assets_dir, exist_ok=True)

        render_cut_target(os.path.join(assets_dir, 'aaa_mossy_rock_cut1.png'), (3.8, -4.8, 2.8), (0, 0, 0.45), lens=40)
        render_cut_target(os.path.join(assets_dir, 'aaa_mossy_rock.png'), (3.8, -4.8, 2.8), (0, 0, 0.45), lens=40)
        render_cut_target(os.path.join(assets_dir, 'aaa_mossy_rock_cut2.png'), (2.2, -2.8, 1.5), (0.3, 0, 0.5), lens=52)
        render_cut_target(os.path.join(assets_dir, 'aaa_mossy_rock_cut3.png'), (2.5, -3.0, 3.5), (0, 0, 0.45), lens=38)
        render_cut_target(os.path.join(assets_dir, 'aaa_mossy_rock_cut4.png'), (-3.5, 4.2, 2.5), (0, 0, 0.45), lens=40)

        glb_path = os.path.join(assets_dir, 'aaa_mossy_rock.glb')
        for obj in bpy.data.objects:
            if 'Studio_Floor' in obj.name: obj.select_set(False)
            else: obj.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=glb_path,
            export_format='GLB',
            use_selection=True,
            export_materials='EXPORT',
            export_apply=True
        )
        print(f'Exported GLB: {glb_path}')
    else:
        style_name = dna['style']
        print(f'=== 🪨 サコッシュ伊藤様式プロシージャル苔岩 生成完了！ (Seed: {actual_seed} / スタイル: {style_name}) ===')
        print(f'💡 再び「▶」(Alt+P)を押すと、次のランダムな岩が即座に生成されます！')

if __name__ == '__main__':
    main()
