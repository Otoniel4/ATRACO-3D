"""Ejecuta las pruebas del grafo y del movimiento real con un modelo físico analítico."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
OUT = ROOT / 'Temp' / 'SidewalkValidation'
OUT.mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, str(HERE/'verify_graph.py')], cwd=ROOT, check=True)

dotnet = shutil.which('dotnet')
if dotnet is None:
    raise RuntimeError('Hace falta el SDK de .NET para ejecutar las pruebas analíticas.')
sdk = subprocess.check_output([dotnet,'--list-sdks'],text=True).strip().splitlines()[-1]
version,parent = re.fullmatch(r'(\S+) \[(.+)\]',sdk).groups()
compiler = Path(parent)/version/'Roslyn/bincore/csc.dll'
packs = Path(parent).parent/'packs/Microsoft.NETCore.App.Ref'
pack = max((p for p in packs.iterdir() if re.fullmatch(r'\d+\.\d+\.\d+',p.name)),key=lambda p:tuple(map(int,p.name.split('.'))))
major = pack.name.split('.')[0]
ref = pack/f'ref/net{major}.0'
street = ROOT/'Assets/Party/Scripts/AI/Street'
sources = [HERE/'StreetStubs.cs',HERE/'StreetTests.cs',street/'SidewalkGraph.cs',street/'SidewalkWalker.cs',street/'SidewalkClearance.cs',
           HERE/'VisitTests.cs',street/'SidewalkVisit.cs',HERE/'PopulationTests.cs',street/'SidewalkPopulation.cs',
           ROOT/'Assets/Party/Scripts/Core/Contracts/ITrafficSignals.cs']
domain = street.parent / 'CityLifeR5/Domain'
sources.extend(domain / name for name in ('PedestrianRoutine.cs', 'ShopQueue.cs', 'ShopService.cs', 'CounterChoreography.cs'))
sources.append(HERE / 'CounterTests.cs')
assembly = OUT/'StreetTests.dll'
args = ['-target:exe', f'-out:"{assembly}"', '-nologo']
args.extend(f'-r:"{p}"' for p in ref.glob('*.dll'))
args.extend(f'"{p}"' for p in sources)
rsp = OUT/'StreetTests.rsp'
rsp.write_text('\n'.join(args),encoding='utf-8')
subprocess.run([dotnet,str(compiler),'@'+str(rsp)],cwd=ROOT,check=True)
(OUT/'StreetTests.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':f'net{major}.0','framework':{'name':'Microsoft.NETCore.App','version':f'{major}.0.0'}}}),encoding='utf-8')
result = subprocess.run([dotnet,str(assembly)],cwd=ROOT,check=True,capture_output=True,text=True,encoding='utf-8')
(HERE/'runtime-results.txt').write_text(result.stdout,encoding='utf-8')
print(result.stdout,end='')
