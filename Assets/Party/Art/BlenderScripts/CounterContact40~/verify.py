"""Contacto con los FBX reales, sin estirar huesos. Previsualización Blender; no ejecuta Unity."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
H=Path(__file__).resolve().parent;ART=H.parents[1]
layouts=json.loads((ART/'City/Shops/shop_layouts.json').read_text())['shops']
contacts=json.loads((H/'contacts.json').read_text())
helper=ART/'BlenderScripts/HideoutB1Fix~/DoorReview36~/verify_contacts.py'
scope={'__file__':str(helper)};exec(helper.read_text().split('for path in sorted',1)[0],scope)
turn,frame=scope['turn'],scope['frame'];up=Vector((0,0,1));rows=[];bones_dump=[]

def rig_setup(path):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path))
    imported=set(bpy.data.objects)-before;rig=next(o for o in imported if o.type=='ARMATURE')
    for obj in imported:
        if obj.name.startswith('ShoppingBag_'):obj.hide_render=True
        if obj.animation_data:
            for t in obj.animation_data.nla_tracks:t.mute=True
            action=next((a for a in bpy.data.actions if a.name.startswith(obj.name.split('.')[0]+'|Idle')),None)
            obj.animation_data.action=action
            if action and action.slots:obj.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();rig.animation_data_clear()
    return rig,imported

def solve(rig,target,forward,above=False):
    b=rig.pose.bones
    def p(n):return rig.matrix_world@b[n].head
    def r(n):return (rig.matrix_world@b[n].matrix).to_quaternion()
    fingers=p('Middle2.R')-p('Wrist.R');normal=(p('Index2.R')-p('Pinky2.R')).cross(fingers).normalized()
    palm=p('Middle2.R')-fingers.normalized()*.025+normal*.015
    offset=r('Wrist.R').inverted()@(palm-p('Wrist.R'));local=r('Wrist.R').inverted()@frame(fingers,normal)
    rotation=frame(forward,-up if above else up)@local.inverted();goal=target-rotation@offset
    length=(p('UpperArm.R')-p('LowerArm.R')).length+(p('LowerArm.R')-p('Wrist.R')).length-.006
    direction=target-p('UpperArm.R');direction.z=0;axis=up.cross(direction.normalized())
    shoulder,spine=p('UpperArm.R'),p('Abdomen');angle=60
    for candidate in range(12,61,2):
        projected=spine+Quaternion(axis,math.radians(candidate))@(shoulder-spine)
        if (goal-projected).length<=length:angle=candidate;break
    free=r('UpperArm.L')
    turn(rig,b['Abdomen'],Quaternion(axis,math.radians(angle))@r('Abdomen'))
    turn(rig,b['UpperArm.L'],free)
    shoulder=p('UpperArm.R');elbow=p('LowerArm.R');hand=p('Wrist.R')
    a=(elbow-shoulder).length;bb=(hand-elbow).length;reach=goal-shoulder;direction=reach.normalized()
    d=max(abs(a-bb)+.001,min(a+bb-.001,reach.length));along=(a*a-bb*bb+d*d)/(2*d)
    bend=elbow-shoulder;bend-=direction*bend.dot(direction)
    new_elbow=shoulder+direction*along+bend.normalized()*math.sqrt(max(0,a*a-along*along))
    turn(rig,b['UpperArm.R'],(elbow-shoulder).rotation_difference(new_elbow-shoulder)@r('UpperArm.R'))
    turn(rig,b['LowerArm.R'],(p('Wrist.R')-p('LowerArm.R')).rotation_difference(goal-p('LowerArm.R'))@r('LowerArm.R'))
    turn(rig,b['Wrist.R'],rotation)
    return (p('Wrist.R')+rotation@offset-target).length,angle

actors=sorted((ART/'Characters/Cast').glob('NPC*.fbx'))
heights={}
for layout in layouts:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ART/'Props'/('Prop_'+layout['product']+'.fbx')))
    objs=[o for o in bpy.data.objects if o.type=='MESH' and (layout['kind']!='joyeria' or o.name.split('.')[0] in ('Ring','Gem'))]
    pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
    heights[layout['kind']]=max(p.z for p in pts)-min(p.z for p in pts)
(H/'product-heights.json').write_text(json.dumps(heights,indent=2)+'\n')
for path in actors:
    bpy.ops.wm.read_factory_settings(use_empty=True);rig,objects=rig_setup(path)
    b=rig.pose.bones
    def p(n):return rig.matrix_world@b[n].head
    right=p('UpperArm.R')-p('UpperArm.L');right.z=0;right.normalize();forward=up.cross(right)
    names=['Abdomen','UpperArm.R','LowerArm.R','Wrist.R','Index2.R','Middle2.R','Pinky2.R','Ring2.R','Thumb2.R']
    bones_dump.append(dict(name=path.stem,bones={n:[p(n).dot(right),p(n).z,p(n).dot(forward)] for n in names}))
    original={bone.name:bone.matrix_basis.copy() for bone in b}
    lateral=p('UpperArm.R').dot(right)
    for kind,data in contacts.items():
        for offset in (-.055,0,.055):
            for height,above in ((.12,False),(heights[kind] if kind!='banco' else 0,kind!='banco')):
                for bone in b:bone.matrix_basis=original[bone.name]
                bpy.context.view_layer.update()
                target=right*(lateral+offset)+forward*(data['width']/2+.255)+up*(data['center'][1]-.1+height)
                error,angle=solve(rig,target,forward,above)
                rows.append(dict(npc=path.stem,shop=kind,offset=offset,height=height,above=above,error=error,lean=angle))
(H/'bones.json').write_text(json.dumps(bones_dump,indent=2)+'\n')
(H/'reach-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('CONTACTS',len(rows),'MAX_ERROR',max(r['error'] for r in rows))
assert max(r['error'] for r in rows)<.025

models={'minimarket':'Minimarket','supermercado':'Supermercado','joyeria':'Joyeria','banco':'Banco','comida':'Comida','ropa':'Ropa'}
for i,layout in enumerate(layouts):
    kind=layout['kind'];data=contacts[kind]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ART/'City/Shops'/('Local_'+models[kind]+'.fbx')))
    center=Vector((-data['center'][0],-data['center'][2],data['center'][1]));normal=Vector((-data['normal'][0],-data['normal'][2],0));side=up.cross(normal)
    for obj in list(bpy.data.objects):
        if obj.type!='MESH':continue
        points=[obj.matrix_world@Vector(c) for c in obj.bound_box]
        lo=Vector(tuple(min(p[k] for p in points) for k in range(3)));hi=Vector(tuple(max(p[k] for p in points) for k in range(3)))
        if obj.name.startswith('TellerGlass'):
            for v in obj.data.vertices:
                world=obj.matrix_world@v.co;world.z=hi.z-(hi.z-world.z)*(hi.z-1.38)/(hi.z-lo.z);v.co=obj.matrix_world.inverted()@world
        if obj.name.startswith('TellerSlot'):
            for v in obj.data.vertices:
                world=obj.matrix_world@v.co;world.y=6.35+(world.y-6.08)*(.65/.3);v.co=obj.matrix_world.inverted()@world
        if ((lo+hi)/2-center).length>4 or obj.name.startswith(('Roof','Ceiling','Wall','Store','Pillar','Door','Parapet')):obj.hide_render=True
    for customer in (True,False):
        rig,objects=rig_setup(actors[(i+(0 if customer else 4))%len(actors)])
        b=rig.pose.bones
        def p(n):return rig.matrix_world@b[n].head
        right=p('UpperArm.R')-p('UpperArm.L');right.z=0;right.normalize();forward=up.cross(right)
        facing=-normal if customer else normal
        rotation=forward.rotation_difference(facing)
        root=bpy.data.objects.new('Cliente' if customer else 'Vendedor',None);bpy.context.scene.collection.objects.link(root)
        for obj in objects:
            if obj.parent is None:obj.parent=root
        root.rotation_mode='QUATERNION';root.rotation_quaternion=rotation
        stand=center+normal*(data['width']/2+.255)*(1 if customer else -1);stand.z=.1
        root.location=stand;bpy.context.view_layer.update()
        actor_right=up.cross(facing);root.location+=actor_right*(center-root.location-(p('UpperArm.R')-root.location)).dot(actor_right)
        bpy.context.view_layer.update()
        if not customer:
            target=center+up*(.08+(heights[kind] if kind!='banco' else 0))
            solve(rig,target,facing,kind!='banco')
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ART/'Props'/('Prop_'+layout['product']+'.fbx')))
    objects=set(bpy.data.objects)-before
    for obj in objects:
        if kind=='joyeria' and obj.type=='MESH' and obj.name.split('.')[0] not in ('Ring','Gem'):obj.hide_render=True
    prop=bpy.data.objects.new('Producto_en_mano',None);bpy.context.scene.collection.objects.link(prop)
    for obj in objects:
        if obj.parent is None:obj.parent=prop
    pts=[o.matrix_world@Vector(c) for o in objects if o.type=='MESH' and not o.hide_render for c in o.bound_box]
    lo=Vector(tuple(min(p[k] for p in pts) for k in range(3)));hi=Vector(tuple(max(p[k] for p in pts) for k in range(3)))
    prop.location=center+up*.08-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    scene=bpy.context.scene
    camera=bpy.data.objects.new('Camara',bpy.data.cameras.new('Camara'));scene.collection.objects.link(camera);scene.camera=camera
    camera.location=center+side*3+normal*2+up*1.4
    camera.rotation_euler=(center+up*.2-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.3
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Fondo');scene.world.color=(.22,.24,.27)
    scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(H/(kind+'.png'));bpy.ops.render.render(write_still=True)
    if kind=='banco':bpy.ops.wm.save_as_mainfile(filepath=str(H/'Contactos_Banco.blend'))
