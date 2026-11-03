"""Instala solo la corrección de escenas, sin tocar exportaciones ni sus .meta."""
from pathlib import Path
import hashlib
import json
import os
import shutil

FIX = Path(__file__).resolve().parent
BUILD = FIX.parent / 'playtest_r7'
PROJECT = Path('C:/Users/Alain/Atraco3D')
PARTY = PROJECT / 'Assets/Party'
REVIEW = PARTY / 'Art/BlenderScripts/PlaytestR7~'
DELIVERY = BUILD.parent.parent / 'outputs/Alarma-Prueba-Completa-R7'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

baseline = json.loads((FIX / 'baseline.json').read_text(encoding='utf-8'))
changes = []
for source in sorted((BUILD / 'Unity/Editor').glob('*.cs')):
    destination = PARTY / 'Scripts/City/Editor/PlaytestR7' / source.name
    changes.append((source, destination, 'Unity/Editor/' + source.name))
changes.append((BUILD / 'Patched/Editor/CityLifeSceneBuilder.cs',
                PARTY / 'Scripts/City/Editor/CityLifeR5/CityLifeSceneBuilder.cs',
                'Patched/Editor/CityLifeSceneBuilder.cs'))

# Detecta cambios ajenos antes de escribir la primera fuente activa.
for source, destination, _ in changes:
    if str(destination) in baseline:
        assert destination.exists(), 'Fuente activa ausente: ' + str(destination)
        assert digest(destination) in (baseline[str(destination)], digest(source)), 'Fuente modificada fuera de esta corrección: ' + str(destination)
    else:
        assert not destination.exists() or digest(destination) == digest(source), 'Conflicto con fuente nueva: ' + str(destination)

# Guarda comprobaciones y receta dentro de una carpeta ignorada por Unity.
report = {
    'version': 'playtest-r7-2',
    'compiled_assemblies': json.loads((BUILD / 'compile_validation.json').read_text(encoding='utf-8')),
    'scene_policy_cases': 5,
    'scene_policy_passed': True,
    'reusable_art': json.loads((FIX / 'reuse_validation.json').read_text(encoding='utf-8')),
    'unity_opened': False,
    'play_executed': False,
    'remaining': 'Alain debe recompilar y probar el menú dentro de Unity.',
}
(FIX / 'validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
records = {}
stage = REVIEW / 'SceneFix~' / 'staging~'
stage.mkdir(parents=True, exist_ok=True)
for index, (source, destination, key) in enumerate(changes):
    temporary = stage / (str(index) + '_' + source.name)
    shutil.copy2(source, temporary)
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temporary, destination)
    assert digest(destination) == digest(source)
    records[str(destination)] = digest(source)

for root in (REVIEW, DELIVERY):
    values = json.loads((root / 'SHA256SUMS.json').read_text(encoding='utf-8'))
    for source, _, key in changes:
        target = root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        values[key] = digest(target)
    for name in ('README.md', 'compile_validation.json'):
        shutil.copy2(BUILD / name, root / name)
        values[name] = digest(root / name)
    for name in ('ScenePolicyChecks.cs', 'ScenePolicyChecks.csproj', 'NuGet.Config',
                 'audit_reuse.py', 'reuse_validation.json', 'validation.json', 'install_fix.py'):
        target = root / 'SceneFix~' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIX / name, target)
        values['SceneFix~/' + name] = digest(target)
    # La prueba empaquetada debe apuntar a la fuente de su propia entrega.
    csproj = root / 'SceneFix~/ScenePolicyChecks.csproj'
    csproj.write_text(csproj.read_text(encoding='utf-8').replace('../playtest_r7/Unity/', '../Unity/'), encoding='utf-8')
    values['SceneFix~/ScenePolicyChecks.csproj'] = digest(csproj)
    (root / 'SHA256SUMS.json').write_text(json.dumps(values, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

guide = PARTY / 'docs/Prueba-Completa-R7.md'
shutil.copy2(BUILD / 'README.md', guide)

instructions = PROJECT / 'AGENTS.md'
title = '## Corrección de escenas sin guardar y recuperación de importación R7.2 — 2026-11-02'
content = instructions.read_text(encoding='utf-8')
if title not in content:
    content += '\n\n' + title + '\n\n'
    content += ('La prueba de Alain falló con Cannot create a new scene additively with an untitled scene unsaved. '
                'El diálogo anterior permitía continuar con una escena Untitled sin ruta; crear otra aditivamente no es válido. '
                'R7.2 sustituye ese diálogo por respaldos automáticos dentro de Assets/Party/Scenes/Backups/BeforePlaytest_<fecha>; '
                'asigna ruta a las escenas sin nombre y guarda copia de las escenas existentes con cambios, sin sobrescribir originales. '
                'Comprueba la precondición y crea la escena temporal antes de importar. '
                'Reutiliza arte preparado de los intentos fallidos por ese error y de sus puntos de control; '
                'los prefabs/datos/escena se crean en una carpeta nueva y pueden referenciar el arte anterior. '
                'No borrar las carpetas Generated anteriores. Se conservan sus .meta. '
                'Las cinco asambleas compilan contra las DLL instaladas; cinco casos de política de respaldo pasan. '
                'Dos lotes contienen los 295 FBX obligatorios y 406 materiales cada uno. '
                'La comprobación de disco no sustituye la prueba de carga de Unity. '
                'El agente no abrió Unity ni ejecutó Play. Alain debe cancelar el diálogo viejo, esperar compilación y volver a pulsar '
                'Alarma/Crear y probar juego. Guía actualizada en docs/Prueba-Completa-R7.md; fuentes y evidencias en '
                'Art/BlenderScripts/PlaytestR7~. No cerrar tareas ni hacer commit sin la prueba y confirmación de Alain.\n')
    instructions.write_text(content, encoding='utf-8')

result = {'installed': True, 'files': records, 'guide': str(guide), 'version': 'playtest-r7-2', 'unity_opened': False, 'play_executed': False}
(FIX / 'install_result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('SCENE_FIX_INSTALLED: ' + str(len(records)) + ' fuentes, documentación y copias verificadas; sin ejecutar Unity.')
