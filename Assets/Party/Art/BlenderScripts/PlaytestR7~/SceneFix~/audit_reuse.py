from pathlib import Path
import json
B=Path(__file__).resolve().parent;R7=B.parent/'playtest_r7';P=Path('C:/Users/Alain/Atraco3D/Assets/Party');world=json.loads((R7/'world.json').read_text(encoding='utf-8'));cast=json.loads((R7/'characters.json').read_text(encoding='utf-8'))['characters'];rows=[]
expected=['Art/'+c['file'] for c in world['cells']]+['Art/'+d['file'] for d in world['doors']]+['Art/Characters/'+c['id']+'.fbx' for c in cast]+['Art/Props/'+s['product']+'.fbx' for s in world['shops']]+['Art/Props/CashNote.fbx','Art/Props/Receipt.fbx']
for folder in sorted((P/'Generated').glob('AlarmaPrueba_*'),reverse=True):
    failure=folder/'BuildFailure.json'
    if not failure.exists():continue
    record=json.loads(failure.read_text(encoding='utf-8'))
    known=record.get('version')=='playtest-r7-1' and 'Cannot create a new scene additively with an untitled scene unsaved' in record.get('error','')
    missing=[name for name in expected if not (folder/name).is_file() or not Path(str(folder/name)+'.meta').is_file()]
    materials=list((folder/'Materials').glob('*.mat'))
    if known and not missing and materials:rows.append({'folder':str(folder),'expected_models_present':len(expected),'materials':len(materials)})
assert rows,'No se encontró la preparación reutilizable que mostraba el registro'
(B/'reuse_validation.json').write_text(json.dumps({'passed':True,'recoverable':rows},indent=2));print('REUSABLE_ART_FOUND',len(rows),'folders;',rows[0]['expected_models_present'],'models;',rows[0]['materials'],'materials')
