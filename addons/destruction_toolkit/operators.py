import random

import bpy

from . import effects, fracture_core, shapes

IMPACT_FRAME = 8


class DESTRUCTION_OT_place_object(bpy.types.Operator):
    bl_idname = "destruction.place_object"
    bl_label = "Place Destructible Object"
    bl_description = "3Dカーソル位置にプロシージャルな被破壊オブジェクトを配置する"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.destruction_toolkit
        cursor = context.scene.cursor.location.copy()
        seed_val = props.seed if props.seed else random.randint(1, 999999)

        target, ground, hit_pos_local = shapes.build_shape(props.shape_type, seed_val)
        target.location = (
            target.location.x + cursor.x,
            target.location.y + cursor.y,
            target.location.z + cursor.z,
        )
        ground.location = (
            ground.location.x + cursor.x,
            ground.location.y + cursor.y,
            ground.location.z + cursor.z,
        )
        # 衝突を狙う目安として3Dカーソルを形状のヒット位置へ寄せる(手動で動かし直せる)。
        context.scene.cursor.location = (
            hit_pos_local[0] + cursor.x,
            hit_pos_local[1] + cursor.y,
            hit_pos_local[2] + cursor.z,
        )

        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
        context.view_layer.objects.active = target

        self.report({"INFO"}, f"Placed '{target.name}' (seed={seed_val})")
        return {"FINISHED"}


class DESTRUCTION_OT_fracture_selected(bpy.types.Operator):
    bl_idname = "destruction.fracture_selected"
    bl_label = "Fracture Selected Object"
    bl_description = (
        "選択中のオブジェクト(配置したもの/シーンにある任意のメッシュ)を"
        "Cell Fractureで破片に分解し、固定接合の剛体ネットワークを作る"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and not obj.get("is_destruction_ground")

    def execute(self, context):
        props = context.scene.destruction_toolkit
        target = context.active_object

        ground = fracture_core.find_or_create_ground(target)
        fracture_core.ensure_ground_passive_body(ground)

        seed_val = props.seed if props.seed else random.randint(1, 999999)
        shards = fracture_core.fracture_object(target, props.shard_count, props.shard_noise, seed_val)
        if not shards:
            self.report({"ERROR"}, "破砕結果が0個でした(Shard Countを見直してください)")
            return {"CANCELLED"}

        bpy.ops.object.select_all(action="DESELECT")
        for s in shards:
            s.select_set(True)
        context.view_layer.objects.active = shards[0]

        self.report({"INFO"}, f"Fractured into {len(shards)} shards")
        return {"FINISHED"}


class DESTRUCTION_OT_trigger_collapse(bpy.types.Operator):
    bl_idname = "destruction.trigger_collapse"
    bl_label = "Trigger Collapse"
    bl_description = "破砕済みの破片に対して衝突崩壊または自然崩壊をベイクする"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return any(o.get("destruction_shard") for o in context.scene.objects)

    def execute(self, context):
        props = context.scene.destruction_toolkit
        scene = context.scene
        shards = [o for o in scene.objects if o.get("destruction_shard")]
        if not shards:
            self.report({"ERROR"}, "破砕済みの破片が見つかりません。先にFracture Selectedを実行してください")
            return {"CANCELLED"}

        scene.frame_start = 1
        scene.frame_end = props.total_frames
        if not scene.rigidbody_world:
            bpy.ops.rigidbody.world_add()
        scene.rigidbody_world.point_cache.frame_start = 1
        scene.rigidbody_world.point_cache.frame_end = props.total_frames
        scene.rigidbody_world.time_scale = props.time_scale
        scene.rigidbody_world.enabled = True

        ground = fracture_core.find_or_create_ground(shards[0])
        fracture_core.ensure_ground_passive_body(ground)

        ball = None

        if props.collapse_mode == "IMPACT":
            hit_pos = tuple(scene.cursor.location)

            fracture_core.apply_kinematic_freeze(shards, freeze_until_frame=IMPACT_FRAME - 1)
            uniform_threshold = (props.breaking_threshold_min + props.breaking_threshold_max) * 0.5
            fracture_core.set_uniform_breaking_threshold(shards, uniform_threshold)

            ball = fracture_core.spawn_cannonball_and_shockwave(
                hit_pos,
                props.seed,
                props.ball_size,
                props.impact_angle_h,
                props.impact_angle_v,
                props.shock_power,
                IMPACT_FRAME,
            )

            if props.enable_sparks:
                effects.add_sparks(hit_pos, props.spark_count, props.spark_speed, IMPACT_FRAME)
            if props.enable_explode_debris:
                effects.add_explode_debris(hit_pos, props.explode_piece_count, IMPACT_FRAME)
            if props.enable_mantaflow_fire:
                effects.add_mantaflow_fire_smoke(hit_pos, IMPACT_FRAME, props.total_frames)
        else:  # NATURAL
            fracture_core.randomize_breaking_thresholds(
                shards, props.breaking_threshold_min, props.breaking_threshold_max
            )

        fracture_core.bake_simulation_to_keyframes(
            shards, ball=ball, total_frames=props.total_frames, time_scale=props.time_scale
        )

        for s in shards:
            if s.name in bpy.data.objects:
                s["destruction_shard"] = True  # bake処理はプロパティに触れないはずだが念のため保持

        scene.frame_set(1)
        self.report({"INFO"}, f"Collapse baked ({props.collapse_mode})")
        return {"FINISHED"}


classes = (
    DESTRUCTION_OT_place_object,
    DESTRUCTION_OT_fracture_selected,
    DESTRUCTION_OT_trigger_collapse,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
