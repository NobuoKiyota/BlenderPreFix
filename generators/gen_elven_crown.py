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
    m_silver = create_pbr_material("M_Crown_Silver", base_color=(0.95, 0.95, 0.98, 1.0), metallic=1.0, roughness=0.15)
    m_sapphire = create_pbr_material("M_Crown_Sapphire", base_color=(0.08, 0.2, 0.85, 1.0), transmission=0.94, roughness=0.05, ior=1.77)
    m_diamond = create_pbr_material("M_Crown_Diamond", base_color=(0.98, 0.98, 1.0, 1.0), transmission=0.98, roughness=0.02, ior=2.42)

    # Head Circlet Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.008, location=(0, 0, 0.12))
    ring = bpy.context.active_object
    ring.scale = (0.9, 1.1, 1.0)
    ring.name = "Crown_Ring"
    ring.data.materials.append(m_silver)

    # Center Leaf
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.025, depth=0.09, location=(0, -0.15, 0.16))
    leaf_c = bpy.context.active_object
    leaf_c.scale = (1.2, 0.3, 1.0)
    leaf_c.name = "Crown_CenterLeaf"
    leaf_c.data.materials.append(m_silver)

    # Side Leaves
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.02, depth=0.07, location=(sign * 0.05, -0.14, 0.15))
        leaf = bpy.context.active_object
        leaf.scale = (1.0, 0.3, 1.0)
        leaf.rotation_euler = (0, 0, sign * math.radians(-25))
        leaf.name = f"Crown_SideLeaf_{sign}"
        leaf.data.materials.append(m_silver)

    # Center Sapphire Gem
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.022, location=(0, -0.158, 0.14))
    gem = bpy.context.active_object
    gem.scale = (1.0, 0.5, 1.3)
    gem.name = "Crown_Sapphire"
    gem.data.materials.append(m_sapphire)

    # Diamond Accents
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.008, location=(sign * 0.035, -0.152, 0.13))
        dia = bpy.context.active_object
        dia.name = f"Crown_Dia_{sign}"
        dia.data.materials.append(m_diamond)


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
    
    glb_path = os.path.join(assets_dir, "elven_crown.glb")
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
    render_cut(os.path.join(assets_dir, "elven_crown_cut1.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "elven_crown.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "elven_crown_cut2.png"), (0.5, -1.2, 1.4), (72, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "elven_crown_cut3.png"), (1.4, -1.6, 2.2), (50, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "elven_crown_cut4.png"), (1.6, -1.4, 0.4), (84, 0, 48), 35)

if __name__ == "__main__":
    main()
