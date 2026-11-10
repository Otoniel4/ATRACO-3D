"""Repara únicamente los siete accesos. Ejecutar con Blender MCP; publica primero en Library."""
import ast
import json
import math
import re
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1]
ART = SCRIPTS.parent
OUT = ART.parents[2] / 'Library/Alarma/DoorReview36'
(OUT / 'City/Shops').mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPTS))

def definitions(name):
    path = SCRIPTS / name
    source = path.read_text(encoding='utf-8-sig')
    end = max(n.end_lineno for n in ast.parse(source).body if isinstance(n, ast.FunctionDef))
    scope = {'__name__':'door_review', '__file__':str(path)}
    exec(compile('\n'.join(source.splitlines()[:end]), str(path), 'exec'), scope)
    return scope

shops = definitions('build_shops.py')
house = definitions('build_hideout.py')
a = shops['a']
scene = bpy.data.scenes.new('Puertas36_Todos_Los_Accesos')
bpy.context.window.scene = scene
roots = {}
report = {}

def base(obj): return re.sub(r'\.\d+$', '', obj.name)
def child(root, name): return next(o for o in root.children_recursive if base(o) == name)

for index, kind in enumerate(('Banco','Joyeria','Supermercado','Minimarket','Comida','Ropa','Escondite')):
    name = 'Local_' + kind
    file = 'Alarma_Escondite.blend' if kind == 'Escondite' else 'Alarma_Shops_Puertas33.blend'
    with bpy.data.libraries.load(str(ART / 'BlenderSources~' / file)) as (original, target):
        target.collections = ['ASSET_' + name]
    collection, = target.collections
    scene.collection.children.link(collection)
    root = next(o for o in collection.objects if base(o) == name)
    root.name = name
    root.location = (0,0,0)
    left = child(root, 'DoorLeaf_L')
    y = left.location.y
    trim = child(root, 'DoorPanel_L' if kind == 'Escondite' else 'DoorRailTop_L').active_material
    if kind != 'Escondite':
        glass = child(root, 'DoorGlass_L').active_material
        metal = next(o.active_material for o in root.children_recursive if o.name.startswith('Detail_DoorPull'))
        header = child(root, 'DoorHeader')
        height = header.location.z-header.dimensions.z/2
    old = set()
    for side in ('L','R'):
        leaf = child(root, 'DoorLeaf_'+side)
        old.update([leaf,*leaf.children_recursive])
    old.update(o for o in root.children_recursive if o.name.startswith(('Detail_DoorJamb','Detail_DoorLintel','EntranceJamb','EntranceLintel','EntrancePivotHousing','DoorReveal','DoorPivotHousing')))
    preserved = set(root.children_recursive)-old
    for obj in old: bpy.data.objects.remove(obj,do_unlink=True)
    a.ROOT,a.COLLECTION = root,collection
    if kind == 'Escondite': house['entrance_door'](root,child(root,'Edificio'))
    else: shops['store_doors'](y,2.2,height,trim,glass,metal)
    assert preserved <= set(root.children_recursive)
    for obj in root.children_recursive:
        for slot in obj.material_slots:
            mat = slot.material
            match = re.fullmatch(r'(Alarma_.+)\.\d{3}',mat.name) if mat else None
            canonical = bpy.data.materials.get(match[1]) if match else None
            if canonical and all(abs(x-y)<.0001 for x,y in zip(mat.diffuse_color,canonical.diffuse_color)): slot.material=canonical
    a.CATALOG[name] = {'root':root,'category':'City/Shops'}
    previous = a.ART
    try:
        a.ART = OUT
        bpy.context.view_layer.update()
        a.export_asset(name)
    finally: a.ART=previous
    roots[kind]=root
    report[kind]={'preserved_objects':len(preserved),'side_seam_m':.005,'top_seam_m':.004}
    root.location.x=index*35

# Una fuente con los siete accesos y sus colecciones canónicas para futuras correcciones.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Alarma_Puertas36.blend'))

camera=bpy.data.objects.new('Revision36_Camera',bpy.data.cameras.new('Revision36_Camera'))
scene.collection.objects.link(camera);scene.camera=camera
scene.render.resolution_x,scene.render.resolution_y=1100,900
scene.render.resolution_percentage=100
area=next(ar for ar in bpy.context.screen.areas if ar.type=='VIEW_3D')
area.spaces.active.region_3d.view_perspective='CAMERA'
area.spaces.active.overlay.show_overlays=False
area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
region=next(r for r in area.regions if r.type=='WINDOW')
for kind,root in roots.items():
    leaf=child(root,'DoorLeaf_L');front=leaf.location.y
    for side in ('fuera','dentro'):
        camera.location=root.location+Vector((.65,front+(-3.5 if side=='fuera' else 3.5),1.5))
        camera.rotation_euler=(root.location+Vector((0,front,1.35))-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.lens=38
        scene.render.filepath=str(HERE/(kind+'_'+side+'.png'))
        bpy.context.view_layer.update()
        with bpy.context.temp_override(area=area,region=region): bpy.ops.render.opengl(write_still=True,view_context=True)
(HERE/'models.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
