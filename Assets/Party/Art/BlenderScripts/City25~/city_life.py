"""Datos de la ciudad viva: semáforos (ejes de cada cruce) y red peatonal (aceras, esquinas y pasos de cebra).

Red peatonal: el eje de cada acera se muestrea cada 2 m. Cada tramo se comprueba a lo largo de su recorrido,
con margen para los dos sentidos de marcha y el ancho de la cápsula. Las esquinas no pueden recortar parcelas
ni invadir la calzada. Los extremos de los pasos de cebra se colocan sobre su eje y se enlazan por la acera.
Un paso controlado conserva el semáforo y el eje de la vía que atraviesa.
Formato pensado para JsonUtility de Unity: listas planas de números.
"""
import json
import math
from pathlib import Path

from city_objects import HIDEOUT_REAR, HIDEOUT_SIDE, HIDEOUT_YARD, samples, segment_box

SIGNAL_REACH = 8.0   # distancia máxima de un paso de cebra al cruce que lo controla, además del ancho de la vía
CORNER = 7.5         # extremos de aceras más cercanos que esto se unen (esquinas)
SNAP = 6.0           # distancia máxima de un extremo de paso de cebra a la acera
BODY_BAND = .59      # radio (.25), separación lateral (.28) y margen de discretización


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


class Grid:
    def __init__(self, cell):
        self.cell, self.items = cell, {}

    def add(self, x, y, item):
        self.items.setdefault((int(x // self.cell), int(y // self.cell)), []).append(item)

    def near(self, x, y):
        cx, cy = int(x // self.cell), int(y // self.cell)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                yield from self.items.get((cx + i, cy + j), ())

    def bounds(self, x0, y0, x1, y1, item):
        for i in range(int(x0 // self.cell), int(x1 // self.cell) + 1):
            for j in range(int(y0 // self.cell), int(y1 // self.cell) + 1):
                self.items.setdefault((i, j), []).append(item)

    def at(self, x, y):
        return self.items.get((int(x // self.cell), int(y // self.cell)), ())


class WalkableArea:
    """Bandas de acera, esquinas y parcelas para evaluar el tramo completo, incluido el ancho del cuerpo."""

    def __init__(self, plan, objects=()):
        self.roads, self.corners, self.parcels = Grid(36.), Grid(36.), Grid(36.)
        kinds = plan['kinds']
        widths = {r['id']: kinds[r['kind']] for r in plan['roads']}
        for road in plan['roads']:
            kind = widths[road['id']]
            half, sidewalk = kind['width'] / 2, kind['sidewalk']
            for a, b in zip(road['points'], road['points'][1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                length = math.hypot(dx, dy)
                if length < 1e-6:
                    continue
                reach = half + sidewalk + BODY_BAND
                self.roads.bounds(min(a[0], b[0]) - reach, min(a[1], b[1]) - reach,
                                  max(a[0], b[0]) + reach, max(a[1], b[1]) + reach,
                                  (a[0], a[1], dx / length, dy / length, length, half, sidewalk))
        for corner in plan['intersections']:
            styles = [widths[r] for r in corner['roads']]
            half = max(s['width'] for s in styles) / 2 + max(s['sidewalk'] for s in styles) + 1.
            x, y = corner['x'], corner['y']
            self.corners.bounds(x-half, y-half, x+half, y+half, (x, y, half))
        for obj in objects:
            if obj.get('kind') not in ('house', 'apartment', 'warehouse', 'tower', 'shop') or 'size' not in obj:
                continue
            x, y = obj['x'], obj['y']
            hw, hd = obj['size'][0] / 2, obj['size'][1] / 2
            yaw = math.radians(obj['yaw'])
            fx, fy = math.sin(yaw), math.cos(yaw)
            if obj.get('place', {}).get('kind') == 'escondite':
                # La parcela completa de la guarida es privada, aunque el portón esté abierto.
                hw += HIDEOUT_SIDE
                hd += (HIDEOUT_YARD + HIDEOUT_REAR) / 2
                x += fx * (HIDEOUT_YARD - HIDEOUT_REAR) / 2
                y += fy * (HIDEOUT_YARD - HIDEOUT_REAR) / 2
            reach = math.hypot(hw, hd) + BODY_BAND
            self.parcels.bounds(x-reach, y-reach, x+reach, y+reach, (x, y, fx, fy, hw, hd))

    def sidewalk(self, x, y):
        valid = False
        for ax, ay, ux, uy, length, half, sidewalk in self.roads.at(x, y):
            dx, dy = x-ax, y-ay
            along, lateral = dx*ux+dy*uy, abs(dx*uy-dy*ux)
            if -BODY_BAND <= along <= length + BODY_BAND and lateral < half + BODY_BAND:
                return False
            if 0 <= along <= length and half + BODY_BAND <= lateral <= half + sidewalk - BODY_BAND:
                valid = True
        if valid:
            return True
        return any(max(abs(x-cx), abs(y-cy)) <= half-BODY_BAND for cx, cy, half in self.corners.at(x, y))

    def segment(self, a, b, crossing=None):
        distance = math.dist(a, b)
        if distance < .015:
            return False
        steps = max(1, math.ceil(distance / .45))
        parcel_set = set()
        for i in range(steps + 1):
            t = i / steps
            x, y = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
            parcel_set.update(self.parcels.at(x, y))
            if self.sidewalk(x, y):
                continue
            if crossing is None:
                return False
            # Las marcas tienen 3 m de ancho a lo largo de la calle.
            dx, dy = x-crossing['x'], y-crossing['y']
            ux, uy = crossing['along']
            if abs(dx*ux+dy*uy) > 1.5 - BODY_BAND or abs(dx*uy-dy*ux) > crossing['length']/2 + BODY_BAND:
                return False
        for x, y, fx, fy, hw, hd in parcel_set:
            la = ((a[0]-x)*fy-(a[1]-y)*fx, (a[0]-x)*fx+(a[1]-y)*fy)
            lb = ((b[0]-x)*fy-(b[1]-y)*fx, (b[0]-x)*fx+(b[1]-y)*fy)
            if segment_box(la, lb, hw, hd) < BODY_BAND:
                return False
        return True


def build_signals(plan):
    roads = {r['id']: r for r in plan['roads']}
    signals = []
    for node in plan['intersections']:
        if node['control'] != 'semaforo':
            continue
        axes = []
        for rid in node['roads']:
            ux, uy = direction(roads[rid], node['x'], node['y'])
            if not any(abs(ux * ax + uy * ay) > .8 for ax, ay in axes):
                axes.append((ux, uy))
        signals.append(dict(x=node['x'], y=node['y'], axes=axes))
    return signals


def signal_for(signals, x, y, ux, uy, reach):
    # Cruce con semáforo más cercano y el eje paralelo a (ux, uy).
    best = None
    for i, s in enumerate(signals):
        d = math.hypot(s['x'] - x, s['y'] - y)
        if d < reach and (best is None or d < best[0]):
            axis = next((k for k, (ax, ay) in enumerate(s['axes']) if abs(ax * ux + ay * uy) > .8), None)
            if axis is not None:
                best = (d, i, axis)
    return (best[1], best[2]) if best else (-1, -1)


def build_walkways(plan, signals, objects=()):
    kinds = plan['kinds']
    roads = {r['id']: r for r in plan['roads']}
    area = WalkableArea(plan, objects)
    nodes, edges, ends = [], [], []
    index = Grid(12.0)
    edge_pairs = set()

    def node(x, y):
        nodes.append((round(x, 2), round(y, 2)))
        index.add(x, y, len(nodes) - 1)
        return len(nodes) - 1

    def connect(a, b, signal=-1, axis=-1, crossing=None):
        key = (min(a,b), max(a,b))
        if key in edge_pairs or not area.segment(nodes[a], nodes[b], crossing):
            return False
        edges.append((a,b,signal,axis))
        edge_pairs.add(key)
        return True

    for road in plan['roads']:
        k = kinds[road['kind']]
        if not k['sidewalk']:
            continue
        line = samples(road['points'], 2.0)
        for side in (1, -1):
            off = side * (k['width'] / 2 + k['sidewalk'] / 2)
            previous = None
            for x, y, ux, uy in line:
                p = (x - uy * off, y + ux * off)
                if not area.sidewalk(*p):
                    if previous is not None:
                        ends.append(previous)
                    previous = None
                    continue
                current = node(*p)
                if previous is None or not connect(previous, current):
                    if previous is not None:
                        ends.append(previous)
                    ends.append(current)
                previous = current
            if previous is not None:
                ends.append(previous)
    # Esquinas: extremos de aceras que se tocan.
    end_set = set(ends)
    for e in ends:
        x, y = nodes[e]
        for other in index.near(x, y):
            if other > e and other in end_set and math.dist(nodes[other], (x, y)) < CORNER:
                connect(e, other)
    # Pasos de cebra: unen las dos aceras de la vía; los de un semáforo esperan a que su eje esté en rojo.
    crossings = 0
    for c in plan['crosswalks']:
        ux, uy = c['along']
        px, py = -uy, ux
        width = c['length']
        sides = []
        sidewalk = kinds[roads[c['road']]['kind']]['sidewalk']
        if sidewalk <= 2*BODY_BAND:
            continue
        for s in (1, -1):
            p = (c['x'] + px*s*(width/2 + sidewalk/2), c['y'] + py*s*(width/2 + sidewalk/2))
            best = next((n for n in sorted(index.near(*p), key=lambda n: math.dist(nodes[n], p))
                         if .015 < math.dist(nodes[n], p) < SNAP and area.segment(nodes[n], p)), None)
            if best is not None:
                sides.append((p, best))
        if len(sides) == 2 and sides[0][1] != sides[1][1] and area.segment(sides[0][0], sides[1][0], c):
            a, b = (node(*p) for p, _ in sides)
            connect(sides[0][1], a)
            connect(sides[1][1], b)
            signal, axis = signal_for(signals, c['x'], c['y'], ux, uy, width + SIGNAL_REACH)
            if connect(a, b, signal if signal >= 0 else -2, axis, c):
                crossings += 1
    used = sorted({n for a, b, _, _ in edges for n in (a, b)})
    remap = {old: new for new, old in enumerate(used)}
    return [nodes[i] for i in used], [(remap[a], remap[b], s, ax) for a,b,s,ax in edges], crossings


def build_life(plan, objects=()):
    signals = build_signals(plan)
    nodes, edges, crossings = build_walkways(plan, signals, objects)
    data = dict(
        signals=[dict(x=s['x'], y=s['y'], axes=[round(v, 4) for a in s['axes'] for v in a]) for s in signals],
        nodes=[v for n in nodes for v in n],
        edges=[v for e in edges for v in e],
    )
    stats = dict(semaforos=len(signals), nodos=len(nodes), tramos=len(edges), pasos=crossings,
                 pasos_con_semaforo=sum(1 for e in edges if e[2] >= 0))
    return data, signals, stats


if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    plan = json.loads((folder/'city_plan.json').read_text(encoding='utf-8'))
    objects = json.loads((folder/'city_objects.json').read_text(encoding='utf-8'))['objects']
    life, _, stats = build_life(plan, objects)
    (folder/'city_life.json').write_text(json.dumps(life, separators=(',', ':')), encoding='utf-8')
    print(json.dumps(stats, ensure_ascii=False))
