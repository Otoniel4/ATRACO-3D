"""Compila las cuatro asambleas con las DLL instaladas; no abre Unity ni ejecuta Play."""
from pathlib import Path
import subprocess,json
B=Path(__file__).resolve().parent;U=Path('C:/Program Files/Unity/Hub/Editor/6000.3.27f2/Editor/Data');P=Path('C:/Users/Alain/Atraco3D/Library/ScriptAssemblies');CSC=Path('C:/Program Files/dotnet/sdk/10.0.402/Roslyn/bincore/csc.dll');OUT=B/'compile_checks';OUT.mkdir(exist_ok=True)
runtime=list((U/'NetStandard/ref/2.1.0').glob('*.dll'))+list((U/'Managed/UnityEngine').glob('UnityEngine*.dll'))+[P/'Unity.InputSystem.dll']
editors=list((U/'Managed/UnityEngine').glob('UnityEditor*.dll'))+[P/'Unity.AI.Navigation.dll']
def compile(name,paths,extra=()):
    output=OUT/(name+'.dll');rsp=OUT/(name+'.rsp');args=['-nologo','-target:library','-langversion:9.0','-nostdlib+','-warn:4','-out:'+str(output)]+['-r:'+str(p) for p in runtime+list(extra) if p.is_file()]+[str(p) for p in paths]
    rsp.write_text('\n'.join('"'+a+'"' for a in args),encoding='utf-8');result=subprocess.run(['dotnet',str(CSC),'@'+str(rsp)],capture_output=True,text=True,encoding='utf-8');(OUT/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stdout+result.stderr;return output
ai=compile('Alarma.CityLife',list((B/'Patched/Runtime').rglob('*.cs')))
ai_editor=compile('Alarma.CityLife.Editor',list((B/'Patched/Editor').glob('*.cs')),editors+[ai])
game=compile('Alarma.Playtest',list((B/'Unity/Runtime').glob('*.cs')),[ai])
editor=compile('Alarma.Playtest.Editor',list((B/'Unity/Editor').glob('*.cs')),editors+[ai,ai_editor,game])
core_editor=compile('Alarma.Core.Editor',list((B/'Patched/CoreEditor').glob('*.cs')),editors+[P/'UnityEditor.TestRunner.dll',P/'UnityEngine.TestRunner.dll',U/'NetStandard/compat/2.1.0/shims/netfx/mscorlib.dll'])
report={'passed':True,'unity':'6000.3.27f2','assemblies':5,'unity_opened':False,'play_executed':False};(B/'compile_validation.json').write_text(json.dumps(report,indent=2));print('C_SHARP_COMPILED',json.dumps(report))
