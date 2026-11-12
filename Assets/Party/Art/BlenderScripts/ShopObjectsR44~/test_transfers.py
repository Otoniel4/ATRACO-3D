"""Traspasos del presentador real; manos controladas para aislar la propiedad del objeto."""
import json,re,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[4];OUT=ROOT/'Temp/Transfers44';OUT.mkdir(parents=True,exist_ok=True)
old=H.parent/'CounterContact40~'
# Reutiliza las transformaciones y los casos de regresión de R40.
setup=(old/'test_transfers.py').read_text().split('dotnet=')[0]
setup=setup.replace('H=Path(__file__).resolve().parent;',f'H=Path({str(old)!r});')
scope={'__file__':str(old/'test_transfers.py')};exec(setup,scope)
math=(ROOT/'Temp/CounterTransfer40/Math.cs').read_text()
math=math.replace('public static Quaternion Slerp(', '''public static Quaternion RotateTowards(Quaternion a,Quaternion b,float degrees){float dot=Math.Clamp(MathF.Abs(N.Quaternion.Dot(a.Q,b.Q)),0,1);float angle=2*MathF.Acos(dot)*180/MathF.PI;return Slerp(a,b,angle<.0001f?1:MathF.Min(1,degrees/angle));}
        public static Quaternion Slerp(''')
math=math.replace('public bool Destroyed, activeSelf=true;', '''public string name=>transform.name;
        private readonly Dictionary<Type,object> components=new();
        public T GetComponent<T>() where T:class =>components.TryGetValue(typeof(T),out var c)?c as T:null;
        public T AddComponent<T>() where T:class,new(){var value=new T();if(value is MonoBehaviour m)m.transform=transform;components[typeof(T)]=value;return value;}
        public bool Destroyed, activeSelf=true;''')
(OUT/'Math.cs').write_text(math)
stubs=(old/'TransferTests.cs').read_text()
stubs=stubs.replace('public static float time;', 'public static float time,deltaTime=1f/60f;')
stubs=stubs.replace('public Transform transform;', '''public Transform transform;
        public GameObject gameObject=>transform.gameObject;
        public T GetComponent<T>() where T:class=>gameObject.GetComponent<T>();''',1)
stubs=stubs.replace('public static class Time', '''public class ScriptableObject{}
    public class CreateAssetMenuAttribute:Attribute{public string menuName;}
    public class RangeAttribute:Attribute{public RangeAttribute(float a,float b){}}
    public static class Time''')
stubs=stubs.replace('public class ShopTaskSettings{','public class ShopTaskSettings{public ShopProductDefinition[] Products;')
stubs=stubs.replace('public class CounterExchange\n    {','''public class PedestrianReach:MonoBehaviour {public void SetObjectPose(Vector3 a,Vector3 b,float c,float[] d=null){}public Vector3 PocketPoint=>transform.TransformPoint(new Vector3(.22f,.95f,.05f));public bool RelaxedCarry=>false;public Quaternion HandFrame=>Quaternion.identity;}
    public class CommerceSupportHand:MonoBehaviour {public bool Contact=true;public bool Touches(Vector3 p)=>Contact;public void Follow(Vector3 p,Vector3 a,Vector3 b,float c,float[] d=null){}}
    public class CounterExchange
    {
        public PedestrianReach CashierHand;''')
(OUT/'Stubs.cs').write_text(stubs)
math=(OUT/'Math.cs').read_text().replace('public static Vector3 down=>-up;','public static Vector3 left=>-right;public static Vector3 down=>-up;');(OUT/'Math.cs').write_text(math)
dotnet=shutil.which('dotnet');version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll';pack=max((Path(parent).parent/'packs/Microsoft.NETCore.App.Ref').iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))));major=pack.name.split('.')[0]
ai=ROOT/'Assets/Party/Scripts/AI/CityLifeR5'
sources=[OUT/'Math.cs',OUT/'Stubs.cs',H/'TransferTests.cs']+[ai/(n+'.cs') for n in ['ShoppingPresentation','ShopProductDefinition','ShopProductInstance','HandPose']]+list((ai/'Domain').glob('*.cs'))
for main in ['TransferTests','Transfers44']:
    dll=OUT/(main+'.dll');rsp=OUT/(main+'.rsp');rsp.write_text('\n'.join(['-nologo','-target:exe','-main:'+main,f'-out:"{dll}"']+[f'-r:"{p}"' for p in (pack/f'ref/net{major}.0').glob('*.dll')]+[f'"{p}"' for p in sources]))
    subprocess.run([dotnet,str(compiler),'@'+str(rsp)],cwd=ROOT,check=True)
    dll.with_suffix('.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
    r=subprocess.run([dotnet,str(dll)],cwd=ROOT,capture_output=True,text=True);print(r.stdout+r.stderr,flush=True)
    r.check_returncode();(H/(main+'-results.txt')).write_text(r.stdout)
