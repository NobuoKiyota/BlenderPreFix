"""プロシージャル破壊対象形状(岩・壁・柱・建物・地面)とマテリアルの生成。

generators/gen_destruction_scene.py の build_*_shape / create_*_material 群を
パラメータ化・関数引数化して移植したもの(モジュールグローバルへの依存を排除)。
"""

import random

import bmesh
import bpy
import mathutils


def create_outer_stone_material():
    mat = bpy.data.materials.new(name="Mat_Destruction_OuterStone")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.72, 0.69, 0.65, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
    return mat


def create_inner_chipped_material():
    mat = bpy.data.materials.new(name="Mat_Destruction_InnerChipped")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.42, 0.38, 0.35, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.92
    return mat


def _add_ground_plane(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    ground = bpy.context.active_object
    ground.name = name
    ground.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    ground.data.materials.append(material)
    ground["is_destruction_ground"] = True
    return ground


def build_craggy_rock_shape(outer_mat, inner_mat, seed_val):
    random.seed(seed_val)
    hit_pos = (0.0, 0.0, 1.40)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.65, location=hit_pos)
    rock = bpy.context.active_object
    rock.name = "Destruction_Rock"

    rock.scale = (
        random.uniform(1.05, 1.35),
        random.uniform(0.85, 1.15),
        random.uniform(0.95, 1.30),
    )
    bpy.ops.object.transform_apply(scale=True)

    bm = bmesh.new()
    bm.from_mesh(rock.data)
    n = mathutils.noise
    seed_offset = mathutils.Vector(
        (random.uniform(-50.0, 50.0), random.uniform(-50.0, 50.0), random.uniform(-50.0, 50.0))
    )
    for v in bm.verts:
        p = (v.co * 0.75) + seed_offset
        disp = n.fractal(p, 0.75, 2.2, 4) * 0.65 - n.noise(p * 1.8) * 0.35
        v.co += v.normal * disp
    bm.to_mesh(rock.data)
    bm.free()
    rock.data.update()

    bpy.ops.object.modifier_add(type="BEVEL")
    bev = rock.modifiers["Bevel"]
    bev.width = 0.06
    bev.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")

    rock.data.materials.append(outer_mat)
    rock.data.materials.append(inner_mat)

    ground = _add_ground_plane("Destruction_Ground", (0, 0, 0.05), (8.5, 8.5, 0.10), outer_mat)
    return rock, ground, hit_pos


def build_craggy_wall_shape(outer_mat, inner_mat, seed_val):
    random.seed(seed_val)
    hit_pos = (0.0, 0.0, 1.65)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.70))
    wall = bpy.context.active_object
    wall.name = "Destruction_Wall"
    wall.scale = (4.6, 1.05, 3.4)
    bpy.ops.object.transform_apply(scale=True)

    sub = wall.modifiers.new("Subsurf", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = 4
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    bm = bmesh.new()
    bm.from_mesh(wall.data)
    n = mathutils.noise
    seed_offset = mathutils.Vector((random.uniform(-30, 30), random.uniform(-30, 30), random.uniform(-30, 30)))
    for v in bm.verts:
        if abs(v.co.y) > 0.35:
            p = (v.co * 1.1) + seed_offset
            disp = n.fractal(p, 0.7, 2.0, 3) * 0.32 - n.noise(p * 2.2) * 0.16
            v.co += v.normal * disp
    bm.to_mesh(wall.data)
    bm.free()
    wall.data.update()

    wall.data.materials.append(outer_mat)
    wall.data.materials.append(inner_mat)

    ground = _add_ground_plane("Destruction_Ground", (0, 0, 0.05), (9.0, 9.0, 0.10), outer_mat)
    return wall, ground, hit_pos


def build_building_shape(outer_mat, inner_mat):
    tower_parts = []
    for ox, oy in [(-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy, 2.4))
        c = bpy.context.active_object
        c.scale = (0.45, 0.45, 4.8)
        bpy.ops.object.transform_apply(scale=True)
        tower_parts.append(c)

    for floor_z in (1.5, 3.0, 4.7):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, floor_z))
        slab = bpy.context.active_object
        slab.scale = (2.6, 2.6, 0.28)
        bpy.ops.object.transform_apply(scale=True)
        tower_parts.append(slab)

    bpy.context.view_layer.objects.active = tower_parts[0]
    bpy.ops.object.select_all(action="DESELECT")
    for p in tower_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = tower_parts[0]
    bpy.ops.object.join()
    tower = bpy.context.active_object
    tower.name = "Destruction_Building"
    tower.data.materials.append(outer_mat)
    tower.data.materials.append(inner_mat)

    ground = _add_ground_plane("Destruction_Ground", (0, 0, 0.05), (8.5, 8.5, 0.10), outer_mat)
    return tower, ground, (0.0, 0.0, 1.50)


def build_pillar_shape(outer_mat, inner_mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=3.6, location=(0, 0, 1.85))
    pillar = bpy.context.active_object
    pillar.name = "Destruction_Pillar"
    pillar.data.materials.append(outer_mat)
    pillar.data.materials.append(inner_mat)

    ground = _add_ground_plane("Destruction_Ground", (0, 0, 0.05), (7.5, 7.5, 0.10), outer_mat)
    return pillar, ground, (0, 0, 1.40)


def build_ground_shape(outer_mat, inner_mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    ground_plate = bpy.context.active_object
    ground_plate.name = "Destruction_GroundSlab"
    ground_plate.scale = (6.0, 6.0, 0.50)
    bpy.ops.object.transform_apply(scale=True)
    ground_plate.data.materials.append(outer_mat)
    ground_plate.data.materials.append(inner_mat)

    ground = _add_ground_plane("Destruction_Ground", (0, 0, 0.17), (8.5, 8.5, 0.35), outer_mat)
    return ground_plate, ground, (0, 0, 0.30)


SHAPE_BUILDERS = {
    "ROCK": lambda outer, inner, seed: build_craggy_rock_shape(outer, inner, seed),
    "WALL": lambda outer, inner, seed: build_craggy_wall_shape(outer, inner, seed),
    "BUILDING": lambda outer, inner, seed: build_building_shape(outer, inner),
    "PILLAR": lambda outer, inner, seed: build_pillar_shape(outer, inner),
    "GROUND": lambda outer, inner, seed: build_ground_shape(outer, inner),
}


def build_shape(shape_type, seed_val):
    """shape_type(RANDOMを含む)から形状を1つ構築し、(target_obj, ground_obj, hit_pos)を返す。"""
    outer_mat = create_outer_stone_material()
    inner_mat = create_inner_chipped_material()

    available = list(SHAPE_BUILDERS.keys())
    resolved = random.choice(available) if shape_type == "RANDOM" else shape_type
    if resolved not in SHAPE_BUILDERS:
        resolved = "ROCK"

    builder = SHAPE_BUILDERS[resolved]
    return builder(outer_mat, inner_mat, seed_val)
