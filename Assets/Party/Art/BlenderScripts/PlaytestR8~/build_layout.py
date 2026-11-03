"""Rutas sobre aceras reales y calzadas para comprobar vegetación y dibujar el plano."""
import bpy,json,math,collections
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r6()/'Villa_Alarma_Compras_R6.blend'))
meshes=[o for o in bpy.data.objects['VillaAlarma_4000m'].children_recursive if o.type=='MESH']
def surface(roles,asphalt=False):
    vertices=[];faces=[];polygons=[]
    for o in meshes:
        if not asphalt and o.get('MapRole') not in roles:continue
        selected=[p for p in o.data.polygons if not asphalt or o.get('MapRole')=='Roads' or (p.material_index<len(o.data.materials) and o.data.materials[p.material_index] and 'asphalt' in o.data.materials[p.material_index].name.lower())]
        if not selected:continue
        offset=len(vertices);vs=[o.matrix_world@v.co for v in o.data.vertices];vertices.extend(vs)
        faces.extend([offset+i for i in p.vertices] for p in selected)
        if asphalt:
            for p in selected:
                if all(abs(vs[i].z)<1 for i in p.vertices):polygons.append({'points':[{'v':[vs[i].x,0,-vs[i].y]} for i in p.vertices]})
    return BVHTree.FromPolygons(vertices,faces,all_triangles=False),polygons
walk,_=surface({'Sidewalks','BusinessAprons','pedestrian_access','Plaza','ParkPaths'})
obstacles,_=surface({'building','hero_shell','sidewalk_furniture','planter_rim','parked_vehicle','bicycle_rack','prop','detailed_interior'})
roads,polygons=surface(set(),True)
def floor(x,y):
    p,n,_,_=walk.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),5)
    if p is None or abs(n.z)<.5:return None
    for dx,dy in [(0,0),(.32,0),(-.32,0),(0,.32),(0,-.32)]:
        hit,_,_,_=obstacles.ray_cast(Vector((x+dx,y+dy,p.z+.45)),Vector((0,0,1)),1.3)
        if hit is not None:return None
    return [x,p.z+.025,-y]
layout=json.loads((map1()/'layout.json').read_text());routes=[]
world=json.loads((r7()/'world.json').read_text())
def near_shop(p):return any(abs(p[0]-s['origin'][0])<10 and abs(-p[2]+s['origin'][2])<16 for s in world['shops'])
for line in layout['lines']:
    a,b=Vector(line['a']),Vector(line['b']);direction=(b-a).normalized();normal=Vector((-direction.y,direction.x));length=(b-a).length
    for side in [-1,1]:
        for index in range(int(length/60)):
            centre=a+direction*(index*60+30)+normal*side*(line['width']/2+1.6)
            left=[];right=[]
            for step in range(31):
                middle=centre+direction*((step-15)*1.2)
                ps=[floor(*(middle+normal*v)) for v in [-.48,.48]]
                if any(p is None or near_shop(p) for p in ps):break
                left.append(ps[0]);right.append(ps[1])
            if len(left)<31:continue
            points=left+list(reversed(right));center=[sum(p[i] for p in points)/len(points) for i in range(3)]
            routes.append({'center':center,'points':[{'v':p} for p in points]})
assert len(routes)>100,len(routes)
data={'routes':routes};(B/'street_routes.json').write_text(json.dumps(data,separators=(',',':')))
(B/'road_areas.json').write_text(json.dumps({'polygons':polygons},separators=(',',':')))
(B/'layout_validation.json').write_text(json.dumps({'passed':True,'routes':len(routes),'nodes':sum(len(r['points']) for r in routes),'roads':len(polygons),'route_surface':'aceras reales; margen lateral; rayos de obstáculos; sin rutas dentro de las tres tiendas'},indent=2))
print('STREET_ROUTES',len(routes),'ROAD_POLYGONS',len(polygons),flush=True)
