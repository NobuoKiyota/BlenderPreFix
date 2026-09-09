"""衝突崩壊(Impact)時のみ選択可能な追加エフェクト: 火花・Explode微細粉砕・Mantaflow炎/煙。

generators/gen_destruction_scene.py の setup_explosion_effects を、トグルごとに
独立した関数へ分割して移植したもの。Mantaflow部分は同セッションで実機検証済みの
2つの罠(炎源メッシュのhide_render漏れ、キャッシュ相対パス解決失敗)を修正済みの
状態で反映している。
"""

import os
import tempfile
import uuid

import bmesh
import bpy


def create_spark_material():
    mat = bpy.data.materials.new(name="Mat_Destruction_Spark")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type="ShaderNodeOutputMaterial")
    emit = nodes.new(type="ShaderNodeEmission")
    emit.inputs["Color"].default_value = (1.0, 0.45, 0.05, 1.0)
    emit.inputs["Strength"].default_value = 25.0
    mat.node_tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def create_fire_smoke_material():
    mat = bpy.data.materials.new(name="Mat_Destruction_FireSmoke")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type="ShaderNodeOutputMaterial")
    vol = nodes.new(type="ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 4.0
    vol.inputs["Blackbody Intensity"].default_value = 1.5
    vol.inputs["Blackbody Tint"].default_value = (1.0, 0.5, 0.1, 1.0)
    vol.inputs["Temperature"].default_value = 1600.0
    mat.node_tree.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return mat


def _ensure_spark_instance_mesh(spark_mat):
    spark_instance = bpy.data.objects.get("Destruction_Spark_Instance")
    if spark_instance:
        return spark_instance
    mesh = bpy.data.meshes.new("Destruction_Spark_Instance")
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.035)
    bm.to_mesh(mesh)
    bm.free()
    spark_instance = bpy.data.objects.new("Destruction_Spark_Instance", mesh)
    bpy.context.scene.collection.objects.link(spark_instance)
    spark_instance.data.materials.append(spark_mat)
    spark_instance.location = (0, 0, -20.0)
    spark_instance.hide_render = True
    return spark_instance


def add_sparks(hit_pos, spark_count, spark_speed, impact_frame):
    """衝突瞬間の爆散火花パーティクル。"""
    spark_mat = create_spark_material()
    spark_instance = _ensure_spark_instance_mesh(spark_mat)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=hit_pos)
    emitter = bpy.context.active_object
    emitter.name = "Destruction_Spark_Emitter"
    emitter.display_type = "WIRE"
    emitter.hide_render = True

    emitter.modifiers.new("Sparks", "PARTICLE_SYSTEM")
    settings = emitter.particle_systems[0].settings
    settings.count = int(spark_count)
    settings.frame_start = float(impact_frame)
    settings.frame_end = float(impact_frame + 2)
    settings.lifetime = 45.0
    settings.lifetime_random = 0.5
    settings.normal_factor = float(spark_speed)
    settings.factor_random = 8.0
    settings.effector_weights.gravity = 0.45
    settings.render_type = "OBJECT"
    settings.instance_object = spark_instance
    settings.particle_size = 0.8
    settings.size_random = 0.75
    return emitter


def add_explode_debris(hit_pos, piece_count, impact_frame):
    """Explodeモディファイアによる瞬間粉砕メッシュ(微細な砕け散り)。"""
    spark_mat = create_spark_material()

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.45, location=hit_pos)
    shatter_ball = bpy.context.active_object
    shatter_ball.name = "Destruction_MicroDebris"
    shatter_ball.data.materials.append(spark_mat)

    bpy.ops.object.particle_system_add()
    settings = shatter_ball.particle_systems[0].settings
    settings.count = int(piece_count)
    settings.frame_start = float(impact_frame)
    settings.frame_end = float(impact_frame + 1)
    settings.lifetime = 60.0
    settings.normal_factor = 14.0
    settings.factor_random = 6.0
    settings.effector_weights.gravity = 0.60
    settings.render_type = "NONE"

    exp_mod = shatter_ball.modifiers.new("Explode", "EXPLODE")
    exp_mod.use_edge_cut = True
    exp_mod.show_unborn = False
    exp_mod.show_dead = True
    return shatter_ball


def add_mantaflow_fire_smoke(hit_pos, impact_frame, total_frames):
    """本格的なMantaflow火炎・煙ボリューム。

    実機検証で確認した2つの罠を修正済み:
    1. 炎源メッシュ(Flow役)はhide_render=Trueにしないと、既定の灰色マテリアルの
       不透明球が炎の中心に重なって炎を隠してしまう。
    2. ドメインのcache_directoryは絶対パスに固定する(既定の相対パス "//.." は
       シーン未保存時に解決できずキャッシュが正しく書き出されないことがある)。
    """
    fire_smoke_mat = create_fire_smoke_material()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=hit_pos)
    flow_obj = bpy.context.active_object
    flow_obj.name = "Destruction_FireSmoke_Flow"
    flow_obj.hide_render = True
    flow_mod = flow_obj.modifiers.new("Fluid", "FLUID")
    flow_mod.fluid_type = "FLOW"
    flow_mod.flow_settings.flow_type = "BOTH"
    flow_mod.flow_settings.flow_behavior = "INFLOW"
    flow_mod.flow_settings.fuel_amount = 2.0
    flow_mod.flow_settings.use_inflow = True
    flow_obj.keyframe_insert(data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=1)
    flow_obj.keyframe_insert(data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=impact_frame)
    flow_mod.flow_settings.use_inflow = False
    flow_obj.keyframe_insert(
        data_path='modifiers["Fluid"].flow_settings.use_inflow', frame=impact_frame + 5
    )

    hx, hy, hz = hit_pos
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, hy, hz + 0.8))
    domain = bpy.context.active_object
    domain.name = "Destruction_FireSmoke_Domain"
    domain.scale = (5.0, 5.0, 4.5)
    bpy.ops.object.transform_apply(scale=True)
    domain_mod = domain.modifiers.new("Fluid", "FLUID")
    domain_mod.fluid_type = "DOMAIN"
    domain_mod.domain_settings.domain_type = "GAS"
    domain_mod.domain_settings.resolution_max = 64
    domain_mod.domain_settings.cache_frame_start = 1
    domain_mod.domain_settings.cache_frame_end = int(total_frames)
    cache_dir = os.path.join(tempfile.gettempdir(), "destruction_toolkit_fluid_cache", uuid.uuid4().hex)
    os.makedirs(cache_dir, exist_ok=True)
    domain_mod.domain_settings.cache_directory = cache_dir
    domain.data.materials.append(fire_smoke_mat)

    # bpy.ops.fluid.bake_all() はGUIのモーダル操作のため、スクリプト/バックグラウンド
    # 実行では最初の数フレームしか進まない(ProcVFXのMantaflowデバッグで確認済みの罠)。
    # scene.frame_set()でフレームを1つずつ進めるとGUI再生時と同じ経路で確実に進む。
    # 実際のベイクは fracture_core.bake_simulation_to_keyframes 内のフレームステップ
    # ループが剛体と同時に副作用として行うため、ここでは明示的なベイクは行わない。

    return flow_obj, domain
