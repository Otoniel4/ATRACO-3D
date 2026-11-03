"""Escala, sectores, continuidad vial, accesos y ausencia de edificios en calzadas."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from layout_math import overlap,strip
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
scene=bpy.data.scenes['Map4Km_Overview'];bpy.context.window.scene=scene;bpy.context.view_layer.update()
root=bpy.data.objects['VillaAlarma_4000m'];meshes=[o for o in root.children_recursive if o.type=='MESH']
lo=[float('inf')]*3;hi=[-float('inf')]*3
for obj in meshes:
    assert all(math.isfinite(v) for row in obj.matrix_world for v in row),obj.name
    for v in obj.bound_box:
        p=obj.matrix_world@Vector(v)
        for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
assert abs(lo[0]+2000)<.01 and abs(hi[0]-2000)<.01 and abs(lo[1]+2000)<.01 and abs(hi[1]-2000)<.01,(lo,hi)
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['sectors'])==64 and manifest['building_count']>1000
layout=json.loads((BASE/'layout.json').read_text());polys=[strip(l['a'],l['b'],l['width']+5.8) for l in layout['lines']]
footprints=json.loads((BASE/'building_footprints.json').read_text());collisions=[]
for i,f in enumerate(footprints):
    if any(overlap(f['polygon'],p) for p in polys):collisions.append(i)
assert not collisions,collisions[:10]
graph=layout['graph'];adj={n['id']:set() for n in graph['nodes']}
for a,b in graph['edges']:adj[a].add(b);adj[b].add(a)
seen={0};stack=[0]
while stack:
    for node in adj[stack.pop()]-seen:seen.add(node);stack.append(node)
assert len(seen)==len(adj)
for identifier in ['Minimarket','MallJewelry','Bank']:
    poi=next(p for p in manifest['pois'] if p['id']==identifier)
    assert poi.get('interior_asset') and poi.get('entrance') and poi.get('rear_exit')
    assert any(o.name.startswith(identifier+'_Door') and o.get('HingeOrigin') for o in meshes)
assert len(manifest['roof_objects'])>=9
results={'world_xy_min':lo[:2],'world_xy_max':hi[:2],'world_size_m':[hi[0]-lo[0],hi[1]-lo[1]],'area_km2':16,
         'sectors':64,'road_graph_nodes':len(adj),'road_graph_edges':len(graph['edges']),'road_graph_connected':True,
         'generic_buildings_on_roads':len(collisions),'building_count':manifest['building_count'],
         'checked_building_footprints':len(footprints),'robbery_interiors_with_entrance_rear_exit':3,
         'unity_navmesh_collision_and_performance_verified':False}
(BASE/'validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('MAP_VALIDATION_SUCCESS',results,flush=True)
