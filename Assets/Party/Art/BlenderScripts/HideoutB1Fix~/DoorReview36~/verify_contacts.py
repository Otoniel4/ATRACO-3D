"""Mide el apoyo de palma con los diez FBX reales. No abre Unity ni cambia sus modelos."""
import json
import itertools
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

HERE=Path(__file__).resolve().parent
ART=HERE.parents[2]
results=[]

def frame(f,n):
    z=f.normalized();x=n.cross(z).normalized();y=z.cross(x)
    return Matrix((x,y,z)).transposed().to_quaternion()

def turn(rig,bone,q):
    world=rig.matrix_world@bone.matrix
    bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(world.translation,q,world.to_scale())
    bpy.context.view_layer.update()

for path in sorted((ART/'Characters/Cast').glob('NPC*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    grip=next(o for o in bpy.data.objects if o.name.startswith('Grip_R6_'))
    for obj in (rig,grip):
        obj.animation_data_create()
        for track in obj.animation_data.nla_tracks:track.mute=True
        action=bpy.data.actions.get(obj.name+'|Idle');obj.animation_data.action=action
        if action and action.slots:obj.animation_data.action_slot=action.slots[0]
    for sample in (1,17,33):
        for height,cell in itertools.product((1.18,1.28),(-.5,0,.5)): # Interior y acera; tres columnas del grafo.
            bpy.context.scene.frame_set(sample);bpy.context.view_layer.update()
            bones=rig.pose.bones
            def pos(n):return rig.matrix_world@bones[n].head
            def rot(b):return (rig.matrix_world@b.matrix).to_quaternion()
            upper,lower,wrist,spine=[bones[n] for n in ('UpperArm.R','LowerArm.R','Wrist.R','Abdomen')]
            right=pos('UpperArm.R')-pos('UpperArm.L');right.z=0;right.normalize()
            up=Vector((0,0,1));forward=up.cross(right).normalized()
            fingers=pos('Middle2.R')-pos('Wrist.R')
            normal=(pos('Index2.R')-pos('Pinky2.R')).cross(fingers).normalized()
            palm=pos('Middle2.R')-fingers.normalized()*.025+normal*.015
            offset=rot(wrist).inverted()@(palm-pos('Wrist.R'))
            local_frame=rot(wrist).inverted()@frame(fingers,normal)
            contact_x=min((-.162,.162),key=lambda x:abs(x-(cell+.22)))
            initial_distance=.525 if height==1.28 else .475
            adjustment=Vector((contact_x-pos('UpperArm.R').dot(right)-cell,initial_distance-.4,0))
            if adjustment.length>.48:adjustment*=.48/adjustment.length
            target=right*(contact_x-cell-adjustment.x)+forward*(initial_distance-adjustment.y-.035)+up*height
            # Misma inclinación del componente y misma solución a muñeca tras orientar la palma.
            direction=target-pos('UpperArm.R');direction.z=0
            turn(rig,spine,Quaternion(up.cross(direction.normalized()),math.radians(10))@rot(spine))
            rotation=frame(up,forward)@local_frame.inverted()
            goal=target-rotation@offset
            shoulder=pos('UpperArm.R');elbow=pos('LowerArm.R');hand=pos('Wrist.R')
            a=(elbow-shoulder).length;b=(hand-elbow).length
            reach=goal-shoulder;direction=reach.normalized()
            distance=max(abs(a-b)+.001,min(a+b-.001,reach.length))
            along=(a*a-b*b+distance*distance)/(2*distance)
            bend=elbow-shoulder; bend-=direction*bend.dot(direction)
            if bend.length<.0001:bend=-up+right*.45;bend-=direction*bend.dot(direction)
            goal_elbow=shoulder+direction*along+bend.normalized()*math.sqrt(max(0,a*a-along*along))
            turn(rig,upper,(elbow-shoulder).rotation_difference(goal_elbow-shoulder)@rot(upper))
            turn(rig,lower,(pos('Wrist.R')-pos('LowerArm.R')).rotation_difference(goal-pos('LowerArm.R'))@rot(lower))
            turn(rig,wrist,rotation)
            error=(pos('Wrist.R')+rotation@offset-target).length
            results.append({'npc':path.stem,'frame':sample,'contact_height':height,'arrival_column':cell,'error_m':error})

(HERE/'contact-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
maximum=max(r['error_m'] for r in results)
print('CONTACT_CASES',len(results),'MAX_ERROR',maximum)
assert len(results)==180
assert maximum<.035,sorted(results,key=lambda r:r['error_m'],reverse=True)[:5]
