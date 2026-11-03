# Alarma — ciudad moderna low poly R2

Revisión artística del mapa de **4.000 × 4.000 m**, solicitada por Alain al rechazar la sencillez de la entrega anterior.
Se conserva la distribución general, la plaza y las diagonales de su referencia. Se reconstruye la arquitectura,
la vegetación y el mobiliario. Alain confirmó **completar primero el diseño**: esta entrega no añade tráfico ni animaciones.

## Qué cambió

- **Casas:** doce variantes con ventanas en las cuatro fachadas, marcos, huecos reales, porches, terrazas,
  balcones, cubiertas planas o inclinadas, paneles solares, jardineras y accesos de parcela.
  Varias tienen planta superior retranqueada. Se representan sala, cocina y dormitorio con mobiliario sencillo.
- **Apartamentos:** seis variantes con balcones, barandillas, ventanas, acceso y cubiertas equipadas.
- **Empresas:** tres siluetas de oficinas: bloque con podio, torre retranqueada y torres gemelas con conexión.
  Fachadas acristaladas, paños de colores, marcos, pórticos, terrazas, áreas ajardinadas y accesos pavimentados.
  Las plantas altas de oficinas son envolventes visuales; no se modela cada despacho.
- **Comercios ordinarios:** doce variantes con rótulo, escaparates, marquesina, mostrador y mobiliario según uso:
  panadería, café, farmacia, tecnología, bicicletas, libros, mercado, flores, comida, estudio, ropa y oficinas pequeñas.
- **Locales principales:** nueve edificios reconstruidos, con envolvente, mobiliario, techo y puertas separados.
  Minimercado con góndolas, refrigeradores y caja; banco con ventanillas, cajeros y bóveda; joyería con vitrinas;
  comisaría con recepción y celdas; restaurante con cocina y terraza; ropa con percheros; taller con elevador y herramientas;
  tienda de equipo y escondite. Son diseños de interiores, todavía sin interacciones.
- **Árboles:** seis diseños con raíces, troncos, ramas y copas facetadas: frondosos, jacarandá estilizado,
  frutal, pino y palmera. Rotación, tamaño y posición del bosque varían para romper la cuadrícula.
- **Espacio público:** pérgolas, mesas, sillas, bancos, farolas, maceteros, paradas de bus,
  aparcabicicletas, cargadores eléctricos, canchas y pequeños juegos infantiles.
- **Plaza:** fuente del pato conservada, chorros de agua modelados, puestos de café, pasos peatonales,
  pavimento, jardines y zonas de estancia. El agua sigue estática.

Los 3.738 edificios genéricos de la ciudad usan las nuevas piezas. Además se revisan los locales principales
y un negocio de la galería. La comprobación geométrica abarca 3.748 envolventes y sus cubiertas.
Se mantienen los 64 sectores de 500 m y los recorridos de metro, parking y alcantarillado de la revisión anterior.

## Abrir y revisar

1. Abrir **`Villa_Alarma_Modern_R2.blend`**. Generado y comprobado con Blender **4.5.15 LTS**.
   Para revisar primero las piezas sin cargar la ciudad, abrir **`CityR2_Showcase.blend`**: es una muestra pequeña
   con las mismas mallas, materiales, casas, negocios, árboles y una oficina. No sustituye el mapa completo.
2. Seleccionar `CityR2_ModernStreet` o `CityR2_StreetLevel`. Numpad 0 muestra el encuadre de cámara.
3. Revisar `CityR2_Residential`, `CityR2_Neighborhood`, `CityR2_BusinessDistrict` y `CityR2_Plaza`.
4. Ver los interiores en `CityR2_Minimarket_Inside`, `CityR2_Bank_Inside` y `CityR2_Police_Inside`.
   Esas escenas ocultan las colecciones de cubiertas. Los muebles se conservan a escala real.
5. Elegir `CityR2_Plan` o `CityR2_Aerial` para ver el mundo completo y `CityR2_ForestRiver` para la vegetación.
6. Para editar con más comodidad, aislar un sector y activar Overlays. El recorte lejano de las cámaras es 30.000 m.

Para ver los cristales y los interiores, usar **Previsualización de materiales** o Rendered.
Durante la revisión aparecieron líneas diagonales con las sombras de Workbench en el mundo completo;
se corrigió la vista entregada desactivando Shadows y Cavity en Solid. Los renders EEVEE no presentan esas líneas.

Las piezas nuevas usan nombres `CityR2_*`. Las raíces `Sector_00_00` a `Sector_07_07` agrupan la ciudad.
Los techos nuevos se organizan en `R2_Roofs_Sector_*`. Las hojas de puertas principales tienen el origen en la bisagra.
Las tres figuras del elenco R3 son referencias de escala y se excluyen del FBX del mapa.

## Archivos creados

| Archivo o carpeta | Uso |
| --- | --- |
| `Villa_Alarma_Modern_R2.blend` | Ciudad completa editable y cámaras de revisión |
| `CityR2_Showcase.blend`, `make_showcase.py` | Vista ligera y receta de generación para revisar el diseño |
| `export/Villa_Alarma_Modern_R2.fbx` | Ciudad ensamblada, con colocación y jerarquía |
| `export/sectors/` | 64 FBX con origen local al centro del sector |
| `export/kit/` | 153 FBX de piezas maestras, cubiertas y mobiliario exportados por separado |
| `export/sector_layout.json` | Posiciones de sectores y lista exacta del kit entregado |
| `modern_assets.py` | Factorías de casas, apartamentos, oficinas, negocios, árboles y mobiliario |
| `hero_businesses.py` | Envolventes y muebles de los nueve locales principales |
| `build_modern_city.py` | Sustitución de arquitectura, vegetación, accesos y plazas |
| `polish_public_space.py` | Volúmenes finales de oficinas y equipamiento de parques |
| `mesh_tools.py`, `layout_math.py` | Geometría, materiales y cálculo de polígonos |
| `render_modern_city.py` | Cámaras, iluminación procedural y renders de revisión |
| `export_map.py`, `verify_fbx.py` | Exportación y comprobación de ida y vuelta |
| `validate_city.py` | Medidas, huellas, materiales y piezas separadas |
| `viewport_review.py`, `make_review.py` | Captura OpenGL y láminas de revisión |
| `map_config.json`, `palette.json` | Dimensiones, semilla y colores ajustables |
| `manifest.json`, `asset_catalog.json` | Catálogo y estadísticas del resultado |
| `baseline/v1_map.blend` | Nuestra entrega anterior, como entrada reproducible del refinamiento |
| `renders/` | Vistas del resultado, lámina general, interiores y comparación anterior/R2 |
| `validation.json`, `fbx_validation.json` | Evidencia de comprobaciones y alcance |
| `SHA256SUMS.json` | Integridad de los archivos de entrega |

`review_assets.py` produce una escena pequeña para estudiar piezas maestras. `finish_interiors.py` conserva
la corrección local usada durante la revisión de celdas; la corrección ya está integrada en `hero_businesses.py`.
Los demás edificios y escenas anteriores se conservan en sus entregas separadas.

## Pasos para Unity — Alain

Se mantiene **Unity 6000.3.27f2 / URP**. No se abrió el editor ni se cambiaron escenas o prefabs del proyecto.
Los fuentes están en `Assets/Party/Art/BlenderScripts/Map4KmModernR2~`; Unity ignora esa carpeta terminada en `~`.

1. Tras revisar el aspecto, copiar el FBX ensamblado a `Assets/Party/Art/City/Map4KmModernR2/`.
2. En una escena de revisión, colocarlo en posición cero y escala uno. Mantener la conversión de ejes del importador.
   Confirmar que el terreno mide 4.000 m por lado. Las unidades de origen son metros.
3. Extraer/remapear los materiales a URP/Lit. Los colores hexadecimales están en `palette.json`.
   Para `City4_clear_glass`, elegir Surface Type **Transparent**, Alpha aproximado **0,22**, Smoothness **0,82**.
   Los otros colores son opacos, con brillo bajo. La iluminación y el cielo de Blender no se exportan en FBX.
4. Para revisar sectores individualmente, usar `export/sector_layout.json` y sus orígenes.
   No colocar todos los sectores en cero: se superpondrían. La conversión prevista es `(X, Z, -Y)` de Blender a Unity;
   debe confirmarse en el editor. La colocación completa ya viaja en el FBX ensamblado.
5. Comprobar con una cápsula de referencia de 1,65–1,80 m las puertas, escaparates y anchuras de paso.
   La cápsula sirve como regla visual; todavía no hay colisiones ni controlador de jugador integrados.

## Cómo probar y qué falta

Comparar `renders/Antes_Despues.png` y revisar los edificios desde cerca, no solo desde el plano de 4 km.
Confirmar variedad de cubiertas, profundidad de ventanas, apariencia de árboles, mobiliario e identidad de locales.
Probar la importación en Unity, la escala y los materiales transparentes. Informar de recortes, objetos flotantes o solapamientos.

Se comprobó extensión, 64 sectores, 3.748 huellas de edificios sin invadir calzadas, seis especies de árboles,
techos y puertas separados y asignaciones válidas de materiales. El trazado vial conserva la conectividad comprobada en V1.
El FBX completo y dos sectores se reimportan para contrastar medidas, orientación, nombres y colores por cara.
La captura del viewport y las imágenes muestran geometría real de los archivos entregados.

Esta revisión prioriza el **diseño** autorizado por Alain. El conjunto reúne aproximadamente **29 millones de triángulos
instanciados**, con mallas compartidas. No se afirma que deba cargarse todo simultáneamente en el juego.
Faltan medición en Unity, LOD, occlusion/streaming, colliders, NavMesh, tráfico, animaciones y red.
La configuración de materiales URP sigue pendiente de comprobar dentro del editor.
Task 03.5 permanece abierta hasta la revisión y prueba de Alain; no se hace commit de cierre.

## Regenerar en una copia

Python 3 para las láminas, Pillow instalado y Blender 4.5 LTS para el resto. No se descargan recursos.

```powershell
blender -b --python-exit-code 1 -P build_modern_city.py
blender -b --python-exit-code 1 -P polish_public_space.py
blender -b --python-exit-code 1 -P sync_metadata.py
blender -b --python-exit-code 1 -P render_modern_city.py
blender -b --python-exit-code 1 -P validate_city.py
blender -b --python-exit-code 1 -P export_map.py
blender -b --python-exit-code 1 -P verify_fbx.py
python make_review.py
blender -b --python-exit-code 1 -P make_showcase.py
blender -b --python-exit-code 1 -P finalize_display.py
```

`polish_public_space.py` admite repetición y detecta si su pase ya está aplicado.
Los otros generadores sustituyen archivos de su carpeta: trabajar siempre en una copia para conservar ajustes manuales.
FBX: escala 1, FBX All, Forward -Z, Up Y, solo mallas y empties, sin cámaras, luces ni clips.
La opción experimental Apply Transform se mantiene desactivada para conservar la coherencia de jerarquías y sectores.

## Explicación para aprender

La mejora se construye en las piezas maestras y se propaga a sus instancias por toda la ciudad.
Cada local separa estructura, muebles, techo y puertas para facilitar su edición y sus futuras interacciones.
Las factorías de edificios y árboles generan variantes sin copiar toda la geometría en memoria.
Los módulos de creación, composición, exportación y validación tienen responsabilidades distintas: principio S.
Las pruebas geométricas detectan fallos de escala y colocación; la revisión visual sigue siendo necesaria para juzgar el diseño.

## Procedencia

Arquitectura, vegetación y equipamiento nuevos modelados mediante bpy propio. Trazado, terreno, vehículos y figuras
proceden de nuestra entrega anterior. Sin modelos ni texturas descargados. Cielo procedural nativo de Blender.
La referencia de ciudad de Alain guía la composición y no se usa como textura. Rótulos con la fuente incluida
en Blender; Arial instalada localmente solo para láminas. No se incorporaron recursos ni clips de Mixamo.
