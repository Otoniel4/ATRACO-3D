"""Vídeo/GIF a partir de los fotogramas renderizados; valida duración y movimiento."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageChops,ImageStat
BASE=Path(__file__).resolve().parent;OUT=BASE/'renders'
files=sorted((BASE/'animation_frames').glob('frame_*.png'));assert len(files)==96,len(files)
listing=BASE/'animation_frames/frames.txt'
listing.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files),encoding='utf-8')
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True).stdout
run('ffmpeg','-y','-r','12','-f','concat','-safe','0','-i',str(listing),'-frames:v','96',
    '-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'Macetas_Pasto_Viento_R4.mp4'))
run('ffmpeg','-y','-i',str(OUT/'Macetas_Pasto_Viento_R4.mp4'),'-filter_complex',
    'fps=12,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a',
    '-loop','0',str(OUT/'Macetas_Pasto_Viento_R4.gif'))
probe=json.loads(run('ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration','-of','json',str(OUT/'Macetas_Pasto_Viento_R4.mp4')))['streams'][0]
assert int(probe['nb_frames'])==96 and abs(float(probe['duration'])-8)<.001,probe
first=Image.open(files[0]).convert('RGB');later=Image.open(files[24]).convert('RGB')
movement=ImageStat.Stat(ImageChops.difference(first,later)).mean;assert sum(movement)>1,movement
gif=Image.open(OUT/'Macetas_Pasto_Viento_R4.gif');duration=0
for i in range(gif.n_frames):gif.seek(i);duration+=gif.info.get('duration',0)
report={'video':probe,'gif_frames':gif.n_frames,'gif_duration_ms':duration,'pixel_motion_mean':movement,'passed':True}
(BASE/'video_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PLANT_VIDEO_READY',json.dumps(report))
