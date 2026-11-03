"""Carrera en el sitio: apoyo real, fase de vuelo y brazos con codos flexionados."""
import bpy,json,math,sys
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Vector,Matrix,Quaternion
B=Path(__file__).resolve().parent;R6=sources9.r6();sys.path.insert(0,str(R6));import animation;from fbx_utils import export;from hands import curl_fingers
bpy.ops.wm.open_mainfile(filepath=str(sources9.r8()/'Elenco_Corregido_R8.blend'));catalog=json.loads((R6/'animation_catalog.json').read_text(encoding='utf-8'));report=[]
PERIOD=5/6;STANCE=.40;TRAVEL=1.0;LIFT=.20
def pose(rig,time):
    for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.matrix_basis=Matrix.Identity(4)
    phase=time/PERIOD*math.tau;shift=Vector((.012*math.sin(phase),0,-.06+.025*math.cos(2*phase)));ankles={};supports=[]
    for side,offset in [('Left',0),('Right',.5)]:
        t=(time/PERIOD+offset)%1;ankle=rig.data.bones[side+'Foot'].head_local.copy()
        if t<STANCE:ankle.y+=-TRAVEL/2+TRAVEL*t/STANCE;supports.append(side)
        else:q=(t-STANCE)/(1-STANCE);ankle.y+=TRAVEL/2-TRAVEL*(q*q*(3-2*q));ankle.z+=LIFT*math.sin(math.pi*q)
        ankles[side]=ankle
        if side in supports:
            hip=rig.data.bones[side+'UpperLeg'].head_local;length=rig.data.bones[side+'UpperLeg'].length+rig.data.bones[side+'LowerLeg'].length-.006
            horizontal=(hip.x+shift.x-ankle.x)**2+(hip.y-ankle.y)**2;allowed=ankle.z+math.sqrt(max(.01,length*length-horizontal))-hip.z;shift.z=min(shift.z,allowed)
    hips=rig.data.bones['Hips'].matrix_local.copy();hips.translation+=shift;rig.pose.bones['Hips'].matrix=hips;bpy.context.view_layer.update()
    for side in ['Left','Right']:animation.leg(rig,side,ankles[side],shift)
    spine=rig.pose.bones['Spine'];spine.matrix=Matrix.Translation(spine.head)@Matrix.Rotation(.11,4,'X')@Matrix.Rotation(.045*math.sin(phase),4,'Z')@Matrix.Translation(-spine.head)@spine.matrix;bpy.context.view_layer.update()
    for side,sign,offset in [('Left',1,0),('Right',-1,math.pi)]:
        upper=rig.data.bones[side+'UpperArm'];lower=rig.data.bones[side+'LowerArm'];head=rig.pose.bones[side+'UpperArm'].head.copy();direction=Vector((sign*.045,.18*math.cos(phase+offset),-.28)).normalized();fore=Matrix.Rotation(-math.radians(85),3,'X')@direction;elbow=head+direction*upper.length;hand=elbow+fore*lower.length
        animation.segment(rig,side+'UpperArm',head,elbow);bpy.context.view_layer.update();animation.segment(rig,side+'LowerArm',elbow,hand);bpy.context.view_layer.update()
    # Pulgares hacia arriba y manos relajadas en vez de palmas de bandeja.
    for side in ['Left','Right']:
        hand=rig.pose.bones[side+'Hand'];axis=(hand.tail-hand.head).normalized();across=rig.pose.bones[side+'ThumbProximal'].head-rig.pose.bones[side+'MiddleProximal'].head;across=(across-axis*across.dot(axis)).normalized();up=Vector((0,0,1));up=(up-axis*up.dot(axis)).normalized();angle=math.atan2(axis.dot(across.cross(up)),across.dot(up));head=hand.head.copy();hand.matrix=Matrix.Translation(head)@Matrix.Rotation(angle,4,axis)@Matrix.Translation(-head)@hand.matrix;bpy.context.view_layer.update()
    curl_fingers(rig,.65);bpy.context.view_layer.update();return supports,ankles
for row in catalog:
    scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']];rig.animation_data.action=None
    for track in list(rig.animation_data.nla_tracks):
        if track.name=='Run':rig.animation_data.nla_tracks.remove(track)
        else:track.mute=True
    action=bpy.data.actions.new(rig.name+'_Run_Normal');rig.animation_data.action=action;maximum_error=0;airborne=0
    for frame in range(1,22):
        scene.frame_set(frame);supports,ankles=pose(rig,(frame-1)/24)
        if not supports:airborne+=1
        for side in supports:maximum_error=max(maximum_error,(rig.pose.bones[side+'Foot'].head-ankles[side]).length)
        for bone in rig.pose.bones:bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name);bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
    assert maximum_error<.005,(row['id'],maximum_error)
    action.use_fake_user=True;rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='Run';track.strips.new('Run',1,action)
    for t in rig.animation_data.nla_tracks:t.mute=False
    bpy.data.objects[row['bag']].hide_viewport=False;bpy.data.objects[row['bag']].hide_render=False
    export(B/'export/Characters'/(row['id']+'.fbx'),[o for o in scene.objects if o.type in ['MESH','ARMATURE','EMPTY']],True)
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name=='Idle');scene.frame_set(1)
    report.append({'id':row['id'],'support_error_m':maximum_error,'flight_frames':airborne})
(B/'characters.json').write_text(json.dumps({'characters':[{'id':r['id'],'rig':r['rig']} for r in catalog]},indent=2));(B/'run_validation.json').write_text(json.dumps({'passed':True,'period':PERIOD,'support_fraction':STANCE,'characters':report},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(B/'Elenco_R9.blend'),compress=True);print('R9_NORMAL_RUN_READY',len(report),flush=True)
