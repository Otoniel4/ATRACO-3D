# Árboles y viento natural R3 — Alarma

Entrega del 1 de noviembre de 2026. Mantiene Unity **6000.3.27f2**, URP **17.3.0** y la ciudad de **4.000 × 4.000 m**. Esta revisión responde a la petición de Alain de mejorar los árboles y mover las hojas. El tráfico, los peatones y otras dinámicas permanecen fuera de esta entrega.

## Qué cambió

Se construyeron seis especies estilizadas: fresno, olivo, jacaranda, cítrico, pino y palmera. Tienen troncos curvos con variación de sección, raíces, ramas afinadas, ramillas y hojas individuales plegadas. El pino usa grupos de acículas y la palmera, frondas arqueadas. Jacarandas y cítricos tienen pequeños detalles de flor o fruto. La paleta sigue siendo plana y low poly; no hay texturas descargadas.

El viento combina balanceo lento del tronco, movimiento de ramas y aleteo de las hojas. La intensidad varía en ráfagas y cada hoja tiene una fase distinta. La base del tronco queda fija. El bucle dura ocho segundos a 24 fps; hay 192 fotogramas renderizados, sin interpolación de imágenes.

La copia nueva del mapa sustituye **10.745 árboles**. Se reubicaron 7.261 que invadían edificios según la comprobación geométrica del generador; no se eliminaron árboles por falta de sitio. Se verificó que la geometría y las transformaciones de los objetos ajenos a la vegetación conservan su huella. La ciudad moderna R2 y los personajes anteriores se mantienen disponibles.

## Ver el resultado en Blender

1. Abre `Arboles_Viento_R3.blend` con Blender 4.5 o posterior. Para una revisión rápida, usa este archivo pequeño antes del mapa completo.
2. Selecciona la escena `Trees_R3_Wind_Closeup`. Pulsa **Espacio** en el viewport para reproducir. El intervalo es 1–192; `Trees_R3_Gallery` permite revisar las seis especies.
3. Selecciona un árbol y abre su modificador Geometry Nodes. `Strength = 0` detiene la deformación; `Strength = 1` recupera el viento. `Speed` ajusta la velocidad; al cambiarla, el periodo real pasa a ser 8 / Speed segundos.
4. Abre `Villa_Alarma_Arboles_Viento_R3.blend` para revisar los árboles en la ciudad. Las escenas `CityR3_StreetLevel` y `CityR3_Plaza` muestran las zonas de revisión.

En el mapa se dejó Geometry Nodes activo en **65 árboles próximos a las zonas de revisión**. Los demás conservan la geometría de reposo para evitar evaluar miles de modificadores durante esta revisión en Blender. Todos contienen los datos necesarios para el shader de viento de Unity. La escena de galería y la escena de primer plano sí animan sus árboles.

El mapa asigna una malla según la distancia a las cámaras de revisión: 54 árboles LOD0, 2.295 LOD1 y 8.396 LOD2. Esta asignación es fija; todavía no constituye un sistema de LOD por distancia al jugador. Hay tres FBX separados por especie para construir posteriormente los `LODGroup` de Unity.

## Archivos creados

| Archivo o carpeta | Contenido |
| --- | --- |
| `Arboles_Viento_R3.blend` | Galería, primer plano, seis especies y grupo de viento editable. |
| `Villa_Alarma_Arboles_Viento_R3.blend` | Copia del mapa de 4 × 4 km con vegetación R3. |
| `export/trees/` | 18 FBX: seis especies y tres niveles de detalle. |
| `export/Villa_Alarma_Arboles_Viento_R3.fbx` | Mapa completo en reposo con colores de vértice de viento. |
| `Unity/TreeWindURP.shader` | Viento en GPU, iluminación URP, sombras, profundidad y normales. |
| `Unity/Materials/` | 21 materiales de colores planos y sus `.meta`. |
| `Unity/Scripts/City/TreeWindBounds.cs` | Margen de descarte para árboles deformados por el shader. |
| `settings.json` | Semilla, paleta, intensidad, periodo, amplitudes y densidad de LOD. |
| `tree_geometry.py`, `wind_nodes.py` | Construcción de mallas y del grupo Geometry Nodes. |
| `build_trees.py`, `update_city.py` | Generación de la biblioteca y sustitución en una copia de ciudad. |
| `export_trees.py`, `check_fbx.py`, `validate_wind.py` | Exportación y comprobaciones independientes. |
| `render_animation.py`, `render_portraits.py`, `render_review.py` | Render del viento, retratos y vistas de ciudad. |
| `viewport_review.py` | Captura OpenGL en una instancia aislada de Blender. |
| `prepare_unity.py`, `make_review.py`, `encode_preview.py` | Materiales, hoja de especies y vídeo de revisión. |
| `baseline/` | Copia del mapa R2 propio y datos de trazado necesarios para regenerar. |
| `catalog.json`, `tree_placements.json` | Recuento de polígonos y posiciones reales de los árboles. |
| `renders/` | GIF, MP4, seis retratos, vistas de ciudad y captura real del viewport. |
| `*_validation.json`, `city_update.json`, `viewport_status.json` | Resultados de las verificaciones. |

Los scripts y fuentes se entregan en `Assets/Party/Art/BlenderScripts/TreesWindR3~`. El sufijo `~` mantiene esta entrega de revisión fuera de la importación automática. El shader y el componente aún deben compilarse y probarse en Unity; por eso no se sustituyeron materiales, escenas ni prefabs activos.

## Pasos para el editor de Unity

1. En el proyecto actual, copia el shader, su `.meta` y la carpeta `Materials` desde esta entrega a `Assets/Party/Art/Vegetation/WindR3`. Conserva los `.meta`: enlazan los materiales con el shader.
2. Copia `Unity/Scripts/City/TreeWindBounds.cs` a `Assets/Party/Scripts/City`. Espera la compilación y revisa Console antes de continuar.
3. Para una prueba pequeña, copia únicamente `export/trees/TreeR3_Fresno_LOD0.fbx` a `Assets/Party/Art/Vegetation/WindR3/Models`. Mantén la escala a 1 y los colores de vértice. No hace falta importar el mapa completo para comprobar el viento.
4. En la pestaña **Materials** del FBX, usa la búsqueda/remapeo por nombre en el proyecto para asignar los `WindTree_*` de esta entrega. Si no encuentra alguno, asígnalo manualmente por el mismo nombre en `Remapped Materials`. Los materiales deben usar `Alarma/Vegetation/Natural Wind R3`, tanto en hojas como en ramas y tronco.
5. Arrastra el FBX a una escena de prueba y añade `TreeWindBounds` al objeto que contiene `MeshFilter` y `MeshRenderer`. El margen inicial de 1 m cubre las amplitudes suministradas. Recalcula mediante `RefreshBounds()` si un sistema cambia la escala durante la ejecución.
6. En el material, usa fuerza 1, velocidad 1 y periodo 8. El shader se anima con el tiempo de Unity. No necesita Animator ni clips. Configura una luz direccional con sombras para revisar también su movimiento.
7. Tras validar el árbol pequeño, importa el mapa nuevo como una copia de escena. Remapea solamente los materiales `WindTree_*`; conserva los materiales de edificios y demás objetos. Añade el margen a los renderers de los árboles. No marques los árboles como **Batching Static**, porque las mallas combinadas impedirían gestionar sus límites individualmente.
8. Para LOD por distancia, importa los tres FBX de una especie, colócalos con la misma transformación bajo una raíz y crea un `LODGroup`. Asigna cada renderer a su nivel y ajusta las transiciones mediante una prueba real. El mapa entregado no crea esos grupos automáticamente.

**El FBX guarda la malla de reposo y las máscaras de viento. No transporta Geometry Nodes ni su animación.** Un material URP Lit estándar dejará los árboles inmóviles. La reproducción de Blender y el shader URP son dos implementaciones de la misma fórmula, con ejes adaptados.

## Cómo probarlo

1. En Blender, reproduce el primer plano y observa las puntas de hojas y ramas. Comprueba la base del tronco y el paso del fotograma 192 al 1. Compara el GIF y el MP4 incluidos.
2. En Unity, tras completar el remapeo anterior, entra en Play. Las hojas deben variar entre sí y las ramas deben balancearse más despacio. La base debe seguir en el mismo sitio.
3. Cambia la fuerza de 1 a 0 y de nuevo a 1. El árbol debe detenerse y recuperar el movimiento; evita guardar un material compartido a cero si quieres mantener el viento en el resto.
4. Observa las sombras y acerca el árbol al borde de pantalla. Sus hojas no deben desaparecer al superar los límites de reposo. Si aumentas la fuerza o las amplitudes, aumenta también el margen de `TreeWindBounds`.
5. Comprueba Console, colores, dobles caras y los tres niveles de detalle. Usa el Profiler con una cámara a altura de jugador antes de elegir densidades y distancias para toda la ciudad.

Esta entrega no requiere Multiplayer Play Mode: el viento es visual y no modifica estados de juego. La fase de tiempo no se sincroniza en red; no se usa para colisiones ni decisiones del servidor.

## Verificación realizada

- Blender 4.5.15 LTS: biblioteca, ciudad, renders y captura de viewport real abiertos y revisados.
- Fórmula del modificador contrastada con una implementación matemática independiente, incluyendo traslación, giro y escala no uniforme. Error máximo aproximado: **0,0000022 m**.
- Raíces comprobadas: **0 m** de desplazamiento. Cierre del bucle: error inferior a **0,000001 m**. Una hoja muestreada recorre unos **10,8 cm** entre dos poses; ese valor no representa todas las hojas.
- 18 FBX de especies exportados. Máscaras contrastadas por posición en 4.034 esquinas del fresno LOD0 reimportado: error máximo **0**.
- FBX del mapa reimportado: 10.745 mallas de árbol con datos de viento y límites de **4.000 × 4.000 m**.
- Vídeo H.264: 900 × 900, 192 fotogramas, 24 fps y ocho segundos. GIF: 600 × 600, 96 fotogramas y ocho segundos.
- Includes y funciones del shader contrastados con los paquetes URP instalados. APIs de límites del renderer contrastadas con la documentación XML de Unity instalada.
- **Pendiente:** compilación del shader y C#, importación visual, sombras, descarte, LOD y rendimiento dentro de Unity. No se abrió el editor ni se ejecutó el juego durante esta entrega.

Los LOD0 de frondosas tienen entre 27.448 y 45.808 triángulos; la palmera tiene 5.762. Los LOD2 van de 1.808 a 6.952. Es vegetación estilizada con hojas de geometría real; el catálogo permite decidir dónde reducir densidad. No se ha medido FPS ni se afirma que el mapa completo esté optimizado para jugar. El viento es procedural artístico, no una simulación física de botánica.

## Máscara y parámetros

El atributo de color `WindMask` almacena R = flexión del tronco, G = flexión de ramas, B = flexión de puntas de hojas y A = fase por hoja. **A no es transparencia.** El material conserva opacidad 1. No repintes ni elimines estos canales al exportar o importar.

En `settings.json`: `primary_amplitude_m = 0.24`, `branch_amplitude_m = 0.09`, `leaf_amplitude_m = 0.045`, `leaf_vertical_amplitude_m = 0.028`. Son parámetros máximos de la fórmula antes de aplicar máscaras y ráfagas; no son el recorrido de todos los vértices. `wind_strength` multiplica el resultado y `wind_speed` cambia su velocidad. Los controles del modificador permiten ensayar sin regenerar. Los controles equivalentes de Unity están en cada material.

## Regeneración

Trabaja en una copia de esta carpeta. Los scripts usan rutas relativas a su ubicación. Necesitas Blender 4.5, Python con Pillow y FFmpeg/FFprobe disponibles en PATH. `prepare_unity.py` comprueba el PackageCache del proyecto local indicado en su código; adapta esa ruta si trabajas en otro equipo. `make_review.py` usa Arial instalada en Windows para los rótulos.

Desde la carpeta de la entrega, ejecuta en este orden, sustituyendo `blender` por la ruta de tu ejecutable si no está en PATH:

```powershell
blender -b -P build_trees.py
blender -b -P validate_wind.py
blender -b -P update_city.py
blender -b -P export_trees.py
blender -b -P check_fbx.py
blender -b -P render_animation.py
blender -b -P render_portraits.py
blender -b -P render_review.py
python prepare_unity.py
python encode_preview.py
python make_review.py
blender --factory-startup --python viewport_review.py
```

El último comando abre y cierra únicamente su propia instancia de Blender para capturar el viewport. No se debe ejecutar sobre una sesión de artista con cambios sin guardar. Las 192 imágenes intermedias se regeneran en `animation_frames`; no se incluyen para evitar duplicar el vídeo completo.

## Explicación para aprender

La geometría define la silueta; las máscaras indican cuánto puede moverse cada vértice.
Geometry Nodes aplica el viento en Blender y el shader ejecuta la misma idea en la GPU de Unity.
La fase distinta por hoja evita que toda la copa oscile como un bloque rígido.
Los scripts separan generación, viento, exportación y validación: cada pieza tiene una responsabilidad.
`TreeWindBounds` solo gestiona el margen del renderer; no mezcla movimiento ni lógica de juego.
Esta separación aplica responsabilidad única y permite cambiar la vegetación sin modificar los sistemas del personaje.
Los niveles de detalle reducen hojas lejanas, pero sus distancias deben decidirse con mediciones en el juego.

## Procedencia y estado

Geometría, colores, scripts y viento propios. El mapa base es nuestra revisión R2. No hay modelos, texturas ni clips descargados. FFmpeg se utiliza como herramienta de codificación; Arial solo aparece en la hoja de revisión. La revisión visual de Alain y la prueba en Unity siguen pendientes. No se ha cerrado ninguna task ni creado un commit de cierre.
