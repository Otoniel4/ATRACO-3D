import bpy,json,sys
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from hands import replace_hands
from sources import previous_revision;old=previous_revision();bpy.ops.wm.open_mainfile(filepath=str(old/'baseline/Cast_R3.blend'))
catalog=json.loads((old/'baseline/cast_catalog.json').read_text());report=[]
for entry in catalog:
    scene=bpy.data.scenes['LegsR3_'+entry['id']];rig=next(o for o in scene.objects if o.type=='ARMATURE')
    hands,audit=replace_hands(scene,rig,entry['id']);scene.name='LifeR6_'+entry['id']
    report.append({'id':entry['id'],'scene':scene.name,'rig':rig.name,'bones':len(rig.data.bones),'hands':hands.name,'audit':audit,'objects':[o.name for o in scene.objects if o.type=='MESH']})
    scene.frame_set(1)
    if entry['id']=='NPC02_Denim':
        target=Vector((0,-.02,1));scene.camera.location=target+Vector((2,-6,1));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.2
        scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders/Manos_Cuerpo_R6.png');bpy.ops.render.render(write_still=True)
(B/'hands_catalog.json').write_text(json.dumps(report,indent=2));bpy.context.window.scene=bpy.data.scenes['LifeR6_NPC02_Denim']
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Elenco_Manos_R6.blend'),compress=True);print('HANDS_CREATED',len(report),flush=True)
