"""Contactos de renders reales para revisar todo el elenco."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
CAST=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))['characters']
FONT='C:/Windows/Fonts/arial.ttf'

def sheet(name,view,title):
    w,h=280,390;canvas=Image.new('RGB',(1680,1235),'#25292e');draw=ImageDraw.Draw(canvas)
    draw.text((20,17),title,font=ImageFont.truetype(FONT,26),fill='#f5e9d5')
    for i,actor in enumerate(CAST):
        image=Image.open(BASE/'renders'/actor['id']/(view+'.png')).convert('RGB');image.thumbnail((270,350),Image.Resampling.LANCZOS)
        x=(i%6)*w;y=65+(i//6)*h;canvas.paste(image,(x+(w-image.width)//2,y))
        font=ImageFont.truetype(FONT,17)
        if draw.textlength(actor['label'],font=font)>w-5:font=ImageFont.truetype(FONT,15)
        draw.text((x+(w-draw.textlength(actor['label'],font=font))/2,y+356),actor['label'],font=font,fill='#f5e9d5')
    canvas.save(BASE/'renders'/name)

for file,view,title in [('elenco.png','front','ALARMA · piernas y articulaciones R3'),
                        ('perfiles.png','side','Perfiles · alineación de piernas'),
                        ('espaldas.png','back','Espaldas · revisión de prendas'),
                        ('paso.png','step_pose','Paso · flexión de cadera, rodilla y hombro'),
                        ('rodillas.png','double_knee_pose','Prueba de ambas rodillas · 18 personajes')]:
    sheet(file,view,title)
ids=['NPC01_Bomber','NPC03_Tourist','NPC10_Cardigan','NPC14_PoliceFemale','Player03_Distractor','NPC02_Denim']
canvas=Image.new('RGB',(1800,1250),'#25292e');draw=ImageDraw.Draw(canvas)
for n,identifier in enumerate(ids):
    x=(n%3)*600;y=(n//3)*625
    label=next(a['label'] for a in CAST if a['id']==identifier)
    draw.text((x+15,y+10),label,font=ImageFont.truetype(FONT,20),fill='#f5e9d5')
    for col,(root,caption) in enumerate([(BASE/'baseline/renders_r2','Antes'),(BASE/'renders','Ahora')]):
        image=Image.open(root/identifier/'front.png').convert('RGB');image.thumbnail((290,540),Image.Resampling.LANCZOS)
        canvas.paste(image,(x+col*300+(300-image.width)//2,y+65))
        draw.text((x+col*300+10,y+40),caption,font=ImageFont.truetype(FONT,16),fill='#bdc7ce')
canvas.save(BASE/'renders/antes_despues.png')
print('R3_SHEETS_READY')
