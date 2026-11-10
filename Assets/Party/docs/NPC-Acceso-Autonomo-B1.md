# B1 — NPC que alcanzan y abren los negocios

Entrega del 5 de noviembre de 2026. Pendiente la prueba en Play por Alain. No cierra B1 ni modifica el inventario.

## Causa y corrección

`PedestrianTraffic.PassageDistance` calculaba distancias usando las colisiones actuales. Una puerta cerrada separaba el exterior del destino interior. Todas las celdas exteriores recibían distancia infinita y el desempate favorecía quedarse en la celda actual. El NPC no llegaba a la manija. Al abrir el jugador, el destino volvía a ser alcanzable y empezaba la marcha.

Ahora, si no hay una ruta completamente libre, el planificador usa las distancias del grafo para acercarse. Cada paso sigue comprobando colisiones, destinos reservados y cruces entre actores. Al llegar al acceso actúa el flujo existente de `PedestrianActor`: orientar el cuerpo, acercarse, alcanzar la superficie con la mano y pedir el empuje tras confirmar contacto. El recorrido continúa cuando la puerta permite pasar. La misma regla funciona al salir. Si existe un desvío libre completo, mantiene su preferencia sobre acercarse al obstáculo.

## Archivos de esta corrección

- `Assets/Party/Scripts/AI/CityLifeR5/Domain/PedestrianTraffic.cs` — búsqueda provisional hasta el obstáculo cuando la ruta está desconectada.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/PedestrianDoorApproachTests.cs` — nueve casos adicionales de ruta con puerta cerrada.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/run_interaction_tests.py` — comprobación de que el comportamiento anterior falla y opción de compilar únicamente CityLife.
- `interaction-results.json` e `interaction-test-results.txt` en esa carpeta — evidencia actualizada.
- Este documento, `AGENTS.md` y `TASKS.md` — seguimiento pendiente.

## Verificación realizada

- 22 comprobaciones de acercamiento y rutas, incluidas nueve nuevas: avance desde la acera, parada ante la hoja, reserva durante el gesto, continuación tras abrir, salida, desvío libre y dos clientes en lados opuestos.
- La misma regresión falla al retirar la corrección: el NPC no da el primer paso hacia el negocio.
- 12 comprobaciones de interacción de puertas del jugador.
- 30 comprobaciones del código real de `ShopDoor` con física simulada, incluido cierre con el umbral libre.
- 67 comprobaciones de circulación, visitas y transacciones.
- `Alarma.CityLife` compiló contra las DLL instaladas de Unity 6000.3.27f2. Una compilación adicional de Playtest encontró una referencia `ICharacterRig` desactualizada durante cambios paralelos del inventario; la verificación final aisló la asamblea modificada. No se certifica aquí una compilación completa del proyecto.
- Son pruebas de lógica y sustitutos de física. El gesto de mano, PhysX y la visita completa requieren Play. El agente no abrió Unity.

## Pasos para el editor y cómo probar

1. Sal de Play y espera a que Unity termine de compilar. Esta corrección de lógica no necesita regenerar modelos.
2. Inicia **Alarma > Crear y probar juego**.
3. Ve con **M** al supermercado. Sitúate a unos 3 m de la puerta, hacia un costado, dejando libre el paso.
4. Mantén la puerta cerrada y no pulses **E**. Observa durante 60 segundos a los clientes que llegan desde la acera.
5. Comprueba que un cliente se acerca, toca la puerta, la abre, cruza y continúa su visita. Comprueba también la salida y el cierre cuando no queda nadie en el umbral.
6. Repite en banco y joyería, después en minimarket, comida y ropa. No cuentes como entrada autónoma a los clientes que ya estaban dentro al llegar.
7. Confirma el resultado antes de marcar B1 como terminada o hacer su commit.

## Explicación para aprender

Una puerta cerrada es un obstáculo temporal que el personaje puede accionar. El grafo le permite acercarse, mientras la física decide si cada paso está libre. La búsqueda y las reservas permanecen en `PedestrianTraffic`; el gesto y la solicitud de apertura permanecen en `PedestrianActor`. Se conserva la máquina de estados de la visita y la separación de responsabilidades, sin mezclar compras, animación y navegación.
