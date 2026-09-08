import bpy
import bmesh
import math
import random
import os
import mathutils

# ==============================================================================
# 🌲 ユーザー設定パラメータ (User Parameters)
# Blenderのテキストエディタでここをお好みに変更して「▶」を押してください！
# ==============================================================================
USE_RANDOM_SEED = True   # ← 【True】: 「▶」(Alt+P)を押すたびに完全ランダムで毎回違う木が生成されます！
                         #   【False】: 下の TREE_SEED で指定した固定形状になります
TREE_SEED = 777          # 固定シード値 (USE_RANDOM_SEED = False の場合に使用)
TREE_HEIGHT = 5.2        # 樹木の高さ (m)
BRANCH_COUNT = 54        # 主枝の本数 (20=まばらな古木 / 50=標準 / 90=鬱蒼と茂る巨木)
TREE_STYLE = 'AUTO'      # 'AUTO'(Seedで自動決定) / 'SPREADING'(広がり大木) / 'WEEPING'(しだれ) / 'UPRIGHT'(直立円錐) / 'TWISTED'(ねじれ)
BRANCH_CURL = 1.0        # 枝のうねり・屈曲度合い (0.0=直線的 / 1.0=自然 / 2.0=激しいねじれ)
DROOP_FACTOR = 1.0       # 枝のしだれ・垂れ下がり度合い (0.0=ピンと張る / 1.0=自然 / 2.0=柳のように垂れる)
CANOPY_DENSITY = 1.0     # 葉の密度倍率
# ==============================================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.curves: bpy.data.curves.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)

def get_tree_dna(seed, style):
    rng = random.Random(seed)
    styles = ['SPREADING', 'WEEPING', 'UPRIGHT', 'TWISTED']
    chosen_style = style if style in styles else rng.choice(styles)

    # 幹の変形パラメータ
    if chosen_style == 'TWISTED':
        trunk_lean = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25))
        trunk_wiggle_amp = rng.uniform(0.18, 0.32)
        trunk_wiggle_freq = rng.uniform(2.0, 3.2)
        base_elev = rng.uniform(15.0, 35.0)
        droop_mult = rng.uniform(0.6, 1.2) * DROOP_FACTOR
        curl_mult = rng.uniform(1.4, 2.2) * BRANCH_CURL
        spread_exp = 0.8
    elif chosen_style == 'WEEPING':
        trunk_lean = (rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08))
        trunk_wiggle_amp = rng.uniform(0.06, 0.12)
        trunk_wiggle_freq = 1.6
        base_elev = rng.uniform(25.0, 45.0)
        droop_mult = rng.uniform(1.6, 2.6) * DROOP_FACTOR # 強くしだれる
        curl_mult = rng.uniform(0.7, 1.2) * BRANCH_CURL
        spread_exp = 1.1
    elif chosen_style == 'SPREADING':
        trunk_lean = (rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12))
        trunk_wiggle_amp = rng.uniform(0.10, 0.18)
        trunk_wiggle_freq = 1.8
        base_elev = rng.uniform(15.0, 32.0) # 横へ大きく広がる
        droop_mult = rng.uniform(0.7, 1.2) * DROOP_FACTOR
        curl_mult = rng.uniform(1.0, 1.5) * BRANCH_CURL
        spread_exp = 0.55 # 上部も広く開いたドーム傘状
    else: # UPRIGHT
        trunk_lean = (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04))
        trunk_wiggle_amp = rng.uniform(0.04, 0.08)
        trunk_wiggle_freq = 1.5
        base_elev = rng.uniform(28.0, 52.0) # 上向きピラミッド
        droop_mult = rng.uniform(0.4, 0.8) * DROOP_FACTOR
        curl_mult = rng.uniform(0.5, 0.9) * BRANCH_CURL
        spread_exp = 1.0

    return {
        'style': chosen_style,
        'lean': trunk_lean,
        'amp': trunk_wiggle_amp,
        'freq': trunk_wiggle_freq,
        'base_elev': base_elev,
        'droop_mult': droop_mult,
        'curl_mult': curl_mult,
        'spread_exp': spread_exp,
        'rng': rng
    }

def get_trunk_transform(z, height, dna):
    t = max(0.0, min(1.0, z / height))
    lx, ly = dna['lean']
    amp = dna['amp']
    freq = dna['freq']
    
    # 幹のS字〜多重屈曲
    cx = lx * (t ** 1.3) * height + amp * math.sin(t * math.pi * freq)
    cy = ly * (t ** 1.3) * height + amp * math.cos(t * math.pi * (freq * 0.85) + 0.5)
    rad = 0.22 * ((1.0 - t) ** 1.35) + 0.018
    return mathutils.Vector((cx, cy, z)), rad

def create_leaf_prototype():
    bm = bmesh.new()
    v_stem = bm.verts.new((0, 0, 0))
    v_l1 = bm.verts.new((-0.035, 0.04, 0.006))
    v_r1 = bm.verts.new((0.035, 0.04, 0.006))
    v_mid1 = bm.verts.new((0, 0.09, -0.010))
    v_l2 = bm.verts.new((-0.055, 0.09, 0.014))
    v_r2 = bm.verts.new((0.055, 0.09, 0.014))
    v_mid2 = bm.verts.new((0, 0.15, -0.016))
    v_l3 = bm.verts.new((-0.044, 0.15, 0.009))
    v_r3 = bm.verts.new((0.044, 0.15, 0.009))
    v_mid3 = bm.verts.new((0, 0.21, -0.024))
    v_l4 = bm.verts.new((-0.024, 0.21, 0.005))
    v_r4 = bm.verts.new((0.024, 0.21, 0.005))
    v_tip = bm.verts.new((0, 0.28, -0.048))

    bm.faces.new([v_stem, v_l1, v_mid1])
    bm.faces.new([v_stem, v_mid1, v_r1])
    bm.faces.new([v_l1, v_l2, v_mid1])
    bm.faces.new([v_r1, v_mid1, v_r2])
    bm.faces.new([v_mid1, v_l2, v_l3, v_mid2])
    bm.faces.new([v_mid1, v_mid2, v_r3, v_r2])
    bm.faces.new([v_mid2, v_l3, v_l4, v_mid3])
    bm.faces.new([v_mid2, v_mid3, v_r4, v_r3])
    bm.faces.new([v_mid3, v_l4, v_tip])
    bm.faces.new([v_mid3, v_tip, v_r4])

    mesh = bpy.data.meshes.new('Leaf_Prototype')
    bm.to_mesh(mesh)
    bm.free()
    for f in mesh.polygons: f.use_smooth = True
    return mesh

def create_materials():
    mat_bark = bpy.data.materials.new(name='M_Hiranoji_Bark')
    mat_bark.use_nodes = True
    nb = mat_bark.node_tree.nodes
    lb = mat_bark.node_tree.links
    nb.clear()

    out_b = nb.new(type='ShaderNodeOutputMaterial')
    bsdf_b = nb.new(type='ShaderNodeBsdfPrincipled')
    lb.new(bsdf_b.outputs['BSDF'], out_b.inputs['Surface'])

    coord_b = nb.new(type='ShaderNodeTexCoord')
    map_b = nb.new(type='ShaderNodeMapping')
    map_b.inputs['Scale'].default_value = (2.0, 2.0, 15.0)
    lb.new(coord_b.outputs['Object'], map_b.inputs['Vector'])

    noise_b = nb.new(type='ShaderNodeTexNoise')
    noise_b.inputs['Scale'].default_value = 10.0
    noise_b.inputs['Detail'].default_value = 8.0
    noise_b.inputs['Roughness'].default_value = 0.72
    lb.new(map_b.outputs['Vector'], noise_b.inputs['Vector'])

    ramp_b = nb.new(type='ShaderNodeValToRGB')
    ramp_b.color_ramp.elements[0].color = (0.09, 0.07, 0.05, 1.0)
    ramp_b.color_ramp.elements[1].color = (0.26, 0.21, 0.17, 1.0)
    lb.new(noise_b.outputs['Fac'], ramp_b.inputs['Fac'])
    lb.new(ramp_b.outputs['Color'], bsdf_b.inputs['Base Color'])

    bump_b = nb.new(type='ShaderNodeBump')
    bump_b.inputs['Strength'].default_value = 0.50
    lb.new(noise_b.outputs['Fac'], bump_b.inputs['Height'])
    lb.new(bump_b.outputs['Normal'], bsdf_b.inputs['Normal'])
    bsdf_b.inputs['Roughness'].default_value = 0.88

    mat_leaf = bpy.data.materials.new(name='M_Hiranoji_Leaves')
    mat_leaf.use_nodes = True
    nf = mat_leaf.node_tree.nodes
    lf = mat_leaf.node_tree.links
    nf.clear()

    out_f = nf.new(type='ShaderNodeOutputMaterial')
    bsdf_f = nf.new(type='ShaderNodeBsdfPrincipled')
    lf.new(bsdf_f.outputs['BSDF'], out_f.inputs['Surface'])

    coord_f = nf.new(type='ShaderNodeTexCoord')
    noise_f = nf.new(type='ShaderNodeTexNoise')
    noise_f.inputs['Scale'].default_value = 12.0
    noise_f.inputs['Detail'].default_value = 4.0
    lf.new(coord_f.outputs['Object'], noise_f.inputs['Vector'])

    ramp_f = nf.new(type='ShaderNodeValToRGB')
    ramp_f.color_ramp.elements[0].color = (0.10, 0.32, 0.05, 1.0)
    ramp_f.color_ramp.elements[1].color = (0.28, 0.62, 0.09, 1.0)
    lf.new(noise_f.outputs['Fac'], ramp_f.inputs['Fac'])
    lf.new(ramp_f.outputs['Color'], bsdf_f.inputs['Base Color'])

    bsdf_f.inputs['Roughness'].default_value = 0.38
    if 'Specular IOR Level' in bsdf_f.inputs:
        bsdf_f.inputs['Specular IOR Level'].default_value = 0.35
    elif 'Specular' in bsdf_f.inputs:
        bsdf_f.inputs['Specular'].default_value = 0.35

    if 'Subsurface Weight' in bsdf_f.inputs:
        bsdf_f.inputs['Subsurface Weight'].default_value = 0.60
        if 'Subsurface Radius' in bsdf_f.inputs:
            bsdf_f.inputs['Subsurface Radius'].default_value = (0.3, 0.6, 0.1)
    elif 'Subsurface' in bsdf_f.inputs:
        bsdf_f.inputs['Subsurface'].default_value = 0.60
        if 'Subsurface Color' in bsdf_f.inputs:
            bsdf_f.inputs['Subsurface Color'].default_value = (0.32, 0.75, 0.10, 1.0)

    return mat_bark, mat_leaf

def generate_hiranoji_tree(seed=TREE_SEED, height=TREE_HEIGHT, branch_count=BRANCH_COUNT, style=TREE_STYLE):
    mat_bark, mat_leaf = create_materials()
    leaf_proto = create_leaf_prototype()
    dna = get_tree_dna(seed, style)
    rng = dna['rng']

    # =========================================================================
    # 1. 幹（Trunk）を最初から純粋な「POLYGON MESH」として直接構築！
    # =========================================================================
    mesh_trunk = bpy.data.meshes.new('Tree_Trunk_Mesh')
    obj_trunk = bpy.data.objects.new('AAA_Tree_Trunk', mesh_trunk)
    bpy.context.collection.objects.link(obj_trunk)
    obj_trunk.data.materials.append(mat_bark)

    bm_trunk = bmesh.new()
    trunk_slices = 24
    trunk_sides = 12

    slice_rings = []
    for i in range(trunk_slices):
        z_curr = (i / (trunk_slices - 1)) * height
        center_pos, rad = get_trunk_transform(z_curr, height, dna)
        
        # 幹の接線ベクトル (Tangent) と法線基底
        if i < trunk_slices - 1:
            z_next = ((i + 1) / (trunk_slices - 1)) * height
            next_pos, _ = get_trunk_transform(z_next, height, dna)
            tan_z = (next_pos - center_pos).normalized()
        else:
            z_prev = ((i - 1) / (trunk_slices - 1)) * height
            prev_pos, _ = get_trunk_transform(z_prev, height, dna)
            tan_z = (center_pos - prev_pos).normalized()

        tan_x = tan_z.cross(mathutils.Vector((0, 1, 0)))
        if tan_x.length < 1e-3: tan_x = mathutils.Vector((1, 0, 0))
        else: tan_x.normalize()
        tan_y = tan_z.cross(tan_x).normalized()

        ring_verts = []
        for k in range(trunk_sides):
            ang = k * (2 * math.pi / trunk_sides)
            # 樹皮の微細な節（ノイズ）
            wobble = 1.0 + 0.04 * math.sin(k * 3.0 + i * 0.5)
            offset = (tan_x * math.cos(ang) + tan_y * math.sin(ang)) * (rad * wobble)
            v = bm_trunk.verts.new(center_pos + offset)
            ring_verts.append(v)
        slice_rings.append(ring_verts)

    # 幹のポリゴン面貼り
    for i in range(trunk_slices - 1):
        r1 = slice_rings[i]
        r2 = slice_rings[i + 1]
        for k in range(trunk_sides):
            kn = (k + 1) % trunk_sides
            bm_trunk.faces.new([r1[k], r2[k], r2[kn], r1[kn]])

    # 幹頭頂部のキャップ
    top_center_v = bm_trunk.verts.new(get_trunk_transform(height, height, dna)[0])
    top_ring = slice_rings[-1]
    for k in range(trunk_sides):
        kn = (k + 1) % trunk_sides
        bm_trunk.faces.new([top_ring[k], top_center_v, top_ring[kn]])

    bm_trunk.to_mesh(mesh_trunk)
    bm_trunk.free()
    for f in mesh_trunk.polygons: f.use_smooth = True

    # =========================================================================
    # 2. 枝（Branches & Twigs）＆ 葉（Leaves）
    # =========================================================================
    mesh_wood = bpy.data.meshes.new('Tree_Wood_Branches')
    obj_wood = bpy.data.objects.new('AAA_Tree_Wood', mesh_wood)
    bpy.context.collection.objects.link(obj_wood)
    obj_wood.data.materials.append(mat_bark)

    mesh_leaves = bpy.data.meshes.new('Tree_Leaves')
    obj_leaves = bpy.data.objects.new('AAA_Tree_Leaves', mesh_leaves)
    bpy.context.collection.objects.link(obj_leaves)
    obj_leaves.data.materials.append(mat_leaf)

    bm_wood = bmesh.new()
    bm_leaves = bmesh.new()
    proto_bm = bmesh.new()
    proto_bm.from_mesh(leaf_proto)

    def add_cylinder(bm, p1, p2, r1, r2, sides=6):
        v_diff = p2 - p1
        if v_diff.length < 1e-4: return
        z_axis = v_diff.normalized()
        x_axis = z_axis.cross(mathutils.Vector((0, 0, 1)))
        if x_axis.length < 1e-3: x_axis = mathutils.Vector((1, 0, 0))
        else: x_axis.normalize()
        y_axis = z_axis.cross(x_axis).normalized()

        ring1, ring2 = [], []
        for k in range(sides):
            ang = k * (2 * math.pi / sides)
            offset = x_axis * math.cos(ang) + y_axis * math.sin(ang)
            ring1.append(bm.verts.new(p1 + offset * r1))
            ring2.append(bm.verts.new(p2 + offset * r2))
        for k in range(sides):
            kn = (k + 1) % sides
            bm.faces.new([ring1[k], ring2[k], ring2[kn], ring1[kn]])

    def attach_leaf(bm_out, pos, direction, up_hint, scale=1.0, roll_ang=0.0):
        dir_norm = direction.normalized()
        side_norm = dir_norm.cross(up_hint).normalized()
        up_norm = side_norm.cross(dir_norm).normalized()

        rot_mat = mathutils.Matrix((
            (side_norm.x, dir_norm.x, up_norm.x),
            (side_norm.y, dir_norm.y, up_norm.y),
            (side_norm.z, dir_norm.z, up_norm.z)
        ))
        roll_mat = mathutils.Matrix.Rotation(roll_ang, 3, dir_norm)
        final_mat = roll_mat @ rot_mat

        v_map = {}
        for v in proto_bm.verts:
            p_rot = final_mat @ (v.co * scale)
            v_map[v] = bm_out.verts.new(pos + p_rot)
        for f in proto_bm.faces:
            bm_out.faces.new([v_map[v] for v in f.verts])

    # 3. 多彩な枝ぶり（DNAに基づくダイナミック変化）
    droop_mult = dna['droop_mult']
    curl_mult = dna['curl_mult']
    base_elev = dna['base_elev']
    spread_exp = dna['spread_exp']

    for i in range(branch_count):
        t = i / max(1, (branch_count - 1))
        z_root = 0.80 + t * (height * 0.80)

        # 黄金角にシード依存のクラスタリング・揺らぎを付与
        spiral_twist = rng.uniform(-0.15, 0.15) * curl_mult
        theta = i * math.radians(137.5) + spiral_twist

        trunk_center, r_trunk = get_trunk_transform(z_root, height, dna)

        # スタイルに応じた樹冠プロファイル（円錐〜ドーム傘〜楕円）
        canopy_shape = (1.0 - (t ** spread_exp) * 0.72) * (0.80 + 0.40 * math.sin(t * math.pi))
        b_len = max(0.40, 2.4 * canopy_shape * rng.uniform(0.85, 1.15))

        # 枝の仰角 (スタイルと高さで大きく変動)
        elev_angle = math.radians(base_elev + (t ** 0.8) * 32.0 + rng.uniform(-8, 8))
        dir_main = mathutils.Vector((
            math.cos(theta) * math.cos(elev_angle),
            math.sin(theta) * math.cos(elev_angle),
            math.sin(elev_angle)
        )).normalized()

        # 幹の芯からスタート（完全シームレス結合）
        curr_p = trunk_center + dir_main * (r_trunk * 0.15)
        branch_pts = [curr_p.copy()]
        b_radius = 0.028 * (1.0 - t * 0.60) * (0.8 + 0.4 * rng.random())

        # 各枝独自のうねりベクトル (Curvature DNA)
        wiggle_dir = dir_main.cross(mathutils.Vector((0, 0, 1))).normalized() * rng.uniform(-0.06, 0.06) * curl_mult

        seg_count = 6
        step_len = b_len / seg_count

        for s in range(seg_count):
            st = (s + 1) / seg_count
            # 激しく変わる下垂れ (Droop) & 横うねり (Curl)
            droop = -0.09 * droop_mult * math.sin(st * math.pi * 0.88)
            curr_p += dir_main * step_len + wiggle_dir * math.sin(st * math.pi)
            curr_p.z += droop
            branch_pts.append(curr_p.copy())

            # 小枝 (Twigs)
            if s >= 1:
                side_v = dir_main.cross(mathutils.Vector((0, 0, 1))).normalized()
                twig_dirs = [
                    (dir_main * 0.60 + side_v * 0.75 - mathutils.Vector((0, 0, 0.20 * droop_mult))).normalized(),
                    (dir_main * 0.60 - side_v * 0.75 - mathutils.Vector((0, 0, 0.20 * droop_mult))).normalized(),
                    (dir_main * 0.70 + mathutils.Vector((0, 0, 0.35))).normalized()
                ]

                for twig_dir in twig_dirs:
                    twig_len = step_len * rng.uniform(0.70, 1.30)
                    twig_tip = curr_p + twig_dir * twig_len
                    add_cylinder(bm_wood, curr_p, twig_tip, b_radius * 0.42, b_radius * 0.12, sides=4)

                    leaf_count = int(7 * CANOPY_DENSITY)
                    for lk in range(leaf_count):
                        lt = (lk + 1) / max(1, leaf_count)
                        l_pos = curr_p + (twig_tip - curr_p) * lt
                        l_side = twig_dir.cross(mathutils.Vector((0, 0, 1))).normalized()
                        sign = 1 if lk % 2 == 0 else -1
                        l_dir = (twig_dir * 0.6 + l_side * sign * 0.65 - mathutils.Vector((0, 0, 0.35 * droop_mult))).normalized()
                        l_scale = rng.uniform(0.78, 1.18) * (1.0 - t * 0.15)
                        attach_leaf(bm_leaves, l_pos, l_dir, mathutils.Vector((0, 0, 1)), scale=l_scale, roll_ang=rng.uniform(-0.4, 0.4))

            if s >= 2:
                for sign in [1, -1]:
                    side_v = dir_main.cross(mathutils.Vector((0, 0, 1))).normalized()
                    l_dir = (dir_main * 0.5 + side_v * sign * 0.7 - mathutils.Vector((0, 0, 0.25 * droop_mult))).normalized()
                    attach_leaf(bm_leaves, curr_p, l_dir, mathutils.Vector((0, 0, 1)), scale=rng.uniform(0.85, 1.15), roll_ang=rng.uniform(-0.3, 0.3))

        # 枝先の葉の房
        tip_leaves = int(8 * CANOPY_DENSITY)
        for lk in range(tip_leaves):
            ang = lk * (2 * math.pi / max(1, tip_leaves))
            s_vec = dir_main.cross(mathutils.Vector((0, 0, 1))).normalized()
            u_vec = s_vec.cross(dir_main).normalized()
            l_dir = (dir_main * 0.75 + (s_vec * math.cos(ang) + u_vec * math.sin(ang)) * 0.5 - mathutils.Vector((0, 0, 0.25 * droop_mult))).normalized()
            attach_leaf(bm_leaves, curr_p, l_dir, mathutils.Vector((0, 0, 1)), scale=rng.uniform(0.9, 1.2), roll_ang=rng.uniform(-0.3, 0.3))

        # 枝の円柱メッシュ生成
        for s in range(len(branch_pts) - 1):
            p_a = branch_pts[s]
            p_b = branch_pts[s + 1]
            rad_a = b_radius * (1.0 - (s / seg_count) * 0.75)
            rad_b = b_radius * (1.0 - ((s + 1) / seg_count) * 0.75)
            add_cylinder(bm_wood, p_a, p_b, rad_a, rad_b, sides=6)

    # 4. 梢クラウン
    top_center, _ = get_trunk_transform(height, height, dna)
    crown_count = int(24 * CANOPY_DENSITY)
    for k in range(crown_count):
        ang = k * (2 * math.pi / crown_count)
        l_dir = mathutils.Vector((math.cos(ang) * 0.6, math.sin(ang) * 0.6, 0.45 - 0.2 * math.cos(ang))).normalized()
        attach_leaf(bm_leaves, top_center, l_dir, mathutils.Vector((0, 0, 1)), scale=0.9, roll_ang=rng.uniform(-0.3, 0.3))

    bm_wood.to_mesh(mesh_wood)
    bm_wood.free()
    for f in mesh_wood.polygons: f.use_smooth = True

    bm_leaves.to_mesh(mesh_leaves)
    bm_leaves.free()
    for f in mesh_leaves.polygons: f.use_smooth = True

    proto_bm.free()
    return dna

def setup_sunlit_sky_environment():
    world = bpy.context.scene.world
    world.use_nodes = True
    nw = world.node_tree.nodes
    lw = world.node_tree.links
    nw.clear()

    out_w = nw.new(type='ShaderNodeOutputWorld')
    bg_w = nw.new(type='ShaderNodeBackground')
    lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

    coord_w = nw.new(type='ShaderNodeTexCoord')
    noise_w = nw.new(type='ShaderNodeTexNoise')
    noise_w.inputs['Scale'].default_value = 1.8
    noise_w.inputs['Detail'].default_value = 5.0
    lw.new(coord_w.outputs['Generated'], noise_w.inputs['Vector'])

    ramp_w = nw.new(type='ShaderNodeValToRGB')
    ramp_w.color_ramp.elements[0].color = (0.22, 0.46, 0.82, 1.0)
    ramp_w.color_ramp.elements[1].color = (0.85, 0.90, 0.96, 1.0)
    lw.new(noise_w.outputs['Fac'], ramp_w.inputs['Fac'])
    lw.new(ramp_w.outputs['Color'], bg_w.inputs['Color'])
    bg_w.inputs['Strength'].default_value = 1.25

    bpy.ops.object.light_add(type='SUN', location=(10.0, -10.0, 15.0))
    sun = bpy.context.active_object
    sun.data.energy = 4.8
    sun.data.color = (1.0, 0.98, 0.92)
    sun.rotation_euler = (math.radians(48), math.radians(16), math.radians(-35))

    bpy.ops.object.light_add(type='AREA', location=(-6.0, 8.0, 6.0))
    fill = bpy.context.active_object
    fill.data.energy = 380
    fill.data.size = 8.0
    fill.data.color = (0.6, 0.8, 1.0)

    bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Ground_Floor'
    fmat = bpy.data.materials.new('Ground_Mat')
    fmat.use_nodes = True
    bsdf = fmat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.12, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
    floor.data.materials.append(fmat)

def render_cut(filepath, cam_pos, target_pos, lens=42, samples=32):
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

    scene = bpy.context.scene
    scene.camera = cam
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
    actual_seed = random.randint(1, 999999) if USE_RANDOM_SEED else TREE_SEED
    clear_scene()
    tree_dna = generate_hiranoji_tree(seed=actual_seed)
    setup_sunlit_sky_environment()

    if bpy.app.background:
        assets_dir = 'e:/BlenderPreFix/catalog/assets'
        os.makedirs(assets_dir, exist_ok=True)

        render_cut(os.path.join(assets_dir, 'aaa_conifer_pine_cut1.png'), (2.4, -3.8, 1.6), (0, 0, 3.2), lens=34)
        render_cut(os.path.join(assets_dir, 'aaa_conifer_pine.png'), (2.4, -3.8, 1.6), (0, 0, 3.2), lens=34)
        render_cut(os.path.join(assets_dir, 'aaa_conifer_pine_cut2.png'), (5.5, -6.8, 2.8), (0, 0, 2.5), lens=42)
        render_cut(os.path.join(assets_dir, 'aaa_conifer_pine_cut3.png'), (1.2, -1.8, 2.6), (0.1, 0, 2.65), lens=60)
        render_cut(os.path.join(assets_dir, 'aaa_conifer_pine_cut4.png'), (-4.5, 5.5, 4.2), (0, 0, 2.6), lens=40)

        glb_path = os.path.join(assets_dir, 'aaa_conifer_pine.glb')
        for obj in bpy.data.objects:
            if 'Ground_Floor' in obj.name: obj.select_set(False)
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
        style_name = tree_dna['style']
        print(f'=== 🌲 平の字様式プロシージャル樹木 生成完了！ (Seed: {actual_seed} / スタイル: {style_name}) ===')
        print(f'💡 再び「▶」(Alt+P)を押すと、次のランダムな樹木が即座に生成されます！')

if __name__ == '__main__':
    main()
