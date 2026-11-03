"""Conserva el elenco propio, añade carrera y coloca la bolsa del ladrón sobre su espalda."""
import bpy, json, math, sys
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector, Matrix
B=Path(__file__).resolve().parent;R6=r6();sys.path.insert(0,str(R6))
import animation
from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(R6/'Elenco_Animado_R6.blend'))
catalog=json.loads((R6/'animation_catalog.json').read_text());report=[]
def run(rig,t):
    saved=dict(animation.C)
    animation.C.update(walk_cycle_seconds=2/3,stance_fraction=.43,step_travel_m=.88,foot_lift_m=.18)
    animation.pose(rig,t,'Walk');animation.C.clear();animation.C.update(saved)
    phase=t/(2/3)*math.tau
    for side,sign in [('Left',1),('Right',-1)]:
        upper=rig.data.bones[side+'UpperArm'];lower=rig.data.bones[side+'LowerArm'];head=rig.pose.bones[side+'UpperArm'].head.copy()
        swing=.75*math.sin(phase+(math.pi if side=='Left' else 0))
        elbow=head+Vector((sign*.10,swing,-1)).normalized()*upper.length
        hand=elbow+Vector((sign*.04,-.88,-.20+swing*.35)).normalized()*lower.length
        animation.segment(rig,side+'UpperArm',head,elbow);bpy.context.view_layer.update()
        animation.segment(rig,side+'LowerArm',elbow,hand);bpy.context.view_layer.update()
    spine=rig.pose.bones['Spine'];spine.matrix=Matrix.Translation(spine.head)@Matrix.Rotation(.10,4,'X')@Matrix.Translation(-spine.head)@spine.matrix
    bpy.context.view_layer.update()
for row in catalog:
    scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
    scene.render.fps=24
    rig.animation_data.action=None
    for track in rig.animation_data.nla_tracks:track.mute=True
    if row['id']=='Player01_Thief':
        bag=bpy.data.objects[row['id']+'_Accessories'];vertices=[v.co.copy() for v in bag.data.vertices]
        lo=Vector(tuple(min(v[i] for v in vertices) for i in range(3)));hi=Vector(tuple(max(v[i] for v in vertices) for i in range(3)));center=(lo+hi)*.5
        for vertex in bag.data.vertices:vertex.co=Matrix.Rotation(math.pi/2,4,'Z')@((vertex.co-center)*.85)+Vector((0,.29,1.16))
        bag.vertex_groups.clear();bag.vertex_groups.new(name='Chest').add(list(range(len(vertices))),1,'REPLACE')
        print('BAG_MOVED',list(center),'to',[0,.29,1.16],flush=True)
    action=bpy.data.actions.new(rig.name+'_Run');rig.animation_data.action=action
    for frame in range(1,18):
        scene.frame_set(frame);run(rig,(frame-1)/24)
        for bone in rig.pose.bones:
            bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name)
            bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
    action.use_fake_user=True;rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='Run';track.strips.new('Run',1,action);track.mute=True
    actions={t.name:t.strips[0].action for t in rig.animation_data.nla_tracks};audit={}
    for mode in ['Idle','Walk','Run','Browse','Pay','CarryWalk']:
        rig.animation_data.action=actions[mode];samples=[]
        for frame in [1,5,9,13,17]:
            scene.frame_set(frame);bpy.context.view_layer.update();samples.append(list(rig.pose.bones['LeftFoot'].head))
        audit[mode]=samples
    assert max(Vector(p).y for p in audit['Run'])-min(Vector(p).y for p in audit['Run'])>.5,row['id']
    rig.animation_data.action=None
    for t in rig.animation_data.nla_tracks:t.mute=False
    bag=bpy.data.objects[row['bag']];bag.hide_render=False;bag.hide_viewport=False
    export(B/'export/Characters'/(row['id']+'.fbx'),[o for o in scene.objects if o.type in ['MESH','ARMATURE','EMPTY']],True)
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=actions['Idle'];scene.frame_set(1)
    report.append({'id':row['id'],'rig':row['rig'],'clips':audit})
(B/'character_validation.json').write_text(json.dumps({'passed':True,'characters':report,'run_clip':True,'thief_bag':'Chest; back +Y'},indent=2))
(B/'characters.json').write_text(json.dumps({'characters':[{'id':r['id'],'rig':r['rig']} for r in catalog]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Elenco_Corregido_R8.blend'),compress=True)
print('CHARACTERS_R8_READY',len(report),flush=True)
