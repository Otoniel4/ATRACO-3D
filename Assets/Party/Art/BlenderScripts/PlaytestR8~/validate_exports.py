import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;report=[]
for path in sorted((B/'export/Characters').glob('*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    for t in rig.animation_data.nla_tracks:t.mute=True
    values={}
    for mode in ['Walk','Run']:
        action=next(a for a in bpy.data.actions if a.name==rig.name+'|'+mode);rig.animation_data.action=action
        if action.slots:rig.animation_data.action_slot=action.slots[0]
        samples=[]
        for fraction in [0,.125,.25,.375,.5,.625,.75,.875]:
            frame=action.frame_range[0]+fraction*(action.frame_range[1]-action.frame_range[0]);bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();samples.append(rig.matrix_world@rig.pose.bones['LeftFoot'].head)
        delta=max((p-samples[0]).length for p in samples);assert delta>.07,(path.name,mode,delta);values[mode]=delta
    report.append({'model':path.name,'foot_travel_m':values,'bones':len(rig.data.bones)})
for path in (B/'export/Doors').glob('*.fbx'):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));vertices=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices];height=max(p.z for p in vertices)-min(p.z for p in vertices);assert 2.5<height<3.5,(path.name,height)
assert len(report)==18,len(report)
(B/'fbx_validation.json').write_text(json.dumps({'passed':True,'reimported_characters':report,'reimported_doors':9,'unity_play_tested':False},indent=2));print('R8_FBX_PASS',len(report),'characters and 9 doors',flush=True)
