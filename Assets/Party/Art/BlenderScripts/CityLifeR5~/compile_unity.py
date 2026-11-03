"""Compila contra las DLL reales instaladas; no inicia el editor ni ejecuta el motor Unity."""
from pathlib import Path
import subprocess,json
BASE=Path(__file__).resolve().parent
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.3.27f2/Editor/Data')
CSC=Path('C:/Program Files/dotnet/sdk/10.0.402/Roslyn/bincore/csc.dll')
OUT=BASE/'compile_checks';OUT.mkdir(exist_ok=True)
refs=list((UNITY/'NetStandard/ref/2.1.0').glob('*.dll'))
refs+=list((UNITY/'Managed/UnityEngine').glob('UnityEngine*.dll'))
PROJECT=Path('C:/Users/Alain/Atraco3D/Library/ScriptAssemblies')
refs+=[PROJECT/'Unity.InputSystem.dll']
def compile(name,files,extra=()):
    out=OUT/(name+'.dll');rsp=OUT/(name+'.rsp')
    args=['-nologo','-target:library','-langversion:9.0','-nostdlib+','-warn:4','-out:'+str(out)]
    args+=['-r:'+str(p) for p in refs+list(extra) if p.is_file()]
    args += [str(p) for p in files]
    rsp.write_text('\n'.join('"'+a+'"' for a in args),encoding='utf-8')
    result=subprocess.run(['dotnet',str(CSC),'@'+str(rsp)],capture_output=True,text=True)
    (OUT/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
    return out
runtime=compile('Alarma.CityLife',list((BASE/'Unity/Runtime').rglob('*.cs')))
report={'unity_version':'6000.3.27f2','runtime_compiled_against_installed_unity_dlls':True,
        'editor_compiled':False,'unity_editor_opened':False,'play_mode_tested':False}
editor=list((BASE/'Unity/Editor').glob('*.cs')) if (BASE/'Unity/Editor').exists() else []
if editor:
    editors=list((UNITY/'Managed/UnityEngine').glob('UnityEditor*.dll'))+[PROJECT/'Unity.AI.Navigation.dll',runtime]
    compile('Alarma.CityLife.Editor',editor,editors);report['editor_compiled']=True
(BASE/'compile_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('UNITY_SOURCE_COMPILATION_OK',json.dumps(report))
