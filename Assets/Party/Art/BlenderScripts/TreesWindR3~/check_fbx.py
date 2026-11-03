"""Ida y vuelta de follaje, datos de viento y extensión del mapa. Sin abrir Unity."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Arboles_Viento_R3.blend'))
source=bpy.data.meshes['TreeR3_Fresno_LOD0'];attr=source.color_attributes['WindMask'];expected={}
for v,color in zip(source.vertices,attr.data):expected.setdefault(tuple(round(x,3) for x in v.co),[]).append(tuple(color.color))
source_bounds=[min(v.co[k] for v in source.vertices) for k in range(3)]+[max(v.co[k] for v in source.vertices) for k in range(3)]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'export/trees/TreeR3_Fresno_LOD0.fbx'),colors_type='LINEAR')
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');data=obj.data;colors=data.color_attributes[0];error=0;checked=0
for loop in list(data.loops)[::max(1,len(data.loops)//4000)]:
    p=obj.matrix_world@data.vertices[loop.vertex_index].co;key=tuple(round(x,3) for x in p)
    choices=expected.get(key,[])
    if not choices:
        choices=[color for position,values in expected.items() if sum((position[k]-p[k])**2 for k in range(3))<.000004 for color in values]
    assert choices,tuple(p)
    actual=colors.data[loop.index if colors.domain=='CORNER' else loop.vertex_index].color
    delta=min(max(abs(actual[k]-candidate[k]) for k in range(4)) for candidate in choices);error=max(error,delta);checked+=1
assert error<.006,error
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'export/Villa_Alarma_Arboles_Viento_R3.fbx'),colors_type='LINEAR')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];lo=[math.inf]*3;hi=[-math.inf]*3
for obj in meshes:
    for corner in obj.bound_box:
        p=obj.matrix_world@Vector(corner)
        for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
assert abs(hi[0]-lo[0]-4000)<.02 and abs(hi[1]-lo[1]-4000)<.02,(lo,hi)
tree_names={r['object'] for r in json.loads((BASE/'tree_placements.json').read_text(encoding='utf-8'))}
trees=[o for o in meshes if o.data.color_attributes and o.name in tree_names]
expected_trees=len(tree_names);assert len(trees)==expected_trees
report={'wind_mask_max_error':error,'sampled_fbx_corners':checked,'city_xy_m':[hi[0]-lo[0],hi[1]-lo[1]],
        'tree_meshes_with_wind_data':len(trees),'tree_fbx_files':len(list((BASE/'export/trees').glob('*.fbx'))),
        'passed':True,'unity_shader_compiled':False}
(BASE/'fbx_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('WIND_FBX_VALIDATED',json.dumps(report),flush=True)
