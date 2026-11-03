"""Instala únicamente cambios R9 comprobados y conserva versiones, escenas y GUID."""
from pathlib import Path
import json, hashlib, shutil, os, re, sys

B=Path(__file__).resolve().parent
PROJECT=Path('C:/Users/Alain/Atraco3D'); PARTY=PROJECT/'Assets/Party'
REVIEW=PARTY/'Art/BlenderScripts/PlaytestR9~'
DELIVERY=B.parent.parent/'outputs/Alarma-Ciudad-3km-R9'
MAPPINGS=[('Unity/Runtime','Scripts/City/PlaytestR7'),('Unity/Editor','Scripts/City/Editor/PlaytestR7'),('Patched/Runtime','Scripts/AI/CityLifeR5'),('Patched/Editor','Scripts/City/Editor/CityLifeR5'),('Patched/CoreEditor','Scripts/Core/Editor')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def code(p): return re.sub(r'\s+','',p.read_text(encoding='utf-8-sig'))
def write(path,text): path.write_bytes(text.encode('utf-8'))
baseline=json.loads((B/'baseline.json').read_text(encoding='utf-8')); changes=[]; metas={}
for local,active in MAPPINGS:
    for source in sorted((B/local).rglob('*.cs')):
        dest=PARTY/active/source.relative_to(B/local)
        if dest.exists():
            assert str(dest) in baseline and sha(dest) in [baseline[str(dest)],sha(source)],'Fuente modificada por otro trabajo: '+str(dest)
            if code(source)==code(dest): continue
        changes.append((source,dest))
        meta=Path(str(dest)+'.meta')
        if meta.exists():metas[str(meta)]=sha(meta)
assert json.loads((B/'validation.json').read_text(encoding='utf-8'))['passed']
if '--check' in sys.argv:
    print(json.dumps({'changes':[str(d.relative_to(PARTY)) for s,d in changes],'existing_meta_files_preserved':len(metas),'assets_gb':sum(p.stat().st_size for p in (B/'export').rglob('*.fbx'))/1e9},indent=2));sys.exit(0)

recipes=['build_neighborhood.py','export_world.py','build_goods_doors.py','build_run.py','finish_metadata.py','review_sources_r9.py','render_reviews.py','validate_assets.py','check_roads.py','compile_code.py']
data=['world.json','materials.json','prop_materials.json','characters.json','district.json','lobby.json','map_changes.json','street_routes.json','city_map.png']
reports=['validation.json','export_validation.json','asset_validation.json','layout_validation.json','road_clearance.json','run_validation.json','world_checks.json','world_crowd_validation.json','compile_validation.json','baseline.json']
for root in (REVIEW,DELIVERY):
    root.mkdir(parents=True,exist_ok=True)
    for name in recipes+data+reports+['README.md','Villa_Alarma_3000_R9.blend','Elenco_R9.blend','install.py']:
        shutil.copy2(B/name,root/name)
    for name in ['Unity','Patched','export']:
        shutil.copytree(B/name,root/name,dirs_exist_ok=True)
    shutil.copytree(B/'tests',root/'tests',ignore=shutil.ignore_patterns('bin','obj','debug_traces.json','preview_traces.json'),dirs_exist_ok=True)
    (root/'renders').mkdir(exist_ok=True)
    for name in ['Barrio_y_escondite.png','Mercado_interior.png','Escondite.png','Carrera_R9.gif']:shutil.copy2(B/'renders'/name,root/'renders'/name)

# Se publican fuentes después de preparar todos los recursos que necesita el constructor.
stage=REVIEW/'staging~';stage.mkdir(exist_ok=True);records={}
changes.sort(key=lambda pair:pair[0].name=='AlarmaPlaytestBuilder.cs')
for index,(source,dest) in enumerate(changes):
    temp=stage/(str(index)+'_'+source.name);shutil.copy2(source,temp);dest.parent.mkdir(parents=True,exist_ok=True);os.replace(temp,dest);assert sha(source)==sha(dest);records[str(dest)]=sha(dest)
for meta,digest in metas.items():assert sha(Path(meta))==digest,'GUID alterado: '+meta
guide=PARTY/'docs/Ciudad-3km-R9.md';shutil.copy2(B/'README.md',guide)
oldguide=PARTY/'docs/Correcciones-Prueba-R8.md';old=oldguide.read_text(encoding='utf-8')
notice='> R8 fue rechazada tras la prueba. Revisión vigente: [Ciudad-3km-R9.md](Ciudad-3km-R9.md).\n\n'
if notice not in old:write(oldguide,notice+old)
def append(path,title,body):
    old=path.read_text(encoding='utf-8')
    if title not in old:write(path,old.rstrip()+'\n\n'+title+'\n\n'+body+'\n')
append(PROJECT/'AGENTS.md','## Corrección de integración R9 — 2026-11-02',
       'Alain rechazó R8 por puertas desalineadas, salida bloqueada e interiores/rutinas incompletas. Autorizó explícitamente reducir el mapa a 3 × 3 km; este tamaño sustituye los 4 × 4 km anteriores para la prueba vigente. Inicio dentro de El Escondite con cuatro puestos reservados para futuros compañeros, todavía sesión local. Se reconstruyen escondite y cinco tiendas en parcelas libres de la avenida diagonal; productos propios, estaciones reservadas, fila y caja. Todos los 153 FBX de ciudad se exportan de nuevo con tres anclas para corregir orientación/posición al importar; puertas y mercancía también. Carrera propia de apoyo/vuelo/codos en dieciocho modelos. Vegetación con viento conservada, macetas nuevas y accesos despejados. La fuente nueva está en Art/BlenderScripts/PlaytestR9~; se mantienen las rutas/asambleas de fuentes activas y las revisiones/Generated anteriores. Cinco asambleas compiladas; 191.739 comprobaciones de dominio y diez compras por cada tienda en 180 segundos sobre los cinco grafos; 18 personajes reimportados y límites de 3000 m verificados. Renders Blender revisados. El botón único Alarma/Crear y probar juego comprueba además anclas y colliders reales en Unity, salida del escondite, puertas abiertas/cerradas y compras antes de publicar la escena lista. RuntimeReview registra compras, caja y rutinas fallidas durante el Play de Alain. El agente no abrió Unity ni ejecutó Play. Guía docs/Ciudad-3km-R9.md. Integración física/visual, rendimiento y aprobación pendientes de prueba; no cerrar tareas ni hacer commit. Mantener Unity 6000.3.27f2. El transporte MCP de Blender continúa cerrado; se usa Blender portable con bpy y fuentes propias, como en las correcciones anteriores.')
append(PROJECT/'TASKS.md','### Corrección de prueba R9 — 2026-11-02',
       'R8 rechazada por Alain. Dentro de la misma corrección: mapa 3 × 3 km solicitado, inicio en escondite, cinco comercios reconstruidos con mercancía, fila y caja, calibración espacial FBX, puertas y recorrido de salida, animación de carrera y macetas. Fuentes y pruebas fuera del editor verificadas; comprobaciones físicas integradas en el mismo botón y prueba de Alain pendientes. Ver docs/Ciudad-3km-R9.md. No se cambia ninguna casilla ni se avanza a red.')
append(PARTY/'docs/LICENSES.md','## Ciudad y correcciones R9 — 2026-11-02',
       'Geometría de barrio comercial/escondite, productos, puertas, plano, clips de carrera y código generados para Alarma con bpy y C# propios. Conserva y recorta ciudad, personajes y vegetación propios de revisiones anteriores. Sin modelos, texturas ni animaciones descargados. Blender 4.5.15 portable para construir, exportar, reimportar y renderizar; renders no proceden de Unity. Recetas y evidencia en Art/BlenderScripts/PlaytestR9~. Las DLL instaladas de Unity se utilizan para compilación local y no se redistribuyen.')
record={'installed':True,'version':'playtest-r9-1','changed_source_files':records,'preserved_meta_sha256':metas,'guide':str(guide),'review':str(REVIEW),'delivery':str(DELIVERY),'unity_opened':False,'play_tested':False}
write(B/'installation.json',json.dumps(record,indent=2,ensure_ascii=False))
for root in (REVIEW,DELIVERY):
    shutil.copy2(B/'installation.json',root/'installation.json')
    values={str(p.relative_to(root)).replace('\\','/'):sha(p) for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json' and not p.name.endswith('.meta')}
    write(root/'SHA256SUMS.json',json.dumps(values,indent=2,ensure_ascii=False))
print('R9_INSTALLED',len(records),'fuentes; GUID conservados; Unity no ejecutado')
