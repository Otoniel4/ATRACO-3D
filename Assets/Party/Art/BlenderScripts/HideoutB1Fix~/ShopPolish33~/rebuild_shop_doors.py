"""Sustituye solo los accesos en los seis modelos comerciales. Ejecutar desde Blender."""
from pathlib import Path
import math
import re

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1]
ART = SCRIPTS.parent
PROJECT = ART.parents[2]
OUT = PROJECT / "Library/Alarma/ShopPolish33"
SOURCES = ART / "BlenderSources~"
files = {
    "Banco": "banco",
    "Joyeria": "joyeria",
    "Supermercado": "supermercado",
    "Minimarket": "minimarket_comida_ropa",
    "Comida": "minimarket_comida_ropa",
    "Ropa": "minimarket_comida_ropa",
}
recipe = SCRIPTS / "build_shops.py"
scope = {"__file__": str(recipe), "__name__": "store_door_recipe"}
definitions = recipe.read_text(encoding="utf-8-sig").split("# Uso parcial:", 1)[0]
exec(compile(definitions, str(recipe), "exec"), scope)
art = scope["a"]
previous_art = art.ART
scene = bpy.data.scenes.new("Alarma_Puertas_Comerciales")
bpy.context.window.scene = scene
(OUT / "City/Shops").mkdir(parents=True, exist_ok=True)
art.ART = OUT
stores = {}


def child(root, name):
    return next(obj for obj in root.children_recursive if obj.name.split(".", 1)[0] == name)


try:
    for index, (shop, source) in enumerate(files.items()):
        name = "Local_" + shop
        with bpy.data.libraries.load(str(SOURCES / f"Alarma_Shops_{source}.blend")) as (original, target):
            collection_name = "ASSET_" + name
            assert collection_name in original.collections
            target.collections = [collection_name]
        collection, = target.collections
        scene.collection.children.link(collection)
        root = next(obj for obj in collection.objects if obj.name == name)
        old_doors = [child(root, "DoorLeaf_" + side) for side in ("L", "R")]
        trim = child(root, "DoorFrame_L").active_material
        glass = child(root, "DoorGlass_L").active_material
        chrome = child(root, "DoorBar_L").active_material
        y = old_doors[0].location.y
        width = abs(old_doors[0].location.x) * 2
        header = child(root, "DoorHeader")
        height = header.location.z - header.dimensions.z / 2
        before = {o for o in root.children_recursive}
        for door in old_doors:
            for obj in list(door.children_recursive):
                before.remove(obj)
                bpy.data.objects.remove(obj, do_unlink=True)
            before.remove(door)
            bpy.data.objects.remove(door, do_unlink=True)
        art.ROOT, art.COLLECTION = root, collection
        scope["store_doors"](y, width, height, trim, glass, chrome)
        assert before <= set(root.children_recursive)
        for obj in root.children_recursive:
            for slot in obj.material_slots:
                mat = slot.material
                if not mat:
                    continue
                match = re.fullmatch(r"(Alarma_.+)\.\d{3}", mat.name)
                original_mat = bpy.data.materials.get(match[1]) if match else None
                if original_mat and all(abs(a - b) < .0001 for a, b in zip(mat.diffuse_color, original_mat.diffuse_color)):
                    slot.material = original_mat
        art.CATALOG[name] = {"root": root, "category": "City/Shops"}
        art.export_asset(name)
        root.location = (index * 30, 0, 0)
        stores[shop] = root
        print(name, "objetos existentes conservados", len(before))
finally:
    art.ART = previous_art

root = stores["Supermercado"]
camera = bpy.data.objects.new("Camara_Puerta", bpy.data.cameras.new("Camara_Puerta"))
scene.collection.objects.link(camera)
scene.camera = camera
camera.location = root.location + Vector((3.8, -16.0, 2.1))
target = root.location + Vector((0, -11.0, 1.25))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 40
scene.render.resolution_x, scene.render.resolution_y = 1440, 900
scene.render.resolution_percentage = 100
area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
area.spaces.active.region_3d.view_perspective = "CAMERA"
area.spaces.active.overlay.show_overlays = False
area.spaces.active.shading.type = "SOLID"
area.spaces.active.shading.color_type = "MATERIAL"
region = next(r for r in area.regions if r.type == "WINDOW")
left, right = [child(root, "DoorLeaf_" + side) for side in ("L", "R")]
for label, degrees in (("cerrada", 0), ("abierta", 85)):
    left.rotation_euler.z = math.radians(-degrees)
    right.rotation_euler.z = math.radians(degrees)
    bpy.context.view_layer.update()
    scene.render.filepath = str(OUT / f"supermercado_puerta_{label}.png")
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.render.opengl(write_still=True, view_context=True)
left.rotation_euler.z = right.rotation_euler.z = 0
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "Alarma_Shops_Puertas33.blend"))
