# Villa Alarma — diseño de ciudad low poly

Entrega visual del 1 de noviembre de 2026. Área real **4.000 × 4.000 metros: 16 km²**.
Adaptación de la composición de la imagen de Alain: plaza circular, avenidas diagonales,
barrios en retícula y río con bosque al suroeste. Se conserva el estilo geométrico de los personajes.
La referencia dice 6 × 6 km; esta entrega mantiene los **4 × 4 km solicitados**.

## Abrir y revisar en Blender

1. Abrir `Villa_Alarma_4km.blend` con Blender 4.5 LTS o posterior. Los scripts se ejecutaron en 4.5.15.
2. Elegir `Map4Km_Center` en el selector de escenas. Pulsar numpad 0 para mirar por su cámara.
3. Cambiar a `Map4Km_Plan` o `Map4Km_Aerial` para revisar los 4 km completos.
4. Revisar `Map4Km_Street`, `Map4Km_Plaza`, `Map4Km_ForestRiver`,
   `Map4Km_Minimarket_Inside` y `Map4Km_Bank_Inside`. Las dos últimas ocultan techos solo en esas vistas.
5. Para editar, salir de la cámara y activar Overlays. El recorte lejano de vista/cámaras es 30.000 m.
   La colección del sector permite aislar una zona y trabajar con menos objetos visibles.

En la sesión de Blender conectada quedó abierta `Map4Km_Center`, conservando las escenas anteriores.
La carga inicial de todas las vistas tardó varios minutos. El entregable independiente evita tener que
guardar toda la biblioteca de personajes para conservar el mapa.

## Contenido creado

- 64 sectores, retícula de 8 × 8, terreno de 500 m por sector; raíz `VillaAlarma_4000m`.
- 3.738 edificios: viviendas, apartamentos, comercios, torres y almacenes.
- 14 puntos principales identificados en `renders/Plan_Annotated.png` y `manifest.json`.
- Plaza del Pato con fuente, jardines, árboles facetados, bancos y puestos de comida.
- Calzadas principales de 14 m, bulevares y diagonales de 22 m, secundarias de 8 m y aceras de 4 m.
- Carretera perimetral, río con puentes, bosque y colinas bajas.
- Farolas, semáforos estáticos, señales, pasos de cebra y coches estacionados.
- Minimercado, joyería y banco con mobiliario, entrada y salida posterior.
  También escondite, comisaría/celdas, tienda de equipo, ropa, restaurante y taller de pintura.
- Entrada de metro, parking bajo tierra con rampa y conducto de alcantarillado con dos accesos.
- Tres figuras del elenco R3 para comprobar escala. Son referencias estáticas y se excluyen de los FBX del mapa.
- Techos y hojas de puertas de locales principales separados; las hojas conservan pivotes en la bisagra.
- Paleta de 24 materiales planos `City4_*`, sin imágenes de textura.

Los barrios ordinarios usan fachadas y no incluyen interiores visitables. El metro representa su acceso,
no una red de estaciones. La galería comercial es pequeña. Se simplificaron la densidad y los detalles de la ilustración.

## Archivos y responsabilidades

| Archivo o carpeta | Contenido |
| --- | --- |
| `Villa_Alarma_4km.blend` | Mapa editable y nueve escenas de revisión |
| `export/Villa_Alarma_4km.fbx` | Ciudad completa ensamblada, con jerarquía y colocación |
| `export/sectors/` | 64 FBX con origen local al centro de cada sector |
| `export/sector_layout.json` | Posiciones de sectores y lista de 55 piezas del kit |
| `export/kit/` | Edificios, árboles, mobiliario, coches propios y once módulos constructivos |
| `map_config.json`, `palette.json` | Medidas, semilla, distribución y colores editables |
| `layout.json`, `placements.json` | Trazado de calles y registro de colocación inicial |
| `escape_routes.json` | Posiciones de accesos y recorridos de escape de diseño |
| `manifest.json` | Catálogo y estadísticas del mapa |
| `building_footprints.json` | Huellas usadas para comprobar separación de calzadas |
| `renders/` | Ocho renders, plano rotulado, hoja de revisión y captura OpenGL del viewport |
| `baseline/` | Subconjunto de nuestra biblioteca de interiores y elenco R3 propios para regenerar |
| `references/` | Imagen de Alain, usada solo como guía de composición |
| `validation*.json`, `fbx_validation.*` | Resultados y alcance de las verificaciones |
| `SHA256SUMS.json` | Integridad de todos los archivos entregados |

Scripts comentados por responsabilidad: `layout_math.py` recorta polígonos; `prepare_layout.py` crea el trazado;
`mesh_tools.py` construye primitivas y materiales; `urban_assets.py` define las piezas;
`build_map.py` ensambla la ciudad; `render_map.py` prepara las vistas; `export_map.py` exporta;
`validate_map.py` y `verify_fbx.py` verifican; `make_review.py` prepara las láminas;
`viewport_review.py` captura OpenGL en una instancia aislada; `finalize_view.py` guarda el encuadre inicial.
`refine_details.py` conserva la receta de los pequeños ajustes finales, ya incluidos en `build_map.py`.

## Pasos para el editor de Unity — Alain

Se mantiene **Unity 6000.3.27f2 / URP**. No se abrió Unity ni se sustituyeron escenas o prefabs existentes.
La copia del proyecto está en `Assets/Party/Art/BlenderScripts/Map4Km~`; el sufijo `~` evita importaciones automáticas.

1. Después de revisar el diseño, copiar `export/Villa_Alarma_4km.fbx` a
   `Assets/Party/Art/City/Map4Km/`. Para una primera revisión usar el FBX completo.
2. En su importador mantener escala 1 y unidades de archivo. Colocarlo en una escena de revisión con
   posición cero y escala uno; conservar la rotación que produzca el importador FBX.
3. Extraer/remapear materiales a `Universal Render Pipeline/Lit` si Unity no los convierte correctamente.
   Usar los colores hexadecimales de `palette.json` como Base Map y Smoothness bajo.
4. Usar una cámara de perspectiva con Far Clip de al menos 6.000 m para ver el conjunto.
   Medir el terreno con ProBuilder o una referencia de dimensiones: debe medir 4.000 m por lado.
5. Si se trabaja por sectores, importar sus FBX por separado y colocarlos según `sector_layout.json`.
   No colocar los 64 en el origen: se superpondrían. Las posiciones `blender_origin` usan Z vertical;
   `unity_origin_convention` expresa la conversión prevista a Y vertical, pendiente de confirmar en Unity.
   Algunos árboles/edificios cruzan el límite de su sector; los centros siguen separados 500 m.

No activar todavía tráfico o peatones en esta escena. Los siguientes sistemas necesitan colliders seleccionados,
NavMesh, puntos de aparición, controladores y pruebas propias. No se añadieron automáticamente.

## Cómo probar esta entrega

1. Comparar `Plan_Annotated.png` con la referencia: plaza, dos diagonales, barrios y bosque/río al suroeste.
2. Revisar a escala de personaje la tienda y la plaza. Comprobar que entradas y mobiliario son legibles.
3. Inspeccionar los interiores sin techo y sus salidas posteriores. Las puertas están separadas, todavía sin lógica.
4. En Unity confirmar tamaño, colores URP, orientación y ausencia de errores al importar el FBX.
5. Revisar un sector central y uno de bosque; anotar cualquier hueco o solapamiento antes de preparar colisiones.

Las verificaciones automáticas comprueban extensión, 64 sectores, conectividad del grafo vial y que las
3.738 huellas de edificios genéricos no invadan la calzada. La reimportación comprobó el mapa completo y
dos sectores: escala/orientación, cantidad de piezas y materiales por cara. También se revisó el viewport.
El exportador FBX 4.5 imprime un aviso por cada reutilización de materiales de mallas compartidas;
el script cuenta esos avisos después de auditar las ranuras y el verificador contrasta los colores exportados.

**Pendiente:** aprobación visual de Alain, prueba real en Unity, colliders, NavMesh, LOD/occlusion/streaming,
medición de FPS y memoria, animaciones, tráfico y red. Los 64 sectores son archivos de diseño, no un
sistema de carga dinámica. El mapa reúne aproximadamente 4,14 millones de triángulos instanciados;
no se declara optimizado ni jugable por pasar las pruebas de exportación. Task 03.5 sigue abierta.

## Regenerar

Ejecutar desde esta carpeta con Python 3 y Blender 4.5 LTS. `make_review.py` requiere Pillow;
los scripts de construcción no descargan dependencias ni recursos.

```powershell
python prepare_layout.py
blender -b --python-exit-code 1 -P build_map.py
blender -b --python-exit-code 1 -P render_map.py
blender -b --python-exit-code 1 -P export_map.py
blender -b --python-exit-code 1 -P validate_map.py
blender -b --python-exit-code 1 -P verify_fbx.py
python make_review.py
blender -b --python-exit-code 1 -P finalize_view.py
```

Trabajar en una copia antes de regenerar: estos scripts sustituyen los archivos generados en su carpeta.
FBX estático, escala 1, FBX All, Forward -Z, Up Y, solo mallas y empties, sin animaciones/cámaras/luces.
Apply Transform experimental se desactiva en el mapa para mantener coherentes las jerarquías del mapa y de sus sectores.

## Explicación para aprender

La configuración separa las decisiones artísticas del código que crea la geometría.
El generador organiza la ciudad en sectores y reutiliza mallas para repetir edificios y árboles.
Cada script tiene una responsabilidad: trazar, modelar, ensamblar, exportar o comprobar; aplica separación de responsabilidades (S).
Las factorías de piezas permiten añadir variantes sin cambiar el ensamblaje de barrios.
Los JSON conservan posiciones y conexiones para que los sistemas de juego puedan consumirlos después.
Un grafo conectado comprueba rutas de diseño; no sustituye el NavMesh ni las pruebas con un jugador.

## Procedencia

Geometría nueva mediante bpy propio; interiores, coches y figuras proceden de nuestra biblioteca anterior.
No se descargaron modelos ni texturas. La imagen aportada por Alain se conserva como referencia,
no se usa como textura. Los rótulos 3D usan la fuente incluida en Blender; Arial instalada localmente
solo se usa en las láminas de revisión. No se incorporaron recursos ni clips de Mixamo en esta entrega.
