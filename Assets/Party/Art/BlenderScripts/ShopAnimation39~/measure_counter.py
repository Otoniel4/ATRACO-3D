"""Alcance del cajero en los seis mostradores con los FBX reales; sin Unity."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix
HERE=Path(__file__).resolve().parent;ART=HERE.parents[1]
profiles=json.loads((HERE/'profiles.json').read_text())
shops=json.loads((ART/'City/Shops/shop_layouts.json').read_text())['shops']
helpers=ART/'BlenderScripts/HideoutB1Fix~/DoorReview36~/verify_contacts.py'
scope={'__file__':str(helpers)};exec(helpers.read_text().split('for path in sorted',1)[0],scope)
turn,frame=scope['turn'],scope['frame'];results=[]
for path in sorted((ART/'Characters/Cast').glob('NPC*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    for obj in bpy.data.objects:
        if obj.animation_data:
            for track in obj.animation_data.nla_tracks:track.mute=True
            action=bpy.data.actions.get(obj.name+'|Idle');obj.animation_data.action=action
            if action and action.slots:obj.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    bones=rig.pose.bones
    def pos(n):return rig.matrix_world@bones[n].head
    def rot(b):return (rig.matrix_world@b.matrix).to_quaternion()
    up=Vector((0,0,1));right=pos('UpperArm.R')-pos('UpperArm.L');right.z=0;right.normalize();forward=up.cross(right)
    rest={b.name:b.matrix_basis.copy() for b in bones}
    for shop in shops:
        kind=shop['kind'];profile=profiles[kind]
        cashier=Vector((*shop['cashier'],.1));counter=Vector((*shop['counter'],.1));scan=Vector(shop['scan'])
        toward=(counter-cashier).normalized();side=up.cross(toward)
        # Las poses se evalúan en el marco de cada cuerpo, sin depender del giro del edificio.
        points={'drop':scan+toward*.15+side*.22+up*.03,'reader':scan+side*profile['sweep']+up*profile['inspect'],
            'bag':scan+toward*.15-side*.25+up*.03,'handoff':scan+toward*.05+up*.2,'till':Vector(shop['till'])}
        if kind=='banco':points.update(drop=scan+up*.03,bag=scan+up*.03,handoff=scan+up*.05)
        for who in ('cashier','customer'):
            home=cashier+toward*.28 if who=='cashier' else counter+(scan-counter).xy.to_3d().normalized()*.32
            face=toward if who=='cashier' else (scan-counter).xy.to_3d().normalized()
            lateral=face.cross(up)
            for label,point in points.items():
                if who=='customer' and label in ('reader','till'):continue
                for b in bones:b.matrix_basis=rest[b.name]
                bpy.context.view_layer.update()
                delta=point-home;target=right*delta.dot(lateral)+forward*delta.dot(face)+up*delta.z
                upper,lower,wrist,spine=[bones[n] for n in ('UpperArm.R','LowerArm.R','Wrist.R','Abdomen')]
                fingers=pos('Middle2.R')-pos('Wrist.R');normal=(pos('Index2.R')-pos('Pinky2.R')).cross(fingers).normalized()
                palm=pos('Middle2.R')-fingers.normalized()*.025+normal*.015
                offset=rot(wrist).inverted()@(palm-pos('Wrist.R'));local=rot(wrist).inverted()@frame(fingers,normal)
                direction=target-pos('UpperArm.R');direction.z=0
                turn(rig,spine,Quaternion(up.cross(direction.normalized()),math.radians(12))@rot(spine))
                rotation=frame(forward,up)@local.inverted();goal=target-rotation@offset
                a=(pos('LowerArm.R')-pos('UpperArm.R')).length;b=(pos('Wrist.R')-pos('LowerArm.R')).length
                error=max(0,(goal-pos('UpperArm.R')).length-(a+b-.001))
                results.append(dict(npc=path.stem,shop=kind,who=who,point=label,error=error))
(HERE/'counter-reach.json').write_text(json.dumps(results,indent=2)+'\n')
for shop in shops:
    rows=[r for r in results if r['shop']==shop['kind']]
    print(shop['kind'],[(who,round(max(r['error'] for r in rows if r['who']==who),3)) for who in ('cashier','customer')])
