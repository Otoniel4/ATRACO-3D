"""Busca accesos sobre el suelo FBX y el grafo guardado por Unity en la revisión 20."""
from array import array
import json
import math
import re
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
PARTY = HERE.parents[3]
ART = PARTY / 'Art'
GROUND = ART / 'City/Ground25'
CITY = ART / 'BlenderScripts/City25~'


def read_data(folder, name):
    return json.loads((folder / (name + '.json')).read_text(encoding='utf-8-sig'))


graph = (PARTY / 'Generated/Ciudad2km/Data/SidewalkGraph.asset').read_text(encoding='utf-8-sig')
nodes = [(float(x), float(y)) for x, y in re.findall(r'^  - \{x: ([^,]+), y: ([^}]+)\}$', graph, re.M)]


def indices(name):
    data = array('i')
    data.frombytes(bytes.fromhex(re.search(r'^  ' + name + r': ([a-f0-9]+)$', graph, re.M)[1]))
    return data


first, target, signal = (indices(name) for name in ('first', 'target', 'signal'))
assert len(first) == len(nodes) + 1 and len(target) == len(signal)
spawnable, visited = set(), set()
for node in range(len(nodes)):
    if node in visited or first[node] == first[node + 1]:
        continue
    component = [node]
    visited.add(node)
    for current in component:
        for link in range(first[current], first[current + 1]):
            if target[link] not in visited:
                visited.add(target[link])
                component.append(target[link])
    if len(component) >= 8:
        spawnable.update(n for n in component if all(signal[i] == -1 for i in range(first[n], first[n + 1])))

manifest = read_data(GROUND, 'ground')
tiles = {tuple(s['sector']): s for s in manifest['sectors']}
size, half = manifest['sector_m'], manifest['half']
surface_cache = {}
allowed = {'Acera', 'Bordillo', 'Cesped', 'Lote', 'Concreto', 'Pavimento', 'Alcantarilla'}


def load_tile(tile):
    if tile in surface_cache:
        return surface_cache[tile]
    sector = tiles[tile]
    previous = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(GROUND / (sector['id'] + '.fbx')))
    vertices, faces, materials = [], [], []
    translation = Vector((*sector['center'], 0))
    for obj in set(bpy.data.objects) - previous:
        if obj.type != 'MESH':
            continue
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co + translation for v in obj.data.vertices)
        for face in obj.data.polygons:
            faces.append(tuple(offset + i for i in face.vertices))
            materials.append(obj.data.materials[face.material_index].name.split('.')[0].removeprefix('City25_'))
    surface_cache[tile] = BVHTree.FromPolygons(vertices, faces), materials
    return surface_cache[tile]


def supported(x, y):
    tiles_near = {(math.floor((x + half + dx) / size), math.floor((y + half + dy) / size))
                  for dx, dy in ((0, 0), (-.01, -.01), (.01, .01), (-.01, .01), (.01, -.01))}
    best = None
    for tile in tiles_near:
        if tile not in tiles:
            continue
        tree, materials = load_tile(tile)
        hit, normal, face, _ = tree.ray_cast(Vector((x, y, .475)), Vector((0, 0, -1)), .64)
        if hit is not None and (best is None or hit.z > best[0]):
            best = hit.z, normal.z, materials[face]
    return best is not None and best[1] >= .65 and best[2] in allowed


def approach(start, end, length):
    dx, dy = end[0] - start[0], end[1] - start[1]
    if length < .015:
        return supported(*end)
    steps = math.ceil(length / .8)
    return all(supported(start[0] + dx * i / steps + dy / length * offset,
                         start[1] + dy * i / steps - dx / length * offset)
               for i in range(steps + 1) for offset in (0, .53, -.53))


layouts = {s['kind']: s['sidewalk'] for s in read_data(ART / 'City/Shops', 'shop_layouts')['shops']}
results = []
for item in read_data(CITY, 'city_objects')['objects']:
    place = item.get('place', {})
    kind = place.get('kind')
    if kind not in layouts:
        continue
    angle = math.radians(item['yaw'])
    sin, cos = math.sin(angle), math.cos(angle)
    markers = [(item['x'] + x * cos + y * sin, item['y'] - x * sin + y * cos)
               for x, y in zip(layouts[kind][::2], layouts[kind][1::2])]
    candidates = []
    for end in markers:
        for node in spawnable:
            start = nodes[node]
            dx, dy = start[0] - end[0], start[1] - end[1]
            distance2 = dx * dx + dy * dy
            if distance2 < 18 * 18 and dx * sin + dy * cos >= -.7:
                candidates.append((distance2, start, end))
    result = next((round(math.sqrt(d), 2) for d, start, end in sorted(candidates) if approach(start, end, math.sqrt(d))), None)
    results.append(dict(name=place['name'], kind=kind, ground_distance_m=result))

confirmed = [x for x in results if x['ground_distance_m'] is not None]
assert {'supermercado', 'joyeria', 'banco'} <= {x['kind'] for x in confirmed}
result = dict(verified_ground=len(confirmed), shops=len(results), graph_links=len(target) // 2,
              native_unity_tested=False, locations=results)
(HERE / 'shop-approaches.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('SHOP_APPROACH_GROUND_VALID', len(confirmed), '/', len(results), 'shops')
