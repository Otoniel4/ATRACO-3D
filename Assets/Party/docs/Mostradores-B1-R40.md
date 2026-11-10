# Mostradores y entregas — B1 R40

Corrección solicitada por Alain el 2026-11-09. Pendiente de prueba en Unity y aprobación visual; B1 continúa abierto.

## Qué cambió

- El primero de la fila camina hasta el puesto de atención antes de colocar el producto. Antes comenzaba desde la fila, a veces a más de un metro del mostrador.
- Cada caja tiene una zona de intercambio configurada según su mueble. También se aplica a las cajas adicionales del supermercado y las ventanillas del banco.
- El cliente ajusta sus pies mediante el barrido de colisiones existente. El cajero conserva un puesto fijo fuera del tablero; se retiró su deslizamiento de 28 cm hacia el mueble.
- El brazo calcula la inclinación necesaria usando las longitudes del rig, sin alargar huesos. El brazo libre conserva su orientación durante la inclinación.
- Cajas, envases y joyas se sujetan desde arriba, con flexión de dedos. Dinero y papeles usan apoyo inferior y puntos distintos para ambas personas.
- Un objeto cambia de apoyo/dueño cuando la mano está a 2,5 cm o menos del contacto. Mientras se alcanza, se pausa el reloj de la acción. La transición corta gira alrededor del contacto, sin vuelos largos desde el mostrador.
- Si una interferencia impide el contacto durante diez segundos, se registra el local/caja/estado y se cancela esa visita liberando la fila. Una operación pagada pero no recogida se revierte una sola vez. Es recuperación de un fallo, no una compra completada.
- Joyería: intercambio y piezas manipulables sobre el cristal de 1,34 m. Comida: intercambio apartado de la registradora. Banco: abertura inferior de la ventanilla a 1,38 m y bandeja extendida a ambos lados.
- Constructor `ciudad25-40`: el botón Alarma prepara una revisión con los puntos nuevos. No se editó la escena guardada manualmente ni se sustituyeron los FBX.

## Archivos modificados

Dentro de `Assets/Party/Scripts/AI/CityLifeR5/`:

- `Domain/PedestrianRoutine.cs`: estado de llegada al mostrador y cancelación de interacción.
- `Domain/CounterChoreography.cs`: conservar producto/comprobante mientras se camina a la caja.
- `Domain/ShopService.cs`: revertir operaciones aún no recogidas.
- `ShopActivity.cs`: destino de cada caja y referencia serializada a su zona de trabajo.
- `ShopAnimationProfile.cs`: dimensiones, centro y normal del mostrador.
- `CounterExchange.cs`: apoyos cercanos, trayectoria y puesto fijo del cajero.
- `PedestrianActor.cs`: llegada, ajuste físico, espera de contacto y recuperación.
- `PedestrianReach.cs`, `SurfaceHandPose.cs`, `CommerceHandMotion.cs`: alcance adaptativo y agarre superior.
- `ShoppingPresentation.cs`: traspasos condicionados al contacto, referencias de agarre y conservación de orientación.

Otros archivos:

- `Assets/Party/Data/ShopAnimations/`: los seis perfiles `.asset`.
- `Assets/Party/Scripts/City/Editor/City25/City25Shops.cs`: construcción de puestos, puntos y paso de ventanilla.
- `Assets/Party/Scripts/City/Editor/City25/City25Builder.cs`: versión 40.
- `Assets/Party/Art/BlenderScripts/CounterContact40~/`: medidas, verificación de rigs/modelos, prueba C#, seis imágenes y copia de revisión del banco.
- `Assets/Party/Art/BlenderScripts/ShopAnimation39~/CommerceTests.cs`, `PurchaseReachTests.cs`, `validate.py`: regresiones ampliadas y evidencias.
- Esta guía, su `.meta` y `TASKS.md`.

## Comprobaciones

El validador compila las cuatro asambleas afectadas contra las DLL instaladas, sin iniciar Unity. Comprueba metadatos y referencias de los seis perfiles.

Las pruebas ejercitan llegada demorada a la caja, compras/retiros simultáneos, cobro único, cancelación y devolución. El código real del brazo se ensaya con medidas extraídas de diez FBX, seis mostradores, tres alturas, tres posiciones laterales y cuatro orientaciones: 2.160 contactos, conservando la longitud de los huesos. También se mantienen las regresiones de puertas.

Las imágenes son vistas de Blender de los modelos existentes, con los puestos corregidos; no capturas de Play ni una prueba de PhysX, navegación o animación completa. El Blender conectado no respondió; la revisión se generó en Blender aislado. No se abrió Unity.

Validación final del 2026-11-10: 2.160 contactos del brazo, 288 comprobaciones de traspaso con `ShoppingPresentation` real (seis tipos, cuatro orientaciones), 8.396 comprobaciones de dominio, 16 de agarre y 96 de puertas. Las cuatro asambleas compilan. El traspaso comprueba que el objeto permanece con su dueño cuando la otra mano está lejos, se apoya por la base y cambia de dueño sin salto ni giro.

Alain autorizó commit y push de respaldo antes de la prueba manual. No se cierran tareas por ese respaldo. `Tools~/select_current_city.py` comprueba los GUID de la escena vigente y excluye del commit revisiones antiguas no requeridas, conservándolas localmente.

Comandos reproducibles, mediante RTK:

```text
rtk bypass "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python Assets/Party/Art/BlenderScripts/CounterContact40~/verify.py
rtk bypass python Assets/Party/Art/BlenderScripts/ShopAnimation39~/validate.py
rtk bypass python Assets/Party/Art/BlenderScripts/CounterContact40~/test_transfers.py
```

## Pasos para el editor y prueba

1. Esperar a que Unity termine de compilar. Salir de Play y guardar los cambios propios.
2. Pulsar **Alarma → Crear y probar juego**. Usar esa entrada para obtener los puntos R40; Play sobre una escena antigua conserva sus puntos anteriores.
3. Observar al menos dos compras completas en minimarket, supermercado, joyería, comida y ropa, y dos retiros en el banco.
4. Verificar: primero camina de la fila al puesto; mano toca el producto; producto queda apoyado; vendedor toma, inspecciona y devuelve; cliente paga/recibe y recoge. Ningún objeto debe volar para suplir un brazo corto.
5. En supermercado y banco, observar tres cajas/ventanillas atendiendo a la vez. Cada cliente debe usar su propia caja y sus objetos.
6. Comprobar particularmente el cristal de joyería, el espacio libre junto a la registradora de comida y la bandeja bajo el cristal del banco.
7. Revisar Console. Un aviso `Contacto bloqueado…` identifica una operación cancelada que requiere ajuste; no cuenta como prueba satisfactoria.

Prueba local: no se añadió sincronización de compras por Netcode. Multiplayer Play Mode no corresponde a esta corrección.

## Explicación para aprender

La máquina de estados separa caminar de comprar: el tiempo de colocar empieza solo al llegar.
Los perfiles guardan las medidas del negocio; el mismo código sirve para todas sus cajas.
El controlador de alcance resuelve la postura, y la presentación decide cuándo cambiar el objeto de apoyo.
Esta separación aplica responsabilidad única: navegación, economía y animación tienen funciones distintas.
Una entrega depende del contacto observado, no solamente de que termine un temporizador.
