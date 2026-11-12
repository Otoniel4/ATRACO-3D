# Corrección de recogida y elección de agarre

2026-11-10. Misma tarea de objetos y animación. Pendiente de prueba en Unity.

## Evidencia y cambios

La captura muestra `Contacto bloqueado en Mercado Grande, caja -1, estado PickingUp`. La caja -1 corresponde a un cliente que todavía no eligió caja; el bloqueo ocurre al recoger, no demuestra un fallo de asignación de cajero.

Se corrigieron estos problemas del código:

- La elección del extremo de un objeto a dos manos se fijaba antes de que el NPC terminara de girar hacia él. Ahora se puede corregir antes del contacto y se conserva una vez sujeto.
- Los objetos con dos laterales equivalentes permiten tomar el lado más cercano. No se aplica a asas ni a joyas cuya definición requiere un apoyo distinto.
- El acercamiento utiliza el contacto del producto y busca una distancia de 38 cm, en lugar de 55 cm desde su centro. El barrido de cápsula, las colisiones y el límite de desplazamiento de 48 cm dentro de la reserva se conservan: este objetivo no autoriza atravesar muebles.
- Los objetos a dos manos usan el punto medio para situar el cuerpo.
- El objetivo de los pies permanece ligado al estante y el acercamiento termina cuando el producto ya está en la mano. No se persigue la mano durante el resto de PickingUp.
- El aviso de contacto bloqueado ahora incluye objeto, mano, distancia, altura y necesidad de dos manos. Si un mueble impide llegar, la visita se cancela; no se hace volar el objeto para ocultarlo.

Las posturas de las capturas también necesitan revisión en ejecución. No se declara resuelto todo bloqueo físico por haber compilado.

## Archivos modificados

- `Scripts/AI/CityLifeR5/ShoppingPresentation.cs`: elección de agarre, objetivo estable, estado de recogida y diagnóstico.
- `Scripts/AI/CityLifeR5/PedestrianActor.cs`: acercamiento y salida al sujetar el producto.
- `Art/BlenderScripts/ShopObjectsR44~/TransferTests.cs`: regresiones de giro previo y detención del acercamiento; resultados actualizados.

## Verificación

127.696 comprobaciones del presentador real y 288 regresiones anteriores pasan. Incluyen cambios de apoyo, manos ausentes durante una espera prolongada, giro antes/después de recoger y ejes importados reflejados. Pasan 360 contactos matemáticos y compilan cuatro asambleas. Estas pruebas no ejecutan Animator ni PhysX y no sustituyen la compra completa en la escena real.

## Pasos para Alain

1. Sal de Play y espera la compilación. Guarda cualquier cambio tuyo.
2. Ejecuta **Alarma > Crear y probar juego** y limpia los mensajes anteriores de Console.
3. Observa en Mercado Grande la recogida desde un estante lateral, la entrada a una caja y el escaneo del vendedor. El NPC debe dejar de acercarse al sujetar el objeto.
4. Revisa también pizza y camiseta: ambos brazos deben tomar sus extremos sin cruzarse por una elección hecha antes del giro.
5. Si vuelve `Contacto bloqueado`, copia el aviso nuevo completo. La distancia y el objeto permiten distinguir una postura incorrecta de un mueble que impide acercarse.

## Explicación para aprender

El punto al que caminan los pies no debe depender de un objeto que esos mismos pies ayudan a mover. Esa dependencia hacía que el personaje persiguiera su propia mano. Separar el objetivo del estante del objeto transportado rompe ese ciclo. El presentador decide qué se está sujetando; el componente de movimiento conserva la responsabilidad de acercarse con colisiones.
