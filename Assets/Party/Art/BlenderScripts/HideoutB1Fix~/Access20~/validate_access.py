"""Comprueba la abertura, el pavimento y el giro del portón en el FBX reimportado."""
import itertools
import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
RADIUS, HEIGHT, TOP = .24, 1.75, .143
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ART / 'City/Shops/Local_Escondite.fbx'))
gate = bpy.data.objects['GateLeaf_L']
threshold = bpy.data.objects['Umbral_Porton'].matrix_world.translation
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
assert abs(threshold.z - TOP) < .001
assert any(o.name.startswith('PushContact_L') and o.parent == gate for o in bpy.data.objects)


def tree(objects):
    vertices, faces = [], []
    for obj in objects:
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(offset + i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces)


def moving_leaf(obj):
    while obj is not None:
        if obj.name in {'GateLeaf_L', 'SlideGate', 'GarageDoor', 'DoorLeaf_L', 'DoorLeaf_R'}:
            return True
        obj = obj.parent
    return False


structural = [o for o in meshes if not o.name.startswith(('Detail_', 'FloorTiles', 'CeilingLight'))]
static_tree = tree([o for o in structural if not moving_leaf(o)])
panel = [o for o in structural if o.parent == gate]
points = [gate.matrix_world.inverted() @ (o.matrix_world @ v.co) for o in panel for v in o.data.vertices]
lo, hi = (Vector([fn(v[i] for v in points) for i in range(3)]) for fn in (min, max))
box = [gate.matrix_world @ Vector(p) for p in itertools.product(*zip(lo, hi))]
faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
pivot = gate.matrix_world.translation
for degrees in range(-85, 86):
    rotation = Matrix.Rotation(math.radians(degrees), 3, 'Z')
    rotated = [pivot + rotation @ (p - pivot) for p in box]
    candidate = BVHTree.FromPolygons(rotated, faces)
    if static_tree.overlap(candidate):
        offenders = [o.name for o in structural if not moving_leaf(o) and tree([o]).overlap(candidate)]
        raise AssertionError(('intersección de marco', degrees, offenders))

walkway = tree([bpy.data.objects['PatioWalkway']])
for dy in (-.55, -.4, -.2, 0, .2, .5, .8):
    origin = threshold + Vector((0, dy, .5))
    hit, normal, _, _ = walkway.ray_cast(origin, Vector((0, 0, -1)), 1)
    assert hit is not None and abs(hit.z - TOP) < .001 and normal.z > .95, dy

# En el umbral, la misma cápsula que el jugador debe pasar cuando la hoja abre hacia cualquiera de los lados.
def clearance(degrees):
    rotation = Matrix.Rotation(math.radians(degrees), 3, 'Z')
    panel_tree = BVHTree.FromPolygons([pivot + rotation @ (p - pivot) for p in box], faces)
    distances = []
    for dy in (-.52, -.4, -.2, 0, .2, .5, .78):
        for height in (RADIUS, .65, .95, 1.25, HEIGHT - RADIUS):
            point = threshold + Vector((0, dy, .035 + height))
            distances.extend((static_tree.find_nearest(point)[3], panel_tree.find_nearest(point)[3]))
    return min(distances)


closed = clearance(0)
open_clearance = [clearance(angle) for angle in (-85, -82, 82, 85)]
assert closed < RADIUS and min(open_clearance) > RADIUS, (closed, open_clearance)
assert abs(TOP - .14) < .004
assert (bpy.data.objects['PlayerSpawn'].matrix_world.translation - Vector((0, -6, .185))).length < .001
result = dict(fbx_meshes=len(meshes), triangles=sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons),
              angular_samples=171, walkway_height=TOP, sidewalk_height=.14, capsule_radius=RADIUS,
              open_clearance=open_clearance, closed_clearance=closed)
Path(os.environ.get('ALARMA_HIDEOUT_GEOMETRY_REPORT', HERE / 'geometry-results.json')).write_text(
    json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('HIDEOUT_ACCESS_VALID', json.dumps(result))
