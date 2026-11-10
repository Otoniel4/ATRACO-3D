"""Actualiza únicamente los datos de contacto desde la medición; no reescribe C# ni GUID."""
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
for kind,p in json.loads((HERE/'contacts.json').read_text()).items():
    path=ROOT/'Assets/Party/Data/ShopAnimations'/f'{kind}.asset'
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'^  Counter(?:Center|Normal|Width):.*\n','',text,flags=re.M)
    def vector(v):return '{'+', '.join(f'{k}: {n}' for k,n in zip('xyz',v))+'}'
    text += f"  CounterCenter: {vector(p['center'])}\n  CounterNormal: {vector(p['normal'])}\n  CounterWidth: {p['width']}\n"
    path.write_text(text,encoding='utf-8')
