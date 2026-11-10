import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ART=HERE.parents[1]
rigs=[]
def frame(f,n):
    z=f.normalized();x=n.cross(z).normalized();y=z.cross(x)
    return Matrix((x,y,z)).transposed().to_quaternion()
for path in sorted((ART/'Characters/Cast').glob('NPC*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    if rig.animation_data:
        for track in rig.animation_data.nla_tracks:track.mute=True
        action=bpy.data.actions.get(rig.name+'|Idle');rig.animation_data.action=action
        if action and action.slots:rig.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    def pos(n):return rig.matrix_world@rig.pose.bones[n].head
    right=pos('UpperArm.R')-pos('UpperArm.L');right.z=0;right.normalize();up=Vector((0,0,1));forward=up.cross(right)
    def local(p):return [p.dot(right),p.dot(forward),p.z]
    fingers=pos('Middle2.R')-pos('Wrist.R');normal=(pos('Index2.R')-pos('Pinky2.R')).cross(fingers).normalized()
    palm=pos('Middle2.R')-fingers.normalized()*.025+normal*.015
    wrist=(rig.matrix_world@rig.pose.bones['Wrist.R'].matrix).to_quaternion()
    offset=wrist.inverted()@(palm-pos('Wrist.R'));basis=wrist.inverted()@frame(fingers,normal)
    held=frame(forward,up)@basis.inverted()
    rigs.append(dict(name=path.stem,shoulder=local(pos('UpperArm.R')),spine=local(pos('Abdomen')),
        wrist_offset=local(held@offset),length=(pos('LowerArm.R')-pos('UpperArm.R')).length+(pos('Wrist.R')-pos('LowerArm.R')).length-.001))
(HERE/'rigs.json').write_text(json.dumps(rigs,indent=2)+'\n')
print('RIG',rigs[0])
surfaces={}
for path in sorted((ART/'City/Shops').glob('Local_*.fbx')):
    if path.stem=='Local_Escondite':continue
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
    rows=[]
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not any(token in obj.name for token in ('Cash','Register','Counter','Top','Tray','WindowGlass','Teller','Scanner','LaneBelt')):continue
        corners=[obj.matrix_world@Vector(c) for c in obj.bound_box]
        lo=[min(p[i] for p in corners) for i in range(3)];hi=[max(p[i] for p in corners) for i in range(3)]
        if hi[2]>.6 and lo[2]<1.7:rows.append(dict(name=obj.name,lo=lo,hi=hi))
    surfaces[path.stem]=rows
(HERE/'surfaces.json').write_text(json.dumps(surfaces,indent=2)+'\n')
print('EXTRACTED',len(rigs),'rigs',len(surfaces),'shops')
