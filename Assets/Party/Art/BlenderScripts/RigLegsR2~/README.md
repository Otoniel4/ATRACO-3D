# Alarma — revisión de esqueletos y piernas R2 · 2026-11-01

Se revisaron los 18 personajes a petición de Alain. La apariencia extraña de Toñito provenía principalmente de una falta de centrado entre el pantalón y la pierna, junto con una rodilla baja y una pantorrilla poco definida. Las cadenas de huesos estaban unidas: no había una desconexión real en cadera, rodilla o tobillo.

## Correcciones realizadas

- Toñito: pantalón centrado sobre los huesos, bajos horizontales, rodillas elevadas de Z=0,5023 a 0,565 m y tobillos algo más próximos. Se reconstruyó el volumen de rodilla/pantorrilla y se reasignaron sus pesos; zapatos y huesos del pie se desplazaron juntos. El muslo oculto queda dentro del pantalón. Altura final 1,88 m; 2,802 triángulos.
- Tito Vacaciones y Clara Botones: centrado y bajos de sus pantalones cortos, con pesos coherentes con las piernas. La cintura conserva la altura de la prenda anterior.
- Lola Denim: el pantalón tenía influencias de manos en adornos/costuras y otras asignaciones inadecuadas. Se reasignó a cadera/piernas/pies. En chaqueta y top se retiraron influencias de piernas/pies y se trasladaron las de Head a Neck, conservando los pesos válidos de brazos y mangas.

## Qué se comprobó

Los 18 tienen 21 huesos, cadenas simétricas y sin separación entre muslo, pantorrilla, pie y dedos del pie. Los ejes de los huesos coinciden con sus extremos, y no hay escalas negativas. No se detectaron pesos hacia la pierna contraria por encima del umbral auditado, ni pesos de brazos/manos en la zona inferior del pantalón. Las tres prendas corregidas quedan centradas en las secciones medidas y cubren la piel al salir de sus bajos.

En Toñito se midió antes un desfase lateral de unos 4,4 cm entre pantalón y eje de pierna a Z≈0,639 m. En la sección equivalente corregida el desfase es inferior a 1 mm. Las secciones de muslo oculto comprobadas tampoco sobresalen de la tela en reposo.

Se renderizaron dos poses por actor: paso con rodilla a 75° y doble flexión a 80°, además de renders de reposo. Se revisaron las 36 capturas en hojas de contacto. La reimportación de los 18 FBX con Blender 4.5.15 confirmó altura, apoyo en Z=0 con tolerancia de 3 mm, pesos normalizados y cero vértices sin pesos. Giro de cabeza, flexión y recuperación de reposo también superados. Captura del viewport conectado revisada.

Estas comprobaciones cubren las poses y secciones indicadas. La revisión visual de Alain, el Avatar Humanoid en Unity y la prueba con clips finales continúan pendientes. No se han creado animaciones de juego, controladores ni lógica de movimiento.

## Archivos creados

- `Alarma_RigLegs_R2.blend`: elenco integrado; escena `RigReview_Player04_Muscle`, una `RigReview_<id>` por actor y `RigReview_Gallery`.
- `fbx/`: 18 FBX de esta revisión, con mallas y un rig por archivo; sin luces, cámaras ni clips.
- `renders/tonito_antes_despues.png` y `tonito_esqueleto.png`: comparación y diagrama de articulaciones reales. El diagrama es una proyección de los huesos; no representa geometría añadida al personaje.
- `renders/paso_18.png`, `rodillas_18.png`, `elenco_R2.png`: hojas de revisión. Cada actor conserva sus capturas individuales.
- `viewport_revision_r2.png`: captura del modelo corregido en Blender conectado.
- `correct_leg_alignment.py`: corrección reproducible sobre nuestro elenco anterior. Medidas de Toñito al principio del script.
- `export_review.py`, `audit_rigs.py`, `validate_cast.py`: exportación, poses y comprobaciones separadas.
- `audit_before.json`, `audit_after.json`, `validation.json`, `manifest.json`, logs y proyección de articulaciones.
- `baseline/elenco_gym_r1.blend`: fuente propia anterior; `character_primitives.py` es un módulo auxiliar importado por el corrector.
- `SHA256.json`: integridad de los archivos.

## Revisar en Blender

1. Abrir `Alarma_RigLegs_R2.blend` y elegir `RigReview_Player04_Muscle`; en el Blender conectado ya está abierta con el rig visible.
2. En Pose Mode, probar una rodilla y la cadera; para volver al reposo, seleccionar los huesos y borrar rotación/traslación de pose. Revisar la salida de la pierna bajo el pantalón desde frente y perfil.
3. Elegir otras escenas `RigReview_<id>` y comparar con `paso_18.png` y `rodillas_18.png`.

## Pasos para Unity

1. Mantener **Unity 6000.3.27f2**. Tras revisar el diseño, copiar los FBX elegidos a la carpeta de modelos dentro de `Assets/Party`. `RigLegsR2~` permanece excluida de la importación automática.
2. Configurar Rig = Humanoid, Create From This Model, Apply y Configure. Confirmar asignación y pose válida antes de hacer prefabs.
3. Probar los clips finales de caminar, correr y agacharse cuando estén disponibles; observar rodillas, cadera, bajos del pantalón y mangas.

No se abrió Unity ni se sustituyeron prefabs. El rig es propio de bpy, no Mixamo. Las versiones anteriores se conservan; no cerrar tareas de personajes/animación por estas pruebas.

## Regenerar

Desde esta carpeta, usando Blender 4.5.x:

```powershell
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P correct_leg_alignment.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P export_review.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P audit_rigs.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P validate_cast.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P make_skeleton_diagram.py
```

Las hojas de contacto se regeneran con `make_review_sheets.py` en Python con Pillow. El corrector se ejecuta sobre `baseline/`, conservando la revisión anterior. El módulo auxiliar no se ejecuta por separado.

## Explicación para aprender

Un esqueleto puede estar conectado y tener pesos que sumen uno, pero mover la prenda equivocada: una costura asignada a Hand seguirá la mano aunque esté en el pantalón. Por eso se comprueban tanto las cadenas como la región anatómica de cada influencia. La malla también debe rodear el mismo eje que los huesos; de otro modo una pierna puede atravesar un bajo de pantalón incluso en reposo. Construcción, exportación y auditoría se mantienen en scripts distintos para separar responsabilidades. No se añadió código C# ni un nuevo sistema de juego.

## Procedencia

Geometría, materiales planos y rigs propios, derivados de nuestras bases. Sin modelos, texturas ni clips descargados. Sin recursos de Mixamo incorporados. Las capturas y diagramas son diagnósticos del modelo propio; Arial instalada localmente solo aparece en rótulos de revisión.
