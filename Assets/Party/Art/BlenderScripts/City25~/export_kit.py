"""Kit de la ciudad de 2 × 2 km: edificios, árboles, mobiliario y autos sacados del mundo R9 ya aprobado.

Cada variante de edificio junta sus piezas (base, techo, bordes y follaje con viento) en un solo objeto
con el origen a nivel de calle en el centro de su planta. Las coordenadas se toman sin la rotación de la
instancia, así que la fachada queda siempre hacia el mismo lado local (FRONT en kit.json).
Uso: blender -b --factory-startup -P export_kit.py
Salida: Art/City/Kit25/<grupo>/<pieza>.fbx, kit.json y renders/kit_*.png
"""
import bpy, json, math, re, sys
from pathlib import Path
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_fbx import export  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / 'BlenderSources~' / 'Villa_Alarma_R9_Ligera.blend'  # del mundo R9 retirado solo se conserva esta fuente
OUT = HERE.parent.parent / 'City' / 'Kit25'
BUILDINGS = {'House': 12, 'Apartment': 6, 'Shop': 12, 'Tower': 3, 'Warehouse': 3}
PROPS = ['CityR2_Lamp', 'Signal', 'CityR2_Bench', 'CityR2_Bin', 'CityR2_CafeSet', 'CityR2_Planter_R4Base', 'CityR2_BikeRack',
         'CityR2_FoodStand', 'CityR2_Playground', 'CityR2_BasketballCourt', 'CityR2_EVCharger']
TREES = ['TreeR3_Fresno_LOD1_Ligera', 'TreeR3_Olivo_LOD1_Ligera', 'TreeR3_Citrico_LOD1_Ligera', 'TreeR3_Pino_LOD2_Ligera',
         'TreeR3_Jacaranda_LOD2_Ligera', 'TreeR3_Palmera_LOD0_Ligera']
CARS = []  # los autos salen de Art/Vehicles (piezas separadas: ruedas y puertas)


def assemble(name, parts, origin):
    # Copia las piezas sin la transformación de la instancia y las une en una sola malla.
    inverse = origin.inverted()
    copies = []
    for o in parts:
        c = o.copy()
        c.data = o.data.copy()
        c.parent = None
        c.matrix_world = inverse @ o.matrix_world
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    with bpy.context.temp_override(active_object=copies[0], selected_editable_objects=copies, selected_objects=copies):
        bpy.ops.object.join()
    piece = copies[0]
    piece.name = name
    with bpy.context.temp_override(active_object=piece, selected_editable_objects=[piece], object=piece):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return piece


def measure(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def recenter(obj):
    # Origen en el centro de la planta y a ras del suelo.
    lo, hi = measure(obj)
    shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    obj.data.transform(Matrix.Translation(-shift))
    obj.matrix_world = Matrix()
    lo, hi = measure(obj)
    return dict(width=round(hi.x - lo.x, 2), depth=round(hi.y - lo.y, 2), height=round(hi.z - lo.z, 2),
                triangles=sum(len(p.vertices) - 2 for p in obj.data.polygons))


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene_objects = [o for o in bpy.data.objects if o.type == 'MESH']
kit = dict(source=SOURCE.name, front='-Y local (fachada hacia la calle)', pieces=[])
work = bpy.data.collections.new('Kit25')
bpy.context.scene.collection.children.link(work)
for kind, count in BUILDINGS.items():
    for n in range(count):
        tag = f'{kind}_{n}'
        bases = [o for o in scene_objects if re.fullmatch(rf'CityR2_{tag}(_R4Base)?(\.\d+)?', o.data.name)]
        if not bases:
            print('SIN BASE', tag)
            continue
        base = bases[0]
        here = base.matrix_world.to_translation()
        pattern = re.compile(rf'(^|_){tag}(_|$)')
        parts = [o for o in scene_objects if o.parent == base.parent and pattern.search(o.data.name)
                 and (o.matrix_world.to_translation() - here).length < .05]
        origin = Matrix.Translation(here) @ base.matrix_world.to_quaternion().to_matrix().to_4x4()
        piece = assemble(tag, parts, origin)
        info = recenter(piece)
        export([piece], OUT / 'Buildings' / f'{tag}.fbx')
        kit['pieces'].append(dict(id=tag, group='building', kind=kind.lower(), parts=len(parts), **info))
for group, names in (('prop', PROPS), ('tree', TREES), ('car', CARS)):
    for name in names:
        source = next((o for o in scene_objects if o.data.name == name), None)
        if source is None:
            print('SIN PIEZA', name)
            continue
        here = source.matrix_world.to_translation()
        origin = Matrix.Translation(here) @ source.matrix_world.to_quaternion().to_matrix().to_4x4()
        clean = name.replace('CityR2_', '').replace('_R4Base', '').replace('TreeR3_', 'Tree_').replace('_Ligera', '')
        piece = assemble(clean, [source], origin)
        info = recenter(piece)
        export([piece], OUT / {'prop': 'Props', 'tree': 'Trees', 'car': 'Cars'}[group] / f'{clean}.fbx')
        kit['pieces'].append(dict(id=clean, group=group, kind=clean.split('_')[0].lower(), parts=1, **info))
(OUT / 'kit.json').write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding='utf-8')

# Hoja de revisión: edificios en fila mirando a la cámara (-Y), para comprobar que la fachada queda delante.
for o in list(bpy.context.scene.objects):
    if o.name not in {p['id'] for p in kit['pieces']}:
        o.hide_render = True
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 3000, 900
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
scene.collection.objects.link(cam)
cam.data.type = 'ORTHO'
scene.camera = cam
for group, kinds in (('edificios', ['House', 'Apartment', 'Shop']), ('grandes', ['Tower', 'Warehouse'])):
    shown = [bpy.data.objects[p['id']] for p in kit['pieces'] if p['group'] == 'building' and p['id'].split('_')[0] in kinds]
    x = 0
    for o in bpy.data.objects:
        if o.name in {p['id'] for p in kit['pieces']}:
            o.hide_render = o not in shown
    for o in shown:
        w = o.dimensions.x
        o.location = (x + w / 2, 0, 0)
        x += w + 4
    cam.data.ortho_scale = x + 10
    cam.location = (x / 2, -200, 18)
    cam.rotation_euler = (math.radians(84), 0, 0)
    scene.render.filepath = str(HERE / 'renders' / f'kit_{group}.png')
    bpy.ops.render.render(write_still=True)
    for o in shown:
        o.location = (0, 0, 0)
print('KIT', len(kit['pieces']), json.dumps([(p['id'], p['width'], p['depth'], p['height']) for p in kit['pieces']]))
