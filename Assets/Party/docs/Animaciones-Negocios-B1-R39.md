# Atención y compras por negocio — revisión 39

Solicitud de Alain, 2026-11-07. Mejora dentro de B1, pendiente de prueba visual en Unity 6000.3.27f2. No se abrió Unity ni se ejecutó Play. No se cambian los FBX ni las escenas guardadas; el botón de preparación instala la configuración nueva.

## Cambios

Cada uno de los seis tipos de negocio tiene un `ShopAnimationProfile` editable. Todas las sucursales y cajas adicionales del mismo tipo lo utilizan. El constructor pasa a `ciudad25-39` y detecta cambios de esos perfiles y de los scripts comerciales.

| Negocio | Atención preparada |
| --- | --- |
| Minimarket | Recogida, apoyo, revisión breve y entrega del paquete. |
| Supermercado | Recorrido más ancho sobre el lector y separación entre recogida y entrega. |
| Joyería | Inspección más lenta, elevada y con inclinación suave; se transportan el anillo y su gema, no todo el conjunto de exposición. |
| Banco | Turno, registro, conteo de efectivo sobre la caja y entrega por bandeja con más tiempo. |
| Comida | Movimiento más lento y horizontal para mantener estable el paquete. |
| Ropa | Revisión del paquete con recorrido lateral y poca inclinación. No se simula deformación de tela. |

La mano de cada comprador tiene una trayectoria independiente. Antes, los compradores que tomaban productos podían alternar un mismo objetivo perteneciente a la caja. El objetivo ahora pertenece a cada persona y se libera al terminar o volver al pool. El cajero conserva su propia trayectoria.

Las manos aceleran y frenan suavemente. La palma de compras se calibra a partir de los huesos y la muñeca se orienta antes de resolver el brazo. Los dedos reciben una flexión ligera de apoyo, restaurada antes de cada fotograma para no acumular deformación. La puerta conserva su modo de contacto independiente.

Los productos conservan la conversión de orientación del FBX. El apoyo se mide en los ejes del juego, no suponiendo que el eje Y local del archivo sea vertical. Los traspasos interpolan posición y giro, añaden una elevación suave y no saltan directamente a la mano al activarse. Una vez termina el traspaso, siguen el punto real de la palma. Billetes y vuelto comienzan su recorrido desde bolsillo o caja. La mercancía del estante también se centra sobre su apoyo.

Los hitos de todas las fases se expresan proporcionalmente a su duración. Cambiar el tiempo de atención de una joyería o un banco ya no deja los traspasos usando segundos fijos del supermercado. Se reutilizan los clips existentes y el ajuste de brazos; no se añadieron clips externos ni nuevas mallas.

## Verificación y límites

Corrección de importación del 2026-11-07: Alain recibió el aviso de Safe Mode. `Editor.log` identificó un GUID de 33 caracteres en `ShopAnimationProfile.cs.meta`; Unity ignoraba el script y producía CS0246 en `CounterExchange` y `ShopTaskSettings`. Se sustituyó por un GUID válido de 32 caracteres y se actualizaron conjuntamente los seis perfiles y su receta. No se borraron cachés ni escenas. La validación ahora comprueba metadatos antes de compilar: 9.340 GUID válidos, sin duplicados, seis referencias correctas y regresión que rechaza el identificador anterior. La comprobación C# anterior añadía archivos a su lista y no detectaba que Unity había ignorado uno por su `.meta`.

Si el aviso sigue abierto: elegir **Enter Safe Mode**, esperar la importación y recompilación; si no se inicia, usar **Assets → Refresh**. Confirmar que Console queda sin errores antes de **Exit Safe Mode** y de volver a **Alarma → Crear y probar juego**. No pulsar Ignore para saltarse la compilación.

- Cuatro asambleas compiladas contra las DLL instaladas: CityLife, CityLife.Editor, Playtest y City.Editor.
- 36 escenarios completos a tres frecuencias de actualización, con tres personas y tres cajas por escenario: 108 visitas terminadas sin doble cobro/retiro y liberando sus filas.
- 8.382 comprobaciones de secuencia y suavizado; 16 de contacto/restauración de compras y 96 regresiones del contacto de puertas.
- Seis renders Blender revisados con personajes y productos existentes. Representan poses de apoyo/inspección, no una captura de ejecución ni una validación de todo el recorrido. El render no incluye la flexión adicional de dedos del runtime.
- La auditoría geométrica de mostradores detecta puntos nominales fuera del alcance de algunos cajeros/clientes (`counter-reach.json`). El apoyo en la palma está comprobado, pero esto **no certifica contacto físico durante todos los traspasos en todos los mostradores**. Sigue pendiente revisar alcance, desplazamiento y contacto con los muebles en Play. No se da por aprobado ese apartado ni se oculta esta limitación con las pruebas de estados.
- La validación usa matemáticas y sustitutos fuera del editor; no ejecuta Animator/PhysX. Sigue siendo una demo local, sin sincronización de red.

## Archivos creados o modificados

Rutas relativas a `Assets/Party/`:

- `Scripts/AI/CityLifeR5/ShopAnimationProfile.cs`, `CommerceHandMotion.cs`, `CommerceFingerPose.cs` y sus `.meta`.
- `Data/ShopAnimations/`: seis perfiles `.asset`, sus `.meta` y `.meta` de carpeta.
- `Scripts/AI/CityLifeR5/Domain/CounterChoreography.cs`.
- `Scripts/AI/CityLifeR5/CounterExchange.cs`, `ShopTaskSettings.cs`, `ShopActivity.cs`, `PedestrianActor.cs`, `PedestrianReach.cs`, `SurfaceHandPose.cs`, `ShoppingPresentation.cs`, `ShopStockDisplay.cs`.
- `Scripts/City/Editor/City25/City25Shops.cs`, `City25Builder.cs`.
- `Art/BlenderScripts/ShopAnimation39~/`: recetas, pruebas, resultados numéricos y seis vistas.
- Corrección de Safe Mode: `ShopAnimationProfile.cs.meta`, los seis perfiles `.asset`, `create_profiles.py`, `validate.py`, `validate_metadata.py` y `metadata-results.json`.
- `Art/BlenderScripts/HideoutB1Fix~/DoorReview36~/test_reach.py`: incluye el nuevo auxiliar de dedos al compilar la regresión.
- Este documento y su `.meta`; nota pendiente en `TASKS.md`.

## Pasos para el editor

1. Sal de Play y deja terminar la compilación.
2. Pulsa **Alarma → Crear y probar juego**. El constructor crea una revisión nueva y asigna los perfiles a las cajas. No borres `Generated` ni rehagas prefabs a mano.
3. Los ajustes quedan en `Assets/Party/Data/ShopAnimations`. Cambiar una duración conserva el orden relativo de las fases. Vuelve a preparar con el botón después de cambiar datos.

## Cómo probarlo

1. Visita minimarket, supermercado, joyería, banco, comida y ropa. Observa al menos una atención completa en cada tipo.
2. Mira recogida, traslado, apoyo, manipulación del vendedor, dinero/vuelto y recogida final. Comprueba que los objetos no giren 90° ni aparezcan directamente en el destino.
3. En supermercado y banco observa varias cajas a la vez. Dos clientes tomando productos simultáneamente no deben mover la mano hacia el producto del otro.
4. En joyería debe viajar un anillo con su gema; las joyas decorativas del local siguen presentes. En banco el efectivo debe seguir la bandeja y volver al cliente.
5. Al terminar, las manos deben recuperar la pose, los clientes salir y la caja aceptar al siguiente. Al alejarte y volver, los NPC reutilizados no deben conservar objetos ni gestos anteriores.
6. Para cualquier mano que quede corta o atraviese el mueble, registra negocio, número de caja, fase y una captura. Es la comprobación pendiente de la auditoría de alcance, no una prueba ya superada.

No corresponde Multiplayer Play Mode mientras esta rutina sea local. B1 permanece pendiente y no se hace commit de cierre sin confirmación.

## Vistas de Blender

[Minimarket](../Art/BlenderScripts/ShopAnimation39~/minimarket.png), [supermercado](../Art/BlenderScripts/ShopAnimation39~/supermercado.png), [joyería](../Art/BlenderScripts/ShopAnimation39~/joyeria.png), [banco](../Art/BlenderScripts/ShopAnimation39~/banco.png), [comida](../Art/BlenderScripts/ShopAnimation39~/comida.png), [ropa](../Art/BlenderScripts/ShopAnimation39~/ropa.png).

## Explicación para aprender

La máquina de estados decide qué ocurre y los perfiles definen cuánto dura y cómo se presenta. Las trayectorias pertenecen a cada persona para evitar que clientes simultáneos compartan objetivos. La vista del producto conserva su orientación importada y lo vincula al punto real de la mano. Se aplica responsabilidad única: rutina, alcance, presentación y configuración tienen funciones distintas. Las pruebas de estados garantizan orden y cobro único; la calidad del contacto con los muebles necesita además revisión visual.
