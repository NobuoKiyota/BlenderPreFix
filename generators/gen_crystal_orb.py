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

def create_pbr_material(name, base_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, emission_color=None, emission_strength=1.0, transmission=0.0, ior=1.45):
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
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = transmission
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = transmission
    bsdf.inputs['IOR'].default_value = ior
    
    if emission_color:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emission_color
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength

    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_model():
    m_glass = create_pbr_material("M_Orb_Glass", base_color=(0.95, 0.98, 1.0, 1.0), transmission=1.0, roughness=0.02, ior=1.52)
    m_nebula = create_pbr_material("M_Orb_Nebula", base_color=(0.8, 0.1, 0.9, 1.0), emission_color=(0.8, 0.1, 0.9, 1.0), emission_strength=7.0)
    m_bronze = create_pbr_material("M_Orb_BronzeStand", base_color=(0.55, 0.42, 0.22, 1.0), metallic=0.92, roughness=0.38)
    m_ruby = create_pbr_material("M_Orb_RubyStud", base_color=(0.85, 0.05, 0.15, 1.0), transmission=0.85, roughness=0.1, ior=1.76)

    # Crystal Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.32, location=(0, 0, 0.58))
    orb = bpy.context.active_object
    orb.name = "Orb_Sphere"
    orb.data.materials.append(m_glass)

    # Nebula Core
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.16, location=(0, 0, 0.58))
    core = bpy.context.active_object
    core.name = "Orb_Nebula_Core"
    core.data.materials.append(m_nebula)

    # Base Stand
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.25, depth=0.05, location=(0, 0, 0.025))
    base = bpy.context.active_object
    base.name = "Orb_Stand_Base"
    base.data.materials.append(m_bronze)

    # Tripod Claws
    for i in range(3):
        angle = math.radians(i * 120)
        x = math.cos(angle) * 0.18
        y = math.sin(angle) * 0.18
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.022, depth=0.45, location=(x, y, 0.28))
        claw = bpy.context.active_object
        claw.rotation_euler = (-math.sin(angle)*0.25, math.cos(angle)*0.25, angle)
        claw.name = f"Orb_Claw_{i}"
        claw.data.materials.append(m_bronze)

        # Ruby Stud
        rx = math.cos(angle) * 0.22
        ry = math.sin(angle) * 0.22
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.016, location=(rx, ry, 0.06))
        gem = bpy.context.active_object
        gem.name = f"Orb_Ruby_{i}"
        gem.data.materials.append(m_ruby)


def setup_lighting():
    # World
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.015, 0.018, 0.024, 1.0)
        bg.inputs['Strength'].default_value = 0.6

    # Key light
    bpy.ops.object.light_add(type='AREA', location=(2.5, -3.0, 3.2))
    key = bpy.context.active_object
    key.data.energy = 380
    key.data.size = 2.0
    key.data.color = (1.0, 0.96, 0.9)
    key.rotation_euler = (math.radians(52), 0, math.radians(38))

    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-2.8, -1.8, 2.0))
    fill = bpy.context.active_object
    fill.data.energy = 160
    fill.data.size = 2.5
    fill.data.color = (0.75, 0.85, 1.0)
    fill.rotation_euler = (math.radians(60), 0, math.radians(-50))

    # Rim light
    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.2, 3.0))
    rim = bpy.context.active_object
    rim.data.energy = 300
    rim.data.spot_size = math.radians(65)
    rim.data.color = (0.9, 0.95, 1.0)
    rim.rotation_euler = (math.radians(-50), 0, math.radians(180))

    # Studio Floor
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.05, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.5
    floor.data.materials.append(fmat)

def setup_camera(pos, rot_deg, lens=50):
    bpy.ops.object.camera_add(location=pos)
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    cam.data.lens = lens
    bpy.context.scene.camera = cam
    return cam

def render_cut(filepath, pos, rot_deg, lens=50, samples=24):
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
    build_model()
    setup_lighting()
    
    assets_dir = "e:/BlenderPreFix/catalog/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    glb_path = os.path.join(assets_dir, "crystal_orb.glb")
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
    
    # 4-Cut Renders
    render_cut(os.path.join(assets_dir, "crystal_orb_cut1.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "crystal_orb.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "crystal_orb_cut2.png"), (0.5, -1.2, 1.4), (72, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "crystal_orb_cut3.png"), (1.4, -1.6, 2.2), (50, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "crystal_orb_cut4.png"), (1.6, -1.4, 0.4), (84, 0, 48), 35)

if __name__ == "__main__":
    main()
