> Revisión posterior: [Piernas del resto del elenco R3](CastLegs-R3.md), 2026-11-01.

> Revisión posterior: [Esqueletos y piernas R2](RigLegs-R2.md), 2026-11-01.

> Revisión más reciente de Toñito: [Torso de gimnasio R1](Tonito-Gym-R1.md), 2026-11-01. El archivo original de este elenco conserva su versión anterior.

# Alarma — elenco low poly · 2026-11-01

17 personajes nuevos y la mujer aprobada: 18 en total. Diez civiles, dos guardias, dos policías y los cuatro roles de jugador: Ladrón, Hacker, Distractor y Músculo.

La cabeza geométrica, los ojos simples y el pelo facetado continúan la dirección aprobada por Alain. Las variantes añaden gafas, bigotes, cejas, peinados, prendas y accesorios. El ladrón lleva un saco exagerado, el hacker una gorra con antenas, el distractor un disfraz con bigote y Toñito brazos enormes y un gorrito diminuto. Son diseños de revisión; todavía requieren la revisión visual de Alain.

La entrega está en `Assets/Party/Art/BlenderScripts/LowPolyCast~`. Las rutas siguientes son relativas a esa carpeta.

## Archivos

- `Alarma_LowPoly_Cast.blend`: fuente Blender 4.5.15; escena `Cast_Gallery` con el elenco y una escena `Cast_<id>` por personaje, en el origen y en pose neutra.
- `fbx/`: 18 exportaciones, una por personaje; mallas y esqueleto solamente.
- `renders/<id>/`: frente, perfil, espalda y rostro (72 imágenes); `gallery.png` es el render de la galería 3D.
- `renders/elenco.png`, `rostros.png`, `roles.png`, `perfiles.png`, `espaldas.png`: hojas de revisión compuestas a partir de renders reales.
- `viewport_gallery.png`: captura revisada del viewport de Blender conectado con los 18 personajes.
- `pose_checks/`: seis capturas de flexión del FBX reimportado.
- `cast_catalog.json`: colores, alturas, anchuras, prendas y rasgos editables.
- `build_cast.py`: construcción, variación, render y exportación reutilizables.
- `character_primitives.py`: módulo auxiliar reutilizado del modelo aprobado; importar desde el generador, no ejecutar por separado.
- `baseline/approved_female.blend`: nuestra base aprobada, necesaria para reconstruir y transferir sus pesos.
- `validate_cast.py`, `validation.json`, `manifest.json` y logs: pruebas y medidas reales.
- `SHA256.json`: integridad de los archivos de esta entrega.

## Qué se comprobó

Generación y reimportación headless con Blender 4.5.15 LTS. Los 18 FBX contienen un rig de 21 huesos cada uno, sin cámaras ni luces; altura y apoyo en Z=0 con tolerancia de 3 mm; cero vértices sin pesos y pesos normalizados. Se probó el giro de cabeza, flexión de brazo/pierna y recuperación de la pose inicial; hay seis capturas de pose. Se revisaron renders frontal/lateral/posterior y captura del viewport conectado.

Los 17 nuevos diseños tienen entre 2,242 y 3,224 triángulos por personaje. La mujer aprobada se conserva con 16.620 triángulos; su ropa/cuerpo aún requieren una reducción posterior si el presupuesto de NPC lo exige. No se midió rendimiento en Unity.

## Qué falta

El rig es propio de bpy, no un rig descargado de Mixamo. La estructura es consistente entre personajes para preparar retargeting, pero el Avatar Humanoid dentro de Unity no está comprobado. No se crearon clips, Animator Controllers ni locomoción en esta entrega. Las manos son simplificadas, sin dedos articulados; no hay rig facial. Los accesorios tienen pesos rígidos básicos; las armas y herramientas son visuales. Las pruebas de flexión no garantizan ausencia de penetraciones en todas las futuras animaciones.

Las prendas/cabeza/pelo/accesorios están separados por función y comparten nombres de huesos; cada FBX es una exportación autónoma. El equipamiento modular durante el juego y los prefabs aún no están conectados. Guardias con porra, sin pistola; policías con funda y empuñadura. Civiles sin armas de fuego.

La carpeta del proyecto termina en `~` para que Unity no importe automáticamente esta revisión antes de decidir los diseños. No se reemplazaron los prefabs existentes. Las revisiones antiguas se conservan.

## Revisar en Blender

1. Abrir `Alarma_LowPoly_Cast.blend`, o elegir `Cast_Gallery` en Blender ya abierto.
2. Cambiar a `Cast_<id>` para revisar cada modelo; seleccionar su Armature y usar Pose Mode para comprobar brazos/piernas/cabeza.
3. Revisar especialmente las siluetas, vestuario y accesorios antes de comenzar los clips finales.

## Pasos para Unity — después de aprobar el diseño

Mantener Unity **6000.3.27f2**. Estos pasos los realiza Alain en el editor; no se ha abierto Unity desde esta tarea.

1. Copiar los FBX aprobados desde `LowPolyCast~/fbx` a una carpeta nueva, por ejemplo `Assets/Party/Art/Characters/LowPolyCast/Models`. Esperar la importación.
2. En cada FBX: pestaña Rig, Animation Type = Humanoid, Avatar Definition = Create From This Model, Apply y Configure. Confirmar asignación de huesos y pose válida; las manos no tienen dedos opcionales.
3. Revisar orientación, escala en metros y pies sobre el suelo. Si Humanoid informa un problema, conservar el FBX y aportar el mensaje para corregir el rig antes de animar.
4. Preparar materiales URP con los colores del catálogo y crear prefabs nuevos al validar cada Avatar. No reutilizar automáticamente los constructores de las versiones rechazadas.
5. Cuando haya un clip de caminar aprobado, probarlo en un civil, un uniforme y cada rol. Revisar codos, rodillas, cintura y accesorios antes de compartir las animaciones con todo el elenco.

## Cómo regenerar

Abrir una terminal en la carpeta que contiene este README y sustituir la ruta de Blender por la instalación 4.x. Estos comandos regeneran los archivos de salida de esa copia:

```powershell
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P build_cast.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P validate_cast.py
```

Para una variante: añadir `-- --only NPC01_Bomber` al primer comando. Ese modo produce un catálogo de salida parcial: usar una copia de trabajo para no confundirlo con la entrega completa. Las hojas de contacto se pueden rehacer con `make_sheets.py` y Python con Pillow, después de generar los 18 modelos.

## Explicación para aprender

El catálogo separa las decisiones visuales del código de construcción: cambiar un color o altura no obliga a reescribir el generador. Las funciones construyen prendas y accesorios por separado, mientras que el rig proporciona la jerarquía común que mueve las piezas. Los pesos de la base aprobada se transfieren a las superficies nuevas; cabeza y accesorios rígidos reciben el peso del hueso correspondiente. La exportación y la validación están en scripts distintos para mantener responsabilidades separadas. Esto aplica el principio de responsabilidad única; no incorpora nuevos sistemas C# ni patrones de red.

## Catálogo y medidas

| ID / nombre del FBX | Personaje | Altura (m) | Triángulos |
|---|---|---:|---:|
| NPC01_Bomber | Nico Naranja | 1.76 | 2326 |
| NPC02_Denim | Lola Denim | 1.65 | 16620 |
| NPC03_Tourist | Tito Vacaciones | 1.79 | 3224 |
| NPC04_Lavender | Violeta Turbo | 1.68 | 2408 |
| NPC05_Burgundy | Don Bigotín | 1.73 | 2416 |
| NPC06_Mechanic | Cora Tornillos | 1.64 | 3130 |
| NPC07_PaddedVest | Paco Bolsillos | 1.82 | 2242 |
| NPC08_Sport | Rita Rebote | 1.67 | 2834 |
| NPC09_Flannel | Bruno Cuadritos | 1.84 | 2670 |
| NPC10_Cardigan | Clara Botones | 1.63 | 2924 |
| NPC11_SecurityMale | Guardia Bigotes | 1.80 | 3092 |
| NPC12_SecurityFemale | Guardia Chispa | 1.70 | 2848 |
| NPC13_PoliceMale | Oficial Mostacho | 1.79 | 3054 |
| NPC14_PoliceFemale | Oficial Visera | 1.71 | 2900 |
| Player01_Thief | Don Sigilo · Ladrón | 1.69 | 2556 |
| Player02_Hacker | Primo WiFi · Hacker | 1.75 | 3012 |
| Player03_Distractor | Abuelita Falsa · Distractor | 1.62 | 2778 |
| Player04_Muscle | Toñito · Músculo | 1.88 | 2636 |

## Origen

Geometría, materiales planos y rig propios, construidos con bpy a partir de nuestra mujer aprobada. Sin modelos ni texturas descargados; sin archivos ni clips Mixamo. Las referencias aportadas por Alain se utilizaron como guía de vestuario, no como texturas.
