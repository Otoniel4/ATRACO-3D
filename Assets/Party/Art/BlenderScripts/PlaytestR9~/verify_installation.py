"""Comprueba instalación y recetas entregadas sin abrir Unity."""
from pathlib import Path
import hashlib,json,re,importlib.util,py_compile
B=Path(__file__).resolve().parent;P=Path('C:/Users/Alain/Atraco3D')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((B/'installation.json').read_text(encoding='utf-8'));baseline=json.loads((B/'baseline.json').read_text(encoding='utf-8'))
changed=record['changed_source_files']
for name,value in changed.items():assert sha(Path(name))==value,name
for name,value in baseline.items():
    if name not in changed:assert sha(Path(name))==value,'Cambios fuera del alcance: '+name
for name,value in record['preserved_meta_sha256'].items():assert sha(Path(name))==value,name
assert '6000.3.27f2' in (P/'ProjectSettings/ProjectVersion.txt').read_text(encoding='utf-8')
menus=[]
for file in (P/'Assets/Party/Scripts').rglob('*.cs'):
    s=file.read_text(encoding='utf-8-sig')
    if '[MenuItem("Alarma/Crear y probar juego",false,0)]' in s:menus.append(file)
assert len(menus)==1
for root in [Path(record['review']),Path(record['delivery'])]:
    manifest=json.loads((root/'SHA256SUMS.json').read_text(encoding='utf-8'))
    for name,value in manifest.items():assert sha(root/name)==value,str(root/name)
    spec=importlib.util.spec_from_file_location('sources_installed',root/'review_sources_r9.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for fn in ['r6','r7','r8','map1','map2','plants']:getattr(module,fn)()
    for script in root.glob('*.py'):py_compile.compile(str(script),doraise=True)
report={'passed':True,'version':record['version'],'changed_sources':len(changed),'preserved_meta_files':len(record['preserved_meta_sha256']),'menu_entries':len(menus),'package_hashes_verified':True,'other_sources_unchanged':True,'unity_version':'6000.3.27f2','unity_opened':False,'play_tested':False}
(B/'installation_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('INSTALLATION_VERIFIED',json.dumps(report))
