"""Traza 4×4 km, retícula, diagonales y rotonda de la referencia. Sin dependencias externas."""
import math,json
from pathlib import Path
from layout_math import *
BASE=Path(__file__).resolve().parent
c=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'))
lines=[]
for x in range(c['urban_x'][0],c['urban_x'][1]+1,c['block_pitch_m']):
    lines.append({'a':[x,-1600],'b':[x,1600],'width':22 if x in [-320,0,640] else 14,'kind':'grid'})
for y in range(-1600,1601,160):
    lines.append({'a':[-1600,y],'b':[1440,y],'width':22 if y in [-320,0,640] else 14,'kind':'grid'})
reserved={tuple(p['block']) for p in c['pois'] if 'block' in p}|{tuple(p) for p in c['park_blocks']}
for bx in range(19):
    for by in range(20):
        if (bx,by) in reserved:continue
        x=-1600+(bx+.5)*160;y=-1600+(by+.5)*160
        if x<-1180 and y<-1080:continue
        lines.extend([{'a':[x-80,y],'b':[x+80,y],'width':8,'kind':'secondary'},
                      {'a':[x,y-80],'b':[x,y+80],'width':8,'kind':'secondary'}])
for a,b in c['diagonal_avenues']:lines.append({'a':a,'b':b,'width':22,'kind':'diagonal'})
for a,b in [((-1850,-1850),(1850,-1850)),((1850,-1850),(1850,1850)),((1850,1850),(-1850,1850)),((-1850,1850),(-1850,-1850))]:
    lines.append({'a':a,'b':b,'width':30,'kind':'highway'})
for x in [-1280,0,1280]:
    for s in [-1,1]:lines.append({'a':[x,s*1600],'b':[x,s*1850],'width':22,'kind':'connector'})
road_rects=[strip(l['a'],l['b'],l['width']) for l in lines]
inner=disk(0,0,48,48);outer=disk(0,0,64,48)
ring=[ccw([outer[i],outer[(i+1)%48],inner[(i+1)%48],inner[i]]) for i in range(48)]
roads=difference(union(road_rects+ring),[inner])
print('ROAD_UNION',len(roads),flush=True)
envelopes=[strip(l['a'],l['b'],l['width']+8) for l in lines]
walks=difference(union(envelopes),road_rects+[outer])
river_parts=[]
for a,b in zip(c['river_path'],c['river_path'][1:]):river_parts.append(strip(a,b,c['river_width_m']))
river_parts += [disk(x,y,c['river_width_m']/2,16) for x,y in c['river_path']]
river=union(river_parts)
walks=difference(walks,river)
print('SIDEWALKS',len(walks),'RIVER',len(river),flush=True)
# Grafo geométrico de líneas: sin tráfico ni IA. La rotonda conecta los ocho accesos.
graph_lines=lines.copy();mid=disk(0,0,56,48)
graph_lines += [{'a':mid[i],'b':mid[(i+1)%48],'width':16,'kind':'roundabout'} for i in range(48)]
splits=[[(0,l['a']),(1,l['b'])] for l in graph_lines]
for i,l in enumerate(graph_lines):
    for j in range(i):
        q=graph_lines[j];hit=intersection(l['a'],l['b'],q['a'],q['b'])
        if hit:
            p,t,u=hit;splits[i].append((t,p));splits[j].append((u,p))
nodes={};edges=set()
def node(p):
    key=tuple(round(v,3) for v in p)
    if key not in nodes:nodes[key]=len(nodes)
    return nodes[key]
for line,points in zip(graph_lines,splits):
    points=sorted(points,key=lambda x:x[0])
    for (_,a),(_,b) in zip(points,points[1:]):
        if math.dist(a,b)<.01:continue
        midpoint=((a[0]+b[0])/2,(a[1]+b[1])/2)
        if math.hypot(*midpoint)<48:continue
        ia,ib=node(a),node(b);edges.add(tuple(sorted((ia,ib))))
adj={i:set() for i in nodes.values()}
for a,b in edges:adj[a].add(b);adj[b].add(a)
seen={0};pending=[0]
while pending:
    for n in adj[pending.pop()]-seen:seen.add(n);pending.append(n)
assert len(seen)==len(nodes),(len(seen),len(nodes))
data={'roads':roads,'sidewalks':walks,'river':river,'lines':lines,
      'graph':{'nodes':[{'id':i,'position':[x,y,.04]} for (x,y),i in nodes.items()],
               'edges':sorted(edges),'connected':True,'status':'geometric design only'}}
(BASE/'layout.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
print('LAYOUT_READY',len(nodes),'NODES',len(edges),'EDGES',flush=True)
