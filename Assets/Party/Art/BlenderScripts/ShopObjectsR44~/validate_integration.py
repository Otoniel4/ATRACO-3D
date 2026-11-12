"""Código real contra DLL instaladas y matemáticas de rigs; no ejecuta Unity."""
import json,re,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[4];OUT=ROOT/'Temp/ShopObjects44';OUT.mkdir(parents=True,exist_ok=True)
AI=ROOT/'Assets/Party/Scripts/AI/CityLifeR5'
dotnet=shutil.which('dotnet');version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll'
pack=max((Path(parent).parent/'packs/Microsoft.NETCore.App.Ref').iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))));major=pack.name.split('.')[0]
def run(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(result.stdout,flush=True)
    if result.returncode:raise RuntimeError(result.stderr+result.stdout)
    return result.stdout
def compile_test(name,sources,main):
    dll=OUT/(name+'.dll');rsp=OUT/(name+'.rsp')
    rsp.write_text('\n'.join(['-nologo','-target:exe','-main:'+main,f'-out:"{dll}"']+[f'-r:"{p}"' for p in (pack/f'ref/net{major}.0').glob('*.dll')]+[f'"{p}"' for p in sources]))
    run([dotnet,str(compiler),'@'+str(rsp)])
    dll.with_suffix('.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
    return run([dotnet,str(dll)])
math=(ROOT/'Temp/DoorReach36/MathStubs.cs').read_text()
math=math.replace('public static float Distance(','''public static Vector3 SmoothDamp(Vector3 current,Vector3 target,ref Vector3 velocity,float time,float speed,float dt){var delta=target-current;var step=MathF.Min(delta.magnitude,speed*dt);return current+delta.normalized*step;}
        public static float Distance(''')
(OUT/'Math.cs').write_text(math)
stubs=(H.parent/'HideoutB1Fix~/DoorReview36~/ReachRegression.cs').read_text().split('class ReachRegression')[0]
stubs=stubs.replace('RightHand,Spine','RightHand,Spine,LeftUpperArm,LeftLowerArm,LeftHand')
stubs=stubs.replace('string name=bone==','string name=bone==HumanBodyBones.LeftUpperArm?"UpperArm.L":bone==HumanBodyBones.LeftLowerArm?"LowerArm.L":bone==HumanBodyBones.LeftHand?"Wrist.L":bone==')
(OUT/'Stubs.cs').write_text(stubs)
evidence=compile_test('Grips',[OUT/'Math.cs',OUT/'Stubs.cs',H/'GripTests.cs']+[AI/(n+'.cs') for n in ['PedestrianReach','CommerceSupportHand','SurfaceHandPose','CommerceFingerPose']], 'GripTests44')
(H/'grip-results.txt').write_text(evidence)
bee=next((ROOT/'Library/Bee/artifacts').rglob('Alarma.CityLife.rsp')).parent
compiled=[]
for assembly in ['Alarma.CityLife','Alarma.CityLife.Editor','Alarma.Playtest','Alarma.City.Editor']:
    content=(bee/(assembly+'.rsp')).read_text(encoding='utf-8-sig')
    folders={'Alarma.CityLife':AI,'Alarma.CityLife.Editor':ROOT/'Assets/Party/Scripts/City/Editor/CityLifeR5','Alarma.City.Editor':ROOT/'Assets/Party/Scripts/City/Editor/City25'}
    if assembly in folders:
        for file in folders[assembly].rglob('*.cs'):
            if file.name not in content:content+='\n"'+file.as_posix()+'"\n'
    content=re.sub(r'^-out:.*$',f'-out:"{(OUT/(assembly+".dll")).as_posix()}"',content,flags=re.M)
    content=re.sub(r'^-refout:.*$',f'-refout:"{(OUT/(assembly+".ref.dll")).as_posix()}"',content,flags=re.M)
    for name in compiled:
        content=re.sub(r'^(-r:|/reference:)"?[^\r\n"]*'+re.escape(name)+r'(?:\.ref)?\.dll"?$',lambda m:m[1]+'"'+(OUT/(name+'.ref.dll')).as_posix()+'"',content,flags=re.M)
    rsp=OUT/(assembly+'.rsp');rsp.write_text(content)
    run([dotnet,str(compiler),'@'+str(rsp)]);compiled.append(assembly)
print('COMPILED',compiled)
