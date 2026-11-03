"""Calibra las tareas y un grafo conservador para probar el dominio sin iniciar Unity."""
import json,math
from pathlib import Path
B=Path(__file__).resolve().parent;d=json.loads((B/'district.json').read_text())
d['obstacles']=[o for o in d['obstacles'] if not o.get('r6_food_display') and not o.get('r6_staff')]
for x,y in [(21,-2.48),(22.4,-2.48),(22.4,-3.88)]:d['obstacles'].append({'position':[x,y,.635],'size':[.36,.20,.95],'r6_food_display':True})
for x,y in [(-14.7,-4.1),(0,4.65),(21,2.65)]:d['obstacles'].append({'position':[x,y,1.11],'size':[.48,.48,1.9],'r6_staff':True})
pitch=.7;nodes=[];indices={}
def free(x,y):
    on_floor=(-35.8<x<35.8 and -9.7<y<-5.05) or any(abs(x-s['center'][0])<5.65 and -5.2<y<4.65 for s in d['shops'])
    if not on_floor:return False
    return not any(abs(x-o['position'][0])<o['size'][0]/2+.24 and abs(y-o['position'][1])<o['size'][1]/2+.24 for o in d['obstacles'])
for iy in range(21):
    for ix in range(103):
        x=-35.7+ix*pitch;y=-9.1+iy*pitch
        if free(x,y):indices[ix,iy]=len(nodes);nodes.append({'v':[round(x,6),.16,round(-y,6)],'links':[]})
for (ix,iy),i in indices.items():
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        if (ix+dx,iy+dy) not in indices:continue
        j=indices[ix+dx,iy+dy];a=nodes[i]['v'];b=nodes[j]['v']
        if all(free(a[0]+(b[0]-a[0])*t,-a[2]+(-b[2]+a[2])*t) for t in [.2,.4,.6,.8]):nodes[i]['links'].append(j)
def snap(shop,p):
    x=shop['center'][0]+p[0];y=p[1];best=min(range(len(nodes)),key=lambda i:(nodes[i]['v'][0]-x)**2+(nodes[i]['v'][2]+y)**2)
    n=nodes[best]['v'];distance=math.hypot(n[0]-x,n[2]+y)
    assert distance<.7,(shop['id'],p,distance)
    return [round(n[0]-shop['center'][0],6),round(-n[2],6),.16]
for shop in d['shops']:
    sid=shop['id']
    # Un circuito de acera tiene dos carriles; entrada y salida usan lados distintos del hueco de puerta.
    shop['walk']=[[-4.5,-9.1,.16],[4.6,-9.1,.16],[4.6,-7,.16],[-4.5,-7,.16]]
    shop['entry']=[[-.45,-6.3,.16],[-.45,-3.5,.16]]
    shop['exit']=([[-.5,-2.1,.16],[.55,-3.5,.16],[.55,-6.3,.16],[2,-7,.16]] if sid=='Minimarket' else [[1.8,2.8 if sid=='MallJewelry' else .5,.16],[1.8,-3.5,.16],[.55,-6.3,.16],[2,-7,.16]])
    if sid=='Minimarket':
        shop['browseStations']=[[-3.4,1.4,.16],[0,1.4,.16],[3.4,1.4,.16]];shop['queue']=[[3,-2.1,.16],[3,-1.4,.16],[3,-.7,.16]]
        shop['counter']=[3.3,-2.65,1.12];shop['priceCents']=750;shop['product']='JuiceCarton'
    elif sid=='MallJewelry':
        # Vitrinas de las paredes; la fila central no cruza los puestos de compra.
        shop['browseStations']=[[-3.5,-.7,.16],[0,-.7,.16],[3.5,-.7,.16]];shop['queue']=[[0,2.8,.16],[-.7,2.8,.16],[-1.4,2.8,.16]]
        shop['counter']=[0,3.3,1.12];shop['priceCents']=2500;shop['product']='JewelryBox'
    else:
        shop['browseStations']=[[2.8,-2.1,.16],[4.2,-2.1,.16],[4.2,-3.5,.16]];shop['queue']=[[3,.7,.16],[3,0,.16],[3,-.7,.16]]
        shop['counter']=[3,1.25,1.12];shop['priceCents']=1200;shop['product']='FoodBox'
    for key in ['walk','entry','exit','browseStations','queue']:shop[key]=[snap(shop,p) for p in shop[key]]
    assert len({tuple(p) for p in shop['queue']+shop['browseStations']})==6,(sid,'puestos repetidos')
    shop['products']=[]
    for x,y,z in shop['browseStations']:
        shop['products'].append([x,y+(.48 if sid=='MallJewelry' else -.38),1.40 if sid=='MallJewelry' else 1.10])
    shop['staff']=[shop['counter'][0],-4.1 if sid=='Minimarket' else 4.65 if sid=='MallJewelry' else 2.65,.16]
    shop['scan']=[shop['counter'][0],-3.55 if sid=='Minimarket' else 4.25 if sid=='MallJewelry' else 2.25,1.12]
    shop['receipt']=[shop['counter'][0]-.25,shop['counter'][1],1.14]
    shop['till']=[shop['counter'][0]+.45,shop['counter'][1],1.15]
    shop['browse']=shop['browseStations'][0]
(B/'district.json').write_text(json.dumps(d,indent=2));(B/'traffic_graph.json').write_text(json.dumps({'nodes':nodes,'pitch':pitch},indent=2))
u=json.loads(json.dumps(d))
for shop in u['shops']:
    for key in ['walk','entry','exit','browseStations','queue','products']:shop[key]=[{'v':p} for p in shop[key]]
(B/'unity_district.json').write_text(json.dumps(u,indent=2))
print('TRAFFIC_GRAPH_READY',len(nodes),'cells',[(s['id'],s['browseStations'],s['queue']) for s in d['shops']])
