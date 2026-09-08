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
    m_leather = create_pbr_material("M_Book_LeatherCover", base_color=(0.35, 0.08, 0.12, 1.0), roughness=0.55)
    m_gold = create_pbr_material("M_Book_GoldFiligree", base_color=(0.95, 0.8, 0.2, 1.0), metallic=1.0, roughness=0.2)
    m_paper = create_pbr_material("M_Book_Parchment", base_color=(0.88, 0.82, 0.68, 1.0), roughness=0.82)
    m_glass = create_pbr_material("M_Inkpot_Glass", base_color=(0.1, 0.12, 0.15, 1.0), transmission=0.95, roughness=0.05, ior=1.52)
    m_quill = create_pbr_material("M_Quill_Feather", base_color=(0.95, 0.95, 0.92, 1.0), roughness=0.6)

    # Book Left Cover
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.21, 0, 0.01))
    cover_l = bpy.context.active_object
    cover_l.scale = (0.4, 0.52, 0.015)
    cover_l.name = "Spellbook_Cover_L"
    cover_l.data.materials.append(m_leather)

    # Book Right Cover
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.21, 0, 0.01))
    cover_r = bpy.context.active_object
    cover_r.scale = (0.4, 0.52, 0.015)
    cover_r.name = "Spellbook_Cover_R"
    cover_r.data.materials.append(m_leather)

    # Book Pages L & R
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.19, 0, 0.035))
    pages_l = bpy.context.active_object
    pages_l.scale = (0.36, 0.48, 0.04)
    pages_l.name = "Spellbook_Pages_L"
    pages_l.data.materials.append(m_paper)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.19, 0, 0.035))
    pages_r = bpy.context.active_object
    pages_r.scale = (0.36, 0.48, 0.04)
    pages_r.name = "Spellbook_Pages_R"
    pages_r.data.materials.append(m_paper)

    # Spine Gold Inlay
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.015))
    spine = bpy.context.active_object
    spine.scale = (0.05, 0.53, 0.02)
    spine.name = "Spellbook_Spine_Gold"
    spine.data.materials.append(m_gold)

    # Inkpot
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=0.08, location=(0.42, 0.28, 0.04))
    inkpot = bpy.context.active_object
    inkpot.name = "Inkpot"
    inkpot.data.materials.append(m_glass)

    # Quill
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.004, depth=0.35, location=(0.42, 0.28, 0.18))
    quill = bpy.context.active_object
    quill.rotation_euler = (math.radians(20), math.radians(-15), 0)
    quill.name = "Quill_Pen"
    quill.data.materials.append(m_quill)


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
    
    glb_path = os.path.join(assets_dir, "spellbook_quill.glb")
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
    render_cut(os.path.join(assets_dir, "spellbook_quill_cut1.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "spellbook_quill.png"), (1.8, -2.4, 1.6), (65, 0, 35), 50)
    render_cut(os.path.join(assets_dir, "spellbook_quill_cut2.png"), (0.5, -1.2, 1.4), (72, 0, 20), 75)
    render_cut(os.path.join(assets_dir, "spellbook_quill_cut3.png"), (1.4, -1.6, 2.2), (50, 0, 40), 45)
    render_cut(os.path.join(assets_dir, "spellbook_quill_cut4.png"), (1.6, -1.4, 0.4), (84, 0, 48), 35)

if __name__ == "__main__":
    main()
