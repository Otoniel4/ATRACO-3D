# Alarma — Integración y revisión del GDD

Fecha: 31 de octubre de 2026.

## Referencia de diseño y entorno confirmado

Se leyeron las 18 páginas del PDF entregado por Alain y se revisaron visualmente las páginas y tablas. El original se conserva sin cambios. La copia de referencia del proyecto es `C:\Users\Alain\Atraco3D\Assets\Party\docs\GDD.pdf`.

Por instrucción expresa de Alain, el proyecto mantiene Unity **6000.3.27f2**. La versión `6000.5.8f1` y el estado de paquetes de la sección 12.1 del PDF describen un entorno anterior; no justifican migrar este proyecto. La configuración actual del proyecto prevalece para versiones y dependencias, y el GDD prevalece para el diseño de juego.

## Requisitos identificados

- PC Windows, tercera persona, URP y cooperación online de **1 a 4 jugadores**.
- Bucle: planificar, robar, huir, vender y mejorar. Botín y dinero son conceptos distintos; el dinero pertenece a la banda.
- Modelo host-cliente: el host controla NPC, alerta, búsqueda, economía e interacciones compartidas. Cada jugador controla su movimiento; el conductor controla el vehículo.
- Guardado en la cuenta del host al volver al escondite: dinero, equipo, mejoras, disfraces y estado de los locales.
- Nadie muere: derribo, rescate durante 5 segundos y arresto tras 30 segundos o contacto policial.
- Ciudad configurable de 6 por 6 cuadras, tráfico, peatones, semáforos, interiores y rutas de escape.
- Arte propio low-poly, scripts de Blender conservados, rig y animaciones Humanoid, licencias registradas para recursos externos permitidos.
- Fases progresivas con pruebas de dos jugadores antes de ampliar el alcance.

## Diferencias con TASKS.md

| Tema | GDD | Plan de tareas actual | Tratamiento |
| --- | --- | --- | --- |
| Intimidación | Sección 4.3: mientras se apunta al NPC, se agacha y no llama; al dejar de apuntar recupera valentía y puede huir o llamar. | Task 13 permite huir al apuntarle. | Al abordar Task 13, ajustar sus criterios al GDD. No introducir huida mientras permanezca intimidado de forma efectiva. |
| Caja fuerte | Sección 4.5: código aleatorio o taladro lento y ruidoso. La palanca se usa en cerraduras. | Task 17 permite abrir la caja fuerte con palanca. | Al abordar Task 17, usar el GDD como referencia y preparar el taladro y sus datos. |
| Alcance de fases | Sección 2 separa núcleo, ciudad viva, golpes mayores y extras. | Task 34 habla de una versión completa, pero el plan no cubre explícitamente todo el GDD. | No interpretar Task 34 como cobertura automática de todo el diseño. Mantener el orden actual y revisar alcance antes de ampliar el plan. |
| Versión y paquetes | Sección 12.1 indica `6000.5.8f1` y una lista histórica. | Los documentos de instrucciones repiten esa lista. | Corregidos los datos de entorno en AGENTS.md y CLAUDE.md. Se conserva `6000.3.27f2`. |

`TASKS.md` conserva sus tareas y casillas sin cambios. Las correcciones de comportamiento se documentan aquí para revisarlas al llegar a la tarea correspondiente; no se han implementado sistemas futuros.

## Requisitos sin tarea explícita o con cobertura parcial

La lectura identifica puntos que deberán asignarse a tareas antes de considerar completo todo el GDD:

- Roles, pasivas, habilidades Z/X, selección de rol y marcado Q.
- Ciclo de día/noche y variantes del atraco según el horario.
- Radio de guardias con límite de dos respuestas, botones de pánico y cierre automático de puertas por alarma.
- Armadura, penalización por disparar a civiles, reglas de los cinco espacios del inventario y diferencias del rol Músculo.
- Seguridad adaptativa de los locales, progresión persistente de esa seguridad y consecuencias de testigos que escapan grabando.
- Barricadas, helicóptero, camión blindado, compra de información, taller de pintura y mejoras detalladas del escondite.
- Accesos especiales, minijuego de ganzúa, herramientas avanzadas y bóveda de dos llaves o termita para solitario.

Estos puntos son revisión de cobertura, no autorización para saltar tareas ni promesa de implementación dentro de la actual Task 00.

## Diseño de escape — propuesto y aceptado por Alain el 2026-11-09

Amplía Tasks 05, 11, 27 y 28. Es diseño, no implementación: cada parte se construye al llegar a su task. Los números son valores de partida y van en ScriptableObjects para ajustarlos jugando.

**Regla central.** La policía busca una **descripción** (ropa y auto) y la **última posición vista**, no al jugador directamente.

**Estados de la búsqueda (host).**
1. **Visto:** un policía tiene línea de visión. El radar parpadea en rojo. Ningún truco de escape funciona.
2. **Búsqueda:** se rompió la línea de visión. Círculo en la última posición vista, conos de visión de cada policía y contador.
3. **Libre:** el contador llega a cero sin ser visto.

**Formas de escapar (solo fuera de la vista).**
- Salir del círculo evitando los conos.
- Cambiar de ropa en la tienda de ropa: cuesta dinero, borra la descripción y acelera el contador.
- Maniquí: pose en la vitrina; si un policía pasa a menos de 2 m hay que mantener una tecla para no moverse.
- Hacerse pasar por cliente: caminar, hacer fila o sentarse en un local; correr o mostrar el arma delata.
- Cambiar de auto o guardarlo en el garaje de la guarida.
- Esconderse en contenedores, callejones o la guarida.
- Rehén como escudo: la policía no dispara, el jugador camina lento.
- Señuelo en equipo: un compañero atrae a la policía, otro espera con el auto, otro aturde al policía que está esposando.
- Cortar el aviso: el testigo que graba tiene una barra de llamada que se interrumpe intimidándolo; romper las cámaras antes del robo retrasa la respuesta.
- Alcantarillas: **en duda por Alain**. No construir hasta que lo confirme; los callejones y la guarida cubren ese papel.

**Resistencia.** Unos 8 s de carrera, recuperación en unos 4 s caminando, lentitud breve al agotarse. La bolsa de botín la gasta más rápido. Los policías también se cansan.

**Arresto.** Policía a 1,5 m durante 2 s con el jugador aturdido o agotado → esposado. Un compañero puede liberarlo antes de que lo suban a la patrulla; si no, cárcel (Task 20). Los disparos de ambos bandos solo aturden; nadie muere, igual que en el GDD.

**Niveles de búsqueda.**

| Nivel | Qué lo provoca | Respuesta |
| --- | --- | --- |
| 1 | Alarma o llamada de testigo | 1 patrulla, 2 policías a pie |
| 2 | Visto armado o con rehén | 2 patrullas, círculo más grande |
| 3 | Aturdir a un policía; robo a joyería | 3 patrullas, cierre de calles cercanas |
| 4 | Robo a banco; huida larga en auto | Patrullas que cortan el paso |
| 5 | Reincidir sin escapar | Toda la zona; el contador casi no baja sin cambiar ropa o auto |

**Puntos a conciliar con el GDD al llegar a cada task.**
- El GDD arresta tras 30 s de derribo o por contacto policial; aquí se añade el arresto por agotamiento o aturdimiento. Revisar en Tasks 18 y 19.
- Task 27 baja el nivel tras 30 s fuera de la vista; aquí el contador depende del nivel y de la descripción. Fijar los tiempos en Task 27.
- El taller de pintura y los disfraces ya figuran en el GDD como cobertura parcial; este diseño los usa para borrar la descripción.

## Decisiones técnicas pendientes para las tareas correspondientes

El GDD no fija el comportamiento cuando el host se desconecta, cuando todos son arrestados sin dinero suficiente para pagar fianzas, ni los límites iniciales de NPC y tráfico. Esas decisiones deberán concretarse al abordar red, economía y rendimiento. No se han asumido migración de host, deuda ni cantidades arbitrarias.

## Estado de Task 00

- GDD recibido e integrado: sí.
- Versión de Unity confirmada: `6000.3.27f2`.
- Carpeta de contenido confirmada: `Assets/Party`.
- RTK, Caveman, repositorio Git y exclusiones: preparados.
- Paquetes instalados y resueltos: Netcode for GameObjects `2.13.3`, Multiplayer Services `2.4.1`, Multiplayer Play Mode `2.0.2`, Cinemachine `3.1.7`, ProBuilder `6.1.4`, Cloud Save `3.4.2` y Authentication `3.8.0`.
- Servicios en Unity Cloud configurados y Console sin errores: confirmado por Alain. No se realizaron aún pruebas autenticadas de red o guardado.
- Task 00 marcada como completada tras la confirmación de Alain y preparada para su commit de cierre. Task 01 no se ha iniciado.

## Pasos y comprobación para Alain

1. Mantén el editor `6000.3.27f2` del proyecto existente.
2. Completa las pruebas descritas en `Assets/Party/docs/TASK-00-Entorno.md`.
3. Comprueba que Unity importe la documentación sin errores y que todos los paquetes requeridos aparezcan instalados.
4. Alain confirmó Console sin errores y los servicios configurados. No hace falta volver a entregar el GDD ni confirmar otra vez la versión.

## Explicación para aprender

El GDD define las reglas del juego y el plan de tareas organiza su construcción. Cuando difieren, conviene registrar la diferencia antes de programarla. Conservar el PDF original permite distinguir el diseño recibido de los ajustes del entorno. Esta actualización es documental: todavía no introduce clases ni patrones de juego. Mantener una referencia clara evita implementar comportamientos incompatibles entre sistemas.
