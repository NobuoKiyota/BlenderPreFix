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
    m_leaf = create_pbr_material("M_Lotus_Leaf", base_color=(0.1, 0.48, 0.22, 1.0), roughness=0.35, subsurface=0.25)
    m_drop = create_pbr_material("M_Lotus_Droplets", base_color=(0.95, 0.98, 1.0, 1.0), transmission=1.0, roughness=0.01, ior=1.333)
    m_water = create_pbr_material("M_Pond_Water", base_color=(0.08, 0.22, 0.18, 1.0), transmission=0.85, roughness=0.04, ior=1.333)

    # Water Plane Base
    bpy.ops.mesh.primitive_plane_add(size=2.4, location=(0, 0, 0.02))
    pond = bpy.context.active_object
    pond.name = "Lotus_Pond_Base"
    pond.data.materials.append(m_water)

    # Lotus Leaf Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.6, depth=0.015, location=(0, 0, 0.06))
    leaf = bpy.context.active_object
    leaf.scale = (1.05, 0.95, 1.0)
    leaf.name = "Lotus_Leaf_Disc"
    leaf.data.materials.append(m_leaf)

    # Center Main Droplet
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=16, radius=0.045, location=(0.02, -0.02, 0.09))
    main_drop = bpy.context.active_object
    main_drop.scale = (1.0, 1.0, 0.65)
    main_drop.name = "Lotus_Main_Droplet"
    main_drop.data.materials.append(m_drop)

    # Satellite Droplets
    satellites = [(0.18, 0.12, 0.075, 0.018), (-0.15, 0.22, 0.075, 0.014), (0.22, -0.18, 0.075, 0.02), (-0.25, -0.15, 0.075, 0.016)]
    for i, (dx, dy, dz, drad) in enumerate(satellites):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=drad, location=(dx, dy, dz))
        d = bpy.context.active_object
        d.scale = (1.0, 1.0, 0.7)
        d.name = f"Lotus_Droplet_{i}"
        d.data.materials.append(m_drop)


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
    
    glb_path = os.path.join(assets_dir, "lotus_leaf_droplets.glb")
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
    render_cut(os.path.join(assets_dir, "lotus_leaf_droplets_cut1.png"), (1.8, -2.4, 2.0), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "lotus_leaf_droplets.png"), (1.8, -2.4, 2.0), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "lotus_leaf_droplets_cut2.png"), (0.8, -1.6, 1.8), (70, 0, 22), 75)
    render_cut(os.path.join(assets_dir, "lotus_leaf_droplets_cut3.png"), (1.8, -2.0, 3.2), (48, 0, 38), 45)
    render_cut(os.path.join(assets_dir, "lotus_leaf_droplets_cut4.png"), (2.0, -1.8, 0.5), (82, 0, 48), 35)

if __name__ == "__main__":
    main()
