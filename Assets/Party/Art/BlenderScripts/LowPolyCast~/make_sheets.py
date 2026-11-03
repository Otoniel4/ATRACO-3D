"""Compone hojas de revisión a partir de renders reales, sin alterar modelos."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CAST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['characters']
FONT = 'C:/Windows/Fonts/arial.ttf'

def sheet(name, actors, view, cols, cell, title):
    w, h = cell
    rows = (len(actors) + cols - 1) // cols
    canvas = Image.new('RGB', (cols*w, rows*h + 74), '#24282d')
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 18), title, font=ImageFont.truetype(FONT, 27), fill='#f0e5d0')
    for n, actor in enumerate(actors):
        image = Image.open(ROOT / 'renders' / actor['id'] / (view+'.png')).convert('RGB')
        image.thumbnail((w-16, h-48), Image.Resampling.LANCZOS)
        x, y = (n % cols)*w, 74+(n // cols)*h
        canvas.paste(image, (x+(w-image.width)//2, y))
        label = actor['label']
        font = ImageFont.truetype(FONT, 19)
        if draw.textlength(label, font=font) > w-10:
            font = ImageFont.truetype(FONT, 16)
        tw = draw.textlength(label, font=font)
        draw.text((x+(w-tw)/2, y+h-37), label, font=font, fill='#f4ebdd')
    canvas.save(ROOT / 'renders' / name)

sheet('elenco.png', CAST, 'front', 6, (300, 440), 'ALARMA · 18 personajes low poly')
sheet('rostros.png', CAST, 'head', 6, (300, 350), 'Rostros, peinados y expresiones')
sheet('roles.png', CAST[-4:], 'front', 4, (390, 565), 'La banda · Ladrón / Hacker / Distractor / Músculo')
sheet('perfiles.png', CAST, 'side', 6, (240, 355), 'Revisión de perfiles')
sheet('espaldas.png', CAST, 'back', 6, (240, 355), 'Revisión de espaldas y accesorios')
print('SHEETS_READY', len(CAST))
