"""Ejecuta PedestrianReach y SurfaceHandPose reales con matemáticas System.Numerics, sin Unity."""
import json
import re
import shutil
import subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
OUT=ROOT/'Temp/DoorReach36';OUT.mkdir(parents=True,exist_ok=True)
source=(HERE.parents[1]/'HoldGripFix~/GripTests.cs').read_text(encoding='utf-8-sig').split('class GripTests')[0]
source=source.replace('using Alarma.Player.Items;','')
source=source.replace('public Vector3 right =>','public Vector3 forward => rotation*Vector3.forward;\n        public Vector3 right =>')
source=source.replace('public static float Clamp(float','public static float MoveTowards(float a,float b,float step)=>a+Math.Clamp(b-a,-step,step);\n        public static float Clamp(float')
stubs=OUT/'MathStubs.cs';stubs.write_text(source,encoding='utf-8')
dotnet=shutil.which('dotnet')
version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll'
pack=max((Path(parent).parent/'packs/Microsoft.NETCore.App.Ref').iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))))
major=pack.name.split('.')[0];refs=pack/f'ref/net{major}.0'
ai=ROOT/'Assets/Party/Scripts/AI/CityLifeR5'
dll=OUT/'ReachRegression.dll';rsp=OUT/'ReachRegression.rsp'
rsp.write_text('\n'.join(['-nologo','-target:exe',f'-out:"{dll}"']+[f'-r:"{p}"' for p in refs.glob('*.dll')]+
    [f'"{p}"' for p in (stubs,HERE/'ReachRegression.cs',ai/'PedestrianReach.cs',ai/'SurfaceHandPose.cs',ai/'CommerceFingerPose.cs')]),encoding='utf-8')
subprocess.run([dotnet,str(compiler),'@'+str(rsp)],check=True)
dll.with_suffix('.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
result=subprocess.run([dotnet,str(dll)],check=True,capture_output=True,text=True)
(HERE/'reach-code-results.txt').write_text(result.stdout,encoding='utf-8');print(result.stdout)
