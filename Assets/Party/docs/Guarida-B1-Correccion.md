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
