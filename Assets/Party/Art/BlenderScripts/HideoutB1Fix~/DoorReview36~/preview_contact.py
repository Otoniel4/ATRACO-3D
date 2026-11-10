"""Vista nativa del contacto con el banco usando el FBX real. No es una captura de Unity."""
from pathlib import Path
import bpy
from mathutils import Matrix,Quaternion,Vector
import math
HERE=Path(__file__).resolve().parent;ART=HERE.parents[2]
OUT=ART.parents[2]/'Library/Alarma/DoorReview36'
scope={'__file__':str(HERE/'verify_contacts.py')}
exec((HERE/'verify_contacts.py').read_text().split('for path in sorted',1)[0],scope)
turn,frame=scope['turn'],scope['frame']
scene=bpy.data.scenes.new('Banco_Contacto36');bpy.context.window.scene=scene
bpy.ops.import_scene.fbx(filepath=str(OUT/'City/Shops/Local_Banco.fbx'))
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ART/'Characters/Cast/NPC10_Cardigan.fbx'))
objects=set(bpy.data.objects)-before
rig=next(o for o in objects if o.type=='ARMATURE')
grip=next(o for o in objects if o.name.startswith('Grip_R6_'))
for obj in (rig,grip):
    obj.animation_data_create()
    for track in obj.animation_data.nla_tracks:track.mute=True
    action=next(a for a in bpy.data.actions if a.name.startswith(obj.name.split('.')[0]+'|Idle'))
    obj.animation_data.action=action
    if action.slots:obj.animation_data.action_slot=action.slots[0]
for obj in objects:
    if obj.name.startswith('ShoppingBag_'):obj.hide_set(True)
scene.frame_set(1);bpy.context.view_layer.update()
body=bpy.data.objects.new('Cliente_Banco',None);scene.collection.objects.link(body)
for obj in objects:
    if obj.parent is None:obj.parent=body
bones=rig.pose.bones
def pos(n):return rig.matrix_world@bones[n].head
def rot(b):return (rig.matrix_world@b.matrix).to_quaternion()
right=pos('UpperArm.R')-pos('UpperArm.L');right.z=0;right.normalize()
body.rotation_mode='QUATERNION';body.rotation_quaternion=right.rotation_difference(Vector((1,0,0)))
bpy.context.view_layer.update()
target=Vector((.162,-11.010,1.28))
body.location=Vector((target.x-pos('UpperArm.R').x,-11.375,0));bpy.context.view_layer.update()
upper,lower,wrist,spine=[bones[n] for n in ('UpperArm.R','LowerArm.R','Wrist.R','Abdomen')]
fingers=pos('Middle2.R')-pos('Wrist.R');normal=(pos('Index2.R')-pos('Pinky2.R')).cross(fingers).normalized()
palm=pos('Middle2.R')-fingers.normalized()*.025+normal*.015
offset=rot(wrist).inverted()@(palm-pos('Wrist.R'));local=rot(wrist).inverted()@frame(fingers,normal)
up=Vector((0,0,1));forward=Vector((0,1,0))
direction=target-pos('UpperArm.R');direction.z=0
turn(rig,spine,Quaternion(up.cross(direction.normalized()),math.radians(10))@rot(spine))
rotation=frame(up,forward)@local.inverted();goal=target-rotation@offset
shoulder=pos('UpperArm.R');elbow=pos('LowerArm.R');hand=pos('Wrist.R')
a=(elbow-shoulder).length;b=(hand-elbow).length;reach=goal-shoulder;direction=reach.normalized()
d=max(abs(a-b)+.001,min(a+b-.001,reach.length));along=(a*a-b*b+d*d)/(2*d)
bend=elbow-shoulder;bend-=direction*bend.dot(direction)
new_elbow=shoulder+direction*along+bend.normalized()*math.sqrt(max(0,a*a-along*along))
turn(rig,upper,(elbow-shoulder).rotation_difference(new_elbow-shoulder)@rot(upper))
turn(rig,lower,(pos('Wrist.R')-pos('LowerArm.R')).rotation_difference(goal-pos('LowerArm.R'))@rot(lower))
turn(rig,wrist,rotation)
camera=bpy.data.objects.new('Contacto36_Camara',bpy.data.cameras.new('Contacto36_Camara'));scene.collection.objects.link(camera);scene.camera=camera
scene.render.resolution_x,scene.render.resolution_y=1100,900;scene.render.resolution_percentage=100
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
for name,location,aim,lens in [('banco_contacto',(2.0,-13.5,2.1),(0,-11.1,1.2),50),('banco_palma',(.9,-11.8,1.6),(.162,-11.01,1.28),65)]:
    camera.location=location;camera.rotation_euler=(Vector(aim)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens
    scene.render.filepath=str(HERE/(name+'.png'))
    with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
print('Palm error',(pos('Wrist.R')+rotation@offset-target).length)
