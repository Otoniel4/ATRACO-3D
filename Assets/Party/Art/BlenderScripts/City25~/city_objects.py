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
        self.rng = random.Random(25)
        self.roads = sorted((r for r in plan['roads'] if r['kind'] in ROAD_ORDER), key=lambda r: ROAD_ORDER.index(r['kind']))
        self.sides = {r['id']: samples(r['points']) for r in self.roads}

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

    def street_furniture(self):
        for road in self.roads:
            k = self.kinds[road['kind']]
            line = self.sides[road['id']]
            for x, y, ux, uy in line[5::17]:  # un farol cada 34 m por lado
                if self.near_crossing(x, y, 16) or self.river_distance(x, y) < 32:
                    continue
                for s in (1, -1):
                    rx, ry = uy * s, -ux * s
                    off = k['width'] / 2 + (1.9 if k['sidewalk'] else 3.2)
                    # El brazo (frente del kit) cuelga sobre la calzada.
                    self.add('Lamp', x + rx * off, y + ry * off, heading(-rx, -ry))
            if road['kind'] in ('avenue', 'boulevard'):
                for x, y, ux, uy in line[9::9]:  # árboles de acera cada 18 m
                    if self.near_crossing(x, y, 18) or self.river_distance(x, y) < 32:
                        continue
                    for s in (1, -1):
                        rx, ry = uy * s, -ux * s
                        off = k['width'] / 2 + max(1.0, k['sidewalk'] * .25)  # junto al bordillo: el centro de la acera es de los peatones
                        self.add(self.rng.choice(STREET_TREES), x + rx * off, y + ry * off, round(self.rng.uniform(0, 360), 1), street=True)

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
                    px, py = ax + rx * off - dx * 1.1, ay + ry * off - dy * 1.1  # el poste queda en la esquina
                    self.add('Signal', px, py, heading(-dx, -dy), signal=index, axis=axis)

    # --- verde y mobiliario ---
    def shopfronts(self):
        for b in [o for o in self.objects if o.get('kind') in ('shop', 'tower')]:
            fx, fy = b['front']
            rx, ry = fy, -fx
            front = b['size'][1] / 2 + 1.6
            bx, by = b['x'] + fx * front, b['y'] + fy * front
            half = b['size'][0] / 2
            if b.get('place', {}).get('kind') == 'comida':
                self.add('CafeSet', bx + fx * 1.2 + rx * (half - 3), by + fy * 1.2 + ry * (half - 3), b['yaw'])
                self.add('CafeSet', bx + fx * 1.2 - rx * (half - 3), by + fy * 1.2 - ry * (half - 3), b['yaw'])
            elif 'place' in b:
                continue  # la puerta de un local queda despejada
            elif self.rng.random() < .45:
                self.add('Bench', bx + rx * (half - 2), by + ry * (half - 2), heading(-fx, -fy))
                self.add('Bin', bx - rx * (half - 1.5), by - ry * (half - 1.5), b['yaw'])
            elif self.rng.random() < .3:
                self.add('Planter', bx + rx * (half - 3), by + ry * (half - 3), b['yaw'])

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


def place_all(plan, labels, kit, half, cell, river_distance, signals):
    placer = Placer(plan, labels, kit, half, cell, river_distance)
    placer.park(plan['park'])
    placer.lots()
    placer.buildings()
    placer.assign_places()
    placer.sewers()
    placer.shopfronts()
    placer.street_furniture()
    placer.traffic_lights(signals)
    placer.greenery()
    return placer.objects, placer.occupied
