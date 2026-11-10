"""Pruebas matemáticas del código real y compilación aislada contra Unity instalado."""
from pathlib import Path
import json
import re
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OUT=ROOT/'Temp/HoldGripValidation'
OUT.mkdir(parents=True,exist_ok=True)
dotnet=shutil.which('dotnet')
version,parent=re.fullmatch(r'(\S+) \[(.+)\]',subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]).groups()
compiler=Path(parent)/version/'Roslyn/bincore/csc.dll'
packs=Path(parent).parent/'packs/Microsoft.NETCore.App.Ref'
pack=max(packs.iterdir(),key=lambda p:tuple(map(int,p.name.split('.'))))
major=pack.name.split('.')[0]
refs=pack/f'ref/net{major}.0'
items=ROOT/'Assets/Party/Scripts/Player/Items'
def execute(args):
    r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout
rsp=OUT/'GripTests.rsp'
rsp.write_text('\n'.join(['-nologo','-target:exe',f'-out:"{OUT / "GripTests.dll"}"']+
    [f'-r:"{p}"' for p in refs.glob('*.dll')]+[f'"{p}"' for p in [HERE/'GripTests.cs',items/'TwoBoneIk.cs',items/'HandGripPose.cs']]),encoding='utf-8')
execute([dotnet,str(compiler),'@'+str(rsp)])
(OUT/'GripTests.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':pack.name}}}))
result=execute([dotnet,str(OUT/'GripTests.dll')])
print(result)
bee=max((ROOT/'Library/Bee/artifacts').rglob('Alarma.Player.rsp'),key=lambda p:p.stat().st_mtime).parent
compiled=[]
for assembly in ('Alarma.Player','Alarma.Playtest','Alarma.Player.Editor','Alarma.Playtest.Editor','Alarma.City.Editor'):
    source=(bee/(assembly+'.rsp')).read_text(encoding='utf-8-sig')
    source=re.sub(r'^-out:.*$',f'-out:"{(OUT/(assembly+".dll")).as_posix()}"',source,flags=re.M)
    source=re.sub(r'^-refout:.*$',f'-refout:"{(OUT/(assembly+".ref.dll")).as_posix()}"',source,flags=re.M)
    for previous in compiled:
        source=re.sub(r'^(-r:|/reference:)"?[^\r\n"]*'+re.escape(previous)+r'(?:\.ref)?\.dll"?$',
            lambda m:m[1]+'"'+(OUT/(previous+'.ref.dll')).as_posix()+'"',source,flags=re.M)
    if assembly=='Alarma.Player' and 'HandGripPose.cs' not in source:
        source+='\n"'+(items/'HandGripPose.cs').as_posix()+'"\n'
    if assembly=='Alarma.Player.Editor' and not re.search(r'Alarma\.Core(?:\.ref)?\.dll',source):
        source+='\n-r:"'+(ROOT/'Library/ScriptAssemblies/Alarma.Core.dll').as_posix()+'"\n'
    response=OUT/(assembly+'.rsp');response.write_text(source,encoding='utf-8')
    execute([dotnet,str(compiler),'@'+str(response)])
    compiled.append(assembly)
    print('COMPILED',assembly)
(HERE/'code-results.txt').write_text(result+'\nCOMPILED '+', '.join(compiled)+'\nUnity Play no ejecutado.\n',encoding='utf-8')
