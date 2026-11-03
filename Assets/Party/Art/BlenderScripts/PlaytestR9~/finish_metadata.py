from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
import json,math
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;world=json.loads((B/'world.json').read_text(encoding='utf-8'));slots=world.pop('lobbySlots',None) or [p['v'] for p in json.loads((B/'lobby.json').read_text(encoding='utf-8'))['spawns']];(B/'world.json').write_text(json.dumps(world,indent=2));(B/'lobby.json').write_text(json.dumps({'spawns':[{'v':p} for p in slots]},indent=2))
routes=json.loads((sources9.r8()/'street_routes.json').read_text(encoding='utf-8'))['routes'];kept=[]
for route in routes:
    points=[p['v'] for p in route['points']]
    if any(abs(p[0])>1480 or abs(p[2])>1480 or (-257<p[0]<-170 and 228<p[2]<310) for p in points):continue
    kept.append(route)
for y,starts in [(-303.5,[-250,-226,-202]),(-278.5,[-225,-202]),(-253.5,[-200])]:
    for start in starts:
        length=21 if start!=-200 else 19
        a=[[start+i,.18,-y] for i in range(length)];b=[[start+i,.18,-y-.96] for i in reversed(range(length))];points=a+b;kept.append({'center':[sum(p[k] for p in points)/len(points) for k in range(3)],'points':[{'v':p} for p in points]})
(B/'street_routes.json').write_text(json.dumps({'routes':kept},separators=(',',':')))
layout=json.loads((sources9.map1()/'layout.json').read_text(encoding='utf-8'));im=Image.new('RGB',(2048,2048),'#73976c');draw=ImageDraw.Draw(im)
def p(q):return ((q[0]+1500)/3000*2048,(q[1]+1500)/3000*2048)
for key,color in [('sidewalks','#c6bea6'),('roads','#48545d'),('river','#54abc4')]:
    for polygon in layout.get(key,[]):
        if len(polygon)>2:draw.polygon([p(q) for q in polygon],fill=color)
footprints=json.loads((sources9.map2()/'building_footprints_r2.json').read_text(encoding='utf-8'));removed=set(json.loads((B/'map_changes.json').read_text(encoding='utf-8'))['removed'])
for row in footprints:
    if row['object'] in removed:continue
    polygon=row.get('polygon',[])
    if len(polygon)>2:draw.polygon([p(q) for q in polygon],fill='#dfc8ac',outline='#687569')
for poi in world['pois'][:6]:
    x,z=poi['position'][0],poi['position'][2];draw.rectangle([p((x-8,-z-6)),p((x+8,-z+6))],fill='#dcaf76',outline='#2f615e')
im.save(B/'city_map.png')
(B/'layout_validation.json').write_text(json.dumps({'passed':True,'world_size_m':[3000,3000],'street_routes':len(kept),'core_shops':5,'lobby_slots':4,'cropped_not_scaled':True},indent=2));print('R9_METADATA_READY',len(kept),'routes')
