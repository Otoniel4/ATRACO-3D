"""Compila el flujo real con sustitutos y las asambleas reales con las DLL instaladas."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
OUT = ROOT / 'Temp/City25DoorValidation'
OUT.mkdir(parents=True, exist_ok=True)
DOTNET = shutil.which('dotnet')
assert DOTNET
sdk = subprocess.check_output([DOTNET, '--list-sdks'], text=True).strip().splitlines()[-1]
version, sdk_root = sdk.split(' [', 1)
sdk_root = Path(sdk_root.rstrip(']'))
compiler = sdk_root / version / 'Roslyn/bincore/csc.dll'
major = version.split('.')[0]
pack = sdk_root.parent / 'packs/Microsoft.NETCore.App.Ref'
ref_version = max((p.name for p in pack.iterdir() if p.name.startswith(major + '.')),
                  key=lambda v: tuple(map(int, v.split('.'))))
ref = pack / ref_version / 'ref' / ('net' + major + '.0')
interaction = ROOT / 'Assets/Party/Scripts/City/PlaytestR7/ReviewDoorInteraction.cs'


def execute(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def run_tests(name, files):
    dll = OUT / (name + '.dll')
    rsp = ['-nologo', '-target:exe', f'-out:"{dll}"']
    rsp += [f'-r:"{p}"' for p in ref.glob('*.dll')]
    rsp += [f'"{p}"' for p in files]
    response = OUT / (name + '.rsp')
    response.write_text('\n'.join(rsp), encoding='utf-8')
    execute([DOTNET, str(compiler), '@' + str(response)])
    (OUT / (name + '.runtimeconfig.json')).write_text(json.dumps(dict(runtimeOptions=dict(
        tfm='net' + major + '.0', framework=dict(name='Microsoft.NETCore.App', version=ref_version)))), encoding='utf-8')
    return execute([DOTNET, str(dll)])


evidence = run_tests('DoorInteractionTests', (HERE / 'DoorInteractionTests.cs', interaction))
count = int(re.search(r'DOOR_INTERACTION_TESTS_PASSED (\d+)', evidence)[1])
traffic = ROOT / 'Assets/Party/Scripts/AI/CityLifeR5'
approach_files = [HERE / 'PedestrianDoorApproachTests.cs', HERE / 'ShopDoorTests~/UnityStubs.cs']
approach_files += [traffic / (name + '.cs') for name in ('TrafficGraph', 'CityTrafficController', 'PedestrianMovement')]
approach_files += sorted((traffic / 'Domain').glob('*.cs'))
approach = run_tests('PedestrianDoorApproachTests', approach_files)
approach_count = int(re.search(r'PEDESTRIAN_DOOR_APPROACH_TESTS_PASSED (\d+)', approach)[1])
(HERE / 'interaction-test-results.txt').write_text(evidence + '\n' + approach, encoding='utf-8')
print(evidence + '\n' + approach)

bee = next((ROOT / 'Library/Bee/artifacts').rglob('Alarma.Playtest.rsp')).parent
compiled = []
for assembly in ('Alarma.CityLife', 'Alarma.Playtest'):
    source = (bee / (assembly + '.rsp')).read_text(encoding='utf-8-sig')
    source = re.sub(r'^-out:.*$', f'-out:"{(OUT / (assembly + ".dll")).as_posix()}"', source, flags=re.M)
    source = re.sub(r'^-refout:.*$', f'-refout:"{(OUT / (assembly + ".ref.dll")).as_posix()}"', source, flags=re.M)
    if assembly == 'Alarma.Playtest':
        source = re.sub(r'^(-r:|/reference:)"?[^\r\n"]*Alarma\.CityLife(?:\.ref)?\.dll"?$',
                        lambda m: m[1] + '"' + (OUT / 'Alarma.CityLife.ref.dll').as_posix() + '"', source, flags=re.M)
    response = OUT / (assembly + '.rsp')
    response.write_text(source, encoding='utf-8')
    execute([DOTNET, str(compiler), '@' + str(response)])
    compiled.append(assembly)
    print('COMPILED', assembly)

result = dict(interaction_tests=count, pedestrian_approach_tests=approach_count,
              compiled_assemblies=compiled, unity_play_tested=False,
              interaction_source_sha256=hashlib.sha256(interaction.read_bytes()).hexdigest())
(HERE / 'interaction-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
