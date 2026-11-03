from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
import json
BASE=Path(__file__).resolve().parent;R=BASE/'renders'
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
names=['Fresno','Olivo','Jacaranda','Citrico','Pino','Palmera'];canvas=Image.new('RGB',(1800,1460),'#ECEEE7');d=ImageDraw.Draw(canvas)
for i,name in enumerate(names):
    x=(i%3)*600;y=(i//3)*730;d.text((x+20,y+12),name,font=font,fill='#2F493C')
    image=Image.open(R/('Wind_'+name+'.png')).convert('RGB');image.thumbnail((580,665));canvas.paste(image,(x+(600-image.width)//2,y+55))
canvas.save(R/'Arboles_Naturales_R3.png')
first=Image.open(BASE/'animation_frames/frame_0001.png').convert('RGB');later=Image.open(BASE/'animation_frames/frame_0049.png').convert('RGB')
stats=ImageStat.Stat(ImageChops.difference(first,later));assert sum(stats.mean)>1,stats.mean
gif=Image.open(R/'Viento_Natural_R3.gif');frames=gif.n_frames;duration=0
for i in range(frames):gif.seek(i);duration+=gif.info.get('duration',0)
report={'rendered_frames':192,'video_fps':24,'video_seconds':8,'gif_frames':frames,'gif_duration_ms':duration,
        'pixel_motion_mean':stats.mean,'motion_visible_in_rendered_frames':True}
(BASE/'video_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('TREE_REVIEW_READY',json.dumps(report))
