"""Prueba estados reales y compila contra las DLL instaladas; no ejecuta Unity."""
import json, re, shutil, subprocess
from pathlib import Path
from validate_metadata import validate as validate_metadata
validate_metadata()
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OUT=ROOT/'Temp/ShopAnimation39';OUT.mkdir(parents=True,exist_ok=True)
AI=ROOT/'Assets/Party/Scripts/AI/CityLifeR5'
dotnet=shutil.which('dotnet')
version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll'
pack=max((Path(parent).parent/'packs/Microsoft.NETCore.App.Ref').iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))))
major=pack.name.split('.')[0];refs=pack/f'ref/net{major}.0'
def run(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

profiles=[]
for path in sorted((ROOT/'Assets/Party/Data/ShopAnimations').glob('*.asset')):
    text=path.read_text(encoding='utf-8')
    values=[float(re.search(r'^    '+field+r': ([\d.]+)',text,re.M)[1]) for field in ['Pick','Place','Scan','Pay','Change','Bag']]
    profiles.append('new CounterTiming { '+', '.join(f'{k}={v}f' for k,v in zip(['Pick','Place','Scan','Pay','Change','Bag'],values))+' }')
assert len(profiles)==6
(OUT/'Profiles.cs').write_text('using Alarma.AI.CityLife; static class Profiles { public static CounterTiming[] All = { '+','.join(profiles)+' }; }',encoding='utf-8')
sources=list((AI/'Domain').glob('*.cs'))+[HERE/'CommerceTests.cs',OUT/'Profiles.cs']
dll=OUT/'CommerceTests.dll';rsp=OUT/'tests.rsp'
rsp.write_text('\n'.join(['-nologo','-target:exe',f'-out:"{dll}"']+[f'-r:"{p}"' for p in refs.glob('*.dll')]+[f'"{p}"' for p in sources]),encoding='utf-8')
run([dotnet,str(compiler),'@'+str(rsp)])
dll.with_suffix('.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
evidence=run([dotnet,str(dll)]);print(evidence)
door=HERE.parent/'HideoutB1Fix~/DoorReview36~'
print(run([shutil.which('python'),str(door/'test_reach.py')]))
reach_dll=OUT/'PurchaseReachTests.dll';reach_rsp=OUT/'purchase-reach.rsp'
reach_sources=[ROOT/'Temp/DoorReach36/MathStubs.cs',door/'ReachRegression.cs',HERE/'PurchaseReachTests.cs']
reach_sources.append(HERE.parent/'CounterContact40~/CounterReachTests.cs')
reach_sources += [AI/(name+'.cs') for name in ['PedestrianReach','SurfaceHandPose','CommerceFingerPose']]
reach_rsp.write_text('\n'.join(['-nologo','-target:exe','-main:PurchaseReachTests',f'-out:"{reach_dll}"']+
    [f'-r:"{p}"' for p in refs.glob('*.dll')]+[f'"{p}"' for p in reach_sources]),encoding='utf-8')
run([dotnet,str(compiler),'@'+str(reach_rsp)])
shutil.copyfile(dll.with_suffix('.runtimeconfig.json'),reach_dll.with_suffix('.runtimeconfig.json'))
reach_result=run([dotnet,str(reach_dll)]);print(reach_result);evidence+='\n'+reach_result
(HERE/'test-results.txt').write_text(evidence,encoding='utf-8')
bee=next((ROOT/'Library/Bee/artifacts').rglob('Alarma.CityLife.rsp')).parent
compiled=[]
for assembly in ['Alarma.CityLife','Alarma.CityLife.Editor','Alarma.Playtest','Alarma.City.Editor']:
    content=(bee/(assembly+'.rsp')).read_text(encoding='utf-8-sig')
    if assembly=='Alarma.CityLife':
        for file in AI.rglob('*.cs'):
            # Nombre completo del archivo: «HandPose.cs» no debe darse por incluido por «SurfaceHandPose.cs».
            if '/'+file.name not in content.replace('\\','/'): content+='\n"'+file.as_posix()+'"\n'
    if assembly=='Alarma.City.Editor':
        for file in (ROOT/'Assets/Party/Scripts/City/Editor/City25').rglob('*.cs'):
            if file.name not in content: content+='\n"'+file.as_posix()+'"\n'
    content=re.sub(r'^-out:.*$',f'-out:"{(OUT/(assembly+".dll")).as_posix()}"',content,flags=re.M)
    content=re.sub(r'^-refout:.*$',f'-refout:"{(OUT/(assembly+".ref.dll")).as_posix()}"',content,flags=re.M)
    for name in compiled:
        content=re.sub(r'^(-r:|/reference:)"?[^\r\n"]*'+re.escape(name)+r'(?:\.ref)?\.dll"?$',
            lambda m:m[1]+'"'+(OUT/(name+'.ref.dll')).as_posix()+'"',content,flags=re.M)
    response=OUT/(assembly+'.rsp');response.write_text(content,encoding='utf-8')
    run([dotnet,str(compiler),'@'+str(response)])
    compiled.append(assembly);print('COMPILED',assembly)
(HERE/'validation.json').write_text(json.dumps(dict(profiles=6,compiled=compiled,unity_play_tested=False),indent=2)+'\n',encoding='utf-8')
