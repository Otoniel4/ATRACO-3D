"""Kit de calle de la ciudad 3.0 (fase A): paradas de bus, kioscos, hidrantes, buzones, señales de tránsito,
bolardos, contenedores de basura y carteles publicitarios. Mismo estilo low-poly de colores planos del kit.

Cada pieza se arma con primitivas, se une en una sola malla con el origen al centro de su planta y a ras del suelo,
y mira hacia -Y (el frente queda hacia la calle, igual que el resto del kit).
Uso: blender -b --factory-startup -P build_street_kit.py
Salida: Art/City/Kit25/Street/<pieza>.fbx, Art/City/Kit25/street_kit.json, street_materials.json
        y renders/street_kit_*.png para revisión.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import alarmart as a  # noqa: E402
from kit_fbx import export  # noqa: E402

KIT = a.ART / 'City' / 'Kit25'
OUT = KIT / 'Street'
# Color hexadecimal, o (color, emisión, opacidad).
COLORS = dict(Steel='8A9499', DarkSteel='454D53', Glass=('A9D3DB', 0, .35), Roof='ECEAE4', Teal='2F8C88', Wood='B07A4E',
              Poster=('F6F0DE', 1.0, 1), Concrete='B9B5AC', Red='D2372E', White='F4F4F0', Black='22262A', Yellow='F2C230',
              SignBlue='2C5BB8', Green='3E7D4A', DarkGreen='2B5A36', Rubber='23282C', Orange='EE7F2D', Navy='22385A',
              Gold='D6A93A', Cream='F2E3C0', Brown='6E4127', Lamp=('FFF4D6', 2.0, 1), KioskGreen='2E7D5B', Diamond='7CC8EE')
BRIGHT = ['Red', 'Yellow', 'SignBlue', 'Orange', 'White', 'Teal']
REGISTRY = {}
PIECES = []


def M(name):
    full = 'Alarma_Street_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    spec = COLORS[name]
    hex_color, emission, alpha = spec if isinstance(spec, tuple) else (spec, 0.0, 1.0)
    color = tuple(a.linear(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4))
    m = bpy.data.materials.new(full)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = .7
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*color, 1)
        bsdf.inputs['Emission Strength'].default_value = emission
    if alpha < 1:
        bsdf.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
    REGISTRY[full] = (hex_color, emission, alpha)
    return m


def use(obj, name):
    obj.data.materials.clear()
    obj.data.materials.append(M(name))
    return obj


def B(name, loc, size, m, bevel=.01, rot=None):
    return use(a.box(name, loc, size, 'Cream', bevel=bevel, rotation=rot), m)


def C(name, loc, r, depth, m, verts=12, rot=None):
    return use(a.cyl(name, loc, r, depth, 'Metal', vertices=verts, rotation=rot), m)


def S(name, loc, scale, m):
    return use(a.sphere(name, loc, scale, 'Leaf', subdivisions=2), m)


def T(name, body, loc, size, m):
    # Texto convertido en malla con curvas de baja resolución: se lee igual y pesa una fracción.
    curve = bpy.data.curves.new(name + '_Font', 'FONT')
    curve.body, curve.size, curve.align_x, curve.align_y = body, size, 'CENTER', 'CENTER'
    curve.extrude, curve.resolution_u = .002, 2
    obj = bpy.data.objects.new(name, curve)
    a.COLLECTION.objects.link(obj)
    obj.parent, obj.location, obj.rotation_euler = a.ROOT, loc, (math.pi / 2, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    return use(bpy.context.object, m)


def plate(name, points, y, m):
    # Polígono plano en el plano XZ con la cara hacia -Y (hacia quien lo mira desde la calle).
    verts = [(x, y, z) for x, z in reversed(points)]
    return use(a.mesh(name, verts, [tuple(range(len(verts)))]), m)


FACE = (math.pi / 2, 0, 0)  # disco con su cara hacia -Y


def begin(piece_id):
    a.begin('SK_' + piece_id, 'City/Kit25/Street')


def measure(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def finish(piece_id, kind):
    root = a.ROOT
    bpy.context.view_layer.update()
    meshes = [o for o in a.descendants(root) if o.type == 'MESH']
    for o in meshes:
        world = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = world
    with bpy.context.temp_override(active_object=meshes[0], selected_editable_objects=meshes, selected_objects=meshes):
        bpy.ops.object.join()
    piece = meshes[0]
    piece.name = piece.data.name = piece_id
    with bpy.context.temp_override(active_object=piece, selected_editable_objects=[piece], object=piece):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.data.objects.remove(root)
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(piece.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=.0005)
    bm.to_mesh(piece.data)
    bm.free()
    # Origen al centro de la planta y a ras del suelo, como el resto del kit.
    lo, hi = measure(piece)
    piece.data.transform(Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    piece.matrix_world = Matrix()
    lo, hi = measure(piece)
    info = dict(width=round(hi.x - lo.x, 2), depth=round(hi.y - lo.y, 2), height=round(hi.z - lo.z, 2),
                triangles=sum(len(p.vertices) - 2 for p in piece.data.polygons))
    export([piece], OUT / f'{piece_id}.fbx')
    PIECES.append(dict(id=piece_id, group='street', kind=kind, parts=len(meshes), **info))
    return piece


# --- piezas ---
def bus_stop():
    begin('BusStop')
    for sx in (-1, 1):
        for y in (.70, -.55):
            B('Post', (sx * 1.92, y, 1.3), (.08, .08, 2.6), 'DarkSteel', .005)
    B('BackGlass', (0, .70, 1.3), (3.76, .03, 1.9), 'Glass', 0)
    B('RailLow', (0, .70, .32), (3.84, .06, .06), 'DarkSteel', 0)
    B('RailTop', (0, .70, 2.27), (3.84, .06, .06), 'DarkSteel', 0)
    B('SideGlass', (-1.92, .075, 1.3), (.03, 1.19, 1.9), 'Glass', 0)
    # Caja de luz con publicidad a los dos lados, de cara a la vereda.
    B('AdBox', (1.92, .075, 1.25), (.2, 1.25, 1.95), 'DarkSteel', .01)
    for sx in (-1, 1):
        x = 1.92 + sx * .105
        B('AdPoster', (x, .075, 1.3), (.01, 1.08, 1.72), 'Poster', 0)
        B('AdBand', (x + sx * .004, .075, 1.75), (.01, 1.08, .55), 'Orange', 0)
        B('AdStripe', (x + sx * .006, .075, .9), (.01, .7, .12), 'Teal', 0)
    B('Roof', (0, .05, 2.66), (4.3, 1.9, .1), 'Roof', .02)
    B('Fascia', (0, -.92, 2.62), (4.3, .05, .22), 'Teal', 0)
    T('FasciaText', 'PARADA', (0, -.95, 2.62), .17, 'White')
    B('Seat', (0, .40, .47), (2.4, .38, .05), 'Wood', .01)
    B('Backrest', (0, .63, .76), (2.4, .04, .26), 'Wood', .01)
    for x in (-1.0, 1.0):
        B('SeatLeg', (x, .45, .23), (.06, .3, .46), 'DarkSteel', 0)
    C('BusMast', (-1.75, -.7, 3.0), .03, .7, 'Steel', 8)
    C('BusDisc', (-1.75, -.7, 3.45), .27, .03, 'SignBlue', 20, rot=FACE)
    T('BusText', 'BUS', (-1.75, -.72, 3.45), .2, 'White')
    B('Pad', (0, .05, .015), (4.0, 1.6, .03), 'Concrete', 0)
    return finish('BusStop', 'busstop')


def kiosk():
    begin('Kiosk')
    B('Base', (0, 0, .5), (2.4, 2.0, 1.0), 'KioskGreen', .02)
    B('Counter', (0, -1.08, 1.03), (2.5, .32, .06), 'Wood', .01)
    B('Back', (0, .95, 1.75), (2.4, .1, 1.5), 'KioskGreen', .01)
    for sx in (-1, 1):
        B('Side', (sx * 1.15, .05, 1.75), (.1, 1.9, 1.5), 'KioskGreen', .01)
    B('Lintel', (0, -.95, 2.38), (2.4, .1, .24), 'KioskGreen', .01)
    B('Roof', (0, -.1, 2.56), (2.9, 2.6, .12), 'DarkGreen', .02)
    for i in range(6):
        x = -1.45 + (i + .5) * 2.9 / 6
        B('Awning', (x, -1.62, 2.38), (2.9 / 6, .55, .04), 'Red' if i % 2 == 0 else 'White', 0, rot=(math.radians(25), 0, 0))
    B('SignBoard', (0, -1.1, 2.86), (2.0, .08, .44), 'Yellow', .01)
    T('SignText', 'KIOSCO', (0, -1.145, 2.86), .28, 'Black')
    # Estantes con golosinas al fondo y revistas colgadas por fuera de los costados.
    for z in (1.3, 1.75):
        B('Shelf', (0, .78, z), (2.1, .3, .04), 'Wood', 0)
        for i in range(8):
            B('Snack', (-.88 + i * .25, .78, z + .12), (.18, .2, .2), BRIGHT[(i + int(z * 10)) % 6], 0)
    for sx in (-1, 1):
        B('Rack', (sx * 1.215, -.1, 1.65), (.03, 1.5, 1.1), 'DarkSteel', 0)
        for row in range(3):
            for col in range(4):
                B('Mag', (sx * 1.24, -.7 + col * .4, 1.3 + row * .36), (.015, .3, .32), BRIGHT[(row * 4 + col + (0 if sx < 0 else 3)) % 6], 0)
    for i in range(3):
        B('Paper', (-.7 + i * .7, -1.1, 1.08), (.4, .26, .04), 'White' if i != 1 else 'Cream', 0)
    return finish('Kiosk', 'kiosk')


def hydrant():
    begin('Hydrant')
    C('Flange', (0, 0, .03), .16, .06, 'Red', 12)
    C('Body', (0, 0, .33), .12, .54, 'Red', 12)
    C('Bonnet', (0, 0, .62), .145, .06, 'Red', 12)
    S('Dome', (0, 0, .65), (.115, .115, .085), 'Red')
    C('Nut', (0, 0, .74), .03, .05, 'DarkSteel', 6)
    for sx in (-1, 1):
        C('Nozzle', (sx * .17, 0, .43), .05, .12, 'Red', 10, rot=(0, math.pi / 2, 0))
        C('Cap', (sx * .235, 0, .43), .055, .03, 'Yellow', 10, rot=(0, math.pi / 2, 0))
    C('Pumper', (0, -.16, .38), .07, .1, 'Red', 12, rot=FACE)
    C('PumperCap', (0, -.22, .38), .075, .03, 'Yellow', 12, rot=FACE)
    return finish('Hydrant', 'hydrant')


def mailbox():
    begin('Mailbox')
    B('Foot', (0, 0, .02), (.3, .3, .04), 'DarkSteel', 0)
    B('Post', (0, 0, .35), (.1, .1, .66), 'DarkSteel', .005)
    B('Body', (0, 0, .92), (.5, .4, .5), 'SignBlue', .02)
    C('Top', (0, 0, 1.17), .2, .5, 'SignBlue', 16, rot=(0, math.pi / 2, 0))
    B('Band', (0, 0, .74), (.52, .42, .06), 'Yellow', 0)
    B('Slot', (0, -.205, 1.04), (.28, .02, .04), 'Black', 0)
    T('Label', 'CORREO', (0, -.212, .88), .085, 'White')
    return finish('Mailbox', 'mailbox')


def sign(piece_id, kind, build):
    # Señal de tránsito: poste detrás de la placa (no la atraviesa) y la placa de cara a los autos que llegan.
    begin(piece_id)
    C('Pole', (0, .05, 1.25), .035, 2.5, 'Steel', 8)
    B('Clamp', (0, .03, 2.3), (.1, .04, .08), 'DarkSteel', 0)
    build()
    return finish(piece_id, kind)


def stop_face():
    rot = (math.pi / 2, math.pi / 8, 0)  # octógono con lados arriba y abajo
    C('Back', (0, .014, 2.3), .40, .008, 'Steel', 8, rot=rot)
    C('Border', (0, .004, 2.3), .40, .012, 'White', 8, rot=rot)
    C('Face', (0, -.006, 2.3), .36, .01, 'Red', 8, rot=rot)
    T('Text', 'PARE', (0, -.013, 2.3), .2, 'White')


def yield_face():
    rot = (math.pi / 2, math.pi, 0)  # triángulo con la punta hacia abajo (el primer vértice nace en +Y)
    C('Back', (0, .014, 2.25), .52, .008, 'Steel', 3, rot=rot)
    C('Border', (0, .004, 2.25), .52, .012, 'Red', 3, rot=rot)
    C('Face', (0, -.006, 2.25), .36, .01, 'White', 3, rot=rot)
    T('Text', 'CEDA\nEL PASO', (0, -.013, 2.3), .075, 'Black')


def speed_face(limit):
    def build():
        C('Back', (0, .014, 2.3), .34, .008, 'Steel', 24, rot=FACE)
        C('Ring', (0, .004, 2.3), .34, .012, 'Red', 24, rot=FACE)
        C('Face', (0, -.006, 2.3), .26, .01, 'White', 24, rot=FACE)
        T('Text', str(limit), (0, -.013, 2.3), .27, 'Black')
    return build


def bollards():
    begin('BollardRow')
    for x in (-1.2, 0, 1.2):
        C('Bollard', (x, 0, .42), .09, .84, 'DarkSteel', 10)
        S('Cap', (x, 0, .84), (.09, .09, .05), 'DarkSteel')
        C('Band', (x, 0, .72), .095, .06, 'Yellow', 10)
    return finish('BollardRow', 'bollards')


def dumpster():
    begin('Dumpster')
    lo, hi = (.9, .52, .22), (1.0, .6, 1.28)  # se abre hacia arriba
    verts = [(-lo[0], -lo[1], lo[2]), (lo[0], -lo[1], lo[2]), (lo[0], lo[1], lo[2]), (-lo[0], lo[1], lo[2]),
             (-hi[0], -hi[1], hi[2]), (hi[0], -hi[1], hi[2]), (hi[0], hi[1], hi[2]), (-hi[0], hi[1], hi[2])]
    body = use(a.mesh('Body', verts, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]), 'Green')
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(body.data)
    bm.free()
    B('Rim', (0, 0, 1.29), (2.06, 1.24, .06), 'DarkSteel', 0)
    B('LidL', (-.5, 0, 1.345), (.98, 1.26, .05), 'DarkGreen', .01)
    B('LidR', (.5, 0, 1.36), (.98, 1.26, .05), 'DarkGreen', .01, rot=(math.radians(-6), 0, 0))
    for sx in (-1, 1):
        C('Pin', (sx * .99, 0, .95), .06, .12, 'DarkSteel', 8, rot=(0, math.pi / 2, 0))
        for sy in (-1, 1):
            B('Caster', (sx * .78, sy * .4, .2), (.1, .1, .06), 'DarkSteel', 0)
            C('Wheel', (sx * .78, sy * .4, .1), .1, .08, 'Rubber', 10, rot=(0, math.pi / 2, 0))
    T('Label', 'RESIDUOS', (0, -.585, .85), .15, 'White')
    return finish('Dumpster', 'dumpster')


def billboard(piece_id, background, band, title, subtitle, title_color, subtitle_color, icon):
    # Cartel sobre dos pilares con pasarela y focos; la publicidad es de los locales del propio juego.
    begin(piece_id)
    for sx in (-1, 1):
        B('Post', (sx * 2.6, .25, 2.25), (.36, .36, 4.5), 'Steel', .01)
        B('Foot', (sx * 2.6, .25, .1), (.8, .8, .2), 'Concrete', .01)
    B('Brace', (0, .25, 3.0), (5.2, .15, .15), 'Steel', 0)
    B('Panel', (0, .2, 6.1), (8.4, .3, 3.6), 'DarkSteel', .02)
    B('Face', (0, .04, 6.1), (8.0, .02, 3.2), background, 0)
    B('Band', (0, .025, 4.78), (8.0, .01, .5), band, 0)
    B('Catwalk', (0, -.25, 4.25), (8.2, .6, .06), 'Steel', 0)
    B('Rail', (0, -.53, 4.8), (8.2, .04, .04), 'Steel', 0)
    for x in (-4.0, -1.35, 1.35, 4.0):
        B('RailPost', (x, -.53, 4.52), (.04, .04, .56), 'Steel', 0)
    for x in (-2.6, 0, 2.6):
        B('LampArm', (x, -.35, 8.0), (.08, .9, .08), 'DarkSteel', 0)
        B('LampHead', (x, -.82, 7.95), (.45, .22, .12), 'DarkSteel', 0)
        B('LampGlow', (x, -.82, 7.885), (.4, .18, .01), 'Lamp', 0)
    icon()
    T('Title', title, (1.0, .015, 6.65), .48, title_color)
    T('Subtitle', subtitle, (1.0, .015, 5.85), .26, subtitle_color)
    return finish(piece_id, 'billboard')


def burger():
    for name, z, h, m in (('BunTop', 6.95, .5, 'Gold'), ('Lettuce', 6.62, .14, 'Green'), ('Patty', 6.4, .3, 'Brown'),
                          ('Cheese', 6.2, .1, 'Yellow'), ('BunBottom', 5.98, .32, 'Gold')):
        B(name, (-2.6, .022, z), (1.9 if name != 'Lettuce' else 2.05, .01, h), m, 0)
    for x in (-3.0, -2.6, -2.2):
        B('Seed', (x, .015, 7.05), (.12, .01, .06), 'Cream', 0)


def coin():
    C('Coin', (-2.6, .025, 6.3), .9, .01, 'Gold', 28, rot=FACE)
    C('CoinInner', (-2.6, .018, 6.3), .7, .01, 'Yellow', 28, rot=FACE)
    T('Sign', '$', (-2.6, .01, 6.3), 1.0, 'Navy')


def diamond():
    plate('Gem', [(-3.15, 6.75), (-2.05, 6.75), (-1.65, 6.4), (-2.6, 5.45), (-3.55, 6.4)], .025, 'SignBlue')
    plate('GemLight', [(-3.0, 6.65), (-2.2, 6.65), (-1.92, 6.4), (-2.6, 5.75), (-3.28, 6.4)], .018, 'Diamond')
    plate('GemShine', [(-2.95, 6.6), (-2.6, 6.6), (-2.9, 6.42)], .012, 'White')


bpy.ops.wm.read_factory_settings(use_empty=True)
OUT.mkdir(parents=True, exist_ok=True)
bus_stop()
kiosk()
hydrant()
mailbox()
sign('StopSign', 'stopsign', stop_face)
sign('YieldSign', 'yieldsign', yield_face)
sign('SpeedSign_40', 'speedsign', speed_face(40))
sign('SpeedSign_60', 'speedsign', speed_face(60))
bollards()
dumpster()
billboard('Billboard_A', 'Orange', 'Yellow', 'BURGER BANDIDO', 'SABOR QUE SE ESCAPA', 'White', 'Cream', burger)
billboard('Billboard_B', 'Navy', 'Gold', 'BANCO SIN PRISA', 'TU DINERO, SIEMPRE SEGURO', 'White', 'Gold', coin)
billboard('Billboard_C', 'Cream', 'SignBlue', 'DIAMANTE AZUL', 'JOYERIA FINA DESDE 1990', 'Navy', 'SignBlue', diamond)

(KIT / 'street_kit.json').write_text(json.dumps(dict(source='build_street_kit.py', front='-Y local (hacia la calle)', pieces=PIECES),
                                                indent=1, ensure_ascii=False), encoding='utf-8')
entries = [dict(name=n, r=int(h[0:2], 16) / 255, g=int(h[2:4], 16) / 255, b=int(h[4:6], 16) / 255, a=al, metallic=0, roughness=.7,
                emission=round(e * .5, 2)) for n, (h, e, al) in sorted(REGISTRY.items())]
(KIT / 'street_materials.json').write_text(json.dumps(dict(materials=entries), indent=1), encoding='utf-8')
print('KIT_CALLE', json.dumps([(p['id'], p['width'], p['depth'], p['height'], p['triangles']) for p in PIECES]))

# --- revisión: escena de vereda con cada pieza donde irá en la ciudad, más dos autos del proyecto para la escala ---
scene = bpy.context.scene
work = bpy.data.collections.new('Revision')
scene.collection.children.link(work)


def slab(name, x0, y0, x1, y1, z, m):
    data = bpy.data.meshes.new(name)
    data.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, data)
    work.objects.link(o)
    o.data.materials.append(M(m))
    return o


COLORS.update(Asfalto='414B52', Acera='C9C6BE', Pasto='6E9A5C', Linea='F4F4F0')
slab('Pasto', -40, -12, 40, 30, -.01, 'Pasto')
slab('Calzada', -40, -12, 40, 0, .045, 'Asfalto')
slab('Vereda', -40, 0, 40, 5, .14, 'Acera')
for i in range(8):
    slab('Linea', -38 + i * 10, -6.1, -33 + i * 10, -5.9, .05, 'Linea')
cars = {}
for car in ('Car_Sedan', 'Car_Van'):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(a.ART / 'Vehicles' / f'{car}.fbx'))
    new = [o for o in bpy.data.objects if o not in before]
    holder = bpy.data.objects.new(car + '_Holder', None)
    work.objects.link(holder)
    for o in new:
        if o.parent is None:
            o.parent = holder
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    size = [round(max(p[i] for p in pts) - min(p[i] for p in pts), 2) for i in range(3)]
    cars[car] = holder
    print('AUTO', car, 'medidas', size, 'mallas', len(meshes))


def put(name, x, y, z, yaw):
    o = bpy.data.objects[name] if name in bpy.data.objects else cars[name]
    o.location = (x, y, z)
    o.rotation_euler = (0, 0, math.radians(yaw))


# Frente del kit = -Y = hacia la calle. Rotar 180° deja el frente hacia la vereda (buzón).
put('Billboard_B', -14, 12, 0, 0)
put('Billboard_A', 2, 14, 0, 0)
put('Kiosk', -12, 3.7, .14, 0)
put('BusStop', 0, 3.9, .14, 0)
put('BollardRow', -19, .5, .14, 0)
put('Mailbox', -6, .5, .14, 180)
put('Hydrant', 5, .45, .14, 0)
put('SpeedSign_60', 9, .45, .14, 90)
put('StopSign', -25, .5, .14, 90)
put('YieldSign', -28, .5, .14, 90)
put('SpeedSign_40', 12, .45, .14, 90)
put('Dumpster', 17, -.75, .045, 0)
put('Car_Sedan', 23, -1.05, .045, 90)
put('Car_Van', 30, -1.1, .045, 90)
put('Billboard_C', 22, 13, 0, 0)

scene.render.engine = 'BLENDER_WORKBENCH'
sky = bpy.data.worlds.new('Cielo')
sky.color = (.62, .74, .9)
scene.world = sky
scene.view_settings.view_transform = 'Standard'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x, scene.render.resolution_y = 1800, 1000
cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
work.objects.link(cam)
scene.camera = cam
renders = HERE / 'renders'
renders.mkdir(exist_ok=True)
for label, eye, target, lens in (('calle', (-4, -26, 9), (2, 5, 2.5), 26), ('cerca', (-8, -7, 2.2), (-3, 3, 1.2), 24),
                                 ('senales', (-14, -6, 2.4), (-24, .5, 1.8), 30), ('carteles', (4, -10, 4), (6, 12, 6), 26),
                                 ('contenedor', (12, -9, 2.2), (20, -1, .8), 28)):
    cam.location = eye
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(renders / f'street_kit_{label}.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / 'BlenderSources~' / 'Alarma_StreetKit.blend'))
