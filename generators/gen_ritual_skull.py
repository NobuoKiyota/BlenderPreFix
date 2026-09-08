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
    m_bone = create_pbr_material("M_Skull_Bone", base_color=(0.82, 0.78, 0.68, 1.0), roughness=0.65)
    m_rune = create_pbr_material("M_Skull_RuneGlow", base_color=(0.1, 0.9, 0.4, 1.0), emission_color=(0.1, 0.9, 0.4, 1.0), emission_strength=8.0)
    m_dark = create_pbr_material("M_Skull_DarkSocket", base_color=(0.02, 0.02, 0.03, 1.0), roughness=0.95)

    # Cranium
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.18, location=(0, 0, 0.28))
    cranium = bpy.context.active_object
    cranium.scale = (0.85, 1.15, 0.95)
    cranium.name = "Skull_Cranium"
    cranium.data.materials.append(m_bone)

    # Maxilla Jaw
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.1, 0.14))
    maxilla = bpy.context.active_object
    maxilla.scale = (0.13, 0.11, 0.12)
    maxilla.name = "Skull_Maxilla"
    maxilla.data.materials.append(m_bone)

    # Eye Sockets (Dark interior + Gem glow)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(sign * 0.065, -0.16, 0.22))
        socket = bpy.context.active_object
        socket.name = f"Skull_Socket_{sign}"
        socket.data.materials.append(m_dark)

        # Soul Gem
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.018, location=(sign * 0.065, -0.15, 0.22))
        gem = bpy.context.active_object
        gem.name = f"Skull_EyeGem_{sign}"
        gem.data.materials.append(m_rune)

    # Forehead Rune Glyph
    bpy.ops.mesh.primitive_cube_add(size=0.03, location=(0, -0.18, 0.32))
    rune = bpy.context.active_object
    rune.scale = (1.5, 0.2, 0.8)
    rune.name = "Skull_RuneGlyph"
    rune.data.materials.append(m_rune)


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
    
    glb_path = os.path.join(assets_dir, "ritual_skull.glb")
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
    render_cut(os.path.join(assets_dir, "ritual_skull_cut1.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "ritual_skull.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "ritual_skull_cut2.png"), (0.5, -1.2, 1.4), (72, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "ritual_skull_cut3.png"), (1.4, -1.6, 2.2), (50, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "ritual_skull_cut4.png"), (1.6, -1.4, 0.4), (84, 0, 48), 35)

if __name__ == "__main__":
    main()
