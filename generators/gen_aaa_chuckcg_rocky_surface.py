import bpy
import bmesh
import math
import random
import os
import mathutils

# ==============================================================================
# 🪨 ユーザー設定パラメータ (User Parameters)
# Blenderのテキストエディタでここをお好みに変更して「▶」を押してください！
# ==============================================================================
USE_RANDOM_SEED = True       # ← 【True】: 「▶」(Alt+P)を押すたびに完全ランダムで毎回違う岩肌が生成されます！
                             #   【False】: 下の ROCK_SEED で指定した固定形状になります
ROCK_SEED = 777              # 固定シード値 (USE_RANDOM_SEED = False の場合に使用)
CLIFF_STYLE = 'AUTO'         # 'AUTO'(Seedで自動決定) / 'WALL'(垂直断崖壁) / 'BOULDER'(崩落巨塊) / 'LEDGE'(段状岩棚) / 'OVERHANG'(覆い被さり岩)
ROCK_SCALE = 1.0             # 全体スケール倍率
FRACTURE_INTENSITY = 1.0     # 節理・クラックの激しさ (0.5=丸み風化 / 1.0=標準 / 1.8=鋭利破断)
# ==============================================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)

def get_cliff_dna(seed, style):
    rng = random.Random(seed)
    styles = ['WALL', 'BOULDER', 'LEDGE', 'OVERHANG']
    chosen_style = style if style in styles else rng.choice(styles)

    if chosen_style == 'WALL':
        dims = (rng.uniform(2.0, 2.6), rng.uniform(0.7, 1.0), rng.uniform(1.5, 2.2))
        macro_scale = rng.uniform(0.55, 0.75)
        vor_scale = rng.uniform(0.28, 0.40)
        disp_macro = rng.uniform(0.32, 0.45) * FRACTURE_INTENSITY
        disp_vor = rng.uniform(0.14, 0.22) * FRACTURE_INTENSITY
    elif chosen_style == 'LEDGE':
        dims = (rng.uniform(1.8, 2.4), rng.uniform(1.6, 2.2), rng.uniform(0.6, 0.9))
        macro_scale = rng.uniform(0.60, 0.85)
        vor_scale = rng.uniform(0.35, 0.50)
        disp_macro = rng.uniform(0.25, 0.38) * FRACTURE_INTENSITY
        disp_vor = rng.uniform(0.12, 0.18) * FRACTURE_INTENSITY
    elif chosen_style == 'OVERHANG':
        dims = (rng.uniform(1.5, 2.1), rng.uniform(1.2, 1.6), rng.uniform(1.1, 1.6))
        macro_scale = rng.uniform(0.50, 0.70)
        vor_scale = rng.uniform(0.25, 0.38)
        disp_macro = rng.uniform(0.40, 0.55) * FRACTURE_INTENSITY
        disp_vor = rng.uniform(0.18, 0.26) * FRACTURE_INTENSITY
    else: # BOULDER
        dims = (rng.uniform(1.6, 2.0), rng.uniform(1.2, 1.5), rng.uniform(0.85, 1.25))
        macro_scale = rng.uniform(0.60, 0.80)
        vor_scale = rng.uniform(0.30, 0.45)
        disp_macro = rng.uniform(0.30, 0.42) * FRACTURE_INTENSITY
        disp_vor = rng.uniform(0.14, 0.20) * FRACTURE_INTENSITY

    return {
        'style': chosen_style,
        'dims': dims,
        'macro_scale': macro_scale,
        'vor_scale': vor_scale,
        'disp_macro': disp_macro,
        'disp_vor': disp_vor,
        'seed_offset': (rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(-50, 50)),
        'rng': rng
    }

def create_chuckcg_rock_material(seed, dna):
    mat = bpy.data.materials.new(name='M_ChuckCG_CliffRock_PBR')
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

    # 1. Weathered Stone Palette (ChuckCG style ColorRamp)
    noise_lg = nodes.new(type='ShaderNodeTexNoise')
    noise_lg.inputs['Scale'].default_value = 3.2
    noise_lg.inputs['Detail'].default_value = 6.0
    links.new(map_node.outputs['Vector'], noise_lg.inputs['Vector'])

    ramp_color = nodes.new(type='ShaderNodeValToRGB')
    ramp_color.color_ramp.elements[0].position = 0.22
    ramp_color.color_ramp.elements[0].color = (0.10, 0.11, 0.12, 1.0)
    ramp_color.color_ramp.elements[1].position = 0.78
    ramp_color.color_ramp.elements[1].color = (0.34, 0.32, 0.30, 1.0)
    links.new(noise_lg.outputs['Fac'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])

    # 2. Serial Multi-Bump Network (Direct ChuckCG technique: Normal -> Normal link)
    bump_macro = nodes.new(type='ShaderNodeBump')
    bump_macro.inputs['Strength'].default_value = 0.45 * FRACTURE_INTENSITY
    links.new(noise_lg.outputs['Fac'], bump_macro.inputs['Height'])

    noise_micro = nodes.new(type='ShaderNodeTexNoise')
    noise_micro.inputs['Scale'].default_value = 36.0
    noise_micro.inputs['Detail'].default_value = 8.0
    links.new(map_node.outputs['Vector'], noise_micro.inputs['Vector'])

    bump_micro = nodes.new(type='ShaderNodeBump')
    bump_micro.inputs['Strength'].default_value = 0.25
    links.new(noise_micro.outputs['Fac'], bump_micro.inputs['Height'])

    links.new(bump_macro.outputs['Normal'], bump_micro.inputs['Normal'])
    links.new(bump_micro.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.88
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.25

    return mat

def build_model(seed, dna):
    mesh = bpy.data.meshes.new('ChuckCG_Rock_Base')
    obj = bpy.data.objects.new('ChuckCG_Rocky_Surface', mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    # Scale base cube according to DNA
    sx, sy, sz = dna['dims']
    for v in bm.verts:
        v.co.x *= (sx * ROCK_SCALE)
        v.co.y *= (sy * ROCK_SCALE)
        v.co.z *= (sz * ROCK_SCALE)
        v.co.z += (sz * ROCK_SCALE * 0.5)

    # Irregular bevel on edges for sharp fractures
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.22 * ROCK_SCALE, segments=2)
    bm.to_mesh(mesh)
    bm.free()

    # Layered Procedural Modifiers (ChuckCG Stack)
    sub1 = obj.modifiers.new(name='Subsurf_Base', type='SUBSURF')
    sub1.subdivision_type = 'SIMPLE'
    sub1.levels = 3
    sub1.render_levels = 3

    # Displace Macro (Clouds)
    tex_macro = bpy.data.textures.new(f'Chuck_Macro_{seed}', type='CLOUDS')
    tex_macro.noise_scale = dna['macro_scale']
    tex_macro.noise_depth = 2
    d_macro = obj.modifiers.new(name='Disp_Macro', type='DISPLACE')
    d_macro.texture = tex_macro
    d_macro.strength = dna['disp_macro'] * ROCK_SCALE

    # Displace Voronoi (Sharp Fractures)
    tex_vor = bpy.data.textures.new(f'Chuck_Voronoi_{seed}', type='VORONOI')
    tex_vor.noise_scale = dna['vor_scale']
    d_vor = obj.modifiers.new(name='Disp_Voronoi', type='DISPLACE')
    d_vor.texture = tex_vor
    d_vor.strength = dna['disp_vor'] * ROCK_SCALE

    # Voxel Remesh
    remesh = obj.modifiers.new(name='Voxel_Remesh', type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.045 * max(0.6, ROCK_SCALE)

    # Subsurf Organic
    sub2 = obj.modifiers.new(name='Subsurf_Organic', type='SUBSURF')
    sub2.levels = 1
    sub2.render_levels = 1

    # Displace Micro
    tex_micro = bpy.data.textures.new(f'Chuck_Micro_{seed}', type='CLOUDS')
    tex_micro.noise_scale = 0.08
    tex_micro.noise_depth = 4
    d_micro = obj.modifiers.new(name='Disp_Micro', type='DISPLACE')
    d_micro.texture = tex_micro
    d_micro.strength = 0.035 * ROCK_SCALE

    mat = create_chuckcg_rock_material(seed, dna)
    obj.data.materials.append(mat)

    for f in mesh.polygons:
        f.use_smooth = True

    return obj

def setup_lighting():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    bpy.ops.object.light_add(type='AREA', location=(3.8, -4.5, 3.8))
    key = bpy.context.active_object
    key.data.energy = 600
    key.data.size = 3.8
    key.data.color = (1.0, 0.98, 0.92)

    bpy.ops.object.light_add(type='AREA', location=(-3.8, -2.5, 2.2))
    fill = bpy.context.active_object
    fill.data.energy = 240
    fill.data.size = 4.5
    fill.data.color = (0.65, 0.80, 1.0)

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 4.0, 4.0))
    rim = bpy.context.active_object
    rim.data.energy = 700
    rim.data.spot_size = math.radians(65)
    rim.data.color = (0.9, 0.95, 1.0)

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Studio_Floor'
    fmat = bpy.data.materials.new('Floor_Mat')
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.028, 0.035, 0.045, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.75
    floor.data.materials.append(fmat)

def render_cut_target(filepath, cam_pos, target_pos=(0, 0, 0.5), lens=45, samples=28):
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
    dna = get_cliff_dna(actual_seed, CLIFF_STYLE)

    clear_scene()
    build_model(actual_seed, dna)
    setup_lighting()

    if bpy.app.background:
        assets_dir = 'e:/BlenderPreFix/catalog/assets'
        os.makedirs(assets_dir, exist_ok=True)

        render_cut_target(os.path.join(assets_dir, 'aaa_chuckcg_rock_cut1.png'), (3.6, -4.5, 2.6), (0, 0, 0.5), lens=42)
        render_cut_target(os.path.join(assets_dir, 'aaa_chuckcg_rock.png'), (3.6, -4.5, 2.6), (0, 0, 0.5), lens=42)
        render_cut_target(os.path.join(assets_dir, 'aaa_chuckcg_rock_cut2.png'), (1.8, -2.4, 0.9), (0.2, 0, 0.4), lens=55)
        render_cut_target(os.path.join(assets_dir, 'aaa_chuckcg_rock_cut3.png'), (2.4, -2.8, 3.2), (0, 0, 0.5), lens=38)
        render_cut_target(os.path.join(assets_dir, 'aaa_chuckcg_rock_cut4.png'), (-3.2, 3.8, 2.2), (0, 0, 0.5), lens=40)

        glb_path = os.path.join(assets_dir, 'aaa_chuckcg_rock.glb')
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
        print(f'=== 🪨 ChuckCG様式プロシージャル断崖岩肌 生成完了！ (Seed: {actual_seed} / スタイル: {style_name}) ===')
        print(f'💡 再び「▶」(Alt+P)を押すと、次のランダムな岩肌が即座に生成されます！')

if __name__ == '__main__':
    main()
