"""Láminas de revisión a partir de renders reales de la ciudad, sin imágenes generadas."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,textwrap
BASE=Path(__file__).resolve().parent
FONT=Path('C:/Windows/Fonts/arial.ttf');BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
plan=Image.open(BASE/'renders/Plan.png').convert('RGB')
canvas=Image.new('RGB',(2820,2360),'#F5F1E8');canvas.paste(plan,(30,120));d=ImageDraw.Draw(canvas)
d.text((45,24),'VILLA ALARMA · MAPA LOW POLY',font=font(52,True),fill='#243846')
d.text((45,82),'4.000 × 4.000 m · 16 km² · 64 sectores de 500 m · Norte arriba',font=font(25),fill='#52616A')
def project(p):return (30+2200*(.5+p[0]/4400),120+2200*(.5-p[1]/4400))
labels=['Mini Todo','Brilla Brilla / galería','Banco Sin Prisa','Comisaría y cárcel','Escondite de la banda',
        'Don Trueque / equipo','Camaleón / pintura','Ni Me Viste / ropa','Pizza Pánico','Metro Central',
        'Parking Bajo Perfil','Plaza del Pato','Alcantarilla comercial','Salida del alcantarillado']
for index,poi in enumerate(manifest['pois'],1):
    x,y=project(poi['position']);r=21
    d.ellipse((x-r,y-r,x+r,y+r),fill='#243846',outline='white',width=3)
    d.text((x,y),str(index),anchor='mm',font=font(23,True),fill='white')
    ly=250+(index-1)*122
    d.ellipse((2290,ly,2340,ly+50),fill='#243846')
    d.text((2315,ly+25),str(index),anchor='mm',font=font(25,True),fill='white')
    for line,text in enumerate(textwrap.wrap(labels[index-1],25)):
        d.text((2360,ly+line*35),text,font=font(29),fill='#243846')
    p=poi['position'];d.text((2360,ly+74),f'X {p[0]:.0f} · Y {p[1]:.0f} m',font=font(22),fill='#59696F')
d.text((2300,150),'LUGARES PRINCIPALES',font=font(31,True),fill='#243846')
# La cámara ortográfica cubre 4400 m en 2200 px: 250 px representan 500 m.
d.line((150,2240,400,2240),fill='#243846',width=10)
for x in [150,400]:d.line((x,2225,x,2255),fill='#243846',width=6)
d.text((275,2265),'500 m',anchor='mt',font=font(28,True),fill='#243846')
d.line((2140,280,2140,175),fill='#243846',width=9)
d.polygon([(2140,150),(2117,192),(2163,192)],fill='#243846')
d.text((2140,125),'N',anchor='mm',font=font(36,True),fill='#243846')
d.text((2300,2070),'Diseño estático para revisar.',font=font(27),fill='#243846')
d.text((2300,2115),'Tráfico y jugabilidad pendientes.',font=font(25),fill='#59696F')
canvas.save(BASE/'renders/Plan_Annotated.png')
sheet=Image.new('RGB',(1600,1250),'#F5F1E8');d=ImageDraw.Draw(sheet)
for i,(name,label) in enumerate([('Center','Centro y avenidas'),('ForestRiver','Río y bosque'),
                                ('Street','Escala con personajes'),('Minimarket_Inside','Interior del minimercado')]):
    x=(i%2)*800;y=(i//2)*625
    image=Image.open(BASE/'renders'/(name+'.png')).convert('RGB');image.thumbnail((780,550))
    sheet.paste(image,(x+(800-image.width)//2,y+55+(550-image.height)//2))
    d.text((x+20,y+12),label,font=font(27,True),fill='#243846')
sheet.save(BASE/'renders/Review_Sheet.png')
print('REVIEW_IMAGES_READY')
