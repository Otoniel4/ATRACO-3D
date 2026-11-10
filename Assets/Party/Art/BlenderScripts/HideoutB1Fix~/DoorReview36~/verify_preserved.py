"""Compara geometría y materiales ajenos a las puertas, incluido el garaje y portón de la guarida."""
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;ART=HERE.parents[2]
OUT=ART.parents[2]/'Library/Alarma/DoorReview36'

def fingerprints(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    moving=set()
    for o in bpy.data.objects:
        if o.name.startswith(('DoorLeaf_L','DoorLeaf_R')):moving.update(o.children_recursive)
    result=Counter()
    for o in bpy.data.objects:
        if o.type!='MESH' or o in moving or o.name.startswith(('Detail_DoorJamb','Detail_DoorLintel','DoorReveal','DoorPivotHousing','EntranceJamb','EntranceLintel','EntrancePivotHousing')):continue
        vertices=sorted(tuple(round(v,3) for v in o.matrix_world@p.co) for p in o.data.vertices)
        materials=[re.sub(r'\.\d+$','',m.name) for m in o.data.materials if m]
        signature=json.dumps([vertices,len(o.data.polygons),materials],sort_keys=True).encode()
        result[hashlib.sha256(signature).hexdigest()]+=1
    return result

report={}
for path in sorted((OUT/'City/Shops').glob('Local_*.fbx')):
    before=fingerprints(ART/'City/Shops'/path.name);after=fingerprints(path)
    assert before==after,(path.stem,sum((before-after).values()),sum((after-before).values()))
    report[path.stem]=sum(before.values())
(HERE/'preserved-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('MALLAS AJENAS A PUERTAS IDENTICAS',report)
