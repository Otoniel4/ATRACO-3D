"""Simulación de revisión para Blender; la ejecución de juego usa los componentes C# y NavMesh."""
import math,json,heapq
from pathlib import Path
BASE=Path(__file__).resolve().parent
D=json.loads((BASE/'district.json').read_text());SHOP=D['shops'][0];OFFSET=SHOP['center'][0]
OBSTACLES=[]
for item in D['obstacles']:
    x,y,z=item['position'];sx,sy,sz=item['size']
    if abs(x-OFFSET)<10 and z+sz/2>.35:OBSTACLES.append((x-sx/2-.23,y-sy/2-.23,x+sx/2+.23,y+sy/2+.23))


def free(x,y):
    inside=(OFFSET-5.76<x<OFFSET+5.76 and -5.1<y<4.76) or (OFFSET-8<x<OFFSET+8 and -9.75<y<-4.9)
    return inside and not any(a<x<c and b<y<d for a,b,c,d in OBSTACLES)


def path(start,target):
    scale=5
    def snap(p):
        origin=(round(p[0]*scale),round(p[1]*scale));choices=[]
        for i in range(-3,4):
            for j in range(-3,4):
                n=(origin[0]+i,origin[1]+j)
                if free(n[0]/scale,n[1]/scale):choices.append((((n[0]/scale-p[0])**2+(n[1]/scale-p[1])**2),n))
        if not choices:raise RuntimeError('Destino de revisión bloqueado: '+str(p))
        return min(choices)[1]
    a,b=snap(start),snap(target);heap=[(0,a)];cost={a:0};previous={}
    while heap:
        _,node=heapq.heappop(heap)
        if node==b:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            n=(node[0]+dx,node[1]+dy)
            if not free(n[0]/scale,n[1]/scale):continue
            if dx and dy and (not free((node[0]+dx)/scale,node[1]/scale) or not free(node[0]/scale,(node[1]+dy)/scale)):continue
            value=cost[node]+math.hypot(dx,dy)
            if value>=cost.get(n,math.inf):continue
            cost[n]=value;previous[n]=node;heapq.heappush(heap,(value+math.hypot(n[0]-b[0],n[1]-b[1]),n))
    if b not in cost:raise RuntimeError('No hay ruta de revisión: '+str((start,target)))
    route=[b]
    while route[-1]!=a:route.append(previous[route[-1]])
    route=[(x/scale,y/scale) for x,y in reversed(route)]
    def clear(p,q):
        count=max(1,math.ceil(math.dist(p,q)/.08))
        return all(free(p[0]+(q[0]-p[0])*i/count,p[1]+(q[1]-p[1])*i/count) for i in range(count+1))
    smooth=[route[0]];i=0
    while i<len(route)-1:
        j=len(route)-1
        while j>i+1 and not clear(route[i],route[j]):j-=1
        smooth.append(route[j]);i=j
    return smooth[1:]


def simulate(seconds=24,fps=24):
    def world(p):return (p[0]+OFFSET,p[1])
    people=[];queue=[1,2,3];purchases=[]
    def new(index,p,state):return {'id':index,'p':world(p),'state':state,'timer':0.,'route':[], 'carrying':False,'queue_target':None,'yaw':0.}
    people.append(new(0,(0,-6.6),'Entering'))
    for i in [1,2,3]:people.append(new(i,(3,-2.05+(i-1)*.7),'Queue'))
    for i,p in enumerate([(-7,-8.2),(6,-9.2),(-3,-9.2),(3,-8.2),(-6,-9.2)],4):people.append(new(i,p,'Walking'))
    people.append(new(9,(3,-4),'Staff'));people[9]['yaw']=math.pi
    people[0]['route']=path(people[0]['p'],world(SHOP['browse']))
    for person in people[4:9]:person['route']=path(person['p'],world((7 if person['p'][0]<OFFSET else -7,person['p'][1])))
    traces=[[] for _ in people];dt=1/fps
    for frame in range(1,seconds*fps+1):
        for person in people:
            state=person['state'];person['timer']+=dt
            if state=='Queue':
                index=queue.index(person['id']);target=world((3,-2.05+index*.7))
                if target!=person['queue_target']:
                    person['route']=path(person['p'],target);person['queue_target']=target
                if index==0 and not person['route']:person['state']='Paying';person['timer']=0
            elif state=='Paying' and person['timer']>=2:
                person['state']='Clearing';person['carrying']=True;person['timer']=0
                purchases.append({'actor':person['id'],'seconds':frame/fps});person['route']=path(person['p'],world((1,-2.05)))
            elif state=='Clearing' and not person['route']:
                queue.remove(person['id']);person['state']='Leaving';person['route']=path(person['p'],world((0,-6.6)))
            elif state=='Entering' and not person['route']:person['state']='Browsing';person['timer']=0
            elif state=='Browsing' and person['timer']>=2:
                if len(queue)<3:queue.append(person['id']);person['state']='Queue';person['queue_target']=None
            elif state=='Leaving' and not person['route']:
                person['state']='Walking';person['route']=path(person['p'],world((-7,-8.2)))
            elif state=='Walking' and not person['route']:
                target=world((7 if person['p'][0]<OFFSET else -7,-8.2 if person['id']%2==0 else -9.2));person['route']=path(person['p'],target)
            if person['route']:
                target=person['route'][0];distance=math.dist(person['p'],target)
                step=min(distance,dt);dx=(target[0]-person['p'][0])/max(distance,1e-8);dy=(target[1]-person['p'][1])/max(distance,1e-8)
                proposed=(person['p'][0]+dx*step,person['p'][1]+dy*step)
                can_move=all(other==person or other['state']=='Staff' or math.dist(proposed,other['p'])>.43 for other in people)
                if can_move:
                    person['p']=proposed;desired=math.atan2(dx,-dy);turn=(desired-person['yaw']+math.pi)%math.tau-math.pi
                    person['yaw']+=max(-3.5*dt,min(3.5*dt,turn))
                    if distance<=dt+.0001:person['route'].pop(0)
            mode='Idle'
            if person['route']:mode='CarryWalk' if person['carrying'] else 'Walk'
            elif person['state']=='Paying':mode='Pay'
            elif person['state']=='Browsing':mode='Browse'
            elif person['state']=='Staff' and any(p['state']=='Paying' for p in people):mode='Pay'
            traces[person['id']].append({'frame':frame,'position':[person['p'][0],person['p'][1],.16],
                'yaw':person['yaw'],'mode':mode,'carrying':person['carrying'],'state':person['state']})
    return traces,purchases


if __name__=='__main__':
    traces,purchases=simulate();(BASE/'preview_traces.json').write_text(json.dumps({'actors':traces,'purchases':purchases}),encoding='utf-8')
    assert purchases,'No se completó ninguna compra en la revisión'
    assert any(p['actor']==0 for p in purchases),'El cliente que entra no terminó su compra'
    print('CITY_LIFE_PREVIEW_SIMULATED',purchases)
