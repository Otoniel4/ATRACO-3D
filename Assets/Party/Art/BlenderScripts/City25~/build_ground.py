"""Suelo de la ciudad de 2 × 2 km: césped, losas por zona, calzadas, aceras con bordillo, marcas viales, pasos de cebra,
río con muros y barandas, puentes, plaza con fuente, parque con senderos y estanque, lotes y alcantarillas.

Lee city_plan.json y city_objects.json. Exporta un FBX por sector de 250 m con el origen en el centro del sector
(Art/City/Ground25/Ground_<i>_<j>.fbx) y ground_materials.json con los colores (sRGB) para Unity.
Con --preview coloca además el kit sobre el suelo y renderiza vistas de revisión en renders/ciudad_*.png.
Uso: blender -b --factory-startup -P build_ground.py [-- --preview]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kit_fbx import export  # noqa: E402

KIT = HERE.parent.parent / 'City' / 'Kit25'
OUT = HERE.parent.parent / 'City' / 'Ground25'
PLAN = json.loads((HERE / 'city_plan.json').read_text(encoding='utf-8'))
OBJECTS = json.loads((HERE / 'city_objects.json').read_text(encoding='utf-8'))['objects']
HALF = PLAN['size_m'] / 2
SECTOR = 250.0
COUNT = int(round(2 * HALF / SECTOR))
KINDS = PLAN['kinds']
RIVER = PLAN['river']
WATER = RIVER['width'] / 2

# Alturas de cada capa: separadas lo justo para que no parpadeen a distancia.
Z = dict(ground=0.0, asphalt=0.04, marking=0.06, slab=0.08, lot=0.09, sidewalk=0.10, water=-0.9, bed=-1.6)
COLORS = {  # sRGB
    'Cesped': (0.45, 0.56, 0.35), 'Asfalto': (0.21, 0.22, 0.24), 'Acera': (0.70, 0.69, 0.66), 'Bordillo': (0.84, 0.83, 0.80),
    'LineaBlanca': (0.94, 0.94, 0.91), 'LineaAmarilla': (0.96, 0.76, 0.22), 'Pavimento': (0.66, 0.62, 0.56), 'Concreto': (0.58, 0.58, 0.56),
    'Parque': (0.38, 0.60, 0.32), 'Sendero': (0.80, 0.72, 0.56), 'Agua': (0.20, 0.47, 0.64), 'Muro': (0.52, 0.50, 0.47),
    'Lecho': (0.22, 0.24, 0.22), 'Baranda': (0.26, 0.28, 0.31), 'Piedra': (0.74, 0.72, 0.68), 'Lote': (0.30, 0.31, 0.33),
    'Alcantarilla': (0.13, 0.13, 0.14), 'Marquesina': (0.86, 0.22, 0.19), 'Puente': (0.60, 0.58, 0.55),
}
NAMES = list(COLORS)


def material_name(key):
    return 'City25_' + key


def river_center(x):
    pts = RIVER['points']
    if x <= pts[0][0]:
        return pts[0][1]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if x <= bx:
            return ay + (by - ay) * (x - ax) / (bx - ax)
    return pts[-1][1]


class Sink:
    """Reúne caras por sector y material; cada cara lleva sus propios vértices (sombreado plano)."""

    def __init__(self):
        self.parts = {}

    def key(self, x, y):
        clamp = lambda v: max(0, min(COUNT - 1, int((v + HALF) // SECTOR)))
        return clamp(x), clamp(y)

    def face(self, pts, material):
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        part = self.parts.setdefault(self.key(cx, cy), dict(v=[], f=[], m=[]))
        base = len(part['v'])
        part['v'].extend(pts)
        part['f'].append(list(range(base, base + len(pts))))
        part['m'].append(NAMES.index(material))

    def quad(self, a, b, c, d, z, material):
        # a-b-c-d en sentido antihorario visto desde arriba.
        self.face([(a[0], a[1], z), (b[0], b[1], z), (c[0], c[1], z), (d[0], d[1], z)], material)

    def wall(self, a, b, z0, z1, material):
        # Cara vertical de a hacia b; mira a la derecha del recorrido.
        self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], material)

    def box(self, a, b, width, z0, z1, material):
        # Prisma entre dos puntos del plano: barandas, postes y bordes de puente.
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length * width / 2, dx / length * width / 2
        p = [(a[0] - nx, a[1] - ny), (b[0] - nx, b[1] - ny), (b[0] + nx, b[1] + ny), (a[0] + nx, a[1] + ny)]
        self.quad(p[0], p[1], p[2], p[3], z1, material)
        for i in range(4):
            self.wall(p[i], p[(i + 1) % 4], z0, z1, material)

    def post(self, x, y, size, z0, z1, material):
        self.box((x - size / 2, y), (x + size / 2, y), size, z0, z1, material)

    def disc(self, cx, cy, r0, r1, z, material, segments=32):
        # Disco (r0 = 0) o anillo plano.
        for k in range(segments):
            a0, a1 = 2 * math.pi * k / segments, 2 * math.pi * (k + 1) / segments
            outer = [(cx + r1 * math.cos(a), cy + r1 * math.sin(a)) for a in (a0, a1)]
            if r0 <= 0:
                self.face([(cx, cy, z), (outer[0][0], outer[0][1], z), (outer[1][0], outer[1][1], z)], material)
            else:
                inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)) for a in (a0, a1)]
                self.quad(inner[0], outer[0], outer[1], inner[1], z, material)

    def cylinder(self, cx, cy, r, z0, z1, material, segments=24, inward=False):
        for k in range(segments):
            a0, a1 = 2 * math.pi * k / segments, 2 * math.pi * (k + 1) / segments
            p0, p1 = (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))
            self.wall(p1, p0, z0, z1, material) if inward else self.wall(p0, p1, z0, z1, material)

    def split_rect(self, x0, y0, x1, y1, z, material):
        # Rectángulo alineado a los ejes partido en los bordes de sector.
        cuts = lambda a, b: sorted({a, b, *[-HALF + k * SECTOR for k in range(1, COUNT) if a < -HALF + k * SECTOR < b]})
        xs, ys = cuts(x0, x1), cuts(y0, y1)
        for xa, xb in zip(xs, xs[1:]):
            for ya, yb in zip(ys, ys[1:]):
                self.quad((xa, ya), (xb, ya), (xb, yb), (xa, yb), z, material)


# --- geometría de vías ---
class Polyline:
    def __init__(self, points):
        self.points = [tuple(p) for p in points]
        self.closed = len(self.points) > 2 and math.dist(self.points[0], self.points[-1]) < .5
        self.normals = [self.miter(i) for i in range(len(self.points))]

    def direction(self, i):
        a, b = self.points[i], self.points[i + 1]
        length = math.dist(a, b) or 1.0
        return (b[0] - a[0]) / length, (b[1] - a[1]) / length

    def miter(self, i):
        # Normal izquierda promediada en cada vértice para que las franjas empalmen sin huecos.
        n = len(self.points)
        dirs = []
        if i > 0:
            dirs.append(self.direction(i - 1))
        elif self.closed:
            dirs.append(self.direction(n - 2))
        if i < n - 1:
            dirs.append(self.direction(i))
        elif self.closed:
            dirs.append(self.direction(0))
        ux = sum(d[0] for d in dirs) / len(dirs)
        uy = sum(d[1] for d in dirs) / len(dirs)
        length = math.hypot(ux, uy) or 1.0
        ux, uy = ux / length, uy / length
        scale = 1.0
        if len(dirs) == 2:
            cos = dirs[0][0] * ux + dirs[0][1] * uy
            scale = 1.0 / max(cos, .5)
        return -uy * scale, ux * scale

    def offset(self, i, distance):
        x, y = self.points[i]
        nx, ny = self.normals[i]
        return x + nx * distance, y + ny * distance

    def pieces(self, step):
        # Tramos cortos (inicio, fin) por segmento, con los desplazamientos interpolados entre vértices.
        for i in range(len(self.points) - 1):
            length = math.dist(self.points[i], self.points[i + 1])
            n = max(1, int(math.ceil(length / step)))
            for k in range(n):
                yield i, k / n, (k + 1) / n

    def at(self, i, t, distance):
        a, b = self.offset(i, distance), self.offset(i + 1, distance)
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


class RoadIndex:
    """Rejilla de segmentos para saber rápido si un punto cae sobre la calzada de otra vía."""

    def __init__(self, roads, cell=40.0):
        self.cell, self.grid = cell, {}
        for road in roads:
            half = KINDS[road['kind']]['width'] / 2
            for a, b in zip(road['points'], road['points'][1:]):
                x0, x1 = min(a[0], b[0]) - half, max(a[0], b[0]) + half
                y0, y1 = min(a[1], b[1]) - half, max(a[1], b[1]) + half
                for gx in range(int(x0 // cell), int(x1 // cell) + 1):
                    for gy in range(int(y0 // cell), int(y1 // cell) + 1):
                        self.grid.setdefault((gx, gy), []).append((road['id'], a, b, half))

    def inside(self, x, y, exclude, margin=0.3):
        for rid, a, b, half in self.grid.get((int(x // self.cell), int(y // self.cell)), ()):
            if rid == exclude:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            length2 = dx * dx + dy * dy
            t = 0 if length2 < 1e-9 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / length2))
            if math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) < half + margin:
                return True
        return False


def runs(flags):
    # Agrupa tramos consecutivos aceptados: (primero, último).
    start = None
    for i, ok in enumerate(flags + [False]):
        if ok and start is None:
            start = i
        elif not ok and start is not None:
            yield start, i - 1
            start = None


def build_roads(sink):
    index = RoadIndex(PLAN['roads'])
    nodes = {}
    for node in PLAN['intersections']:
        width = max(KINDS[r['kind']]['width'] for r in PLAN['roads'] if r['id'] in node['roads'])
        for rid in node['roads']:
            nodes.setdefault(rid, []).append((node['x'], node['y'], width / 2 + 4))
    for road in PLAN['roads']:
        k = KINDS[road['kind']]
        line = Polyline(road['points'])
        half = k['width'] / 2
        pieces = list(line.pieces(50.0))
        for i, t0, t1 in pieces:
            sink.quad(line.at(i, t0, -half), line.at(i, t1, -half), line.at(i, t1, half), line.at(i, t0, half), Z['asphalt'], 'Asfalto')
        if k['sidewalk']:
            sidewalks(sink, line, road, half, k['sidewalk'], index)
        markings(sink, line, road, half, k, nodes.get(road['id'], []))


def sidewalks(sink, line, road, half, width, index):
    pieces = list(line.pieces(2.0))
    for side in (1, -1):
        inner, curb, outer = side * half, side * (half + .3), side * (half + width)
        mid = side * (half + width / 2)
        keep = []
        for i, t0, t1 in pieces:
            pts = [line.at(i, t, d) for t in (t0, (t0 + t1) / 2, t1) for d in (inner + side * .2, mid, outer)]
            keep.append(not any(index.inside(x, y, road['id']) for x, y in pts))
        for first, last in runs(keep):
            # Se juntan tramos del mismo segmento en caras de hasta 50 m.
            group = []
            for n in range(first, last + 1):
                i, t0, t1 = pieces[n]
                if group and (group[-1][0] != i or len(group) >= 25):
                    emit_sidewalk(sink, line, group, inner, curb, outer, side)
                    group = []
                group.append(pieces[n])
            if group:
                emit_sidewalk(sink, line, group, inner, curb, outer, side)


def emit_sidewalk(sink, line, group, inner, curb, outer, side):
    i, t0, t1 = group[0][0], group[0][1], group[-1][2]
    a0, a1 = line.at(i, t0, inner), line.at(i, t1, inner)
    c0, c1 = line.at(i, t0, curb), line.at(i, t1, curb)
    o0, o1 = line.at(i, t0, outer), line.at(i, t1, outer)
    if side > 0:
        sink.quad(a0, a1, c1, c0, Z['sidewalk'], 'Bordillo')
        sink.quad(c0, c1, o1, o0, Z['sidewalk'], 'Acera')
        sink.wall(a0, a1, Z['asphalt'], Z['sidewalk'], 'Bordillo')
        sink.wall(o1, o0, Z['ground'], Z['sidewalk'], 'Acera')
    else:
        sink.quad(c0, c1, a1, a0, Z['sidewalk'], 'Bordillo')
        sink.quad(o0, o1, c1, c0, Z['sidewalk'], 'Acera')
        sink.wall(a1, a0, Z['asphalt'], Z['sidewalk'], 'Bordillo')
        sink.wall(o0, o1, Z['ground'], Z['sidewalk'], 'Acera')


def markings(sink, line, road, half, k, nodes):
    def clear(x, y):
        return all(math.hypot(x - nx, y - ny) > r for nx, ny, r in nodes)

    def strip(offset, width, material, dash=None, gap=None):
        walked = 0.0
        for i, t0, t1 in line.pieces(1.5):
            length = math.dist(line.points[i], line.points[i + 1]) * (t1 - t0)
            on = dash is None or (walked % (dash + gap)) < dash
            walked += length
            p0, p1 = line.at(i, t0, offset), line.at(i, t1, offset)
            if not on or not clear(*p0) or not clear(*p1):
                continue
            q0, q1 = line.at(i, t0, offset + width), line.at(i, t1, offset + width)
            sink.quad(p0, p1, q1, q0, Z['marking'], material)

    if road['kind'] in ('ring', 'avenue', 'boulevard'):
        strip(.1, .14, 'LineaAmarilla')
        strip(-.24, .14, 'LineaAmarilla')
    elif road['kind'] == 'street':
        strip(-.07, .14, 'LineaBlanca', 3.0, 4.0)
    if k['lanes'] == 2 and road['kind'] != 'roundabout':
        strip(half / 2 - .07, .14, 'LineaBlanca', 3.0, 6.0)
        strip(-half / 2 - .07, .14, 'LineaBlanca', 3.0, 6.0)


def crosswalks(sink):
    for c in PLAN['crosswalks']:
        ux, uy = c['along']
        px, py = -uy, ux  # a través de la calzada
        t = -c['length'] / 2 + .9
        while t <= c['length'] / 2 - .9:
            cx, cy = c['x'] + px * t, c['y'] + py * t
            a = (cx - ux * 1.5 - px * .3, cy - uy * 1.5 - py * .3)
            b = (cx + ux * 1.5 - px * .3, cy + uy * 1.5 - py * .3)
            d = (cx - ux * 1.5 + px * .3, cy - uy * 1.5 + py * .3)
            e = (cx + ux * 1.5 + px * .3, cy + uy * 1.5 + py * .3)
            sink.quad(a, b, e, d, Z['marking'], 'LineaBlanca')
            t += 1.2


# --- suelo, río y puentes ---
def build_land(sink):
    step = 10.0
    edges = [-HALF + k * SECTOR for k in range(COUNT + 1)]
    x = -HALF
    while x < HALF - 1e-6:
        x1 = min(HALF, x + step)
        c0, c1 = river_center(x), river_center(x1)
        bank = WATER + RIVER['bank']
        # Paseo de ribera, muros del cauce, lecho y agua.
        sink.quad((x, c0 + WATER), (x1, c1 + WATER), (x1, c1 + bank), (x, c0 + bank), Z['sidewalk'], 'Acera')
        sink.quad((x, c0 - bank), (x1, c1 - bank), (x1, c1 - WATER), (x, c0 - WATER), Z['sidewalk'], 'Acera')
        sink.wall((x, c0 + WATER), (x1, c1 + WATER), Z['bed'], Z['sidewalk'], 'Muro')
        sink.wall((x1, c1 - WATER), (x, c0 - WATER), Z['bed'], Z['sidewalk'], 'Muro')
        sink.quad((x, c0 - WATER), (x1, c1 - WATER), (x1, c1 + WATER), (x, c0 + WATER), Z['bed'], 'Lecho')
        sink.quad((x, c0 - WATER), (x1, c1 - WATER), (x1, c1 + WATER), (x, c0 + WATER), Z['water'], 'Agua')
        # Césped al norte y al sur del río, partido en los bordes de sector.
        for lo, hi, top in (((c0 + bank, c1 + bank), None, True), ((c0 - bank, c1 - bank), None, False)):
            limit = HALF if top else -HALF
            inner = max(lo) if top else min(lo)
            cuts = [e for e in edges if (inner < e < limit if top else limit < e < inner)]
            bounds = sorted(cuts + [limit], reverse=not top)
            first = bounds[0]
            if top:
                sink.quad((x, lo[0]), (x1, lo[1]), (x1, first), (x, first), Z['ground'], 'Cesped')
                for ya, yb in zip(bounds, bounds[1:]):
                    sink.quad((x, ya), (x1, ya), (x1, yb), (x, yb), Z['ground'], 'Cesped')
            else:
                sink.quad((x, first), (x1, first), (x1, lo[1]), (x, lo[0]), Z['ground'], 'Cesped')
                for ya, yb in zip(bounds, bounds[1:]):
                    sink.quad((x, yb), (x1, yb), (x1, ya), (x, ya), Z['ground'], 'Cesped')
        x = x1


def crossing_road(x, y):
    for road in PLAN['roads']:
        k = KINDS[road['kind']]
        reach = k['width'] / 2 + k['sidewalk'] + .6
        for a, b in zip(road['points'], road['points'][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length2 = dx * dx + dy * dy
            t = 0 if length2 < 1e-9 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / length2))
            if math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) < reach:
                return True
    return False


def railings(sink):
    # Barandas a lo largo del cauce, interrumpidas donde pasa un puente.
    for side in (1, -1):
        x = -HALF
        previous = None
        while x <= HALF:
            y = river_center(x) + side * (WATER + .15)
            if crossing_road(x, y):
                previous = None
            else:
                sink.post(x, y, .12, Z['sidewalk'], 1.05, 'Baranda')
                if previous:
                    sink.box(previous, (x, y), .08, .95, 1.05, 'Baranda')
                previous = (x, y)
            x += 3.0


def bridges(sink):
    for road in PLAN['roads']:
        k = KINDS[road['kind']]
        line = Polyline(road['points'])
        reach = k['width'] / 2 + k['sidewalk']
        for side in (1, -1):
            previous = None
            for i, t0, t1 in line.pieces(2.0):
                x, y = line.at(i, t0, 0)
                over = abs(y - river_center(x)) < WATER + 1.5
                if not over:
                    previous = None
                    continue
                edge0, edge1 = line.at(i, t0, side * reach), line.at(i, t1, side * reach)
                rail0 = line.at(i, t0, side * (reach - .15))
                if side > 0:
                    sink.wall(edge1, edge0, -.7, Z['sidewalk'], 'Puente')
                else:
                    sink.wall(edge0, edge1, -.7, Z['sidewalk'], 'Puente')
                    other0, other1 = line.at(i, t0, -side * reach), line.at(i, t1, -side * reach)
                    sink.face([(edge0[0], edge0[1], -.7), (other0[0], other0[1], -.7), (other1[0], other1[1], -.7), (edge1[0], edge1[1], -.7)], 'Puente')
                sink.post(rail0[0], rail0[1], .14, Z['sidewalk'], 1.1, 'Baranda')
                if previous:
                    sink.box(previous, rail0, .1, 1.0, 1.1, 'Baranda')
                previous = rail0


# --- zonas, plaza, parque, lotes ---
def surfaces(sink):
    for x0, y0, x1, y1, kind in PLAN['surfaces']:
        sink.split_rect(x0, y0, x1, y1, Z['slab'], kind)


def plaza(sink):
    r = PLAN['plaza_radius'] - KINDS['roundabout']['width'] / 2 - KINDS['roundabout']['sidewalk']
    sink.disc(0, 0, 0, r, Z['sidewalk'], 'Pavimento', 48)
    sink.disc(0, 0, 14, r - 5, Z['sidewalk'] + .02, 'Parque', 48)
    # Fuente: pileta, agua, pedestal y copa.
    sink.cylinder(0, 0, 9, Z['sidewalk'], .75, 'Piedra', 32)
    sink.cylinder(0, 0, 8.5, Z['sidewalk'], .75, 'Piedra', 32, inward=True)
    sink.disc(0, 0, 8.5, 9, .75, 'Piedra', 32)
    sink.disc(0, 0, 0, 8.5, .55, 'Agua', 32)
    sink.cylinder(0, 0, 1.0, .55, 2.4, 'Piedra', 16)
    sink.cylinder(0, 0, 2.6, 2.4, 2.75, 'Piedra', 20)
    sink.disc(0, 0, 0, 2.6, 2.75, 'Agua', 20)


def park(sink):
    x0, y0, x1, y1 = PLAN['park']
    scale = (x1 - x0) / (850 - 440)  # los senderos del mapa están en el espacio de diseño del parque
    to_world = lambda p: (x0 + (p[0] - 440) * scale, y0 + (p[1] - 440) * scale)
    for path in ([(470, 480), (560, 600), (700, 640), (820, 820)], [(470, 800), (600, 700), (760, 560), (820, 470)]):
        line = Polyline([to_world(p) for p in path])
        for i, t0, t1 in line.pieces(8.0):
            sink.quad(line.at(i, t0, -1.6), line.at(i, t1, -1.6), line.at(i, t1, 1.6), line.at(i, t0, 1.6), Z['lot'], 'Sendero')
    cx, cy = to_world((645, 645))
    radius = 45 * scale
    sink.disc(cx, cy, 0, radius, Z['sidewalk'] + .03, 'Agua', 40)
    sink.cylinder(cx, cy, radius + 1.2, Z['ground'], .4, 'Piedra', 40)
    sink.cylinder(cx, cy, radius, Z['sidewalk'], .4, 'Piedra', 40, inward=True)
    sink.disc(cx, cy, radius, radius + 1.2, .4, 'Piedra', 40)


def lots(sink):
    for o in OBJECTS:
        yaw = math.radians(o.get('yaw', 0))
        fx, fy = math.sin(yaw), math.cos(yaw)  # hacia la calle
        rx, ry = fy, -fx
        point = lambda a, b: (o['x'] + rx * a + fx * b, o['y'] + ry * a + fy * b)
        if o['kit'] == 'Lot':
            w, d = o['size']
            sink.quad(point(-w / 2, -d / 2), point(w / 2, -d / 2), point(w / 2, d / 2), point(-w / 2, d / 2), Z['lot'], 'Lote')
            if o['spot'] == 'estacionamiento':
                for k in range(7):
                    a = -w / 2 + .7 + k * 4.6
                    sink.quad(point(a - .07, -d / 2 + .5), point(a + .07, -d / 2 + .5), point(a + .07, -1), point(a - .07, -1), Z['lot'] + .01, 'LineaBlanca')
            else:
                for a, b in ((-8, -4), (8, -4), (-8, 4), (8, 4)):
                    p = point(a, b)
                    sink.post(p[0], p[1], .3, Z['lot'], 4.6, 'Baranda')
                corners = [point(-9.5, -5.5), point(9.5, -5.5), point(9.5, 5.5), point(-9.5, 5.5)]
                sink.face([(x, y, 5.1) for x, y in corners], 'Marquesina')
                sink.face([(x, y, 4.6) for x, y in reversed(corners)], 'Marquesina')
                for m in range(4):
                    sink.wall(corners[m], corners[(m + 1) % 4], 4.6, 5.1, 'Marquesina')
        elif o['kit'] == 'Sewer':
            sink.disc(o['x'], o['y'], 0, .45, Z['sidewalk'] + .006, 'Alcantarilla', 10)


# --- salida ---
def materials():
    out = {}
    for key, (r, g, b) in COLORS.items():
        m = bpy.data.materials.new(material_name(key))
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in (r, g, b)]
        m.diffuse_color = (*linear, 1)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (*linear, 1)
        bsdf.inputs['Roughness'].default_value = .9
        out[key] = m
    return out


def build_objects(sink, mats):
    objects = {}
    for (i, j), part in sorted(sink.parts.items()):
        cx, cy = -HALF + (i + .5) * SECTOR, -HALF + (j + .5) * SECTOR
        mesh = bpy.data.meshes.new(f'Ground_{i}_{j}')
        mesh.from_pydata([(x - cx, y - cy, z) for x, y, z in part['v']], [], part['f'])
        used = sorted(set(part['m']))
        for key in used:
            mesh.materials.append(mats[NAMES[key]])
        remap = {key: n for n, key in enumerate(used)}
        mesh.polygons.foreach_set('material_index', [remap[m] for m in part['m']])
        mesh.validate()
        mesh.update()
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.location = (cx, cy, 0)
        bpy.context.scene.collection.objects.link(obj)
        objects[(i, j)] = obj
    return objects


def save(objects):
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for (i, j), obj in objects.items():
        location = obj.location.copy()
        obj.location = (0, 0, 0)  # el FBX lleva la malla relativa al centro del sector
        bpy.context.view_layer.update()
        export([obj], OUT / f'{obj.name}.fbx')
        obj.location = location
        report.append(dict(id=obj.name, sector=[i, j], center=[location.x, location.y], faces=len(obj.data.polygons)))
    manifest = dict(materials=[dict(name=material_name(k), r=c[0], g=c[1], b=c[2], a=1, metallic=0, roughness=.9) for k, c in COLORS.items()])
    (OUT / 'ground_materials.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    (OUT / 'ground.json').write_text(json.dumps(dict(sector_m=SECTOR, count=COUNT, half=HALF, heights=Z, sectors=report), indent=1), encoding='utf-8')
    return report


# --- revisión: kit colocado y vistas renderizadas ---
def place_kit():
    pieces = {}
    library = bpy.data.collections.new('Kit25')
    bpy.context.scene.collection.children.link(library)
    for path in KIT.glob('*/*.fbx'):
        if path.parent.name == 'Ground25':
            continue
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(path))
        for o in set(bpy.data.objects) - before:
            if o.type == 'MESH':
                pieces[path.stem] = o.data
            for c in o.users_collection:
                c.objects.unlink(o)
            library.objects.link(o)
    library.hide_render = True
    city = bpy.data.collections.new('Ciudad')
    bpy.context.scene.collection.children.link(city)
    placed = 0
    for o in OBJECTS:
        data = pieces.get(o['kit'])
        if data is None:
            continue
        obj = bpy.data.objects.new(o['kit'], data)
        obj.location = (o['x'], o['y'], 0)
        obj.rotation_euler = (0, 0, math.radians(180 - o['yaw']))  # frente -Y hacia el rumbo
        city.objects.link(obj)
        placed += 1
    return placed


def render_views():
    scene = bpy.context.scene
    for engine in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    if hasattr(scene, 'eevee'):
        scene.eevee.taa_render_samples = 16
    world = bpy.data.worlds.new('Cielo')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (.55, .72, .88, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .9
    scene.world = world
    sun = bpy.data.objects.new('Sol', bpy.data.lights.new('Sol', 'SUN'))
    sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(48), 0, math.radians(30))
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    cam.data.clip_end = 3000
    scene.collection.objects.link(cam)
    scene.camera = cam
    hideout = next(p for p in PLAN['places'] if p['kind'] == 'escondite')['position']
    bank = next(p for p in PLAN['places'] if p['name'] == 'Banco Central')['position']
    views = {
        'aerea_centro': ((-260, -330, 230), (20, 40, 0), 40),
        'plaza_calle': ((0, -120, 1.7), (0, 0, 2), 60),
        'banco_central': ((bank[0] - 18, bank[1] - 22, 2.0), (bank[0], bank[1], 3), 65),
        'escondite': ((hideout[0] + 25, hideout[1] - 20, 2.0), (hideout[0], hideout[1], 2), 65),
        'rio_puente': ((-120, -520, 18), (-40, -440, 0), 55),
        'aerea_ciudad': ((-1100, -1300, 900), (0, 0, 0), 38),
    }
    for name, (eye, target, lens) in views.items():
        cam.location = eye
        cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens_unit = 'FOV'
        cam.data.angle = math.radians(lens)
        scene.render.filepath = str(HERE / 'renders' / f'ciudad_{name}.png')
        bpy.ops.render.render(write_still=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
sink = Sink()
build_land(sink)
surfaces(sink)
build_roads(sink)
crosswalks(sink)
railings(sink)
bridges(sink)
plaza(sink)
park(sink)
lots(sink)
objects = build_objects(sink, materials())
report = save(objects)
print('SUELO', len(report), 'sectores', sum(r['faces'] for r in report), 'caras')
if '--preview' in sys.argv:
    print('KIT', place_kit(), 'objetos')
    render_views()
