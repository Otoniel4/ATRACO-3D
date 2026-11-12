"""Instala los FBX aprobados y sus datos; no abre Unity ni modifica escenas."""
import ast, json, re, shutil, uuid
from pathlib import Path
root = Path(__file__).resolve().parents[3]
party = root/'Assets/Party'
source = party/'Art/BlenderScripts/ShopObjectsR44~'
target = party/'Art/Props/ShopObjects'
target.mkdir(parents=True, exist_ok=True)
def vector(p): return dict(zip(('x','y','z'), p))
items=[]
for obj in json.loads((source/'catalog.json').read_text()):
    name=obj['id']; grips=obj['grips_unity']
    right=grips['Grip_R']; left=grips['Grip_L']; fingers=[0,0,1]; normal=[-1,0,0]; curl=1.5
    two=name in ('Pizza','Camiseta')
    if two:
        fingers=[0,0,1];normal=[-1,0,0];curl=.65
    elif name in ('Bolso','Maletin'):
        fingers=[0,0,1];normal=[0,-1,0];curl=2.2
    elif name in ('Anillo','Reloj','Collar'):
        # Las piezas pequeñas se muestran sobre la palma abierta, no dentro del puño.
        right=[0,grips['Support'][1]-.004,0]
        fingers=[0,0,1];normal=[0,1,0];curl=.12
        if name=='Collar': fingers=[0,-.25,1];curl=0
    elif name=='Sobre':
        fingers=[0,0,1];normal=[0,-1,0];curl=.45
    elif name=='Vaso':
        right=[.033,.07,0] # El cuerpo del vaso, no la tapa ni la pajita.
    items.append(dict(id=name,shop=obj['shop'],support=vector(grips['Support']),right=vector(right),left=vector(left),
        fingers=vector(fingers),normal=vector(normal),leftFingers=vector(fingers),leftNormal=vector([1,0,0]),curl=curl,twoHands=two))
    if not (target/obj['fbx']).exists() or (source/obj['fbx']).read_bytes()!=(target/obj['fbx']).read_bytes():
        shutil.copy2(source/obj['fbx'], target/obj['fbx'])
recipe=(party/'Art/BlenderScripts/build_shop_objects_r44.py').read_text()
palette=ast.literal_eval(re.search(r'for n,c,m,r in (\[.*\]):mat',recipe)[1])
materials=[dict(name='R44_'+n,color=dict(zip(('r','g','b','a'),(*c,1))),metallic=m,roughness=r) for n,c,m,r in palette]
(target/'catalog.json').write_text(json.dumps(dict(items=items,materials=materials),indent=2)+'\n')
for path in [target,*target.iterdir(),* (party/'Scripts/AI/CityLifeR5').glob('*.cs'),* (party/'Scripts/City/Editor/City25').glob('*.cs')]:
    if path.suffix=='.meta':continue
    meta=Path(str(path)+'.meta')
    if not meta.exists():
        guid=uuid.uuid5(uuid.NAMESPACE_URL,path.relative_to(root).as_posix()).hex
        meta.write_text('fileFormatVersion: 2\nguid: '+guid+'\n'+('folderAsset: yes\n' if path.is_dir() else ''))
print('18 modelos instalados, 6 negocios, materiales y agarres escritos.')
