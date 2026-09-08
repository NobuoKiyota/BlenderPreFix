import bpy
import bmesh
import math
import sys
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

# 1. マテリアル（テクスチャはスルー、クリーンなPBRシェーダー）
def create_leather_cover_material():
    mat = bpy.data.materials.new(name="Book_Cover_Leather_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 深みのあるアンティークバーガンディ（ワインレッドレザー）
    bsdf.inputs['Base Color'].default_value = (0.15, 0.03, 0.04, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    
    # 微細な革シボバンプ
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 45.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "Leather"
    mat["audio_tag"] = "Sound_Book_Close_Thud"
    return mat

def create_paper_material():
    mat = bpy.data.materials.new(name="Book_Page_Paper_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    # 生成りの上質紙（わずかに温かみのあるオフホワイト）
    bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 0.84, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat["surface_type"] = "Paper"
    mat["audio_tag"] = "Sound_Page_Turn_Whoosh"
    return mat

def create_pages_block_material():
    mat = bpy.data.materials.new(name="Book_Pages_Block_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.86, 0.83, 0.76, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    # 小口（紙の積層スリット）のバンプ
    tex_wave = nodes.new(type='ShaderNodeTexWave')
    tex_wave.inputs['Scale'].default_value = 120.0
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    
    links.new(tex_wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    mat["surface_type"] = "PaperBlock"
    mat["audio_tag"] = "Sound_Page_Riffle"
    return mat

def create_spine_ribbon_material():
    mat = bpy.data.materials.new(name="Book_Spine_Ribbon_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # しおり紐・金の箔押し風アクセント
        bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.15, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.25
    return mat

# 2. メッシュ＆リグ構築
def build_book_and_page_turn():
    cover_mat = create_leather_cover_material()
    paper_mat = create_paper_material()
    block_mat = create_pages_block_material()
    gold_mat = create_spine_ribbon_material()
    
    # 1. 背表紙 (Spine)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.02))
    spine = bpy.context.active_object
    spine.name = "Book_Spine"
    spine.scale = (0.16, 2.2, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    spine.data.materials.append(cover_mat)
    
    # 2. 左右のハードカバー（開いた状態）
    # 左カバー
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.83, 0, 0.02))
    left_cover = bpy.context.active_object
    left_cover.name = "Book_Cover_Left"
    left_cover.scale = (1.5, 2.2, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    left_cover.data.materials.append(cover_mat)
    
    # 右カバー
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.83, 0, 0.02))
    right_cover = bpy.context.active_object
    right_cover.name = "Book_Cover_Right"
    right_cover.scale = (1.5, 2.2, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    right_cover.data.materials.append(cover_mat)
    
    # 3. 左右のページ束（ブロック）
    # 左ページブロック
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.75, 0, 0.09))
    left_block = bpy.context.active_object
    left_block.name = "Book_Pages_Block_Left"
    left_block.scale = (1.35, 2.05, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    left_block.data.materials.append(block_mat)
    
    # 右ページブロック
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.75, 0, 0.09))
    right_block = bpy.context.active_object
    right_block.name = "Book_Pages_Block_Right"
    right_block.scale = (1.35, 2.05, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    right_block.data.materials.append(block_mat)
    
    # 4. めくれるページ（Turning Page 1）の作成
    # 平面を作成し、原点を綴じ目（X=0）に配置
    bm = bmesh.new()
    page_w = 1.35
    page_h = 2.05
    x_segs = 32
    y_segs = 12
    
    # グリッド頂点（X: 0.0 -> page_w, Y: -page_h/2 -> page_h/2）
    grid_verts = []
    for yi in range(y_segs + 1):
        row = []
        y = -page_h/2 + (page_h / y_segs) * yi
        for xi in range(x_segs + 1):
            x = (page_w / x_segs) * xi
            # 右側から左側へめくれ上がる放物線アーチ（空中でのしなり状態）
            # h_ratio: 0(綴じ目) -> 1(先端)
            ratio = xi / x_segs
            # アーチの高さ: 途中で高く持ち上がり、先端が下へ垂れ下がる
            z = 0.14 + 0.65 * math.sin(ratio * math.pi * 0.85)
            # ねじれと横方向のカーブ
            x_curved = x * (0.3 + 0.7 * math.cos(ratio * 1.8))
            v = bm.verts.new((x_curved, y, z))
            row.append(v)
        grid_verts.append(row)
        
    for yi in range(y_segs):
        for xi in range(x_segs):
            v1 = grid_verts[yi][xi]
            v2 = grid_verts[yi][xi+1]
            v3 = grid_verts[yi+1][xi+1]
            v4 = grid_verts[yi+1][xi]
            bm.faces.new([v1, v2, v3, v4])
            
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh1 = bpy.data.meshes.new("Turning_Page_Mesh_1")
    bm.to_mesh(mesh1)
    bm.free()
    
    page1 = bpy.data.objects.new("Turning_Page_1", mesh1)
    bpy.context.collection.objects.link(page1)
    page1.data.materials.append(paper_mat)
    for p in page1.data.polygons:
        p.use_smooth = True
        
    # 厚み付け（Solidify）で本物の紙の極薄な厚み
    sol1 = page1.modifiers.new("Solidify", 'SOLIDIFY')
    sol1.thickness = 0.003
    sub1 = page1.modifiers.new("Subsurf", 'SUBSURF')
    sub1.levels = 1
    sub1.render_levels = 2
    
    # 5. 2枚目の追従ページ（Turning Page 2）
    # 1枚目の直後を追いかけるように少し低い角度でめくれ始める
    bm2 = bmesh.new()
    grid_verts2 = []
    for yi in range(y_segs + 1):
        row = []
        y = -page_h/2 + (page_h / y_segs) * yi
        for xi in range(x_segs + 1):
            x = (page_w / x_segs) * xi
            ratio = xi / x_segs
            z = 0.14 + 0.32 * math.sin(ratio * math.pi * 0.7)
            x_curved = x * (0.6 + 0.4 * math.cos(ratio * 1.2))
            v = bm2.verts.new((x_curved, y, z))
            row.append(v)
        grid_verts2.append(row)
        
    for yi in range(y_segs):
        for xi in range(x_segs):
            v1 = grid_verts2[yi][xi]
            v2 = grid_verts2[yi][xi+1]
            v3 = grid_verts2[yi+1][xi+1]
            v4 = grid_verts2[yi+1][xi]
            bm2.faces.new([v1, v2, v3, v4])
            
    bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)
    mesh2 = bpy.data.meshes.new("Turning_Page_Mesh_2")
    bm2.to_mesh(mesh2)
    bm2.free()
    
    page2 = bpy.data.objects.new("Turning_Page_2", mesh2)
    bpy.context.collection.objects.link(page2)
    page2.data.materials.append(paper_mat)
    for p in page2.data.polygons:
        p.use_smooth = True
        
    sol2 = page2.modifiers.new("Solidify", 'SOLIDIFY')
    sol2.thickness = 0.003
    
    # 6. しおりリボン（Book Ribbon）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=2.4, location=(0, -0.2, 0.16))
    ribbon = bpy.context.active_object
    ribbon.name = "Book_Ribbon"
    ribbon.rotation_euler = (math.radians(90), 0, math.radians(12))
    ribbon.data.materials.append(gold_mat)
    
    return spine, left_cover, right_cover, left_block, right_block, page1, page2, ribbon

def setup_camera(pos, rot_deg, lens=50):
    cam_data = bpy.data.cameras.new(name="Cam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name="Cam", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = pos
    cam_obj.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    bpy.context.scene.camera = cam_obj
    return cam_obj

def setup_lighting():
    # キーライト（温かい書斎・ライブラリの照明）
    light_key = bpy.data.lights.new(name="KeyLight", type='AREA')
    light_key.energy = 450.0
    light_key.size = 2.0
    light_key.color = (1.0, 0.95, 0.88)
    key_obj = bpy.data.objects.new("KeyLight", light_key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (2.2, -2.5, 3.2)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(35))
    
    # フィルライト（柔らかな反射光）
    light_fill = bpy.data.lights.new(name="FillLight", type='AREA')
    light_fill.energy = 180.0
    light_fill.size = 3.0
    light_fill.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", light_fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-2.8, -1.8, 2.5)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-50))
    
    # ワールド背景（落ち着いたスタジオダークグレー）
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.025, 0.03, 1.0)
        bg.inputs['Strength'].default_value = 0.4

def render_cut(filepath, pos, rot_deg, lens=50, samples=32):
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
    build_book_and_page_turn()
    setup_lighting()
    
    assets_dir = r"e:\BlenderPreFix\catalog\assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. 3D GLB エクスポート
    glb_path = os.path.join(assets_dir, "book_page_turn.glb")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"Exported high quality GLB: {glb_path}")
    
    # 2. マルチカット Cycles レンダリング (全4カット)
    # Cut 1: 正面斜めシネマティック全体像（めくりページが美しく空中をアーチ状にしなる）
    render_cut(
        os.path.join(assets_dir, "book_page_turn_cut1.png"),
        pos=(2.2, -2.8, 2.2),
        rot_deg=(58, 0, 36),
        lens=50
    )
    # サムネイル用
    render_cut(
        os.path.join(assets_dir, "book_page_turn.png"),
        pos=(2.2, -2.8, 2.2),
        rot_deg=(58, 0, 36),
        lens=50
    )
    
    # Cut 2: ページのしなり曲面クローズアップ（アーチ状の湾曲と影）
    render_cut(
        os.path.join(assets_dir, "book_page_turn_cut2.png"),
        pos=(1.2, -1.4, 1.2),
        rot_deg=(65, 0, 38),
        lens=75
    )
    
    # Cut 3: 45°斜め上俯瞰（本全体のレイアウトと左右のページブロック構造）
    render_cut(
        os.path.join(assets_dir, "book_page_turn_cut3.png"),
        pos=(0.4, -2.2, 3.2),
        rot_deg=(42, 0, 10),
        lens=42
    )
    
    # Cut 4: 綴じ目と背表紙のローアングル（ヒンジ構造と厚み）
    render_cut(
        os.path.join(assets_dir, "book_page_turn_cut4.png"),
        pos=(2.0, -1.2, 0.6),
        rot_deg=(80, 0, 58),
        lens=40
    )

if __name__ == "__main__":
    main()
