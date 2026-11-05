"""Audita los datos publicados y comprueba la geometría de esquina, parcela y cruce."""
import collections
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
ROOT = ART.parents[2]
CITY = ART / 'BlenderScripts' / 'City25~'
sys.path.insert(0, str(CITY))
from city_life import WalkableArea
from city_objects import HIDEOUT_REAR, HIDEOUT_SIDE, HIDEOUT_YARD, segment_box


def load(name):
    return json.loads((CITY / name).read_text(encoding='utf-8'))


def graph(data):
    nodes = list(zip(data['nodes'][::2], data['nodes'][1::2]))
    edges = list(zip(*(data['edges'][offset::4] for offset in range(4))))
    return nodes, edges


plan = load('city_plan.json')
objects = load('city_objects.json')['objects']
life = load('city_life.json')
previous = json.loads(subprocess.check_output(['git', 'show', 'e4d28cf:' + (CITY / 'city_life.json').relative_to(ROOT).as_posix()], cwd=ROOT))
assert previous['signals'] == life['signals']
area = WalkableArea(plan, objects)
nodes, edges = graph(life)
old_nodes, old_edges = graph(previous)
for a, b, signal, axis in edges:
    assert 0 <= a < len(nodes) and 0 <= b < len(nodes) and a != b
    assert signal in (-1, -2) or (0 <= signal < len(life['signals']) and 0 <= axis < len(life['signals'][signal]['axes']) // 2)
    if signal == -1:
        assert area.segment(nodes[a], nodes[b])
    else:
        p, q = nodes[a], nodes[b]
        center = ((p[0]+q[0])/2, (p[1]+q[1])/2)
        candidates = [c for c in plan['crosswalks'] if math.dist(center, (c['x'],c['y'])) <= .015]
        assert any(abs((q[0]-p[0])*c['along'][0] + (q[1]-p[1])*c['along'][1]) <= .025 and area.segment(p,q,c)
                   for c in candidates), (p,q)

links = collections.defaultdict(list)
for a,b,_,_ in edges:
    links[a].append(b)
    links[b].append(a)
assert len(links) == len(nodes)
assert len({(min(a,b),max(a,b)) for a,b,_,_ in edges}) == len(edges)
remaining = set(links)
largest = 0
while remaining:
    frontier = [remaining.pop()]
    count = 1
    while frontier:
        for neighbor in links[frontier.pop()]:
            if neighbor in remaining:
                remaining.remove(neighbor)
                frontier.append(neighbor)
                count += 1
    largest = max(largest,count)
assert largest / len(nodes) > .9

# El antiguo offset multiplicaba el largo del tramo. Demostrar invasión con la ubicación real del patio.
hideout = next(o for o in objects if o.get('place',{}).get('kind') == 'escondite')
yaw = math.radians(hideout['yaw'])
fx, fy = math.sin(yaw), math.cos(yaw)
cx = hideout['x'] + fx * (HIDEOUT_YARD-HIDEOUT_REAR)/2
cy = hideout['y'] + fy * (HIDEOUT_YARD-HIDEOUT_REAR)/2
hw = hideout['size'][0]/2+HIDEOUT_SIDE
hd = hideout['size'][1]/2+(HIDEOUT_YARD+HIDEOUT_REAR)/2


def local(p):
    dx,dy = p[0]-cx,p[1]-cy
    return dx*fy-dy*fx, dx*fx+dy*fy


old_patio = 0
old_cuts = 0
old_max_offset = 0.
for a,b,s,_ in old_edges:
    if s != -1:
        continue
    p,q = old_nodes[a],old_nodes[b]
    old_cuts += not area.segment(p,q)
    old_max_offset = max(old_max_offset, math.dist(p,q)*.6)
    for side in (-.6,.6):
        target = q[0]+(q[1]-p[1])*side, q[1]-(q[0]-p[0])*side
        old_patio += segment_box(local(p),local(target),hw,hd) < .001
assert old_patio > 0 and old_cuts > 0
assert all(segment_box(local(nodes[a]),local(nodes[b]),hw,hd) >= .55 for a,b,_,_ in edges)

fixture = {'kinds':{'street':{'width':12,'sidewalk':3.5}},
           'roads':[{'id':'A','kind':'street','points':[(-40,0),(40,0)]}], 'intersections':[]}
walk = WalkableArea(fixture)
cross = {'x':0,'y':0,'along':[1,0],'length':12}
assert walk.segment((-10,7.75),(10,7.75))
assert not walk.segment((0,7.75),(0,-7.75))
assert walk.segment((0,7.75),(0,-7.75),cross)
assert not walk.segment((2,7.75),(2,-7.75),cross)
house = {'x':0,'y':9,'yaw':30,'kind':'house','size':[4,4,5]}
assert not WalkableArea(fixture,[house]).segment((-10,7.75),(10,7.75))

result = dict(nodes=len(nodes), edges=len(edges), crossings=sum(e[2]!=-1 for e in edges),
              signalized_crossings=sum(e[2]>=0 for e in edges), signals_preserved=len(life['signals']),
              largest_component=largest, old_sidewalk_shortcuts=old_cuts,
              old_max_lateral_metres=round(old_max_offset,3), old_patio_intrusions_at_max_offset=old_patio,
              new_patio_intrusions=0, native_unity_tested=False)
(HERE / 'graph-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
