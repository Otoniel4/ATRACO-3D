from pathlib import Path
import subprocess,json
from PIL import Image,ImageChops,ImageStat
BASE=Path(__file__).resolve().parent;files=sorted((BASE/'animation_frames').glob('frame_*.png'));assert len(files)==288,len(files)
listing=BASE/'animation_frames/frames.txt';listing.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files),encoding='utf-8')
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True).stdout
video=BASE/'renders/Ciudad_Viva_R5.mp4';gif=BASE/'renders/Ciudad_Viva_R5.gif'
run('ffmpeg','-y','-r','12','-f','concat','-safe','0','-i',str(listing),'-frames:v','288','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video))
run('ffmpeg','-y','-i',str(video),'-filter_complex','fps=8,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',str(gif))
probe=json.loads(run('ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)))['streams'][0]
assert int(probe['nb_frames'])==288 and abs(float(probe['duration'])-24)<.001,probe
movement=ImageStat.Stat(ImageChops.difference(Image.open(files[0]).convert('RGB'),Image.open(files[24]).convert('RGB'))).mean;assert sum(movement)>1
report={'video':probe,'motion_pixel_mean':movement,'blender_preview_not_unity_capture':True,'passed':True}
(BASE/'video_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('CITY_LIFE_VIDEO_READY',json.dumps(report))
