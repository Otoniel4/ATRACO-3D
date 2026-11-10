"""Instala el lote validado con copia recuperable; conserva todos los GUID de Unity."""
import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ART=HERE.parents[2]
OUT=ART.parents[2]/'Library/Alarma/DoorReview36'
processes=subprocess.check_output(['powershell','-NoProfile','-Command',
    'Get-Process Unity -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path'],text=True)
assert '\\Editor\\Unity.exe' not in processes,'Cerrar Unity Editor antes de instalar.'
checks=json.loads((HERE/'sweep-results.json').read_text())
preserved=json.loads((HERE/'preserved-results.json').read_text())
assert len(checks)==len(preserved)==7
assert all(v['full_box_sweep_samples']==342 for v in checks.values())
assert max(v['error_m'] for v in json.loads((HERE/'contact-results.json').read_text()))<.006
assert 'REACH_REGRESSION_PASSED 96' in (HERE/'reach-code-results.txt').read_text()
backup=OUT/('Anterior_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True,exist_ok=False)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=[]
for name in sorted(checks):
    src=OUT/'City/Shops'/(name+'.fbx');dst=ART/'City/Shops'/src.name
    meta=dst.with_suffix('.fbx.meta');guid=digest(meta)
    shutil.copy2(dst,backup/dst.name)
    old=digest(dst);shutil.copy2(src,dst)
    assert digest(dst)==digest(src) and digest(meta)==guid
    manifest.append({'path':str(dst),'before':old,'after':digest(dst),'meta':guid})
source=OUT/'Alarma_Puertas36.blend';target=ART/'BlenderSources~'/source.name
if target.exists():shutil.copy2(target,backup/target.name)
shutil.copy2(source,target);assert digest(source)==digest(target)
(HERE/'installed.json').write_text(json.dumps({'backup':str(backup),'models':manifest,'source':str(target),'source_sha256':digest(target)},indent=2)+'\n',encoding='utf-8')
print('INSTALADOS',len(manifest),'FBX; GUID conservados. Fuente:',target)
print('RESPALDO',backup)
