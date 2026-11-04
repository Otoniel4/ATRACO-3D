# AGENTS.md — Proyecto "Alarma" (Unity 6, multijugador online)

## Rol
Actúa como un **ingeniero desarrollador de videojuegos en Unity con nivel de magíster**, especializado en:
- Patrones de diseño (State, Observer/Eventos, Command, Strategy, Factory, Object Pool; Service Locator solo si se justifica).
- Principios **SOLID** en todo el código, sin excepción.
- Programación en red con **Netcode for GameObjects**, Unity Relay, Lobby, Authentication y Cloud Save.

El usuario (Alain) es estudiante y **está aprendiendo**. Tu trabajo es construir el juego con él, no por él.

## Documentos de referencia
- `Assets/Party/docs/GDD.pdf`: diseño completo del juego. Es la fuente de verdad del diseño.
- `TASKS.md`: lista de tareas del proyecto. Es la fuente de verdad del orden de trabajo. Donde dice "El agente hace", eres tú.

## Datos del proyecto
- Unity 6000.3.27f2, plantilla Universal 3D (URP). Versión confirmada por Alain; no migrar sin instrucción expresa.
- Paquetes verificados: URP, Input System, AI Navigation, Timeline, Netcode for GameObjects, Multiplayer Services, Multiplayer Play Mode, Cinemachine, ProBuilder, Cloud Save y Authentication. Versiones resueltas en `Packages/packages-lock.json`.
- **Todo el contenido del juego se crea dentro de la carpeta `Party/`** que indique el usuario. Si no está claro dónde está, pregunta antes de crear cualquier archivo. No crees archivos del juego fuera de ella.
- No puedes abrir el editor de Unity ni jugar el juego: todo lo que requiera el editor se entrega como pasos para Alain.

## Protocolo de tareas (OBLIGATORIO)
1. Trabaja **una sola task a la vez**, en el orden de `TASKS.md`. Nunca empieces la siguiente por tu cuenta, aunque la actual parezca terminada.
2. Al empezar una task: lee su objetivo y criterios, y resume en 3–5 líneas qué vas a hacer antes de editar archivos.
3. Al terminar una task, entrega siempre:
   - Lista de archivos creados o modificados.
   - **Pasos para el editor**: lo que Alain debe hacer a mano en Unity (escenas, prefabs, componentes, configuraciones), numerados.
   - **Cómo probarlo**: pasos exactos, incluyendo Multiplayer Play Mode cuando haya red.
   - **Explicación para aprender** (ver abajo).
4. Luego **detente y espera** a que Alain confirme que lo probó y funciona. Solo con su confirmación marcas la task como `[x]` en `TASKS.md` y haces el commit.
5. Si una prueba falla, se corrige dentro de la misma task. No se avanza con errores.
6. Si algo de una task no es posible o choca con el GDD, dilo con claridad y propone la alternativa real. No inventes soluciones ni APIs; si no estás seguro de una API de Unity o de Netcode, revisa la documentación del paquete instalado (carpeta `Library/PackageCache`) antes de usarla.

## Skills y herramientas (OBLIGATORIO)
- **Caveman** (skill): úsalo en todas las respuestas de trabajo (planes, listas de archivos, pasos). Sin saludos ni relleno.
- **Excepción**: la sección **"Explicación para aprender"** de cada task se escribe en español normal y claro, máximo 10 líneas: qué hace cada pieza, qué patrón se usó y por qué, y qué principio SOLID se aplicó.
- **RTK**: ejecuta los comandos de terminal a través de RTK (`rtk git status`, `rtk git diff`, lecturas y búsquedas) siguiendo las instrucciones de `RTK.md`. Al iniciar la Task 00 verifica que esté instalado con `rtk gain`.
- Si Caveman o RTK no están instalados, **detente** y dile a Alain cómo instalarlos; no continúes sin ellos.

## Reglas de código
- C# con namespaces por módulo: `Alarma.Core`, `Alarma.Player`, `Alarma.Networking`, `Alarma.AI`, `Alarma.Heist`, `Alarma.Police`, `Alarma.Economy`, `Alarma.UI`, `Alarma.Animation`, `Alarma.City`, `Alarma.Traffic`, `Alarma.Vehicles`, `Alarma.Audio`.
- SOLID:
  - **S**: una clase, una responsabilidad. Nada de "GameManager" que haga todo.
  - **O**: nuevos ítems, armas o estados se agregan con clases o ScriptableObjects nuevos, sin modificar las existentes.
  - **L**: las subclases deben poder reemplazar a su base sin romper nada.
  - **I**: interfaces pequeñas (`IInteractable`, `IDamageable`, `IDetectable`, `IArrestable`, `IIntimidatable`).
  - **D**: depende de interfaces y eventos, no de clases concretas. Evita `FindObjectOfType` y singletons innecesarios.
- Datos configurables en **ScriptableObjects** (armas, herramientas, locales, precios, tiempos).
- Comunicación entre sistemas con **eventos**, no con referencias directas cruzadas.
- **Red**: toda decisión que afecte a todos la toma el host (servidor). Los clientes piden acciones con RPC; el host valida y aplica. El movimiento del jugador usa autoridad del dueño. Los NPC, la alerta, el nivel de búsqueda y el dinero los controla solo el host.
- Comentarios en español, breves, solo donde aporten. Nombres de clases y métodos en inglés.
- Nada de código muerto ni de "TODO" sin explicar.

## Arte, modelos y animaciones
- **Prohibido usar modelos o texturas ya hechos descargados de internet.** Todos los modelos se crean con IA controlando Blender por MCP (aceptado por el ingeniero). Excepción para personajes desde 2026-11-03: ver «Personajes de páginas gratuitas».
- **Permitido:** Mixamo para el auto-rig de los modelos propios y para las animaciones; sonidos descargados de sitios con licencia clara. Todo se registra en `docs/LICENSES.md`.
- Mixamo no tiene API: la subida y descarga las hace Alain en el navegador. Tú preparas los FBX para subir y la lista exacta de animaciones a descargar.
- Si el servidor MCP de Blender tiene integraciones que descargan assets (bibliotecas de modelos o texturas), no las uses.
- Estilo low-poly con colores planos, sin texturas pintadas. Escala: 1 unidad = 1 metro.
- Después de crear o modificar un modelo, toma una captura del viewport y revísala antes de darlo por terminado; entrega las capturas a Alain para que apruebe.
- Personajes: dos cuerpos base (hombre y mujer) rigeados con Mixamo e importados como Humanoid; las piezas de ropa y uniformes se asignan al mismo esqueleto con transferencia de pesos. La variedad sale de piezas intercambiables y colores, no de modelos duplicados.
- Las animaciones se comparten entre todos los personajes mediante el retargeting Humanoid de Unity.
- Uniformes distintos: guardias (con porra, sin pistola) y policías (con pistola). Solo la policía usa armas de fuego entre los NPC.
- Exporta a FBX con un script reutilizable; ruedas y puertas de los autos como objetos separados.
- Guarda los scripts bpy en `Party/Art/BlenderScripts/` para poder regenerar o ajustar cualquier modelo.
- Animator Controllers con Blend Trees y capas; el código solo cambia parámetros del Animator desde un componente dedicado. Sincronización con NetworkAnimator.
- Los locales robables deben verse completos y decorados, nunca vacíos.

## Rendimiento
- NPC, peatones y autos lejanos a todos los jugadores se desactivan o no se sincronizan.
- Peatones, autos y policías usan Object Pool.
- Mide con el Profiler antes de optimizar; no optimices a ciegas.

## Git
- Un commit por task terminada y confirmada: `task-XX: descripción corta`.
- Verifica que exista un `.gitignore` de Unity (Library, Temp, Logs, UserSettings, Obj, Build).


## Estado verificado de Task 00 — 2026-10-31

Esta sección actualiza únicamente los datos del entorno descritos arriba.
- Proyecto: `C:\Users\Alain\Atraco3D`.
- Carpeta de contenido confirmada por Alain: `C:\Users\Alain\Atraco3D\Assets\Party`.
- Unity confirmado por Alain: `6000.3.27f2`, según `ProjectSettings/ProjectVersion.txt`. Mantener esta versión.
- Instalados: URP `17.3.0`, Input System `1.20.1`, AI Navigation `2.0.16` y Timeline `1.8.13`.
- Instalación verificada: Netcode for GameObjects `2.13.3`, Multiplayer Services `2.4.1`, Multiplayer Play Mode `2.0.2`, Cinemachine `3.1.7`, ProBuilder `6.1.4`, Cloud Save `3.4.2` y Authentication `3.8.0`. Alain confirmó que Console no muestra errores y los servicios están configurados. La prueba funcional online corresponde a Task 02, después del arte según el orden vigente de TASKS.md.
- Multiplayer Center está instalado; no sustituye los paquetes anteriores.
- RTK funciona por invocación explícita. La ausencia de un hook automático no impide usar `rtk`; consultar `RTK.md`.
- GDD recibido y revisado: `Assets/Party/docs/GDD.pdf` (18 páginas). Diferencias y cobertura registradas en `Assets/Party/docs/GDD-REVISION.md`. El PDF original se conserva íntegro.
- Task 00 completada: paquetes verificados y prueba del entorno confirmada por Alain el 2026-10-31. Commit de cierre: `1c3dbdc`. Task 01 validada por Alain: captura con 9 pruebas correctas y autorización para continuar con Blender. Commit de cierre de Task 01: `afa86c4`.
- Informe y pasos: `Assets/Party/docs/TASK-00-Entorno.md`.

## Prioridad confirmada por Alain — 2026-10-31

Después de Task 01: conectar Blender y crear mapa, personajes, accesorios, vehículos, armas y herramientas. Después del arte aprobado: clips, prototipo de red y dinámicas. Seguir la sección de orden vigente de TASKS.md; Task 02 ya no precede al arte. Mantener Unity 6000.3.27f2.

## Producción de arte autorizada

Alain pidió continuar con Blender para realizar todos los diseños requeridos. Progresar por los hitos de conexión, estilo y lotes de modelos, conservando capturas y scripts. La aprobación visual de Alain sigue pendiente para cada entrega; no marcar diseños como aprobados ni simular el rig de Mixamo sin los archivos necesarios.

## Revisión de personajes con referencias — 2026-10-31

Alain rechazó la simplicidad del primer lote y aportó 14 láminas: diez civiles, dos guardias y dos policías. Se creó una revisión separada en `Assets/Party/Art/Characters/ReferenceV2` y `BlenderSources~/Alarma_Characters_ReferenceV2.blend`. La geometría y las capturas están disponibles para corrección y aprobación; aún no igualan todos los detalles de las láminas. Los rig de Mixamo, pesos, Humanoid y clips siguen pendientes. No cerrar Tasks 03.2, 03.3 ni 03.4 hasta cumplir sus pruebas. Mantener Unity 6000.3.27f2 y el resto del arte existente.

## Rechazo explícito de V2 — 2026-10-31

Alain rechazó V2 por falta de similitud y cuerpo deforme. No usarla ni continuar su rig o variantes. Rehacer primero el civil masculino de chaqueta naranja con referencias frontal, lateral y posterior calibradas. No declarar corregido el personaje por tener geometría cerrada o exportar sin errores. Las tareas de personajes y animación permanecen abiertas.

## Foco actualizado: estructura femenina — 2026-10-31

Alain volvió a señalar anatomía deforme y adjuntó la referencia 02 (mujer con chaqueta denim). Priorizar esta mujer y la estructura corporal sobre el rostro. Se creó `FemaleBody_AnatomyStudy`: una única base continua y un rig diagnóstico de 29 huesos para ensayar articulaciones. Es un estudio pendiente de revisión y refinamiento, no el personaje acabado ni el rig Mixamo final. La V2 sigue rechazada. No generar variantes hasta resolver esta base.

## Ajuste de ambas bases autorizado — 2026-10-31

Alain confirmó que la estructura continua femenina va bien y autorizó ajustar cintura y demás proporciones, y crear después una base masculina esbelta. Se conservaron dos copias nuevas en `BodyBases_Refined.blend`, con rigs diagnósticos independientes y pruebas de flexión. La aprobación anterior corresponde a la dirección de la estructura, no al personaje terminado ni a Humanoid. La V2 sigue rechazada; ropa y rig final pendientes.


## Blockout Blender 4.x solicitado explícitamente — 2026-10-31

Alain pidió un script autónomo headless para una mujer de 1,65 m, unas 6,5 cabezas, superficies mayormente en quads, siete piezas separadas y rig automático bpy. Esta solicitud específica sustituye el uso obligatorio de Mixamo y MCP para esta entrega de estudio. Script, referencias, .blend, FBX e informes en Assets/Party/Art/BlenderScripts/CharacterBlockout4~; render y reimportación verificados con Blender 4.5.15 portable. Sigue pendiente la revisión visual de Alain y el Avatar Humanoid dentro de Unity; no cerrar tareas de personajes ni animación por estas comprobaciones. Tras revisar la guía PDF adicional, Alain confirmó mantener 1,65 m y 6,5 cabezas, sin cambiar al estilo chunky. Mantener Unity 6000.3.27f2.


## Corrección de proporciones R1 — 2026-10-31

Alain autorizó corregir cabeza, cuello, hombros y tiro del blockout femenino de 1,65 m. La revisión independiente está en Assets/Party/Art/BlenderScripts/CharacterProportionsR1~; se conserva CharacterBlockout4~. Incluye jaula continua de cabeza/cuello en quads, cintura y tiro elevados, rig recalculado y FBX reimportado con prueba básica de flexión. Captura del viewport revisada en Blender conectado. La escena de revisión en el Blender abierto es Female_Proportions_R1. Sigue pendiente la aprobación visual de Alain; no cerrar tareas de personajes ni comenzar animaciones finales.


## Ajuste de mandíbula R2 — 2026-11-01

Alain pidió revisar y arreglar la mandíbula. Revisión independiente en Assets/Party/Art/BlenderScripts/CharacterJawR2~ y escena de revisión Female_Jaw_R2 en Blender conectado. Se conserva R1. Ajuste de mentón y transición cuello/mandíbula; verificación local de coordenadas, quads cerrados, altura, pesos y reimportación del FBX superada en Blender 4.5.15. Captura de viewport revisada. Esperar aprobación visual; no marcar tareas de personajes ni animaciones como completadas.


## Cambio explícito a cabeza low poly — 2026-11-01

Alain rechazó la cabeza anterior y pidió rehacerla directamente como low poly, sin buscar aspecto tan humano. Nueva escena Female_LowPoly; fuente y archivo independiente en Assets/Party/Art/BlenderScripts/CharacterLowPoly~. Se conservan el cuerpo y la ropa, y se añade una cabeza geométrica con ojos y sonrisa simples y pelo facetado. Esta dirección sustituye la búsqueda anatómica de R1/R2; las versiones previas no se consideran aprobadas. Verificación en Blender 4.5.15 y captura revisada en Blender conectado. Esperar aprobación visual antes de crear variantes o animaciones finales; mantener Unity 6000.3.27f2.

## Elenco low poly autorizado — 2026-11-01

Alain aprobó la dirección de la cabeza low poly y pidió crear los demás personajes divertidos. Se generaron 17 nuevos y se conservó la mujer aprobada: 10 civiles, 2 guardias, 2 policías y 4 roles del GDD (Ladrón, Hacker, Distractor, Músculo). Fuentes, FBX, capturas y pruebas en Assets/Party/Art/BlenderScripts/LowPolyCast~; documentación en Assets/Party/docs/LowPolyCast.md. Galería Cast_Gallery y escenas individuales cargadas en Blender conectado. Reimportación y pruebas básicas de pesos/poses de los 18 FBX superadas con Blender 4.5.15; captura del viewport revisada. Rigs propios de 21 huesos, no Mixamo. La aprobación de la cabeza previa no aprueba automáticamente el elenco nuevo. Quedan pendientes revisión visual del elenco, Avatar Humanoid en Unity, clips y sistema modular de prefabs. No cerrar Tasks 03.2, 03.3 ni 03.4 por estas pruebas. Mantener Unity 6000.3.27f2; versiones anteriores preservadas.

## Toñito con torso de gimnasio — 2026-11-01

Alain pidió corregir los brazos de Toñito y ensanchar el cuerpo desde la cintura hacia arriba. Revisión separada en Assets/Party/Art/BlenderScripts/TonitoGymR1~ y documento docs/Tonito-Gym-R1.md: torso en V, hombros más separados, brazos más proporcionados, camiseta y pesos ajustados. Escena Cast_Player04_Muscle_Gym_R1 cargada en Blender conectado; Cast_Gallery usa la nueva colección. FBX reimportado y pruebas de escala/pesos/flexión superadas; captura de viewport revisada. El .blend integrado conserva exactamente las mallas de los otros 17 actores; la versión anterior de Toñito sigue disponible. Esperar revisión visual del usuario. Avatar Humanoid y animaciones pendientes; no cerrar tareas ni hacer commit de cierre por esta corrección. Mantener Unity 6000.3.27f2.

## Auditoría de piernas y pesos R2 — 2026-11-01

Alain pidió revisar los esqueletos del elenco porque las piernas de Toñito parecían salirse. Las cadenas estaban conectadas, pero el pantalón de Toñito tenía unos 4,4 cm de desfase lateral respecto al eje de pierna en una sección medida. Revisión en Assets/Party/Art/BlenderScripts/RigLegsR2~: rodillas/pantorrillas/pies de Toñito, centrado de pantalones cortos de Toñito/Tito/Clara y pesos de pantalón/chaqueta/top de Lola corregidos. Auditoría semántica de pesos, jerarquía y simetría superada para 18; 18 FBX reimportados y 36 poses de diagnóstico renderizadas y revisadas. RigReview_Player04_Muscle abierta en Blender conectado con esqueleto visible; captura revisada. Documentación en docs/RigLegs-R2.md. La revisión visual del usuario, los Avatar Humanoid y los clips finales permanecen pendientes. No cerrar tareas ni hacer commit de cierre por esta auditoría. Mantener Unity 6000.3.27f2; no se abrió el editor ni se sustituyeron prefabs.

## Ajuste del resto del elenco R3 — 2026-11-01

Alain aprobó la dirección de la corrección R2 y pidió aplicar lo mismo al resto. Se ajustaron las piernas, rodillas, tobillos, pantalones y pesos de los otros 17 actores; Toñito R2 se conserva con huella de geometría/pesos/huesos comprobada. Fuente, 18 FBX, capturas y scripts en Assets/Party/Art/BlenderScripts/CastLegsR3~; documento docs/CastLegs-R3.md. Auditoría de 18 rigs, reimportación de los 18 FBX y 36 poses de diagnóstico superadas/revisadas, junto con frente/perfil/espalda. Galería LegsR3_Gallery y escenas individuales cargadas en Blender conectado; captura revisada. Revisión visual de este lote R3, Avatar Humanoid y clips finales pendientes. No cerrar tareas de personajes/animación ni hacer commit de cierre por estas pruebas. Mantener Unity 6000.3.27f2; no se abrió Unity ni se sustituyeron prefabs.


## Mapa low poly de 4 × 4 km — 2026-11-01

Alain pidió un mapa low poly divertido a juego con el elenco y aportó una imagen de ciudad con plaza circular, diagonales y río. Se adapta a 4.000 × 4.000 m reales (16 km²), aunque la referencia diga 6 × 6 km. Fuentes, 64 sectores, 55 piezas, FBX completo, capturas y scripts en Assets/Party/Art/BlenderScripts/Map4Km~; documentación en docs/Map4Km.md. Escenas Map4Km_* cargadas en Blender conectado y viewport revisado; apertura inicial tardó varios minutos, después respondió. Verificados límites, conectividad vial, 3.738 huellas sin invadir calzadas y reimportación del FBX completo más dos sectores con materiales por cara. Geometría propia y reutilización de nuestros interiores/coches; sin modelos ni texturas descargados. Diseño estático pendiente de aprobación visual, prueba en Unity, colisiones, NavMesh, rendimiento, LOD/streaming y dinámicas. No se abrió Unity ni se cambiaron escenas/prefabs. No cerrar Task 03.5 ni hacer commit de cierre por esta entrega; mantener Unity 6000.3.27f2 y personajes R3.


## Ciudad moderna R2 — 2026-11-01

Alain rechazó la sencillez del mapa V1 y pidió más diseño en árboles, casas, empresas y negocios, manteniendo low poly y 4 × 4 km. Confirmó completar primero el diseño, sin añadir todavía movimiento ambiental. Revisión independiente en Assets/Party/Art/BlenderScripts/Map4KmModernR2~; guía en docs/Map4Km-Modern-R2.md. Se sustituyen las piezas de los 3.738 edificios genéricos y se reconstruyen nueve locales con interiores, fachadas modernas, ventanas, techos y puertas separados; seis especies de árboles, jardines, pérgolas, mobiliario y equipamiento de parques. Se conservan V1 y el elenco R3. Comprobados 4.000 m por lado, 64 sectores y 3.748 envolventes sin invadir calzadas; FBX completo más dos sectores reimportados con colores por cara contrastados. Entrega de 153 piezas de kit y renders/captura de viewport. El conjunto ronda 29 millones de triángulos instanciados; rendimiento, LOD, streaming, colisiones, NavMesh y materiales URP quedan pendientes de medir/probar en Unity. No se abrió Unity ni se sustituyeron escenas o prefabs. Esperar aprobación visual y prueba de Alain; no cerrar Task 03.5 ni hacer commit de cierre. Mantener Unity 6000.3.27f2.

## Árboles con viento R3 — 2026-11-01

Alain pidió expresamente árboles menos básicos y hojas con movimiento natural. Esta petición autoriza el movimiento de vegetación y actualiza la indicación anterior de terminar primero el diseño; no autoriza todavía tráfico o peatones dinámicos. Revisión independiente en Assets/Party/Art/BlenderScripts/TreesWindR3~; guía en docs/Trees-Wind-R3.md. Seis especies propias con hojas individuales, ramas y viento Geometry Nodes; bucle de 8 segundos renderizado y captura de viewport revisados en Blender 4.5.15 aislado. MCP no respondió; la receta bpy headless mantiene el flujo de generación reproducible. La copia del mapa conserva 4.000 × 4.000 m y la geometría ajena a la vegetación; sustituye 10.745 árboles, deja 65 con viento activo cerca de las zonas de revisión y entrega todos con máscaras para viento en GPU. 18 FBX de especies, FBX completo, shader URP, 21 materiales y componente de límites preparados. Reimportación FBX y datos de viento verificados en Blender; shader/C# y ejecución en Unity pendientes. Los archivos de Unity permanecen dentro de la entrega ignorada hasta la prueba manual. No se abrió Unity ni se sustituyeron escenas o prefabs. Mantener Unity 6000.3.27f2, ciudad R2 y elenco R3; esperar revisión visual y prueba de Alain. No cerrar tasks ni hacer commit de cierre por esta entrega.

## Jardineras y pasto R4 — 2026-11-01

Alain señaló los arbustos básicos de las jardineras y pidió plantas similares al arbolado R3 y pasto más detallado. Revisión independiente en Assets/Party/Art/BlenderScripts/PlantersGrassR4~; guía en docs/Planters-Grass-R4.md. Se reemplazan 133628 volúmenes antiguos de follaje de macetas y sotobosque, procedentes de 99 mallas compartidas; ese número no representa macetas distintas. Se añaden 14000 parches de pasto comprobados sobre superficies de césped. Las caras ajenas al follaje de las mallas intervenidas y el arbolado R3 se conservan mediante comprobación de huellas. Incluye kit de macetas, variantes de arbustos, tres LOD, 19 FBX de kit, FBX completo, materiales que reutilizan el shader R3, demostración de ocho segundos y captura del viewport revisada. Solo las zonas de revisión evalúan viento en Blender; todas las plantas tienen máscaras para el shader de Unity. Blender 4.5.15 aislado se utilizó porque el transporte MCP sigue cerrado. Máscaras, bucle, puntos estáticos y reimportación FBX verificados en Blender; compilación y ejecución de Unity pendientes. No se abrió Unity ni se sustituyeron escenas/prefabs activos. Mantener Unity 6000.3.27f2, 4 × 4 km y elenco R3. Esperar revisión visual y prueba de Alain; no cerrar tasks ni hacer commit de cierre.

## Ciudad viva e interiores R5 — 2026-11-02

Alain aprobó visualmente la vegetación R4 y pidió más dinámica, NPC paseando/entrando a comprar y objetos más diseñados. Autoriza esta preparación de rutinas y clips propios ahora; la sincronización compartida continúa después de Task 02. Fuentes en Assets/Party/Art/BlenderScripts/CityLifeR5~ y guía docs/City-Life-R5.md. Se entregan 32 piezas detalladas, nueve interiores con 103 instancias nuevas, regiones de bóveda/celdas conservadas y un mapa de 4 × 4 km con 26 personajes de revisión. Diez civiles conservan mallas/pesos R3 y reciben cinco clips propios (Idle/Walk/Browse/Pay/CarryWalk), Generic de estudio, sin Mixamo ni Avatar Humanoid validado. Demo Blender de 24 segundos con paseos, cuatro compras, filas, bolsas y puertas. Es una revisión horneada, no captura de Unity. Runtime C# instalado en Scripts/AI/CityLifeR5; constructor en Scripts/City/Editor/CityLifeR5. Menú Alarma/Ciudad/Crear demo local R5 prepara tres negocios, NavMesh, controladores, diez variantes, pools, hasta 24 peatones y tres dependientes en una escena nueva. Los FBX completos del mapa se omiten de esa demo. Compilación de runtime/editor contra DLL instaladas superada; 20 comprobaciones de dominio, 44 FBX reimportados, dimensiones 4000 × 4000 y captura de viewport revisados. No se abrió Unity ni se ejecutó Play. No hay implementación de Relay/Lobby ni sincronización NPC: la demo es local. Compras ambientales sin modificar dinero de banda. Esperar prueba de Alain y revisión visual R5; no cerrar Tasks 02/03.4/03.7/04/12/26 ni hacer commit de cierre. Mantener Unity 6000.3.27f2.

## Corrección de circulación, manos y compras R6 — 2026-11-02

Alain detectó bloqueos entre NPC, manos insuficientes y pidió tareas de compra completas con dependientes y filas. R5 no queda aprobada por haber compilado. R6 conserva cuerpos/piernas R3 y añade 36 manos con dedos a 18 personajes, 51 huesos por rig, cinco clips propios por personaje y agarres de prototipo. Fuentes en Assets/Party/Art/BlenderScripts/CityLifeR6~; guía docs/City-Life-R6.md. Se actualizan las fuentes activas dentro de Scripts/AI/CityLifeR5 y Scripts/City/Editor/CityLifeR5 para evitar clases duplicadas; menú Alarma/Ciudad/Crear demo local R6. La escena nueva contiene mercado, joyería, restaurante, hasta 24 peatones y tres dependientes. Tráfico con reservas/herencia de prioridad, aforo por local, selección, producto en mano, fila FIFO, cinta, escaneo, saldo ambiental, cobro único, recibo, bolsa y limpieza al salir/volver al pool. Dominio C# probado durante 180 s: 12 compradores atendidos, 34 compras y ninguna rutina fallida; mínimo entre centros 0,49497 m. Pruebas enfrentadas y de puerta, FIFO, cancelación, sobreventa y duplicación de pago superadas. 18 FBX y 37 piezas reimportados; runtime/editor compilados contra las DLL instaladas. Captura nativa de viewport y vídeo Blender revisados. Contactos horneados con error máximo aproximado de 10,3 cm frente al punto ideal; pulido de agarres pendiente. Mapa de 4000 × 4000 con 27 actores de revisión en las tres zonas, una vitrina bloqueante retirada y tres expositores añadidos. Geometría/vegetación restante preservada por SHA-256 y FBX del mapa reimportado. Blender reproduce trazas horneadas; no es captura del juego. No se abrió Unity ni se ejecutó Play. Sigue siendo prototipo local, Generic, sin sincronización Netcode; integración del runtime en todo el mapa requiere sectores y medir rendimiento. Esperar prueba y revisión visual de Alain. No cerrar tasks ni hacer commit de cierre; mantener Unity 6000.3.27f2 y todas las revisiones anteriores.

## Prueba integrada con una sola entrada R7 — 2026-11-02

Alain pidió un único botón Alarma para reunir y probar todo lo preparado y comunicar cambios. Esta solicitud autoriza una escena local de revisión con control de personaje y cámara; no cierra las tareas de jugador/red del GDD. El intento R6 quedó incompleto por Puesto inaccesible o compartido Routine_Minimarket/Browse_0. Se corrige usando el grafo geométrico comprobado, sin el filtrado adicional de vóxeles. Entrada única Alarma/Crear y probar juego; las funciones anteriores se conservan sin entradas de menú. Fuentes nuevas en Scripts/City/PlaytestR7 y Scripts/City/Editor/PlaytestR7. El botón importa/prepara 263 partes del mapa 4000 × 4000, colisiones, viento, 17 hojas de nueve accesos, cuatro roles controlables, 18 modelos de personaje, catálogo de vehículos/equipos/props y rutinas de mercado/joyería/restaurante en sus coordenadas reales. Guarda una escena nueva completa y solicita entrar en Play únicamente cuando Alain pulsa el botón. Reutiliza la escena lista en posteriores pulsaciones y protege escenas previas con el diálogo de guardado de Unity. Ante fallo cierra su escena temporal y conserva las anteriores. Cinco asambleas compiladas contra DLL instaladas; dominio de compras/tráfico y 18 puestos comprobados, con desnivel máximo 0,17 m. Muestras de FBX, nombres, límites, máscaras y nueve puertas reimportados. El agente no abrió Unity ni ejecutó Play; quedan pendientes construcción efectiva de escena/prefabs, render, controles y rendimiento con la prueba de Alain. Es una prueba local del contenido existente: no declara implementados red, atracos, combate, conducción ni animaciones finales. Guía docs/Prueba-Completa-R7.md; arte y recetas en Art/BlenderScripts/PlaytestR7~. No marcar tareas ni crear commit de cierre hasta confirmación; mantener Unity 6000.3.27f2 y revisiones anteriores.


## Corrección de escenas sin guardar y recuperación de importación R7.2 — 2026-11-02

La prueba de Alain falló con Cannot create a new scene additively with an untitled scene unsaved. El diálogo anterior permitía continuar con una escena Untitled sin ruta; crear otra aditivamente no es válido. R7.2 sustituye ese diálogo por respaldos automáticos dentro de Assets/Party/Scenes/Backups/BeforePlaytest_<fecha>; asigna ruta a las escenas sin nombre y guarda copia de las escenas existentes con cambios, sin sobrescribir originales. Comprueba la precondición y crea la escena temporal antes de importar. Reutiliza arte preparado de los intentos fallidos por ese error y de sus puntos de control; los prefabs/datos/escena se crean en una carpeta nueva y pueden referenciar el arte anterior. No borrar las carpetas Generated anteriores. Se conservan sus .meta. Las cinco asambleas compilan contra las DLL instaladas; cinco casos de política de respaldo pasan. Dos lotes contienen los 295 FBX obligatorios y 406 materiales cada uno. La comprobación de disco no sustituye la prueba de carga de Unity. El agente no abrió Unity ni ejecutó Play. Alain debe cancelar el diálogo viejo, esperar compilación y volver a pulsar Alarma/Crear y probar juego. Guía actualizada en docs/Prueba-Completa-R7.md; fuentes y evidencias en Art/BlenderScripts/PlaytestR7~. No cerrar tareas ni hacer commit sin la prueba y confirmación de Alain.

## Rechazo de la prueba integrada y correcciones R8 — 2026-11-02

Alain rechazó la ejecución R7: caminar/correr, puertas y colisiones, población, mapa con traslado, árboles en pistas y bolsa lateral. R7 no queda aprobada. Se prepara R8 dentro de la misma corrección: seis clips propios y Blend Tree, bolsa del ladrón en espalda, cámara detrás, nueve puertas detalladas con colisión, comprobación de triángulos grandes y árboles importados frente al asfalto, reserva de pasos ante jugador/puertas, 4.153 recorridos de acera con pool y activación por carga de zona. Los grafos de las tres tiendas se contrastan con obstáculos y se ajustan; manos/agarres de NPC quedan serializados. M muestra plano y ubicación sin viajar. Fuentes activas conservan rutas/asambleas y GUID; receta/arte en Art/BlenderScripts/PlaytestR8~ y guía docs/Correcciones-Prueba-R8.md. Se conservan todas las carpetas Generated y R7 como fuente de ciudad. Dieciocho personajes y nueve puertas reimportados; cinco asambleas compiladas; pruebas de dominio y 180 s sobre los grafos corregidos pasan. Renders de Blender revisados; el transporte MCP está cerrado y se usa Blender portable aislado. No son capturas de Unity. El constructor comprobará el movimiento real de los clips importados y los prefabs antes de publicar; RuntimeReview.json registrará lo observado en Play. El agente no abrió Unity ni ejecutó Play. Falta la prueba y aprobación de Alain. No se cierran tasks ni se hace commit. Mantener 6000.3.27f2 y 4 × 4 km.

## Corrección de integración R9 — 2026-11-02

Alain rechazó R8 por puertas desalineadas, salida bloqueada e interiores/rutinas incompletas. Autorizó explícitamente reducir el mapa a 3 × 3 km; este tamaño sustituye los 4 × 4 km anteriores para la prueba vigente. Inicio dentro de El Escondite con cuatro puestos reservados para futuros compañeros, todavía sesión local. Se reconstruyen escondite y cinco tiendas en parcelas libres de la avenida diagonal; productos propios, estaciones reservadas, fila y caja. Todos los 153 FBX de ciudad se exportan de nuevo con tres anclas para corregir orientación/posición al importar; puertas y mercancía también. Carrera propia de apoyo/vuelo/codos en dieciocho modelos. Vegetación con viento conservada, macetas nuevas y accesos despejados. La fuente nueva está en Art/BlenderScripts/PlaytestR9~; se mantienen las rutas/asambleas de fuentes activas y las revisiones/Generated anteriores. Cinco asambleas compiladas; 191.739 comprobaciones de dominio y diez compras por cada tienda en 180 segundos sobre los cinco grafos; 18 personajes reimportados y límites de 3000 m verificados. Renders Blender revisados. El botón único Alarma/Crear y probar juego comprueba además anclas y colliders reales en Unity, salida del escondite, puertas abiertas/cerradas y compras antes de publicar la escena lista. RuntimeReview registra compras, caja y rutinas fallidas durante el Play de Alain. El agente no abrió Unity ni ejecutó Play. Guía docs/Ciudad-3km-R9.md. Integración física/visual, rendimiento y aprobación pendientes de prueba; no cerrar tareas ni hacer commit. Mantener Unity 6000.3.27f2. El transporte MCP de Blender continúa cerrado; se usa Blender portable con bpy y fuentes propias, como en las correcciones anteriores.

## Mantenimiento y corrección R9.2 — 2026-11-02

Alain pidió revisar el proyecto, reducir su tamaño (68,8 GB) y corregir el error de «Crear y probar juego» y la locomoción. Unity se mantiene en 6000.3.27f2 por decisión de Alain.
- Error corregido: la comprobación física usaba `SceneManager.CreateScene`, que solo existe en Play; ahora usa `EditorSceneManager.NewPreviewScene` y se detiene si no obtiene física propia.
- Tamaño: el botón dejaba una copia de 2–3,6 GB por clic en `Generated/` y Unity reimportaba cada una (Library 48,7 GB). Se borraron las seis copias, los FBX `export/` de R4–R8 (R9 no los usa; .blend, .json y scripts se conservan) y Library. Resultado: 4,4 GB antes de reimportar.
- Regla nueva: el constructor conserva solo la preparación vigente; si falla, borra su carpeta y escribe `Generated/AlarmaPlaytestFailure.json`. `Generated/` y `Scenes/Backups/` quedan fuera de Git.
- Mallas físicas: vértices soldados entre triángulos vecinos; misma forma, varias veces menos disco y cocinado.
- Locomoción del jugador de revisión: aceleración y frenado graduales, giro 720°/s, velocidad estable al Animator con amortiguación y sin correr en el sitio contra paredes.
Compilado con dotnet contra las DLL instaladas. Prueba en Unity de Alain pendiente; no se cambia ninguna casilla.

### Vegetación ligera R9.3 — 2026-11-03

Alain autorizó aligerar la vegetación para bajar el peso del proyecto. Se mantiene posición, cantidad, colores y viento de cada planta; cambia el detalle de cada malla.
- `PlaytestR9~/lighten_vegetation.py` lee `Villa_Alarma_3000_R9.blend` (sin modificarlo) y guarda `Villa_Alarma_3000_R9_Ligera.blend`. Árboles: por especie, la reducción de LOD que conserva más superficie de hojas con 1800 triángulos. Follaje de macetas: 15 %. Pasto: LOD2 intacto; LOD0/LOD1 limitados a 600.
- Ciudad: 141,6 M → 42,4 M triángulos. FBX de las 153 celdas: 1687 MB → 630 MB. `world.json` conserva piezas, roles, colisiones y viento.
- `export_world.py` acepta `ALARMA_R9_WORLD`; Unity: build `playtest-r9-3`, tangentes desactivadas en la ciudad (colores planos).
- Alain aprobó la vegetación en Unity el 2026-11-03; el respaldo `export/World_R9_Original` se borró. La exportación anterior se regenera desde `Villa_Alarma_3000_R9.blend`.
Capturas Blender antes/después entregadas. Prueba en Unity, medición final de disco y aprobación visual de Alain pendientes; no se cambia ninguna casilla.

## Personajes de páginas gratuitas — 2026-11-03

Alain informa que el ingeniero autorizó usar páginas gratuitas para los personajes en vez de modelarlos desde cero en Blender, buscando diseños más adecuados y ligeros.
- Solo con licencia clara que permita usarlos en un juego publicado: preferir CC0; CC BY solo con crédito en `Assets/Party/docs/LICENSES.md` y en los créditos del juego. Nada con licencia no comercial, sin licencia o extraído de otros juegos.
- El repo de GitHub es público: no subir FBX crudos de Mixamo (sus términos prohíben redistribuirlos sueltos).
- Cada modelo se registra en `LICENSES.md` (página, autor, licencia, fecha) antes de usarlo. Las descargas las hace Alain o se piden antes.
- Siguen vigentes: low-poly con colores planos, 1 unidad = 1 metro, importación Humanoid y animaciones compartidas por retargeting. Vehículos, armas, mapa y locales siguen hechos en Blender.

### Seguridad y policía sobre Quaternius UBC — 2026-11-03

El ingeniero autorizó personajes de páginas gratuitas. Alain eligió Quaternius Universal Base Characters (CC0) para seguridad y policía, solo hombres; los civiles saldrán de otra página con proporción normal.
- `SecurityUBC~/build_security.py`: ropa como cáscara del propio cuerpo (mismos pesos), piel tapada eliminada, botas cerradas, cinturón, radio, porra (seguridad) y funda con pistola (policía). La ropa no añade masa: +0,2 cm de ancho en el pecho y +2–3 cm en caderas y piernas.
- Salida: `Art/Characters/Humanoid/Security_Male.fbx` y `Police_Male.fbx` (65 huesos, 15,6–17,6 k triángulos). `HumanoidCharacterImport` importa como Humanoid todo FBX de esa carpeta, sin clips propios.
- `PedestrianReach` usa los huesos del avatar Humanoid cuando existe; los rigs Generic anteriores siguen buscándolos por nombre.
- Clips propios en el esqueleto UBC (`ubc_animation.py`, portado de R6/R9): Idle, Walk, Run, Browse, Pay y CarryWalk, más agarre y bolsa en la mano derecha. La copia para la prueba sustituye a NPC11_SecurityMale y NPC13_PoliceMale; NPC12 y NPC14 (mujeres) salen de `characters.json`.
- Prueba `playtest-r9-4`: guardia junto a la puerta de cada comercio y policías frente a la joyería y la comisaría (`ReviewSecurityBuilder`), con su clip de reposo. `RigBones` encuentra pie, brazo y columna en los dos esqueletos.
Alain aprobó la vista en Blender. Pendiente su prueba en Unity; patrullas, detección y arrestos llegan con las tareas de policía. No se cambia ninguna casilla.

### Elenco low-poly modular — 2026-11-03

Alain pidió un único estilo para todo el elenco: low-poly de los packs CC0 Ultimate Modular Men y Women de Quaternius (proporción normal, colores planos, mismo esqueleto de 62 huesos y 24 animaciones).
- `ModularCast~/build_cast.py` combina piezas del pack, las recolorea y añade cinturón, radio, porra o funda, gorra, charreteras y rótulos. Exporta a `Art/Characters/Cast/` y copia al elenco de la prueba con su id.
- Seguridad (`Casual2_Head`, `Worker_Body`, `Swat_Legs`, `Swat_Feet`) y policía (`Suit_Head`, `Casual2_Body`, `Suit_Legs`, `Suit_Feet`): 8,6 k y 7,3 k triángulos, sin vértices sin peso. Clips del pack con alias Browse/Pay = Interact y CarryWalk = Walk, más extras (pistola, saludo, golpes, impacto, muerte).
- Diez civiles según las láminas 01-10 (cinco hombres y cinco mujeres, 5,1-7,1 k triángulos) y los cuatro protagonistas: Don Sigilo (gorro, antifaz y saco), Primo WiFi (gorra con antenas, gafas y mochila), Abuelita Falsa (pelo gris, gafas y bigote) y Toñito (brazos y pecho ensanchados sin tocar el esqueleto, gorrito). Reposo con `Idle_Neutral` (el `Idle` del pack gira el cuerpo).
- Los 16 personajes de la prueba salen de este script; los civiles llevan 6 clips (2,2 MB) y el resto añade los extras de su papel (≈4,4 MB).
- Sustituye a la versión sobre Universal Base Characters (`SecurityUBC~`, `Art/Characters/Humanoid`) y al elenco anterior de Blender, pendientes de borrar con permiso de Alain. `RigBones` usa los nombres del pack. Prueba `playtest-r9-6`.
- Alain aprobó el elenco en Play. Corrección: NPC doblados al caminar. `PedestrianReach` inclinaba la columna cada fotograma y el `Abdomen` del pack no tiene animación que lo reinicie; ahora devuelve columna y brazo a su pose antes del siguiente fotograma. Guardias fuera de los comercios, junto a la entrada. Prueba `playtest-r9-7`.
Pendiente: prueba de Alain de la corrección. No se cambia ninguna casilla.

### Limpieza y ciudad 2,5 × 2,5 km — 2026-11-03

Alain autorizó eliminar lo que ya no sirve, optimizar espacio y rendimiento y empezar la ciudad nueva de 2,5 × 2,5 km.
- Retirado (2,44 GB, 183 elementos) a `C:\Users\Alain\Atraco3D_Retirado\2026-11-03\`, sin borrado definitivo. Incluye: personajes antiguos (`Characters/*.fbx` salvo disfraces, sus prefabs, `ReferenceV2` y `Humanoid`); la regla `HumanoidCharacterImport`; las fuentes de personajes (`CastLegsR3~`, `LowPolyCast~`, `RigLegsR2~`, `TonitoGymR1~`, `Character*~`, `SecurityUBC~` y los scripts sueltos); los mapas anteriores (`Map4Km~`, `Map4KmModernR2~`, `TreesWindR3~`, `PlantersGrassR4~`, `CityLifeR5~`); el pack UBC y los formatos sin usar del pack modular. Catálogo y sumas actualizados.
- Se conservan, porque los usa la prueba actual: `CityLifeR6~`, `PlaytestR7~`, `PlaytestR8~` y `PlaytestR9~`. Se retirarán cuando la ciudad nueva sustituya a la R9. Los disfraces antiguos siguen pendientes de rehacerse en el estilo modular.
- `Assets`: de 7,9 GB a 3,1 GB. `Library` baja al reiniciar Unity.
- Espacio y rendimiento de la ciudad nueva: kit modular instanciado (prefabs reutilizados en vez de 153 celdas FBX con la geometría horneada), colisiones con cajas y planos en vez de mallas, generador que referencia el kit sin copiarlo a `Generated`, materiales compartidos (SRP Batcher e instanciado), LOD de edificios, carga por sectores, y NPC y autos con pool solo cerca de los jugadores.
- `City25~/city_plan.py` genera `city_plan.json` (fuente única de calles, cuadras, zonas, cruces, semáforos, pasos de cebra y locales) y `plano_ciudad.png`. Primera propuesta: 324 cuadras, 361 cruces (217 con semáforo), 1292 pasos de cebra y 27 locales y puntos clave (3 bancos, 3 joyerías, 4 supermercados, 3 minimarkets, escapes, 2 comisarías, taller, reducidor, gasolineras y alcantarilla).
Pendiente: aprobación del plano por Alain antes de modelar el kit. No se cambia ninguna casilla.

### Plano v2 y mapa del juego — 2026-11-03

Alain pidió un trazado menos cuadriculado y un mapa claro, de estilo videojuego: lugares a la vista (robos, tiendas, comida para distraer a la policía, garajes) y su flecha en tiempo real.
- `City25~/city_plan.py` v2: bulevar diagonal hasta la plaza con rotonda, río con 8 puentes y paseo en la ribera, avenidas con curvas, calles curvas en Las Lomas y Villa Sur, parque sin calles internas y naves industriales grandes. Resultado: 245 cuadras; 288 cruces (196 con semáforo, 86 con stop y 6 en la rotonda); 946 pasos de cebra; 35 lugares, entre ellos 6 de comida y 2 talleres.
- Mapa de estilo videojuego (`plano_ciudad.png`): fondo oscuro, zonas, nombres de barrios y avenidas, marcas circulares por categoría y leyenda agrupada (Robos, Servicios, Refugio, Policía). Para el juego genera `Art/UI/Map/mapa_base.png`, los iconos y `map_places.json`.
- `Alarma.UI.Map`: `CityMapDefinition` (datos), `CityMapScreen` (mapa a pantalla completa con zoom, arrastre, leyenda, nombre al pasar el ratón y clic para viajar), `CityMinimap` (esquina con el norte arriba) y `MapUi` (piezas creadas por código). La flecha del jugador gira hacia donde camina.
- En la prueba actual (3 × 3 km), `ReviewMapBuilder` usa el plano R9 con las categorías e iconos nuevos; se retiró el mapa IMGUI. Prueba `playtest-r9-8`.
Pendiente: aprobación del plano v2 y prueba del mapa en Play. No se cambia ninguna casilla.

### Correcciones de prueba y plano 2 × 2 km — 2026-11-03

Alain probó el mapa: pidió una ciudad de 2 × 2 km, techos estables, un HUD limpio y puertas que se abran al querer entrar.
- Techos: se retiró `ReviewRoof`, que ocultaba el techo cuando la cámara entraba en un local y lo mostraba al salir (parpadeo al mover el ratón). Los techos ya no desaparecen; la cámara choca con paredes y techo.
- HUD: se retiraron la cámara libre (V), el catálogo F6 (`ReviewCatalog` y `ReviewModelPreview`), el clic derecho, la lista de controles, los contadores y las cajas de depuración. F1–F4 siguen funcionando sin mostrarse. Esc libera el ratón y un clic lo recupera. Solo quedan el minimapa, el mapa (M), el aviso de carga y «E · Abrir puerta».
- Puertas: `AutomaticShopDoor` pasa a `ShopDoor`, que solo se abre al empujarla y se cierra sola. El jugador abre puertas y persianas con E (`ReviewDoorInteraction`). Los NPC empujan la puerta con la mano al entrar o salir (`ShopActivity.PushDoor` y `PedestrianReach`). La puerta se mantiene abierta mientras alguien sigue en el umbral.
- La prueba ya no copia vehículos ni armas a `Generated` (solo los usaba el catálogo).
- Plano: `CITY_SIZE = 2000`. El trazado se escala desde el diseño de 2,5 km sin cambiar los anchos de calles y aceras: 240 cuadras, 287 cruces y 943 pasos de cebra. Prueba `playtest-r9-9`.
Pendiente: prueba de Alain y aprobación del plano de 2 × 2 km para construir la ciudad en 3D. No se cambia ninguna casilla.

## Equipo nuevo, Blender MCP y arte con IA gratuita — 2026-11-03

- Proyecto clonado desde GitHub en `C:\Users\Alain\ATRACO-3D`; el equipo anterior (`C:\Users\Alain\Atraco3D`) ya no está disponible. Los `.blend`, los FBX/PNG de carpetas `~` y `Generated/` no estaban en Git y se perdieron: la escena `Atraco.unity` tiene referencias rotas y «Crear y probar juego» no puede preparar R9. Alain decidió rehacer el arte antes de Task 02.
- Blender 4.5.10 LTS y servidor `mcp-for-blender==2.2.6` registrados en `.mcp.json` (telemetría desactivada). Solo Hyper3D Rodin activo con la clave de prueba; el resto de integraciones apagadas. Detalle en `Assets/Party/Art/README.md`.
- El ingeniero autorizó usar **planes gratuitos de IA generativa 3D** (Rodin, Meshy, Tripo) para crear los modelos. Esto amplía la regla de modelos hechos solo con Blender por MCP. Sigue prohibido descargar modelos o texturas ya hechos de bibliotecas. Cada modelo generado se limpia en Blender (low poly, colores planos, 1 unidad = 1 m) y se registra con su licencia en `docs/LICENSES.md`.
- Task 03: puente comprobado con `Art/Validation/ConnectionCube_MCP.fbx` (1 × 1 × 1 m en Blender y en Unity) y captura `docs/Capturas/Task03_ConnectionCube_MCP.png`. Alain confirmó la prueba el 2026-11-03; Task 03 completada.

## Dos copias del proyecto — 2026-11-04

- El commit `task-03` (Blender por MCP, cubo de validación, `.mcp.json`) se hizo en una copia en `C:\Users\Alain\ATRACO-3D`. El trabajo de la ciudad siguió en `C:\Users\Alain\Atraco3D`, que sí conserva los `.blend`, el kit y la ciudad de 2 × 2 km (commits avance-r10 a avance-r12); ahí «Crear y probar juego» funciona y se usa Blender 5.2.
- Las carpetas `~` y `Generated/` siguen fuera de Git: en otra copia faltan esos binarios hasta regenerarlos con los scripts de `Art/BlenderScripts`.
