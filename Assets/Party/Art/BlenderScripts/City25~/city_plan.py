"""Plano de la ciudad (2 × 2 km por defecto) y mapa de estilo videojuego.

Trazado menos cuadriculado: bulevar diagonal, plaza con rotonda, río con puentes, avenidas con curvas,
parque sin calles que lo crucen, naves industriales grandes y calles que terminan en la ribera.
Es la fuente de datos única de la ciudad nueva: el kit de Blender y el generador de Unity leerán city_plan.json.
Cambiar un ancho, una avenida o un local es cambiar un dato aquí, no código. CITY_SIZE fija el tamaño:
el trazado se diseña en coordenadas de 2,5 km y se escala; anchos de calles y aceras no cambian.
Uso: python city_plan.py
Salida: city_plan.json, city_objects.json (edificios y mobiliario, ver city_objects.py), cuadras.png y plano_ciudad.png en esta carpeta;
mapa_base.png, iconos y map_places.json en Art/UI/Map para el mapa del juego.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from city_life import build_life, build_signals
from city_objects import SECTOR, place_all
from city_traffic import build_traffic

HERE = Path(__file__).resolve().parent
UI = HERE.parent.parent / 'UI' / 'Map'
KIT = HERE.parent.parent / 'City' / 'Kit25' / 'kit.json'
STREET_KIT = KIT.with_name('street_kit.json')  # build_street_kit.py
# Fuentes libres (OFL) que trae Blender; no se usan fuentes de Windows en recursos del juego.
FONTS = Path('C:/Program Files/Blender Foundation/Blender 5.2/5.2/datafiles/fonts')
CITY_SIZE = 2000         # lado de la ciudad en metros
DESIGN_HALF = 1250       # las coordenadas escritas abajo están en este espacio de diseño
SCALE = CITY_SIZE / 2 / DESIGN_HALF
HALF = CITY_SIZE / 2
CELL = 2.0  # metros por píxel del raster de cuadras


def W(p):
    # Del espacio de diseño al mundo real.
    return (p[0] * SCALE, p[1] * SCALE)

KINDS = {
    'ring':       dict(width=24, lanes=2, sidewalk=0, label='Circunvalación'),
    'boulevard':  dict(width=26, lanes=2, sidewalk=5, label='Bulevar'),
    'avenue':     dict(width=20, lanes=2, sidewalk=5, label='Avenida'),
    'roundabout': dict(width=14, lanes=2, sidewalk=4, label='Rotonda'),
    'street':     dict(width=12, lanes=1, sidewalk=3.5, label='Calle'),
}
RIVER_WIDTH, RIVER_BANK = 46, 7
RIVER = [(-1260, -600), (-900, -520), (-560, -610), (-200, -540), (150, -600), (520, -500), (900, -570), (1260, -520)]
PARK = (440, 440, 850, 850)       # Parque Central: sin calles que lo crucen
PLAZA_R = 55                       # rotonda de la plaza central
RIVER_WORLD = [W(p) for p in RIVER]

PLACES = [
    # (tipo, nombre, punto deseado)
    ('escondite', 'El escondite', (-640, 220)),
    ('banco', 'Banco Central', (90, 70)), ('banco', 'Banco Sin Prisa', (-180, 280)), ('banco', 'Banco del Puerto', (330, -230)),
    ('joyeria', 'Brilla Joyería', (-80, -170)), ('joyeria', 'Oro Fino', (260, 160)), ('joyeria', 'Diamante Azul', (-300, -60)),
    ('supermercado', 'Súper Ahorro', (-260, -280)), ('supermercado', 'Mercado Grande', (300, 380)),
    ('supermercado', 'Súper Barrio', (-700, 650)), ('supermercado', 'Hiper Sur', (-300, -760)),
    ('minimarket', 'Mini Todo', (170, -280)), ('minimarket', 'Minimarket 24h', (-650, -250)),
    ('minimarket', 'La Esquina', (650, 250)), ('minimarket', 'Abarrotes Lomas', (-180, 650)),
    ('comida', 'Donas El Patrullero', (80, 330)), ('comida', 'Donas El Patrullero', (650, -250)),
    ('comida', 'Burger Bandido', (-430, 120)), ('comida', 'Pizzería Fuga', (180, -90)),
    ('comida', 'Café Pánico', (-120, 160)), ('comida', 'Tacos La Sirena', (60, -700)),
    ('ropa', 'Buena Pinta', (-300, 190)), ('ropa', 'Moda Rápida', (290, -40)),
    ('estacionamiento', 'Parking Bajo Perfil', (160, 260)), ('estacionamiento', 'Parking Ribera', (-560, -420)),
    ('taller', 'Taller de pintura', (700, -760)), ('taller', 'Garaje Express', (-760, -900)),
    ('reducidor', 'Don Trueque', (960, -900)),
    ('comisaria', 'Comisaría Centro', (-560, 40)), ('comisaria', 'Comisaría Este', (720, -120)),
    ('gasolinera', 'Gasolinera Norte', (0, 1010)), ('gasolinera', 'Gasolinera Oeste', (-1010, 0)), ('gasolinera', 'Gasolinera Este', (1010, 300)),
    ('alcantarilla', 'Alcantarilla Centro', (-60, -420)), ('alcantarilla', 'Alcantarilla Sur', (900, -1020)),
]
CATEGORIES = {
    # tipo: (grupo, nombre en la leyenda, color de la marca, glifo de Noto Emoji)
    'banco':           ('ROBOS', 'Banco', (46, 204, 113), '\U0001F3E6'),
    'joyeria':         ('ROBOS', 'Joyería', (41, 197, 246), '\U0001F48E'),
    'supermercado':    ('ROBOS', 'Supermercado', (243, 156, 18), '\U0001F6D2'),
    'minimarket':      ('ROBOS', 'Minimarket', (241, 196, 15), '\U0001F6CD'),
    'comida':          ('SERVICIOS', 'Comida (distrae a la policía)', (255, 111, 168), '\U0001F369'),
    'ropa':            ('SERVICIOS', 'Ropa (cambia de aspecto)', (155, 89, 182), '\U0001F455'),
    'taller':          ('SERVICIOS', 'Taller y garaje', (230, 126, 34), '\U0001F527'),
    'estacionamiento': ('SERVICIOS', 'Estacionamiento', (52, 152, 219), '\U0001F697'),
    'gasolinera':      ('SERVICIOS', 'Gasolinera', (231, 76, 60), '\u26FD'),
    'reducidor':       ('SERVICIOS', 'Reducidor (vende el botín)', (22, 160, 133), '\U0001F4E6'),
    'escondite':       ('REFUGIO', 'Escondite', (255, 210, 63), '\U0001F3E0'),
    'alcantarilla':    ('REFUGIO', 'Alcantarilla (escape)', (127, 140, 141), '\U0001F573'),
    'comisaria':       ('POLICÍA', 'Comisaría', (47, 91, 211), '\U0001F46E'),
}
ZONES = {
    'financiero':  dict(map=(44, 53, 77), label='Centro financiero'),
    'comercial':   dict(map=(66, 56, 50), label='Barrio comercial'),
    'residencial': dict(map=(44, 58, 51), label='Residencial'),
    'industrial':  dict(map=(58, 54, 50), label='Zona industrial'),
    'parque':      dict(map=(47, 107, 69), label='Parque'),
    'afueras':     dict(map=(48, 50, 44), label='Afueras'),
}


# --- geometría ---
def river_distance(x, y):
    # Distancia al eje del río, para no poner edificios ni faroles sobre la ribera o los puentes.
    best = 1e9
    for (ax, ay), (bx, by) in zip(RIVER_WORLD, RIVER_WORLD[1:]):
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(ax + t * dx - x, ay + t * dy - y))
    return best - RIVER_WIDTH / 2


def interp(points, x):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


def rounded_square(half, radius, steps=7):
    pts = []
    for cx, cy, a0 in ((half - radius, half - radius, 0), (-half + radius, half - radius, 90),
                       (-half + radius, -half + radius, 180), (half - radius, -half + radius, 270)):
        for k in range(steps + 1):
            a = math.radians(a0 + 90 * k / steps)
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts + [pts[0]]


def circle(r, steps=40, cx=0, cy=0):
    return [(cx + r * math.cos(2 * math.pi * k / steps), cy + r * math.sin(2 * math.pi * k / steps)) for k in range(steps + 1)]


def blocked(x, y, kind):
    # Dónde no puede pasar una vía de ese tipo.
    # Las avenidas entran en la rotonda; las calles se quedan antes de la plaza.
    if math.hypot(x, y) < (PLAZA_R + 25 if kind == 'street' else PLAZA_R - 4):
        return True
    if kind != 'street':
        return False
    if abs(y - interp(RIVER, x)) < RIVER_WIDTH / 2 + RIVER_BANK + 8:
        return True
    if PARK[0] < x < PARK[2] and PARK[1] < y < PARK[3]:
        return True
    if x > 440 and y < interp(RIVER, x) - 20 and abs(y + 820) > 10:
        return True  # naves industriales grandes: sin calles internas
    return False


def clipped(points, kind, step=2.0):
    # Parte una vía (recta o curva) en los trozos que no atraviesan zonas prohibidas (río, parque, plaza, naves).
    samples = []
    for a, b in zip(points, points[1:]):
        n = max(1, int(math.dist(a, b) / step))
        samples += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    samples.append(points[-1])
    pieces, run = [], []
    for q in samples + [None]:
        if q is not None and not blocked(q[0], q[1], kind):
            run.append(q)
            continue
        if len(run) > 15:
            # Se conserva un punto cada ~10 m: suficiente para las curvas, ligero para el tráfico.
            pieces.append(run[::5] + ([run[-1]] if (len(run) - 1) % 5 else []))
        run = []
    return pieces


def wave(x0, x1, y, amplitude, waves):
    return [(x, y + amplitude * math.sin((x - x0) / (x1 - x0) * math.pi * waves)) for x in np.linspace(x0, x1, 60)]


def build_roads():
    roads = []

    def add(name, kind, pts):
        roads.append(dict(id=f'R{len(roads):03d}', name=name, kind=kind, points=[[round(x * SCALE, 1), round(y * SCALE, 1)] for x, y in pts]))

    add('Circunvalación', 'ring', rounded_square(1150, 230))
    add('Plaza Mayor', 'roundabout', circle(PLAZA_R))
    # Avenidas: espaciado irregular y algunas con curva suave.
    avenues = [('Av. Libertad', [(-860, -1150), (-860, 1150)]),
               ('Av. del Puerto', [(-430, -1150), (-430, 220), (-395, 520), (-380, 1150)]),
               ('Av. Las Torres', [(430, -1150), (430, 1150)]),
               ('Av. Oriente', [(880, -1150), (860, -200), (880, 1150)]),
               ('Av. Sur', [(-1150, -820), (1150, -820)]),
               ('Av. Ribera', [(-1150, -330), (-200, -345), (430, -320), (1150, -330)]),
               ('Av. Norte', [(-1150, 440), (1150, 440)]),
               ('Av. Cumbre', [(-1150, 860), (-300, 860), (300, 900), (1150, 880)])]
    for name, pts in avenues:
        add(name, 'avenue', pts)
    # Ejes que entran a la plaza: se cortan en la rotonda.
    # El bulevar diagonal une el suroeste con la plaza y sigue hasta la esquina del parque, sin cruzarlo.
    for name, kind, line in (('Av. Central', 'avenue', [(0, -1150), (0, 1150)]), ('Av. Mayor', 'avenue', [(-1150, 0), (1150, 0)]),
                             ('Bulevar Diagonal', 'boulevard', [(-1090, -970), (0, 0), (428, 436)])):
        for piece in clipped(line, kind):
            add(name, kind, piece)
    # Calles: en el centro cada ~110 m; en los barrios, más separadas y cortadas por río, parque y naves.
    center_x, center_y = [-330, -230, -120, 120, 230, 330], [-230, -120, 120, 230, 330]
    straight = [(f'Calle {x:+d}', [(x, -1150), (x, 1150)]) for x in center_x + [-720, -580, 580, 730, 1010]]
    straight += [(f'Calle {y:+d}N', [(-430, y), (430, y)]) for y in center_y + [600, 740]]
    straight += [(f'Calle {y:+d}N', [(x0, y), (x1, y)]) for y in (-200, 150, 290, 1010) for x0, x1 in ((-1150, -430), (430, 1150))]
    straight += [(f'Calle {y:+d}N', [(430, y), (1150, y)]) for y in (600, 740)]
    straight += [('Calle -680N', [(-1150, -680), (430, -680)])]
    # Calles curvas en Las Lomas y Villa Sur, y un paseo que sigue la orilla norte del río.
    curved = [('Calle Las Lomas', wave(-1150, -430, 670, 55, 3)), ('Calle Villa Sur', wave(-1150, 430, -960, 45, 4)),
              ('Paseo Ribera', [(x, interp(RIVER, x) + RIVER_WIDTH / 2 + RIVER_BANK + 13) for x in np.linspace(-1150, 430, 60)])]
    for name, line in straight + curved:
        for piece in clipped(line, 'street'):
            add(name, 'street', piece)
    return roads


def segments(road):
    pts = road['points']
    return list(zip(pts, pts[1:]))


def cross(p, q, r, s):
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-9:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if -1e-6 <= t <= 1 + 1e-6 and -1e-6 <= u <= 1 + 1e-6:
        return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])), (q[0] - p[0], q[1] - p[1]), (s[0] - r[0], s[1] - r[1])
    return None


def near_road(road, x, y):
    w = KINDS[road['kind']]['width'] / 2
    for a, b in segments(road):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
        if math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) <= w:
            return True
    return False


def build_crossings(roads):
    # Cruces: intersecciones entre vías (o un extremo que toca otra vía), fusionadas si están a menos de 18 m.
    raw = []
    for i, ra in enumerate(roads):
        for rb in roads[i + 1:]:
            if ra['name'] == rb['name']:
                continue  # trozos de la misma vía cortada por el río o la plaza
            for p, q in segments(ra):
                for r, s in segments(rb):
                    hit = cross(p, q, r, s)
                    if hit:
                        raw.append((hit[0], {ra['id']: hit[1], rb['id']: hit[2]}))
    nodes = []
    for point, dirs in raw:
        node = next((n for n in nodes if math.dist(n['p'], point) < 18), None)
        if node is None:
            nodes.append(dict(p=point, dirs=dict(dirs)))
        else:
            node['dirs'].update(dirs)
    by_id = {r['id']: r for r in roads}
    intersections, crosswalks = [], []
    for n in nodes:
        kinds = {by_id[r]['kind'] for r in n['dirs']}
        control = 'rotonda' if 'roundabout' in kinds else 'semaforo' if kinds & {'avenue', 'boulevard', 'ring'} else 'stop'
        x, y = n['p']
        intersections.append(dict(x=round(x, 1), y=round(y, 1), roads=sorted(n['dirs']), control=control))
        if control == 'rotonda':
            continue
        widest = max(KINDS[by_id[r]['kind']]['width'] for r in n['dirs'])
        for rid, (dx, dy) in n['dirs'].items():
            road = by_id[rid]
            if road['kind'] == 'ring':
                continue  # la circunvalación es vía rápida: sin pasos de cebra
            length = math.hypot(dx, dy)
            ux, uy = dx / length, dy / length
            for sign in (1, -1):
                d = widest / 2 + 2.5
                cx, cy = x + sign * ux * d, y + sign * uy * d
                # Solo si la vía sigue en ese sentido (en una T no hay paso hacia la nada).
                if not near_road(road, x + sign * ux * (d + 4), y + sign * uy * (d + 4)):
                    continue
                crosswalks.append(dict(x=round(cx, 1), y=round(cy, 1), along=[round(ux, 3), round(uy, 3)],
                                       length=KINDS[road['kind']]['width'], road=rid))
    bridges = []
    for road in roads:
        if road['kind'] == 'street':
            continue
        for p, q in segments(road):
            for r, s in zip(RIVER_WORLD, RIVER_WORLD[1:]):
                hit = cross(p, q, r, s)
                if hit:
                    bridges.append(dict(road=road['id'], name=road['name'], x=round(hit[0][0], 1), y=round(hit[0][1], 1),
                                        length=RIVER_WIDTH + 2 * RIVER_BANK))
    return intersections, crosswalks, bridges


# --- cuadras a partir de un raster ---
def to_px(x, y, scale):
    return ((x + HALF) * scale, (HALF - y) * scale)


def occupancy(roads):
    n = int(2 * HALF / CELL)
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    s = 1 / CELL
    for road in roads:
        k = KINDS[road['kind']]
        width = (k['width'] + 2 * k['sidewalk']) * s
        pts = [to_px(x, y, s) for x, y in road['points']]
        d.line(pts, fill=255, width=max(1, int(round(width))), joint='curve')
        for px, py in (pts[0], pts[-1]):
            d.ellipse([px - width / 2, py - width / 2, px + width / 2, py + width / 2], fill=255)
    d.line([to_px(x, y, s) for x, y in RIVER_WORLD], fill=255, width=int((RIVER_WIDTH + 2 * RIVER_BANK) * s), joint='curve')
    r = PLAZA_R * SCALE
    d.ellipse([*to_px(-r, r, s), *to_px(r, -r, s)], fill=255)
    return np.array(img) == 0


def label(free):
    # Componentes conexos por tramos de fila con unión-búsqueda (sin dependencias externas).
    h, w = free.shape
    labels = np.zeros((h, w), np.int32)
    parent = [0]

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    prev = []
    for y in range(h):
        edges = np.diff(np.concatenate(([0], free[y].astype(np.int8), [0])))
        runs = []
        for s, e in zip(np.where(edges == 1)[0], np.where(edges == -1)[0]):
            lab = None
            for ps, pe, pl in prev:
                if ps < e and s < pe:
                    root = find(pl)
                    if lab is None:
                        lab = root
                    elif root != lab:
                        parent[root] = lab
            if lab is None:
                lab = len(parent)
                parent.append(lab)
            runs.append((s, e, lab))
            labels[y, s:e] = lab
        prev = runs
    roots = np.array([find(i) for i in range(len(parent))], np.int32)
    return roots[labels]


def zone_of(x, y):
    x, y = x / SCALE, y / SCALE  # las zonas se definen en el espacio de diseño
    if PARK[0] < x < PARK[2] and PARK[1] < y < PARK[3]:
        return 'parque'
    river = interp(RIVER, x)
    if x > 440 and y < river:
        return 'industrial'
    if math.hypot(x, y) < 270:
        return 'financiero'
    if abs(x) < 430 and -330 < y < 440:
        return 'comercial'
    if max(abs(x), abs(y)) > 870:
        return 'afueras'
    return 'residencial'


def build_blocks(roads):
    labels = label(occupancy(roads))
    ids, counts = np.unique(labels[labels > 0], return_counts=True)
    ys, xs = np.nonzero(labels)
    lab = labels[ys, xs]
    sx = np.bincount(lab, weights=xs, minlength=labels.max() + 1)
    sy = np.bincount(lab, weights=ys, minlength=labels.max() + 1)
    blocks, remap = [], np.zeros(labels.max() + 1, np.int32)
    for i, c in zip(ids, counts):
        area = c * CELL * CELL
        if area < 600:
            continue  # restos entre vías: quedan como isletas verdes
        cx = sx[i] / c * CELL - HALF
        cy = HALF - sy[i] / c * CELL
        pix = np.nonzero(labels == i)
        x0, x1 = pix[1].min() * CELL - HALF, (pix[1].max() + 1) * CELL - HALF
        y0, y1 = HALF - (pix[0].max() + 1) * CELL, HALF - pix[0].min() * CELL
        remap[i] = len(blocks) + 1
        blocks.append(dict(id=f'B{len(blocks):03d}', center=[round(cx, 1), round(cy, 1)], bounds=[round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                           area_m2=round(area), zone=zone_of(cx, cy)))
    Image.fromarray(remap[labels].astype(np.uint16)).save(HERE / 'cuadras.png')
    return blocks, remap[labels]


SURFACES = {'financiero': 'Pavimento', 'comercial': 'Pavimento', 'industrial': 'Concreto', 'parque': 'Parque'}


def build_surfaces(blocks, labels):
    # Suelo de cada zona como rectángulos: tramos de fila del raster unidos con los de la fila siguiente si coinciden.
    names = sorted(set(SURFACES.values()))
    lut = np.zeros(labels.max() + 1, np.int8)
    for i, b in enumerate(blocks, start=1):
        if b['zone'] in SURFACES:
            lut[i] = names.index(SURFACES[b['zone']]) + 1
    kind = lut[labels]
    rects, open_runs = [], {}
    for row in range(kind.shape[0] + 1):
        runs = {}
        if row < kind.shape[0]:
            line = kind[row]
            cuts = np.concatenate(([0], np.flatnonzero(np.diff(line)) + 1, [len(line)]))
            for a, b in zip(cuts, cuts[1:]):
                if line[a]:
                    key = (int(a), int(b), int(line[a]))
                    runs[key] = open_runs.pop(key, row)
        for (a, b, k), top in open_runs.items():
            rects.append([round(a * CELL - HALF, 1), round(HALF - row * CELL, 1), round(b * CELL - HALF, 1), round(HALF - top * CELL, 1), names[k - 1]])
        open_runs = runs
    return rects


def build_places(blocks):
    places, used = [], set()
    for kind, name, (px, py) in PLACES:
        options = [b for b in blocks if b['id'] not in used and b['zone'] != 'parque' and b['area_m2'] < 120000]
        best = min(options, key=lambda b: math.dist(b['center'], W((px, py))))
        used.add(best['id'])
        places.append(dict(kind=kind, name=name, block=best['id'], zone=best['zone'], position=best['center']))
    return places


# --- mapa de estilo videojuego ---
def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def blip(category, size=64):
    # Marca circular con borde blanco y glifo blanco, como las del radar de los juegos de mundo abierto.
    group, label_, color, glyph = CATEGORIES[category]
    big = size * 4
    img = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([big * .06, big * .1, big * .98, big * 1.02 - big * .04], fill=(0, 0, 0, 110))
    d.ellipse([big * .04, big * .04, big * .92, big * .92], fill=(255, 255, 255, 255))
    d.ellipse([big * .1, big * .1, big * .86, big * .86], fill=color + (255,))
    g = font('NotoEmoji-VariableFont_wght.woff2', int(big * .42))
    d.text((big * .48, big * .48), glyph, font=g, fill=(255, 255, 255, 255), anchor='mm')
    return img.resize((size, size), Image.LANCZOS)


def arrow(size=56):
    big = size * 4
    img = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tip, base_l, notch, base_r = (big / 2, big * .06), (big * .2, big * .92), (big / 2, big * .72), (big * .8, big * .92)
    d.polygon([tip, base_l, notch, base_r], fill=(255, 255, 255, 255), outline=(20, 24, 28, 255), width=int(big * .05))
    return img.resize((size, size), Image.LANCZOS)


def footprint(o):
    # Esquinas de la planta de un edificio o lote, en el mundo.
    w, d = o['size'][0], o['size'][1]
    yaw = math.radians(o['yaw'])
    fx, fy = math.sin(yaw), math.cos(yaw)
    rx, ry = fy, -fx
    return [(o['x'] + rx * a + fx * b, o['y'] + ry * a + fy * b) for a, b in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]


def draw_map(plan, labels, scale, legend=True, places=True, objects=()):
    size = int(2 * HALF * scale)
    lut = np.zeros((labels.max() + 1, 3), np.uint8)
    lut[0] = (20, 28, 34)
    for i, b in enumerate(plan['blocks'], start=1):
        lut[i] = ZONES[b['zone']]['map']
    base = Image.fromarray(lut[labels]).resize((size, size), Image.LANCZOS)
    img = Image.new('RGB', (size + (560 if legend else 0), size), (16, 22, 28))
    img.paste(base, (0, 0))
    d = ImageDraw.Draw(img, 'RGBA')

    def P(x, y):
        return to_px(x, y, scale)

    def PD(x, y):
        return P(*W((x, y)))
    ui = size / 2000  # tamaño de textos e iconos relativo a la imagen, no a los metros
    # Río con ribera y parque con senderos.
    d.line([P(*p) for p in RIVER_WORLD], fill=(84, 110, 122), width=int((RIVER_WIDTH + 2 * RIVER_BANK) * scale), joint='curve')
    d.line([P(*p) for p in RIVER_WORLD], fill=(30, 110, 170), width=int(RIVER_WIDTH * scale), joint='curve')
    for path in ([(470, 480), (560, 600), (700, 640), (820, 820)], [(470, 800), (600, 700), (760, 560), (820, 470)]):
        d.line([PD(*p) for p in path], fill=(96, 150, 104), width=max(2, int(5 * scale)), joint='curve')
    d.ellipse([*PD(645 - 45, 645 + 45), *PD(645 + 45, 645 - 45)], fill=(40, 120, 170))
    # Plantas de edificios y lotes: dan textura de ciudad sin tapar calles ni marcas.
    for o in objects:
        if o['kit'] == 'Lot':
            d.polygon([P(*c) for c in footprint(o)], fill=(92, 98, 106))
        elif 'kind' in o:
            tone = (30, 30, 30, 70) if o['kind'] in ('tower', 'apartment', 'warehouse') else (255, 255, 255, 28)
            d.polygon([P(*c) for c in footprint(o)], fill=tone, outline=(0, 0, 0, 60))
    order = ['street', 'avenue', 'roundabout', 'boulevard', 'ring']
    colors = {'street': (150, 160, 170), 'avenue': (226, 232, 236), 'roundabout': (226, 232, 236), 'boulevard': (245, 192, 74), 'ring': (240, 168, 48)}
    for kind in order:
        for road in (r for r in plan['roads'] if r['kind'] == kind):
            k = KINDS[kind]
            pts = [P(*p) for p in road['points']]
            if k['sidewalk']:
                d.line(pts, fill=(78, 88, 98), width=int((k['width'] + 2 * k['sidewalk']) * scale), joint='curve')
    for kind in order:
        for road in (r for r in plan['roads'] if r['kind'] == kind):
            pts = [P(*p) for p in road['points']]
            width = int(KINDS[kind]['width'] * scale)
            if kind in ('ring', 'boulevard'):
                d.line(pts, fill=(120, 80, 20), width=width + 4, joint='curve')
            d.line(pts, fill=colors[kind], width=width, joint='curve')
    d.ellipse([*PD(-PLAZA_R + 14, PLAZA_R - 14), *PD(PLAZA_R - 14, -PLAZA_R + 14)], fill=(120, 134, 146))
    d.ellipse([*P(-12, 12), *P(12, -12)], fill=(40, 120, 170))
    for c in plan['crosswalks']:
        ux, uy = c['along']
        half = c['length'] / 2
        ax, ay = c['x'] - uy * half, c['y'] + ux * half
        bx, by = c['x'] + uy * half, c['y'] - ux * half
        d.line([P(ax, ay), P(bx, by)], fill=(250, 250, 250, 200), width=max(1, int(3 * scale)))
    # Nombres de barrios, avenidas y río, sin tapar las marcas.
    district = font('Inter.woff2', int(30 * ui))
    for text, (x, y) in (('CENTRO', (-210, 70)), ('BARRIO COMERCIAL', (-250, 380)), ('PARQUE CENTRAL', (645, 760)),
                         ('ZONA INDUSTRIAL', (720, -700)), ('LAS LOMAS', (-700, 980)), ('VILLA SUR', (-640, -980)),
                         ('RIBERA', (-890, -440)), ('EL MIRADOR', (650, 1000))):
        d.text(PD(x, y), text, font=district, fill=(220, 226, 232, 70), anchor='mm')
    street_font = font('Inter.woff2', int(15 * ui))
    for name, (x, y), angle in (('Av. Libertad', (-860, 650), 90), ('Av. del Puerto', (-412, 380), 84), ('Av. Las Torres', (430, -120), 90),
                                ('Av. Oriente', (870, 600), 90), ('Av. Sur', (-150, -820), 0), ('Av. Ribera', (-650, -338), 0),
                                ('Av. Norte', (-150, 440), 0), ('Av. Cumbre', (-650, 860), 0), ('Bulevar Diagonal', (-520, -462), 41),
                                ('Circunvalación', (-300, 1150), 0), ('Av. Central', (0, -950), 90), ('Av. Mayor', (-650, 0), 0)):
        tw = int(street_font.getlength(name)) + 8
        tag = Image.new('RGBA', (tw, int(22 * ui)), (0, 0, 0, 0))
        ImageDraw.Draw(tag).text((tw / 2, tag.height / 2), name, font=street_font, fill=(30, 34, 38, 255), anchor='mm')
        tag = tag.rotate(angle, expand=True, resample=Image.BICUBIC)
        cx, cy = PD(x, y)
        img.paste(tag, (int(cx - tag.width / 2), int(cy - tag.height / 2)), tag)
    river_font = font('Inter.woff2', int(18 * ui))
    d.text(PD(-180, -570), 'Río Manso', font=river_font, fill=(170, 214, 240), anchor='mm')
    if places:
        icon = int(34 * ui)
        name_font = font('Inter.woff2', int(15 * ui))
        for p in plan['places']:
            mark = blip(p['kind'], icon)
            cx, cy = P(*p['position'])
            img.paste(mark, (int(cx - icon / 2), int(cy - icon / 2)), mark)
            if CATEGORIES[p['kind']][0] in ('ROBOS', 'REFUGIO'):
                d.text((cx + icon * .62, cy), p['name'], font=name_font, fill=(255, 255, 255), anchor='lm',
                       stroke_width=3, stroke_fill=(16, 22, 28))
        hideout = next(p for p in plan['places'] if p['kind'] == 'escondite')
        you = arrow(int(30 * ui)).rotate(-35, expand=True, resample=Image.BICUBIC)
        hx, hy = P(hideout['position'][0] + 55, hideout['position'][1] - 40)
        img.paste(you, (int(hx - you.width / 2), int(hy - you.height / 2)), you)
    if legend:
        lx = size + 32
        d.rectangle([size, 0, size + 560, size], fill=(14, 18, 23))
        d.text((lx, 34), 'ALARMA', font=font('Inter.woff2', 44), fill=(255, 210, 63))
        side = f'{CITY_SIZE / 1000:g}'.replace('.', ',')
        d.text((lx, 88), f'Mapa de la ciudad · {side} × {side} km', font=font('Inter.woff2', 20), fill=(200, 206, 212))
        y = 140
        group = None
        for kind, (g, label_, color, glyph) in CATEGORIES.items():
            if g != group:
                group = g
                y += 14
                d.text((lx, y), g, font=font('Inter.woff2', 18), fill=(150, 160, 170))
                y += 30
            mark = blip(kind, 34)
            img.paste(mark, (lx, y - 4), mark)
            d.text((lx + 48, y + 13), label_, font=font('Inter.woff2', 19), fill=(236, 240, 244), anchor='lm')
            y += 42
        y += 18
        you = arrow(30)
        img.paste(you, (lx + 2, y), you)
        d.text((lx + 48, y + 15), 'Tú (gira hacia donde caminas)', font=font('Inter.woff2', 19), fill=(236, 240, 244), anchor='lm')
        y += 56
        for label_, color in (('Circunvalación y bulevar', (240, 168, 48)), ('Avenida', (226, 232, 236)), ('Calle', (150, 160, 170)), ('Río', (30, 110, 170)), ('Parque', ZONES['parque']['map'])):
            d.rectangle([lx, y + 6, lx + 34, y + 18], fill=color)
            d.text((lx + 48, y + 12), label_, font=font('Inter.woff2', 18), fill=(220, 226, 232), anchor='lm')
            y += 32
        y += 20
        lights = sum(1 for i in plan['intersections'] if i['control'] == 'semaforo')
        stats = (f"{len(plan['blocks'])} cuadras · {len(plan['intersections'])} cruces",
                 f"{lights} con semáforo · {sum(1 for i in plan['intersections'] if i['control'] == 'rotonda')} en rotonda",
                 f"{len(plan['crosswalks'])} pasos de cebra · {len(plan['bridges'])} puentes")
        for line in stats:
            d.text((lx, y), line, font=font('Inter.woff2', 17), fill=(160, 170, 180))
            y += 26
        bar = 500 * scale
        d.rectangle([lx, size - 70, lx + bar, size - 62], fill=(236, 240, 244))
        d.text((lx, size - 56), '500 m', font=font('Inter.woff2', 17), fill=(236, 240, 244))
        d.text((lx + 440, size - 130), 'N ↑', font=font('Inter.woff2', 26), fill=(236, 240, 244))
    return img


def main():
    roads = build_roads()
    intersections, crosswalks, bridges = build_crossings(roads)
    blocks, labels = build_blocks(roads)
    places = build_places(blocks)
    kit = json.loads(KIT.read_text(encoding='utf-8'))
    kit['pieces'] += json.loads(STREET_KIT.read_text(encoding='utf-8'))['pieces']
    partial = dict(kinds=KINDS, roads=roads, intersections=intersections, blocks=blocks, places=places, park=[v * SCALE for v in PARK],
                   crosswalks=crosswalks)
    signals = build_signals(partial)
    # La red peatonal va primero: el mobiliario nuevo se coloca fuera de la franja por donde caminan los peatones.
    life, _, life_stats = build_life(partial)
    objects, _ = place_all(partial, labels, kit, HALF, CELL, river_distance, signals, life)
    (HERE / 'city_life.json').write_text(json.dumps(life, separators=(',', ':')), encoding='utf-8')
    traffic, traffic_stats = build_traffic(partial, signals)
    (HERE / 'city_traffic.json').write_text(json.dumps(traffic, separators=(',', ':')), encoding='utf-8')
    print('vida', life_stats, 'trafico', traffic_stats)
    plan = dict(size_m=2 * HALF, origin='centro', axes='X este, Y norte', kinds=KINDS,
                river=dict(points=RIVER_WORLD, width=RIVER_WIDTH, bank=RIVER_BANK), park=[v * SCALE for v in PARK], plaza_radius=PLAZA_R * SCALE,
                zones={k: v['label'] for k, v in ZONES.items()}, roads=roads, intersections=intersections,
                crosswalks=crosswalks, bridges=bridges, blocks=blocks, places=places, surfaces=build_surfaces(blocks, labels))
    (HERE / 'city_plan.json').write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding='utf-8')
    counts = {}
    for o in objects:
        key = o.get('kind') or o['kit']
        counts[key] = counts.get(key, 0) + 1
    (HERE / 'city_objects.json').write_text(json.dumps(dict(kit='Art/City/Kit25', sector_m=SECTOR, counts=counts, objects=objects),
                                                       ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    draw_map(plan, labels, 2000 / (2 * HALF), objects=objects).save(HERE / 'plano_ciudad.png')
    # Recursos del mapa del juego: fondo sin leyenda ni marcas (las marcas las pone la interfaz), iconos y datos.
    (UI / 'Icons').mkdir(parents=True, exist_ok=True)
    draw_map(plan, labels, 2048 / (2 * HALF), legend=False, places=False, objects=objects).save(UI / 'mapa_base.png')
    for kind in CATEGORIES:
        blip(kind, 64).save(UI / 'Icons' / f'{kind}.png')
    arrow(64).save(UI / 'Icons' / 'jugador.png')
    data = dict(world_min=[-HALF, -HALF], world_max=[HALF, HALF],
                categories=[dict(id=k, group=g, label=l, color='#%02X%02X%02X' % c) for k, (g, l, c, _) in CATEGORIES.items()],
                places=[dict(category=p['kind'], name=p['name'], x=p['position'][0], y=p['position'][1]) for p in places])
    (UI / 'map_places.json').write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding='utf-8')
    zones = {}
    for b in blocks:
        zones[b['zone']] = zones.get(b['zone'], 0) + 1
    print('losas', len(plan['surfaces']), 'vias', len(roads), 'cuadras', len(blocks), zones, 'cruces', len(intersections),
          {c: sum(1 for i in intersections if i['control'] == c) for c in ('semaforo', 'stop', 'rotonda')},
          'pasos', len(crosswalks), 'puentes', len(bridges), 'locales', len(places), 'objetos', len(objects), counts)


main()
