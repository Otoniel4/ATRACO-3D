import bpy,json,math,collections
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r6()/'Villa_Alarma_Compras_R6.blend'));buckets=collections.defaultdict(list)
for o in bpy.data.objects['VillaAlarma_4000m'].children_recursive:
    if o.type!='MESH' or o.get('MapRole') not in ['street_tree','forest']:continue
    points=[o.matrix_world@v.co for v in o.data.vertices];z=min(p.z for p in points);bottom=[p for p in points if p.z<z+.15];p=sum(bottom,Vector())/len(bottom);buckets[(int(p.x//16),int(p.y//16))].append((p.x,p.y,.65))
def free(p):
    x,y=p[0],-p[2]
    for i in range(int(x//16)-1,int(x//16)+2):
        for j in range(int(y//16)-1,int(y//16)+2):
            if any((x-a)**2+(y-b)**2<r*r for a,b,r in buckets[i,j]):return False
    return True
path=B/'street_routes.json';data=json.loads(path.read_text());before=len(data['routes']);routes=[]
for row in data['routes']:
    points=[p['v'] for p in row['points']];valid=True
    for a,b in zip(points,points[1:]+points[:1]):
        if any(not free([(1-t)*a[k]+t*b[k] for k in range(3)]) for t in [0,.25,.5,.75]):valid=False;break
    if valid:routes.append(row)
assert len(routes)>100
data['routes']=routes;path.write_text(json.dumps(data,separators=(',',':')));report=json.loads((B/'layout_validation.json').read_text());report.update(routes_before_tree_clearance=before,routes=len(routes),nodes=sum(len(r['points']) for r in routes),tree_clearance_m=.65);(B/'layout_validation.json').write_text(json.dumps(report,indent=2));print('TREE_ROUTE_CLEARANCE',before,'to',len(routes),flush=True)
