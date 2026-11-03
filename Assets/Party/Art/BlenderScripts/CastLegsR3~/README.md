# Alarma — ajuste del resto del elenco R3 · 2026-11-01

Alain aprobó la corrección R2 de Toñito y pidió aplicar el mismo criterio a los demás. Se ajustaron 17 personajes; el archivo integrado contiene los 18. El Toñito aprobado se conserva y se verificó su huella de geometría, pesos y huesos durante la construcción.

## Cambios

- Rodillas situadas aproximadamente a media distancia entre articulación de cadera y tobillo, con una ligera flexión frontal. Las posiciones se calculan para la altura de cada personaje.
- Tobillos algo más próximos, con zapatos y huesos Foot/Toes desplazados juntos.
- Pantorrillas y rodillas reconstruidas con volúmenes low poly, adaptados al cuerpo masculino/femenino y al tamaño del actor.
- Pantalones, costuras y bolsillos de pierna trasladados al nuevo eje y a la nueva posición de rodilla. Los anchos propios de las prendas se conservan: pantalón ancho, cargo, culotte y uniforme siguen siendo distintos.
- Pesos de la región inferior reasignados a Hips, UpperLeg, LowerLeg y Foot. La falda mantiene su caída desde la cadera y las piernas pasan por debajo.
- La piel oculta se ajusta con margen bajo la ropa. Alturas de personajes y colores existentes conservados.

## Verificaciones

Generación con Blender 4.5.15 LTS. Los 18 rigs tienen 21 huesos, cadenas inferiores conectadas, simetría y ejes coherentes. Se comprobaron las influencias por región y el centrado de los bajos de los pantalones cortos. El nuevo criterio de altura de rodilla se verifica para todo el elenco.

Los 18 FBX se reimportaron correctamente: altura y apoyo en Z=0 con tolerancia de 3 mm, pesos normalizados, cero vértices sin pesos y ausencia de luces/cámaras. Pasaron giro de cabeza, flexión y recuperación de reposo. Se renderizaron frente, perfil, espalda, tres cuartos y dos poses de diagnóstico por actor; las 36 poses de flexión y las hojas de vistas se revisaron. La galería está cargada en Blender conectado y su captura de viewport fue revisada.

Las pruebas cubren esas poses y secciones. La validación de Avatar Humanoid y los clips definitivos en Unity continúan pendientes; no se afirma ausencia de penetraciones en todas las animaciones futuras. Esta entrega no crea animaciones de juego ni controladores de movimiento.

## Archivos creados

- `Alarma_CastLegs_R3.blend`: fuente integrada. Escena `LegsR3_Gallery` y una `LegsR3_<id>` por actor.
- `fbx/`: 18 FBX, uno por actor, con mallas y esqueleto; sin luces/cámaras ni clips.
- `renders/<id>/`: seis vistas/poses por actor: frente, perfil, espalda, tres cuartos, paso y doble flexión.
- `renders/elenco.png`, `perfiles.png`, `espaldas.png`, `paso.png`, `rodillas.png` y `antes_despues.png`: hojas de revisión compuestas con renders reales.
- `viewport_gallery_r3.png`: captura de la galería en Blender conectado.
- `apply_cast_legs.py`: parámetros de proporción, reconstrucción, ajuste de ropa y huesos.
- `leg_tools.py`: funciones de ejes, transformación y pesos. `character_primitives.py`: módulo auxiliar propio importado, no ejecutar por separado.
- `export_review.py`, `audit_rigs.py`, `validate_cast.py`: exportación y comprobaciones.
- `changes.json`: medidas antes/después de los 17 y huella del Toñito conservado.
- `manifest.json`, `audit_after.json`, `validation.json`, logs y `pose_checks/`: medidas y resultados.
- `baseline/elenco_r2.blend`: nuestra fuente anterior para reconstruir esta corrección. `baseline/renders_r2/` contiene las seis referencias de comparación.
- `SHA256.json`: integridad de los archivos.

## Revisar en Blender

1. Abrir `Alarma_CastLegs_R3.blend` o elegir `LegsR3_Gallery` en el Blender conectado.
2. Elegir una escena `LegsR3_<id>` para inspeccionar frente y perfil. Mostrar su Armature y entrar en Pose Mode para flexionar cadera y rodilla.
3. Comparar con `renders/paso.png` y `renders/rodillas.png`; volver al reposo antes de guardar cambios propios.

## Pasos para Unity — después de la revisión visual

1. Mantener **Unity 6000.3.27f2**. Copiar los FBX elegidos a la carpeta de modelos dentro de `Assets/Party`.
2. En cada archivo, configurar Rig = Humanoid, Avatar Definition = Create From This Model, Apply y Configure. Validar asignación de huesos y pose antes de crear prefabs.
3. Cuando haya clips finales, probar caminar, correr y agacharse en cada tipo de prenda; observar cadera, rodillas, tobillos y bajos.

La carpeta `CastLegsR3~` está excluida de la importación automática. No se abrió Unity ni se sustituyeron prefabs. Los rigs siguen siendo propios de bpy, no Mixamo. No cerrar tareas de personajes/animación por estas comprobaciones.

## Regenerar

Desde esta carpeta, con Blender 4.5.x:

```powershell
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P apply_cast_legs.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P export_review.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P audit_rigs.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P validate_cast.py
```

Los parámetros están al principio de `apply_cast_legs.py`. Las hojas de revisión se regeneran con `make_sheets.py` en Python con Pillow, una vez terminados los renders.

## Explicación para aprender

Mover una rodilla exige ajustar también el eje de la pierna, la ropa y sus pesos. Esta corrección transforma cada zona entre cadera, rodilla y tobillo para que las superficies acompañen a los nuevos huesos. Los anchos de las prendas se mantienen, mientras la piel oculta recibe margen para reducir cruces con la tela. Construcción, utilidades, exportación y auditoría están separadas por responsabilidad. Esto aplica responsabilidad única sin añadir sistemas C# ni lógica de red.

## Altura de las rodillas

Medida del centro de la articulación izquierda en Z, en metros; el lado derecho es simétrico.

| Personaje | Antes | Ahora |
|---|---:|---:|
| Nico Naranja | 0.452 | 0.508 |
| Lola Denim | 0.414 | 0.466 |
| Tito Vacaciones | 0.459 | 0.517 |
| Violeta Turbo | 0.440 | 0.495 |
| Don Bigotín | 0.455 | 0.512 |
| Cora Tornillos | 0.421 | 0.474 |
| Paco Bolsillos | 0.467 | 0.526 |
| Rita Rebote | 0.439 | 0.494 |
| Bruno Cuadritos | 0.465 | 0.523 |
| Clara Botones | 0.426 | 0.480 |
| Guardia Bigotes | 0.473 | 0.532 |
| Guardia Chispa | 0.430 | 0.484 |
| Oficial Mostacho | 0.462 | 0.520 |
| Oficial Visera | 0.432 | 0.487 |
| Don Sigilo · Ladrón | 0.436 | 0.491 |
| Primo WiFi · Hacker | 0.413 | 0.464 |
| Abuelita Falsa · Distractor | 0.421 | 0.474 |

## Procedencia

Geometría, materiales y rigs propios, derivados del elenco R2. Sin modelos, texturas ni animaciones descargados ni archivos de Mixamo. Las hojas usan Arial instalada localmente para sus rótulos de revisión; no se exporta al juego.
