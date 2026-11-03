"""Comprobaciones geométricas de la revisión: mundo, calles, edificios nuevos y partes editables."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from layout_math import rect,overlap
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
scene=bpy.data.scenes['CityR2_Overview'];bpy.context.window.scene=scene;bpy.context.view_layer.update()
root=bpy.data.objects['VillaAlarma_4000m'];objects=list(root.children_recursive)
meshes=[o for o in objects if o.type=='MESH'];lo=[math.inf]*3;hi=[-math.inf]*3
for obj in meshes:
    for vertex in obj.bound_box:
        p=obj.matrix_world@Vector(vertex)
        for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
assert abs(hi[0]-lo[0]-4000)<.02 and abs(hi[1]-lo[1]-4000)<.02,(lo,hi)
assert len(root.children)==64
roads=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))['roads']
collisions=[];checked=0
for obj in meshes:
    if obj.get('MapRole') not in ['building','hero_shell','gallery_business']:continue
    vertices=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    roof=bpy.data.objects.get(obj.name+'_ModernRoof')
    if roof:vertices.extend(roof.matrix_world@Vector(p) for p in roof.bound_box)
    polygon=rect(min(p.x for p in vertices),min(p.y for p in vertices),max(p.x for p in vertices),max(p.y for p in vertices))
    if any(overlap(polygon,p) for p in roads):collisions.append(obj.name)
    checked+=1
assert not collisions,collisions[:20]
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['pois'])==14
heroes=[o for o in meshes if o.get('MapRole')=='hero_shell'];assert len(heroes)==9
doors=[o for o in meshes if o.get('MapRole')=='door'];assert len(doors)>=26
roofs=[o for o in meshes if o.get('MapRole')=='removable_roof'];assert len(roofs)>3700
species={o.get('R2Species') for o in meshes if 'R2Species' in o};assert len(species)==6
for obj in meshes:
    assert all(math.isfinite(v) for v in obj.matrix_world.translation),obj.name
    assert all(p.material_index<len(obj.data.materials) for p in obj.data.polygons),obj.name
result={'world_minimum':lo,'world_maximum':hi,'world_xy_m':[hi[0]-lo[0],hi[1]-lo[1]],'sector_count':64,
        'mesh_objects':len(meshes),'checked_buildings_including_heroes':checked,'buildings_on_roads':collisions,
        'hero_interiors':len(heroes),'separate_doors':len(doors),'separate_roofs':len(roofs),
        'tree_species':len(species),'instanced_triangles':manifest['evaluated_triangles'],
        'animation':False,'unity_performance_navmesh_collisions_verified':False,'passed':True}
(BASE/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MODERN_CITY_VALIDATION_SUCCESS',json.dumps(result),flush=True)
