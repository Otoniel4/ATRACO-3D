"""Comprueba escala, marcador y espacio de aparición en el FBX reimportado; no ejecuta PhysX ni Unity."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ART = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ART / 'City/Shops/Local_Escondite.fbx'))
spawn = next(o for o in bpy.data.objects if o.name == 'PlayerSpawn')
feet = spawn.matrix_world.translation
assert (feet - Vector((0, -6, .185))).length < .001, tuple(feet)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
vertices, polygons = [], []
moving = {'DoorLeaf_L', 'DoorLeaf_R', 'GateLeaf_L', 'SlideGate'}
def is_moving(obj):
    while obj is not None:
        if obj.name in moving:
            return True
        obj = obj.parent
    return False

for obj in meshes:
    if obj.name.startswith('Detail_') or is_moving(obj):
        continue
    start = len(vertices)
    vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
    polygons.extend(tuple(start + i for i in poly.vertices) for poly in obj.data.polygons)
tree = BVHTree.FromPolygons(vertices, polygons)
hit, normal, _, _ = tree.ray_cast(feet + Vector((0, 0, .28)), Vector((0, 0, -1)), .93)
assert hit is not None and abs(hit.z - .15) < .001 and normal.z > .64
# Muestras sobre el eje de la cápsula, incluyendo la esfera inferior/superior, contra triángulos reales.
minimum = float('inf')
for i in range(101):
    center = feet + Vector((0, 0, .24 + (1.75 - .48) * i / 100))
    nearest, _, _, distance = tree.find_nearest(center)
    assert nearest is not None
    minimum = min(minimum, distance)
assert minimum > .24, minimum
assert len([o for o in meshes if o.name.startswith('Detail_MonitorFoot')]) == 3
assert len([o for o in meshes if o.name.startswith('Detail_ChairLeg')]) == 24
assert len([o for o in meshes if o.name.startswith('Detail_HangerHook')]) == 6
assert len([o for o in meshes if o.name.startswith('Detail_Caster')]) == 5
assert all(not o.data.validate() for o in meshes)
result = dict(meshes=len(meshes), triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),
              marker_local_blender=list(feet), floor_height=hit.z, minimum_capsule_axis_distance=minimum,
              probe_above_feet=.28, maximum_drop=.65, capsule_height=1.75, capsule_radius=.24,
              fbx_reimport_passed=True, unity_play_tested=False)
(OUT / 'geometry-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('HIDEOUT_GEOMETRY_VALID', json.dumps(result))
