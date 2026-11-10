"""Instala el modelo verificado conservando archivos originales y metadatos de Unity."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
OUT = ART.parents[2] / 'Library/Alarma/DoorFrame34'
check = subprocess.run(['powershell','-NoProfile','-Command',
    "if (Get-Process Unity -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*Hub\\Editor*' }) { exit 1 }"], check=False)
if check.returncode:
    raise RuntimeError('Cierra Unity antes de instalar el modelo.')
evidence = json.loads((HERE/'export-results.json').read_text(encoding='utf-8'))
assert evidence['fbx_reimport_passed']
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
meta = ART/'City/Shops/Local_Escondite.fbx.meta'
before_meta = digest(meta)
backup = OUT/'Anterior'
backup.mkdir(exist_ok=True)
installed = {}
for source, target in [(OUT/'City/Shops/Local_Escondite.fbx',ART/'City/Shops/Local_Escondite.fbx'),
                       (OUT/'Alarma_Escondite_Validated.blend',ART/'BlenderSources~/Alarma_Escondite.blend')]:
    old = backup/target.name
    if not old.exists():
        shutil.copy2(target,old)
        assert digest(old) == digest(target)
    shutil.copy2(source,target)
    assert digest(source) == digest(target)
    installed[str(target.relative_to(ART))] = digest(target)
assert digest(meta) == before_meta
(HERE/'installation-results.json').write_text(json.dumps(installed,indent=2)+'\n',encoding='utf-8')
print('Instalados FBX y fuente Blender; metadatos conservados.')
