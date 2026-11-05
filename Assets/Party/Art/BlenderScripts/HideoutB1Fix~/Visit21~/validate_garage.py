"""Reimporta el FBX y valida el garaje y el acceso peatonal."""
import itertools
import json
import os
import runpy
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
os.environ['ALARMA_HIDEOUT_GEOMETRY_REPORT'] = str(HERE / 'pedestrian-access.json')
access = runpy.run_path(str(HERE.parent / 'Access20~' / 'validate_access.py'))
static_tree = access['static_tree']
faces = access['faces']


def box(low, high):
    return BVHTree.FromPolygons([Vector(p) for p in itertools.product(*zip(low, high))], faces)


leaf = bpy.data.objects['GarageDoor']
threshold = bpy.data.objects['Umbral_Auto'].matrix_world.translation
opened = bpy.data.objects['GarageOpen'].matrix_world.translation
travel = opened - leaf.matrix_world.translation
slats = [o for o in leaf.children if o.name.startswith('GarageSlat_') and o.type == 'MESH']
assert len(slats) == 17 and abs(travel.z - 2.465) < .002 and abs(travel.x) + abs(travel.y) < .001
vertices = [obj.matrix_world @ v.co for obj in slats for v in obj.data.vertices]
lo, hi = (Vector([fn(v[i] for v in vertices) for i in range(3)]) for fn in (min, max))
assert 3.50 < hi.x - lo.x < 3.54
height = threshold.z + travel.z
for i in range(100):
    bottom = lo.z + travel.z * i / 100
    clipped = box((lo.x, lo.y, bottom), (hi.x, hi.y, height))
    if static_tree.overlap(clipped):
        offenders = [o.name for o in access['structural'] if not access['moving_leaf'](o)
                     and access['tree']([o]).overlap(clipped)]
        raise AssertionError((i, tuple(lo), tuple(hi), offenders))

# Envolvente del compacto del proyecto, con espacio delante y detrás.
parked = box((threshold.x - .87, threshold.y + .24, threshold.z + .005),
             (threshold.x + .87, threshold.y + 4.14, threshold.z + 1.505))
assert not static_tree.overlap(parked)
for dy in (-.62, 0, .4, 2, 4.14):
    origin = threshold + Vector((0, dy, .6))
    surface, normal, _, _ = static_tree.ray_cast(origin, Vector((0, 0, -1)), 1)
    assert surface is not None and abs(surface.z - threshold.z) < .002 and normal.z > .95, dy

result = dict(slats=len(slats), lift_m=round(travel.z, 3), curtain_width_m=round(hi.x - lo.x, 3),
              sweep_samples=100, compact_car_m=[3.9, 1.74, 1.50], compact_clear=True, native_unity_tested=False)
(HERE / 'garage-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('GARAGE_VALID', json.dumps(result))
