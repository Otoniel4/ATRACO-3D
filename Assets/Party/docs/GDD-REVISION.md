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
