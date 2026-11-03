import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/Cast_R3.blend'))
report=[]
for scene in bpy.data.scenes:
    rigs=[o for o in scene.objects if o.type=='ARMATURE']
    if len(rigs)!=1:continue
    rig=rigs[0]
    report.append({'scene':scene.name,'rig':rig.name,'collections':[c.name for c in scene.collection.children],
        'objects':[{'name':o.name,'role':o.get('CharacterRole'),'parent':o.parent.name if o.parent else None} for o in scene.objects if o.type=='MESH'],
        'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones}})
(BASE/'cast_inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CAST_SCENES',[(r['scene'],r['rig']) for r in report],flush=True)
