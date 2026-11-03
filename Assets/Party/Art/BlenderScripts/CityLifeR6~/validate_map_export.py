import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export/Map/Villa_Alarma_Ciudad_R6.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];minimum=[float('inf')]*3;maximum=[-float('inf')]*3
for obj in meshes:
    for corner in obj.bound_box:
        p=obj.matrix_world@Vector(corner)
        for i in range(3):minimum[i]=min(minimum[i],p[i]);maximum[i]=max(maximum[i],p[i])
dimensions=[maximum[i]-minimum[i] for i in range(3)];assert abs(dimensions[0]-4000)<.05 and abs(dimensions[1]-4000)<.05,dimensions
assert not any(o.type in ['ARMATURE','CAMERA','LIGHT'] for o in bpy.context.scene.objects)
assert not any(o.name=='InteriorR5_MallJewelry_JewelryCase_3' for o in meshes)
assert sum(o.name.startswith('R6_FoodDisplay_') for o in meshes)==3
masks=sum(bool(o.data.color_attributes.get('WindMask')) for o in meshes);assert masks>20000,masks
report={'passed':True,'dimensions_m':dimensions,'bounds_min':minimum,'bounds_max':maximum,'meshes':len(meshes),'objects_with_wind_mask':masks,'animated_characters_exported_in_map':False,'pickup_displays':3,'removed_blocking_case_verified':True}
(B/'map_fbx_validation.json').write_text(json.dumps(report,indent=2));print('MAP_FBX_VERIFIED',json.dumps(report),flush=True)
