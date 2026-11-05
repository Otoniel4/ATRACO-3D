"""Herramientas comunes de arte propio de Alarma. Escala: metros; frente: -Y."""
import bpy
import math
import json
from mathutils import Vector
from pathlib import Path

ART = Path(__file__).resolve().parent.parent
OUTPUTS = ART / "Previews~" / "Catalog"
PALETTE = {
    "Apricot": "EF9B59", "Terracotta": "C9684F", "Coral": "DF7966",
    "Cream": "F4E4C1", "Mustard": "E6BB55", "Teal": "397C78",
    "Sage": "87A885", "Leaf": "579267", "Navy": "293C55",
    "Asphalt": "414B52", "Metal": "84949A", "Glass": "91C5CF",
    "Ivory": "FFF7DF", "Rubber": "27313A", "PoliceRed": "DE5853",
    "PoliceBlue": "4D88D8", "Wood": "AE7851", "Berry": "A15A78",
    "SkinLight": "E9B68D", "SkinMedium": "C88D65", "SkinDeep": "81533F",
    "HairBrown": "5B3B33", "HairBlack": "2B2930", "HairGold": "C99B52",
}
CATALOG = globals().get("CATALOG", {})
ROOT = None
COLLECTION = None

def linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

def mat(name):
    material = bpy.data.materials.get("Alarma_" + name)
    if material:
        return material
    value = PALETTE[name]
    color = tuple(linear(int(value[i:i+2], 16) / 255) for i in (0, 2, 4))
    material = material or bpy.data.materials.new("Alarma_" + name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    shader = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None) or nodes.new("ShaderNodeBsdfPrincipled")
    output = next((node for node in nodes if node.type == "OUTPUT_MATERIAL"), None) or nodes.new("ShaderNodeOutputMaterial")
    material.node_tree.links.new(shader.outputs[0], output.inputs[0])
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.82
    return material

def fast_box(name, location, size, material="Cream", bevel=0, parent=None, rotation=None):
    x,y,z=(value/2 for value in size)
    vertices=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj=mesh(name,vertices,faces,material,parent)
    obj.location=location
    if rotation:obj.rotation_euler=rotation
    return obj

def new_scene(name):
    scene = bpy.data.scenes.new("Alarma_" + name)
    bpy.context.window.scene = scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    # Blender 5 llama BLENDER_EEVEE al motor que en 4.2–4.5 era BLENDER_EEVEE_NEXT.
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1100
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = 0.25
    world = bpy.data.worlds.get("Alarma_WarmWorld") or bpy.data.worlds.new("Alarma_WarmWorld")
    world.use_nodes = True
    background = next((node for node in world.node_tree.nodes if node.type == "BACKGROUND"), None) or world.node_tree.nodes.new("ShaderNodeBackground")
    output = next((node for node in world.node_tree.nodes if node.type == "OUTPUT_WORLD"), None) or world.node_tree.nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(background.outputs[0], output.inputs[0])
    background.inputs[0].default_value = (0.65, 0.73, 0.85, 1)
    background.inputs[1].default_value = 0.65
    scene.world = world
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                shading = area.spaces.active.shading
                shading.type = "SOLID"
                shading.color_type = "MATERIAL"
                shading.light = "STUDIO"
                shading.show_shadows = True
                shading.show_cavity = True
                area.spaces.active.overlay.show_overlays = False
    return scene

def begin(name, category):
    global ROOT, COLLECTION
    if bpy.data.objects.get(name):
        raise RuntimeError("El asset ya existe; revisar antes de regenerar: " + name)
    COLLECTION = bpy.data.collections.new("ASSET_" + name)
    bpy.context.scene.collection.children.link(COLLECTION)
    ROOT = bpy.data.objects.new(name, None)
    COLLECTION.objects.link(ROOT)
    ROOT.empty_display_size = 0.12
    ROOT["AlarmaCategory"] = category
    ROOT["ReviewStatus"] = "Pending visual approval"
    ROOT["ScaleMeters"] = 1.0
    CATALOG[name] = {"category": category, "root": ROOT, "collection": COLLECTION}
    return ROOT

def link(obj, name, material="Cream", parent=None):
    obj.name = name
    for collection in list(obj.users_collection): collection.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    obj.parent = parent or ROOT
    if obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(mat(material))
    return obj

def box(name, location, size, material="Cream", bevel=0.015, parent=None, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = link(bpy.context.object, name, material, parent)
    obj.location = location
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation: obj.rotation_euler = rotation
    if bevel:
        modifier = obj.modifiers.new("Edge chamfer", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.2)
        modifier.segments = 1
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj

def cyl(name, location, radius, depth, material="Metal", vertices=12, rotation=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    obj = link(bpy.context.object, name, material, parent)
    obj.location = location
    if rotation: obj.rotation_euler = rotation
    return obj

def sphere(name, location, scale, material="Leaf", subdivisions=1, parent=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1)
    obj = link(bpy.context.object, name, material, parent)
    obj.location = location
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def mesh(name, vertices, faces, material="Cream", parent=None):
    data = bpy.data.meshes.new(name + "_Mesh")
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    COLLECTION.objects.link(obj)
    obj.parent = parent or ROOT
    data.materials.append(mat(material))
    return obj

def beam(name, start, end, radius, material="Metal", vertices=8, parent=None):
    a, b = Vector(start), Vector(end)
    obj = cyl(name, (a + b) / 2, radius, (b - a).length, material, vertices=vertices, parent=parent)
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return obj

def empty(name, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    COLLECTION.objects.link(obj)
    obj.parent = parent or ROOT
    obj.location = location
    obj.empty_display_size = 0.08
    return obj

def torus(name, location, major, minor, material="Metal", rotation=None, scale=None, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=6, major_radius=major, minor_radius=minor)
    obj = link(bpy.context.object, name, material, parent)
    obj.location = location
    if rotation: obj.rotation_euler = rotation
    if scale: obj.scale = scale
    return obj

def text(name, content, location, size, material="Navy", rotation=(math.pi / 2, 0, 0), parent=None):
    curve = bpy.data.curves.new(name + "_Font", "FONT")
    curve.body = content
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.002
    obj = bpy.data.objects.new(name, curve)
    COLLECTION.objects.link(obj)
    obj.parent = parent or ROOT
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat(material))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object

def descendants(root):
    return [root] + list(root.children_recursive)

def export_asset(name):
    entry = CATALOG[name]
    root = entry["root"]
    path = ART / entry["category"] / (name + ".fbx")
    path.parent.mkdir(exist_ok=True)
    old_location = root.location.copy()
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    originals = []
    visibility = []
    try:
        for obj in descendants(root):
            visibility.append((obj,obj.hide_get(),obj.hide_viewport))
            obj.hide_viewport=False
            obj.hide_set(False)
            if obj.type == "MESH":
                slots=[(slot.link,slot.material) for slot in obj.material_slots]
                original=obj.data
                temporary=original.copy()
                obj.data=temporary
                temporary.materials.clear()
                for _,material in slots: temporary.materials.append(material)
                for slot in obj.material_slots: slot.link="DATA"
                originals.append((obj,original,temporary,slots))
            if obj.name in bpy.context.view_layer.objects: obj.select_set(True)
        bpy.context.view_layer.objects.active = root
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH", "EMPTY"}, global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y", use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
    finally:
        for obj,original,temporary,slots in originals:
            obj.data=original
            for slot,(link,material) in zip(obj.material_slots,slots):
                slot.link=link
                if link=="OBJECT": slot.material=material
            bpy.data.meshes.remove(temporary)
        for obj,hidden,disabled in visibility:
            obj.hide_viewport=disabled
            obj.hide_set(hidden)
        root.location = old_location
    meshes = [obj for obj in descendants(root) if obj.type == "MESH"]
    entry["file"] = str(path)
    entry["mesh_count"] = len(meshes)
    entry["vertices"] = sum(len(obj.data.vertices) for obj in meshes)
    entry["triangles"] = sum(sum(len(face.vertices) - 2 for face in obj.data.polygons) for obj in meshes)
    return path

def clone(name, instance_name, location, rotation=0):
    entry = CATALOG[name]
    original = entry["root"]
    mapping = {}
    for item in descendants(original):
        copy = item.copy()
        COLLECTION.objects.link(copy)
        copy.name = instance_name + "_" + item.name
        mapping[item] = copy
    for source, copy in mapping.items():
        copy.parent = mapping.get(source.parent, ROOT)
    result = mapping[original]
    result.location = location
    result.rotation_euler.z = rotation
    return result

def arrange(names, columns, spacing, start=(0, 0)):
    for index, name in enumerate(names):
        CATALOG[name]["root"].location = (start[0] + (index % columns) * spacing[0], start[1] + (index // columns) * spacing[1], 0)

def camera(target, distance, ortho_scale):
    scene = bpy.context.scene
    data = bpy.data.cameras.new(scene.name + "_Camera")
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = Vector(target) + Vector(distance)
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    data.lens = 50
    data.clip_end = 1000
    scene.camera = obj
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D": area.spaces.active.region_3d.view_perspective = "CAMERA"
    return obj

def studio_floor(center, size):
    scene = bpy.context.scene
    data = bpy.data.meshes.new("StudioFloor")
    x, y = center
    data.from_pydata([(x-size, y-size, -0.035), (x+size, y-size, -0.035), (x+size, y+size, -0.035), (x-size, y+size, -0.035)], [], [(0, 1, 2, 3)])
    obj = bpy.data.objects.new("StudioFloor", data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat("Cream"))
    light_data = bpy.data.lights.new("StudioKey", "AREA")
    light_data.energy = 1800
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new("StudioKey", light_data)
    scene.collection.objects.link(light)
    light.location = (x - size * 0.5, y - size * 0.7, size)
    light.rotation_euler = (Vector((x, y, 0)) - light.location).to_track_quat("-Z", "Y").to_euler()

def save_library():
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    source = ART / "BlenderSources~/Alarma_ArtLibrary.blend"
    source.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    entries = [{key: value for key, value in entry.items() if key not in {"root", "collection"}} | {"name": name, "approval": "pending"} for name, entry in CATALOG.items()]
    (ART / "BlenderScripts/asset_catalog.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    (OUTPUTS / "Alarma-Catalogo-modelos.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print("LIBRARY_SAVED", sum("file" in entry for entry in entries), "exported assets", sum(entry.get("triangles", 0) for entry in entries), "triangles")
