"""Previsualiza los agarres aprobados en una escena independiente del Blender conectado."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
ROOT=Path('C:/Users/Alain/Atraco3D'); ART=ROOT/'Assets/Party/Art'; OUT=ART/'BlenderScripts/ShopObjectsR44~'
scene=bpy.data.scenes.new('R44_Revision_Agarres');bpy.context.window.scene=scene
helper=ART/'BlenderScripts/CounterContact40~/verify.py'
scope={'__file__':str(helper)};exec(helper.read_text().split('actors=')[0],scope)
rig_setup=scope['rig_setup'];turn=scope['turn'];frame=scope['frame']
up=Vector((0,0,1))
def cv(p):return Vector((p['x'],-p['z'],p['y']))
def pose(rig,target,fwd,normal,curl,left=False,lean=True):
    b=rig.pose.bones;s='.L' if left else '.R'
    def p(n):return rig.matrix_world@b[n].head
    def r(n):return (rig.matrix_world@b[n].matrix).to_quaternion()
    wrist='Wrist'+s;upper='UpperArm'+s;lower='LowerArm'+s
    fingers=p('Middle2'+s)-p(wrist);outward=(p('Index2'+s)-p('Pinky2'+s)).cross(fingers).normalized()
    if left:outward=-outward
    palm=p('Middle2'+s)-fingers.normalized()*.025+outward*.015
    offset=r(wrist).inverted()@(palm-p(wrist));local=r(wrist).inverted()@frame(fingers,outward)
    rotation=frame(fwd,normal)@local.inverted();goal=target-rotation@offset
    if lean:
        length=(p(upper)-p(lower)).length+(p(lower)-p(wrist)).length-.006
        direction=target-p(upper);direction.z=0;axis=up.cross(direction.normalized())
        shoulder=p(upper);spine=p('Abdomen');best=(float('inf'),12)
        for candidate in range(12,61,2):
            d=(goal-spine-Quaternion(axis,math.radians(candidate))@(shoulder-spine)).length
            if d<best[0]:best=(d,candidate)
            if d<=length:break
        free=r('UpperArm.L');turn(rig,b['Abdomen'],Quaternion(axis,math.radians(best[1]))@r('Abdomen'));turn(rig,b['UpperArm.L'],free)
    shoulder=p(upper);elbow=p(lower);hand=p(wrist);a=(elbow-shoulder).length;bb=(hand-elbow).length
    reach=goal-shoulder;direction=reach.normalized();d=max(abs(a-bb)+.001,min(a+bb-.001,reach.length));along=(a*a-bb*bb+d*d)/(2*d)
    bend=elbow-shoulder;bend-=direction*bend.dot(direction)
    if bend.length<.0001:bend=Vector((-.45 if left else .45,0,-1));bend-=direction*bend.dot(direction)
    e=shoulder+direction*along+bend.normalized()*math.sqrt(max(0,a*a-along*along))
    turn(rig,b[upper],(elbow-shoulder).rotation_difference(e-shoulder)@r(upper))
    turn(rig,b[lower],(p(wrist)-p(lower)).rotation_difference(goal-p(lower))@r(lower));turn(rig,b[wrist],rotation)
    for name in ('Index','Middle','Ring','Pinky','Thumb'):
        for n in (2,3):
            bone=b.get(name+str(n)+s);next_b=b.get(name+str(n+1)+s)
            if not bone:continue
            direction=rig.matrix_world@(next_b.head if next_b else bone.head)-rig.matrix_world@(bone.head if next_b else bone.parent.head)
            inward=p('Middle2'+s)-p(name+str(n)+s) if name=='Thumb' else rotation@local@Vector((0,1,0))
            axis=direction.cross(inward).normalized()
            turn(rig,bone,Quaternion(axis,math.radians((16 if name=='Thumb' else 22)*curl))@r(bone.name))
    return (p(wrist)+rotation@offset-target).length

catalog=json.loads((ART/'Props/ShopObjects/catalog.json').read_text())['items']
actors=sorted((ART/'Characters/Cast').glob('NPC*.fbx'))
camera=bpy.data.objects.new('R44_GripCamera',bpy.data.cameras.new('R44_GripCamera'));scene.collection.objects.link(camera);scene.camera=camera
camera.data.type='ORTHO';camera.data.ortho_scale=.65
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=800;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
results=[]
for i,data in enumerate(catalog):
    rig,objects=rig_setup(actors[i%2]);root=bpy.data.objects.new('Agarre_'+data['id'],None);scene.collection.objects.link(root)
    for obj in objects:
        if obj.parent is None:obj.parent=root
    b=rig.pose.bones
    def p(n):return rig.matrix_world@b[n].head
    right=p('UpperArm.R')-p('UpperArm.L');right.z=0;right.normalize();forward=up.cross(right)
    root.rotation_mode='QUATERNION';root.rotation_quaternion=forward.rotation_difference(Vector((0,1,0)))
    root.location=(i%6*2,i//6*2,0);bpy.context.view_layer.update()
    grip=cv(data['right']);base=Vector(root.location)+Vector((0 if data['twoHands'] else (p('UpperArm.R')-root.location).x-grip.x,.65,1.1))
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ART/'Props/ShopObjects'/(data['id']+'.fbx')))
    imported=set(bpy.data.objects)-before
    item=bpy.data.objects.new('Producto_'+data['id'],None);scene.collection.objects.link(item)
    for obj in imported:
        if obj.parent is None:obj.parent=item
    item.location=base;bpy.context.view_layer.update()
    fingers=cv(data['fingers']);normal=cv(data['normal'])
    if fingers.y<0:fingers=-fingers
    error=pose(rig,base+grip,fingers,normal,data['curl'])
    if data['twoHands']:
        lf=cv(data['leftFingers']);ln=cv(data['leftNormal'])
        if lf.y<0:lf=-lf
        error=max(error,pose(rig,base+cv(data['left']),lf,ln,data['curl'],True,False))
    results.append(dict(id=data['id'],palm_error=error))
    center=base+Vector((0,0,.07));camera.location=center+Vector((.5,-.75,.4));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/('Agarre_'+data['id']+'.png'));bpy.ops.render.render(write_still=True)
(OUT/'visual-grips.json').write_text(json.dumps(results,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Agarres_R44.blend'))
print('R44_VIEW',len(results),'max error',max(r['palm_error'] for r in results))
