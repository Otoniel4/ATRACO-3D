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
- **Prohibido usar modelos o texturas ya hechos descargados de internet.** Todos los modelos se crean con IA controlando Blender por MCP (aceptado por el ingeniero).
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
- Task 00 completada: paquetes verificados y prueba del entorno confirmada por Alain el 2026-10-31. Commit de cierre: `1c3dbdc`. Task 01 validada por Alain: captura con 9 pruebas correctas y autorización para continuar con Blender. Registrar su commit de cierre antes de empezar el arte.
- Informe y pasos: `Assets/Party/docs/TASK-00-Entorno.md`.

## Prioridad confirmada por Alain — 2026-10-31

Después de Task 01: conectar Blender y crear mapa, personajes, accesorios, vehículos, armas y herramientas. Después del arte aprobado: clips, prototipo de red y dinámicas. Seguir la sección de orden vigente de TASKS.md; Task 02 ya no precede al arte. Mantener Unity 6000.3.27f2.

## Producción de arte autorizada

Alain pidió continuar con Blender para realizar todos los diseños requeridos. Progresar por los hitos de conexión, estilo y lotes de modelos, conservando capturas y scripts. La aprobación visual de Alain sigue pendiente para cada entrega; no marcar diseños como aprobados ni simular el rig de Mixamo sin los archivos necesarios.
