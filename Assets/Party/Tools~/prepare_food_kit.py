"""Descarga oficial de arte CC0 a una carpeta de revisión ignorada por Unity."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Assets/Party/Art/ThirdParty~/KenneyFoodKit';OUT.mkdir(parents=True,exist_ok=True)
URL='https://kenney.nl/media/pages/assets/food-kit/83086fa91c-1719418518/kenney_food-kit.zip'
archive=OUT/'kenney_food-kit.zip'
if not archive.exists() or not zipfile.is_zipfile(archive):
    with urllib.request.urlopen(URL,timeout=60) as response:data=response.read()
    import io
    if not zipfile.is_zipfile(io.BytesIO(data)):
        if archive.exists() and not zipfile.is_zipfile(archive):archive.unlink()
        raise RuntimeError('El servidor no entregó un ZIP. No se importó ningún recurso.')
    archive.write_bytes(data)
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        dest=(OUT/entry.filename).resolve()
        if not dest.is_relative_to(OUT.resolve()):raise ValueError('Ruta ZIP fuera de destino')
    z.extractall(OUT)
inventory=[p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.suffix.lower() in ('.fbx','.glb','.gltf','.png','.txt')]
(OUT/'source.json').write_text(json.dumps(dict(source='https://kenney.nl/assets/food-kit',download=URL,license='CC0',sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=inventory,integrated=False),indent=2)+'\n')
print('\n'.join(p for p in inventory if p.endswith('.fbx') or 'icense' in p))
