> R7 fue rechazada tras la prueba. Corrección vigente: [Correcciones-Prueba-R8.md](Correcciones-Prueba-R8.md).

# Alarma: un botón para preparar y probar lo creado

Entrada única en Unity: **Alarma → Crear y probar juego**.

La primera vez prepara los modelos, materiales, partes de ciudad, colisiones, jugador, NPC, puertas y catálogo. Guarda una escena nueva y abre Play automáticamente. Las siguientes veces abre la escena preparada. Conserva Unity **6000.3.27f2** y todas las entregas anteriores.

Antes de crear otra escena, el botón respalda las escenas sin nombre y los cambios pendientes en `Assets/Party/Scenes/Backups/BeforePlaytest_<fecha>`. Las escenas sin nombre reciben la ruta de su respaldo; las escenas que ya tienen archivo se guardan como copia sin sobrescribir el original. `OpenScenes.json` registra los nombres y las rutas. El constructor no sustituye escenas existentes antes de terminar la preparación. Si hay un fallo, cierra su escena temporal y conserva las anteriores; el informe queda en la carpeta generada.

La revisión `playtest-r7-2` corrige el fallo `Cannot create a new scene additively with an untitled scene unsaved`. La opción **Don't Save** del diálogo anterior dejaba una escena sin ruta, y Unity impedía crear la escena aditiva. Ahora se comprueba esa condición antes de importar modelos. Si todavía ves aquel diálogo, pulsa **Cancel**, espera la compilación y vuelve a pulsar el menú.

Los modelos y materiales ya importados en los intentos que terminaron con ese error se reutilizan. Se crea una carpeta nueva para los prefabs, datos y escena de la prueba. **Conserva las carpetas `Generated/AlarmaPrueba_*` anteriores**: la nueva escena puede referenciar sus modelos y materiales. `assetFolder` en `BuildReport.json` identifica la carpeta reutilizada. Si falta algún recurso obligatorio, el botón prepara un lote nuevo.

## Qué reúne esta prueba

- Ciudad completa de **4.000 × 4.000 m**, con 52.774 piezas de malla de la revisión R6. Se reparte en **263 partes** para cargar las cercanas. Las 17 hojas de acceso a nueve locales se preparan por separado.
- Suelos, edificios, mobiliario y vehículos estacionados con colisiones; árboles con colisión de tronco, vegetación y viento propios.
- Personaje en tercera persona con movimiento, cámara y cambio entre Ladrón, Hacker, Distractor y Músculo.
- Los 18 personajes con manos R6, vehículos, armas, herramientas y accesorios disponibles en un catálogo de inspección. El catálogo respeta escala y orientación de los FBX.
- Puertas automáticas en los nueve locales principales; la puerta del taller se eleva.
- Mercado, joyería y restaurante con peatones, compradores, filas, productos, dependientes, cobros, recibos y bolsas. La población se activa cerca de la cámara.
- Mapa de visitas para desplazarte entre los puntos principales y revisar el entorno.

Esta es una **prueba local del contenido preparado**, no el juego final del GDD. Aún faltan multijugador, misiones de atraco, combate, conducción y sus sistemas compartidos. Las armas y vehículos se pueden inspeccionar; no disparan ni se conducen. El movimiento rápido reutiliza el clip de caminar acelerado; no se declara terminado el set de animaciones final. Los agarres R6 conservan su carácter de prototipo.

## Controles

| Control | Acción |
| --- | --- |
| WASD | Mover al personaje |
| Shift | Acelerar |
| Ratón | Girar la cámara |
| V | Alternar vuelo de revisión |
| Q / E en vuelo | Bajar / subir |
| M | Abrir el mapa y visitar lugares |
| F6 | Abrir el catálogo de modelos; arrastrar para girar |
| F1 / F2 / F3 / F4 | Cambiar de personaje |
| Esc | Liberar el ratón |
| Clic derecho | Capturar el ratón cuando está libre |

Las puertas responden a la proximidad. En el catálogo también hay botones para cambiar de personaje. Si la vista Game es pequeña, amplíala para revisar los menús cómodamente.

## Pasos para Alain

1. Sal de Play y activa Unity; espera a que compile. Si sigue abierto el diálogo de guardado del intento anterior, pulsa **Cancel**.
2. Pulsa **Alarma → Crear y probar juego**. Las escenas pendientes se respaldan automáticamente. La primera preparación puede tardar varios minutos por la importación y creación de prefabs. Si los modelos ya están preparados, se reutilizan; todavía debe crear los prefabs y la escena. Unity muestra su progreso.
3. Se abre una escena nueva `Alarma_Prueba_Completa.unity` y comienza Play. Espera el mensaje de carga de la primera zona.
4. Camina al mercado. Usa **M** para visitar joyería, restaurante, banco, comisaría y los demás lugares. Usa **F6** para revisar los modelos.
5. Detén Play con el botón habitual de Unity cuando termines. No hace falta ejecutar los constructores antiguos.

El fallo anterior `Puesto inaccesible o compartido en el grafo: Routine_Minimarket/Browse_0` se corrige usando el grafo geométrico ya comprobado. La conversión adicional a vóxeles de NavMesh podía descartar ese puesto estrecho. El motor cooperativo trabaja sobre su grafo y sigue validando puestos distintos y conectividad.

## Cómo probar y comunicar cambios

1. Comprueba que el menú Alarma tenga una sola acción y que al usarla no quede una escena incompleta ni dos cámaras principales activas.
2. Camina, acelera, rodea edificios, atraviesa accesos abiertos y cambia entre los cuatro personajes. Comprueba escala, cámara y colisiones.
3. Observa las compras durante tres minutos: producto, fila, turno, escaneo, dinero, recibo y salida. Las cuentas de la tienda cercana aparecen en la interfaz.
4. Visita zonas alejadas con M y en vuelo con V. Comprueba suelo, aparición de edificios, vegetación y velocidad de fotogramas. La interfaz indica cuántas partes están cargadas.
5. Revisa personajes, vehículos, equipos y accesorios en F6. Señala el nombre del modelo, el lugar y el comportamiento que quieres cambiar.
6. Detén Play y vuelve a pulsar el mismo botón. Debe reutilizar la escena preparada, sin volver a copiar toda la ciudad.

Si aparece un error nuevo, conserva su primera línea y la captura de Console. Las carpetas generadas están en `Assets/Party/Generated/AlarmaPrueba_<fecha>`. El registro de preparación está en `BuildReport.json` o `BuildFailure.json`; la referencia a la última escena lista está en `Assets/Party/Generated/AlarmaPlaytestReady.json`.

## Archivos creados o modificados

- `Scripts/City/PlaytestR7/`: entrada, jugador, presentación, cámara, carga de partes, techos, puertas, catálogo e interfaz. Asamblea `Alarma.Playtest`.
- `Scripts/City/Editor/PlaytestR7/`: entrada única y constructores de recursos, mundo, actividades y escena. Añade protección de escenas y recuperación de recursos preparados. Asamblea `Alarma.Playtest.Editor`.
- `Scripts/AI/CityLifeR5/ShopActivity.cs` y `CityPopulationDirector.cs`: cada tienda puede utilizar su propio planificador en su posición real del mapa.
- `Scripts/City/Editor/CityLifeR5/CityTrafficGraphBuilder.cs`: grafo comprobado, sin el redondeo que descartaba puestos.
- `Scripts/City/Editor/CityLifeR5/CityLifeSceneBuilder.cs`: fábrica reutilizable y colisiones de NPC; se retira su entrada de menú antigua.
- `Scripts/Core/Editor/ArchitectureTestRunner.cs`, `ArtAssetBuilder.cs` y `BlenderImportValidator.cs`: sus funciones se conservan y se retiran las entradas antiguas de Alarma.
- `Art/BlenderScripts/PlaytestR7~`: exportaciones por partes, metadatos, fuentes reproducibles y resultados de comprobación. Unity ignora esa carpeta hasta que el botón importa lo necesario.
- Esta guía: `docs/Prueba-Completa-R7.md`. Versiones previas y escenas R6 conservadas.

## Verificado antes de instalar

Las cinco asambleas modificadas/nuevas se compilan contra las DLL reales de Unity 6000.3.27f2. El dominio de tráfico y compras vuelve a pasar sus comprobaciones de enfrentamientos, puerta, filas, cancelaciones y cobro único. Se validan 263 partes y los 18 puestos de las tiendas en sus coordenadas reales, con desnivel máximo de 0,17 m entre nodos vecinos. Se reimportan muestras de suelo, sectores comerciales y follaje, más las nueve piezas de puertas: nombres, unidades, límites y máscaras comprobados.

Para la corrección de escenas se comprueban cinco casos de la política de respaldo, incluida una sesión con varias escenas sin nombre. La auditoría de disco encuentra dos lotes recuperables, cada uno con los 295 modelos obligatorios y 406 materiales. Esta comprobación permite preparar la reutilización, pero la carga de objetos y la creación real de escena siguen pendientes de Unity.

**No se abrió Unity ni se ejecutó Play desde el agente.** La construcción efectiva de prefabs/escena, carga de recursos, control y render de Unity quedan pendientes de tu prueba con el botón. No se cierran tareas ni se hace commit de cierre hasta tu confirmación.

## Explicación para aprender

El botón actúa como una fachada: llama a constructores separados para importar recursos, preparar el mundo y montar la escena. Las partes de ciudad se cargan cerca de la cámara y se liberan al alejarse. El movimiento del jugador emite eventos que actualizan su animación. Cada tienda conserva su propia fila, caja y planificador. Esta separación aplica responsabilidad única y permite corregir una pieza sin concentrar toda la lógica en un único controlador.
