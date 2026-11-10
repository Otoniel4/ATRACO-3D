"""Incluye la revisión guardada y sus dependencias; conserva las otras revisiones en disco."""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='Assets/Party/Generated/Ciudad2km/Revisiones/'
report=json.loads((ROOT/'Assets/Party/Generated/Ciudad2km/BuildReport.json').read_text(encoding='utf-8-sig'))
scene=report['scene'];assert scene.startswith(BASE)
active=scene[len(BASE):].split('/')[0]
guid_map={}
for p in (ROOT/'Assets').rglob('*.meta'):
    m=re.search(r'^guid: ([a-f0-9]{32})',p.read_text(encoding='utf-8-sig',errors='replace'),re.M)
    if m:guid_map[m[1]]=Path(str(p)[:-5])
pending=[p for p in (ROOT/BASE/active).rglob('*') if p.is_file()]
seen=set();revisions={active};missing=set();extensions={'.unity','.prefab','.asset','.mat','.controller','.overridecontroller','.anim','.meta','.playable','.shadergraph','.shadersubgraph'}
while pending:
    p=pending.pop()
    if p in seen:continue
    seen.add(p)
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith(BASE):
        revision=rel[len(BASE):].split('/')[0]
        if revision not in revisions:
            revisions.add(revision);pending.extend(q for q in (ROOT/BASE/revision).rglob('*') if q.is_file())
    if p.suffix.lower() not in extensions:continue
    for guid in re.findall(r'guid: ([a-f0-9]{32})',p.read_text(encoding='utf-8-sig',errors='replace')):
        if guid.startswith('0000000000000000'):continue
        dependency=guid_map.get(guid)
        if dependency and dependency.is_file():pending.append(dependency)
        elif not dependency:missing.add(guid)
# Los GUID de paquetes son externos a Assets, pero están fijados por packages-lock.json.
for p in (ROOT/'Library/PackageCache').rglob('*.meta'):
    if not missing:break
    m=re.search(r'^guid: ([a-f0-9]{32})',p.read_text(encoding='utf-8-sig',errors='replace'),re.M)
    if m:missing.discard(m[1])
assert not missing,'GUID sin resolver: '+str(sorted(missing))
path=ROOT/'.gitignore';text=path.read_text(encoding='utf-8-sig')
begin='# BEGIN current-city-backup';end='# END current-city-backup'
text=re.sub(re.escape(begin)+r'.*?'+re.escape(end)+r'\n?', '', text, flags=re.S).rstrip()+'\n\n'
text+=begin+'\n/'+BASE+'*\n'
for revision in sorted(revisions):text+='!/'+BASE+revision+'/\n!/'+BASE+revision+'.meta\n'
text+=end+'\n';path.write_text(text,encoding='utf-8')
print('Revisiones requeridas:',sorted(revisions),'Archivos recorridos:',len(seen),'GUID ausentes: 0')
