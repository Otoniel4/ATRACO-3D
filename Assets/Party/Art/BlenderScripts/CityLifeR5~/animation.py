"""Locomoción en el sitio con piernas resueltas analíticamente y pies apoyados durante la fase de soporte."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
C=json.loads((Path(__file__).resolve().parent/'settings.json').read_text())


def segment(rig,name,head,target):
    bone=rig.data.bones[name];rest_direction=bone.tail_local-bone.head_local
    rotation=rest_direction.rotation_difference(Vector(target)-Vector(head))@bone.matrix_local.to_quaternion()
    matrix=rotation.to_matrix().to_4x4();matrix.translation=head;rig.pose.bones[name].matrix=matrix


def leg(rig,side,ankle,shift):
    upper=rig.data.bones[side+'UpperLeg'];lower=rig.data.bones[side+'LowerLeg']
    hip=upper.head_local+shift;delta=ankle-hip;distance=min(delta.length,upper.length+lower.length-.0001)
    axis=delta.normalized();a=(upper.length**2-lower.length**2+distance**2)/(2*distance)
    h=math.sqrt(max(0,upper.length**2-a*a));forward=Vector((0,-1,0));forward=(forward-axis*forward.dot(axis)).normalized()
    knee=hip+axis*a+forward*h;end=hip+axis*distance
    segment(rig,side+'UpperLeg',hip,knee);bpy.context.view_layer.update()
    segment(rig,side+'LowerLeg',knee,end);bpy.context.view_layer.update()
    matrix=rig.data.bones[side+'Foot'].matrix_local.copy();matrix.translation=end;rig.pose.bones[side+'Foot'].matrix=matrix


def pose(rig,seconds,mode='Walk'):
    for bone in rig.pose.bones:bone.rotation_mode='QUATERNION';bone.matrix_basis=Matrix.Identity(4)
    walking=mode in ['Walk','CarryWalk'];phase=seconds/C['walk_cycle_seconds']*math.tau
    idle_phase=seconds*math.pi*(1.5 if mode=='Pay' else 1)
    shift=Vector((0,0,-.035+.010*math.cos(phase*2))) if walking else Vector((0,0,-.015+.003*math.sin(idle_phase)))
    hips=rig.data.bones['Hips'].matrix_local.copy();hips.translation+=shift;rig.pose.bones['Hips'].matrix=hips
    bpy.context.view_layer.update()
    for side,offset in [('Left',0),('Right',.5)]:
        ankle=rig.data.bones[side+'Foot'].head_local.copy()
        if walking:
            t=(seconds/C['walk_cycle_seconds']+offset)%1;s=C['stance_fraction'];travel=C['step_travel_m']
            if t<s:y=-travel*.5+travel*t/s;lift=0
            else:
                q=(t-s)/(1-s);smooth=q*q*(3-2*q);y=travel*.5-travel*smooth;lift=C['foot_lift_m']*math.sin(math.pi*q)
            ankle.y+=y;ankle.z+=lift
        leg(rig,side,ankle,shift)
    for side,sign in [('Left',1),('Right',-1)]:
        upper=rig.data.bones[side+'UpperArm'];lower=rig.data.bones[side+'LowerArm'];head=upper.head_local+shift
        swing=.22*math.sin(phase+(math.pi if side=='Left' else 0)) if walking else .025*math.sin(idle_phase)
        direction=Vector((sign*.12,swing,-1)).normalized();forearm=Vector((sign*.10,swing-.11,-1)).normalized()
        if mode=='CarryWalk' and side=='Right':direction=Vector((sign*.10,-.10,-1)).normalized();forearm=Vector((sign*.04,-.70,-.70)).normalized()
        if mode in ['Browse','Pay'] and side=='Right':
            wave=.04*math.sin(idle_phase*2)
            direction=Vector((sign*.14,-.40,-.85)).normalized();forearm=Vector((sign*.03,-1,.12+wave)).normalized()
        elbow=head+direction*upper.length;hand=elbow+forearm*lower.length
        segment(rig,side+'UpperArm',head,elbow);bpy.context.view_layer.update()
        segment(rig,side+'LowerArm',elbow,hand);bpy.context.view_layer.update()
    if mode=='Browse':
        head=rig.pose.bones['Head'];head.rotation_quaternion=Quaternion((0,0,1),.10*math.sin(idle_phase))
    bpy.context.view_layer.update()


def bake_actions(rig):
    rig.animation_data_clear();actions={}
    for mode,frames in [('Idle',49),('Walk',25),('Browse',49),('Pay',33),('CarryWalk',25)]:
        action=bpy.data.actions.new(rig.name+'_'+mode);rig.animation_data_create().action=action
        for frame in range(1,frames+1):
            bpy.context.scene.frame_set(frame);pose(rig,(frame-1)/24,mode)
            for bone in rig.pose.bones:
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name)
                bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
        actions[mode]=action;action.use_fake_user=True
    rig.animation_data.action=None
    for mode,action in actions.items():
        track=rig.animation_data.nla_tracks.new();track.name=mode;track.strips.new(mode,1,action);track.mute=True
    rig.animation_data.action=actions['Idle'];return actions
