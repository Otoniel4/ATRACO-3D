# Jardineras y pasto R4 — Alarma

Revisión del 1 de noviembre de 2026. Responde a la captura de Alain: sustituir los arbustos básicos de las macetas y dar más detalle al pasto, manteniendo low poly y coherencia con los árboles R3. Se mantiene Unity **6000.3.27f2 / URP 17.3.0** y el mapa de **4.000 × 4.000 m**.

## Resultado

- Arbustos con tallos y hojas individuales plegadas, colores verdes y salvia, y variantes con pequeñas flores rosas o crema.
- Kit de jardinera rectangular con borde, sustrato y piedras; maceta redonda de terracota con boca y borde modelados.
- En la ciudad, los contenedores y suelos existentes se conservan. Se retiran sus viejos volúmenes de follaje y se añaden plantas separadas y bordes sobre el sustrato.
- Pasto formado por briznas curvas con sección plegada, alturas entre 12 y 30 cm, orientaciones distintas y mezcla de verdes con algunas puntas secas.
- Viento suave de ocho segundos para arbustos y briznas, con máscaras que dejan fijas las macetas y los puntos de anclaje.

No todos los volúmenes reemplazados son macetas distintas: una misma jardinera podía contener varios poliedros de follaje. Los recuentos exactos de volúmenes, objetos, jardineras y parches están separados en `city_update.json`. Los árboles R3 y las caras ajenas al follaje de las mallas intervenidas tienen comprobaciones de conservación.

Se sustituyeron 133.628 volúmenes de follaje de 99 mallas compartidas, distribuidos en 7.983 objetos de plantas; se detectaron 21.982 superficies de sustrato. Se añadieron **14.000 parches de pasto**: 361 LOD0, 2.088 LOD1 y 11.551 LOD2. Los 10.745 árboles R3 permanecen conservados. En Blender hay 53 objetos de arbustos y 160 parches con viento activo cerca de las zonas de revisión.

El pasto se distribuye en grupos sobre césped existente. El generador lanza rayos en el centro y cuatro extremos de cada parche y exige que la superficie superior sea césped, para evitar cubrir pavimentos, accesos y bases de edificios. Hay más detalle cerca de las cámaras de revisión y grupos repartidos en jardines, zonas verdes y junto al arbolado. No se presenta una cobertura continua de los 16 km².

## Revisar en Blender

1. Abre `Macetas_Pasto_Viento_R4.blend` y selecciona `PlantersR4_Closeup`.
2. Pulsa **Espacio** en el viewport. Compara el movimiento de hojas y briznas; la jardinera y el sustrato deben seguir fijos.
3. Para detenerlo, selecciona una planta y cambia `Strength` a 0 en Geometry Nodes. Usa 1 para recuperar el viento y `Speed` para ajustar su velocidad.
4. Abre `Villa_Alarma_Jardineras_Pasto_R4.blend` para ver la aplicación a la ciudad. La escena inicial `CityR4_PlanterDetail` enfoca una jardinera del minimercado. También hay vistas `CityR4_StreetLevel` y `CityR4_Plaza`.

La galería anima sus plantas y pasto. En la ciudad solo se evalúa viento en Blender cerca de las zonas de revisión y en hasta 160 parches de pasto próximos; el resto mantiene sus máscaras para el shader de Unity. Los niveles de detalle del mapa se asignan según las cámaras de revisión y permanecen fijos. No hay todavía cambio automático de LOD por jugador ni streaming.

## Archivos entregados

| Archivo o carpeta | Uso |
| --- | --- |
| `Macetas_Pasto_Viento_R4.blend` | Kit editable y demostración animada. |
| `Villa_Alarma_Jardineras_Pasto_R4.blend` | Ciudad con jardineras y pasto R4, conservando árboles R3. |
| `export/kit/` | 19 FBX: 12 arbustos, tres parches de pasto, dos macetas y dos conjuntos ensamblados. |
| `export/Villa_Alarma_Jardineras_Pasto_R4.fbx` | Mapa completo en reposo con máscaras de viento. |
| `Unity/Materials/` | 19 materiales `WindPlant_*` con sus `.meta`. |
| `Unity/SharedSupport~/` | Copia del shader de árboles R3, su `.meta` y `TreeWindBounds.cs`, para usar si aún no están importados. |
| `flora.py`, `settings.json` | Construcción de plantas, briznas, macetas, paleta, densidades y medidas. |
| `wind_nodes.py` | Geometry Nodes de viento compatible con el sistema R3. |
| `build_assets.py`, `update_city.py` | Generación del kit y actualización de una copia del mapa. |
| `export_models.py`, `check_fbx.py`, `validate_wind.py` | Exportación y verificaciones. |
| `render_animation.py`, `encode_preview.py`, `viewport_review.py` | Vídeo, GIF y captura real del viewport. |
| `baseline/` | Mapa R3 propio y material de referencia necesarios para regenerar. |
| `renders/` | Render del kit, vista de ciudad, captura de viewport, GIF y MP4. |
| `city_update.json`, `*_validation.json`, `preserved_faces.json` | Recuentos y resultados de las comprobaciones. |
| `plant_placements.json`, `grass_placements.json` | Ubicaciones y niveles de detalle asignados. |

Fuentes del proyecto: `Assets/Party/Art/BlenderScripts/PlantersGrassR4~`. El sufijo `~` mantiene la entrega en revisión fuera de la importación automática. No se sustituyeron escenas, materiales ni prefabs activos. Guía del proyecto: `Assets/Party/docs/Planters-Grass-R4.md`. No se cerró ninguna task ni se hizo commit de cierre.

## Pasos para el editor de Unity

1. Si ya importaste el shader `Alarma/Vegetation/Natural Wind R3` y `TreeWindBounds` de los árboles, reutilízalos. **No copies otra vez sus `.meta` ni su clase C#**: son los mismos recursos. Si aún no están importados, copia el shader y su `.meta` desde `Unity/SharedSupport~` a `Assets/Party/Art/Vegetation/WindR3`, y `TreeWindBounds.cs` a `Assets/Party/Scripts/City`.
2. Copia `Unity/Materials` a `Assets/Party/Art/Vegetation/PlantsR4/Materials`, conservando los `.meta`. Espera la compilación y comprueba Console.
3. Para una prueba pequeña, importa `Jardinera_Florida_R4.fbx`, `Maceta_Salvia_R4.fbx` y `PlantR4_Grass_LOD0.fbx` desde `export/kit`. Usa escala 1 y conserva colores de vértice.
4. En **Materials**, remapea por nombre los `WindPlant_*` a los materiales entregados. Deben usar el shader de viento R3. La maceta puede usar ese mismo shader: sus máscaras están a cero. El atributo RGBA de viento no es el color visible de la hoja.
5. Coloca los tres conjuntos en una escena y añade `TreeWindBounds` a cada objeto que contenga `MeshFilter` y `MeshRenderer`. Conserva su margen de 1 m para los valores suministrados; actualízalo si aumentas mucho las amplitudes o cambias la escala durante ejecución.
6. Tras validar el kit, importa el FBX de ciudad en una copia de escena. Conserva los materiales de arquitectura y remapea los `WindPlant_*` nuevos. Los `WindTree_*` siguen usando los materiales de árboles R3 de la entrega anterior.
7. No marques las plantas como **Batching Static** si vas a gestionar límites de cada renderer por separado. Para LOD por distancia, crea `LODGroup` con los tres FBX de cada arbusto o parche y ajusta las transiciones mediante una prueba real.

**El FBX no transporta Geometry Nodes ni su animación.** Incluye la geometría de reposo y `WindMask`; el shader realiza el movimiento en Unity. Un material URP Lit estándar conserva la forma estática.

## Cómo probarlo

1. Reproduce la escena pequeña de Blender y observa el cierre del bucle. Compara con el vídeo/GIF de ocho segundos.
2. En Unity, entra en Play y cambia la fuerza de 1 a 0 y de nuevo a 1 en un material de planta. Hojas y briznas deben detenerse y recuperar el movimiento. La base y la maceta deben quedar fijas.
3. Revisa sombras, dobles caras y bordes de pantalla. Acerca la cámara al pasto para comprobar que son briznas modeladas y que el margen evita su desaparición durante el movimiento.
4. Recorre una zona del minimercado y otra de jardines. Verifica accesos despejados, escala y colores. Prueba los tres LOD y mide con el Profiler antes de decidir distancias y densidad para toda la ciudad.

El viento es visual; no modifica colisiones ni estados de juego y no requiere Multiplayer Play Mode. Su reloj no se sincroniza por red.

## Verificación y límites

En Blender 4.5.15 se verificaron 22 objetos de la escena pequeña, incluyendo un padre girado y escalado: desplazamiento de muestras estáticas **0 m**, error del bucle menor de **0,000001 m** y coincidencia con una fórmula independiente. En las poses muestreadas, hojas y pasto se desplazaron unos **2,4 cm** y **2,2 cm**, respectivamente. Son muestras, no límites de todo el movimiento.

El MP4 tiene 800 × 600 píxeles, 96 fotogramas, 12 fps y ocho segundos. Se renderiza un fotograma cada dos pasos de la escena a 24 fps; no hay interpolación de imágenes. La captura del viewport se obtiene en una instancia aislada de Blender, sin reemplazar la sesión del artista.

Los resultados de reimportación FBX y los recuentos definitivos del mapa están en los JSON de validación. La reimportación comprueba colores de viento y dimensiones. **Compilación del shader/C#, apariencia, sombras, LOD y rendimiento dentro de Unity siguen pendientes.** No se abrió el editor ni se jugó durante esta entrega.

Cada parche de pasto tiene 5.250 / 1.200 / 210 triángulos en LOD0/1/2, con 525 / 120 / 21 briznas. El catálogo también registra los arbustos y macetas. El conjunto completo de la ciudad suma unos **163,8 millones de triángulos instanciados en reposo**, contando todas las piezas del mapa, aunque estén fuera de cámara. Es una entrega de diseño: necesita LOD por distancia, descarte y streaming antes de valorar su coste jugable. Son mallas compartidas, pero su coste de dibujo depende de la cantidad visible y de la integración en Unity. No se ha medido FPS ni se declara optimizada la ciudad completa.

Se retiraron 219 mallas de trabajo sin usuarios del .blend de ciudad y se guardó comprimido. Se verificó que esa limpieza conserva las mallas usadas en la escena.

## Ajustar y regenerar

`settings.json` contiene la semilla, colores, número de tallos, supervivencia de hojas por LOD, grupos de pasto y rango de altura. `flora.py` define dimensiones y pliegues; `build_assets.py` dispone las macetas de ejemplo. En `update_city.py` se distribuyen los parches y se seleccionan las zonas de revisión. Trabaja en una copia de la entrega.

Desde esta carpeta, con Blender 4.5, Python con Pillow y FFmpeg/FFprobe en PATH:

```powershell
blender -b -P build_assets.py
blender -b -P validate_wind.py
blender -b -P update_city.py
blender -b -P export_models.py
blender -b -P check_fbx.py
blender -b -P render_animation.py
python encode_preview.py
python prepare_unity.py
blender --factory-startup --python viewport_review.py
```

`prepare_unity.py` comprueba los includes del PackageCache local de Atraco3D; adapta esa ruta si cambias de equipo. El último comando abre y cierra solo su propia instancia para capturar el viewport. Los fotogramas intermedios se regeneran en `animation_frames` y se excluyen del paquete.

## Explicación para aprender

Las hojas y las briznas son geometría real; el material aporta su color plano.
La máscara R controla flexión general, G controla tallos y B las puntas; A guarda una fase, no transparencia.
La base tiene valores de movimiento a cero para conservar su anclaje.
Geometry Nodes y el shader usan la misma fórmula con los ejes de cada programa.
La generación, el viento, la distribución y la exportación tienen responsabilidades separadas.
`TreeWindBounds` solo ajusta el margen de dibujo; no mezcla lógica de juego ni animación.
Los LOD reducen detalle lejano; el Profiler permite decidir sus distancias con datos reales.

## Procedencia

Geometría, materiales, scripts y viento propios. Mapa base: nuestra ciudad con árboles R3. Sin modelos, texturas ni animaciones descargados. FFmpeg/FFprobe son herramientas de producción, no recursos del juego. Revisión visual de Alain e integración funcional en Unity pendientes.
