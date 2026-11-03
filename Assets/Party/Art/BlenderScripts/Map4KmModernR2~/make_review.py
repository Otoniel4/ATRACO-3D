"""Láminas de revisión R2 con renders reales y comparación con la entrega anterior."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
BASE=Path(__file__).resolve().parent;R=BASE/'renders'
FONT='C:/Windows/Fonts/arial.ttf';BOLD='C:/Windows/Fonts/arialbd.ttf'
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def panel(canvas,path,box):
    image=Image.open(path).convert('RGB');image=ImageOps.fit(image,(box[2]-box[0],box[3]-box[1]),centering=(.5,.5))
    canvas.paste(image,box[:2])
canvas=Image.new('RGB',(1800,1320),'#F4F1E9');d=ImageDraw.Draw(canvas)
d.text((30,18),'ALARMA · CIUDAD MODERNA LOW POLY',font=font(38,True),fill='#263C48')
entries=[('Residential','Casas con terrazas y jardines'),('StreetLevel','Negocios y escaparates amueblados'),
         ('BusinessDistrict','Oficinas con volúmenes distintos'),('Plaza','Vegetación y espacios públicos')]
for i,(name,label) in enumerate(entries):
    x=(i%2)*900;y=85+(i//2)*610
    d.text((x+25,y),label,font=font(28,True),fill='#263C48')
    panel(canvas,R/(name+'.png'),(x+20,y+45,x+880,y+590))
canvas.save(R/'Revision_R2.png')
canvas=Image.new('RGB',(1800,1260),'#F4F1E9');d=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate([('Minimarket_Inside','Minimercado'),('Bank_Inside','Banco y bóveda'),('Police_Inside','Comisaría y celdas'),('Restaurant','Restaurante y terraza')]):
    x=(i%2)*900;y=(i//2)*630;d.text((x+25,y+15),label,font=font(30,True),fill='#263C48')
    panel(canvas,R/(name+'.png'),(x+20,y+65,x+880,y+610))
canvas.save(R/'Interiores_R2.png')
old=BASE/'baseline/Street_V1.png'
if old.exists():
    canvas=Image.new('RGB',(1800,670),'#F4F1E9');d=ImageDraw.Draw(canvas)
    for i,(path,label) in enumerate([(old,'Entrega anterior'),(R/'StreetLevel.png','Revisión moderna R2')]):
        x=i*900;d.text((x+25,15),label,font=font(32,True),fill='#263C48');panel(canvas,path,(x+15,75,x+885,650))
    canvas.save(R/'Antes_Despues.png')
print('R2_REVIEW_SHEETS_READY')
