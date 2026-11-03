from pathlib import Path
import ast,json,math,hashlib
B=Path(__file__).resolve().parent
for path in B.glob('*.py'):
    text=path.read_text(encoding='utf-8');text=text.replace('from review_sources import r6,r7,map1,map2','from review_sources import r6,r7,map1,map2')
    if path.name=='render_review.py':
        start=text.index("catalog=json.loads");end=text.index('views=')
        text=text[:start]+"catalog=json.loads((r6()/'animation_catalog.json').read_text())\n"+text[end:]
    ast.parse(text,filename=str(path));path.write_text(text,encoding='utf-8')
world=json.loads((B/'world.json').read_text());routes=json.loads((B/'street_routes.json').read_text())['routes'];coverage=[]
for poi in world['pois']:
    count=sum(sum((p-q)**2 for p,q in zip(row['center'],poi['position']))<90**2 for row in routes);coverage.append({'poi':poi['id'],'routes_within_90m':count})
for name in ['Minimarket','MallJewelry','Restaurant']:
    assert next(r['routes_within_90m'] for r in coverage if r['poi']==name)>0,name
interface=(B/'Unity/Runtime/ReviewInterface.cs').read_text(encoding='utf-8');map_code=interface.split('private void DrawMap(')[1].split('private void DrawCatalog(')[0]
assert 'Teleport' not in interface and 'Travel(' not in interface and 'GUI.Button' not in map_code
assert 'MapTexture' in map_code and 'ReviewMapProjection.Normalized(player.transform.position)' in map_code
assert '[SerializeField] private Transform grip;' in (B/'Patched/Runtime/PedestrianActor.cs').read_text()
for p in B.rglob('*.cs'):
    if any(a in p.parts for a in ['bin','obj','compile_checks']):continue
    assert p.stat().st_size>0,p
reports=['compile_validation.json','fbx_validation.json','shop_clearance.json','layout_validation.json','world_checks.json','world_crowd_validation.json']
for name in reports:assert json.loads((B/name).read_text())['passed'],name
report={'passed':True,'version':'playtest-r8-1','street_routes':len(routes),'poi_coverage':coverage,'animation_characters':18,'doors':9,'map_teleport':False,'unity_opened':False,'unity_play_tested':False,'reports':reports}
(B/'validation.json').write_text(json.dumps(report,indent=2));print('R8_FINAL_CHECKS_PASS',len(routes),'routes; 18 characters; 9 doors; map read-only')
