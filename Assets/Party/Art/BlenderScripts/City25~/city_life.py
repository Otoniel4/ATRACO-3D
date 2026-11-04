"""Datos de la ciudad viva: semáforos (ejes de cada cruce) y red peatonal (aceras, esquinas y pasos de cebra).

Red peatonal: el eje de cada acera se muestrea cada 2 m, se quitan los tramos que caen sobre la calzada de otra vía
(como hace el suelo) y quedan cadenas de nodos cada ~6 m. Las cadenas se unen en las esquinas y los pasos de cebra
unen las dos aceras de una misma vía. Un paso de cebra junto a un semáforo guarda el cruce y el eje de la vía que
atraviesa: el peatón solo cruza cuando ese eje está en rojo.
Formato pensado para JsonUtility de Unity: listas planas de números.
"""
import math

from city_objects import samples

SIGNAL_REACH = 8.0   # distancia máxima de un paso de cebra al cruce que lo controla, además del ancho de la vía
CORNER = 7.5         # extremos de aceras más cercanos que esto se unen (esquinas)
SNAP = 6.0           # distancia máxima de un extremo de paso de cebra a la acera


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


def build_walkways(plan, signals):
    kinds = plan['kinds']
    asphalt = Grid(40.0)
    for road in plan['roads']:
        half = kinds[road['kind']]['width'] / 2
        for a, b in zip(road['points'], road['points'][1:]):
            for t in (0, .25, .5, .75, 1):
                asphalt.add(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (road['id'], a, b, half))

    def on_asphalt(x, y, own):
        for rid, a, b, half in asphalt.near(x, y):
            if rid == own:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            l2 = dx * dx + dy * dy
            t = 0 if l2 < 1e-9 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / l2))
            if math.hypot(a[0] + t * dx - x, a[1] + t * dy - y) < half + .3:
                return True
        return False

    nodes, edges, ends = [], [], []
    index = Grid(12.0)

    def node(x, y):
        nodes.append((round(x, 2), round(y, 2)))
        index.add(x, y, len(nodes) - 1)
        return len(nodes) - 1

    for road in plan['roads']:
        k = kinds[road['kind']]
        if not k['sidewalk']:
            continue
        line = samples(road['points'], 2.0)
        for side in (1, -1):
            off = side * (k['width'] / 2 + k['sidewalk'] / 2)
            points = [(x - uy * off, y + ux * off) for x, y, ux, uy in line]
            keep = [not on_asphalt(x, y, road['id']) for x, y in points]
            run = []
            for p, ok in zip(points + [None], keep + [False]):
                if ok:
                    run.append(p)
                    continue
                if len(run) >= 2:
                    chain = run[::3] if (len(run) - 1) % 3 == 0 else run[::3] + [run[-1]]
                    ids = [node(*q) for q in chain]
                    edges.extend((a, b, -1, -1) for a, b in zip(ids, ids[1:]))
                    ends.extend((ids[0], ids[-1]))
                run = []
    # Esquinas: extremos de aceras que se tocan.
    end_set = set(ends)
    for e in ends:
        x, y = nodes[e]
        for other in index.near(x, y):
            if other > e and other in end_set and math.dist(nodes[other], (x, y)) < CORNER:
                edges.append((e, other, -1, -1))
    # Pasos de cebra: unen las dos aceras de la vía; los de un semáforo esperan a que su eje esté en rojo.
    crossings = 0
    for c in plan['crosswalks']:
        ux, uy = c['along']
        px, py = -uy, ux
        width = c['length']
        sides = []
        for s in (1, -1):
            ex, ey = c['x'] + px * s * (width / 2 + 1.2), c['y'] + py * s * (width / 2 + 1.2)
            best = min(((math.dist(nodes[n], (ex, ey)), n) for n in index.near(ex, ey)), default=None)
            if best and best[0] < SNAP:
                sides.append(best[1])
        if len(sides) == 2 and sides[0] != sides[1]:
            signal, axis = signal_for(signals, c['x'], c['y'], ux, uy, width + SIGNAL_REACH)
            edges.append((sides[0], sides[1], signal, axis) if signal >= 0 else (sides[0], sides[1], -2, -1))
            crossings += 1
    return nodes, edges, crossings


def build_life(plan):
    signals = build_signals(plan)
    nodes, edges, crossings = build_walkways(plan, signals)
    data = dict(
        signals=[dict(x=s['x'], y=s['y'], axes=[round(v, 4) for a in s['axes'] for v in a]) for s in signals],
        nodes=[v for n in nodes for v in n],
        edges=[v for e in edges for v in e],
    )
    stats = dict(semaforos=len(signals), nodos=len(nodes), tramos=len(edges), pasos=crossings,
                 pasos_con_semaforo=sum(1 for e in edges if e[2] >= 0))
    return data, signals, stats
