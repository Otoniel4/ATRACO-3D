"""Hojas de revisión con renders reales; no modifica las imágenes de origen."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
cast=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))['characters']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)

def sheet(name,view,title):
    w,h=280,390;canvas=Image.new('RGB',(6*w,3*h+65),'#272b30');draw=ImageDraw.Draw(canvas)
    draw.text((20,18),title,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26),fill='#f5ead7')
    for i,actor in enumerate(cast):
        im=Image.open(BASE/'renders'/actor['id']/(view+'.png')).convert('RGB');im.thumbnail((270,350),Image.Resampling.LANCZOS)
        x=(i%6)*w;y=65+(i//6)*h
        canvas.paste(im,(x+(w-im.width)//2,y))
        label=actor['label'];font_size=18 if draw.textlength(label,font=font)<w else 15
        f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',font_size)
        draw.text((x+(w-draw.textlength(label,font=f))/2,y+355),label,font=f,fill='#f5ead7')
    canvas.save(BASE/'renders'/name)

sheet('paso_18.png','step_pose','Prueba de cadera, rodilla y hombro · 18 actores')
sheet('rodillas_18.png','double_knee_pose','Flexión de ambas rodillas · 18 actores')
sheet('elenco_R2.png','front','ALARMA · revisión de esqueletos y piernas R2')
canvas=Image.new('RGB',(1200,820),'#272b30');draw=ImageDraw.Draw(canvas)
for i,(path,title) in enumerate([(BASE/'baseline/tonito_before.png','Antes'),
                                 (BASE/'renders/Player04_Muscle/front.png','Ahora · piernas centradas')]):
    im=Image.open(path).convert('RGB');im.thumbnail((580,740),Image.Resampling.LANCZOS)
    canvas.paste(im,(i*600+(600-im.width)//2,65))
    draw.text((i*600+20,18),title,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24),fill='#f5ead7')
canvas.save(BASE/'renders/tonito_antes_despues.png')
print('REVIEW_SHEETS_READY')
