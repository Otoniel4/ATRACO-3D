"""Reimportación de los 17 prototipos y del mapa; comprueba máscaras y escala real."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Macetas_Pasto_Viento_R4.blend'))
catalog=json.loads((BASE/'asset_catalog.json').read_text());expected={}
for row in catalog:
    data=bpy.data.meshes[row['mesh']];colors=data.color_attributes['WindMask']
    tree=KDTree(len(data.vertices));values=[]
    for i,(v,color) in enumerate(zip(data.vertices,colors.data)):tree.insert(v.co,i);values.append(tuple(color.color))
    tree.balance();expected[row['mesh']]=(tree,values)
max_error=0;corners=0
for row in catalog:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(BASE/'export/kit'/(row['mesh']+'.fbx')),colors_type='LINEAR')
    obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');data=obj.data;colors=data.color_attributes[0]
    for loop in list(data.loops)[::max(1,len(data.loops)//1000)]:
        p=obj.matrix_world@data.vertices[loop.vertex_index].co;tree,values=expected[row['mesh']]
        choices=[values[i] for _,i,dist in tree.find_range(p,.00001)];assert choices,(obj.name,tuple(p))
        actual=colors.data[loop.index if colors.domain=='CORNER' else loop.vertex_index].color
        error=min(max(abs(actual[k]-candidate[k]) for k in range(4)) for candidate in choices)
        max_error=max(max_error,error);corners+=1
assert max_error<.006,max_error
for name,count in [('Jardinera_Florida_R4',5),('Maceta_Salvia_R4',2)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(BASE/'export/kit'/(name+'.fbx')),colors_type='LINEAR')
    parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(parts)==count,(name,len(parts))
    pots=[o for o in parts if o.name.startswith('Pot')];assert len(pots)==1
    assert all(max(c.color[:3])<1e-7 for c in pots[0].data.color_attributes[0].data),name
    assert all(any(max(c.color[:3])>.02 for c in o.data.color_attributes[0].data) for o in parts if o not in pots),name
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'export/Villa_Alarma_Jardineras_Pasto_R4.fbx'),colors_type='LINEAR')
objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
for path,key in [('plant_placements.json','foliage'),('grass_placements.json','object')]:
    for row in json.loads((BASE/path).read_text()):
        obj=objects[row[key]];assert obj.data.color_attributes,obj.name
        assert any(c.color[0]+c.color[1]+c.color[2]>.02 for c in obj.data.color_attributes[0].data),obj.name
low=[math.inf]*3;high=[-math.inf]*3
for obj in objects.values():
    for corner in obj.bound_box:
        p=obj.matrix_world@Vector(corner)
        for i in range(3):low[i]=min(low[i],p[i]);high[i]=max(high[i],p[i])
assert all(abs(high[i]-low[i]-4000)<.02 for i in range(2)),(low,high)
report={'kit_prototypes_reimported':len(catalog),'assembled_planters_reimported':2,'kit_fbx_files':len(list((BASE/'export/kit').glob('*.fbx'))),
        'mask_sampled_corners':corners,'mask_max_error':max_error,'city_xy_m':[high[i]-low[i] for i in range(2)],
        'city_plant_and_grass_masks_present':True,'unity_tested':False,'passed':True}
(BASE/'fbx_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PLANT_FBX_VERIFIED',json.dumps(report),flush=True)
