"""Materiales de plantas que reutilizan el shader de viento ya entregado; sin abrir Unity."""
from pathlib import Path
import json,shutil,uuid,re
BASE=Path(__file__).resolve().parent;C=json.loads((BASE/'settings.json').read_text())
OUT=BASE/'Unity';(OUT/'Materials').mkdir(parents=True,exist_ok=True)
assert (OUT/'SharedSupport~/TreeWindURP.shader').is_file()
shader_guid=uuid.uuid5(uuid.NAMESPACE_URL,'Alarma/Vegetation/NaturalWindR3').hex
template=(BASE/'baseline/material_template.mat').read_text()
for name,value in C['palette'].items():
    label='WindPlant_'+name;rgb=[int(value[i:i+2],16)/255 for i in [0,2,4]]
    body=re.sub(r'm_Name: .*', 'm_Name: '+label,template)
    body=re.sub(r'- _BaseColor: .*',f'- _BaseColor: {{r: {rgb[0]}, g: {rgb[1]}, b: {rgb[2]}, a: 1}}',body)
    assert shader_guid in body
    path=OUT/'Materials'/(label+'.mat');path.write_text(body,encoding='utf-8')
    guid=uuid.uuid5(uuid.NAMESPACE_URL,'Alarma/Vegetation/PlantsR4/'+label).hex
    path.with_suffix('.mat.meta').write_text(f'fileFormatVersion: 2\nguid: {guid}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n',encoding='utf-8')
source=(OUT/'SharedSupport~/TreeWindURP.shader').read_text()
cache=Path('C:/Users/Alain/Atraco3D/Library/PackageCache');includes=[]
for include in re.findall(r'#include "([^"]+)"',source):
    _,package,relative=include.split('/',2)
    assert any((p/relative).is_file() for p in cache.glob(package+'@*')),include
    includes.append(include)
report={'plant_materials':len(C['palette']),'shader_guid':shader_guid,'shared_with_trees_R3':True,
        'includes_found':includes,'shader_compiled_in_unity':False,'game_verified':False}
(BASE/'unity_static_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PLANT_UNITY_FILES_PREPARED',len(C['palette']),'materials')
