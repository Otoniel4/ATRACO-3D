from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess
B=Path(__file__).resolve().parent;rows=json.loads((B/'video_frames.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for row in rows:
    p=B/'video_frames'/(str(row['index']).zfill(5)+'.png');im=Image.open(p).convert('RGB');draw=ImageDraw.Draw(im);draw.rectangle((0,668,960,720),fill='#152832');draw.text((20,682),row['label']+' | Blender: revision horneada',font=font,fill='#ffffff');im.save(p)
video=B/'renders/Compras_Filas_Manos_R6.mp4';subprocess.run(['ffmpeg','-y','-v','error','-framerate','8','-i',str(B/'video_frames/%05d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=nb_read_frames,width,height','-show_entries','format=duration','-of','json',str(video)]));assert int(probe['streams'][0]['nb_read_frames'])==len(rows)
(B/'video_validation.json').write_text(json.dumps({'passed':True,'frames':len(rows),'seconds':float(probe['format']['duration']),'width':960,'height':720,'source':'Blender, C# baked traces, not Unity Play'},indent=2))
files=sorted((B/'renders').glob('Mano_*.png'));thumbs=[];smallfont=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for p in files:
    im=Image.open(p).convert('RGB');im.thumbnail((230,270));tile=Image.new('RGB',(240,300),'#26343b');tile.paste(im,((240-im.width)//2,0));ImageDraw.Draw(tile).text((8,277),p.stem.replace('Mano_','').replace('_',' '),font=smallfont,fill='white');thumbs.append(tile)
gallery=Image.new('RGB',(6*240,3*300),'#26343b')
for i,tile in enumerate(thumbs):gallery.paste(tile,((i%6)*240,(i//6)*300))
gallery.save(B/'renders/Manos_18_Personajes_R6.png')
contact=Image.new('RGB',(1280,960),'#26343b')
for i,index in enumerate([60,100,165,255]):
    im=Image.open(B/'video_frames'/(str(index).zfill(5)+'.png')).convert('RGB');im.thumbnail((640,480));contact.paste(im,((i%2)*640,(i//2)*480))
contact.save(B/'renders/Resumen_Compras_R6.png');print('MEDIA_VERIFIED',len(rows),'frames',float(probe['format']['duration']),'seconds')
