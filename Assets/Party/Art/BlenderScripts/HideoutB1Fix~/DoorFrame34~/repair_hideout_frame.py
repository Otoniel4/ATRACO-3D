"""Ajuste aislado del acceso de la guarida. Ejecutar en Blender mediante MCP."""
from pathlib import Path
import json
import math
import re

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1]
ART = SCRIPTS.parent
OUT = ART.parents[2] / 'Library/Alarma/DoorFrame34'
OUT.mkdir(parents=True, exist_ok=True)
recipe = SCRIPTS / 'build_hideout.py'
scope = {'__file__': str(recipe), '__name__': 'hideout_frame_recipe'}
source = recipe.read_text(encoding='utf-8-sig')
# Cargar las funciones sin ejecutar la reconstrucción de casa e interior.
import ast
module = ast.parse(source)
# El bloque ejecutable comienza después de review().
last_function = max(node.end_lineno for node in module.body if isinstance(node, ast.FunctionDef))
exec(compile('\n'.join(source.splitlines()[:last_function]), str(recipe), 'exec'), scope)
art = scope['a']
scene = bpy.data.scenes.new('Guarida_Marco34')
bpy.context.window.scene = scene
with bpy.data.libraries.load(str(ART / 'BlenderSources~/Alarma_Escondite.blend')) as (original, target):
    target.collections = ['ASSET_Local_Escondite']
collection, = target.collections
scene.collection.children.link(collection)
root = next(o for o in collection.objects if o.name.split('.')[0] == 'Local_Escondite')
def child(name):
    return next(o for o in root.children_recursive if o.name.split('.')[0] == name)
shell = child('Edificio')
old = set()
for side in ('L', 'R'):
    leaf = child('DoorLeaf_' + side)
    old.update([leaf, *leaf.children_recursive])
old.update(o for o in root.children_recursive if o.name.startswith(('Detail_DoorJamb', 'Detail_DoorLintel')))
preserved = set(root.children_recursive) - old
for obj in old:
    bpy.data.objects.remove(obj, do_unlink=True)
art.ROOT, art.COLLECTION = root, collection
scope['entrance_door'](root, shell)
assert preserved <= set(root.children_recursive)
for obj in root.children_recursive:
    for slot in obj.material_slots:
        mat = slot.material
        match = re.fullmatch(r'(Alarma_.+)\.\d{3}', mat.name) if mat else None
        original = bpy.data.materials.get(match[1]) if match else None
        if original and all(abs(a-b) < .0001 for a,b in zip(mat.diffuse_color, original.diffuse_color)):
            slot.material = original

def tree(objects):
    vertices, faces = [], []
    for obj in objects:
        start = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(start+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces)

bpy.context.view_layer.update()
fixed = tree([o for o in root.children_recursive if o.type == 'MESH' and o.name.startswith(('Entrance', 'FrontWall', 'DoorHead'))])
faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
checks = 0
for side in ('L', 'R'):
    leaf = child('DoorLeaf_' + side)
    # Igual que LeafCollider: panel y ventana, sin manija ni adornos.
    points = [leaf.matrix_world.inverted() @ o.matrix_world @ Vector(c)
              for o in leaf.children_recursive if o.type == 'MESH' and o.name.startswith(('DoorPanel_', 'DoorWindow_'))
              for c in o.bound_box]
    lo = [min(v[i] for v in points) for i in range(3)]
    hi = [max(v[i] for v in points) for i in range(3)]
    for degrees in range(-85, 86):
        leaf.rotation_euler.z = math.radians(degrees)
        bpy.context.view_layer.update()
        corners = [leaf.matrix_world @ Vector(tuple(hi[i] if mask & (1 << i) else lo[i] for i in range(3))) for mask in range(8)]
        assert not fixed.overlap(BVHTree.FromPolygons(corners, faces)), (side, degrees)
        checks += 1
    leaf.rotation_euler.z = 0
bpy.context.view_layer.update()
art.CATALOG['Local_Escondite'] = {'root': root, 'category': 'City/Shops'}
previous = art.ART
try:
    art.ART = OUT
    (OUT / 'City/Shops').mkdir(parents=True, exist_ok=True)
    art.export_asset('Local_Escondite')
finally:
    art.ART = previous

camera = bpy.data.objects.new('Camara_Marco34', bpy.data.cameras.new('Camara_Marco34'))
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.resolution_x, scene.render.resolution_y = 1200, 1000
scene.render.resolution_percentage = 100
area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
area.spaces.active.region_3d.view_perspective = 'CAMERA'
area.spaces.active.overlay.show_overlays = False
area.spaces.active.shading.type = 'SOLID'
area.spaces.active.shading.color_type = 'MATERIAL'
region = next(r for r in area.regions if r.type == 'WINDOW')
for label, location, angle in [('interior_cerrada',(.65,-4.7,1.65),0), ('interior_abierta',(.65,-4.7,1.65),85), ('exterior_cerrada',(-.65,-11.1,1.65),0)]:
    camera.location = location
    camera.rotation_euler = (Vector((0,-7.9,1.3))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens = 34
    child('DoorLeaf_L').rotation_euler.z = math.radians(angle)
    child('DoorLeaf_R').rotation_euler.z = math.radians(-angle)
    bpy.context.view_layer.update()
    scene.render.filepath = str(HERE / (label + '.png'))
    with bpy.context.temp_override(area=area,region=region):
        bpy.ops.render.opengl(write_still=True, view_context=True)
child('DoorLeaf_L').rotation_euler.z = child('DoorLeaf_R').rotation_euler.z = 0
bpy.context.view_layer.update()
bpy.data.libraries.write(str(OUT / 'Alarma_Escondite.blend'), {scene}, compress=True)
result = dict(preserved_objects=len(preserved), box_sweep_checks=checks, side_seam_m=.025, top_seam_m=.015, unity_play_tested=False)
(HERE / 'geometry-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
