"""Compila políticas reales con sustitutos y ensamblados reales con las DLL instaladas; no abre Unity."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'ProjectSettings/ProjectVersion.txt').exists())
OUT = ROOT / 'Temp/City25RecoveryValidation'
OUT.mkdir(parents=True, exist_ok=True)
dotnet = shutil.which('dotnet')
assert dotnet
sdk_lines = subprocess.check_output([dotnet, '--list-sdks'], text=True).strip().splitlines()
sdk_version, sdk_parent = re.fullmatch(r'(\S+) \[(.+)\]', sdk_lines[-1]).groups()
compiler = Path(sdk_parent) / sdk_version / 'Roslyn/bincore/csc.dll'
refs_base = Path(sdk_parent).parent / 'packs/Microsoft.NETCore.App.Ref'
refs_version = sorted((p for p in refs_base.iterdir() if p.name.startswith('9.')), key=lambda p: tuple(map(int, p.name.split('.'))))[-1]
refs = refs_version / 'ref/net9.0'


def block(text, marker):
    start = text.index('{', text.index(marker))
    depth = 1
    end = start + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


flat_path = ROOT / 'Assets/Party/Scripts/City/Editor/CityLifeR5/FlatMaterialLibrary.cs'
recovery_path = ROOT / 'Assets/Party/Scripts/City/Editor/City25/City25BuildRecovery.cs'
builder_path = ROOT / 'Assets/Party/Scripts/City/Editor/City25/City25Builder.cs'
kit_path = ROOT / 'Assets/Party/Scripts/City/Editor/City25/City25Kit.cs'
data_path = ROOT / 'Assets/Party/Scripts/City/Editor/City25/City25Data.cs'
flat, builder, kit, data = (p.read_text(encoding='utf-8-sig') for p in (flat_path, builder_path, kit_path, data_path))
path_constants = '\n'.join(re.findall(r'^\s*public const string (?:Output|SceneSuffix|Scene|Revisions|Report) = [^\n]+;', data, re.M))
extracted = '''using System; using System.IO; using System.Linq; using UnityEditor; using UnityEngine; using Alarma.AI.CityLife.Editor;
namespace Alarma.AI.CityLife.Editor { public static class FlatMaterialLibrary { public static void EnsureFolder(string path) ''' + block(flat, 'public static void EnsureFolder(string path)') + ''' } }
namespace Alarma.City.Editor {
internal static class City25Paths {''' + path_constants + '''
public static bool IsCityScene(string path) ''' + block(data, 'public static bool IsCityScene') + ''' }
internal static class BuildPolicy {
public static void Handle(City25BuildRecovery recovery, Exception error) ''' + block(builder, 'catch (Exception error)') + '''
public static void PrepareOutput(string output) ''' + block(builder, 'private static void PrepareOutput') + '''
public static void SelectBuildScene(string scene) ''' + block(builder, 'private static void SelectBuildScene') + ' } }\n'
(OUT / 'ActualPolicyExtract.cs').write_text(extracted, encoding='utf-8')
rsp = ['-target:exe', '-out:"' + str(OUT / 'RecoveryTests.dll') + '"', '-nologo']
rsp += ['-r:"' + str(p) + '"' for p in refs.glob('*.dll')]
rsp += ['"' + str(p) + '"' for p in [HERE / 'EditorStubs.cs', HERE / 'RecoveryTests.cs', OUT / 'ActualPolicyExtract.cs', recovery_path]]
(OUT / 'Tests.rsp').write_text('\n'.join(rsp), encoding='utf-8')
compiled = subprocess.run([dotnet, str(compiler), '@' + str(OUT / 'Tests.rsp')], cwd=ROOT, capture_output=True, text=True)
print(compiled.stdout + compiled.stderr)
assert compiled.returncode == 0, 'Falló la compilación de políticas con sustitutos'
(OUT / 'RecoveryTests.runtimeconfig.json').write_text(json.dumps({'runtimeOptions': {'tfm': 'net9.0', 'framework': {'name': 'Microsoft.NETCore.App', 'version': '9.0.0'}}}), encoding='utf-8')
workspace = Path(tempfile.mkdtemp(prefix='workspace_', dir=OUT))
result = subprocess.run([dotnet, str(OUT / 'RecoveryTests.dll'), str(workspace)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
(HERE / 'publication-results.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
print(result.stdout + result.stderr)
assert result.returncode == 0, 'Falló una regresión de recuperación'
cases = int(re.search(r'PUBLICATION_TESTS_PASSED (\d+)', result.stdout)[1])
assert 'Directory.CreateDirectory' not in block(builder, 'private static void PrepareOutput')
assert 'FlatMaterialLibrary.EnsureFolder' in block(builder, 'private static void PrepareOutput')
assert 'EnsureFolder(output + "/Art")' in block(kit, 'private static GameObject MakeParked(')
assert 'EnsureFolder(output + "/Materials")' in block(kit, 'private static Material LightsOff(')
assert 'AssetDatabase.DeleteAsset' not in builder
assert builder.index('recovery.Publish(') > builder.index('AssetDatabase.ImportAsset(recovery.ScenePath')
assert builder.index('var stage = recovery.OpenStage();') > builder.index('PrepareOutput(output);')
print('PASS guardas de carpeta y orden de publicación en fuentes reales')

backup = runpy.run_path(str(ROOT / 'Assets/Party/Tools~/backup_project.py'))
current_scene = backup['current_scene']
current_scene.__globals__['ROOT'] = workspace / 'Backup'
city = workspace / 'Backup' / backup['CITY_OUTPUT']
city.mkdir(parents=True)
published_scene = backup['CITY_OUTPUT'] + '/Revisiones/R_' + 'a' * 32 + '/Scenes/Ciudad_2km.unity'
published_file = workspace / 'Backup' / published_scene
published_file.parent.mkdir(parents=True)
published_file.write_bytes(b'escena nueva')
assert current_scene() == backup['SCENE']
(city / 'BuildReport.json').write_text(json.dumps(dict(complete=True, scene=published_scene)), encoding='utf-8')
assert current_scene() == published_scene
(city / 'BuildReport.json').write_text(json.dumps(dict(complete=True, scene='../External.unity')), encoding='utf-8')
try:
    current_scene()
except ValueError:
    pass
else:
    raise AssertionError('Se aceptó una escena fuera de la ciudad.')
print('PASS el respaldo identifica la revisión publicada y rechaza rutas ajenas')

compiled_assemblies = []
bee = next((ROOT / 'Library/Bee/artifacts').glob('*/Alarma.City.Editor.rsp')).parent
for assembly in ['Alarma.CityLife.Editor', 'Alarma.City.Editor']:
    source = (bee / (assembly + '.rsp')).read_text(encoding='utf-8-sig')
    source = re.sub(r'^-out:.*$', '-out:"' + str(OUT / (assembly + '.dll')).replace('\\', '/') + '"', source, flags=re.M)
    source = re.sub(r'^-refout:.*$', '-refout:"' + str(OUT / (assembly + '.ref.dll')).replace('\\', '/') + '"', source, flags=re.M)
    if assembly == 'Alarma.City.Editor':
        source = source.replace(bee.relative_to(ROOT).as_posix() + '/Alarma.CityLife.Editor.ref.dll', (OUT / 'Alarma.CityLife.Editor.ref.dll').as_posix())
        if 'City25BuildRecovery.cs' not in source:
            source += '\n"' + str(recovery_path).replace('\\', '/') + '"\n'
    response = OUT / (assembly + '.rsp')
    response.write_text(source, encoding='utf-8')
    check = subprocess.run([dotnet, str(compiler), '@' + str(response)], cwd=ROOT, capture_output=True, text=True)
    print(assembly, 'exit', check.returncode, check.stdout, check.stderr)
    assert check.returncode == 0, assembly
    compiled_assemblies.append(assembly)

report = dict(policy_tests=cases, policy_tests_passed=True, folder_guards_source_check=True,
              compiled_assemblies=compiled_assemblies, unity_editor_opened=False, unity_native_importer_tested=False,
              source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [flat_path, recovery_path, builder_path, kit_path, data_path]})
(HERE / 'publication-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report))
