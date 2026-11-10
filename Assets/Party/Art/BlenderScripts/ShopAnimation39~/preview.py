"""Muestras de apoyo e inspección con los modelos existentes. Render Blender, no captura de Play."""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector, Quaternion, Matrix
HERE=Path(__file__).resolve().parent;ART=HERE.parents[1]
profiles=json.loads((HERE/'profiles.json').read_text())
layouts=json.loads((ART/'City/Shops/shop_layouts.json').read_text())['shops']
helper=ART/'BlenderScripts/HideoutB1Fix~/DoorReview36~/verify_contacts.py'
scope={'__file__':str(helper)};exec(helper.read_text().split('for path in sorted',1)[0],scope)
turn,frame=scope['turn'],scope['frame'];report=[]
actors=sorted((ART/'Characters/Cast').glob('NPC*.fbx'))
for i,layout in enumerate(layouts):
    kind=layout['kind'];profile=profiles[kind]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(actors[i%len(actors)]))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    for obj in bpy.data.objects:
        if obj.name.startswith('ShoppingBag_'):obj.hide_render=True
        if obj.animation_data:
            for track in obj.animation_data.nla_tracks:track.mute=True
            action=bpy.data.actions.get(obj.name+'|Idle');obj.animation_data.action=action
            if action and action.slots:obj.animation_data.action_slot=action.slots[0]
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();bones=rig.pose.bones
    rig.animation_data_clear() # El render no debe volver a evaluar Idle sobre la pose de revisión.
    def pos(n):return rig.matrix_world@bones[n].head
    def rot(b):return (rig.matrix_world@b.matrix).to_quaternion()
    up=Vector((0,0,1));right=pos('UpperArm.R')-pos('UpperArm.L');right.z=0;right.normalize();forward=up.cross(right)
    upper,lower,wrist,spine=[bones[n] for n in ('UpperArm.R','LowerArm.R','Wrist.R','Abdomen')]
    fingers=pos('Middle2.R')-pos('Wrist.R');normal=(pos('Index2.R')-pos('Pinky2.R')).cross(fingers).normalized()
    palm=pos('Middle2.R')-fingers.normalized()*.025+normal*.015
    offset=rot(wrist).inverted()@(palm-pos('Wrist.R'));local=rot(wrist).inverted()@frame(fingers,normal)
    target=right*pos('UpperArm.R').dot(right)+forward*.28+up*(1.06+profile['inspect'])
    direction=target-pos('UpperArm.R');direction.z=0
    turn(rig,spine,Quaternion(up.cross(direction.normalized()),math.radians(12))@rot(spine))
    rotation=frame(forward,up)@local.inverted();goal=target-rotation@offset
    shoulder=pos('UpperArm.R');elbow=pos('LowerArm.R');hand=pos('Wrist.R')
    a=(elbow-shoulder).length;b=(hand-elbow).length;reach=goal-shoulder;direction=reach.normalized()
    d=max(abs(a-b)+.001,min(a+b-.001,reach.length));along=(a*a-b*b+d*d)/(2*d)
    bend=elbow-shoulder;bend-=direction*bend.dot(direction)
    new_elbow=shoulder+direction*along+bend.normalized()*math.sqrt(max(0,a*a-along*along))
    turn(rig,upper,(elbow-shoulder).rotation_difference(new_elbow-shoulder)@rot(upper))
    turn(rig,lower,(pos('Wrist.R')-pos('LowerArm.R')).rotation_difference(goal-pos('LowerArm.R'))@rot(lower))
    turn(rig,wrist,rotation)
    actual=pos('Wrist.R')+rotation@offset
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ART/'Props'/('Prop_'+layout['product']+'.fbx')))
    objects=set(bpy.data.objects)-before
    if kind=='joyeria':
        for obj in objects:
            if obj.type=='MESH' and obj.name.split('.')[0] not in ('Ring','Gem'):obj.hide_render=True
    root=bpy.data.objects.new('Objeto_en_palma',None);scene.collection.objects.link(root)
    for obj in objects:
        if obj.parent is None:obj.parent=root
    if kind=='banco':root.scale=(.6,.6,.6)
    root.rotation_mode='QUATERNION';root.rotation_quaternion=Quaternion(forward,math.radians(profile['tilt']))
    bpy.context.view_layer.update()
    points=[obj.matrix_world@Vector(corner) for obj in objects if obj.type=='MESH' and not obj.hide_render for corner in obj.bound_box]
    lo=Vector(tuple(min(p[k] for p in points) for k in range(3)));hi=Vector(tuple(max(p[k] for p in points) for k in range(3)))
    root.location=actual-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    camera=bpy.data.objects.new('Camara',bpy.data.cameras.new('Camara'));scene.collection.objects.link(camera);scene.camera=camera
    camera.location=forward*2.1+right*1.7+up*1.7
    camera.rotation_euler=(up*1.1-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1.65
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Fondo');scene.world.color=(.22,.24,.27)
    scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(HERE/(kind+'.png'));bpy.ops.render.render(write_still=True)
    report.append(dict(shop=kind,npc=actors[i%len(actors)].stem,palm_error=(actual-target).length,preview=str(HERE/(kind+'.png'))))
(HERE/'preview-results.json').write_text(json.dumps(report,indent=2)+'\n')
print('PREVIEW',len(report),'max palm error',max(row['palm_error'] for row in report))
