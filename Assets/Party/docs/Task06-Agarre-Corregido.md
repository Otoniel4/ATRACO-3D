# Task 06 — corrección de brazos, manos y agarre

Entrega del 5 de noviembre de 2026. Pendiente la aprobación visual y prueba de Alain en Unity 6000.3.27f2. No cierra Task 06 ni implementa disparos o uso de herramientas.

## Problemas encontrados

- `HeldItemView` sobrescribía la rotación de importación del modelo. El FBX de la pistola contiene −90° en X en la raíz para convertir los ejes de Blender. Ahora la pose se aplica sobre la orientación importada.
- Se colocaba la palma y después se giraba la muñeca. Ese último giro desplazaba el punto de contacto, especialmente en la mano de apoyo.
- El código orientaba la mano, pero no flexionaba los huesos de los dedos.
- El marcador `Grip_R6` sirve para la bolsa y estaba cerca de la muñeca. El agarre nuevo se calibra con los nudillos, usando un ancla propia para no alterar las compras ni las puertas.

## Cambios

El IK resuelve brazo y antebrazo hasta la muñeca, descontando la posición de la palma ya orientada. La orientación usa dos ejes anatómicos y los dedos se flexionan por sus articulaciones. El índice derecho queda extendido junto al arma durante la pose de reposo. Ambas manos conservan las longitudes de sus huesos.

El objeto permanece unido al agarre real. Al cambiar de espacio, primero baja el objeto anterior y después equipa el siguiente. Las modificaciones de huesos se restauran antes de la siguiente evaluación de animación. Cambiar de rol reconstruye la calibración y libera las anclas anteriores. El gesto de puerta tiene prioridad sobre el objeto equipado.

## Archivos creados o modificados

- `Assets/Party/Scripts/Player/Items/HeldItemView.cs` — orientación importada, transición de equipar/guardar, coordinación de ambas manos y cambio de rol.
- `Assets/Party/Scripts/Player/Items/HandGripPose.cs` y `.meta` — calibración de palma, orientación de muñeca, flexión y restauración de dedos.
- `Assets/Party/Scripts/Player/Items/TwoBoneIk.cs` — resolución hasta la muñeca con compensación del agarre y protección de direcciones degeneradas.
- `Assets/Party/Scripts/Player/Items/ICharacterRig.cs` y `Assets/Party/Scripts/City/PlaytestR7/ReviewCharacterView.cs` — estado de manos ocupadas por la puerta.
- `Assets/Party/Art/BlenderScripts/HoldGripFix~/preview_grip.py` — revisión sobre los FBX reales de los cuatro protagonistas.
- `Assets/Party/Art/BlenderScripts/HoldGripFix~/GripTests.cs`, `verify_code.py`, resultados y capturas — comprobaciones reproducibles.
- Este documento, `TASKS.md` y `AGENTS.md` — seguimiento pendiente.

No se sustituyeron los modelos ni los clips del elenco. Las poses se aplican sobre la animación existente.

## Verificación

- 14 comprobaciones matemáticas ejecutan `TwoBoneIk` y `HandGripPose` reales con sustitutos de Transform/Quaternion. Detectan el desfase anterior, contacto menor a 1 mm, longitudes conservadas, orientación del arma, restauración sin deriva durante 60 ciclos y liberación de anclas.
- Compilación contra las DLL instaladas: `Alarma.Player`, `Alarma.Playtest`, `Alarma.Player.Editor`, `Alarma.Playtest.Editor` y `Alarma.City.Editor`.
- Blender: ocho poses de pistola (cuatro protagonistas, postura normal y postura con arma baja para correr), con ambos agarres a menos de 1 mm. Esta medida corresponde a las anclas; no certifica ausencia de intersecciones de todas las superficies de piel.
- Capturas revisadas desde frente, costado y mano de apoyo. Son vistas estáticas de Blender sobre la pose Idle, no capturas de Play ni una reproducción de la locomoción.
- Las transiciones, apertura de puertas con arma equipada, herramientas y mezcla con caminar/correr requieren la prueba siguiente. No se abrió el editor de Unity por el agente.

## Pasos para el editor y cómo probar

1. Sal de Play y espera a que Unity termine de compilar.
2. Pulsa **Alarma > Crear y probar juego**. El constructor detecta el cambio en los scripts de jugador y prepara la escena actualizada.
3. Selecciona la pistola con **1**. Gira la cámara para ver las dos manos y comprueba que el arma apunte hacia delante, que los dedos rodeen la empuñadura y que las muñecas no se separen.
4. Camina, corre y detente. Repite el cambio **1 → 2 → 1** y cambia también a un espacio vacío desde el inventario. Comprueba la transición y que las manos vuelvan a la locomoción al guardar.
5. Prueba **F1–F4** con la pistola equipada. Las manos deben reajustarse al nuevo personaje.
6. Abre una puerta con **E** llevando la pistola. Comprueba que el gesto tenga la mano libre y que el agarre se recupere después.
7. Revisa taladro, escopeta, rifle y tablet desde el inventario, especialmente la mano de apoyo. Confirma el resultado antes de cerrar la tarea o hacer commit.

## Explicación para aprender

`HeldItemView` coordina el equipamiento. `HandGripPose` calcula la orientación y flexión de una mano. `TwoBoneIk` resuelve la posición del brazo. Esta separación aplica responsabilidad única. El evento `RigChanged` sigue el patrón Observer y permite recalibrar al cambiar de personaje. La interfaz `ICharacterRig` evita que el inventario dependa del controlador concreto del jugador.
