"""Publica R8 sin borrar versiones anteriores ni cambiar los GUID de fuentes existentes."""
from pathlib import Path
import json,hashlib,shutil,os
B=Path(__file__).resolve().parent;PROJECT=Path('C:/Users/Alain/Atraco3D');PARTY=PROJECT/'Assets/Party';REVIEW=PARTY/'Art/BlenderScripts/PlaytestR8~';DELIVERY=B.parent.parent/'outputs/Alarma-Prueba-Corregida-R8'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
baseline=json.loads((B/'baseline.json').read_text());changes=[]
for local,active in [('Unity/Runtime','Scripts/City/PlaytestR7'),('Unity/Editor','Scripts/City/Editor/PlaytestR7'),('Patched/Runtime','Scripts/AI/CityLifeR5'),('Patched/Editor','Scripts/City/Editor/CityLifeR5')]:
    for source in sorted((B/local).rglob('*.cs')):
        destination=PARTY/active/source.relative_to(B/local)
        if destination.exists():
            assert str(destination) in baseline and sha(destination) in [baseline[str(destination)],sha(source)],'Hay cambios ajenos: '+str(destination)
            if sha(destination)==sha(source):continue
        changes.append((source,destination))
assert json.loads((B/'validation.json').read_text())['passed']

# Prepara primero todos los recursos ignorados; publica el constructor activo al final.
scripts=['build_characters.py','finalize_backpack.py','build_doors.py','build_layout.py','filter_street_trees.py','repair_shop_graph.py','draw_map.py','render_review.py','render_motion.py','validate_exports.py','review_sources.py','compile_code.py','final_checks.py','make_contact_sheet.py','install.py']
reports=['validation.json','character_validation.json','fbx_validation.json','layout_validation.json','shop_clearance.json','world_checks.json','world_crowd_validation.json','world_corrections.json','compile_validation.json']
for root in (REVIEW,DELIVERY):
    root.mkdir(parents=True,exist_ok=True)
    for name in scripts+reports+['README.md','characters.json','world.json','street_routes.json','road_areas.json','door_materials.json','city_map.png','Elenco_Corregido_R8.blend']:
        shutil.copy2(B/name,root/name)
    for name in ['Unity','Patched','export']:
        shutil.copytree(B/name,root/name,dirs_exist_ok=True)
    shutil.copytree(B/'tests',root/'tests',ignore=shutil.ignore_patterns('bin','obj','debug_traces.json','preview_traces.json'),dirs_exist_ok=True)
    (root/'renders').mkdir(exist_ok=True)
    for name in ['Revision_R8.png','Carrera_R8.gif','Puerta_R8.png']:
        shutil.copy2(B/'renders'/name,root/'renders'/name)
    values={str(file.relative_to(root)).replace('\\','/'):sha(file) for file in root.rglob('*') if file.is_file() and file.name!='SHA256SUMS.json'}
    (root/'SHA256SUMS.json').write_text(json.dumps(values,indent=2,ensure_ascii=False),encoding='utf-8')

stage=REVIEW/'staging~';stage.mkdir(exist_ok=True);records={}
changes.sort(key=lambda pair:pair[0].name=='AlarmaPlaytestBuilder.cs')
for index,(source,destination) in enumerate(changes):
    temporary=stage/(str(index)+'_'+source.name);shutil.copy2(source,temporary);destination.parent.mkdir(parents=True,exist_ok=True);os.replace(temporary,destination);assert sha(source)==sha(destination);records[str(destination)]=sha(source)
guide=PARTY/'docs/Correcciones-Prueba-R8.md';shutil.copy2(B/'README.md',guide)
previous=PARTY/'docs/Prueba-Completa-R7.md';text=previous.read_text(encoding='utf-8');notice='> R7 fue rechazada tras la prueba. Corrección vigente: [Correcciones-Prueba-R8.md](Correcciones-Prueba-R8.md).\n\n'
if notice not in text:previous.write_text(notice+text,encoding='utf-8')
title='## Rechazo de la prueba integrada y correcciones R8 — 2026-11-02'
agents=PROJECT/'AGENTS.md';text=agents.read_text(encoding='utf-8')
if title not in text:
    agents.write_text(text.rstrip()+'\n\n'+title+'\n\nAlain rechazó la ejecución R7: caminar/correr, puertas y colisiones, población, mapa con traslado, árboles en pistas y bolsa lateral. R7 no queda aprobada. Se prepara R8 dentro de la misma corrección: seis clips propios y Blend Tree, bolsa del ladrón en espalda, cámara detrás, nueve puertas detalladas con colisión, comprobación de triángulos grandes y árboles importados frente al asfalto, reserva de pasos ante jugador/puertas, 4.153 recorridos de acera con pool y activación por carga de zona. Los grafos de las tres tiendas se contrastan con obstáculos y se ajustan; manos/agarres de NPC quedan serializados. M muestra plano y ubicación sin viajar. Fuentes activas conservan rutas/asambleas y GUID; receta/arte en Art/BlenderScripts/PlaytestR8~ y guía docs/Correcciones-Prueba-R8.md. Se conservan todas las carpetas Generated y R7 como fuente de ciudad. Dieciocho personajes y nueve puertas reimportados; cinco asambleas compiladas; pruebas de dominio y 180 s sobre los grafos corregidos pasan. Renders de Blender revisados; el transporte MCP está cerrado y se usa Blender portable aislado. No son capturas de Unity. El constructor comprobará el movimiento real de los clips importados y los prefabs antes de publicar; RuntimeReview.json registrará lo observado en Play. El agente no abrió Unity ni ejecutó Play. Falta la prueba y aprobación de Alain. No se cierran tasks ni se hace commit. Mantener 6000.3.27f2 y 4 × 4 km.\n',encoding='utf-8')
tasks=PROJECT/'TASKS.md';text=tasks.read_text(encoding='utf-8');title2='### Corrección de integración R8 — 2026-11-02'
if title2 not in text:tasks.write_text(text.rstrip()+'\n\n'+title2+'\n\nR7 rechazada por Alain durante Play. Se corrigen dentro de la prueba integrada actual: animaciones de locomoción, bolsa/cámara, puertas, contactos y rodeos de NPC, población de aceras, grafos de compra, mapa sin traslado y comprobación de vegetación contra asfalto. Entrega en docs/Correcciones-Prueba-R8.md. Verificaciones de fuentes superadas; prueba en Unity y aprobación pendientes. No se modifica ninguna casilla.\n',encoding='utf-8')
licenses=PARTY/'docs/LICENSES.md';text=licenses.read_text(encoding='utf-8');title3='## Correcciones de prueba R8 — 2026-11-02'
if title3 not in text:licenses.write_text(text.rstrip()+'\n\n'+title3+'\n\nClips de carrera, puertas, correas de bolsa, plano de ciudad y código propios; se conservan los modelos y materiales propios de R6/R7. Sin modelos, texturas ni animaciones descargados. Blender 4.5.15 portable exporta y reimporta; las capturas de revisión son renders Blender. Fuentes en Art/BlenderScripts/PlaytestR8~. Las DLL de Unity se utilizan localmente para comprobar compilación, sin redistribuirlas.\n',encoding='utf-8')
record={'installed':True,'version':'playtest-r8-1','changed_source_files':records,'guide':str(guide),'review':str(REVIEW),'delivery':str(DELIVERY),'unity_opened':False,'play_tested':False}
(B/'installation.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
for root in [REVIEW,DELIVERY]:shutil.copy2(B/'installation.json',root/'installation.json')
print('R8_INSTALLED',len(records),'source files; assets and documents preserved; Unity not run')
