# Objetos de negocios: integración y revisión de agarres

Fecha: 2026-11-10. Diseños R44 aprobados por Alain. Integración y animación pendientes de prueba en Unity; no se cierra la tarea.

## Cambios

- Catálogo de 18 modelos propios con materiales URP y definiciones de agarre. Las cinco tiendas alternan sus tres productos en los puestos al reponerlos. El mismo objeto acompaña al cliente durante su compra.
- Banco: conserva la retirada de efectivo y utiliza el sobre como documento. Lingote y maletín se colocan como objetos del banco; todavía no participan en una transacción de compra ni se implementó aquí su robo.
- Pizza y camiseta: apoyo bilateral, elección de los extremos según cliente o vendedor y conservación del extremo agarrado durante los giros.
- Anillo, reloj y collar: presentación sobre la palma abierta. El collar tiene una orientación de dedos que deja visibles los eslabones y el colgante.
- Los puntos de apoyo se calibran leyendo los marcadores del FBX importado. Se contempla la inversión lateral de ejes al importar, sin alterar la escala de los modelos.
- Se eliminan las excepciones que autorizaban un traspaso sin contacto por brazo extendido o después de 1,5 segundos. El objeto permanece con su apoyo anterior hasta que llegan las manos requeridas.
- Se conserva la interpolación de posición y rotación al cambiar de apoyo. No se reemplaza el objeto por otra instancia al escanearlo o entregarlo.
- El constructor detecta cambios del catálogo, los modelos y su importador. Se preserva la versión 46 y las otras correcciones de postura existentes.

## Archivos de esta corrección

- `Scripts/AI/CityLifeR5/ShoppingPresentation.cs`: contacto obligatorio y agarre estable durante giros.
- `Scripts/City/Editor/City25/City25Products.cs`: calibración a partir de los FBX importados.
- `Scripts/City/Editor/City25/City25Builder.cs`: dependencias del catálogo para reconstrucción.
- `Tools~/integrate_shop_objects.py` y `Art/Props/ShopObjects/catalog.json`: datos por objeto y apoyo de joyas.
- `Art/BlenderScripts/review_shop_grips_r44.py`: revisión reproducible en una escena Blender independiente.
- `Art/BlenderScripts/ShopObjectsR44~/TransferTests.cs`, `test_transfers.py`, `GripTests.cs`, `validate_integration.py`: pruebas y resultados.
- `Art/BlenderScripts/ShopObjectsR44~/Agarres_R44.blend`, `Agarre_*.png`, `visual-grips.json`: poses y capturas de los 18 modelos.

La integración previa añade `ShopProductDefinition`, `ShopProductInstance`, `CommerceSupportHand`, el catálogo activo y cambios en el expositor, presentadores, alcance y constructor de tiendas. No se sobrescribieron escenas guardadas ni se abrió Unity.

## Verificación realizada

- Cuatro asambleas compiladas contra las DLL instaladas: CityLife, CityLife.Editor, Playtest y City.Editor.
- 360 contactos con código de alcance real: 18 objetos, diez rigs y ambos lados del mostrador; error máximo medido 5,07 mm. La prueba usa transformaciones matemáticas, no Animator ni colisiones Unity.
- 127.376 comprobaciones del presentador real: 18 objetos, cuatro orientaciones, ejes normales/reflejados, cinco cambios de apoyo, espera de 2,5 segundos sin contacto, apoyo izquierdo obligatorio y giro sin cambio de extremo.
- 288 comprobaciones anteriores de traspasos continúan pasando.
- Dieciocho poses preparadas en Blender; revisadas las capturas de pizza, camiseta, anillo, reloj y collar, además del viewport. Son previsualizaciones de agarres, no una grabación de la ejecución en Unity. El script de revisión no reproduce toda la cadena de postura R46 ni PhysX.

## Pasos en Unity y prueba de Alain

1. Guarda tus cambios y sal de Play. Espera a que Unity termine de importar y compilar.
2. Ejecuta **Alarma > Crear y probar juego** para reconstruir con el catálogo actualizado.
3. En comida, observa un cliente con pizza; en ropa, uno con camiseta. Deben apoyar ambas manos al recoger y depositar. Revisa también al vendedor desde el otro lado de la caja.
4. En joyería, observa anillo, reloj y collar sobre la palma. Sigue cada pieza desde el expositor hasta el mostrador y de vuelta al cliente.
5. En las demás tiendas, observa al menos una compra completa: estante, mano, mostrador, vendedor, recogida y salida. El objeto no debe volar hacia una mano que aún no llegó ni cambiar de posición al girar el personaje.
6. Si aparece «Contacto bloqueado», comunica negocio, objeto y estado indicado en Console. La visita se cancela después de diez segundos para liberar la fila; no se simula contacto haciendo volar el objeto.

La prueba de movimiento, colisiones, contactos con muebles y fluidez durante una compra completa sigue pendiente en Play. El prototipo continúa local: esta entrega no añade sincronización de compras con Netcode.

## Explicación para aprender

La definición del producto guarda dónde se apoya y dónde lo sostiene cada mano. El presentador controla cuándo cambia de dueño, mientras los componentes de alcance mueven los brazos. Esta separación aplica responsabilidad única. La máquina de estados de la compra solicita el siguiente paso, pero el contacto físico funciona como condición de transición. El tiempo transcurrido no puede sustituir esa condición: hacerlo ocultaba el bloqueo y provocaba que los objetos volaran hacia la mano.
