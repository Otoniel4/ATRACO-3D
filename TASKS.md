# TASKS.md — Plan de desarrollo de "Alarma"

Reglas: una task a la vez y en orden. Nunca se salta de una task a otra sin la confirmación de Alain. Una task solo se marca `[x]` cuando Alain la probó y funciona. Cada task se cierra con su commit.

Formato de cada task: **Objetivo** · **Patrones / SOLID** · **El agente hace** · **Alain hace** · **Criterios de aceptación**.

Hitos: al terminar cada bloque marcado como **HITO**, se hace una prueba completa con 2 jugadores antes de seguir.

---

# BLOQUE A — Base técnica

## [x] Task 00 — Entorno y verificación
- **Objetivo:** entorno listo antes de escribir código del juego.
- **El agente hace:** verificar RTK (`rtk gain`) y Caveman; revisar `Packages/manifest.json` y listar paquetes faltantes (AI Navigation, Cloud Save, Timeline); verificar `.gitignore` de Unity e inicializar Git; confirmar con Alain la ubicación de `Party/`.
- **Alain hace:** instalar los paquetes faltantes; activar Relay, Lobby y Cloud Save en Unity Cloud.
- **Criterios:** herramientas activas, paquetes instalados, Git listo, carpeta `Party/` confirmada.

## [ ] Task 01 — Arquitectura base
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

## [ ] Task 03 — Conexión Codex ↔ Blender (MCP)
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
