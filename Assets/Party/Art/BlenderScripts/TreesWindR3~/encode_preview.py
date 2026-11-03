"""Codifica los renders reales a MP4/GIF y comprueba el vídeo sin abrir Unity."""
from pathlib import Path
import json
import subprocess

BASE = Path(__file__).resolve().parent
FRAMES = BASE / 'animation_frames/frame_%04d.png'
OUT = BASE / 'renders'
OUT.mkdir(exist_ok=True)


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


run('ffmpeg', '-y', '-framerate', '24', '-start_number', '1', '-i', str(FRAMES),
    '-frames:v', '192', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', str(OUT / 'Viento_Natural_R3.mp4'))
run('ffmpeg', '-y', '-framerate', '24', '-start_number', '1', '-i', str(FRAMES),
    '-filter_complex', 'fps=12,scale=600:-1:flags=lanczos,split[a][b];'
    '[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a',
    '-loop', '0', str(OUT / 'Viento_Natural_R3.gif'))
info = json.loads(run('ffprobe', '-v', 'error', '-show_entries',
    'stream=codec_name,width,height,r_frame_rate,nb_frames,duration',
    '-of', 'json', str(OUT / 'Viento_Natural_R3.mp4')))['streams'][0]
assert info['codec_name'] == 'h264' and int(info['nb_frames']) == 192, info
assert info['width'] == 900 and info['height'] == 900, info
assert info['r_frame_rate'] == '24/1' and abs(float(info['duration']) - 8) < .001, info
(BASE / 'video_probe.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print('VIDEO_VALIDATED', json.dumps(info))
