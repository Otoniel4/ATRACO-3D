"""Revisión del agarre sobre los FBX reales, sin modificar modelos ni abrir Unity."""
from pathlib import Path
import math
import json
import bpy
from mathutils import Vector, Matrix, Quaternion, Euler

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]

def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    return list(set(bpy.data.objects)-before)

def frame(forward, normal):
    z = forward.normalized()
    x = normal.cross(z).normalized()
    y = z.cross(x).normalized()
    return Matrix((x,y,z)).transposed().to_quaternion()

def turn_bone(arm, bone, rotation):
    world = arm.matrix_world @ bone.matrix
    bone.matrix = arm.matrix_world.inverted() @ Matrix.LocRotScale(world.translation, rotation, world.to_scale())
    bpy.context.view_layer.update()

def solve(arm, side, palm_offset, target, wrist_rotation, bend):
    upper, lower, wrist = [arm.pose.bones[n+'.'+side] for n in ('UpperArm','LowerArm','Wrist')]
    mw = arm.matrix_world
    shoulder, elbow, hand = [mw@b.head for b in (upper,lower,wrist)]
    goal = target-wrist_rotation@palm_offset
    a,b=(elbow-shoulder).length,(hand-elbow).length
    direction=(goal-shoulder).normalized()
    distance=max(abs(a-b)+.001,min(a+b-.001,(goal-shoulder).length))
    along=(a*a-b*b+distance*distance)/(2*distance)
    outward=(bend-direction*bend.dot(direction)).normalized()
    new_elbow=shoulder+direction*along+outward*math.sqrt(max(0,a*a-along*along))
    q=(elbow-shoulder).rotation_difference(new_elbow-shoulder)
    turn_bone(arm,upper,q@(mw@upper.matrix).to_quaternion())
    elbow,hand=mw@lower.head,mw@wrist.head
    q=(hand-elbow).rotation_difference(goal-elbow)
    turn_bone(arm,lower,q@(mw@lower.matrix).to_quaternion())
    turn_bone(arm,wrist,wrist_rotation)
    return mw@wrist.head+wrist_rotation@palm_offset

def prepare_hand(arm,side):
    mw=arm.matrix_world
    pos=lambda name: mw@arm.pose.bones[name+'.'+side].head
    wrist=arm.pose.bones['Wrist.'+side]
    forward=pos('Middle2')-pos('Wrist')
    normal=(pos('Index2')-pos('Pinky2')).cross(forward)*(1 if side=='R' else -1)
    normal.normalize()
    local=(mw@wrist.matrix).to_quaternion().inverted()@frame(forward,normal)
    joints=[]
    for finger in ('Index','Middle','Ring','Pinky','Thumb'):
        thumb=finger=='Thumb'
        for number in range(1 if thumb else 2,4 if thumb else 5):
            bone=arm.pose.bones[f'{finger}{number}.{side}']
            nxt=arm.pose.bones.get(f'{finger}{number+1}.{side}')
            direction=mw@nxt.head-mw@bone.head if nxt else mw@bone.head-mw@bone.parent.head
            inward=pos('Middle2')-mw@bone.head if thumb else normal
            axis=(mw@bone.matrix).to_quaternion().inverted()@direction.cross(inward).normalized()
            degrees=(18 if number==1 else 35) if thumb else (65 if number==2 else 85 if number==3 else 45)
            joints.append((bone,bone.matrix_basis.to_quaternion(),axis,degrees,finger=='Index'))
    return local,joints

def run(role='Player01_Thief', running=False, capture=True):
    scene=bpy.data.scenes.new('Agarre_Corregido')
    bpy.context.window.scene=scene
    body=load(ART/'Characters/Cast'/f'{role}.fbx')
    arm=next(o for o in body if o.type=='ARMATURE')
    scene.frame_set(1)
    frozen={b.name:b.matrix.copy() for b in arm.pose.bones}
    arm.animation_data_clear()
    for b in arm.pose.bones:
        b.matrix=frozen[b.name]
        bpy.context.view_layer.update()
    for o in body:
        if o.name.startswith('ShoppingBag'): o.hide_set(True)
    grip=next(o for o in body if o.name.startswith('Grip_R6'))
    mw=arm.matrix_world
    offsets={}
    frames={}
    curls={}
    for side in ('R','L'):
        wrist=arm.pose.bones['Wrist.'+side]
        world=mw@wrist.matrix
        frames[side],curls[side]=prepare_hand(arm,side)
        middle=mw@arm.pose.bones['Middle2.'+side].head
        forward=(middle-world.translation).normalized()
        normal=(world.to_quaternion()@frames[side])@Vector((0,1,0))
        palm=middle-forward*.025+normal*.015
        offsets[side]=world.to_quaternion().inverted()@(palm-world.translation)
    weapon=load(ART/'Weapons/Weapon_Pistol.fbx')
    root=next(o for o in weapon if o.parent is None)
    grips={side:next(o for o in weapon if o.name.split('.')[0]=='Grip_'+side) for side in ('R','L')}
    chest=mw@arm.pose.bones['Chest'].head
    rotation=Euler((math.radians(55 if running else 14),0,math.radians(-8 if running else 0)), 'ZXY').to_quaternion()
    root.rotation_mode='QUATERNION';root.rotation_quaternion=rotation
    bpy.context.view_layer.update()
    target=chest+Vector((-.12,-.24,-.24) if running else (-.05,-.34,-.2))
    root.location+=target-grips['R'].matrix_world.translation
    bpy.context.view_layer.update()
    errors={}
    for side in ('R','L'):
        f=Vector((0,-1,0));n=Vector((1 if side=='R' else -1,0,0))
        desired=rotation@frame(f,n)@frames[side].inverted()
        target=grips[side].matrix_world.translation
        palm=solve(arm,side,offsets[side],target,desired,Vector((-.45 if side=='R' else .45,0,-1)))
        errors[side]=(palm-target).length
        if side=='R':root.location+=palm-target
        for bone,rest,axis,degrees,index in curls[side]:
            bone.rotation_mode='QUATERNION'
            bone.rotation_quaternion=rest@Quaternion(axis,math.radians(degrees*(.08 if side=='R' and index else 1)))
            bpy.context.view_layer.update()
    camera=bpy.data.objects.new('Camara_Agarre',bpy.data.cameras.new('Camara_Agarre'))
    scene.collection.objects.link(camera);scene.camera=camera
    camera.data.lens=52
    scene.render.resolution_x,scene.render.resolution_y=1100,1000
    scene.render.resolution_percentage=100
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
    area.spaces.active.region_3d.view_perspective='CAMERA'
    area.spaces.active.overlay.show_overlays=False
    area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
    region=next(r for r in area.regions if r.type=='WINDOW')
    shots=[('frente',(-.8,-1.5,.15)),('manos',(-.45,-.72,.02)),('lateral',(-1.4,-.4,.1)),('apoyo',(.65,-.95,.15))] if capture else []
    for name,offset in shots:
        aim=chest+Vector((0,-.25,-.15))
        camera.location=aim+Vector(offset)
        camera.rotation_euler=(aim-camera.location).to_track_quat('-Z','Y').to_euler()
        prefix='' if role=='Player01_Thief' and not running else role+('_carrera_' if running else '_')
        scene.render.filepath=str(HERE/(prefix+name+'.png'))
        with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    print('ERRORES_PALMA_METROS',role,running,errors)
    return dict(role=role, running=running, palm_errors_m=errors)

if __name__ == '__main__':
    results=[run(role,running,capture=role=='Player01_Thief') for role in
             ('Player01_Thief','Player02_Hacker','Player03_Distractor','Player04_Muscle') for running in (False,True)]
    assert max(e for r in results for e in r['palm_errors_m'].values()) < .001
    (HERE/'contact-results.json').write_text(json.dumps(results,indent=2)+'\n')
