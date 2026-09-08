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
    m_wood = create_pbr_material("M_Barrel_Oak", base_color=(0.32, 0.22, 0.14, 1.0), roughness=0.78)
    m_iron = create_pbr_material("M_Barrel_IronHoop", base_color=(0.18, 0.18, 0.2, 1.0), metallic=0.92, roughness=0.52)
    m_bung = create_pbr_material("M_Barrel_TapWood", base_color=(0.25, 0.15, 0.08, 1.0), roughness=0.85)

    # Barrel Main Body
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.42, depth=1.1, location=(0, 0, 0.55))
    barrel = bpy.context.active_object
    barrel.scale = (1.1, 1.1, 1.0)
    barrel.name = "Barrel_Body"
    barrel.data.materials.append(m_wood)

    # 4 Iron Hoops
    hoop_zs = [0.18, 0.38, 0.72, 0.92]
    hoop_rads = [0.44, 0.47, 0.47, 0.44]
    for i, (z, r) in enumerate(zip(hoop_zs, hoop_rads)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r * 1.03, depth=0.035, location=(0, 0, z))
        hoop = bpy.context.active_object
        hoop.name = f"Barrel_Hoop_{i}"
        hoop.data.materials.append(m_iron)

    # Bung Tap
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.028, depth=0.06, location=(0.5, 0, 0.55))
    bung = bpy.context.active_object
    bung.rotation_euler = (0, math.radians(90), 0)
    bung.name = "Barrel_Bung"
    bung.data.materials.append(m_bung)


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
    
    glb_path = os.path.join(assets_dir, "wooden_barrel.glb")
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
    render_cut(os.path.join(assets_dir, "wooden_barrel_cut1.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "wooden_barrel.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "wooden_barrel_cut2.png"), (0.5, -1.2, 1.4), (72, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "wooden_barrel_cut3.png"), (1.4, -1.6, 2.2), (50, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "wooden_barrel_cut4.png"), (1.6, -1.4, 0.4), (84, 0, 48), 35)

if __name__ == "__main__":
    main()
