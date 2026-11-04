"""Carriles de la ciudad para los autos: circulación por la derecha, la rotonda en un solo sentido (antihorario).

Cada vía se corta en los cruces. Cada tramo da un carril por sentido y por pista ("enlace"), recortado antes del cruce
donde está la línea de parada; el giro dentro del cruce lo dibuja Unity con una curva hasta el enlace siguiente.
Un enlace guarda qué controla su final: semáforo (con su eje), pare, rotonda o nada; y a qué enlaces puede seguir.
En los callejones sin salida el auto da la vuelta. Formato para JsonUtility: listas planas.
"""
import math

from city_life import direction

SPEED = {'street': 9.0, 'avenue': 12.5, 'boulevard': 13.5, 'ring': 15.0, 'roundabout': 7.0}  # m/s
CONTROL = {'semaforo': 1, 'stop': 2, 'rotonda': 3}
# Centro del carril desde el eje: en las calles queda a 2,5 m para dejar junto al bordillo la franja de autos estacionados.
LANE_CENTER = {'street': 2.5}
STEP = 5.0


def arc(points):
    out = [0.0]
    for a, b in zip(points, points[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def project(points, lengths, x, y):
    best = None
    for i, (a, b) in enumerate(zip(points, points[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        t = 0 if l2 < 1e-9 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / l2))
        d = math.hypot(a[0] + t * dx - x, a[1] + t * dy - y)
        if best is None or d < best[0]:
            best = (d, lengths[i] + t * math.sqrt(l2))
    return best[1]


def at(points, lengths, s):
    # Punto y dirección a la distancia s (con vuelta en vías cerradas).
    total = lengths[-1]
    s = s % total if s > total or s < 0 else s
    for i in range(len(points) - 1):
        if lengths[i + 1] >= s:
            a, b = points[i], points[i + 1]
            seg = lengths[i + 1] - lengths[i] or 1.0
            t = (s - lengths[i]) / seg
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / seg, (b[1] - a[1]) / seg)
    a, b = points[-2], points[-1]
    seg = math.dist(a, b) or 1.0
    return b, ((b[0] - a[0]) / seg, (b[1] - a[1]) / seg)


def build_traffic(plan, signals):
    kinds = plan['kinds']
    nodes = plan['intersections']
    roads = {r['id']: r for r in plan['roads']}
    signal_of = {}
    for index, n in enumerate(n for n in nodes if n['control'] == 'semaforo'):
        signal_of[(n['x'], n['y'])] = index
    widest = [max(kinds[roads[r]['kind']]['width'] for r in n['roads']) for n in nodes]
    links = []
    for road in plan['roads']:
        k = kinds[road['kind']]
        pts = [tuple(p) for p in road['points']]
        closed = len(pts) > 2 and math.dist(pts[0], pts[-1]) < .5
        lengths = arc(pts)
        total = lengths[-1]
        stops = sorted({(round(project(pts, lengths, n['x'], n['y']), 1), i) for i, n in enumerate(nodes) if road['id'] in n['roads']})
        marks = [(None, 0.0)] if not closed and (not stops or stops[0][0] > 1) else []
        marks += [(i, s) for s, i in stops]
        if not closed and (not stops or stops[-1][0] < total - 1):
            marks.append((None, total))
        spans = list(zip(marks, marks[1:]))
        if closed and len(marks) > 1:
            spans.append((marks[-1], (marks[0][0], marks[0][1] + total)))
        # La rotonda es de un solo sentido: antihorario según el área con signo del círculo.
        one_way = road['kind'] == 'roundabout'
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:]))
        directions = [1 if area > 0 else -1] if one_way else [1, -1]
        lanes = k['lanes']
        def clearance(n):
            # Línea de parada detrás del paso de cebra; en la rotonda el anillo sigue casi entero y las avenidas ceden al borde.
            if n is None:
                return 1.0
            if nodes[n]['control'] == 'rotonda':
                return 4.0 if one_way else kinds['roundabout']['width'] / 2 + 3.0
            return widest[n] / 2 + 5.5

        for segment, ((n0, s0), (n1, s1)) in enumerate(spans):
            a, b = s0 + clearance(n0), s1 - clearance(n1)
            if b - a < 3:
                continue
            count = max(2, int(math.ceil((b - a) / STEP)) + 1)
            line = [at(pts, lengths, a + (b - a) * i / (count - 1)) for i in range(count)]
            for d in directions:
                for lane in range(lanes):
                    if one_way:
                        off = (lane - (lanes - 1) / 2) * 3.4
                    else:
                        off = LANE_CENTER.get(road['kind'], (lane + .5) * k['width'] / 2 / lanes)
                    # Derecha del sentido de marcha: (uy, -ux) multiplicado por el sentido.
                    path = [(x + uy * d * off, y - ux * d * off) for (x, y), (ux, uy) in line]
                    start, end = (n0, n1) if d > 0 else (n1, n0)
                    if d < 0:
                        path.reverse()
                    control, signal, axis = 0, -1, -1
                    if end is not None:
                        control = CONTROL.get(nodes[end]['control'], 0)
                        if control == 1:
                            signal = signal_of[(nodes[end]['x'], nodes[end]['y'])]
                            ux, uy = direction(road, nodes[end]['x'], nodes[end]['y'])
                            axis = next(i for i, (ax, ay) in enumerate(signals[signal]['axes']) if abs(ax * ux + ay * uy) > .8)
                    links.append(dict(road=road['id'], segment=(road['id'], segment), dir=d, lane=lane, start=start, end=end,
                                      control=control, signal=signal, axis=axis, speed=SPEED[road['kind']],
                                      points=[round(v, 2) for p in path for v in p]))
    # Sucesores: enlaces que salen del cruce donde termina; sin dar la vuelta salvo en callejones sin salida.
    by_start = {}
    for i, l in enumerate(links):
        if l['start'] is not None:
            by_start.setdefault(l['start'], []).append(i)
    for l in links:
        if l['end'] is None:
            l['next'] = [i for i, o in enumerate(links) if o['segment'] == l['segment'] and o['dir'] != l['dir']]
            continue
        options = [i for i in by_start.get(l['end'], []) if not (links[i]['segment'] == l['segment'] and links[i]['dir'] != l['dir'])]
        l['next'] = options or by_start.get(l['end'], [])
    data = dict(links=[dict(points=l['points'], next=l['next'], control=l['control'], signal=l['signal'], axis=l['axis'], speed=l['speed'])
                       for l in links])
    stats = dict(enlaces=len(links), sin_salida=sum(1 for l in links if not l['next']),
                 con_semaforo=sum(1 for l in links if l['control'] == 1), callejones=sum(1 for l in links if l['end'] is None))
    return data, stats
