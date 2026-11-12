"""Comprueba nombres de nodos reales en los FBX y ejecuta el resolutor C# real."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent
exec((H/'validate_integration.py').read_text().split('math=')[0])
inventory={}
for model in (ROOT/'Assets/Party/Art/Props/ShopObjects').glob('*.fbx'):
    names=re.findall(rb'((?:Support|Grip_R|Grip_L)(?:\.[0-9]+)?)\x00\x01Model',model.read_bytes())
    assert len(names)==3,(model.name,names)
    inventory[model.name]=[n.decode() for n in names]
assert len(inventory)==18
(OUT/'anchor-names.json').write_text(json.dumps(inventory,indent=2))
result=compile_test('AnchorNames',[H/'AnchorNameTests.cs',ROOT/'Assets/Party/Scripts/City/Editor/CityLifeR5/BlenderAssetNames.cs'],'AnchorNameTests')
(H/'anchor-results.txt').write_text(result)
