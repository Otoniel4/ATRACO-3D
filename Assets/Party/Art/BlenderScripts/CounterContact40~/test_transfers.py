"""Ejecuta ShoppingPresentation real con transformaciones matemáticas; sin Animator/PhysX."""
import json,re,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[4];OUT=ROOT/'Temp/CounterTransfer40';OUT.mkdir(parents=True,exist_ok=True)
s=(ROOT/'Temp/DoorReach36/MathStubs.cs').read_text()
s=s.replace('public bool Destroyed;', '''public bool Destroyed, activeSelf=true;
        public Renderer renderer;
        public void SetActive(bool value)=>activeSelf=value;
        public T[] GetComponentsInChildren<T>(bool value) where T:class => renderer is T r ? new[]{r} : Array.Empty<T>();''')
s=s.replace('public Vector3 localPosition;', '''public Vector3 localScale=new(1,1,1);
        public Vector3 lossyScale=>localScale;
        public Vector3 TransformPoint(Vector3 p)=>position+rotation*Vector3.Scale(p,localScale);
        public Vector3 InverseTransformPoint(Vector3 p){var v=Quaternion.Inverse(rotation)*(p-position);return new(v.x/localScale.x,v.y/localScale.y,v.z/localScale.z);}
        public void SetPositionAndRotation(Vector3 p,Quaternion q){position=p;rotation=q;}
        public Vector3 localPosition;''')
s=s.replace('public static float Distance(', '''public static Vector3 Scale(Vector3 a,Vector3 b)=>new(a.x*b.x,a.y*b.y,a.z*b.z);
        public static Vector3 Lerp(Vector3 a,Vector3 b,float t)=>a+(b-a)*Math.Clamp(t,0,1);
        public static float Distance(''')
s=s.replace('public static float MoveTowards(', 'public static float Clamp01(float v)=>Math.Clamp(v,0,1);\n        public static float MoveTowards(')
(OUT/'Math.cs').write_text(s)
dotnet=shutil.which('dotnet');version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll';pack=max((Path(parent).parent/'packs/Microsoft.NETCore.App.Ref').iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))));major=pack.name.split('.')[0]
sources=[OUT/'Math.cs',H/'TransferTests.cs',ROOT/'Assets/Party/Scripts/AI/CityLifeR5/ShoppingPresentation.cs']+list((ROOT/'Assets/Party/Scripts/AI/CityLifeR5/Domain').glob('*.cs'))
dll=OUT/'Transfers.dll';rsp=OUT/'tests.rsp';rsp.write_text('\n'.join(['-nologo','-target:exe',f'-out:"{dll}"']+[f'-r:"{p}"' for p in (pack/f'ref/net{major}.0').glob('*.dll')]+[f'"{p}"' for p in sources]))
subprocess.run([dotnet,str(compiler),'@'+str(rsp)],cwd=ROOT,check=True)
dll.with_suffix('.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
r=subprocess.run([dotnet,str(dll)],cwd=ROOT,check=True,capture_output=True,text=True)
(H/'transfer-results.txt').write_text(r.stdout);print(r.stdout)
