from pathlib import Path
from review_sources import r6,r7,map1,map2
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;source=map1();layout=json.loads((source/'layout.json').read_text());image=Image.new('RGB',(2048,2048),'#73976c');draw=ImageDraw.Draw(image)
def p(point):return ((point[0]+2000)/4000*2048,(point[1]+2000)/4000*2048)
for key,color in [('sidewalks','#c6bea6'),('roads','#48545d'),('river','#54abc4')]:
    for polygon in layout.get(key,[]):
        if len(polygon)>2:draw.polygon([p(q) for q in polygon],fill=color)
footprints=json.loads((map2()/'building_footprints_r2.json').read_text())
for row in footprints:
    polygon=row.get('polygon',[])
    if len(polygon)>2:draw.polygon([p(q) for q in polygon],fill=['#e0ccb0','#d2a48a','#b8c7be','#d8bd94'][hashlib.sha256(row['object'].encode()).digest()[0]%4],outline='#5b6960')
world=json.loads((r7()/'world.json').read_text())
for poi in world['pois']:
    x,z=poi['position'][0],poi['position'][2];cx,cy=p([x,-z]);r=4;draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#d5773d',outline='#fff0c0')
image.save(B/'city_map.png');print('CITY_MAP_READY',image.size)
