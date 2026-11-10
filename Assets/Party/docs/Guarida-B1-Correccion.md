# Guarida B1: aparición en planta baja y muebles — 2026-11-04

Corrección dentro de Ciudad 3.0 B1, pendiente de la prueba de Alain. No se avanza a B2 ni se cierra una tarea. Alain confirmó que salió de Play, guardó y cerró Unity antes de ajustar la escena y el modelo.

## Causa y corrección

`ReviewPlayerMotor` buscaba suelo desde tres metros por encima de los pies. Con el jugador guardado en Y=0,5, el rayo nacía en Y=3,5 y podía tomar la losa de la planta superior o el toldo como apoyo. La aceptación comprobaba otro rayo más bajo, por eso la construcción pasaba aunque Play colocara al personaje arriba.

Ahora `ReviewPlayerGrounding` aplica la misma regla al editor y al runtime: consulta desde los pies +0,28 m, admite hasta 0,65 m de descenso y exige pendiente caminable y espacio para la cápsula completa. Las capas de personajes, jugador y triggers no cuentan como obstáculos iniciales. Si el sector o el apoyo no está listo, espera y reintenta. También se recupera la posición guardada en `Awake`; el punto privado de respawn ya no termina en el origen al entrar en Play. Un destino de mapa inválido conserva el último punto seguro.

El modelo tiene un marcador `PlayerSpawn` dentro del recibidor: Blender (0, −6, 0,185), orientado hacia la sala. El constructor utiliza su posición y orientación reales después de colocar la casa, y la cámara mira en la misma dirección. La escena ya guardada recibió únicamente dos cambios de posición: jugador y cámara, conservando todos los demás objetos y GUID. Los pies quedan en aproximadamente (−528, 0,185, 135,55).

La versión vigente del constructor es `ciudad25-22`. Integra el garaje y las visitas de peatones de la revisión 21. **Alarma > Crear y probar juego** prepara la escena nueva en una carpeta independiente y conserva la ciudad anterior.

## Interior y muebles

- Tres pantallas con pie/base y contenido que gira junto con cada monitor; TV con soporte.
- Seis sillas con cuatro patas y refuerzo; silla de oficina con cinco apoyos y ruedas.
- Mesa baja con tablero/patas, cojines de sofá, puertas/manijas del mueble de TV.
- Casilleros con manijas, caja fuerte con frente y agarradera, fajos con bandas y bolsos con asas/cierre.
- Cocina con puertas, manijas, fregadero/grifo, ventana del microondas y jarra de cafetera.
- Perchero con perchas, ganchos y mangas. Se conservan distribución y pasillos.
- Hoja de la puerta de casa reducida a 2,20 m para dejar 5 cm bajo el dintel, en lugar de atravesarlo.

Los detalles pequeños llevan prefijo `Detail_` y no generan MeshCollider; las superficies principales siguen siendo obstáculos. Se conservan patio, accesos, tamaño de la casa y ciudad de 2 × 2 km. Todo se modeló con nuestras recetas mediante Blender MCP; sin descargas. `kit_parts.py` identifica Principled BSDF por tipo, porque el nombre visible cambia con el idioma de Blender.

## Archivos

- Runtime: `Scripts/City/PlaytestR7/ReviewPlayerMotor.cs`, nuevo `ReviewPlayerGrounding.cs` y su `.meta`.
- Editor: `Scripts/City/Editor/City25/City25Builder.cs`, `City25Acceptance.cs`, `City25Kit.cs`.
- Arte: `Art/BlenderScripts/build_hideout.py`, `City25~/kit_parts.py`, `Art/BlenderSources~/Alarma_Escondite.blend`, `Art/City/Shops/Local_Escondite.fbx` y seis capturas `Art/Previews~/escondite_*.png`.
- Escena: `Generated/Ciudad2km/Scenes/Ciudad_2km.unity`, solo las posiciones iniciales de jugador/cámara.
- Evidencias y herramientas: `Art/BlenderScripts/HideoutB1Fix~`, este documento, historial de AGENTS/TASKS y manifiesto de respaldo actualizado.

## Verificación realizada

18 pruebas analíticas del código real de movimiento/apoyo con sustitutos de las consultas físicas: losa/toldo, pendiente, obstrucción, capas, triggers, espera del sector, reintento, respawn y mapa. No son una ejecución de PhysX. Runtime y editor compilaron contra las DLL instaladas de Unity 6000.3.27f2, sin abrir el editor.

FBX reimportado en Blender 5.2.3 LTS: 363 mallas, 13.392 triángulos, marcador Z≈0,185 y suelo Z≈0,150. La consulta corta encuentra el piso. Muestras contra triángulos reales alrededor del eje de la cápsula de 1,75 × 0,48 m dan separación mínima 0,275 m, mayor que su radio 0,24 m. No sustituye las colisiones de PhysX.

Se revisaron renders del interior/dinero/tablero y una captura nativa del viewport (`HideoutB1Fix~/viewport_interior.png`). Es una vista de Blender; no es una captura del juego. Los renders de revisión cortan el techo, mientras la escena del juego conserva su techo estable. El agente no abrió Unity ni entró en Play.

## Pasos para el editor

1. Abrir Unity 6000.3.27f2 y esperar importación/compilación. Mantener Play detenido.
2. Abrir `Assets/Party/Generated/Ciudad2km/Scenes/Ciudad_2km.unity`, recuperada tras el intento fallido. No añadir una cámara a la escena vacía Untitled.
3. Pulsar **Alarma > Crear y probar juego**. La revisión 22 verifica aceras y accesos comerciales contra la geometría importada. Los usos posteriores abren la última preparación publicada.
4. Esperar a que termine y entre en Play. No iniciar la escena vieja antes de esta preparación para revisar los colliders nuevos.

## Cómo probarlo

1. Comprobar que Don Sigilo empieza **dentro del recibidor, en planta baja**, con el suelo bajo los pies y el techo por encima. No debe aparecer en balcón, losa ni origen del mapa.
2. Caminar y correr hacia la mesa y por sus costados; revisar soportes de pantallas/TV, sillas, cocina, caja fuerte y perchero. Confirmar que no atraviesa los muebles principales.
3. Abrir ambas hojas de casa con E, salir al patio, abrir el portón peatonal, volver a entrar y comprobar que la cámara permanece dentro de paredes/techo.
4. Cambiar F1–F4 y confirmar que el personaje conserva el piso. Con M, viajar a un lugar de revisión y volver al escondite; el ajuste de suelo no debe subir a la losa.
5. Salir y entrar en Play dos veces. Confirmar que siempre vuelve al recibidor, sin arrastrar la posición de la sesión anterior.
6. Revisar Console. Si hay error, adjuntar texto y captura; se corrige dentro de B1. Multiplayer Play Mode no corresponde a esta prueba local; red continúa pendiente.

Tras la confirmación de Alain se podrá cerrar la corrección y hacer su commit. El respaldo publicado anterior sigue disponible en `e4d28cf`; todavía no se publica esta corrección pendiente de prueba.

## Explicación para aprender

El rayo debe buscar cerca de los pies: un rayo que empieza sobre un techo puede confundirlo con el piso. Separar esa decisión del movimiento cumple responsabilidad única. Compartir la misma regla evita que el constructor y Play acepten posiciones distintas. El marcador pertenece al modelo y sigue su posición y giro al colocar la casa. Los eventos de velocidad mantienen Observer para comunicar movimiento y animación sin unir sus responsabilidades. Los detalles visuales pequeños no necesitan la misma colisión que un mueble completo.

## Fallo de carpetas y escena vacía — revisión 19

La prueba de Alain falló con `Parent directory must exist before creating asset` al crear `Art/Car_Sedan_Alarma_Trim.asset`. `Editor.log` sitúa el error en `City25Kit.MakeParked`, después de la preparación de materiales. El código anterior creaba directorios con `Directory.CreateDirectory` y llamaba `Refresh`, pero no verificaba que AssetDatabase reconociera cada carpeta. El mensaje nativo confirma la precondición ausente; sin ejecutar Unity no se atribuye a una carrera concreta del importador.

El manejador de errores agravaba el fallo: intentaba cerrar la única escena temporal y borraba incondicionalmente toda la salida generada. El registro confirma `Unloading the last loaded scene` en ese `catch`. El resultado fue una escena Untitled vacía, sin cámara, y 538 archivos generados faltantes. Alain cerró Unity para permitir la recuperación.

Se recuperaron únicamente los archivos faltantes desde el commit de respaldo y se reaplicaron las dos posiciones B1 de jugador/cámara. La escena coincide con la huella B1 anterior al fallo: `5920f16cb8bb45c6b84aa2c851a3d3d2047d8e30ff861fc64a30f87046f4606d`. Se preservan las modificaciones de materiales que Unity escribió durante el intento; no se revierten archivos existentes.

Cambios de esta revisión:

- `FlatMaterialLibrary.EnsureFolder` crea cada nivel con `AssetDatabase.CreateFolder`, importa directorios físicos pendientes y comprueba GUID, ruta exacta, existencia y registro. No acepta una carpeta alternativa como `Art 1`.
- `PrepareOutput` usa esa regla para sus seis subcarpetas. `City25Kit` vuelve a comprobar los padres inmediatamente antes de crear mallas, materiales apagados y prefabs de autos.
- Nuevo `City25BuildRecovery.cs` y `.meta`: copia íntegra de la salida anterior y sus `.meta` bajo `Library/Alarma/City25Recovery/<id>` antes de reemplazarla. No duplica GUID dentro de Assets.
- Si falla la reconstrucción, recupera los archivos e importa la salida anterior antes de restaurar las escenas guardadas. No intenta cerrar la última escena. Los errores previos a la mutación no borran la ciudad vigente.
- Una salida ya publicada no se revierte por errores posteriores de interfaz. La copia temporal se elimina solo al finalizar con éxito; si la recuperación falla, el diálogo muestra dónde se conservó el respaldo.

Se actualizan también este documento, AGENTS/TASKS, el manifiesto local y las evidencias de pruebas. Sigue siendo B1 pendiente de prueba, sin commit ni publicación. El agente no abrió Unity ni ejecutó Play.

Validación de la revisión 19: 26 regresiones superadas con el helper real de recuperación y los métodos reales de carpeta/catch, usando sustitutos de AssetDatabase y de escenas. Las copias/restauraciones de archivos se ejercitaron con bytes y `.meta` reales en una carpeta temporal. Incluyen creación recursiva, carpetas no registradas, rechazo de sufijos, recuperación exacta, errores anteriores a mutación y posteriores a publicación, última escena y conservación de respaldo. Alarma.CityLife.Editor y Alarma.City.Editor compilaron contra las DLL instaladas (exit 0). Evidencias y runner: Art/BlenderScripts/HideoutB1Fix~/BuildRecoveryTests~. No se ejecutó el importador nativo ni Play; Alain debe repetir la prueba de editor indicada arriba.

## Revisión 20 de aceras y acceso a la guarida

El desplazamiento lateral del peatón usaba un vector cuya longitud dependía de la arista. En tramos largos podía mandar al NPC hasta 5,20 m fuera de su ruta. El grafo también tenía atajos que cortaban esquinas. Ahora los carriles laterales se calculan en metros y el constructor comprueba el pavimento, los desniveles y el espacio de la cápsula en cada recorrido. En Play, cada peatón comprueba el siguiente movimiento y espera o elige otro tramo si encuentra una obstrucción. Las calzadas se usan en los cruces definidos. Al bajar del bordillo, el peatón conserva la altura hasta que su cápsula despeja el borde. Los autos mantienen su espera mientras haya un obstáculo, incluso tras seis segundos.

La puerta de la casa y el portón peatonal usan un punto de contacto ligado a la hoja. Al acercarse con movimiento hacia la puerta o pulsar E, el personaje se alinea y lleva la palma a ese punto. La hoja empieza a girar cuando la palma llega y el contacto la acompaña durante el empuje. La hoja frena si detecta un obstáculo en su giro y espera a que quede libre el umbral antes de cerrar. La corredera de vehículos conserva E y se desplaza en metros con detección de obstáculos.

El exterior revisado es el de la guarida. Tiene un sendero continuo a la acera con 3 mm de diferencia de altura, un hueco libre de 1,40 m, postes y bisagras visibles, lámpara sujeta, jardineras con follaje modelado y guía de corredera a ras del acceso. El FBX conserva el interior y el marcador de aparición de la revisión anterior. La escena generada que Alain guardó con la revisión 19 se conserva hasta que pulse el constructor.

La copia local `Library/Alarma/City25Recovery/AntesRevision20-CiudadGuardada19.zip` contiene los 538 archivos y metadatos de esa salida generada. Cada entrada se comparó por SHA-256 con el archivo de disco.

### Archivos de la revisión 20

- Peatones de calle en `Scripts/AI/Street/` — `SidewalkGraph.cs`, `SidewalkPopulation.cs`, `SidewalkWalker.cs` y `SidewalkClearance.cs` con su `.meta`.
- Puertas y peatones de tienda en `Scripts/AI/CityLifeR5/` — `ShopDoor.cs`, `ShopActivity.cs`, `PedestrianActor.cs`, `PedestrianReach.cs`, `PedestrianMovement.cs` y `CityTrafficController.cs`.
- Jugador y corredera en `Scripts/City/PlaytestR7/` — `ReviewDoorInteraction.cs`, `ReviewPlayerMotor.cs` y `ReviewSlidingDoor.cs`. Tráfico en `Scripts/Traffic/TrafficCar.cs`.
- Constructor en `Scripts/City/Editor/City25/` — `City25Builder.cs`, `City25Kit.cs`, `City25Life.cs` y `City25Walkability.cs` con su `.meta`.
- Datos de rutas en `Art/BlenderScripts/City25~/city_life.py` y `city_life.json`.
- Modelo en `Art/BlenderScripts/build_hideout.py`, `Art/BlenderSources~/Alarma_Escondite.blend`, `Art/City/Shops/Local_Escondite.fbx`, `Art/City/Shops/hideout_materials.json` y seis vistas en `Art/Previews~/escondite_*.png`.
- Pruebas y captura en `Art/BlenderScripts/HideoutB1Fix~/`. También se actualizaron este documento, AGENTS.md, TASKS.md y el inventario de respaldo.

### Prueba de la revisión 20 en Unity

1. Tras construir desde el menú, confirma que apareces dentro de la guarida en planta baja. Cruza la puerta de casa hacia el patio.
2. Acércate al portón con W. Mira que la palma alcance la placa antes de que gire la hoja. Cruza sin soltar W. Espera en el umbral y verifica que el portón se mantenga abierto. Aléjate y observa el cierre.
3. Vuelve desde la acera. Pulsa E cerca de la placa y repite el cruce en sentido contrario. Prueba con F1–F4 para comparar el alcance de los cuatro personajes.
4. Rodea la manzana. Observa peatones en las dos aceras, al doblar una esquina y en un cruce con semáforo. Ponte delante de uno y comprueba si espera o busca otro tramo. Comprueba que los autos esperen hasta liberar el paso.
5. Observa a un cliente cruzar la puerta de un comercio. Revisa la consola al terminar. Esta revisión se prueba en Play local.

### Verificación fuera de Unity

Siete asambleas compilaron juntas contra las DLL instaladas. La auditoría del grafo analizó 45.759 tramos y 806 cruces, sin rutas que entren en la parcela de la guarida. Pasaron 23 casos peatonales, 11 de interacción del jugador, 11 de acercamiento de compradores, 25 del movimiento de la hoja y 5 de tráfico. Los ensayos de comportamiento sustituyen las consultas físicas. Se estimó el alcance a las placas en 16 poses sobre los cuatro rigs originales y el margen quedó dentro de la tolerancia del gesto.

El FBX reimportado en Blender pasó 171 muestras de giro y comprobaciones del sendero y la cápsula con el portón abierto en ambos sentidos. La captura del viewport muestra la geometría en pose abierta. Falta verificar la importación, la animación del personaje y las colisiones en Play.

## Revisión 21 del garaje y las visitas

El registro de Unity de la prueba de Alain confirma que la revisión 20 publicó 43.957 tramos y 22 comercios con interior. La espera en los cruces carecía de salida alternativa y el radio anterior incluía vehículos ajenos al paso. Ahora se consulta el corredor del cruce. Si la espera se prolonga, el peatón busca otro tramo. Se separan los puntos de aparición y se excluyen las bocas de cruce y los grupos aislados de menos de ocho nodos.

La ciudad usa el mismo peatón para pasear y visitar comercios. Elige un local cercano con ruta válida por su lado de la calle. Reserva una visita, camina hasta la entrada, usa la rutina interior, vuelve por el mismo acceso y continúa paseando. Cada local recibe un visitante a la vez en esta revisión. Las compras usan la caja y el inventario existentes. En el banco el cliente va a caja, recibe efectivo y un comprobante. El retiro resta de la caja del banco y suma a la cartera ambiental del peatón.

El acceso ancho de la guarida ahora es un garaje cubierto. La persiana de 17 lamas sube 2,465 m y el tramo visible conserva colisión. Si la bajada detecta un cuerpo, la persiana vuelve a subir. La bahía admite la envolvente del compacto de 3,90 m del proyecto. La entrada peatonal y la aparición en planta baja se conservan. La copia local `Library/Alarma/City25Recovery/AntesRevision21-CiudadGuardada20.zip` guarda 538 archivos y metadatos de la escena anterior, cotejados por SHA-256.

### Archivos de la revisión 21

- Peatones de calle en `Scripts/AI/Street/` — `SidewalkWalker.cs`, `SidewalkPopulation.cs`, `SidewalkGraph.cs`, `SidewalkClearance.cs` y `SidewalkVisit.cs` con su `.meta`. Referencia añadida a `Scripts/AI/Alarma.AI.asmdef`.
- Rutina y caja en `Scripts/AI/CityLifeR5/` — `PedestrianActor.cs`, `PedestrianMovement.cs`, `CityTrafficController.cs`, `ShopActivity.cs`, `ShopTaskSettings.cs`, `ShoppingPresentation.cs`, `Domain/PedestrianRoutine.cs` y `Domain/ShopService.cs`.
- Constructor en `Scripts/City/Editor/City25/` — `City25Builder.cs`, `City25Characters.cs`, `City25Kit.cs`, `City25Life.cs`, `City25Shops.cs` y `City25Walkability.cs`. Persiana en `Scripts/City/PlaytestR7/ReviewSlidingDoor.cs`.
- Arte en `Art/BlenderScripts/build_hideout.py`, `Art/BlenderSources~/Alarma_Escondite.blend`, `Art/City/Shops/Local_Escondite.fbx`, su manifiesto de materiales y seis vistas de la guarida en `Art/Previews~/`.
- Evidencia y pruebas en `Art/BlenderScripts/HideoutB1Fix~/Visit21~`, `SidewalkTests~` y `DoorContactTests~` dentro de la misma carpeta. También se actualizaron esta guía, el historial de B1 y el inventario de respaldo.

### Prueba de la revisión 21 en Unity

1. Abrir `Ciudad_2km.unity` y pulsar **Alarma > Crear y probar juego**. Esperar **Verificando aceras**. Revisar en Console el número de comercios conectados.
2. Salir al patio por la puerta de casa. Acercarse al garaje por la calle y pulsar **E**. Entrar a la bahía, detenerse bajo la persiana y comprobar que el cierre espere o reabra. Alejarse para ver el cierre completo. Repetir el acceso peatonal con **W**.
3. Volver a la esquina del reporte y observar durante un ciclo de semáforo. Comprobar que los peatones esperen con tráfico y que los que no puedan cruzar continúen por otra acera.
4. Usar **M** y seleccionar un supermercado, una joyería y un banco. Mirar desde fuera hasta que se acerque un peatón. Seguir al mismo personaje mientras entra, compra o recibe dinero y vuelve a pasear.

### Verificación de la revisión 21

Las siete asambleas compilaron contra las DLL instaladas. Pasaron 36 pruebas de calle y transacciones, 11 de interacción del jugador y 13 de acceso de compradores con simulación de colisiones. El contraste del suelo FBX con el grafo guardado encontró un acceso candidato para cada uno de los 22 comercios. El constructor comprueba los obstáculos reales de la escena al conectar los candidatos. El FBX de la guarida superó 100 muestras del recorrido de la persiana, la envolvente del compacto y 171 muestras del giro del portón peatonal. La reconstrucción y el recorrido en Play quedan pendientes de Alain.

## Revisión 22 de recuperación y publicación

En la prueba de la revisión 21, Unity devolvió error al borrar `Generated/Ciudad2km` después de retirar parte de su contenido. La recuperación volvió a intentar la misma operación y falló. El proyecto quedó en escenas vacías sin cámara. El registro identifica el fallo de borrado. El estado en disco confirmó que solo quedaban cuatro archivos de la salida anterior.

Con Unity cerrado se repusieron los 534 archivos faltantes desde `Library/Alarma/City25Recovery/AntesRevision21-CiudadGuardada20.zip`. Los 538 archivos y metadatos coinciden con la copia, incluida la escena anterior. La restauración abrió los destinos faltantes en modo de creación exclusiva y conservó los cuatro archivos que seguían presentes.

El constructor prepara mallas, datos, prefabs y escena en `Generated/Ciudad2km/Revisiones/R_<id>`. Una vez guardada e importada la escena, reemplaza el informe de ciudad y actualiza la entrada correspondiente de Build Settings. Si falla antes de publicar, recupera el montaje previo o vuelve a abrir la última ciudad válida cuando el editor partió de escenas vacías. Una limpieza fallida solo afecta la carpeta del intento. El respaldo portátil toma su escena principal del informe publicado.

La prueba posterior cargó la ciudad restaurada, pero la revisión 22 se detuvo al pedir una activación adicional de la etapa. La comprobación ahora acepta una escena válida y cargada cuando ya está activa. El respaldo solicitado por Alain incluye esta corrección y conserva la revisión 20 como última escena guardada. B1 sigue pendiente de Play.

### Archivos de la revisión 22

- Repuestos 534 archivos y metadatos en `Generated/Ciudad2km/`.
- Constructor en `Scripts/City/Editor/City25/` — `City25Builder.cs`, `City25BuildRecovery.cs`, `City25Data.cs` y `City25Kit.cs`.
- Respaldo en `Tools~/backup_project.py` y `Tools~/backup-manifest.json`.
- Pruebas actualizadas en `Art/BlenderScripts/HideoutB1Fix~/BuildRecoveryTests~/`. Evidencias nuevas en `publication-results.txt` y `publication-results.json`.
- Registro actualizado en esta guía, AGENTS.md y TASKS.md.

### Prueba de la revisión 22 en Unity

1. Abrir Unity y esperar la importación. En Project, abrir `Assets/Party/Generated/Ciudad2km/Scenes/Ciudad_2km.unity`. Confirmar que la jerarquía muestra la ciudad.
2. Pulsar **Alarma > Crear y probar juego**. Esperar a que termine la reconstrucción. La escena nueva debe quedar en `Generated/Ciudad2km/Revisiones/` y el jugador debe aparecer dentro de la guarida.
3. Detener Play y pulsar el mismo menú otra vez. Debe abrir la misma revisión y entrar en Play sin reconstruir.
4. Continuar las pruebas del garaje y los peatones de la revisión 21.

### Verificación de la revisión 22

Pasaron 15 regresiones con el código real de preparación y sustitutos de escenas y AssetDatabase. Incluyen una etapa ya activa, borrado parcial, restauración de una ciudad desde escenas vacías, publicación con archivo bloqueado y preservación de escenas ajenas en Build Settings. El bloqueo del informe y la comparación de archivos usaron el sistema de archivos real de Windows. El respaldo reconoció una revisión publicada y rechazó una ruta externa. Alarma.CityLife.Editor y Alarma.City.Editor compilaron contra las DLL de Unity instaladas. La reconstrucción con el importador nativo y la prueba en Play quedan pendientes.

## Revisión 23 de clientes en supermercado, banco y joyería

Alain probó la revisión 22. Al llegar con M al supermercado, al banco o a la joyería no había peatones caminando y nadie entraba a los locales.

Causas en el código de la población de aceras:

1. **Llegada con el mapa.** Tras el viaje se retiraban los peatones lejanos, pero los nuevos solo podían aparecer a más de 30 m del jugador y a razón de cuatro intentos cada medio segundo. El entorno del local quedaba vacío varios segundos.
2. **Visitas escasas.** Cada local aceptaba un único cliente a la vez. Un peatón solo valoraba visitar un local situado a menos de 32 m por su misma acera. Con 45 peatones repartidos en 120 m, una tienda concreta casi nunca recibía visitas.

Cambios, sin reconstruir la ciudad ni modificar la escena publicada:

- `SidewalkPopulation` reconoce un salto mayor de 40 m entre dos cuadros como viaje con el mapa. En ese caso repuebla al instante desde 6 m del jugador.
- Cada local abierto a menos de 85 m del jugador mantiene hasta tres clientes. Al llegar, uno empieza ya frente a la puerta y entra, y otro aparece en la misma acera y camina hacia el local. Después, los clientes nuevos llegan cada 4–10 s, fuera de cámara, a 8–40 m de la entrada.
- Si el cupo de 45 peatones está lleno, la población retira un paseante sin visita, lejano y fuera de cámara, para dejar sitio a un cliente.
- `SidewalkVisit` acepta varios clientes, con una separación de 4 s entre llegadas para evitar choques en la puerta. La búsqueda de locales por la acera llega a 45 m.
- `SidewalkWalker` recibe el local asignado, busca la ruta por su acera y reserva su lugar. Si no existe ruta sin cruzar la calzada, no se envía.

Los valores se ajustan en el componente **Peatones** de la escena (sección «Clientes de los locales»), sin regenerar la ciudad.

### Archivos de la revisión 23

- `Scripts/AI/Street/SidewalkPopulation.cs`, `SidewalkVisit.cs` y `SidewalkWalker.cs`.
- Pruebas en `Art/BlenderScripts/HideoutB1Fix~/SidewalkTests~/`: `VisitTests.cs` y `StreetStubs.cs` actualizados, `PopulationTests.cs` nuevo, `run_tests.py` sin versión fija de .NET. Resultados en `runtime-results.txt`.
- Registro en esta guía, AGENTS.md y TASKS.md.

### Prueba de la revisión 23 en Unity

1. Volver a Unity y esperar la compilación. Console sin errores rojos.
2. Pulsar **Alarma > Crear y probar juego**. Debe abrir la revisión publicada y entrar en Play sin reconstruir.
3. Abrir el mapa con M y viajar al supermercado. Desde el primer segundo debe haber peatones en la acera. Un cliente debe empezar en la puerta y entrar. Otro debe llegar caminando.
4. Esperar 30–60 s frente al local. Deben entrar más clientes, como máximo tres a la vez. Dentro eligen el producto, hacen cola, pagan, reciben la boleta y salen a la acera.
5. Repetir en el banco (retiran efectivo en el mostrador) y en la joyería.
6. Revisar Console. Si aparece «Rutina de compra interrumpida» o cualquier error, adjuntar texto y captura.

### Verificación de la revisión 23

Alarma.AI y Alarma.City.Editor compilaron con C# 9 contra las DLL de Unity 6000.3.27f2 instaladas. Pasaron 50 pruebas de calle, visitas y población: las 36 anteriores, 8 nuevas de capacidad, ruta asignada y arranque en la puerta, y 6 de población, entre ellas el viaje con M a 296 m. Los ensayos sustituyen PhysX, la cámara y el pool por modelos simples. No se ejecutó Play.

### Explicación de la revisión 23

La población es una **Object Pool**: reutiliza peatones en lugar de crearlos y destruirlos. El viaje se detecta observando la posición del jugador, sin que el mapa conozca a los peatones (**D**, inversión de dependencias). Cada clase conserva una responsabilidad (**S**). La población decide cuántos clientes y cuándo llegan. La visita guarda las reservas del local. El planificador calcula rutas. El peatón camina y ejecuta su rutina. Los números nuevos son campos serializados, así que se ajustan en el Inspector sin cambiar el código (**O**).

## Revisión 24: banco rediseñado y personal en los locales

Alain pidió personal atendiendo en todos los negocios y diseños menos básicos, empezando por el banco. Antes, cada local tenía un solo cajero con ropa de civil y el banco tenía cuatro ventanillas y cuatro escritorios vacíos.

**Referencias consultadas.** Distribución de sucursales: ventanillas al fondo por seguridad, recepción pasada la entrada, asesores, espera cómoda y cajeros automáticos aparte (The Financial Brand, Archello, Design Clarity).

**Banco nuevo** (`build_shops.py`, `furnish_banco`):

- Cuatro ventanillas con vidrio de seguridad, bandeja, número y pantalla «TURNO A-07». La zona de personal tiene bóveda, cajas fuertes y archivadores, con puertas «SOLO PERSONAL».
- Fila con postes y cordón hasta la ventanilla 2, donde ahora se hace el retiro (antes era un mostrador junto a la puerta).
- Recepción «INFORMACIÓN», máquina de turnos, folletos y vestíbulo «CAJEROS 24 H».
- Dos cubículos de asesores con vidrio y afiches, oficina de «GERENCIA» con biblioteca y una sala de espera con dos grupos de sillas.
- Losas de 2 m, zócalo de madera, cuadros, lámparas colgantes, marquesina lisa y pilares revestidos (sin toldo a rayas). Total: 246 piezas y 53.256 triángulos.

**Personal.** Cada local puede declarar puestos (`staff` en `shop_layouts.json`) con rol, pose, posición y uniforme. El banco tiene 8 empleados:

- 4 cajeros de pie (uno es el cajero que atiende).
- 2 asesores sentados.
- 1 gerente sentado.
- 1 recepcionista.

`analyze_staff_uniforms.py` midió en qué altura cae cada material de los diez civiles y guardó las prendas de arriba y de abajo en `Characters/Cast/staff_uniform_slots.json`. `City25Staff` las cambia por el saco verde y el pantalón grafito del banco; el gerente va de traje azul. Los sentados usan la misma regla de huesos que los conductores (`SeatedPose`). Los demás locales no cambian hasta su propio rediseño.

`build_shops.py -- --only banco` regenera solo ese local y conserva los otros cinco: su FBX, su entrada del JSON y sus materiales. `alarmart.py` acepta el motor EEVEE de Blender 4.5 y de Blender 5.

### Archivos de la revisión 24

- Blender:
  - `Art/BlenderScripts/build_shops.py` y `alarmart.py`.
  - Nuevo `analyze_staff_uniforms.py`.
  - `BlenderSources~/Alarma_Shops_banco.blend`.
- Salida:
  - `Art/City/Shops/Local_Banco.fbx`, `shop_layouts.json` y `shop_materials.json`.
  - `Art/Characters/Cast/staff_uniform_slots.json`.
- Capturas: `Art/Previews~/local_banco_{fachada,interior,pasillo,ventanillas,asesores,gerencia}.png`.
- Unity:
  - Nuevo `Scripts/City/Editor/City25/City25Staff.cs`.
  - `City25Shops.cs` y `City25Data.cs`.
  - `City25Builder.cs`: constructor `ciudad25-24`.

### Prueba de la revisión 24 en Unity

1. Volver a Unity y esperar la importación de `Local_Banco.fbx` y la compilación. Console sin errores rojos.
2. Pulsar **Alarma > Crear y probar juego**. Esta vez reconstruye la ciudad porque cambiaron el banco y el constructor. Console debe mostrar «Personal de locales: 22 cajeros y 21 empleados más» (3 bancos × 7).
3. Con M, viajar al banco. Revisar:
   - Fachada sin toldo.
   - Cuatro cajeros detrás del vidrio.
   - Asesores y gerente sentados en sus sillas.
   - Recepcionista en la entrada.
   - Todos con uniforme.
4. Esperar a un cliente: entra, hace fila entre los cordones, retira en la ventanilla 2 y sale.
5. Si un empleado flota, atraviesa la silla o mira hacia la pared, enviar captura y su nombre en Hierarchy.

### Verificación de la revisión 24

Blender 4.5.10 generó el banco sin errores. Las capturas se revisaron: ventanillas, sala, asesores y gerencia. La comprobación de la cuadrícula caminable (misma regla que `City25Shops.Cells`) dio 916 celdas, todos los puntos de la rutina dentro y conectados desde la acera. Los otros cinco locales quedaron idénticos en el JSON. Alarma.AI y Alarma.City.Editor compilaron contra Unity 6000.3.27f2. No se ejecutaron la reconstrucción ni Play.

## Revisión 25: joyería rediseñada con personal

Alain aprobó el banco de la revisión 24 y pidió seguir con la joyería. Antes eran cajas sueltas sobre un piso de tablero, sin luz de acento ni empleados.

**Referencias.** Las joyerías usan un circuito de vitrinas con el vendedor detrás. Suman un mostrador donde el cliente se sienta para piezas caras y luz en tres capas: general, de acento y de vitrina. La zona de personal está separada (Jewel360, InStore, Degree Furniture).

**Joyería nueva** (`furnish_joyeria` y `showcase` en `build_shops.py`):

- **Fondo:** mostrador de atención de 10 m con vitrina, tres taburetes de terciopelo y caja a la derecha. Detrás hay cuatro nichos de nogal con fondo morado, estantes de vidrio y luz. Encima, el letrero dorado «JOYERÍA AURA». La puerta «SOLO PERSONAL» lleva a las cajas fuertes y al panel de alarma.
- **Lados:** seis vitrinas separadas de la pared, con tira de luz y joyas. El vendedor atiende desde el pasillo trasero, con espejos de marco dorado y una línea de luz detrás.
- **Centro:** dos islas hexagonales con cúpula de cristal para rodear y una lámpara de araña dorada. Hay focos sobre cada vitrina y los láseres de seguridad siguen sobre el mostrador.
- **Entrada:** escaparates con pedestales, un busto con collar y anillos. También hay un rincón de espera con dos sillones y mesa dorada, un espejo de pie, una planta y una alfombra de terciopelo.
- **Acabados:** paredes champán, losas oscuras de 2 m, marquesina morada y pilares revestidos (sin toldo a rayas). Total: 229 piezas y 25.860 triángulos.

**Personal:** 4 empleados con saco ciruela y pantalón negro:

- La cajera en el mostrador.
- Una asesora junto a los taburetes.
- Dos vendedores detrás de las vitrinas laterales.

Los clientes miran joyas en 12 puestos (vitrinas, islas y mostrador), hacen fila y pagan en la caja del mostrador.

### Archivos de la revisión 25

- `Art/BlenderScripts/build_shops.py` y `BlenderSources~/Alarma_Shops_joyeria.blend`.
- `Art/City/Shops/Local_Joyeria.fbx`, `shop_layouts.json` y `shop_materials.json`.
- Capturas: `Art/Previews~/local_joyeria_{fachada,interior,pasillo,mostrador,vitrinas,islas}.png`.
- Sin cambios de código en Unity: `City25Staff` lee los puestos nuevos.

### Prueba de la revisión 25 en Unity

1. Volver a Unity y esperar la importación. Pulsar **Alarma > Crear y probar juego**. Reconstruye la ciudad.
2. La Console debe mostrar «Personal de locales: 22 cajeros y 30 empleados más»: 3 bancos × 7 y 3 joyerías × 3.
3. Con M, viajar a la joyería. Revisar los cuatro empleados con uniforme y a los clientes mirando vitrinas, haciendo fila y pagando en el mostrador.
4. Repetir la revisión del banco de la revisión 24.

### Verificación de la revisión 25

Blender 4.5.10 generó la joyería sin errores y las capturas se revisaron. La cuadrícula caminable dio 1069 celdas, con todos los puntos de la rutina dentro y conectados. Los otros cinco locales siguen idénticos en el JSON, incluido el banco. Alarma.City.Editor compiló contra Unity 6000.3.27f2. No se ejecutaron la reconstrucción ni Play.

## Revisión 26: supermercado rediseñado con personal

Alain aprobó la joyería de la revisión 25 y pidió seguir con el supermercado. Antes tenía tres pasillos, una sola caja junto a la puerta y cajones de fruta contra la pared.

**Referencias.** Las frutas y verduras reciben al cliente en la entrada. Las góndolas forman un circuito y los refrigerados van al fondo para que se recorra el local. Las cajas quedan visibles desde todo el local y las ofertas se ponen en los extremos de los pasillos (Esselunga en Archello, Florida Trend, ITRetail, Seattle Times).

**Supermercado nuevo** (`furnish_supermercado` y `checkout_lane` en `build_shops.py`):

- **Cajas:** tres líneas numeradas junto a la salida, con cinta, escáner, caja registradora, zona de embolsado y luz. La primera es la que cobra. Una baranda separa la salida.
- **Verdulería:** al entrar a la derecha, dos islas de mesas con cajones inclinados de fruta y verdura, una balanza, carros y canastos junto a la puerta.
- **Pasillos:** cuatro pasillos (LIMPIEZA, ABARROTES, SNACKS, CONSERVAS) con letreros colgantes y una isla «OFERTA» con latas en cada punta. Hay estanterías de limpieza en la pared izquierda.
- **Fondo:** lácteos refrigerados a la izquierda y un mostrador de «CARNICERÍA · PANADERÍA» con vitrina, cortes, pan y repisas a la derecha. Bebidas frías en la pared derecha, más el cajero automático.
- **Acabados:** losas de 2 m y marquesina naranja con pilares revestidos (sin toldo a rayas). Total: 412 piezas y 177.320 triángulos. El anterior tenía 132.408. El 70 % viene del prop `RetailShelf` ya existente (45 estanterías en lugar de 36). Queda pendiente medir con el Profiler en Play antes de decidir si se optimiza.

**Personal:** 6 empleados:

- Tres cajeros con polo naranja.
- Un reponedor con su carro de cajas.
- Un carnicero y una panadera con ropa blanca.

Los clientes miran productos en 37 puestos, hacen fila en la caja 1 (tres lugares) y pagan.

### Archivos de la revisión 26

- `Art/BlenderScripts/build_shops.py` y `BlenderSources~/Alarma_Shops_supermercado.blend`.
- `Art/City/Shops/Local_Supermercado.fbx`, `shop_layouts.json` y `shop_materials.json`.
- Capturas: `Art/Previews~/local_supermercado_{fachada,interior,pasillo,cajas,verduleria,carniceria}.png`.
- Sin cambios de código en Unity.

### Prueba de la revisión 26 en Unity

1. Volver a Unity y esperar la importación. Pulsar **Alarma > Crear y probar juego**. Reconstruye la ciudad.
2. La Console debe mostrar «Personal de locales: 22 cajeros y 50 empleados más»: bancos 3 × 7, joyerías 3 × 3 y supermercados 4 × 5.
3. Con M, viajar al supermercado. Revisar los tres cajeros, el reponedor, la carnicería con su personal y a los clientes eligiendo productos, haciendo fila en la caja 1 y pagando.
4. Abrir Window > Analysis > Profiler dentro del supermercado y anotar los milisegundos de CPU y GPU. Con eso se decide si hay que aligerar las estanterías.

### Verificación de la revisión 26

Blender 4.5.10 generó el supermercado sin errores y las capturas se revisaron. La cuadrícula caminable dio 908 celdas, con todos los puntos de la rutina dentro y conectados. Banco, joyería y los demás locales siguen idénticos en el JSON. Alarma.City.Editor compiló contra Unity 6000.3.27f2. No se ejecutaron la reconstrucción, Play ni el Profiler.

## Revisión 27: minimarket, comida y ropa rediseñados con personal

Alain aprobó el supermercado de la revisión 26 y pidió seguir. Con estos tres locales, los seis tipos quedan rediseñados con personal.

**Referencias.**

- **Minimarket:** caja en la entrada para recibir y vigilar, impulso en el mostrador, café contra una pared y lejos de la puerta, bebidas frías al fondo y pasillos visibles (Parts Town, NRS, SLD, CSP Daily News).
- **Comida rápida:** pedido en mostrador con cocina abierta, retiro separado de la fila y asientos por zonas: reservados, mesa comunitaria y mesas de dos (Toast, QSR Magazine).
- **Ropa:** zona despejada al entrar, caja adelante a la izquierda, lo más vendido en la pared derecha y asiento junto a los probadores (Small Business Trends, Top to Toe).

**Minimarket** (`cash_counter`, `wall_stock`):

- Caja a la izquierda de la entrada con golosinas de impulso y repisa de colores detrás con panel «LOTERÍA».
- Tres pasillos cortos con islas de snacks y «BEBIDAS FRÍAS» con refrigeradores en todo el fondo.
- Vitrina caliente con salchichas en la esquina, estación de «CAFÉ» con tres máquinas y vasos, expendedora, cajero automático, hielo, canastos y espejo convexo.
- Personal: cajera y reponedor, con polo verde.
- 217 piezas y 94.060 triángulos; la mayor parte son las estanterías del kit.

**Comida** (`booth`):

- Mostrador de pedidos con caja, bandejas bajo lámparas de calor y menús colgantes (HAMBURGUESAS, COMBOS, BEBIDAS).
- Cocina abierta con plancha y campana, freidora, mesa de armado con salsas y refrigeradores.
- Bebidas de autoservicio y estante «RETIRO» numerado a los lados. Condimentos y basurero con bandejas camino a la salida.
- Tres reservados con cuadros y lámparas, mesa comunitaria con 12 taburetes, mesas de dos y el letrero «SABOR DE BARRIO».
- Personal: cajera con polera roja, dos cocineros de blanco y un mesero.
- 237 piezas y 26.160 triángulos.

**Ropa** (`round_rack`):

- Vidrieras con maniquíes sobre tarimas y mesa de presentación con prendas dobladas en la zona de entrada.
- Caja a la izquierda con bolsas y panel «MODA URBANA».
- Pared derecha con rieles de prendas y cubículos de doblados.
- Cuatro percheros redondos y tres rectos con letreros MUJER y HOMBRE.
- Cuatro probadores numerados, espejo grande y banca para acompañantes.
- Personal: cajera, vendedora y encargada de probadores, con polera negra y jeans.
- 264 piezas y 25.196 triángulos.

Los tres locales usan losas de 2 m. Ropa usa marquesina y revestimiento; minimarket y comida conservan su toldo para variar la calle.

### Archivos de la revisión 27

- `Art/BlenderScripts/build_shops.py` y `BlenderSources~/Alarma_Shops_minimarket_comida_ropa.blend`.
- `Art/City/Shops/Local_Minimarket.fbx`, `Local_Comida.fbx`, `Local_Ropa.fbx`, `shop_layouts.json` y `shop_materials.json`.
- Capturas: `Art/Previews~/local_{minimarket,comida,ropa}_*.png` (seis por local).
- Sin cambios de código en Unity.

### Prueba de la revisión 27 en Unity (todos los locales)

1. Volver a Unity, esperar la importación y pulsar **Alarma > Crear y probar juego**. Reconstruye la ciudad.
2. La Console debe mostrar «Personal de locales: 22 cajeros y 76 empleados más». Son 4 minimarkets × 1, 4 supermercados × 5, 3 joyerías × 3, 3 bancos × 7, 6 locales de comida × 3 y 2 tiendas de ropa × 2.
3. Con M, recorrer un local de cada tipo: personal con uniforme en su puesto y clientes eligiendo, haciendo fila y pagando.
4. Con el Profiler, medir dentro del supermercado y del minimarket, que tienen más triángulos.

### Verificación de la revisión 27

Blender 4.5.10 generó los tres locales sin errores y las capturas se revisaron. La cuadrícula caminable quedó completa: minimarket 1282 celdas, comida 1122 y ropa 1359. Los seis locales tienen todos los puntos de la rutina dentro y conectados. Banco, joyería y supermercado siguen idénticos en el JSON. Alarma.City.Editor compiló contra Unity 6000.3.27f2. No se ejecutaron la reconstrucción, Play ni el Profiler.

### Aprobación visual — 2026-11-05

Alain aprobó las capturas de Blender de los seis locales: banco (revisión 24), joyería (25), supermercado (26) y minimarket, comida y ropa (27). La aprobación corresponde al diseño. Siguen pendientes la reconstrucción en Unity, la prueba en Play de las revisiones 23 a 27 (clientes, viaje con M y personal) y la medición con el Profiler. B1 y su commit esperan esa confirmación.


## Revisión 28: venta realista, personal trabajando y clientes que deciden

Alain pidió:

- Animaciones de venta realistas en cada lugar. El cliente lleva el producto al trabajador y lo deja en la mesa; el trabajador cobra y devuelve el vuelto.
- Agarre correcto de los objetos con la mano.
- Clientes más frecuentes y en mayor número, que entren, revisen productos y a veces se vayan sin comprar.

**Punto de partida.** Los civiles solo traen seis clips (Idle, Walk, Run, Browse, Pay, CarryWalk) y un brazo derecho con IK hasta el marcador `Grip_R6` de la palma. El cajero solo estiraba el brazo hacia la caja. El producto «en el mostrador» quedaba a los pies del cliente. Sin clips nuevos de Mixamo, la venta se arma con esos clips más alcance procedural, con cliente y cajero sincronizados por un mismo guion.

**Guion del mostrador** (`Domain/CounterChoreography.cs`, sin Unity y con pruebas). Para cada estado y segundo indica a qué apunta la mano del cliente y la del cajero, y dónde está cada objeto.

- **Compra:**
  1. El cliente toma el producto del estante.
  2. Lo deja sobre el mostrador.
  3. El cajero lo toma, lo pasa por el escáner y lo deja del lado del cliente.
  4. El cliente saca los billetes del bolsillo y se los da en la mano.
  5. El cajero los guarda en la caja, saca el vuelto y lo entrega en la mano.
  6. El cliente guarda el vuelto y se lleva la compra.
- **Banco:**
  1. El cliente saca número en la máquina de turnos y lo pasa por la bandeja.
  2. El cajero lo toma y registra el retiro en su terminal.
  3. El cajero cuenta el efectivo y lo deja en la bandeja.
  4. El cliente lo toma y lo guarda.
- **Tiempos** (`CounterTiming`): tomar 1,2 s, dejar 1,4 s, escanear 2,4 s, pagar 3,0 s, vuelto 1,2 s, llevar 1,2 s.

**En la escena:**

- `CounterExchange` (nuevo) calcula sobre el mostrador dónde se deja el producto, dónde queda la compra y dónde se pasa el dinero. Mueve el brazo del cajero, que da medio paso hacia el mostrador al tomar o entregar.
- El cliente también se acerca hasta 32 cm desde su lugar y mira la caja.
- `ShoppingPresentation` pone cada objeto donde dice el guion (estante, mano, mostrador o mano del cajero). Si el cliente no compra, el producto queda en su estante.
- El gesto de pagar solo aparece al entregar y recibir dinero.

**Personal trabajando** (`StaffWork`, nuevo). Entre clientes cada empleado lleva la mano a sus puntos de trabajo según su rol:

- Cajeros, recepción, asesores y gerente teclean.
- Cocineros, carnicero y panadera trabajan en la plancha o la vitrina con el gesto de manipular.
- El reponedor acomoda estantes a distintas alturas.
- Vendedores, mesero y probadores atienden con gestos más espaciados.

Los sentados mueven las manos sobre el escritorio. El cajero pausa su trabajo mientras atiende.

**Clientes que deciden** (`PedestrianRoutine`):

- Antes de su puesto miran hasta dos puestos ajenos. Si uno está ocupado más de 6 s, pasan al siguiente.
- El 75 % compra y el resto se va sin comprar (`PedestrianSettings.BuyChance` y `MaxLooks`).
- En el banco también pasan primero por la máquina de turnos o los folletos.

**Más gente y más seguido:**

- Cada local cercano mantiene hasta 5 clientes, nunca más que sus puestos.
- Nuevos clientes cada 2–5 s, en locales a menos de 100 m.
- Los paseantes reconsideran visitar cada 2–5 s, con una búsqueda de 55 m.
- Las llegadas se separan 2,5 s y el cupo de peatones pasa de 45 a 55.

### Archivos de la revisión 28

- Nuevos:
  - `Scripts/AI/CityLifeR5/Domain/CounterChoreography.cs`
  - `Scripts/AI/CityLifeR5/CounterExchange.cs`
  - `Scripts/AI/CityLifeR5/StaffWork.cs`
- Modificados en `Scripts/AI/CityLifeR5/`:
  - `Domain/PedestrianRoutine.cs`
  - `ShopActivity.cs`
  - `ShoppingPresentation.cs`
  - `PedestrianActor.cs`
  - `CashierPresentation.cs`
  - `PedestrianPresentation.cs`
  - `PedestrianSettings.cs` (`PaySeconds` reemplazado por `BuyChance` y `MaxLooks`)
- Modificados en `Scripts/AI/Street/`: `SidewalkPopulation.cs`, `SidewalkVisit.cs` y `SidewalkWalker.cs`.
- Editor:
  - `City25Staff.cs`: rutinas de trabajo por rol.
  - `City25Shops.cs`: trabajo del cajero.
  - `City25Builder.cs`: constructor `ciudad25-28`.
- Pruebas en `Art/BlenderScripts/HideoutB1Fix~/SidewalkTests~/`:
  - Nuevo `CounterTests.cs`.
  - Actualizados `VisitTests.cs`, `PopulationTests.cs`, `StreetTests.cs` y `run_tests.py`.
  - Resultados en `runtime-results.txt`.

### Prueba de la revisión 28 en Unity

1. Volver a Unity y esperar la compilación. Console sin errores rojos.
2. Pulsar **Alarma > Crear y probar juego**. Reconstruye la ciudad (constructor `ciudad25-28`).
3. Con M, viajar al supermercado y mirar la caja 1 de cerca. El cliente deja el producto en la cinta. La cajera lo toma, lo pasa por el escáner y lo deja al otro lado. El cliente saca billetes y se los da. La cajera los guarda y devuelve el vuelto. El cliente lo guarda y se lleva la compra.
4. En el banco: el cliente toma número en la máquina, lo pasa por la bandeja, el cajero teclea, deja el efectivo en la bandeja y el cliente lo guarda.
5. Mirar al personal entre clientes: cajeros tecleando, cocineros en la plancha, reponedor en los estantes, asesores sentados con las manos en el escritorio.
6. Contar clientes: varios entrando, mirando más de un producto. Algunos se van sin comprar.
7. Si una mano atraviesa el mostrador, un objeto queda flotando o alguien se queda quieto en la fila, enviar captura con el nombre del local y del NPC.

### Verificación de la revisión 28

Pasaron 61 pruebas: las 50 anteriores, actualizadas a los nuevos tiempos y capacidades, y 11 nuevas. Las nuevas cubren el recorrido del producto, el dinero de mano en mano, el vuelto, las manos juntas al pagar, el cajero solo con el cliente del mostrador, número y efectivo por la bandeja del banco, mirar dos puestos ajenos, la duración del pago, irse sin comprar y no superar los puestos del local. Alarma.CityLife, Alarma.AI, Alarma.CityLife.Editor, Alarma.Playtest y Alarma.City.Editor compilaron con C# 9 contra Unity 6000.3.27f2. No se ejecutaron la reconstrucción ni Play: la orientación del objeto en la palma y el alcance real del brazo se ven en Unity.

**Límite.** El agarre es de una mano (derecha) con IK y el resto del cuerpo usa los seis clips existentes. Para movimientos más finos se pueden agregar clips de Mixamo (tomar un objeto, teclear, cocinar, entregar). Alain los descarga en el navegador; según CLAUDE.md, los FBX crudos de Mixamo no se suben al repositorio público.


## Revisión 29: puertas que abren, locales en marcha al llegar y bolsa en la mano

Alain probó la revisión 28 y envió dos capturas (COMIDA y SUPERMERCADO) con tres problemas:

- No podía abrir la puerta de ningún local. La animación de empujar se veía, pero la hoja no giraba, y los clientes quedaban esperando afuera.
- Al llegar con M todavía no había gente comprando.
- Un cliente quieto con su compra llevaba la bolsa en la espalda.

**Causas.**

1. `ShopDoor` solo deja girar la hoja si su recorrido no toca ningún collider, y eso incluía a las personas. Con más clientes había gente esperando a ambos lados de la puerta y nadie podía abrir: un bloqueo mutuo.
2. Las alfombras nuevas de entrada recibieron un collider a 13 cm de altura, justo donde pasa el borde inferior de la hoja.
3. El revestimiento de los pilares de banco, joyería, supermercado y ropa quedó pegado a la bisagra y trababa la apertura hacia afuera.
4. Al llegar con M, la población solo ponía un cliente en la puerta y otro caminando.
5. La bolsa cuelga del agarre de la mano, pero el clip `Idle` la anima hacia otra posición cuando el cliente se queda quieto.

**Correcciones.**

- `ShopDoor`: la hoja solo se detiene ante estructura y muebles; las personas ya no la frenan. Sigue quedando abierta mientras alguien pasa.
- `City25Kit`: alfombras sin collider (Runner, LoungeRug, CubicleRug, Rug, VipCarpet, BankStripe).
- `build_shops.py`: el revestimiento junto a la puerta empieza a 15 cm de la bisagra. Se regeneraron los seis locales y sus planos quedaron idénticos.
- **Locales en marcha:** al llegar con M, cada local cercano arranca con clientes ya comprando dentro (capacidad − 2, hasta 3), uno entrando por la puerta y otro en camino. Los de adentro empiezan en su puesto mirando productos y siguen la visita completa: eligen, hacen fila, pagan y salen.
  - Nuevos `PedestrianRoutine.BeginInside`, `ResumeInside` y `PedestrianActor.BeginInside`.
  - `SidewalkWalker` recibe `VisitStart` (Sidewalk, Door o Inside).
- `PedestrianPresentation`: guarda el giro de la bolsa en reposo y la vuelve a poner en la mano después del Animator.
- Constructor `ciudad25-29`.

### Archivos de la revisión 29

- `Scripts/AI/CityLifeR5/`: `ShopDoor.cs`, `Domain/PedestrianRoutine.cs`, `PedestrianActor.cs` y `PedestrianPresentation.cs`.
- `Scripts/AI/Street/`: `SidewalkWalker.cs` y `SidewalkPopulation.cs`.
- `Scripts/City/Editor/City25/`: `City25Kit.cs` y `City25Builder.cs`.
- `Art/BlenderScripts/build_shops.py`.
- Regenerados: `Art/City/Shops/Local_*.fbx`, `BlenderSources~/Alarma_Shops_*.blend` y capturas de `Previews~`.
- Pruebas en `SidewalkTests~`: `VisitTests.cs`, `PopulationTests.cs`, `CounterTests.cs` y `runtime-results.txt`.

### Prueba de la revisión 29 en Unity

1. Volver a Unity, esperar la importación y pulsar **Alarma > Crear y probar juego**. Reconstruye la ciudad.
2. Ir a cualquier local y abrir la puerta con E desde afuera y desde adentro, con y sin clientes cerca. Debe abrir siempre. Probar también la guarida.
3. Viajar con M al supermercado, al banco y a un local de comida. Desde el primer segundo debe haber clientes dentro mirando o comprando, uno entrando y otro llegando. Los clientes no deben quedarse esperando afuera.
4. Mirar a un cliente quieto con su compra: la bolsa va en la mano, no en la espalda.

### Verificación de la revisión 29

Pasaron 63 pruebas. Las nuevas cubren:

- Al llegar hay un cliente comprando dentro, otro en la puerta y otro en camino.
- Quien empieza adentro completa la compra.
- No se crea un cliente dentro si el local está lleno.

Los cinco ensamblados compilaron contra Unity 6000.3.27f2. El giro de la puerta usa la física de Unity, así que su prueba es la de Play.

## Revisión 30 de accesos comerciales

El borde superior de las hojas comerciales podía tocar el dintel desde el primer grado. El constructor baja el marco móvil 4,5 cm antes de ajustar su collider. Las entradas comerciales ahora abren por proximidad desde ambos lados y se mantienen abiertas mientras el paso está ocupado. El gesto de la guarida sigue a cargo de su controlador de interacción.

Los clientes pueden caminar hacia un local sin detenerse para acertar con la mano. Si uno permanece bloqueado en el exterior del umbral durante ocho segundos, libera su reserva y pide una ruta de regreso a la acera. La espera por un puesto lleno se limita a seis segundos en las visitas de calle.

Archivos de juego modificados en `Scripts/AI/CityLifeR5/` — `ShopDoor.cs`, `PedestrianActor.cs`, `Domain/PedestrianRoutine.cs`. Interacción en `Scripts/City/PlaytestR7/ReviewDoorInteraction.cs`. Constructor en `Scripts/City/Editor/City25/City25Kit.cs` y `City25Builder.cs`. Pruebas y evidencias actualizadas en `Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~` y `SidewalkTests~`.

1. Salir de Play y pulsar **Alarma > Crear y probar juego**. Esperar que la revisión 30 regenere los prefabs.
2. Usar **M** para ir al supermercado. Acercarse desde fuera y atravesar la puerta. Repetir desde dentro y comprobar el cierre al despejar el umbral.
3. Observar clientes desde la acera. Comprobar que entren cuando el paso esté libre y que cedan si se bloquea. Repetir en joyería o banco.

Compilaron tres asambleas contra las DLL instaladas de Unity. Pasaron 119 comprobaciones automatizadas de puertas, tráfico y rutinas. Se comprobó la geometría reimportada de las doce hojas comerciales a lo largo de ambos arcos. Falta probar el conjunto en Play.

## Revisión 31 de guardado y limpieza

Alain reportó que Unity ofrecía recargar la escena al usar **Crear y probar juego**. El registro muestra dos importaciones de la escena mientras ya tenía asignada su ruta abierta. Ahora el constructor guarda una copia, la importa antes de abrirla y comprueba que la escena que carga desde disco tenga cámara. Solo entonces actualiza el informe y entra en Play. Se retiró la actualización global al final de ese recorrido.

Con el editor cerrado, se retiró de `Assets` la revisión generada `R_8958378ef3f545dda339aab7b4f8a423`. El rastreo de 359 GUID y rutas encontró cero referencias desde los archivos conservados. La escena publicada pasó la comprobación de GUID sin faltantes. Los 710 archivos, incluidos los metadatos, se cotejaron por SHA-256 antes y después de moverlos a `Library/Alarma/City25Recovery/Retirada_R_8958378ef3f545dda339aab7b4f8a423`. La escena base sigue siendo el respaldo del constructor.

Archivos de código modificados en `Scripts/City/Editor/City25/` — `City25Builder.cs` y `City25BuildRecovery.cs`. Pruebas y evidencias en `Art/BlenderScripts/HideoutB1Fix~/BuildRecoveryTests~/`. Compilaron dos asambleas y pasaron 17 pruebas, entre ellas la importación antes de abrir y el regreso a la ciudad anterior si la copia falla.

1. Abrir Unity y esperar la importación. Pulsar **Alarma > Crear y probar juego** para generar la revisión 31.
2. Confirmar que Play inicia en la guarida sin la ventana **Reload / Ignore**.
3. Detener Play y volver a pulsar el menú. Confirmar que la escena se reutiliza y que la consola queda sin errores de referencias. Después probar los accesos comerciales.

## Revisión 32 del gesto de abrir en los negocios

Las puertas comerciales esperan que el jugador o el cliente se acerque y empuje. La animación alinea el cuerpo y lleva la palma hacia la manija. La hoja empieza a girar al confirmar el contacto. El jugador recupera el control cuando el paso tiene espacio suficiente. Los NPC usan su cuadrícula para llegar, un paso corto para ajustar el alcance y luego retoman su ruta. Al salir por el lado contrario, la hoja se mantiene abierta mientras el umbral esté ocupado y cierra al quedar libre.

Los NPC que quedan bloqueados fuera conservan el retorno a la acera de la revisión 30. El cierre conserva el barrido contra obstáculos. Se mantienen la holgura del dintel y la importación de la copia antes de abrir.

Archivos de juego en `Scripts/AI/CityLifeR5/` — `ShopDoor.cs` y `PedestrianActor.cs`. Interacción en `Scripts/City/PlaytestR7/ReviewDoorInteraction.cs`. Preparación en `Scripts/City/Editor/City25/City25Builder.cs` y `City25Kit.cs`. Regresiones en `Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/`.

1. Salir de Play y pulsar **Alarma > Crear y probar juego** para preparar la revisión 32.
2. En el supermercado, acercarse con **W** o pulsar **E** cerca de la manija. Observar el contacto, cruzar y mirar el cierre. Detenerse en el umbral para comprobar que permanezca abierto.
3. Repetir desde dentro. Seguir a un cliente de calle en un negocio y comprobar que empuje, cruce y continúe su visita.

La compilación y las regresiones se ejecutan fuera de Play. La alineación visual de cada personaje y el paso por los colliders deben confirmarse en Unity.

## Revisión 33 de traspasos y marcos comerciales

Los objetos conservan su posición y giro al empezar cada traspaso. Se acercan al nuevo apoyo de forma gradual y se fijan después de resolver la pose de la mano. El punto de apoyo usa la base visible del objeto para colocarlo en la palma o sobre el mostrador. La mano del cajero recorre tres puntos continuos, desde donde toma el producto, por encima del lector y hasta la zona donde lo recoge el cliente.

Se rediseñaron los accesos de supermercado, minimarket, joyería, banco, comida y ropa en Blender. Cada hoja queda dentro del vano y tiene marco completo, bisagras y placas con tiradores en ambas caras. El empuje conserva el contacto inicial durante más tiempo cuando la mano todavía alcanza la placa. Se comprobaron 24 arcos de 85 grados en los FBX reimportados. La comparación de mallas y materiales conservó los interiores y el resto de la fachada.

Archivos de juego en `Scripts/AI/CityLifeR5/` — `ShoppingPresentation.cs`, `CounterExchange.cs`, `PedestrianReach.cs` y `Domain/CounterChoreography.cs`. Interacción en `Scripts/City/PlaytestR7/ReviewDoorInteraction.cs`. Constructor en `Scripts/City/Editor/City25/City25Builder.cs`. Arte en seis `Art/City/Shops/Local_*.fbx`, `Art/BlenderSources~/Alarma_Shops_Puertas33.blend` y `Art/BlenderScripts/build_shops.py`. Receta de sustitución y capturas en `Art/BlenderScripts/HideoutB1Fix~/ShopPolish33~`. Pruebas actualizadas en `SidewalkTests~` y `DoorContactTests~`.

1. Abrir Unity, esperar la importación y pulsar **Alarma > Crear y probar juego** para preparar la revisión 33.
2. Ir al supermercado con **M**. Seguir una compra desde el estante y observar el apoyo en la palma, la llegada al mostrador, el recorrido por el lector y la recogida.
3. Probar la entrada con **W** o **E** desde ambos lados. Observar el empuje y el cierre. Repetir con un NPC y comprobar el encaje de las hojas al quedar cerradas.

Compilaron tres asambleas y pasaron 67 pruebas de calle y caja. Los seis FBX conservan sus metadatos. La animación y las colisiones quedan pendientes de confirmación en Play.
