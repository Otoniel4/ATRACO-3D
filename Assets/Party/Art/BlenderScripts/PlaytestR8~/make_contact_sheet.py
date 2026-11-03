from PIL import Image,ImageDraw
from pathlib import Path
B=Path(__file__).resolve().parent;sheet=Image.new('RGB',(1260,1100),'#e5e5df');draw=ImageDraw.Draw(sheet)
names=['Espalda','Caminar','Correr','Carrera_espalda','Civil_caminando','Musculo_corriendo']
for i,name in enumerate(names):
    image=Image.open(B/'renders'/str(name+'.png')).convert('RGB');x=(i%3)*420;y=(i//3)*550;sheet.paste(image,(x,y));draw.text((x+12,y+525),name.replace('_',' '),fill='#222222')
sheet.save(B/'renders/Revision_R8.png');print('CONTACT_SHEET_READY')
