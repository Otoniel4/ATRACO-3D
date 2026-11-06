# TASKS.md — Plan de desarrollo de "Alarma"

Reglas: una task a la vez y en orden. Nunca se salta de una task a otra sin la confirmación de Alain. Una task solo se marca `[x]` cuando Alain la probó y funciona. Cada task se cierra con su commit.

Formato de cada task: **Objetivo** · **Patrones / SOLID** · **El agente hace** · **Alain hace** · **Criterios de aceptación**.

Hitos: al terminar cada bloque marcado como **HITO**, se hace una prueba completa con 2 jugadores antes de seguir.

---

## Orden de ejecución vigente — confirmado por Alain

Actualización del 31 de octubre de 2026: Alain pide completar Task 01 y después producir los diseños y modelos en Blender antes de implementar la red y las dinámicas. Esta sección define el orden de trabajo; los números de las tareas se conservan como identificadores.

1. Task 00: entorno (completada).
2. Task 01: arquitectura base (completada y validada por Alain).
3. Task 03: conexión con Blender por MCP y exportación de prueba (completada).
4. Arte: Task 03.1 (estilo), 03.2 (cuerpos y preparación del rig), 03.3 (ropa y variantes), 03.5 (mapa modular), 03.6 (vehículos), 03.7 (accesorios e interiores) y 03.8 (armas y herramientas).
5. Task 03.4: clips y preparación de animaciones una vez aprobados los diseños.
6. Task 02: prototipo de red, antes de integrar dinámicas compartidas.
7. Tasks 04–34: animación en juego, movimiento, interacción, combate, semáforos, tráfico y demás sistemas, en su orden y con sus pruebas online.

Se mantiene una tarea a la vez y la validación de Alain antes del cierre y commit. Ninguna tarea se considera completada por cambiar su prioridad.

### Ampliación autorizada — 2026-11-02

Alain aprueba visualmente vegetación R4 y pide ahora NPC paseando y comprando, junto con interiores más diseñados. Se prepara Ciudad viva R5 como revisión animada de arte y prototipo local aislado: clips propios, rutinas y un constructor de demo. Esta solicitud permite esa preparación ahora. Task 02 continúa antes de integrar decisiones compartidas/sincronización online. No se modifica ninguna casilla ni se da por terminada una task por compilar o renderizar; faltan revisión R5 y prueba en Unity de Alain.

# BLOQUE A — Base técnica

## [x] Task 00 — Entorno y verificación
- **Objetivo:** entorno listo antes de escribir código del juego.
- **El agente hace:** verificar RTK (`rtk gain`) y Caveman; revisar `Packages/manifest.json` y listar paquetes faltantes (AI Navigation, Cloud Save, Timeline); verificar `.gitignore` de Unity e inicializar Git; confirmar con Alain la ubicación de `Party/`.
- **Alain hace:** instalar los paquetes faltantes; activar Relay, Lobby y Cloud Save en Unity Cloud.
- **Criterios:** herramientas activas, paquetes instalados, Git listo, carpeta `Party/` confirmada.

## [x] Task 01 — Arquitectura base
- **Objetivo:** carpetas, namespaces, Assembly Definitions y sistema de eventos.
- **Patrones / SOLID:** Observer (canales de eventos con ScriptableObjects), D (dependencias por eventos e interfaces).
- **El agente hace:** crear en `Party/` las carpetas `Scripts/{Core,Player,Animation,Networking,AI,City,Traffic,Heist,Police,Vehicles,Economy,UI,Audio}`, `Art/{Characters,City,Vehicles,Props,Animations,Materials}`, `Prefabs`, `Scenes`, `Data`; Assembly Definitions por módulo; canales de eventos; interfaces base (`IInteractable`, `IDamageable`, `IDetectable`, `IArrestable`, `IIntimidatable`).
- **Alain hace:** confirmar que compila sin errores.
- **Criterios:** compila; nada fuera de `Party/`; explicación de la arquitectura entregada.

## [ ] Task 02 — Prototipo de red (Relay + Lobby)
- **Objetivo:** dos jugadores conectados por internet con código de sala.
- **Patrones / SOLID:** S (autenticación, sala y conexión como servicios separados), D (la UI depende de interfaces).
- **El agente hace:** inicio de sesión anónimo; crear sala y código de Relay; unirse con código; UI mínima Crear / Unirse.
- **Alain hace:** escena `Boot` con NetworkManager y la UI; cápsula de prueba como prefab de jugador.
- **Criterios:** con Multiplayer Play Mode, ambos jugadores se ven conectados.

## [x] Task 03 — Conexión Codex ↔ Blender (MCP)
- **Objetivo:** que el agente controle Blender para crear todos los modelos con IA.
- **El agente hace:** guiar la instalación de un servidor MCP para Blender (por ejemplo, el proyecto de código abierto `blender-mcp`) y su registro en la configuración del agente (`~/.codex/config.toml` en Codex); verificar la conexión creando un cubo y tomando una captura del viewport; **desactivar** cualquier integración que descargue assets de internet (bibliotecas de modelos o texturas), porque está prohibido usar modelos ya hechos; crear `Party/Art/README.md` con el estilo visual, la escala (1 unidad = 1 metro) y las reglas de exportación (FBX, eje Y arriba, nombres en inglés).
- **Alain hace:** instalar Blender, el add-on y el servidor MCP; arrancar el servidor desde Blender.
- **Criterios:** el agente crea un objeto en Blender, toma una captura y lo exporta a FBX que se importa bien en Unity.

## [ ] Task 03.1 — Guía de estilo y paleta
- **Objetivo:** definir un estilo low-poly de colores planos, sin texturas, para que todos los modelos combinen.
- **El agente hace:** crear en Blender una paleta de materiales compartidos (un atlas de colores en una sola textura pequeña o materiales planos con nombre), un modelo de referencia de escala (persona de 1,75 m, puerta, auto) y un script de exportación a Unity reutilizable.
- **Alain hace:** aprobar el estilo con capturas.
- **Criterios:** un archivo `.blend` de referencia y un script de exportación que funciona.

## [ ] Task 03.2 — Personajes base (hombre y mujer) y rig con Mixamo
- **Objetivo:** dos cuerpos base low-poly rigeados y listos para animar.
- **El agente hace:** generar con scripts bpy los dos cuerpos en pose T, como una sola malla cerrada, con proporciones humanas; exportarlos a FBX listos para subir a Mixamo; después de que Alain traiga el FBX rigeado, revisar el esqueleto en Blender y preparar la importación en Unity como rig Humanoid.
- **Alain hace:** subir cada FBX a Mixamo (cuenta gratuita de Adobe), colocar los marcadores del auto-rig y descargar el modelo rigeado en FBX con piel.
- **Criterios:** los dos personajes se importan en Unity como Humanoid sin errores de huesos y se deforman bien en una pose de prueba.

## [ ] Task 03.3 — Piezas modulares de personajes y uniformes
- **Objetivo:** combinar piezas para lograr al menos 10 civiles distintos, más guardia, policía y jugador.
- **El agente hace:** generar piezas intercambiables ajustadas al cuerpo base (peinados, gorras, chaquetas, camisas, pantalones, faldas, lentes); uniforme de guardia con porra; uniforme de policía con pistola y gorra; uniforme del jugador con máscara; **asignar cada pieza al esqueleto de Mixamo** del cuerpo base transfiriendo los pesos del cuerpo (Data Transfer en Blender), para que todas las piezas compartan el mismo esqueleto.
- **Alain hace:** aprobar los diseños con capturas.
- **Criterios:** las piezas siguen el esqueleto al animarse, sin atravesar el cuerpo de forma visible; guardias y policías se distinguen a simple vista.

## [ ] Task 03.4 — Animaciones con Mixamo
- **Objetivo:** el set de animaciones del juego, compartido por todos los personajes.
- **Lista:** idle, caminar, correr, agacharse, caminar agachado, apuntar con pistola, disparar, asustado agachado, manos arriba, huir, derribado, levantar compañero, golpe de porra, esposar, caída cómica, sacar del auto, ser sacado del auto, sentarse a conducir, salir corriendo de un auto.
- **El agente hace:** preparar la lista con el nombre de búsqueda sugerido en Mixamo y la configuración de descarga de cada una (FBX, sin piel, 30 fps, "In Place" para las de locomoción); configurar la importación en Unity (rig Humanoid, loop donde corresponde, raíz) y los nombres de los clips; donde no exista una animación adecuada en Mixamo (por ejemplo, sacar del auto), crearla con keyframes por script bpy sobre el esqueleto de Mixamo.
- **Alain hace:** buscar y descargar las animaciones en Mixamo siguiendo la lista; registrarlas en `docs/LICENSES.md`.
- **Criterios:** todas las animaciones funcionan en hombres, mujeres, guardias y policías gracias al retargeting Humanoid de Unity.

## [ ] Task 03.5 — Kit modular de ciudad
- **Objetivo:** piezas para armar toda la ciudad.
- **El agente hace:** generar con scripts bpy calles, cruces, aceras, pasos peatonales, bordillos, semáforos, faroles, señales, bancas, basureros, árboles; módulos de edificio (pared, ventana, puerta, esquina, techo, letrero) que encajen en una cuadrícula de 1 m.
- **Alain hace:** aprobar con capturas.
- **Criterios:** las piezas encajan sin huecos y se exportan como prefabs reutilizables.

## [ ] Task 03.6 — Vehículos
- **Objetivo:** autos civiles variados y patrulla exclusiva.
- **El agente hace:** generar un chasis base con ruedas separadas (para Wheel Collider) y puertas como objetos aparte; variantes sedán, hatchback, camioneta y taxi; patrulla con barra de luces; asiento del conductor marcado.
- **Alain hace:** aprobar con capturas.
- **Criterios:** al menos 4 modelos civiles y 1 patrulla, con ruedas y puertas separadas.

## [ ] Task 03.7 — Props de locales
- **Objetivo:** llenar minimarket, joyería, banco, escondite y locales de escape.
- **El agente hace:** generar estantes, productos variados, cajas registradoras, refrigeradores, vitrinas, joyas, escritorios, sillas, cajeros, caja fuerte, bóveda, cámaras de seguridad, luces de alarma, maniquíes, teléfono, bolsas de botín, celulares.
- **Alain hace:** aprobar con capturas.
- **Criterios:** suficientes props para que ningún local se vea vacío.

## [ ] Task 03.8 — Armas y herramientas propias
- **Objetivo:** diseños low-poly de las armas, herramientas y consumibles del GDD antes de implementar su dinámica.
- **El agente hace:** crear con Blender por MCP los modelos de pistola, escopeta, táser, rifle y porra, más palanca, ganzúa, bridas, taladro, cortavidrios, dispositivo de hackeo, termita, gancho, humo, granada aturdidora y EMP; conservar scripts bpy y exportar con escala correcta, puntos de agarre y piezas móviles separadas donde sea necesario. Sin disparos ni efectos implementados en esta tarea.
- **Alain hace:** aprobar las capturas y revisar la escala y orientación en Unity.
- **Criterios:** modelos propios aprobados y exportaciones reutilizables; los NPC guardias solo llevan porra y los únicos NPC con armas de fuego son los policías.

# BLOQUE B — Jugador

## [ ] Task 04 — Personaje del jugador y Animator
- **Objetivo:** personaje con animaciones sincronizadas en red.
- **Patrones / SOLID:** State (locomoción), S (controlador de animación separado del movimiento).
- **El agente hace:** Animator Controller con Blend Tree de locomoción (idle, caminar, correr), capa de agachado, capa superior para apuntar; componente que traduce el estado del jugador a parámetros del Animator; sincronización con NetworkAnimator.
- **Alain hace:** configurar el prefab del jugador con el modelo y el Animator.
- **Criterios:** las animaciones cambian con fluidez y el otro jugador las ve iguales.

## [ ] Task 05 — Movimiento y cámara en tercera persona
- **Objetivo:** moverse, correr, agacharse y apuntar con cámara Cinemachine.
- **Patrones / SOLID:** S (input, movimiento y cámara separados).
- **El agente hace:** acciones de Input System; movimiento con autoridad del dueño; cámara Cinemachine solo para el jugador local, con modo apuntar.
- **Alain hace:** configurar la cámara Cinemachine.
- **Criterios:** cada jugador controla solo su personaje; movimiento fluido en ambas instancias.

## [ ] Task 06 — Inventario rápido e inventario completo
- **Objetivo:** barra de 5 espacios (teclas 1 a 5) y un inventario grande que se abre con Tab.
- **Patrones / SOLID:** Strategy (cada ítem define su uso), O y L (nuevos ítems sin tocar el inventario), ScriptableObjects para los datos.
- **El agente hace:** modelo de inventario de red; barra rápida 1–5 y rueda del mouse; inventario completo con Tab para mover objetos a la barra; ítem visible en la mano del personaje.
- **Alain hace:** crear los assets de pistola, palanca, ganzúa y bridas; enganchar los modelos a la mano.
- **Criterios:** cambiar con 1–5 funciona; Tab abre el inventario completo; el otro jugador ve el ítem en la mano.

## [ ] Task 07 — Sistema de interacción
- **Objetivo:** interactuar manteniendo E.
- **Patrones / SOLID:** I (`IInteractable`), Command (acción pedida por RPC y validada por el host).
- **El agente hace:** detector de interactuables, barra de progreso, validación de distancia en el host.
- **Alain hace:** puerta de prueba.
- **Criterios:** la puerta se abre para ambos; el host rechaza interacciones lejanas.

## [ ] Task 08 — HUD superior: vida y dinero del equipo
- **Objetivo:** barra de vida y dinero compartido arriba de la pantalla.
- **Patrones / SOLID:** Observer (la UI solo escucha eventos).
- **El agente hace:** HUD con vida del jugador local, dinero del equipo y barra rápida del inventario.
- **Alain hace:** acomodar el Canvas.
- **Criterios:** los valores se actualizan en tiempo real e iguales para ambos.

**HITO 1:** dos jugadores animados en red, con inventario, interacción y HUD.

# BLOQUE C — Ciudad

## [ ] Task 09 — Generador de ciudad modular
- **Objetivo:** ciudad de 6×6 cuadras (tamaño configurable) con calles, aceras, cruces peatonales, zonas y edificios.
- **Patrones / SOLID:** O (configuración por ScriptableObject; cambiar a 7×7 es un dato, no código), Factory (piezas por tipo).
- **El agente hace:** script de editor que arma la cuadrícula con piezas modulares de calle, cruces, aceras y edificios según la zona (comercial, financiera, residencial, servicios, afueras); marcadores de puntos clave; capa de navegación para peatones y autos.
- **Alain hace:** ejecutar el generador, corregir detalles a mano y hornear el NavMesh.
- **Criterios:** la ciudad tiene calles continuas, aceras y cruces; se recorre entera en red.

## [ ] Task 10 — Interiores de los locales robables
- **Objetivo:** minimarket, joyería y banco completos y llenos de detalle, no vacíos.
- **El agente hace:** prefabs de cada local con zonas pública y restringida; script de editor que distribuye props (estantes con productos, cajas, vitrinas, escritorios, cajeros) según un ScriptableObject de decoración; puntos de interés para NPC, guardias y cámaras.
- **Alain hace:** revisar y ajustar la decoración a mano hasta que se vea completa.
- **Criterios:** cada local tiene mostrador, productos o vitrinas, zona restringida, puntos de guardia y puntos de cámara; nada se ve vacío.

## [ ] Task 11 — Locales de escape
- **Objetivo:** lugares con interior para esconderse o cruzar durante una persecución.
- **El agente hace:** prefabs de tienda de ropa (modo maniquí), restaurante con puerta trasera, estacionamiento subterráneo, callejones y entrada al alcantarillado; marcadores de escondite.
- **Alain hace:** colocarlos repartidos por la ciudad.
- **Criterios:** hay al menos 5 lugares de escape distribuidos y se puede entrar por un lado y salir por otro.

# BLOQUE D — Atraco

## [ ] Task 12 — NPC dentro de los locales y variantes de personajes
- **Objetivo:** clientes y personal con rutinas, diseños únicos, hombres y mujeres.
- **Patrones / SOLID:** State (comprar, hacer fila, pagar, salir), Factory (crea NPC con variantes), S (percepción, decisión, movimiento y animación separados).
- **El agente hace:** máquina de estados genérica reutilizable; sistema de variantes que combina partes y colores para obtener al menos 10 diseños de civiles (hombres y mujeres); rutinas de cliente y cajera; animaciones conectadas.
- **Alain hace:** preparar las partes modulares y colocar NPC en el minimarket.
- **Criterios:** los NPC cumplen su rutina y no se repite el mismo aspecto en un mismo local.

## [ ] Task 13 — Intimidación, miedo y huida
- **Objetivo:** al apuntar, el NPC se agacha asustado o sale corriendo.
- **Patrones / SOLID:** I (`IIntimidatable`), O (cualquier NPC puede reaccionar sin modificar el sistema).
- **El agente hace:** medidor de valentía; reacción animada (agacharse asustado, manos arriba, huir); amarrar con bridas.
- **Alain hace:** ajustar las animaciones.
- **Criterios:** apuntar produce la reacción correcta y se ve igual en ambas instancias.

## [ ] Task 14 — Guardias con porra
- **Objetivo:** cada local robable tiene sus guardias con uniforme propio y porra (sin pistola).
- **Patrones / SOLID:** State (patrullar, sospechar, perseguir, golpear), Strategy (ataque cuerpo a cuerpo).
- **El agente hace:** patrulla por rutas; reacción al ruido; ataque con porra que quita vida; radio que alerta si queda inconsciente.
- **Alain hace:** modelo de guardia con uniforme distinto al de la policía y porra en la mano.
- **Criterios:** el guardia patrulla, detecta, persigue y golpea; nunca dispara.

## [ ] Task 15 — Cámaras de seguridad y alerta del local
- **Objetivo:** cámaras bien colocadas que vigilan zonas clave y alimentan la alerta.
- **Patrones / SOLID:** State (sigilo → sospecha → alarma → policía en camino → asalto), reutilizar el mismo componente de visión en cámaras, NPC y guardias.
- **El agente hace:** cámaras con modelo, giro y cono de visión; medidor de sospecha; máquina de estados de alerta en el host.
- **Alain hace:** colocar cámaras cubriendo entradas, caja y zona restringida de cada local.
- **Criterios:** ninguna zona restringida queda sin vigilancia; ser visto llena la sospecha.

## [ ] Task 16 — Alarma visual y sonora
- **Objetivo:** cuando salta la alarma se ve y se escucha.
- **Patrones / SOLID:** Observer (luces, sonido y UI escuchan el evento de alarma).
- **El agente hace:** luces giratorias, sirena del local, cambio de música y aviso en el HUD.
- **Alain hace:** colocar las luces de alarma en cada local.
- **Criterios:** al activarse la alarma, ambos jugadores la ven y la escuchan.

## [ ] Task 17 — Caja fuerte y botín
- **Objetivo:** código aleatorio por partida, bolsas que se cargan y se lanzan.
- **Patrones / SOLID:** S (generador de código, caja fuerte y bolsa separados).
- **El agente hace:** nota con el código; caja fuerte con código o palanca (ruido); bolsas que bajan la velocidad 30 % y se lanzan con G.
- **Alain hace:** colocar la caja fuerte y la nota.
- **Criterios:** se abre con el código; la palanca hace ruido; la bolsa pasa entre jugadores.

# BLOQUE E — Combate y policía

## [ ] Task 18 — Disparos, vida, derribo y rescate
- **Objetivo:** disparos hitscan, derribo a 0 de vida y rescate en 5 s.
- **Patrones / SOLID:** State (vivo / derribado / arrestado), I (`IDamageable`).
- **El agente hace:** disparo validado por el host con Raycast; vida en red; derribo con límite de 30 s; levantar compañero; animaciones.
- **Alain hace:** efectos de disparo e impacto.
- **Criterios:** el derribo y el rescate se ven igual en ambas instancias.

## [ ] Task 19 — Policía a pie con pistola y arresto
- **Objetivo:** solo la policía tiene pistola; persigue, apunta, dispara y arresta.
- **Patrones / SOLID:** State (llegar, buscar, perseguir, apuntar, arrestar), Factory y Object Pool.
- **El agente hace:** aparición al terminar la cuenta regresiva; persecución; disparo; arresto con animación de esposar; caída cómica al ser derribado (animación exagerada o ragdoll).
- **Alain hace:** modelo de policía con uniforme exclusivo y pistola.
- **Criterios:** la policía arresta a jugadores derribados; su caída se ve graciosa e igual en ambas instancias.

## [ ] Task 20 — Cárcel y fianza
- **Objetivo:** el arrestado va a la cárcel como espectador y la banda paga la fianza.
- **Patrones / SOLID:** S (cárcel, fianza y cámara de espectador separadas).
- **El agente hace:** traslado a la cárcel, cámara de espectador, pago de fianza en la comisaría.
- **Alain hace:** zona de cárcel y punto de pago.
- **Criterios:** el arrestado vuelve a jugar cuando se paga la fianza.

**HITO 2:** un atraco completo a pie en el minimarket: entrar, intimidar, robar, pelear con guardias, escapar o ir a la cárcel.

# BLOQUE F — Vehículos y ciudad viva

## [ ] Task 21 — Vehículos conducibles
- **Objetivo:** varios modelos de auto que el jugador puede conducir.
- **Patrones / SOLID:** S (entrada, física, asientos y cámara separados), ScriptableObject por modelo de auto.
- **El agente hace:** física con Wheel Collider; subir y bajar con F; autoridad del conductor; cámara de conducción; al menos 4 modelos civiles.
- **Alain hace:** prefabs de cada modelo.
- **Criterios:** dos jugadores en un mismo auto; movimiento estable en ambas instancias.

## [ ] Task 22 — Patrullas policiales
- **Objetivo:** auto exclusivo de policía con sirena y luces.
- **El agente hace:** IA de patrulla que va al punto del atraco y persigue; luces rojas y azules; sirena.
- **Alain hace:** prefab de patrulla.
- **Criterios:** la patrulla llega, persigue y los policías bajan a pie.

## [ ] Task 23 — Semáforos
- **Objetivo:** cruces con semáforos que controlan autos y peatones.
- **Patrones / SOLID:** State (verde, amarillo, rojo), Observer (autos y peatones escuchan al semáforo).
- **El agente hace:** controlador de cruce en el host con ciclos sincronizados; luz visible en el modelo.
- **Alain hace:** colocar semáforos en los cruces principales.
- **Criterios:** los semáforos cambian igual para ambos jugadores.

## [ ] Task 24 — Tráfico de NPC
- **Objetivo:** autos manejados por NPC que circulan y respetan semáforos.
- **Patrones / SOLID:** Object Pool, State (circular, frenar, esperar, huir).
- **El agente hace:** rutas por waypoints; distancia con el auto de adelante; frenar en rojo; aparición y desaparición lejos de los jugadores; conductor NPC visible dentro del auto.
- **Alain hace:** trazar las rutas.
- **Criterios:** los autos circulan sin chocar entre sí y se detienen en rojo.

## [ ] Task 25 — Robar un auto con conductor
- **Objetivo:** sacar al conductor NPC del auto con animación y tomar el auto.
- **El agente hace:** secuencia sincronizada en red: el jugador abre la puerta, saca al conductor (animación), el conductor cae y huye, el jugador entra y conduce; sube la sospecha si hay testigos.
- **Alain hace:** ajustar los puntos de puerta en cada modelo.
- **Criterios:** la secuencia se ve completa y sincronizada en ambas instancias.

## [ ] Task 26 — Peatones en la ciudad
- **Objetivo:** hombres y mujeres con diseños variados caminando por las aceras.
- **Patrones / SOLID:** Object Pool, reutilizar la máquina de estados y las variantes de la Task 12.
- **El agente hace:** peatones que caminan por las aceras, esperan en rojo en los cruces y cruzan en verde; reaccionan a disparos y armas (huyen o graban con el celular).
- **Alain hace:** revisar la densidad de peatones.
- **Criterios:** los peatones respetan el semáforo y reaccionan a los atracos.

# BLOQUE G — Persecución

## [ ] Task 27 — Nivel de búsqueda y escape
- **Objetivo:** estrellas según el local robado y perder a la policía.
- **Patrones / SOLID:** Observer (estrellas notifican a policía, radar y UI), O (los niveles se agregan sin tocar el sistema).
- **El agente hace:** nivel de búsqueda en el host; zona de búsqueda; bajar el nivel tras 30 s fuera de la vista; escondites y cambio de auto.
- **Alain hace:** probar rutas de escape.
- **Criterios:** se puede perder a la policía usando locales de escape o cambiando de auto.

## [ ] Task 28 — Radar (minimapa) estilo persecución
- **Objetivo:** minimapa en la pantalla con la policía y su zona de búsqueda.
- **Patrones / SOLID:** S (cámara del minimapa, íconos y efectos separados), Observer.
- **El agente hace:** cámara cenital que dibuja el minimapa; íconos de jugadores, policías, patrullas, locales y escondites; conos de visión de la policía; borde que parpadea rojo y azul durante la persecución; zona de búsqueda visible.
- **Alain hace:** diseño visual de los íconos.
- **Criterios:** el radar muestra a la policía y el parpadeo solo cuando hay búsqueda activa.

**HITO 3:** atraco, huida en auto robado y persecución con radar en una ciudad con tráfico y peatones.

# BLOQUE H — Progresión

## [ ] Task 29 — Economía: reducidor y bonus
- **Objetivo:** vender el botín y cobrar con bonus de golpe limpio según el lugar.
- **Patrones / SOLID:** Strategy (cálculo del bonus por local), S.
- **El agente hace:** cuenta de banda en el host; venta; bonus de 25 % / 40 % / 50 % / 60 % según el lugar.
- **Alain hace:** NPC reducidor en la ciudad.
- **Criterios:** el dinero es igual para todos y el bonus se aplica solo sin alarma.

## [ ] Task 30 — Escondite y tienda
- **Objetivo:** comprar equipo y disfraces con el dinero de la banda.
- **Patrones / SOLID:** O (catálogo en ScriptableObjects).
- **El agente hace:** catálogo por niveles; compra validada por el host; armario de disfraces.
- **Alain hace:** interior del escondite.
- **Criterios:** comprar descuenta el dinero común y el ítem aparece en el inventario.

## [ ] Task 31 — Guardado con Cloud Save
- **Objetivo:** guardar y cargar la banda.
- **Patrones / SOLID:** D (interfaz de guardado con Cloud Save como implementación).
- **El agente hace:** guardar dinero, equipo, disfraces y locales robados al volver al escondite.
- **Alain hace:** probar cerrando y abriendo el juego.
- **Criterios:** el progreso se conserva.

# BLOQUE I — Sonido y cierre

## [ ] Task 32 — Audio
- **Objetivo:** ciudad y atracos con sonido.
- **Patrones / SOLID:** Observer (el audio escucha eventos), S.
- **El agente hace:** lista de sonidos necesarios con el término de búsqueda sugerido; gestor de audio con AudioMixer (música, efectos, ambiente, voces); ambiente de ciudad; pasos; motores; sirenas; alarmas; disparos; gritos; música que cambia con la situación.
- **Alain hace:** descargar sonidos de buena calidad de sitios con licencia clara (por ejemplo, Freesound filtrando por CC0 o CC-BY, Kenney Audio, Sonniss GDC bundles) siguiendo la lista que prepara el agente, y registrar cada uno en `docs/LICENSES.md` con su autor si la licencia pide atribución.
- **Criterios:** cada evento importante tiene sonido; sonido 3D en el mundo.

## [ ] Task 33 — Optimización
- **Objetivo:** que la ciudad corra fluida con NPC, autos y 4 jugadores.
- **El agente hace:** desactivar NPC y autos lejanos; Object Pool; LOD; oclusión; medir con el Profiler y reportar resultados.
- **Alain hace:** probar en su PC y en la de un compañero.
- **Criterios:** rendimiento estable con 4 jugadores en la ciudad.

## [ ] Task 34 — Prueba integral y build
- **Objetivo:** todo el ciclo funcionando con 2 a 4 jugadores en PCs distintas.
- **El agente hace:** revisar errores, limpiar código y documentar en `Party/README.md` cómo jugar y la arquitectura.
- **Alain hace:** build de Windows y prueba por internet.
- **Criterios:** crear sala, robar, escapar o ser arrestado, vender, comprar y guardar, sin errores.

**HITO 4:** juego completo de la versión actual.

## Revisión de personajes con referencias — 2026-10-31

Alain rechazó la simplicidad del primer lote y aportó 14 láminas: diez civiles, dos guardias y dos policías. Se creó una revisión separada en `Assets/Party/Art/Characters/ReferenceV2` y `BlenderSources~/Alarma_Characters_ReferenceV2.blend`. La geometría y las capturas están disponibles para corrección y aprobación; aún no igualan todos los detalles de las láminas. Los rig de Mixamo, pesos, Humanoid y clips siguen pendientes. No cerrar Tasks 03.2, 03.3 ni 03.4 hasta cumplir sus pruebas. Mantener Unity 6000.3.27f2 y el resto del arte existente.

## Rechazo explícito de V2 — 2026-10-31

Alain rechazó V2 por falta de similitud y cuerpo deforme. No usarla ni continuar su rig o variantes. Rehacer primero el civil masculino de chaqueta naranja con referencias frontal, lateral y posterior calibradas. No declarar corregido el personaje por tener geometría cerrada o exportar sin errores. Las tareas de personajes y animación permanecen abiertas.

## Foco actualizado: estructura femenina — 2026-10-31

Alain volvió a señalar anatomía deforme y adjuntó la referencia 02 (mujer con chaqueta denim). Priorizar esta mujer y la estructura corporal sobre el rostro. Se creó `FemaleBody_AnatomyStudy`: una única base continua y un rig diagnóstico de 29 huesos para ensayar articulaciones. Es un estudio pendiente de revisión y refinamiento, no el personaje acabado ni el rig Mixamo final. La V2 sigue rechazada. No generar variantes hasta resolver esta base.

## Ajuste de ambas bases autorizado — 2026-10-31

Alain confirmó que la estructura continua femenina va bien y autorizó ajustar cintura y demás proporciones, y crear después una base masculina esbelta. Se conservaron dos copias nuevas en `BodyBases_Refined.blend`, con rigs diagnósticos independientes y pruebas de flexión. La aprobación anterior corresponde a la dirección de la estructura, no al personaje terminado ni a Humanoid. La V2 sigue rechazada; ropa y rig final pendientes.

### Corrección solicitada de ciudad viva R6 — 2026-11-02

Corregir dentro de la ampliación actual: circulación sin bloqueo mutuo, ambas manos, tareas de selección/agarre, compra, cobro y filas. Preparación R6 entregada con demo local y revisión Blender; prueba en Play y aprobación visual pendientes. La petición autoriza esta corrección y sus tareas ambientales ahora; no cierra Task 02 ni autoriza declarar sincronización online. No se cambia ninguna casilla por las pruebas automatizadas.

### Prueba integrada autorizada R7 — 2026-11-02

Alain pide una sola entrada en Alarma para preparar y probar lo creado. Se entrega preparación local con ciudad completa por partes, jugador/cámara de revisión, catálogo, interiores y compras de NPC; corrige el fallo del generador R6. La petición autoriza estos controles locales de revisión ahora, sin dar por terminadas Tasks 02/04/05 ni otros sistemas del GDD. Construcción y Play en Unity deben probarse por Alain antes de cerrar cualquier criterio. No se modifican casillas.

### Corrección de integración R8 — 2026-11-02

R7 rechazada por Alain durante Play. Se corrigen dentro de la prueba integrada actual: animaciones de locomoción, bolsa/cámara, puertas, contactos y rodeos de NPC, población de aceras, grafos de compra, mapa sin traslado y comprobación de vegetación contra asfalto. Entrega en docs/Correcciones-Prueba-R8.md. Verificaciones de fuentes superadas; prueba en Unity y aprobación pendientes. No se modifica ninguna casilla.

### Corrección de prueba R9 — 2026-11-02

R8 rechazada por Alain. Dentro de la misma corrección: mapa 3 × 3 km solicitado, inicio en escondite, cinco comercios reconstruidos con mercancía, fila y caja, calibración espacial FBX, puertas y recorrido de salida, animación de carrera y macetas. Fuentes y pruebas fuera del editor verificadas; comprobaciones físicas integradas en el mismo botón y prueba de Alain pendientes. Ver docs/Ciudad-3km-R9.md. No se cambia ninguna casilla ni se avanza a red.

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

## Ciudad 2 × 2 km — avance 2026-11-03 (lista para probar en Unity)

- Kit de 56 piezas desde R9 en `Assets/Party/Art/City/Kit25` (4,2 MB, `kit.json`, `kit_fbx.py` común). Frente = -Y de Blender = +Z de Unity (comprobado importando en un proyecto vacío).
- `City25~/city_objects.py`: 7985 objetos a lo largo de las calles (curvas y diagonal incluidas): 2469 edificios, 2382 faroles, 608 semáforos, árboles, lotes de gasolinera y estacionamiento, alcantarillas y mobiliario. Puertas de los locales despejadas.
- `City25~/build_ground.py`: suelo en 64 sectores FBX (`Art/City/Ground25`, 4,9 MB): calzadas, aceras con bordillo, líneas, 943 pasos de cebra, río con muros y barandas, puentes, plaza con fuente, parque con estanque. `-- --preview` renderiza `renders/ciudad_*.png`.
- Unity: **Alarma/Crear y probar juego** ahora abre la ciudad de 2 × 2 km (`Scripts/City/Editor/City25`); la R9 queda sin menú hasta trasladar sus comercios con NPC, puertas y guardias. Sectores activados por distancia (`CitySectorStreamer`, 420 m), colisiones, materiales planos (`FlatMaterialLibrary`), 4 protagonistas, mapa y minimapa del plano nuevo, comprobaciones en `Generated/Ciudad2km/Acceptance.json`.
- `IPlayableWorld` (Alarma.Core) desacopla jugador e interfaz de la ciudad concreta; R9 sigue funcionando con el mismo jugador (`ReviewPlayerRig`).
- Pendiente de prueba de Alain en Play. Después: semáforos con ciclo y autos (23–24), peatones por pasos de cebra (26), interiores de supermercado, joyería y banco con cajeros (03.7, 10, 12), guardias y puertas en la ciudad nueva.

## Limpieza y menú de pausa — 2026-11-03

- Ciudad de 2 × 2 km aprobada por Alain («si abre y está bien, me quedo con eso»).
- Retirados a `C:\Users\Alain\Atraco3D_Retirado\2026-11-03\` (datos_mapas_viejos y codigo_R9_R6): ciudades R6–R9 con sus compilaciones, respaldos de escenas y el código que solo las preparaba. `Assets` pasó de 3,2 GB a 483 MB. Alain borra esa carpeta a mano cuando quiera liberar el espacio.
- Se conservan: elenco en `Art/Characters/Cast`, colores en `Art/Materials/FlatColors.json`, shader de viento en `Art/Materials/Shaders`, fuente del kit en `Art/BlenderSources~/Villa_Alarma_R9_Ligera.blend`, y el código de NPC de compras (`Scripts/AI/CityLifeR5`) para trasladarlo a la ciudad nueva.
- Menú de pausa (Esc): continuar, opciones (volumen, sensibilidad, pantalla completa, calidad; guardadas en el equipo con `GameSettings`), controles y salir. No congela el juego porque será online.
- Orden siguiente acordado: 1) peatones por las aceras y pasos de cebra; 2) semáforos con ciclo y autos con conductor que los respetan, con autos rediseñados; 3) locales con puerta, interior lleno de productos y cajeros; NPC que entran, eligen, pagan y salen.

## [x] Ciudad viva 1: semáforos y peatones — 2026-11-03 (confirmado por Alain)

- Alain confirmó la limpieza y el menú de pausa («Sí, funciona»).
- `City25~/city_life.py` → `city_life.json`: 195 semáforos con sus ejes y red peatonal (15 992 nodos, 871 pasos de cebra, 539 con semáforo, 98,6 % conectada).
- `Alarma.Traffic`: `TrafficSignalNetwork` (reloj común: verde, amarillo y todo rojo por eje; tiempos en `Party/Data/TrafficSignalTiming.asset`), `TrafficLightHead` (luces encendibles del modelo).
- `Alarma.AI.Street`: `SidewalkGraph`, `SidewalkWalker` (pasea, no vuelve atrás, espera el rojo de la vía que cruza), `SidewalkPopulation` (pool de 45 peatones alrededor del jugador).
- Contrato `ITrafficSignals` en Alarma.Core: los autos usarán el mismo reloj.
- Semáforos reorientados: las luces miran a los autos que llegan. Árboles de avenida junto al bordillo.
- Siguiente: autos con conductor por carriles que respetan semáforos y pasos de cebra; autos rediseñados.

## [x] Ciudad viva 2: autos con conductor — 2026-11-03 (confirmado por Alain)

- Alain confirmó semáforos y peatones («Sí, funciona»).
- `City25~/city_traffic.py` → `city_traffic.json`: 1518 carriles (circulación por la derecha, rotonda antihoraria), líneas de parada antes de los pasos de cebra, control al final (semáforo con eje, pare, ceda en rotonda) y carriles siguientes; vuelta en los 22 callejones sin salida.
- `Alarma.Traffic`: `RoadNetwork` (carriles), `TrafficCar` (sigue el carril, curva en el cruce, frena ante autos, peatones y jugador, se detiene en rojo y en el pare, ruedas que giran), `TrafficPopulation` (pool de 26 autos alrededor del jugador).
- Autos de `Art/Vehicles` (sedán, hatchback, SUV, taxi) para el tráfico y los estacionados; los autos del kit R9 quedaron retirados.
- Siguiente: rediseño de los autos en Blender (más detalle, ruedas y puertas separadas) con capturas para aprobar; después locales con interior y compras.

## [x] Rediseño de autos — 2026-11-03 (v3 e integración confirmados por Alain)

- Alain confirmó el tráfico y pidió autos menos básicos, distintos entre sí, con conductor visible y luces.
- `Art/BlenderScripts/build_vehicles.py` v3: ocho modelos (sedán, hatchback, SUV, pickup con caja de carga, furgoneta, deportivo con alerón, taxi, patrulla), carrocería curva con molduras de arcos, línea lateral, juntas de puertas, marcos cromados, faros con luz de día, intermitentes, pilotos envolventes y tercera luz de freno; conductor sentado al volante y acompañante opcional; vidrio semitransparente. 4,9–7,3 mil triángulos.
- Convenciones para Unity por nombre de material: `Alarma_Paint_*` (color al azar por auto), `Alarma_Headlight`, `Alarma_TailLight` (más fuerte al frenar), `Alarma_Indicator` (parpadea al doblar), `Alarma_CarGlass`, `Alarma_Driver*`.
- Capturas en `Art/Previews~/autos_v3_*.png`. Tras la aprobación: exportar con `-- --export` y adaptar Unity (colores al azar, luces de freno, intermitentes, acompañante al azar, nuevos modelos en tráfico y estacionados).

- Alain aprobó el diseño v3 («Sí, apruebo»). Se corrigió el lado del conductor (izquierda: se circula por la derecha) y los nombres L/R de puertas y ruedas. Exportados los 8 FBX y `Art/Vehicles/vehicle_materials.json` (67 colores con brillo).
- `Alarma.Vehicles`: `CarPalette` (asset en `Party/Data/CarPalette.asset`), `CarAppearance` (pintura, conductor y acompañante al azar; estacionados fijos por posición), `CarLights` (freno e intermitentes), `IVehicleState` (lo implementa `TrafficCar`).
- Tráfico y estacionados usan los 7 modelos civiles; la patrulla queda para la policía.
- Alain pidió interior con detalle, un NPC real conduciendo y giros suaves. Cabina abierta con piso, puertas por dentro, apoyabrazos, asientos con apoyacabezas, consola, palanca, tablero con relojes y pantalla, retrovisor, parasoles y volante con columna; vidrio más oscuro y sin cara inferior.
- Conductores: civiles reales del elenco sentados con `SeatedPose` (misma regla de direcciones probada en Blender); 3 conductores por modelo (21 variantes) y acompañante al azar.
- `TrafficCar`: frena con calma antes de doblar (llega a 4,5 m/s), curva más suave (16 puntos y mirada hacia adelante), ruedas delanteras que doblan y frenado fuerte solo ante obstáculos.
- Corrección (2026-11-03): la moldura cromada era una placa entera que tapaba la cabina desde arriba (el «blanco»); ahora son dos franjas finas. Vidrio sin brillo ni reflejo del cielo. Taxi y patrulla conservan sus colores (no reciben pintura al azar).

## Locales con interior — 2026-11-03 (en curso)

- Alain confirmó autos con interior y conductor («Sí, se ve»). Ciudad viva completa: tráfico, peatones y semáforos.
- Fase 1 (en curso): minimarket modelo. Blender `build_shops.py` → `Art/City/Shops/Local_<tipo>.fbx` (exterior del mismo estilo, puerta de dos hojas real, interior lleno: estanterías con productos de `Art/Props`, refrigeradores, mostrador con caja) y `shop_layouts.json` (suelo caminable, obstáculos, puntos de estantería y producto, fila, mostrador, caja, cajero, puerta y recorridos).
- Unity: `City25Shops` reemplaza el edificio de cada local por su modelo, crea `ShopDoor` (E para el jugador, los NPC la empujan), `ShopActivity` con sus puntos, cuadrícula interior (`TrafficGraph` + `CityTrafficController`), cajero (`CashierPresentation`) y compradores (`CityPopulationDirector` con `PedestrianActor`), todo reutilizado de `Scripts/AI/CityLifeR5`.
- Fase 2: supermercado, joyería, banco, comida y ropa. Fase 3: guardias en las puertas.
- Fase 1 lista para probar: `build_shops.py` → `Art/City/Shops/Local_Minimarket.fbx` (129 piezas, 108 mil triángulos), `shop_layouts.json` y `shop_materials.json`. Unity: `City25Shops` (rutina con puntos, cuadrícula interior, ajustes de tienda, cajero), prefab del local con colisiones y `ShopDoor`, los 4 minimarkets del mapa reemplazan su edificio, compradores con `CityPopulationDirector` (ajustes en `Party/Data/ShopperSettings.asset`), puertas en `ReviewDoorInteraction` (E).
- Alain confirmó el minimarket («Sí, funciona»). Fase 2 lista para probar: `build_shops.py` reorganizado (base común + amueblado por tipo) con supermercado (verdulería, 6 hileras), joyería (vitrinas, islas, cajas fuertes, láseres, espejo), banco (ventanillas, bóveda, escritorios, fila con cordón, cajeros automáticos), comida (cocina, mesas, menú) y ropa (percheros, maniquíes, probadores). Producto, nombre y precio de cada local van en `shop_layouts.json`. 22 locales del mapa usan su interior.
- Fase 3 pendiente: guardias en las puertas de los locales.
- Alain confirmó la fase 2 («Sí, funciona»; se corrigieron dos puntos bloqueados y nombres de materiales). Fase 3 lista para probar: `City25Security` coloca 17 puestos (2 guardias por banco, 1 por joyería y supermercado, 2 policías por comisaría) con los modelos `Security_Male` y `Police_Male` del elenco; `SentryLook` (Alarma.AI.Security) los hace mirar alrededor sin dejar su puesto.
- Alain confirmó guardias y policías («Sí, funciona», 2026-11-04). Ciudad de 2 × 2 km completa para esta etapa: tráfico, peatones, semáforos, autos con conductor, 22 locales con interior y compras, y 17 puestos de seguridad.

## [x] Pulido de ciudad y NPC — 2026-11-04 (confirmado por Alain)

- Pedido de Alain: personajes lentos, puertas con gesto de empujar, postes unidos a árboles, sillas al revés, NPC quietos y en grupo, parpadeos, no se podía mirar al cielo, NPC fuera de la acera, compradores que solo llegan en grupo.
- Hecho: árboles de acera a más de 4,5 m de postes y semáforos (0 casos); sillas del local de comida hacia la mesa; capas del suelo y de los locales más separadas (sin parpadeo); vereda bajo las esquinas de los cruces (sin triángulos de pasto); cámara con inclinación de -35° a 70°; compradores a ~1,2 m/s, de a uno cada 6–14 s y con camino de llegada solo frente a la puerta (las mesas de la vereda los bloqueaban); el jugador hace el gesto de empujar al abrir con E (`PedestrianReach`).
- Postes sobre la calzada (reporte de Alain con captura): el plano ahora prueba cada poste contra todos los tramos de asfalto y las fachadas. Faroles junto al bordillo (0,7 m dentro de la vereda; 1,5 m del borde en el anillo, que no tiene vereda); si caen en otra calzada, en una fachada o sobre un mueble, no se ponen. Semáforos: si la esquina derecha cae en la calzada, retroceden por la vereda o pasan a la esquina izquierda. Resultado: 2341 faroles y 602 semáforos, 0 en asfalto, 0 en fachadas, 339 de 339 accesos con luz como antes, 0 árboles pegados a postes.

## [x] Ciudad 3.0 — fase A: calles con más objetos — 2026-11-04 (confirmado por Alain)

- Pedido de Alain: versión 3.0 del mapa de 2 × 2 km con más objetos, más dinámica y mejor hecha. Plan en 4 fases (A calles, B barrios y lugares, C dinámica, D revisión automática); Alain aprobó empezar por la A.
- Kit nuevo hecho en Blender (`City25~/build_street_kit.py` → `Art/City/Kit25/Street/*.fbx`, `street_kit.json`, `street_materials.json`): parada de bus con techo, banca y caja de luz; kiosco con toldo, revistas y golosinas; hidrante; buzón; señales PARE, CEDA EL PASO, 40 y 60; fila de bolardos; contenedor de basura; tres carteles publicitarios de locales del juego (Burger Bandido, Banco Sin Prisa, Diamante Azul). Capturas en `City25~/renders/street_kit_*.png`.
- Plano (`city_objects.py`, `street_details`): cada objeto se prueba como rectángulo contra la calzada, las fachadas, la franja por donde caminan los peatones (±0,8 m de su línea), las puertas de los locales y lo ya colocado; si no cabe se corre o no se pone. Colocados: 68 paradas, 12 kioscos, 13 carteles, 716 hidrantes, 162 buzones, 327 PARE, 6 CEDA, 308 de velocidad, 20 filas de bolardos frente a bancos, joyerías, supermercados y comisarías, 12 bicicleteros, 263 contenedores y 815 autos estacionados en las calles. Verificación independiente: 0 sobre la senda peatonal, carriles, fachadas o encimados.
- Carriles de las calles a 2,5 m del eje (`city_traffic.py`) para dejar junto al bordillo la franja de estacionamiento. Los objetos llevan su altura (`z`): vereda 0,14 m, asfalto 0,045 m.
- Unity: `City25Kit.Manifest()` junta los dos kits; colisiones por tipo (malla en parada, kiosco y cartel; poste en señales; un poste por bolardo); autos estacionados con una malla por material (de ~120 piezas a una por material) y luces apagadas, generados en `Generated/Ciudad2km`. Los prefabs anteriores `Kit25/Prefabs/Car_*.prefab` se movieron a `Atraco3D_Retirado/2026-11-04/`.
- Corrección pedida por Alain (captura: contenedor en la calzada, «corrige cosas lógicas»): los contenedores ya no van en la calzada; 319 quedan en el terreno de departamentos, galpones, torres y algunos comercios, al costado del edificio y detrás de la línea de fachada. Otras reglas lógicas: kioscos solo en zonas de comercio y parque (no en antejardines), carteles solo en zonas comerciales, industriales y afueras (no entre casas), taxis no quedan estacionados en calles de barrio, la banca de fachada mira a la calle. Barrido de los muebles antiguos con la misma regla: 51 bancas, basureros, maceteros y mesas que pisaban la franja de los peatones o la calzada se acercaron a la fachada y 6 se quitaron por falta de lugar; ahora quedan a la altura de la vereda. Prueba de la franja peatonal con distancia exacta tramo-rectángulo. Verificación: 0 muebles en la calzada o en la franja peatonal, 0 contenedores en veredas, 0 encimados.
- Alain confirmó en Unity la fase A con las correcciones lógicas y los postes fuera de la calzada («Sí, funciona», 2026-11-04). Siguiente: fase B (barrios con identidad y lugares nuevos), a la espera de su aprobación.

## Ciudad 3.0 — fase B1: barrios con identidad y lugares — 2026-11-04 (pendiente de prueba)

- Alain aprobó la fase B. Se divide en B1 (barrios y lugares, esta entrega) y B2 (callejones como rutas de escape, que cambian el plano, el suelo y la red peatonal).
- Herramientas de modelado comunes en `City25~/kit_parts.py` (materiales con manifiesto, primitivas, texto liviano, unión y exportación); `build_street_kit.py` pasó a usarlas y su salida quedó idéntica.
- Kit nuevo `City25~/build_district_kit.py` → `Art/City/Kit25/District/*.fbx`, `district_kit.json`, `district_materials.json`, capturas `renders/district_kit_*.png`: antejardines de tres estilos (madera, reja sobre muro, seto) para los tres anchos de casa, con portón abierto, canteros con flores y camino; muro del escondite (portón corredizo cerrado, puerta peatonal abierta, cámara, timbre, número); cerca de malla de galpón que deja libres sus portones y su puerta; contenedores marítimos de tres colores, pallets, tambores, grúa horquilla, neumáticos, chatarra; pizarras de oferta; letreros de Don Trueque, Taller de pintura y Garaje Express; gasolinera completa Petro Villa (techo, islas con surtidores, tienda 24 h, tótem de precios) y estacionamiento (caseta, barreras, topes, muros con seto, letrero P).
- Plano (`city_objects.py`, `district_details`): 909 antejardines en casas residenciales y de las afueras, muro del escondite, 75 cercas de galpón, patios industriales (contenedores al costado, pallets, tambores y grúas al frente), reducidor y talleres con letrero, 49 pizarras frente a comercios, 3 gasolineras con dos autos cargando y 2 estacionamientos con modelo. Los detalles usan su propia secuencia aleatoria: la elección de edificios no cambió. El techo plano viejo de la gasolinera se quitó del suelo (`build_ground.py`).
- Verificación independiente: 0 piezas en la calzada, la vereda, la franja peatonal o dentro de fachadas; el detalle de calle sigue sin problemas.
- Unity: `City25Kit.Manifest()` lee los tres manifiestos; colisión con la forma real en cercas, letreros, gasolinera, estacionamiento, grúa y chatarra.
- Corrección pedida por Alain (capturas del escondite: «no está completo», no se podía entrar a la casa ni salir por la puerta, mejor cerrada y con animación): el muro suelto `Yard_Escondite` se reemplazó por un modelo propio `Local_Escondite` (`Art/BlenderScripts/build_hideout.py` → `Art/City/Shops/Local_Escondite.fbx`, `hideout_materials.json`, capturas `Art/Previews~/escondite_*.png`). Casa enterable con interior (mesa de planificación con el mapa, tablero «El golpe», casilleros, herramientas, dinero y caja fuerte, puesto del hacker, sala, cocina, disfraces) y patio con muro completo por los cuatro lados. La puerta de la casa y el portón peatonal están cerrados y se abren con E y el gesto de empujar (`ShopDoor`); el portón del auto se corre de lado con E (`ReviewSlidingDoor` ahora acepta un recorrido lateral). El juego empieza dentro del recibidor. Unity registra todas las puertas de los lugares; la prueba de aceptación mide la casa («Edificio») sin el patio. El muro anterior se movió a `Atraco3D_Retirado/2026-11-04/`.

## Equipo nuevo, Blender MCP y arte con IA gratuita — 2026-11-03

- Proyecto clonado desde GitHub en `C:\Users\Alain\ATRACO-3D`; el equipo anterior (`C:\Users\Alain\Atraco3D`) ya no está disponible. Los `.blend`, los FBX/PNG de carpetas `~` y `Generated/` no estaban en Git y se perdieron: la escena `Atraco.unity` tiene referencias rotas y «Crear y probar juego» no puede preparar R9. Alain decidió rehacer el arte antes de Task 02.
- Blender 4.5.10 LTS y servidor `mcp-for-blender==2.2.6` registrados en `.mcp.json` (telemetría desactivada). Solo Hyper3D Rodin activo con la clave de prueba; el resto de integraciones apagadas. Detalle en `Assets/Party/Art/README.md`.
- El ingeniero autorizó usar **planes gratuitos de IA generativa 3D** (Rodin, Meshy, Tripo) para crear los modelos. Esto amplía la regla de modelos hechos solo con Blender por MCP. Sigue prohibido descargar modelos o texturas ya hechos de bibliotecas. Cada modelo generado se limpia en Blender (low poly, colores planos, 1 unidad = 1 m) y se registra con su licencia en `docs/LICENSES.md`.
- Task 03: puente comprobado con `Art/Validation/ConnectionCube_MCP.fbx` (1 × 1 × 1 m en Blender y en Unity) y captura `docs/Capturas/Task03_ConnectionCube_MCP.png`. Alain confirmó la prueba el 2026-11-03; Task 03 completada.

## Dos copias del proyecto — 2026-11-04

- El commit `task-03` (Blender por MCP, cubo de validación, `.mcp.json`) se hizo en una copia en `C:\Users\Alain\ATRACO-3D`. El trabajo de la ciudad siguió en `C:\Users\Alain\Atraco3D`, que sí conserva los `.blend`, el kit y la ciudad de 2 × 2 km (commits avance-r10 a avance-r12); ahí «Crear y probar juego» funciona y se usa Blender 5.2.
- Las carpetas `~` y `Generated/` siguen fuera de Git: en otra copia faltan esos binarios hasta regenerarlos con los scripts de `Art/BlenderScripts`.


## Respaldo completo y limpieza autorizada — 2026-11-04

Alain pidió respaldar en GitHub el proyecto guardado, incluidos `.blend` y escena vigente, y retirar obsoletos. Confirmó guardado/cierre de Unity y autorizó expresamente los 301 archivos de `Assets/Party/Tools~/cleanup-manifest.json`. Se retiraron tras verificar copia recuperable local; ninguna de las 891 dependencias transitivas de la escena actual se elimina. Se conservan fuentes R9 usadas para regenerar Kit25, los 16 personajes actuales, armas, herramientas y diseños únicos útiles.
- Respaldo vigente: `Generated/Ciudad2km`, fuentes Blender, modelos, `.meta`, capturas, datos y configuración. Solo el `.blend` R9 de más de 100 MiB se restaura desde su ZIP íntegro fragmentado en partes de 48 MiB; el resto se guarda directamente. Herramientas en `Assets/Party/Tools~`, instrucciones en README y `docs/RESPALDO-Y-LIMPIEZA.md`.
- `City25Builder` compara contenido SHA-256 en lugar de fechas para que el clon reutilice la escena guardada; BuildReport migrado sin editar la escena. Build Settings apunta a Ciudad_2km. Recetas comunes con rutas relativas al proyecto.
- Esta solicitud autoriza el commit y la publicación del mantenimiento de respaldo; no aprueba B1 ni cierra tareas de juego. Mantener Unity 6000.3.27f2 y ciudad de 2 × 2 km. Play sigue reservado a Alain.


## Corrección de guarida B1 — 2026-11-04 (pendiente de prueba)

Alain reportó aparición sobre la losa y pidió corregir interior/muebles. Confirmó guardar y cerrar Unity. Motor y aceptación comparten sonda corta cerca de pies y cápsula libre; Awake recupera punto guardado de respawn. Modelo con PlayerSpawn dentro del recibidor y cámara orientada al interior. Constructor ciudad25-18 exige el marcador y reconstruirá una vez con Alarma/Crear y probar juego. Escena guardada: solo se ajustan posiciones iniciales de jugador y cámara.
Soportes de monitores/TV, patas de sillas, cojines, mesa baja, casilleros, dinero/bolsos, cocina y perchas corregidos. Puerta deja margen bajo dintel; detalles pequeños sin collider. Generado por Blender MCP 5.2.3; FBX reimportado (363 mallas, 13.392 triángulos) y viewport revisado. 18 pruebas analíticas y compilación runtime/editor superadas; no son PhysX ni Play. Guía: docs/Guarida-B1-Correccion.md; evidencia en Art/BlenderScripts/HideoutB1Fix~. Mantener Unity 6000.3.27f2 y ciudad de 2 × 2 km. No cerrar B1, avanzar a B2 ni hacer commit/publicación hasta prueba y confirmación de Alain.


## Corrección de recuperación B1 — revisión 19 (pendiente de prueba)

Alain reportó Parent directory must exist al crear Car_Sedan_Alarma_Trim.asset y escena Untitled sin cámara. Editor.log confirma error MakeParked y cierre de última escena en catch. Alain cerró Unity. Se recuperaron 538 archivos Generated faltantes desde Git, reaplicando las posiciones B1 (SHA-256 de escena 5920f16cb8bb45c6b84aa2c851a3d3d2047d8e30ff861fc64a30f87046f4606d); no se sobrescribieron archivos existentes ni se revirtieron materiales escritos por Unity. EnsureFolder registra/verifica carpetas mediante AssetDatabase.CreateFolder y se comprueban los padres antes de crear mallas/materiales/prefabs. City25BuildRecovery conserva copia exacta de salida y metadatos fuera de Assets, recupera antes de restaurar escenas y nunca cierra la última ni borra salida por un error anterior a mutación. Constructor ciudad25-19. Guía actualizada en docs/Guarida-B1-Correccion.md. Sin abrir Unity ni Play; no cerrar B1, avanzar ni hacer commit hasta confirmación.

## Corrección de aceras y acceso B1 — revisión 20 (pendiente de prueba)

Alain probó la revisión 19 y observó peatones atravesando muros y un portón que impedía salir. La revisión 20 recalcula rutas de acera y cruces, valida geometría al construir y comprueba obstáculos en movimiento. La puerta abatible espera contacto de la palma antes de girar y espacio libre antes de cerrar. El exterior de la guarida se ajusta con sendero continuo, poste de lámpara, portón y jardinera. Copia verificada de la ciudad 19 en `Library/Alarma/City25Recovery/AntesRevision20-CiudadGuardada19.zip`. Pruebas y archivos en `Assets/Party/docs/Guarida-B1-Correccion.md`. Pendientes reconstrucción y Play por Alain dentro de B1.

## Corrección B1 de cruces, visitas y garaje — revisión 21 (pendiente de prueba)

Alain probó la revisión 20 y reportó grupos inmóviles en las esquinas. Solicitó visitas de peatones a tiendas y bancos y un garaje en el acceso vehicular. La revisión 21 introduce alternativas ante cruces ocupados y une el paseo, la compra o retiro y el regreso a la acera en el mismo peatón. Garaje cubierto con persiana enrollable. Copia local verificada de la ciudad 20. Procedimiento y resultados en `Assets/Party/docs/Guarida-B1-Correccion.md`.

## Recuperación de la reconstrucción B1 — revisión 22 (pendiente de prueba)

La revisión 21 falló al retirar la carpeta generada y dejó una ciudad parcial. Alain cerró Unity. Se repusieron 534 archivos de la copia de revisión 20 y se verificaron los 538. El constructor 22 usa carpetas independientes para cada intento y publica el informe tras guardar e importar la nueva escena. Pendientes reconstrucción y Play por Alain. Pruebas en `Assets/Party/docs/Guarida-B1-Correccion.md`.

## Clientes en locales y llegada con mapa B1 — revisión 23 (pendiente de prueba)

Alain probó la revisión 22: al llegar con M al supermercado, al banco o a la joyería no había peatones y nadie entraba. Causas: tras el viaje los peatones solo reaparecían a más de 30 m y poco a poco, y cada local admitía un solo cliente con búsqueda de 32 m. La revisión 23 repuebla al instante tras un salto de más de 40 m. Mantiene hasta tres clientes por local a menos de 85 m: uno empieza en la puerta y otro llega caminando por su acera. Libera paseantes lejanos si el cupo está lleno. Solo cambian scripts de Street; no hace falta reconstruir la ciudad. Compilación contra Unity 6000.3.27f2 y 50 pruebas superadas; Play pendiente de Alain. Guía: `Assets/Party/docs/Guarida-B1-Correccion.md`. No cerrar B1 ni hacer commit hasta su confirmación.

## Banco rediseñado y personal en locales B1 — revisión 24 (pendiente de aprobación visual y prueba)

Alain pidió empleados en todos los negocios y diseños menos básicos, empezando por el banco. El banco nuevo se basa en referencias de sucursales reales: ventanillas con vidrio al fondo, zona de personal con bóveda, recepción, turnos, cajeros automáticos aparte, asesores, gerencia y sala de espera. Tiene 8 empleados con uniforme (4 cajeros, 2 asesores sentados, gerente y recepcionista). Los puestos se declaran en `shop_layouts.json` y los coloca `City25Staff`. Constructor `ciudad25-24`. Capturas en `Art/Previews~/local_banco_*.png`. Pendientes: aprobación visual de Alain, reconstrucción y Play. Después, mismo criterio en joyería, supermercado, minimarket, comida y ropa. Guía: `Assets/Party/docs/Guarida-B1-Correccion.md`.

## Joyería rediseñada con personal B1 — revisión 25 (pendiente de aprobación visual y prueba)

Alain aprobó el diseño del banco. La joyería sigue las referencias: circuito de vitrinas con el vendedor detrás, mostrador con taburetes y nichos iluminados al fondo, dos islas, lámpara de araña, escaparates, espera y zona de personal. Tiene 4 empleados con uniforme (cajera, asesora y dos vendedores). Capturas en `Art/Previews~/local_joyeria_*.png`. Pendientes: aprobación visual, reconstrucción y Play. Después siguen supermercado, minimarket, comida y ropa.

## Supermercado rediseñado con personal B1 — revisión 26 (pendiente de aprobación visual y prueba)

Alain aprobó la joyería. El supermercado sigue las referencias: verdulería en la entrada, cuatro pasillos con ofertas, refrigerados al fondo y a la derecha, carnicería y panadería, y tres cajas junto a la salida. Tiene 6 empleados (tres cajeros, reponedor, carnicero y panadera). Son 177.320 triángulos frente a 132.408 antes, por las estanterías existentes; medir con el Profiler en Play. Capturas en `Art/Previews~/local_supermercado_*.png`. Pendientes: aprobación, reconstrucción y Play. Faltan minimarket, comida y ropa.

## Minimarket, comida y ropa rediseñados con personal B1 — revisión 27 (pendiente de aprobación visual y prueba)

Alain aprobó el supermercado. Los tres locales restantes siguen sus referencias:

- **Minimarket:** caja en la entrada, café, bebidas frías y comida caliente.
- **Comida:** mostrador con cocina abierta, retiro, bebidas y reservados, mesa comunitaria y mesas de dos.
- **Ropa:** vidrieras, mesa de entrada, caja a la izquierda, pared derecha de prendas, percheros y probadores.

Los seis tipos tienen personal: 22 cajeros y 76 empleados más en la ciudad. Pendientes: aprobación visual, reconstrucción, Play y Profiler. Guía: `Assets/Party/docs/Guarida-B1-Correccion.md`.

**2026-11-05:** Alain aprobó visualmente los seis locales (revisiones 24 a 27). Pendiente: reconstrucción y Play en Unity de las revisiones 23 a 27, y Profiler. Sin commit hasta su confirmación.


## Venta realista, personal trabajando y clientes que deciden B1 — revisión 28 (pendiente de prueba)

Guion del mostrador compartido por cliente y cajero: producto del estante al mostrador, escaneo, billetes de mano en mano y vuelto. El banco usa número y efectivo por la bandeja. El personal trabaja entre clientes según su rol. Los clientes miran puestos ajenos y el 75 % compra. Hasta 5 clientes por local (sin superar sus puestos), cada 2–5 s. Constructor `ciudad25-28`. 61 pruebas y compilación contra Unity; Play pendiente de Alain. Guía: `Assets/Party/docs/Guarida-B1-Correccion.md`.

## Puertas, locales en marcha y bolsa B1 — revisión 29 (pendiente de prueba)

Alain reportó que las puertas no abrían, que los clientes esperaban afuera, que al llegar con M no había gente comprando y que la bolsa salía en la espalda. Ahora las personas ya no bloquean el giro de la hoja, las alfombras no tienen collider y el revestimiento se separa de la bisagra (seis locales regenerados con planos idénticos). Al llegar, los locales cercanos ya tienen clientes dentro, uno en la puerta y otro en camino. La bolsa queda fija en la mano. Constructor `ciudad25-29`, 63 pruebas y compilación; Play pendiente.

## Task 06, entrega 1: inventario local — 2026-11-05 (confirmada por Alain el 2026-11-06)

- Corrección posterior de brazos/manos solicitada por Alain: conservar el giro importado del FBX, resolver la muñeca sin desplazar el agarre, calibrar la palma con los nudillos y flexionar dedos. Equipar/guardar y cambio de rol ajustados. 14 pruebas matemáticas y compilación de cinco asambleas superadas; ocho poses de pistola revisadas en Blender. Pasos y lista de archivos en `Assets/Party/docs/Task06-Agarre-Corregido.md`. Sigue pendiente Play y aprobación; no cerrar esta tarea.

- Pedido de Alain: inventario con 5 espacios abajo del personaje, elegidos con 1 a 5, con todas las armas y herramientas para robar los locales. Se divide en: entrega 1 (inventario, barra, mochila y objeto en la mano) y entrega 2 (usar cada herramienta en los locales: caja registradora, vitrinas, caja fuerte, bóveda, cámaras, bridas). La sincronización en red llega con Task 02.
- `Scripts/Player/Items` (Alarma.Player): `ItemDefinition` (ScriptableObject por objeto: tipo, nivel del GDD, pila, ícono, modelo y ajuste en la mano), `InventoryRules` (barra del GDD 8.2: arma, herramienta, herramienta, consumible, libre; mochila de 20), `StartingLoadout`, `Inventory` (modelo sin escena con eventos), `PlayerInventory`, `HeldItemView` (objeto en la palma, punto `Grip_R` de las armas) e `IHandAnchor`.
- `Scripts/UI/Hud` (Alarma.UI): `HotbarView` (barra abajo al centro con tecla, ícono, cantidad y nombre al cambiar), `InventoryScreen` (Tab: mochila 5 × 4, barra y ficha; clic para equipar o devolver, respeta los tipos) e `ItemSlotWidget`.
- Prueba: `ReviewInput` lee 1–5, rueda y Tab; `ReviewInventoryControls`; `ReviewCharacterView` es la mano; `ReviewInterface` coordina Tab con el mapa y la pausa; el aviso de puertas sube sobre la barra.
- Datos: `Scripts/Player/Editor/ItemAssets.cs` crea una sola vez `Party/Data/Items` (15 objetos del GDD sin la porra de los guardias, reglas y equipo inicial con todo en la mochila y la barra pistola, palanca, ganzúa, bridas, taladro). Íconos de `Art/BlenderScripts/build_item_icons.py` → `Art/UI/Items`.
- Pruebas automáticas: `Tests/EditMode/Player/InventoryTests.cs` (tipos por espacio, intercambio, pilas, devolver, rueda).
- Corrección pedida por Alain (captura: pistola enorme flotando al costado, sin pose ni animación): las armas y herramientas se rehicieron a escala real en `Art/BlenderScripts/build_weapons.py` (pistola 19 cm, escopeta 1,05 m, rifle 0,95 m, granadas 12 cm), con más detalle y puntos `Grip_R`/`Grip_L`/`MuzzlePoint` en el lado correcto. `HeldItemView` ya no pega el objeto a la mano: lo ubica frente al pecho según su forma de sostener (`HoldStyle` en cada objeto y `HoldPoseLibrary` en `Data/Items/HoldPoses.asset`, ajustable en el Inspector) y lleva las manos con IK de dos huesos (`TwoBoneIk`), con los dedos rodeando la empuñadura. Pistola y taladro en guardia baja con dos manos, escopeta y rifle con el guardamanos, tablet y termita con dos manos, el resto en una mano. Se balancea al caminar, baja el arma al correr y la saca desde la cadera al cambiar. `ReviewCharacterView` da los huesos (`ICharacterRig`) y crea la palma izquierda; `RigBones` suma pecho y brazo izquierdo. Revisión en Blender con el elenco real: `preview_hold_poses.py` → `Previews~/sostener_*.png` (todas las manos llegan a su agarre).
- Corrección (captura de Alain: nada en la mano): la escena abierta era de una preparación anterior al cambio de código, y sus componentes no tenían los campos nuevos. Ahora «Crear y probar juego» vuelve a preparar la escena cuando cambia el código del jugador, del inventario o de la interfaz (`City25Builder.Stamp` suma esos scripts), y `HeldItemView` avisa en Console si le falta configuración.

## Task 06, entrega 2: guardar, apuntar, disparar y usar herramientas — 2026-11-05 (confirmada por Alain el 2026-11-06; la sincronización en red de Task 06 sigue pendiente de Task 02)

- Pedido de Alain: la misma tecla guarda el arma; clic derecho apunta; disparo con animación; cada herramienta con su función y su animación.
- Guardar: `Inventory.Select` sobre el espacio ya elegido alterna guardado/sacado (`Holstered`, `ActiveStack`); la rueda saca el objeto; `ConsumeActive` gasta granadas, bridas y termita. La barra muestra el espacio guardado apagado y «(guardada)».
- Acciones (patrón Strategy con ScriptableObjects, `Scripts/Player/Items/Actions`): `ItemAction` (duración, momento del efecto, repetir al mantener, curvas de animación, vibración y pieza que gira), `FirearmAction` (dispersión menor al apuntar, fogonazo, trazador, impacto, daño por `IDamageable`, perdigones y corredera de la escopeta, dardo del táser), `ThrowAction` (humo, aturdidora, EMP), `PlaceChargeAction` (termita con mecha y chispas) y `ToolAction` (palanca, ganzúa, taladro con broca que gira, cortavidrios, tablet, bridas, gancho con cuerda). `ItemEffects` dibuja los efectos. Nuevo contrato `Core/Contracts/IItemTarget` para lo que responde a cada objeto (cajas, vitrinas, cámaras, cerraduras, personas).
- `ItemUser`: clic derecho apunta (sube el arma a los ojos e inclina con la cámara; apuntarle a alguien inicia `IIntimidatable`), clic izquierdo dispara o usa y reproduce la acción sobre la pose de `HeldItemView`. Pose de apuntar en `HoldPoseLibrary` (el asset existente se completa sin tocar lo ajustado).
- Prueba: `ReviewInput` da los clics (`IItemControls`); `ReviewCamera` pasa sobre el hombro y cierra el campo de visión al apuntar; `ReviewPlayerMotor` mira hacia la mira y camina más despacio; `CrosshairView` con la mira; los avisos salen sobre la barra.
- Datos: `Player/Editor/ItemActionAssets.cs` crea una vez `Party/Data/Items/Actions/Action_<objeto>.asset` y los asigna a cada objeto. Pruebas nuevas: guardar/sacar y gastar.
- Pendiente para robar de verdad: que las cajas registradoras, vitrinas, cajas fuertes, bóveda, cámaras, cerraduras y empleados implementen `IItemTarget` (siguiente entrega). Munición, recarga y sonidos todavía no.
- Corrección (captura de Alain: mira visible sin apuntar): `CrosshairView` solo aparece mientras se mantiene clic derecho con un arma.
- Corrección (captura de Alain: marcas de bala flotando en el aire, y animaciones pobres de los demás objetos):
  - Impactos: la marca queda pegada a la superficie que recibió el tiro (si es una puerta o un auto, se mueve con ella). Sobre personas no queda marca: solo el polvo, que se desvanece enseguida (`FirearmAction`, `ItemEffects.Impact`).
  - Cuerpo en las acciones: `HeldItemView` inclina y gira el torso desde el abdomen (`ICharacterRig.Spine`) y lleva la mano izquierda a `Grip_L` cuando la acción lo pide (`ActionPose.Lean` y `LeftHand`; curvas `leanForward`, `leanTwist`, `leanSide` y `leftHand`).
  - Animaciones nuevas en un solo archivo de datos, `Data/Items/item_actions.json`, generado por `Art/BlenderScripts/make_item_actions.py`. `ItemActionAssets` crea o pone al día los `Action_<objeto>.asset` cuando sube la versión (ahora 2), sin pisar ajustes hechos a mano mientras no cambie. Palanca: la clava al frente con las dos manos y hace palanca dos veces girando el cuerpo. Ganzúa: inclinado, la izquierda sostiene la llave de tensión y la derecha tantea hasta girar. Taladro: se apoya y empuja con las dos manos. Cortavidrios: inclinado sobre la vitrina, la izquierda en la ventosa y la derecha traza el círculo. Tablet: la acerca, teclea y el código de la pantalla parpadea (`blinkPart`). Bridas: se inclina, pasa el lazo con las dos manos y tira. Gancho: la izquierda lleva la cuerda, lo hace girar y lo lanza. Granadas: la izquierda saca la anilla, el brazo va atrás con el torso girado y la lanza. Termita: se inclina y la aprieta contra la puerta. Las armas suman un leve retroceso del torso.
  - Modelos: `build_weapons.py` agrega `Grip_L` a palanca, ganzúa (con llave de tensión doblada), cortavidrios (con lengüeta en la ventosa), bridas, gancho y granadas.
  - Revisión cuadro a cuadro en Blender con el elenco real y los mismos datos del juego: `preview_item_actions.py` → `Art/Previews~/acciones/<objeto>.png` (tres cuartos y costado) e `informe.json` (las manos quedan a 7 cm o menos de su agarre en todos los cuadros).
  - «Crear y probar juego» vuelve a preparar la escena también cuando cambia `item_actions.json`.
- Cambio pedido por Alain («plan mixto»: animaciones hechas con Blender u otras fuentes, no solo curvas por código):
  - Revisión: las curvas solo pesaban 17 KB, pero movían brazos, torso y muñeca, sin piernas ni cabeza. Además el código movía los huesos sin pasar por el Animator, y CLAUDE.md pide Animator con capas, un componente dedicado y NetworkAnimator. El pack CC0 del elenco (Quaternius Ultimate Modular) trae 24 clips, pero ninguno sirve para lanzar, agacharse o forzar cerraduras.
  - Clips propios con bpy (`Art/BlenderScripts/build_action_clips.py`) sobre el mismo esqueleto del pack (Men y Women). Reimportar el FBX del elenco cambiaba la orientación de casi todos los huesos, así que no sirve de base. Cada cuadro usa los datos del juego y suma lo que antes faltaba: cadera que baja con rodillas dobladas y pies fijos (IK), cabeza que mira el trabajo y brazo izquierdo libre en las granadas (apunta y equilibra). Hay 11 clips: palanca, ganzúa (agachado), taladro, cortavidrios, tablet, bridas, gancho, tres granadas y termita (agachado frente a la puerta). Salida: `Art/Characters/Animations/Alarma_ItemActions_Men.fbx` (3,5 MB), `_Women.fbx` (4,2 MB) e `item_action_clips.json` (qué esqueleto usa cada personaje). Las armas de fuego siguen con su retroceso por código.
  - Datos (`make_item_actions.py`, versión 3): `clip`, `fullBody` y `animationId` por acción, más las curvas que solo usa el clip (`crouch`, `headPitch`, `headTurn` y la mano izquierda libre).
  - Unity: `ItemActionAnimatorAssets` (editor) copia cada clip con la ruta de huesos de cada rol (`<id>_Rig`), solo con giros y la altura del cuerpo, y agrega al Animator los parámetros `Usando`/`Accion` y dos capas: «Acciones torso» (máscara desde el abdomen, se puede caminar: tablet y granadas) y «Acciones cuerpo» (el resto, el jugador se queda quieto mientras dura). `Alarma.Animation.ItemActionAnimator` es el único componente que cambia esos parámetros y los pesos de capa, a partir del evento `ItemUser.ActionChanged`. Así NetworkAnimator podrá sincronizarlos en Task 02.
  - Con clip, `HeldItemView` ya no inclina la columna por código (lo hace el clip). El objeto sigue el mismo recorrido y las manos lo toman con IK. `ICharacterAnimator` da el Animator del cuerpo; `ReviewPlayerMotor.HoldStill` frena al jugador en las acciones de cuerpo completo.
  - Revisión en Blender del archivo exportado (lo mismo que recibe Unity), sobre el personaje real: `preview_item_actions.py` → `Art/Previews~/acciones/`. El clip «Reposo» coincide exactamente con el reposo del elenco (diferencia 0,0), y las manos quedan a 7 cm o menos de su agarre.
  - «Crear y probar juego» vuelve a preparar la escena cuando cambian los clips o su lista.
- Corrección (captura de Alain: pose de bridas rígida, «animaciones más realistas»): los clips ahora tienen mecánica de cuerpo, no solo pose.
  - La inclinación se reparte entre cadera, abdomen, torso y pecho (antes se doblaba en un solo punto). La cadera va atrás para equilibrar el peso y los hombros acompañan al brazo. Hay respiración y un leve vaivén de peso en los clips que no se repiten.
  - Pies: en este esqueleto cuelgan de `Root`, así que se mueven solos y las piernas llegan a ellos con IK, con las rodillas hacia la punta del pie. Curvas nuevas: `kneel` (rodilla derecha al piso: ganzúa y termita) y `step` (pie izquierdo adelante: palanca, taladro, cortavidrios, bridas y gancho). Las bridas se doblan desde la cadera. Datos versión 4.
  - Unity copia también la posición de los pies (`ItemActionAnimatorAssets.Moved`: Body, Foot.L y Foot.R).
- Corrección (Alain: «la animación para amarrar no tiene sentido»): las bridas ahora son un amarre por detrás.
  - El ladrón apoya la rodilla derecha detrás de una persona arrodillada con las manos en la espalda. La izquierda le junta las muñecas, la derecha pasa el lazo alrededor, tira fuerte para cerrarlo (momento del efecto, 1,6 s de 2,2) y se levanta. Medido en Blender con un rehén de prueba: las manos quedan a unos 5 cm de sus muñecas.
  - Solo empieza si hay alguien que acepte las bridas al frente (`ToolAction.requireTarget` y `ItemAction.CanBegin`); si no, avisa y no se mueve. Mientras no existan rehenes (Task 13), en el juego solo aparece el aviso.
  - Para Task 13: el rehén amarrable queda arrodillado con las dos rodillas, las manos en la espalda sobre la cintura, y el jugador se coloca 0,62 m detrás, mirando hacia el mismo lado (como en `preview_item_actions.py`, `PARTNER_DISTANCE`).
  - Curvas: el suavizado de Unity (`SmoothTangents`) se pasaba de largo en los tramos quietos; la cadera de la ganzúa, que debía bajar 40 cm, llegaba a 62. Ahora `ItemActionAssets` y la revisión de Blender usan la misma tangente que no se pasa (plana en picos y tramos quietos). Afecta y mejora todas las acciones. Datos versión 5.
