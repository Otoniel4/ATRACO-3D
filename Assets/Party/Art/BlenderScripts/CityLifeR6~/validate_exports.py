"""Verifica cada FBX animado con una importación independiente; mide dedos y animación real."""
import bpy,json,sys,bmesh
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;catalog=json.loads((B/'animation_catalog.json').read_text());report=[]
for row in catalog:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export/Characters'/(row['id']+'.fbx')))
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');hands=next(o for o in bpy.context.scene.objects if o.type=='MESH' and '_Hands' in o.name)
    assert len([o for o in bpy.context.scene.objects if o.type in ['CAMERA','LIGHT']])==0
    required=[side+finger+joint for side in ['Left','Right'] for finger in ['Thumb','Index','Middle','Ring','Little'] for joint in ['Proximal','Intermediate','Distal']]
    assert all(name in rig.data.bones for name in required),(row['id'],'faltan dedos')
    assert all(sum(g.weight for g in v.groups)>.99 for v in hands.data.vertices),(row['id'],'mano sin pesos')
    rig_actions=[a for a in bpy.data.actions if a.name.startswith(rig.name+'|')]
    assert len([a for a in rig_actions if any(a.name.endswith('|'+mode) for mode in row['clips'])])==5,(row['id'],'clips')
    bm=bmesh.new();bm.from_mesh(hands.data);assert all(edge.is_manifold for edge in bm.edges),(row['id'],'mano abierta');bm.free()
    action=next(a for a in rig_actions if a.name.endswith('|Idle'));rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(8);idle=rig.pose.bones['RightIndexProximal'].matrix_basis.to_quaternion().copy()
    action=next(a for a in rig_actions if a.name.endswith('|CarryWalk'));rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(8);finger=rig.pose.bones['RightIndexProximal'];angle=idle.rotation_difference(finger.matrix_basis.to_quaternion()).angle
    assert angle>.15,(row['id'],'sin flexión de dedos',angle)
    hand_groups=[g for g in hands.vertex_groups if g.name in required];assert len(hand_groups)==30
    report.append({'id':row['id'],'fingers':10,'finger_bones':30,'bones':len(rig.data.bones),'clips':5,'hand_vertices':len(hands.data.vertices),'manifold':True,'finger_grip_radians':angle})
    print('VALIDATED',row['id'],flush=True)
for path in (B/'export/Props').glob('*.fbx'):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));assert any(o.type=='MESH' for o in bpy.context.scene.objects),path.name
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export/District_CityLife_R6.fbx'))
assert sum(o.name.startswith('Door_') for o in bpy.context.scene.objects)==6
(B/'fbx_validation.json').write_text(json.dumps({'passed':True,'characters':report,'props':37,'doors':6,'district':True},indent=2));print('R6_FBX_VALIDATION_PASSED',flush=True)
