"""Reimporta cada pieza nueva, los diez civiles, el distrito y el FBX estático del mapa."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
catalog=json.loads((BASE/'prop_catalog.json').read_text());characters=json.loads((BASE/'animation_catalog.json').read_text())
props=[];actors=[]
for row in catalog:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(BASE/'export/Props'/(row['id']+'.fbx')))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1,row['id']
    obj=meshes[0];positions=[obj.matrix_world@v.co for v in obj.data.vertices]
    lo=[min(v[k] for v in positions) for k in range(3)];hi=[max(v[k] for v in positions) for k in range(3)]
    error=max(abs(lo[k]-row['bounds_min'][k]) for k in range(3));error=max(error,max(abs(hi[k]-row['bounds_max'][k]) for k in range(3)))
    assert error<.0001,(row['id'],error)
    assert not any(o.type in ['CAMERA','LIGHT'] for o in bpy.context.scene.objects)
    props.append({'id':row['id'],'bounds_error_m':error})
print('PROP_ROUNDTRIP_PASSED',len(props),flush=True)
for row in characters:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(BASE/'export/Characters'/(row['id']+'.fbx')))
    scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==21,row['id']
    actions={mode:next((a for a in bpy.data.actions if a.name.endswith('|'+mode)),None) for mode in row['clips']};assert all(actions.values()),row['id']
    rig.animation_data_create();rig.animation_data.action=actions['Walk'];rig.data.pose_position='POSE'
    if actions['Walk'].slots:rig.animation_data.action_slot=actions['Walk'].slots[0]
    scene.frame_set(1);bpy.context.view_layer.update();first={b.name:b.matrix.copy() for b in rig.pose.bones}
    scene.frame_set(7);bpy.context.view_layer.update();motion=max((rig.pose.bones[n].head-first[n].translation).length for n in ['LeftFoot','RightFoot','LeftLowerLeg','RightLowerLeg'])
    assert motion>.02,(row['id'],motion)
    scene.frame_set(25);bpy.context.view_layer.update();loop=max(abs(rig.pose.bones[n].matrix[r][c]-matrix[r][c]) for n,matrix in first.items() for r in range(4) for c in range(4))
    assert loop<.005,(row['id'],loop)
    unweighted=0;weight_error=0
    for obj in scene.objects:
        if obj.type!='MESH' or not any(m.type=='ARMATURE' for m in obj.modifiers):continue
        for v in obj.data.vertices:
            total=sum(g.weight for g in v.groups);unweighted+=total<.001;weight_error=max(weight_error,abs(total-1))
    assert unweighted==0 and weight_error<.025,(row['id'],unweighted,weight_error)
    actors.append({'id':row['id'],'bones':21,'clips':len(actions),'walk_motion_m':motion,'loop_matrix_error':loop,'unweighted_vertices':unweighted,'weight_error':weight_error})
print('ANIMATED_CIVILIANS_ROUNDTRIP_PASSED',len(actors),flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(BASE/'export/District_CityLife_R5.fbx'),colors_type='LINEAR')
names={o.name for o in bpy.context.scene.objects}
for shop in ['Minimarket','Clothing','Restaurant']:
    assert 'Door_'+shop+'_L' in names and 'Door_'+shop+'_R' in names,shop
assert not any(o.type in ['LIGHT','CAMERA','ARMATURE'] for o in bpy.context.scene.objects)
print('DISTRICT_ROUNDTRIP_PASSED',flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(BASE/'export/Map/Villa_Alarma_Ciudad_R5.fbx'),colors_type='LINEAR')
lo=[math.inf]*3;hi=[-math.inf]*3;wind_meshes=0
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    if obj.data.color_attributes:wind_meshes+=1
    for corner in obj.bound_box:
        p=obj.matrix_world@Vector(corner)
        for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
assert all(abs(hi[i]-lo[i]-4000)<.03 for i in [0,1]),(lo,hi)
assert not any(o.type in ['LIGHT','CAMERA','ARMATURE'] for o in bpy.context.scene.objects)
report={'props_reimported':props,'characters_reimported':actors,'district_doors_present':True,'full_map_xy_m':[hi[0]-lo[0],hi[1]-lo[1]],
        'full_map_wind_meshes':wind_meshes,'unity_play_tested':False,'passed':True}
(BASE/'fbx_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CITY_LIFE_FBX_VALIDATED',len(props),len(actors),report['full_map_xy_m'],flush=True)
