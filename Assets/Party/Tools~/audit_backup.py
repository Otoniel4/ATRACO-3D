"""Inventario de cambios y comprobación de la escena guardada antes de respaldar Git."""
import collections,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
paths=set(git('ls-files','--modified','--others','--exclude-standard','-z').decode().split('\0'))-{''}
rows=[(p,(ROOT/p).stat().st_size) for p in paths if (ROOT/p).is_file()]
print('Cambios:',len(rows),'MiB:',round(sum(s for _,s in rows)/1048576,2))
print('Grupos:',dict(collections.Counter('/'.join(p.split('/')[:3]) for p,_ in rows)))
print('Mayores:',[(p,round(s/1048576,2)) for p,s in sorted(rows,key=lambda r:r[1],reverse=True)[:8]])
oversize=[p for p,s in rows if s>=100*1048576]
assert not oversize, 'Superan límite GitHub: '+str(oversize)
report=json.loads((ROOT/'Assets/Party/Generated/Ciudad2km/BuildReport.json').read_text(encoding='utf-8-sig'))
scene=report['scene'];assert (ROOT/scene).is_file() and (ROOT/(scene+'.meta')).is_file()
ignored=subprocess.run(['git','check-ignore',scene],cwd=ROOT,capture_output=True)
assert ignored.returncode==1,'Escena actual ignorada'
print('Escena guardada:',scene,'Versión:',report.get('version','').split('|')[0])
assert 'm_Camera' in (ROOT/scene).read_text(encoding='utf-8-sig') or 'Camera:' in (ROOT/scene).read_text(encoding='utf-8-sig'),'Escena sin cámara'
print('Respaldo: escena presente, meta presente, límite por archivo verificado.')
