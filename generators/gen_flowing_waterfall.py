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

def create_pbr_material(name, base_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, emission_color=None, emission_strength=1.0, transmission=0.0, ior=1.45, subsurface=0.0):
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
    
    # Subsurface
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = subsurface
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = subsurface

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
    m_rock = create_pbr_material("M_Waterfall_WetRock", base_color=(0.14, 0.15, 0.17, 1.0), metallic=0.1, roughness=0.22)
    m_stream = create_pbr_material("M_Waterfall_Stream", base_color=(0.88, 0.95, 1.0, 1.0), transmission=0.92, roughness=0.08, ior=1.333)
    m_foam = create_pbr_material("M_Waterfall_Foam", base_color=(0.98, 0.98, 1.0, 1.0), emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=1.4, roughness=0.7)
    m_pool = create_pbr_material("M_Waterfall_Pool", base_color=(0.1, 0.3, 0.35, 1.0), transmission=0.88, roughness=0.03, ior=1.333)

    # Cliff Rock Backdrop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.45, 1.3))
    cliff = bpy.context.active_object
    cliff.scale = (2.2, 1.0, 2.6)
    cliff.name = "Waterfall_Cliff"
    cliff.data.materials.append(m_rock)

    # Mid Ledge
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 1.2))
    ledge = bpy.context.active_object
    ledge.scale = (1.8, 0.4, 0.25)
    ledge.name = "Waterfall_Ledge"
    ledge.data.materials.append(m_rock)

    # Waterfall Upper Stream
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.02, 1.9))
    stream1 = bpy.context.active_object
    stream1.scale = (1.2, 0.12, 1.2)
    stream1.name = "Waterfall_UpperDrop"
    stream1.data.materials.append(m_stream)

    # Waterfall Lower Main Drop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, 0.65))
    stream2 = bpy.context.active_object
    stream2.scale = (1.4, 0.15, 1.1)
    stream2.rotation_euler = (math.radians(12), 0, 0)
    stream2.name = "Waterfall_LowerDrop"
    stream2.data.materials.append(m_stream)

    # Impact Foam Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.1, location=(0, -0.32, 0.16))
    foam = bpy.context.active_object
    foam.scale = (1.5, 0.9, 0.5)
    foam.name = "Waterfall_FoamRing"
    foam.data.materials.append(m_foam)

    # Plunge Pool
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.4, depth=0.25, location=(0, -0.35, 0.1))
    pool = bpy.context.active_object
    pool.name = "Waterfall_Pool"
    pool.data.materials.append(m_pool)


def setup_lighting():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.015, 0.02, 0.028, 1.0)
        bg.inputs['Strength'].default_value = 0.8

    # Sun / Main Area
    bpy.ops.object.light_add(type='AREA', location=(3.0, -3.5, 4.0))
    key = bpy.context.active_object
    key.data.energy = 420
    key.data.size = 3.0
    key.data.color = (1.0, 0.98, 0.92)
    key.rotation_euler = (math.radians(50), 0, math.radians(35))

    # Fill sky light
    bpy.ops.object.light_add(type='AREA', location=(-3.2, -2.0, 2.5))
    fill = bpy.context.active_object
    fill.data.energy = 180
    fill.data.size = 3.5
    fill.data.color = (0.7, 0.85, 1.0)
    fill.rotation_euler = (math.radians(58), 0, math.radians(-52))

    # Rim sun
    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.5, 3.5))
    rim = bpy.context.active_object
    rim.data.energy = 350
    rim.data.spot_size = math.radians(60)
    rim.data.color = (0.95, 0.98, 1.0)
    rim.rotation_euler = (math.radians(-48), 0, math.radians(180))

    # Studio Floor
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    fmat = bpy.data.materials.new("Floor_Mat")
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.035, 0.045, 0.055, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.6
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
    
    glb_path = os.path.join(assets_dir, "flowing_waterfall.glb")
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
    render_cut(os.path.join(assets_dir, "flowing_waterfall_cut1.png"), (2.5, -3.5, 2.2), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "flowing_waterfall.png"), (2.5, -3.5, 2.2), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "flowing_waterfall_cut2.png"), (0.8, -1.6, 1.8), (70, 0, 22), 75)
    render_cut(os.path.join(assets_dir, "flowing_waterfall_cut3.png"), (1.8, -2.0, 3.2), (48, 0, 38), 45)
    render_cut(os.path.join(assets_dir, "flowing_waterfall_cut4.png"), (2.0, -1.8, 0.5), (82, 0, 48), 35)

if __name__ == "__main__":
    main()
