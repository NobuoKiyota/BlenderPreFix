import bpy
import bmesh
import math
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)

def create_pbr_material(name, base_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, emission_color=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission_color:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emission_color
            if 'Emission Strength' in bsdf.inputs: bsdf.inputs['Emission Strength'].default_value = emission_strength
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_battleaxe_blade(name, sign=1, mat_steel=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    z_base = 1.15
    profile_2d = [
        (0.08 * sign, -0.15),
        (0.20 * sign, -0.28),
        (0.38 * sign, -0.38),
        (0.52 * sign, -0.30),
        (0.60 * sign, -0.10),
        (0.62 * sign,  0.00),
        (0.60 * sign,  0.15),
        (0.50 * sign,  0.35),
        (0.35 * sign,  0.42),
        (0.18 * sign,  0.30),
        (0.08 * sign,  0.15)
    ]

    t_inner = 0.035
    t_outer = 0.005

    front_verts = []
    back_verts = []

    for idx, (x, z) in enumerate(profile_2d):
        is_edge = (2 <= idx <= 8)
        th = t_outer if is_edge else t_inner
        vf = bm.verts.new((x,  th * 0.5, z_base + z))
        vb = bm.verts.new((x, -th * 0.5, z_base + z))
        front_verts.append(vf)
        back_verts.append(vb)

    vf_in = bm.verts.new((0.04 * sign,  t_inner * 0.5, z_base))
    vb_in = bm.verts.new((0.04 * sign, -t_inner * 0.5, z_base))

    for i in range(len(front_verts) - 1):
        bm.faces.new([vf_in, front_verts[i], front_verts[i+1]])

    for i in range(len(back_verts) - 1):
        bm.faces.new([vb_in, back_verts[i+1], back_verts[i]])

    for i in range(len(front_verts) - 1):
        bm.faces.new([front_verts[i], back_verts[i], back_verts[i+1], front_verts[i+1]])

    bm.faces.new([vf_in, vb_in, back_verts[0], front_verts[0]])
    bm.faces.new([vf_in, front_verts[-1], back_verts[-1], vb_in])

    bm.to_mesh(mesh)
    bm.free()

    if mat_steel:
        obj.data.materials.append(mat_steel)

    for f in mesh.polygons:
        f.use_smooth = True

    sub = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = 1
    return obj

def build_model():
    # Damascus forged steel with shiny reflective polish
    m_damascus = create_pbr_material("M_AAA_Axe_Damascus", base_color=(0.42, 0.44, 0.48, 1.0), metallic=0.98, roughness=0.18)
    m_wood = create_pbr_material("M_AAA_Axe_DarkOak", base_color=(0.14, 0.08, 0.04, 1.0), roughness=0.82)
    m_leather = create_pbr_material("M_AAA_Axe_GripLeather", base_color=(0.22, 0.11, 0.06, 1.0), roughness=0.68)
    m_brass = create_pbr_material("M_AAA_Axe_OrnateBrass", base_color=(0.95, 0.78, 0.25, 1.0), metallic=0.98, roughness=0.22)
    m_rune = create_pbr_material("M_AAA_Axe_RuneGold", base_color=(1.0, 0.88, 0.35, 1.0), emission_color=(1.0, 0.88, 0.35, 1.0), emission_strength=12.0)

    # 1. Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.032, depth=1.35, location=(0, 0, 0.67))
    shaft = bpy.context.active_object
    shaft.name = "AAA_Axe_Shaft"
    shaft.data.materials.append(m_wood)

    # 2. Pommel & Ring at base
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.055, depth=0.1, location=(0, 0, 0.04))
    pommel = bpy.context.active_object
    pommel.name = "AAA_Axe_Pommel"
    pommel.data.materials.append(m_brass)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.012, location=(0, 0, -0.03))
    ring = bpy.context.active_object
    ring.name = "AAA_Axe_PommelRing"
    ring.data.materials.append(m_brass)

    # 3. Spiral Leather Wrap (mid-shaft)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.036, depth=0.55, location=(0, 0, 0.50))
    grip = bpy.context.active_object
    grip.name = "AAA_Axe_Grip"
    grip.data.materials.append(m_leather)

    for i in range(8):
        z_rib = 0.25 + i * 0.07
        bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.005, location=(0, 0, z_rib))
        rib = bpy.context.active_object
        rib.name = f"AAA_Axe_GripRib_{i}"
        rib.data.materials.append(m_brass)

    # 4. Steel Socket Collar
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0, 0, 1.15))
    socket = bpy.context.active_object
    socket.scale = (1.4, 0.9, 1.8)
    socket.name = "AAA_Axe_Socket"
    socket.data.materials.append(m_damascus)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.052, depth=0.05, location=(0, 0, 0.98))
    c_bot = bpy.context.active_object
    c_bot.name = "AAA_Axe_CollarBot"
    c_bot.data.materials.append(m_brass)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.052, depth=0.05, location=(0, 0, 1.32))
    c_top = bpy.context.active_object
    c_top.name = "AAA_Axe_CollarTop"
    c_top.data.materials.append(m_brass)

    # 5. Dual Crescent Battleaxe Blades
    build_battleaxe_blade("AAA_Axe_Blade_Right", sign=1, mat_steel=m_damascus)
    build_battleaxe_blade("AAA_Axe_Blade_Left", sign=-1, mat_steel=m_damascus)

    # 6. Inlaid Glowing Gold Runes on Socket Face
    for side_y in [0.07, -0.07]:
        bpy.ops.mesh.primitive_cube_add(size=0.03, location=(0, side_y, 1.15))
        r1 = bpy.context.active_object
        r1.scale = (0.7, 0.2, 0.7)
        r1.rotation_euler = (0, math.radians(45), 0)
        r1.name = f"AAA_Axe_RuneCenter_{side_y}"
        r1.data.materials.append(m_rune)

        for sign in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=0.02, location=(sign * 0.05, side_y, 1.15))
            r2 = bpy.context.active_object
            r2.scale = (0.3, 0.2, 1.8)
            r2.name = f"AAA_Axe_RuneSlash_{sign}_{side_y}"
            r2.data.materials.append(m_rune)

    # 7. Armor Piercing Top Spike
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.032, depth=0.28, location=(0, 0, 1.48))
    spike = bpy.context.active_object
    spike.name = "AAA_Axe_TopSpike"
    spike.data.materials.append(m_damascus)

def setup_lighting():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    # Key light positioned to reflect specular gleam off blades
    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.8, 2.5))
    key = bpy.context.active_object
    key.data.energy = 550
    key.data.size = 2.8
    key.data.color = (1.0, 0.98, 0.92)

    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -2.0, 1.8))
    fill = bpy.context.active_object
    fill.data.energy = 240
    fill.data.size = 3.5
    fill.data.color = (0.68, 0.82, 1.0)

    # Rim light
    bpy.ops.object.light_add(type='SPOT', location=(0.0, 2.8, 2.8))
    rim = bpy.context.active_object
    rim.data.energy = 650
    rim.data.spot_size = math.radians(65)
    rim.data.color = (0.92, 0.98, 1.0)

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.028, 0.035, 0.045, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
    floor.data.materials.append(fmat)

def render_cut_target(filepath, cam_pos, target_pos=(0, 0, 1.0), lens=50, samples=28):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_pos)
    target = bpy.context.active_object
    target.name = "CamTarget"

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
    print(f"Rendered cut to: {filepath}")

def main():
    clear_scene()
    build_model()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "aaa_dwarven_battleaxe.glb")
    for obj in bpy.data.objects:
        if "Studio_Floor" in obj.name: obj.select_set(False)
        else: obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"Exported GLB: {glb_path}")

    # Axe center Z=0.95, Blade at Z=1.15
    render_cut_target(os.path.join(assets_dir, "aaa_dwarven_battleaxe_cut1.png"), (1.2, -2.4, 1.4), (0, 0, 0.95), lens=48)
    render_cut_target(os.path.join(assets_dir, "aaa_dwarven_battleaxe.png"), (1.2, -2.4, 1.4), (0, 0, 0.95), lens=48)
    render_cut_target(os.path.join(assets_dir, "aaa_dwarven_battleaxe_cut2.png"), (0.5, -1.2, 1.25), (0, 0, 1.15), lens=60)
    render_cut_target(os.path.join(assets_dir, "aaa_dwarven_battleaxe_cut3.png"), (0.9, -1.3, 1.8), (0, 0, 1.10), lens=45)
    render_cut_target(os.path.join(assets_dir, "aaa_dwarven_battleaxe_cut4.png"), (-1.2, 2.0, 1.2), (0, 0, 0.95), lens=48)

if __name__ == "__main__":
    main()
