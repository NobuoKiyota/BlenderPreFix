import bpy


class VIEW3D_PT_destruction_toolkit(bpy.types.Panel):
    bl_label = "Destruction Toolkit"
    bl_idname = "VIEW3D_PT_destruction_toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Destruction"

    def draw(self, context):
        layout = self.layout
        props = context.scene.destruction_toolkit

        box1 = layout.box()
        box1.label(text="1. Place", icon="MESH_ICOSPHERE")
        box1.prop(props, "shape_type", text="")
        box1.operator("destruction.place_object", icon="ADD")
        box1.label(text="(既にシーンにあるメッシュを選ぶだけでも可)", icon="INFO")

        box2 = layout.box()
        box2.label(text="2. Fracture", icon="MOD_EXPLODE")
        col2 = box2.column(align=True)
        col2.prop(props, "shard_count")
        col2.prop(props, "shard_noise", slider=True)
        col2.prop(props, "seed")
        box2.operator("destruction.fracture_selected", icon="MOD_EXPLODE")

        box3 = layout.box()
        box3.label(text="3. Collapse", icon="FORCE_TURBULENCE")
        box3.prop(props, "collapse_mode", expand=True)
        col3 = box3.column(align=True)
        col3.prop(props, "breaking_threshold_min")
        col3.prop(props, "breaking_threshold_max")
        col3.prop(props, "total_frames")
        col3.prop(props, "time_scale", slider=True)

        if props.collapse_mode == "IMPACT":
            impact_box = box3.box()
            impact_box.label(text="Impact (3Dカーソル位置を狙う)")
            colh = impact_box.column(align=True)
            colh.prop(props, "impact_angle_h", slider=True)
            colh.prop(props, "impact_angle_v", slider=True)
            colh.prop(props, "ball_size", slider=True)
            colh.prop(props, "shock_power")

            fx_box = box3.box()
            fx_box.label(text="Effects", icon="PARTICLES")
            fx_box.prop(props, "enable_sparks")
            if props.enable_sparks:
                row = fx_box.row(align=True)
                row.prop(props, "spark_count")
                row.prop(props, "spark_speed")
            fx_box.prop(props, "enable_explode_debris")
            if props.enable_explode_debris:
                fx_box.prop(props, "explode_piece_count")
            fx_box.prop(props, "enable_mantaflow_fire")

        box3.operator("destruction.trigger_collapse", icon="PLAY")


classes = (VIEW3D_PT_destruction_toolkit,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
