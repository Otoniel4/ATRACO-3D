"""Coloca el kit sobre el plano: edificios mirando a su calle (siguen curvas y diagonales), locales especiales,
lotes de gasolinera y estacionamiento, faroles, semáforos, árboles y mobiliario.
Trabaja sobre el raster de cuadras de city_plan.py; no conoce Unity ni Blender.
Orientación: rumbo en grados, 0 = norte (+Y), 90 = este (+X). El frente del kit (-Y local en Blender) mira hacia ese rumbo.
"""
import math
import random

import numpy as np

STEP = 2.0      # separación de las muestras a lo largo de cada vía
SECTOR = 250.0  # lado de los sectores que Unity activa según la distancia
KINDS_BY_ZONE = {
    'financiero': ['tower', 'tower', 'apartment', 'shop'],
    'comercial': ['shop', 'shop', 'apartment', 'shop'],
    'residencial': ['house', 'house', 'house', 'apartment'],
    'industrial': ['warehouse', 'warehouse', 'shop'],
    'afueras': ['house', 'house', 'warehouse'],
}
SETBACK = {'tower': 3.0, 'apartment': 2.5, 'shop': 0.8, 'house': 4.0, 'warehouse': 6.0}  # retiro desde la acera
GAP = {'tower': 6.0, 'apartment': 4.0, 'shop': 0.5, 'house': 3.0, 'warehouse': 8.0}      # separación lateral
ROAD_ORDER = ['boulevard', 'avenue', 'street', 'ring']  # las vías principales eligen fachada primero
# Edificio que puede ocupar cada local, en orden de preferencia.
PLACE_BUILDINGS = {'banco': ['tower', 'shop', 'apartment'], 'joyeria': ['shop'], 'supermercado': ['shop', 'warehouse'],
                   'minimarket': ['shop'], 'comida': ['shop'], 'ropa': ['shop'], 'taller': ['warehouse', 'shop'],
                   'reducidor': ['warehouse', 'shop'], 'comisaria': ['apartment', 'tower', 'shop'], 'escondite': ['house', 'apartment']}
LOTS = {'gasolinera': (34.0, 24.0), 'estacionamiento': (30.0, 26.0)}  # largo de fachada × fondo
TREES = ['Tree_Fresno_LOD1', 'Tree_Olivo_LOD1', 'Tree_Citrico_LOD1', 'Tree_Pino_LOD2', 'Tree_Jacaranda_LOD2', 'Tree_Palmera_LOD0']
STREET_TREES = ['Tree_Fresno_LOD1', 'Tree_Jacaranda_LOD2', 'Tree_Olivo_LOD1', 'Tree_Palmera_LOD0']
CARS = ['Car_Sedan', 'Car_Hatchback', 'Car_SUV', 'Car_Pickup', 'Car_Van', 'Car_Coupe', 'Car_Taxi']
CAR_SIZE = (2.0, 5.2)  # ancho de carrocería × largo, con margen para la furgoneta
PARKED_SHARE = .15      # fracción de lugares de estacionamiento ocupados en las calles
PARKING_ZONES = ('residencial', 'afueras', 'comercial', 'industrial', 'financiero')
BILLBOARDS = ['Billboard_A', 'Billboard_B', 'Billboard_C']
KIOSK_ZONES = ('comercial', 'financiero', 'parque')  # un kiosco no va en el antejardín de una casa
DUMPSTER_SHARE = {'warehouse': .6, 'apartment': .5, 'tower': .6, 'shop': .15}  # edificios que sacan su basura a un contenedor
SHOPFRONT = ('Bench', 'Bin', 'Planter', 'CafeSet')
PARKED_CARS = [c for c in CARS if c != 'Car_Taxi']  # los taxis circulan; no quedan estacionados en las calles de barrio
STREET_Z, ROAD_Z = .14, .045  # alto de la vereda y del asfalto en build_ground.py
WALK_BAND = .8  # media franja de paso de los peatones alrededor de su línea
# Planta a ras del suelo de las piezas cuya parte ancha va en alto (placas de señales, techo de la parada).
GROUND = {'StopSign': (.2, .2), 'YieldSign': (.2, .2), 'SpeedSign_40': (.2, .2), 'SpeedSign_60': (.2, .2), 'BusStop': (3.95, 1.2)}  # postes de la parada; el techo y el panel van en alto


def heading(nx, ny):
    return round(math.degrees(math.atan2(nx, ny)) % 360, 1)


def samples(points, step=STEP):
    # Puntos equidistantes de una polilínea con su dirección unitaria.
    out = []
    target = 0.0
    walked = 0.0
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        while target <= walked + length:
            s = target - walked
            out.append((ax + ux * s, ay + uy * s, ux, uy))
            target += step
        walked += length
    return out


class Placer:
    def __init__(self, plan, labels, kit, half, cell, river_distance):
        self.plan, self.labels, self.half, self.cell = plan, labels, half, cell
        self.kinds = plan['kinds']
        self.occupied = np.zeros(labels.shape, bool)
        self.by_kind = {}
        for p in kit['pieces']:
            if p['group'] == 'building':
                self.by_kind.setdefault(p['kind'], []).append(p)
        self.river_distance = river_distance
        self.objects = []
        self.kit_pieces = kit['pieces']
        self.rng = random.Random(25)
        self.roads = sorted((r for r in plan['roads'] if r['kind'] in ROAD_ORDER), key=lambda r: ROAD_ORDER.index(r['kind']))
        self.sides = {r['id']: samples(r['points']) for r in self.roads}
        # Rejilla de tramos de calzada para saber si un poste caería sobre el asfalto (curvas, diagonal, esquinas).
        self.asphalt, self.paved = {}, {}
        for road in plan['roads']:
            half = self.kinds[road['kind']]['width'] / 2
            outer = half + self.kinds[road['kind']]['sidewalk']  # borde exterior de la vereda
            for a, b in zip(road['points'], road['points'][1:]):
                for gx in range(int((min(a[0], b[0]) - outer) // 40), int((max(a[0], b[0]) + outer) // 40) + 1):
                    for gy in range(int((min(a[1], b[1]) - outer) // 40), int((max(a[1], b[1]) + outer) // 40) + 1):
                        self.asphalt.setdefault((gx, gy), []).append((a, b, half))
                        self.paved.setdefault((gx, gy), []).append((a, b, outer))

    def on_paved(self, x, y, margin=.1):
        # Calzada o vereda de cualquier vía.
        return self.on_asphalt(x, y, margin, self.paved)

    def on_asphalt(self, x, y, margin=.6, grid=None):
        for a, b, half in (grid or self.asphalt).get((int(x // 40), int(y // 40)), ()):
            dx, dy = b[0] - a[0], b[1] - a[1]
            l2 = dx * dx + dy * dy
            t = 0 if l2 < 1e-9 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / l2))
            if math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) < half + margin:
                return True
        return False

    # --- raster ---
    def cells(self, xs, ys):
        rows = np.floor((self.half - ys) / self.cell).astype(int)
        cols = np.floor((xs + self.half) / self.cell).astype(int)
        return rows, cols

    def label_at(self, x, y):
        r, c = int((self.half - y) // self.cell), int((x + self.half) // self.cell)
        n = self.labels.shape[0]
        return int(self.labels[r, c]) if 0 <= r < n and 0 <= c < n else 0

    def rect(self, cx, cy, u, n, w, d, margin_w=0.0, margin_d=0.0):
        # Celdas que cubre un rectángulo girado: w a lo largo de u y d a lo largo de n.
        a = np.linspace(-w / 2 - margin_w, w / 2 + margin_w, max(2, int(math.ceil((w + 2 * margin_w) / self.cell)) + 1))
        b = np.linspace(-d / 2 - margin_d, d / 2 + margin_d, max(2, int(math.ceil((d + 2 * margin_d) / self.cell)) + 1))
        A, B = np.meshgrid(a, b)
        xs = cx + A * u[0] + B * n[0]
        ys = cy + A * u[1] + B * n[1]
        return self.cells(xs.ravel(), ys.ravel())

    def fits(self, label, cx, cy, u, n, w, d):
        rows, cols = self.rect(cx, cy, u, n, w, d)
        size = self.labels.shape[0]
        if rows.min() < 0 or cols.min() < 0 or rows.max() >= size or cols.max() >= size:
            return False
        return bool((self.labels[rows, cols] == label).all() and not self.occupied[rows, cols].any())

    def occupy(self, cx, cy, u, n, w, d, margin_w=0.0, margin_d=0.0):
        rows, cols = self.rect(cx, cy, u, n, w, d, margin_w, margin_d)
        size = self.labels.shape[0]
        ok = (rows >= 0) & (cols >= 0) & (rows < size) & (cols < size)
        self.occupied[rows[ok], cols[ok]] = True

    def clear_poles(self):
        # Ningún árbol (de parque, lote o vereda) puede quedar pegado a un poste de luz o de semáforo.
        poles = {}
        for o in self.objects:
            if o['kit'] in ('Lamp', 'Signal'):
                poles.setdefault((int(o['x'] // 10), int(o['y'] // 10)), []).append((o['x'], o['y']))
        def crowded(o):
            cx, cy = int(o['x'] // 10), int(o['y'] // 10)
            return any(math.hypot(px - o['x'], py - o['y']) < 4.5
                       for gx in (cx - 1, cx, cx + 1) for gy in (cy - 1, cy, cy + 1) for px, py in poles.get((gx, gy), ()))
        self.objects = [o for o in self.objects if not (o['kit'].startswith('Tree') and crowded(o))]

    def add(self, kit, x, y, yaw, **extra):
        sector = [int((x + self.half) // SECTOR), int((y + self.half) // SECTOR)]
        self.objects.append(dict(kit=kit, x=round(x, 2), y=round(y, 2), yaw=yaw, sector=sector, **extra))
        return self.objects[-1]

    def edge(self, road):
        k = self.kinds[road['kind']]
        return k['width'] / 2 + k['sidewalk']

    # --- lotes sin edificio: gasolineras y estacionamientos ---
    def lots(self):
        for place in self.plan['places']:
            size = LOTS.get(place['kind'])
            if size is None:
                continue
            w, d = size
            px, py = place['position']
            options = []
            for road in self.roads:
                if road['kind'] == 'ring':
                    continue
                edge = self.edge(road)
                for x, y, ux, uy in self.sides[road['id']][::3]:
                    if math.hypot(x - px, y - py) > 220:
                        continue
                    for s in (1, -1):
                        n = (uy * s, -ux * s)
                        cx, cy = x + n[0] * (edge + 1 + d / 2), y + n[1] * (edge + 1 + d / 2)
                        label = self.label_at(cx, cy)
                        if label and self.fits(label, cx, cy, (ux, uy), n, w, d):
                            options.append((math.hypot(cx - px, cy - py), cx, cy, (ux, uy), n))
            if not options:
                raise RuntimeError(f"No hay espacio para {place['name']}")
            _, cx, cy, u, n = min(options, key=lambda o: o[0])
            self.occupy(cx, cy, u, n, w, d, 2, 1)
            front = heading(-n[0], -n[1])
            self.add('Lot', cx, cy, front, size=[w, d], spot=place['kind'], name=place['name'])
            place['position'] = [round(cx - n[0] * (d / 2 - 2), 1), round(cy - n[1] * (d / 2 - 2), 1)]
            if place['kind'] == 'gasolinera':
                # Surtidores en una isla central y el kiosco al fondo.
                for k in range(4):
                    a = -6 + k * 4
                    self.add('EVCharger', cx + u[0] * a, cy + u[1] * a, front)
                self.add('FoodStand', cx + n[0] * (d / 2 - 3), cy + n[1] * (d / 2 - 3), front)
            else:
                for k in range(6):
                    if self.rng.random() < .3:
                        continue
                    a = -w / 2 + 3 + k * 4.6
                    self.add(self.rng.choice(CARS), cx + u[0] * a + n[0] * (d / 4), cy + u[1] * a + n[1] * (d / 4), front, parked=True)

    # --- edificios a lo largo de las vías ---
    def buildings(self):
        for road in self.roads:
            edge = self.edge(road)
            line = self.sides[road['id']]
            for s in (1, -1):
                i = 0
                while i < len(line):
                    x, y, ux, uy = line[i]
                    n = (uy * s, -ux * s)
                    label = self.label_at(x + n[0] * (edge + 3), y + n[1] * (edge + 3))
                    zone = self.plan['blocks'][label - 1]['zone'] if label else None
                    kinds = KINDS_BY_ZONE.get(zone)
                    if not kinds or self.river_distance(x, y) < 40:
                        i += 2
                        continue
                    kind = self.rng.choice(kinds)
                    piece = self.rng.choice(self.by_kind[kind])
                    w, d = piece['width'], piece['depth']
                    j = i + int(round(w / 2 / STEP))
                    if j >= len(line):
                        break
                    xj, yj, uxj, uyj = line[j]
                    u, n = (uxj, uyj), (uyj * s, -uxj * s)
                    placed = False
                    for extra in (0.0, 2.0, 4.0, 7.0):
                        dist = edge + SETBACK[kind] + extra + d / 2
                        cx, cy = xj + n[0] * dist, yj + n[1] * dist
                        if self.fits(label, cx, cy, u, n, w, d):
                            self.occupy(cx, cy, u, n, w, d, GAP[kind] / 2, 1.0)
                            self.add(piece['id'], cx, cy, heading(-n[0], -n[1]), kind=kind, front=[round(-n[0], 4), round(-n[1], 4)],
                                     block=self.plan['blocks'][label - 1]['id'], size=[w, d, piece['height']], road=road['id'])
                            placed = True
                            break
                    i = j + int(math.ceil((w / 2 + GAP[kind]) / STEP)) if placed else i + 2

    def assign_places(self):
        # Cada local ocupa el edificio adecuado más cercano; su posición pasa a ser la puerta.
        taken = set()
        buildings = [o for o in self.objects if 'kind' in o]
        for place in self.plan['places']:
            wanted = PLACE_BUILDINGS.get(place['kind'])
            if not wanted:
                continue
            px, py = place['position']
            options = [b for b in buildings if id(b) not in taken and b['kind'] in wanted]
            best = min(options, key=lambda b: math.hypot(b['x'] - px, b['y'] - py) + wanted.index(b['kind']) * 40)
            taken.add(id(best))
            best['place'] = dict(kind=place['kind'], name=place['name'])
            fx, fy = best['front']
            reach = best['size'][1] / 2 + 1.5
            place['position'] = [round(best['x'] + fx * reach, 1), round(best['y'] + fy * reach, 1)]
            place['building'] = best['kit']

    def sewers(self):
        # Las alcantarillas quedan en la acera más cercana; la tapa la dibuja Unity.
        for place in self.plan['places']:
            if place['kind'] != 'alcantarilla':
                continue
            px, py = place['position']
            best = None
            for road in self.roads:
                k = self.kinds[road['kind']]
                if not k['sidewalk']:
                    continue
                off = k['width'] / 2 + k['sidewalk'] / 2
                for x, y, ux, uy in self.sides[road['id']]:
                    dist = math.hypot(x - px, y - py)
                    if best is None or dist < best[0]:
                        best = (dist, x + uy * off, y - ux * off, heading(ux, uy))
            _, x, y, yaw = best
            self.add('Sewer', x, y, yaw, name=place['name'])
            place['position'] = [round(x, 1), round(y, 1)]

    # --- calles ---
    def near_crossing(self, x, y, distance):
        return any(abs(i['x'] - x) < distance and abs(i['y'] - y) < distance and math.hypot(i['x'] - x, i['y'] - y) < distance
                   for i in self.plan['intersections'])

    def index_solids(self):
        # Rejilla de fachadas (rectángulos girados) y de muebles ya puestos, para que un poste no atraviese nada.
        self.walls, self.props = {}, {}
        for o in self.objects:
            if 'size' in o and not o['kit'].startswith('Lot'):
                reach = math.hypot(o['size'][0], o['size'][1]) / 2
                for gx in range(int((o['x'] - reach) // 40), int((o['x'] + reach) // 40) + 1):
                    for gy in range(int((o['y'] - reach) // 40), int((o['y'] + reach) // 40) + 1):
                        self.walls.setdefault((gx, gy), []).append(o)
            elif o['kit'] not in ('Lamp', 'Signal', 'Sewer') and not o['kit'].startswith('Tree'):
                self.props.setdefault((int(o['x'] // 10), int(o['y'] // 10)), []).append((o['x'], o['y']))

    def blocked(self, x, y, margin=.5):
        for b in self.walls.get((int(x // 40), int(y // 40)), ()):
            yaw = math.radians(b['yaw'])
            lx = (x - b['x']) * math.cos(yaw) - (y - b['y']) * math.sin(yaw)
            ly = (x - b['x']) * math.sin(yaw) + (y - b['y']) * math.cos(yaw)
            if abs(lx) < b['size'][0] / 2 + margin and abs(ly) < b['size'][1] / 2 + margin:
                return True
        cx, cy = int(x // 10), int(y // 10)
        return any(math.hypot(px - x, py - y) < 1.5
                   for gx in (cx - 1, cx, cx + 1) for gy in (cy - 1, cy, cy + 1) for px, py in self.props.get((gx, gy), ()))

    def street_furniture(self):
        self.index_solids()
        for road in self.roads:
            k = self.kinds[road['kind']]
            line = self.sides[road['id']]
            for x, y, ux, uy in line[5::17]:  # un farol cada 34 m por lado
                if self.near_crossing(x, y, 16) or self.river_distance(x, y) < 32:
                    continue
                for s in (1, -1):
                    rx, ry = uy * s, -ux * s
                    # Poste junto al bordillo (0,7 m dentro de la acera, o 1,5 m del borde si no hay acera) y el brazo,
                    # que es el frente del kit, colgando sobre la calzada. El poste está 1,1 m detrás del centro del kit.
                    pole = k['width'] / 2 + (.7 if k['sidewalk'] else 1.5)
                    cx, cy = x + rx * (pole - 1.1), y + ry * (pole - 1.1)
                    if self.on_asphalt(x + rx * pole, y + ry * pole) or self.blocked(x + rx * pole, y + ry * pole):
                        continue  # caería en otra calzada, en una fachada o sobre un mueble: ese farol no se pone
                    self.add('Lamp', cx, cy, heading(-rx, -ry), z=STREET_Z if k['sidewalk'] else 0.0)
        # Segunda pasada, con todos los postes ya puestos: los árboles de acera los esquivan.
        poles = [(o['x'], o['y']) for o in self.objects if o['kit'] in ('Lamp', 'Signal')]
        for road in self.roads:
            k = self.kinds[road['kind']]
            line = self.sides[road['id']]
            if road['kind'] in ('avenue', 'boulevard'):
                for x, y, ux, uy in line[9::9]:  # árboles de acera cada 18 m
                    if self.near_crossing(x, y, 18) or self.river_distance(x, y) < 32:
                        continue
                    for s in (1, -1):
                        rx, ry = uy * s, -ux * s
                        off = k['width'] / 2 + max(1.0, k['sidewalk'] * .25)  # junto al bordillo: el centro de la acera es de los peatones
                        tx, ty = x + rx * off, y + ry * off
                        if any(abs(px - tx) < 4.5 and abs(py - ty) < 4.5 and math.hypot(px - tx, py - ty) < 4.5 for px, py in poles):
                            continue  # un árbol no puede crecer pegado a un poste
                        self.add(self.rng.choice(STREET_TREES), x + rx * off, y + ry * off, round(self.rng.uniform(0, 360), 1), street=True)

    # --- detalle de calle (ciudad 3.0, fase A) ---
    # Cada objeto se prueba como rectángulo girado contra la calzada, las fachadas y lo ya colocado;
    # si no cabe se corre unos metros o no se pone. Nada queda encima de otra cosa.
    def in_wall(self, x, y, margin):
        for b in self.walls.get((int(x // 40), int(y // 40)), ()):
            yaw = math.radians(b['yaw'])
            lx = (x - b['x']) * math.cos(yaw) - (y - b['y']) * math.sin(yaw)
            ly = (x - b['x']) * math.sin(yaw) + (y - b['y']) * math.cos(yaw)
            if abs(lx) < b['size'][0] / 2 + margin and abs(ly) < b['size'][1] / 2 + margin:
                return True
        return False

    def index_walkways(self, life):
        # Tramos de la red peatonal (veredas y cruces) en una rejilla de 10 m.
        nodes, edges = life['nodes'], life['edges']
        self.walkways = {}
        for i in range(0, len(edges), 4):
            a = (nodes[2 * edges[i]], nodes[2 * edges[i] + 1])
            b = (nodes[2 * edges[i + 1]], nodes[2 * edges[i + 1] + 1])
            for gx in range(int(min(a[0], b[0]) // 10), int(max(a[0], b[0]) // 10) + 1):
                for gy in range(int(min(a[1], b[1]) // 10), int(max(a[1], b[1]) // 10) + 1):
                    self.walkways.setdefault((gx, gy), []).append((a, b))

    def crosses_walkway(self, cx, cy, yaw, w, d):
        # Los peatones caminan hasta 0,6 m a cada lado de su línea y ocupan otros 0,2 m: esa franja queda libre.
        fx, fy = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        ux, uy = fy, -fx
        seen = set()
        reach = math.hypot(w, d) / 2 + 1
        for gx in range(int((cx - reach) // 10), int((cx + reach) // 10) + 1):
            for gy in range(int((cy - reach) // 10), int((cy + reach) // 10) + 1):
                for a, b in self.walkways.get((gx, gy), ()):
                    if (a, b) in seen:
                        continue
                    seen.add((a, b))
                    local = [((x - cx) * ux + (y - cy) * uy, (x - cx) * fx + (y - cy) * fy) for x, y in (a, b)]
                    if segment_box(local[0], local[1], w / 2, d / 2) < WALK_BAND:
                        return True
        return False

    def mark(self, x, y, r):
        self.spots.setdefault((int(x // 8), int(y // 8)), []).append((x, y, r))

    def mark_rect(self, cx, cy, yaw, w, d):
        # Un rectángulo se guarda como una fila de círculos a lo largo de su lado mayor.
        fx, fy = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        ax, ay, length, thick = (fy, -fx, w, d) if w >= d else (fx, fy, d, w)
        count = max(1, int(math.ceil(length / max(thick, .5))))
        for i in range(count):
            t = -length / 2 + (i + .5) * length / count
            self.mark(cx + ax * t, cy + ay * t, math.hypot(length / count, thick) / 2)

    def room(self, cx, cy, yaw, w, d, surface, gap=.3):
        # surface: 'sidewalk' (fuera del asfalto), 'road' (todo sobre el asfalto) o 'ground' (lejos del asfalto).
        fx, fy = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        ux, uy = fy, -fx
        for a in (-w / 2, 0, w / 2):
            for b in (-d / 2, 0, d / 2):
                x, y = cx + ux * a + fx * b, cy + uy * a + fy * b
                if surface == 'road' and not self.on_asphalt(x, y, .05):
                    return False
                if surface == 'sidewalk' and self.on_asphalt(x, y, .1):
                    return False
                if surface == 'ground' and (self.on_asphalt(x, y, 1.0) or self.on_paved(x, y)):
                    return False
                if self.in_wall(x, y, gap):
                    return False
        reach = math.hypot(w, d) / 2 + 4
        for gx in range(int((cx - reach) // 8), int((cx + reach) // 8) + 1):
            for gy in range(int((cy - reach) // 8), int((cy + reach) // 8) + 1):
                for px, py, pr in self.spots.get((gx, gy), ()):
                    a = (px - cx) * ux + (py - cy) * uy
                    b = (px - cx) * fx + (py - cy) * fy
                    if math.hypot(a - max(-w / 2, min(w / 2, a)), b - max(-d / 2, min(d / 2, b))) < pr + gap:
                        return False
        return True

    def put(self, kit, cx, cy, yaw, surface, z, gap=.3, **extra):
        w, d = self.sizes[kit]
        if not self.room(cx, cy, yaw, w, d, surface, gap):
            return None
        if self.near_point(self.doors, cx, cy, 2.5):
            return None  # la entrada de cada local y del escondite queda despejada
        gw, gd = GROUND.get(kit, (w, d))  # lo que toca el suelo: un poste, no la placa que va sobre las cabezas
        if self.crosses_walkway(cx, cy, yaw, gw, gd):
            return None
        self.mark_rect(cx, cy, yaw, w, d)
        return self.add(kit, cx, cy, yaw, z=z, **extra)

    def in_block(self, cx, cy, yaw, w, d):
        # Todo el rectángulo dentro de una misma cuadra: así no pisa vereda ni calzada.
        fx, fy = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        rows, cols = self.rect(cx, cy, (fy, -fx), (fx, fy), w, d)
        size = self.labels.shape[0]
        if rows.min() < 0 or cols.min() < 0 or rows.max() >= size or cols.max() >= size:
            return False
        cells = self.labels[rows, cols]
        return bool(cells[0] and (cells == cells[0]).all())

    def near_point(self, points, x, y, distance):
        return any(abs(px - x) < distance and abs(py - y) < distance and math.hypot(px - x, py - y) < distance for px, py in points)

    def zone_beside(self, road, x, y, rx, ry):
        k = self.kinds[road['kind']]
        label = self.label_at(x + rx * (k['width'] / 2 + k['sidewalk'] + 4), y + ry * (k['width'] / 2 + k['sidewalk'] + 4))
        return self.plan['blocks'][label - 1]['zone'] if label else None

    def walk(self, road, s, first, every, tries, attempt, crossing=20):
        # Recorre un lado de la vía cada «every» muestras y prueba hasta «tries» posiciones seguidas en cada punto.
        line = self.sides[road['id']]
        for i in range(first, len(line), every):
            for j in range(i, min(i + tries * 2, len(line)), 2):
                x, y, ux, uy = line[j]
                if self.near_crossing(x, y, crossing) or self.river_distance(x, y) < 40:
                    continue
                if attempt(x, y, ux, uy, uy * s, -ux * s):
                    break

    def corner_signs(self, controls, kit_for):
        # Señal al costado derecho de cada acceso a los cruces con PARE o con rotonda, mirando a los autos que llegan.
        roads_by_id = {r['id']: r for r in self.plan['roads']}
        placed = 0
        for node in (n for n in self.plan['intersections'] if n['control'] in controls):
            widest = max(self.kinds[roads_by_id[r]['kind']]['width'] for r in node['roads'])
            for rid in node['roads']:
                road = roads_by_id[rid]
                kit = kit_for(road)
                if kit is None:
                    continue
                k = self.kinds[road['kind']]
                ux, uy = direction(road, node['x'], node['y'])
                for s in (1, -1):
                    ax, ay = node['x'] + s * ux * (widest / 2 + 3.5), node['y'] + s * uy * (widest / 2 + 3.5)
                    if not on_road(road, ax, ay, k['width'] / 2):
                        continue
                    dx, dy = -s * ux, -s * uy
                    rx, ry = dy, -dx
                    yaw = heading(-dx, -dy)
                    for back in (0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12):
                        # A 0,7 m del bordillo: la placa (hasta 0,9 m de ancho) no asoma sobre la calzada.
                        px, py = ax + rx * (k['width'] / 2 + .7) - dx * back, ay + ry * (k['width'] / 2 + .7) - dy * back
                        if self.put(kit, px, py, yaw, 'sidewalk', STREET_Z if k['sidewalk'] else 0.0):
                            placed += 1
                            break
        return placed

    def settle_shopfronts(self):
        # Bancas, basureros, maceteros y mesas frente a las fachadas: si pisan la calzada o la franja de los peatones
        # se acercan a la fachada de a 0,5 m; si no hay lugar, no se ponen. Quedan a la altura de lo que pisan.
        kept, moved, dropped = [], 0, 0
        for o in self.objects:
            if o['kit'] not in SHOPFRONT:
                kept.append(o)
                continue
            w, d = self.sizes[o['kit']]
            fx, fy = math.sin(math.radians(o['yaw'])), math.cos(math.radians(o['yaw']))
            back = o.pop('facade')  # dirección hacia la fachada de su edificio
            for step in (0, .5, 1.0, 1.5, 2.0):
                x, y = o['x'] + back[0] * step, o['y'] + back[1] * step
                corners = [(x + fy * a + fx * b, y - fx * a + fy * b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2)]
                if any(self.on_asphalt(px, py, .1) or self.in_wall(px, py, .2) for px, py in corners + [(x, y)]):
                    continue
                if self.crosses_walkway(x, y, o['yaw'], w, d):
                    continue
                moved += step > 0
                o['x'], o['y'] = round(x, 2), round(y, 2)
                o['z'] = STREET_Z if self.on_paved(x, y, 0) else 0.0
                kept.append(o)
                break
            else:
                dropped += 1
        self.objects = kept
        return moved, dropped

    def street_details(self):
        self.sizes = {p['id']: (p['width'], p['depth']) for p in self.kit_pieces}
        self.sizes.update({car: CAR_SIZE for car in CARS})
        moved, dropped = self.settle_shopfronts()
        self.spots = {}
        for o in self.objects:
            if 'size' in o:
                continue
            if o['kit'] in ('Lamp', 'Signal'):
                yaw = math.radians(o['yaw'])
                self.mark(o['x'] - math.sin(yaw) * 1.1, o['y'] - math.cos(yaw) * 1.1, .35)  # el poste, no el brazo
            elif o['kit'].startswith('Tree'):
                self.mark(o['x'], o['y'], .8)
            elif o['kit'] in self.sizes:
                self.mark_rect(o['x'], o['y'], o['yaw'], *self.sizes[o['kit']])
        crossings = [(c['x'], c['y']) for c in self.plan['crosswalks']]
        doors = self.doors = [tuple(p['position']) for p in self.plan['places'] if 'position' in p]
        for lot in (o for o in self.objects if o['kit'] == 'Lot'):
            yaw = math.radians(lot['yaw'])
            doors.append((lot['x'] + math.sin(yaw) * lot['size'][1] / 2, lot['y'] + math.cos(yaw) * lot['size'][1] / 2))
        no_parking = []
        counts = {}
        # Carteles también en las avenidas que cruzan la zona industrial y las afueras.
        self.billboard_roads = {r['id'] for r in self.roads if r['kind'] in ('avenue', 'boulevard')
                                and any(self.label_at(x + uy * 20, y - ux * 20) and self.plan['blocks'][self.label_at(x + uy * 20, y - ux * 20) - 1]['zone'] in ('industrial', 'afueras')
                                        for x, y, ux, uy in self.sides[r['id']][::25])}

        def count(obj):
            if obj is not None:
                counts[obj['kit']] = counts.get(obj['kit'], 0) + 1
            return obj is not None

        # Bolardos frente a los locales que se pueden robar y bicicleteros cerca de los comercios.
        roads_by_id = {r['id']: r for r in self.roads}
        for b in (o for o in self.objects if 'place' in o and o.get('road') in roads_by_id):
            road = roads_by_id[b['road']]
            k = self.kinds[road['kind']]
            if not k['sidewalk']:
                continue
            fx, fy = b['front']  # hacia la calle
            dx, dy = b['x'] + fx * (b['size'][1] / 2 + 1), b['y'] + fy * (b['size'][1] / 2 + 1)
            x, y, ux, uy = min(self.sides[road['id']], key=lambda q: math.hypot(q[0] - dx, q[1] - dy))
            curb, yaw, kind = k['width'] / 2, heading(fx, fy), b['place']['kind']

            def spot(c, along):
                return x - fx * (curb + c) + ux * along, y - fy * (curb + c) + uy * along
            if kind in ('banco', 'joyeria', 'supermercado', 'comisaria'):
                for side in (-1, 1):
                    count(self.put('BollardRow', *spot(.5, side * 4.6), yaw, 'sidewalk', STREET_Z))
            if kind in ('comida', 'ropa', 'minimarket', 'supermercado'):
                for side in (1, -1):
                    if count(self.put('BikeRack', *spot(.3 + self.sizes['BikeRack'][1] / 2, side * 8.5), yaw, 'sidewalk', STREET_Z)):
                        break
        street_signs = ('street', 'avenue', 'boulevard')
        counts['StopSign'] = self.corner_signs(('stop',), lambda road: 'StopSign' if road['kind'] in street_signs else None)
        counts['YieldSign'] = self.corner_signs(('rotonda',), lambda road: None if road['kind'] == 'roundabout' else 'YieldSign')

        for road in self.roads:
            k = self.kinds[road['kind']]
            main = road['kind'] in ('avenue', 'boulevard')
            for s in (1, -1):
                odd = s < 0
                if main:
                    # Paradas de bus al fondo de la vereda (los peatones pasan por delante) cada ~300 m, alternadas.
                    def bus(x, y, ux, uy, rx, ry):
                        if self.near_point(doors, x, y, 15):
                            return False
                        c = k['width'] / 2 + k['sidewalk'] - .1 - self.sizes['BusStop'][1] / 2
                        obj = self.put('BusStop', x + rx * c, y + ry * c, heading(-rx, -ry), 'sidewalk', STREET_Z)
                        if obj:
                            no_parking.append((obj['x'], obj['y'], 14))
                        return count(obj)
                    self.walk(road, s, 105 if odd else 30, 175, 8, bus, crossing=30)

                # Kioscos y carteles van justo detrás de la vereda, solo donde el lote está libre.
                def behind(kit, gap_back):
                    def attempt(x, y, ux, uy, rx, ry):
                        w, d = self.sizes[kit]
                        c = k['width'] / 2 + k['sidewalk'] + gap_back + d / 2
                        cx, cy = x + rx * c, y + ry * c
                        label = self.label_at(cx, cy)
                        if not label or self.near_point(doors, x, y, 12) or self.plan['blocks'][label - 1]['zone'] not in KIOSK_ZONES:
                            return False
                        n = (-rx, -ry)
                        if not self.fits(label, cx, cy, (ux, uy), (rx, ry), w + 1, d + 1):
                            return False
                        obj = self.put(kit, cx, cy, heading(*n), 'ground', 0.0, gap=.5)
                        if obj:
                            self.occupy(cx, cy, (ux, uy), (rx, ry), w, d, 1, 1)
                        return count(obj)
                    return attempt
                if main:
                    self.walk(road, s, 130 if odd else 50, 90, 10, behind('Kiosk', .2), crossing=25)
                if road['kind'] == 'ring' or (main and road['id'] in self.billboard_roads):
                    # Carteles dentro de la cuadra (nunca sobre una vereda), a 3 m o más de cualquier fachada.
                    def board(x, y, ux, uy, rx, ry):
                        kit = self.rng.choice(BILLBOARDS)
                        w, d = self.sizes[kit]
                        c = k['width'] / 2 + k['sidewalk'] + 2.5 + d / 2
                        cx, cy = x + rx * c, y + ry * c
                        label = self.label_at(cx, cy)
                        if not label or self.plan['blocks'][label - 1]['zone'] not in ('comercial', 'industrial', 'afueras'):
                            return False
                        rows, cols = self.rect(cx, cy, (ux, uy), (rx, ry), w, d)
                        size = self.labels.shape[0]
                        if rows.min() < 0 or cols.min() < 0 or rows.max() >= size or cols.max() >= size or not (self.labels[rows, cols] == label).all():
                            return False
                        obj = self.put(kit, cx, cy, heading(-rx, -ry), 'ground', 0.0, gap=3.0)
                        if obj:
                            self.occupy(cx, cy, (ux, uy), (rx, ry), w, d, 1, 1)
                        return count(obj)
                    self.walk(road, s, 75 if odd else 20, 90, 8, board, crossing=40)

                # Velocidad máxima: mira a los autos que circulan por ese lado.
                limit = 'SpeedSign_40' if road['kind'] == 'street' else 'SpeedSign_60'
                def speed(x, y, ux, uy, rx, ry):
                    c = k['width'] / 2 + (.6 if k['sidewalk'] else 1.5)
                    yaw = heading(-ux, -uy) if s > 0 else heading(ux, uy)
                    return count(self.put(limit, x + rx * c, y + ry * c, yaw, 'sidewalk' if k['sidewalk'] else 'ground',
                                          STREET_Z if k['sidewalk'] else 0.0))
                self.walk(road, s, 20 if odd else 10, 150, 4, speed, crossing=22)
                if not k['sidewalk']:
                    continue

                # Hidrantes junto al bordillo cada ~90 m; nadie estaciona delante.
                def hydrant(x, y, ux, uy, rx, ry):
                    c = k['width'] / 2 + .45
                    obj = self.put('Hydrant', x + rx * c, y + ry * c, heading(-rx, -ry), 'sidewalk', STREET_Z)
                    if obj:
                        no_parking.append((obj['x'], obj['y'], 3.5))
                    return count(obj)
                self.walk(road, s, 35 if odd else 12, 60, 3, hydrant, crossing=10)

                def mailbox(x, y, ux, uy, rx, ry):
                    if self.zone_beside(road, x, y, rx, ry) not in ('comercial', 'financiero', 'residencial'):
                        return False
                    c = k['width'] / 2 + .5
                    return count(self.put('Mailbox', x + rx * c, y + ry * c, heading(rx, ry), 'sidewalk', STREET_Z))
                self.walk(road, s, 120 if odd else 60, 125, 3, mailbox, crossing=14)

        # Contenedores de basura: en el terreno del edificio, al costado y detrás de la línea de la fachada,
        # nunca en la calzada ni en la vereda. Los usan departamentos, galpones, torres y algunos comercios.
        for b in [o for o in self.objects if o.get('kind') in DUMPSTER_SHARE and 'place' not in o]:
            if self.rng.random() > DUMPSTER_SHARE[b['kind']]:
                continue
            fx, fy = b['front']
            ux, uy = fy, -fx
            w, d = b['size'][0], b['size'][1]
            options = [(side, turn) for side in (1, -1) for turn in (0, 90)]
            self.rng.shuffle(options)
            for side, turn in options:
                across = self.sizes['Dumpster'][0 if turn == 0 else 1]  # lo que ocupa hacia el costado
                lateral = w / 2 + .4 + across / 2
                cx, cy = b['x'] + ux * side * lateral + fx * (d / 2 - 2.0), b['y'] + uy * side * lateral + fy * (d / 2 - 2.0)
                yaw = (b['yaw'] + turn * side) % 360
                if self.in_block(cx, cy, yaw, *self.sizes['Dumpster']) and count(self.put('Dumpster', cx, cy, yaw, 'ground', 0.0)):
                    break

        # Autos estacionados al final: llenan la franja libre de las calles, mirando en el sentido de su carril.
        for road in (r for r in self.roads if r['kind'] == 'street'):
            k = self.kinds[road['kind']]
            line = self.sides[road['id']]
            for s in (1, -1):
                i = self.rng.randrange(3)
                while i < len(line):
                    x, y, ux, uy = line[i]
                    rx, ry = uy * s, -ux * s
                    i += 3
                    if self.rng.random() > PARKED_SHARE or self.zone_beside(road, x, y, rx, ry) not in PARKING_ZONES:
                        continue
                    if (self.near_crossing(x, y, 18) or self.river_distance(x, y) < 40 or self.near_point(crossings, x, y, 8)
                            or self.near_point(doors, x, y, 7)):
                        continue
                    if any(math.hypot(px - x, py - y) < r for px, py, r in no_parking if abs(px - x) < r and abs(py - y) < r):
                        continue
                    c = k['width'] / 2 - 1.0
                    car = self.rng.choice(PARKED_CARS)
                    yaw = heading(ux, uy) if s > 0 else heading(-ux, -uy)
                    if count(self.put(car, x + rx * c, y + ry * c, yaw, 'road', ROAD_Z, gap=.25, parked=True)):
                        i += 1  # deja un hueco entre autos
        counts['fachadas corridas'], counts['fachadas quitadas'] = moved, dropped
        return counts

    def traffic_lights(self, signals):
        # Un semáforo en la esquina derecha de cada acceso al cruce. El modelo lleva la cabeza 2 m por delante del poste
        # y las luces mirando al frente: el frente apunta a los autos que llegan para que vean el color.
        roads_by_id = {r['id']: r for r in self.plan['roads']}
        nodes = [n for n in self.plan['intersections'] if n['control'] == 'semaforo']
        for index, (node, signal) in enumerate(zip(nodes, signals)):
            widest = max(self.kinds[roads_by_id[r]['kind']]['width'] for r in node['roads'])
            for rid in node['roads']:
                road = roads_by_id[rid]
                if road['kind'] not in ('boulevard', 'avenue', 'street'):
                    continue
                k = self.kinds[road['kind']]
                ux, uy = direction(road, node['x'], node['y'])
                axis = next(i for i, (ax, ay) in enumerate(signal['axes']) if abs(ax * ux + ay * uy) > .8)
                for s in (1, -1):
                    ax, ay = node['x'] + s * ux * (widest / 2 + 2.5), node['y'] + s * uy * (widest / 2 + 2.5)
                    if not on_road(road, ax, ay, k['width'] / 2):
                        continue
                    dx, dy = -s * ux, -s * uy  # sentido de los autos que llegan
                    rx, ry = dy, -dx           # su derecha
                    off = k['width'] / 2 + 1.6
                    # El poste va en la vereda de la esquina derecha. Si ahí cae en otra calzada (curva, diagonal, rotonda)
                    # retrocede por la vereda; si tampoco cabe, va a la esquina izquierda. Así cada acceso conserva su luz.
                    spots = [(side, back, e) for side in (1, -1) for back in (0, 2, 4, 6, 8) for e in (0, .5, 1, 1.5, 2)]
                    pole = next(((ax + side * rx * (off + e) - dx * back, ay + side * ry * (off + e) - dy * back)
                                 for side, back, e in spots
                                 if not self.on_asphalt(ax + side * rx * (off + e) - dx * back, ay + side * ry * (off + e) - dy * back)), None)
                    if pole is None:
                        continue  # acceso sin vereda posible: lo cubren las otras luces del mismo eje
                    self.add('Signal', pole[0] - dx * 1.1, pole[1] - dy * 1.1, heading(-dx, -dy), signal=index, axis=axis,
                             z=STREET_Z if k['sidewalk'] else 0.0)

    # --- verde y mobiliario ---
    def shopfronts(self):
        for b in [o for o in self.objects if o.get('kind') in ('shop', 'tower')]:
            fx, fy = b['front']
            rx, ry = fy, -fx
            front = b['size'][1] / 2 + 1.6
            bx, by = b['x'] + fx * front, b['y'] + fy * front
            half = b['size'][0] / 2
            back = [-fx, -fy]  # settle_shopfronts los acerca a la fachada si estorban
            if b.get('place', {}).get('kind') == 'comida':
                self.add('CafeSet', bx + fx * 1.2 + rx * (half - 3), by + fy * 1.2 + ry * (half - 3), b['yaw'], facade=back)
                self.add('CafeSet', bx + fx * 1.2 - rx * (half - 3), by + fy * 1.2 - ry * (half - 3), b['yaw'], facade=back)
            elif 'place' in b:
                continue  # la puerta de un local queda despejada
            elif self.rng.random() < .45:
                # La banca da la espalda a la fachada y mira la calle.
                self.add('Bench', bx + rx * (half - 2), by + ry * (half - 2), b['yaw'], facade=back)
                self.add('Bin', bx - rx * (half - 1.5), by - ry * (half - 1.5), b['yaw'], facade=back)
            elif self.rng.random() < .3:
                self.add('Planter', bx + rx * (half - 3), by + ry * (half - 3), b['yaw'], facade=back)

    def greenery(self):
        for index, block in enumerate(self.plan['blocks'], start=1):
            density = {'parque': 260, 'residencial': 700, 'afueras': 500, 'financiero': 2500, 'comercial': 2500, 'industrial': 3000}.get(block['zone'])
            if density is None:
                continue
            x0, y0, x1, y1 = block['bounds']
            for _ in range(int(block['area_m2'] / density)):
                x, y = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
                if self.fits(index, x, y, (1, 0), (0, 1), 5, 5):
                    self.occupy(x, y, (1, 0), (0, 1), 5, 5)
                    self.add(self.rng.choice(TREES), x, y, round(self.rng.uniform(0, 360), 1))

    def park(self, park):
        cx, cy = (park[0] + park[2]) / 2, (park[1] + park[3]) / 2
        for kit, x, y, w, d, yaw in (('Playground', cx - 50, cy - 40, 12, 12, 0.0), ('BasketballCourt', cx + 55, cy - 30, 28, 15, 90.0)):
            self.occupy(x, y, (1, 0), (0, 1), w + 4, d + 4)
            self.add(kit, x, y, yaw)


def segment_box(a, b, hw, hd):
    # Distancia entre un tramo y un rectángulo centrado en el origen (semiancho hw, semifondo hd).
    def box(x, y):
        return math.hypot(max(abs(x) - hw, 0), max(abs(y) - hd, 0))

    def seg(px, py):
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        t = 0 if l2 < 1e-12 else max(0, min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / l2))
        return math.hypot(a[0] + t * dx - px, a[1] + t * dy - py)
    # ¿El tramo cruza el rectángulo? (recorte de Liang-Barsky)
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    inside = True
    for p, q in ((-dx, a[0] + hw), (dx, hw - a[0]), (-dy, a[1] + hd), (dy, hd - a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                inside = False
                break
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            inside = False
            break
    if inside:
        return 0.0
    return min(box(*a), box(*b), *(seg(x, y) for x in (-hw, hw) for y in (-hd, hd)))


def direction(road, x, y):
    best = None
    for (ax, ay), (bx, by) in zip(road['points'], road['points'][1:]):
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length < 1e-6:
            continue
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (length * length)))
        dist = math.hypot(ax + t * dx - x, ay + t * dy - y)
        if best is None or dist < best[0]:
            best = (dist, dx / length, dy / length)
    return best[1], best[2]


def on_road(road, x, y, half_width):
    for (ax, ay), (bx, by) in zip(road['points'], road['points'][1:]):
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        if length2 < 1e-9:
            continue
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / length2))
        if math.hypot(ax + t * dx - x, ay + t * dy - y) <= half_width:
            return True
    return False


def place_all(plan, labels, kit, half, cell, river_distance, signals, life):
    placer = Placer(plan, labels, kit, half, cell, river_distance)
    placer.index_walkways(life)
    placer.park(plan['park'])
    placer.lots()
    placer.buildings()
    placer.assign_places()
    placer.sewers()
    placer.shopfronts()
    placer.traffic_lights(signals)  # primero los postes: los árboles los esquivan
    placer.street_furniture()
    print('detalle de calle', placer.street_details())
    placer.greenery()
    placer.clear_poles()
    return placer.objects, placer.occupied
