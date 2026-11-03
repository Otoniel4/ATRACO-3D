"""Reimporta los 18 FBX y comprueba rig, escala, pesos y poses de diagnóstico."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
required={'Hips','Spine','Chest','Neck','Head'}
for side in ['Left','Right']:required.update(side+n for n in ['Shoulder','UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot','Toes'])
visual={'NPC01_Bomber','NPC03_Tourist','NPC11_SecurityMale','NPC14_PoliceFemale','Player03_Distractor','Player04_Muscle'}
results=[]

def coordinates(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    data=[evaluated.matrix_world@v.co for v in mesh.vertices];evaluated.to_mesh_clear();return data

def pose_render(identifier,height):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE_NEXT';scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('PoseWorld');scene.world.use_nodes=True
    node=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');node.inputs['Color'].default_value=(.16,.18,.20,1);node.inputs['Strength'].default_value=.5
    for name,pos,energy in [('Key',(2,-3,4),250),('Fill',(-3,-1,2),150),('Back',(0,3,3),220)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.size=4
        obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=pos
        obj.rotation_euler=(Vector((0,0,height/2))-obj.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('PoseCamera');camera=bpy.data.objects.new('PoseCamera',data);scene.collection.objects.link(camera);scene.camera=camera
    data.type='ORTHO';data.ortho_scale=height*1.25
    center=Vector((0,0,height/2));camera.location=center+Vector((-4,-7,1.5));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    folder=BASE/'pose_checks';folder.mkdir(exist_ok=True)
    scene.render.resolution_x=650;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(folder/(identifier+'.png'))
    bpy.ops.render.render(write_still=True)

for entry in manifest['characters']:
    identifier=entry['id'];bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(BASE/'fbx'/(identifier+'.fbx')))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    assert len(rigs)==1 and len(meshes)==entry['meshes'],identifier
    rig=rigs[0];assert set(rig.data.bones.keys())==required,identifier
    assert not any(o.type in {'CAMERA','LIGHT'} for o in bpy.context.scene.objects)
    rest={o.name:coordinates(o) for o in meshes};points=[v for values in rest.values() for v in values]
    height=max(v.z for v in points)-min(v.z for v in points);ground=min(v.z for v in points)
    assert abs(height-entry['height_m'])<.003 and abs(ground)<.003,(identifier,height,ground)
    unweighted=0;max_weight_error=0
    for obj in meshes:
        assert any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers),obj.name
        for v in obj.data.vertices:
            total=sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in required)
            unweighted+=total<1e-6;max_weight_error=max(max_weight_error,abs(total-1))
    assert not unweighted and max_weight_error<.0002,(identifier,unweighted,max_weight_error)
    original={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
    head=rig.pose.bones['Head'];head.rotation_mode='XYZ';head.rotation_euler.z=math.radians(20)
    bpy.context.view_layer.update()
    deform=rig.matrix_world@head.matrix@head.bone.matrix_local.inverted()@rig.matrix_world.inverted()
    head_error=0
    for obj in meshes:
        if obj.name.endswith(('_Head','_Face','_Hair')):
            error=max((a-deform@b).length for a,b in zip(coordinates(obj),rest[obj.name]));head_error=max(head_error,error)
    assert head_error<1e-5,(identifier,head_error)
    for bone in rig.pose.bones:bone.matrix_basis=original[bone.name]
    for name,degrees in [('LeftUpperArm',12),('LeftLowerArm',35),('LeftUpperLeg',10),('LeftLowerLeg',30)]:
        bone=rig.pose.bones[name];bone.rotation_mode='XYZ';bone.rotation_euler.x=math.radians(degrees)
    bpy.context.view_layer.update();maximum=0
    for obj in meshes:
        moved=coordinates(obj)
        distances=[(a-b).length for a,b in zip(moved,rest[obj.name])]
        assert all(math.isfinite(d) for d in distances)
        maximum=max(maximum,max(distances))
    assert .01<maximum<height*.9,(identifier,maximum)
    if identifier in visual:pose_render(identifier,height)
    for bone in rig.pose.bones:bone.matrix_basis=original[bone.name]
    bpy.context.view_layer.update()
    recovery=max(max((a-b).length for a,b in zip(coordinates(obj),rest[obj.name])) for obj in meshes)
    assert recovery<1e-5,(identifier,recovery)
    results.append({'id':identifier,'fbx_reimport_passed':True,'height_m':height,'ground_z':ground,
                    'meshes':len(meshes),'bones':21,'vertices_without_weights':unweighted,
                    'maximum_weight_error':max_weight_error,'head_turn_error_m':head_error,
                    'limb_pose_max_displacement_m':maximum,'rest_recovery_error_m':recovery})
    print('CAST_VALIDATED',identifier,flush=True)
(BASE/'validation.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'validated_count':len(results),
    'characters':results,'unity_avatars_verified':False,'animation_clips_created':False},indent=2),encoding='utf-8')
print('CAST_VALIDATION_SUCCESS',len(results),flush=True)
