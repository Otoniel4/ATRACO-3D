import json
from pathlib import Path
h=Path(__file__).resolve().parent
for shop in json.loads((h.parents[1]/'City/Shops/shop_layouts.json').read_text())['shops']:
 print(shop['kind'], 'stations',shop['stations'],'products',shop['products'])
for kind,rows in json.loads((h/'surfaces.json').read_text()).items():
 print(kind)
 for r in rows:
  if any(x in r['name'] for x in ('TellerGlass','TellerSlot','OrderTop','LaneBelt','Scanner','CounterTop')):print(r)
