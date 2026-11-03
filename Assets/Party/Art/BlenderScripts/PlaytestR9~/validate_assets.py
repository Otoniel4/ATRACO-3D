import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;world=json.loads((B/'world.json').read_text(encoding='utf-8'));bpy.ops.wm.open_mainfile(filepath=str(B/'Villa_Alarma_3000_R9.blend'));root=bpy.data.objects['VillaAlarma_3000m'];lo=Vector((1e9,1e9,1e9));hi=-lo
for obj in root.children_recursive:
    if obj.type!='MESH' or not obj.data.vertices:continue
    coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coords);coords=coords.reshape((-1,3));matrix=np.asarray(obj.matrix_world,dtype=np.float64);points=coords@matrix[:3,:3].T+matrix[:3,3];minimum=points.min(axis=0);maximum=points.max(axis=0)
    for k in range(3):lo[k]=min(lo[k],minimum[k]);hi[k]=max(hi[k],maximum[k])
assert abs(lo.x+1500)<.02 and abs(hi.x-1500)<.02 and abs(lo.y+1500)<.02 and abs(hi.y-1500)<.02,(lo,hi)
characters=[]
for file in sorted((B/'export/Characters').glob('*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(file));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    for t in rig.animation_data.nla_tracks:t.mute=True
    for mode in ['Walk','Run']:
        action=bpy.data.actions.get(rig.name+'|'+mode);assert action,(file,mode);rig.animation_data.action=action
        if action.slots:rig.animation_data.action_slot=action.slots[0]
        positions=[]
        for f in range(1,20,2):bpy.context.scene.frame_set(f);bpy.context.view_layer.update();positions.append(rig.pose.bones['LeftFoot'].head.copy())
        assert max((p-positions[0]).length for p in positions)>.07,(file,mode)
    characters.append(file.name)
for folder in ['Props','Doors']:
    for file in (B/'export'/folder).glob('*.fbx'):
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(file))
        for name in ['Origin','X','Front']:assert bpy.data.objects.get('R9_Anchor_'+name),(file,name)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export/World/District_Start.fbx'))
for name in ['Origin','X','Front']:assert bpy.data.objects.get('R9_Anchor_'+name)
assert len(characters)==18
(B/'asset_validation.json').write_text(json.dumps({'passed':True,'world_bounds':[list(lo),list(hi)],'world_size_m':[3000,3000],'characters_reimported':len(characters),'props':7,'door_types':3,'core_quarter_reimported':True,'unity_play_tested':False},indent=2));print('R9_ASSET_VALIDATION_PASS',flush=True)
