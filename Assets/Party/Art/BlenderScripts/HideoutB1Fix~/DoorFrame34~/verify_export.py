"""Reimporta ambos FBX y contrasta geometría ajena al acceso, sin ejecutar Unity."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import bpy

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
OUT = ART.parents[2] / 'Library/Alarma/DoorFrame34'
review = bpy.context.window.scene

def fingerprints(path):
    scene = bpy.data.scenes.new('Verificacion_FBX')
    bpy.context.window.scene = scene
    bpy.ops.import_scene.fbx(filepath=str(path))
    bpy.context.view_layer.update()
    result = Counter()
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.name.startswith(('DoorPanel_', 'DoorWindow_', 'DoorHandle_', 'Detail_Door', 'EntranceJamb', 'EntranceLintel')):
            continue
        points = sorted(tuple(round(v,3) for v in obj.matrix_world @ p.co) for p in obj.data.vertices)
        materials = sorted(m.name.split('.')[0] for m in obj.data.materials if m)
        payload = (points, len(obj.data.polygons), materials)
        result[hashlib.sha256(repr(payload).encode()).hexdigest()] += 1
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.window.scene = review
    bpy.data.scenes.remove(scene)
    return result

old = fingerprints(ART / 'City/Shops/Local_Escondite.fbx')
new = fingerprints(OUT / 'City/Shops/Local_Escondite.fbx')
assert old == new, (sum((old-new).values()),sum((new-old).values()))
result = dict(unchanged_meshes=sum(old.values()), fbx_reimport_passed=True, unity_play_tested=False)
(HERE / 'export-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result)
