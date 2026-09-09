import bpy


class DestructionToolkitProps(bpy.types.PropertyGroup):
    # --- 1. 配置 ---
    shape_type: bpy.props.EnumProperty(
        name="Shape",
        description="配置するプロシージャル形状(RANDOMは毎回ランダム選定)",
        items=[
            ("RANDOM", "Random", "毎回ランダムに選ぶ"),
            ("ROCK", "Rock", "ゴツゴツした巨岩"),
            ("WALL", "Wall", "荒削りな崖・石壁"),
            ("PILLAR", "Pillar", "石柱"),
            ("BUILDING", "Building", "中空タワー"),
            ("GROUND", "Ground", "地割れする地面スラブ"),
        ],
        default="RANDOM",
    )

    # --- 2. 分解(Fracture) ---
    shard_count: bpy.props.IntProperty(
        name="Shard Count", description="破片の目安数", default=60, min=4, max=400
    )
    shard_noise: bpy.props.FloatProperty(
        name="Shard Noise", description="破片形状のランダム性", default=0.5, min=0.0, max=1.0
    )
    seed: bpy.props.IntProperty(name="Seed", default=0, min=0)

    # --- 3. 崩壊トリガー(共通) ---
    collapse_mode: bpy.props.EnumProperty(
        name="Collapse Mode",
        items=[
            ("IMPACT", "Impact", "外部からの衝突(砲弾)で一気に崩壊させる"),
            ("NATURAL", "Natural", "衝突なし。接合部の強度差で自然に(崖崩れのように)崩れる"),
        ],
        default="IMPACT",
    )
    breaking_threshold_min: bpy.props.FloatProperty(
        name="Breaking Threshold Min",
        description="接合部が壊れる衝撃の下限(小さいほど脆い)。Naturalではこの範囲でランダム化される",
        default=1.0,
        min=0.01,
    )
    breaking_threshold_max: bpy.props.FloatProperty(
        name="Breaking Threshold Max",
        description="接合部が壊れる衝撃の上限。Impactではこの幅の中間的な値が全体に均一適用される",
        default=4.0,
        min=0.01,
    )
    total_frames: bpy.props.IntProperty(name="Total Frames", default=100, min=10, max=1000)
    time_scale: bpy.props.FloatProperty(name="Time Scale", default=0.5, min=0.05, max=2.0)

    # --- Impact専用 ---
    impact_angle_h: bpy.props.FloatProperty(name="Impact Angle H", default=0.0, min=-60.0, max=60.0)
    impact_angle_v: bpy.props.FloatProperty(name="Impact Angle V", default=8.0, min=0.0, max=30.0)
    ball_size: bpy.props.FloatProperty(name="Ball Size", default=0.55, min=0.1, max=2.0)
    shock_power: bpy.props.FloatProperty(name="Shock Power", default=5500.0, min=0.0, max=50000.0)

    enable_sparks: bpy.props.BoolProperty(name="Sparks", default=True)
    spark_count: bpy.props.IntProperty(name="Spark Count", default=350, min=0, max=5000)
    spark_speed: bpy.props.FloatProperty(name="Spark Speed", default=18.0, min=0.0, max=100.0)
    enable_explode_debris: bpy.props.BoolProperty(name="Explode Micro-Debris", default=True)
    explode_piece_count: bpy.props.IntProperty(name="Explode Piece Count", default=200, min=0, max=2000)
    enable_mantaflow_fire: bpy.props.BoolProperty(
        name="Mantaflow Fire/Smoke",
        description="本格的な流体シミュレーションの炎・煙(生成に数秒〜数十秒かかる)",
        default=False,
    )


classes = (DestructionToolkitProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.destruction_toolkit = bpy.props.PointerProperty(type=DestructionToolkitProps)


def unregister():
    del bpy.types.Scene.destruction_toolkit
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
