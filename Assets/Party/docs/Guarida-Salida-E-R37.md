# Guarida: bloqueo al pulsar E — R37

Corrección local del 2026-11-06. Pendiente de prueba de Alain en Unity 6000.3.27f2. No se abrió Unity ni se ejecutó Play. No se modificaron modelos ni escenas para esta corrección.

## Fallo y cambio

El jugador terminaba el acercamiento hasta 7,5 cm antes de su destino. Después comprobaba el alcance usando el marcador para llevar objetos. Ese marcador podía indicar alcance suficiente aunque la muñeca orientada para empujar todavía no llegara a la puerta. El contacto no se confirmaba y la hoja permanecía cerrada.

Ahora primero orienta el cuerpo, alinea el hombro real con la placa y termina el acercamiento a 2,5 cm del destino inicial. Durante el contacto comprueba la posición necesaria de la muñeca, incluida la orientación de la palma; si falta alcance continúa avanzando mediante el mismo CharacterController, conservando las colisiones. La hoja comienza a girar solamente cuando hay contacto. El control vuelve cuando queda paso libre.

Acercamiento, contacto y empuje tienen tiempos separados. Retroceder cancela el gesto inmediatamente. Un fallo libera el movimiento y escribe una sola advertencia con la fase, la distancia de la palma y el obstáculo detectado durante el giro. No se abre la puerta atravesando un obstáculo.

## Archivos de esta corrección

- `Assets/Party/Scripts/City/PlaytestR7/ReviewDoorInteraction.cs`: alineación, alcance real, cancelación y diagnóstico.
- `Assets/Party/Scripts/AI/CityLifeR5/PedestrianReach.cs`: consulta de alcance de muñeca y tolerancia de contacto de superficie de 8 mm; el agarre de compras conserva su tolerancia.
- `Assets/Party/Scripts/AI/CityLifeR5/ShopDoor.cs`: nombre del obstáculo que impide el giro.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/DoorInteractionTests.cs`, `run_interaction_tests.py`, `interaction-results.json`, `interaction-test-results.txt`: pruebas y regresión del alcance antiguo.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorReview36~/ReachRegression.cs`, `reach-code-results.txt`, `install.py`: pruebas de muñeca y actualización del número de comprobaciones exigidas por el instalador anterior. No se volvió a instalar ese lote.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorExit37~/measure_player_exit.py`, `contact-results.json`: medición sobre los cuatro FBX del jugador.
- Este documento, su `.meta` y la nota pendiente en `TASKS.md`.

## Verificación fuera de Unity

- 20 comprobaciones del controlador de interacción, 22 de acercamiento/reservas NPC, 31 de puerta y 96 de brazo: 169 comprobaciones superadas. La física de las pruebas está simulada; no sustituye PhysX en Play.
- La misma prueba falla al sustituir la comprobación nueva por el alcance antiguo del marcador de objetos: reproduce la falta de avance durante Contact.
- Compilación aislada de `Alarma.CityLife` y `Alarma.Playtest` contra las DLL instaladas superada.
- 180 mediciones: cuatro personajes, tres fotogramas de reposo, tres alturas y cinco distancias. A 47,5 cm del plano el error máximo era 6,84 cm; a 35 cm queda en 6,78 mm. Estas medidas verifican alcance geométrico y no garantizan que todas las colisiones de la escena permitan esa posición. La consulta de alcance continúa ajustando hasta el contacto o cancela si encuentra un bloqueo.
- No se estiraron huesos ni se desactivaron colisiones. No se cambió el cierre automático de la puerta.

## Pasos para el editor y cómo probarlo

1. Abre el proyecto, espera a que termine la compilación y pulsa **Alarma → Crear y probar juego**. La huella del código detecta la corrección; no hace falta borrar Generated ni crear otra ciudad a mano.
2. Dentro de la guarida, acércate a la puerta y pulsa **E una vez**. Comprueba el acercamiento, la mano sobre la placa y el giro de la hoja.
3. Avanza con **W** cuando haya paso. Comprueba que sales y la puerta se cierra después de dejar libre el umbral. Repite entrando desde fuera.
4. Repite con **F1–F4**, especialmente Toñito, y prueba **S** durante el acercamiento/contacto: debe cancelar y permitir alejarse.
5. Si vuelve a fallar, copia de Console la línea que empieza con `Alarma: gesto de puerta cancelado`. Indica también el rol y si estabas dentro o fuera. La fase, la distancia y el obstáculo permiten distinguir fallo de alcance de bloqueo físico.

Es una prueba local, sin red. No corresponde Multiplayer Play Mode. B1 sigue pendiente; no se marca completada ni se hace commit de cierre hasta confirmación.

## Explicación para aprender

Al agarrar un objeto y al empujar una puerta la muñeca necesita posiciones diferentes, aunque la mano apunte al mismo sitio. Ahora el cálculo incluye esa orientación. La máquina de estados separa acercamiento, contacto y empuje. El componente de brazo calcula alcance, el motor mueve con colisiones y la puerta controla su giro: cada pieza conserva una responsabilidad.
