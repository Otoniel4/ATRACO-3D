"""Ajusta los grafos de compra a los obstáculos estáticos que utiliza el mapa completo."""
import bpy,json,collections,math
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parent;world=json.loads((r7()/'world.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(r6()/'Villa_Alarma_Compras_R6.blend'))
names={p['source'] for c in world['cells'] for p in c['parts'] if p['collision']==1 or p['role']=='parked_vehicle'}
vertices=[];faces=[]
for name in names:
    obj=bpy.data.objects.get(name)
    if obj is None or obj.type!='MESH':continue
    index=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices);faces.extend([index+i for i in p.vertices] for p in obj.data.polygons)
obstacles=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
def free(point):
    x,z,minusy=point;y=-minusy
    for dx,dy in [(0,0),(.24,0),(-.24,0),(0,.24),(0,-.24),(.17,.17),(-.17,-.17),(.17,-.17),(-.17,.17)]:
        p,_,_,_=obstacles.ray_cast(Vector((x+dx,y+dy,z+.35)),Vector((0,0,1)),1.3)
        if p is not None:return False
    return True
report=[]
for shop in world['shops']:
    nodes=shop['nodes'];valid={i for i,n in enumerate(nodes) if free(n['v'])};edges={}
    for i in valid:
        edges[i]=[j for j in nodes[i]['links'] if j in valid and all(free([(1-t)*nodes[i]['v'][k]+t*nodes[j]['v'][k] for k in range(3)]) for t in [.25,.5,.75])]
    components=[];remaining=set(valid)
    while remaining:
        comp=set();stack=[remaining.pop()]
        while stack:
            i=stack.pop();comp.add(i)
            for j in edges[i]:
                if j in remaining:remaining.remove(j);stack.append(j)
        components.append(comp)
    component=max(components,key=len);ids=sorted(component);mapping={old:new for new,old in enumerate(ids)};moves=[]
    for kind in ['walk','entry','queue','exit','browseStations']:
        used=set()
        for point in shop[kind]:
            local=point['v'];origin=shop['origin'];target=[origin[0]+local[0],origin[1]+local[2],origin[2]-local[1]]
            candidates=[i for i in ids if i not in used];nearest=min(candidates,key=lambda i:sum((nodes[i]['v'][k]-target[k])**2 for k in range(3)))
            distance=math.sqrt(sum((nodes[nearest]['v'][k]-target[k])**2 for k in range(3)))
            assert distance<1.5,(shop['id'],kind,distance)
            used.add(nearest);p=nodes[nearest]['v'];point['v']=[p[0]-origin[0],origin[2]-p[2],p[1]-origin[1]]
            moves.append({'kind':kind,'distance':distance})
    shop['nodes']=[{'v':nodes[i]['v'],'links':[mapping[j] for j in edges[i] if j in component]} for i in ids]
    assert len(ids)>100,(shop['id'],len(ids))
    report.append({'shop':shop['id'],'before':len(nodes),'after':len(ids),'max_station_adjustment':max(m['distance'] for m in moves),'moves':moves})
(B/'world.json').write_text(json.dumps(world,indent=2));(B/'shop_clearance.json').write_text(json.dumps({'passed':True,'shops':report,'clearance_radius_m':.24},indent=2));print('SHOP_CLEARANCE_PASS',[(r['shop'],r['before'],r['after'],r['max_station_adjustment']) for r in report],flush=True)
