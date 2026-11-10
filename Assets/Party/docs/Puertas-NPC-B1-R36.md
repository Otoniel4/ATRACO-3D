# Puertas y contacto autónomo B1 — revisión 36

Estado: instalado localmente; pendiente de prueba y aprobación de Alain en Unity 6000.3.27f2. No se abrió Unity ni se ejecutó Play. No se cerró B1 ni se hizo commit.

## Corrección

- `PedestrianActor` alinea el hombro real con la placa después de orientar el cuerpo. El ajuste anterior suponía un hombro desplazado 22 cm y adelantaba el cuerpo sin resolver el desfase lateral.
- `PedestrianMovement` admite un ajuste continuo de hasta 48 cm dentro de la reserva de llegada. Conserva el barrido de la cápsula, las colisiones con personas y la reserva del siguiente paso desde los pies reales.
- `SurfaceHandPose` calibra la palma con los nudillos y orienta los dedos hacia arriba. `PedestrianReach` resuelve primero la muñeca descontando la palma orientada, inclina el torso 10° y restaura la pose antes del siguiente fotograma. Las compras conservan su marcador original.
- `ShopDoor` conserva una normal independiente en cada cara de la hoja. El apoyo está 14 cm por encima del marcador, en la parte alta de la placa. La apertura sigue exigiendo contacto; el umbral ocupado mantiene la puerta abierta durante el cruce.
- Banco, joyería, supermercado, minimarket, comida, ropa y guarida tienen perfiles completos de pivote y marcos profundos. La junta lateral nominal es de 5 mm y la superior de 4 mm. Los perfiles permiten girar hacia dentro y fuera sin rellenar el arco de la hoja con una pared.
- El constructor usa `ciudad25-36` para preparar una escena con los modelos actuales. No se sobrescribió la escena guardada desde fuera del editor.

## Archivos creados o modificados

Código:

- `Assets/Party/Scripts/AI/CityLifeR5/PedestrianActor.cs`
- `Assets/Party/Scripts/AI/CityLifeR5/PedestrianMovement.cs`
- `Assets/Party/Scripts/AI/CityLifeR5/PedestrianReach.cs`
- `Assets/Party/Scripts/AI/CityLifeR5/SurfaceHandPose.cs` y `.meta` — nuevo.
- `Assets/Party/Scripts/AI/CityLifeR5/RigBones.cs`
- `Assets/Party/Scripts/AI/CityLifeR5/ShopDoor.cs`
- `Assets/Party/Scripts/City/Editor/City25/City25Builder.cs`
- `Assets/Party/Scripts/Player/Editor/Alarma.Player.Editor.asmdef`: declara `Alarma.Core`, necesario para el tipo `NoiseChannel` que usa la configuración de acciones. La compilación final detectó esta dependencia ausente.

Arte y recetas:

- `Assets/Party/Art/BlenderScripts/build_shops.py`
- `Assets/Party/Art/BlenderScripts/build_hideout.py`
- `Assets/Party/Art/City/Shops/Local_Banco.fbx`
- `Assets/Party/Art/City/Shops/Local_Joyeria.fbx`
- `Assets/Party/Art/City/Shops/Local_Supermercado.fbx`
- `Assets/Party/Art/City/Shops/Local_Minimarket.fbx`
- `Assets/Party/Art/City/Shops/Local_Comida.fbx`
- `Assets/Party/Art/City/Shops/Local_Ropa.fbx`
- `Assets/Party/Art/City/Shops/Local_Escondite.fbx`
- `Assets/Party/Art/BlenderSources~/Alarma_Puertas36.blend` — fuente nueva con las siete colecciones completas, incluidas las piezas ajenas al acceso. Esta fuente corresponde a la revisión 36; los archivos Blender anteriores conservan sus revisiones históricas.

Validación y documentación:

- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorReview36~/`: recetas, instalación con respaldo, pruebas de alcance, comparación de geometría, informes y capturas.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/PedestrianDoorApproachTests.cs`, `run_interaction_tests.py` e informes.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorContactTests~/ShopDoorTests~/Regression.cs` e informe.
- Este documento y nota pendiente en `TASKS.md`.
- `Assets/Party/Art/BlenderScripts/HoldGripFix~/verify_code.py`: incorpora esa referencia en la compilación aislada cuando el archivo de respuesta de Unity todavía es anterior al cambio.

## Comprobaciones realizadas

- 80 comprobaciones del C# real de alcance: cuatro orientaciones, cuatro posiciones de hombro, contacto, longitud de brazos y restauración después de soltar.
- 31 comprobaciones del C# real de puertas con física simulada: contacto por ambas caras, apertura, umbral ocupado, cierre y obstáculos.
- 12 comprobaciones de interacción del jugador y 22 de acercamiento, rutas y reservas.
- 180 poses medidas en los diez FBX de civiles: tres momentos de reposo, entrada/salida y tres columnas de llegada. Error máximo de palma: 5,1 mm; umbral de contacto del componente: 35 mm. Esta medición no reproduce Animator ni PhysX de Unity.
- 2.394 muestras de giro sobre las cajas reimportadas de las siete puertas, de −85° a +85°. Se emplea una tolerancia geométrica de 1 mm para caras coplanares con el suelo; el runtime usa 12 mm.
- 1.969 mallas ajenas a las puertas conservan coordenadas redondeadas a 1 mm, cantidad de polígonos y materiales. Incluye los muebles, el portón y el garaje de la guarida.
- Compilación de `Alarma.CityLife` y `Alarma.Playtest` contra las DLL instaladas, sin iniciar Unity.
- Compatibilidad adicional: 14 pruebas de agarre y compilación de `Alarma.Player`, `Alarma.Player.Editor`, `Alarma.Playtest.Editor` y `Alarma.City.Editor`, además de Playtest. La referencia ausente a Core quedó corregida y la repetición pasó.
- Capturas nativas de Blender revisadas desde dentro y fuera. `banco_contacto.png` y `banco_palma.png` muestran una pose de contacto, no una ejecución del juego.

Los siete FBX se instalaron conservando sus `.meta`. `DoorReview36~/installed.json` registra hashes y la ruta del respaldo recuperable bajo `Library/Alarma/DoorReview36/Anterior_...`.

## Pasos para el editor

1. Abrir el proyecto con Unity 6000.3.27f2 y esperar a que termine la importación y compilación.
2. Pulsar **Alarma → Crear y probar juego**. Debe preparar la revisión 36; no probar solamente la escena anterior con Play.
3. Si aparece un error de compilación o construcción, conservar el primer mensaje completo de Console y detener esa prueba.

## Cómo probarlo

1. Ir al banco y observar desde al menos 2 metros del paso, sin pulsar E. Esperar a que un cliente llegue desde la acera, apoye la mano, abra y entre por sí mismo.
2. Permanecer en la zona y observar un retiro completo. El cliente debe salir abriendo desde dentro si la puerta ya cerró. Comprobar al menos tres entradas y tres salidas.
3. Repetir la observación en supermercado, joyería, minimarket, comida y ropa. Confirmar que la espera corresponde a una fila o al aforo, y no a una mano inmóvil en la puerta.
4. Con el jugador, abrir y cruzar cada acceso en ambos sentidos. Detenerse un momento en el umbral: no debe cerrarse encima del cuerpo. Al despejarlo, debe cerrar suavemente.
5. Mirar los laterales y dinteles desde dentro y fuera, con las hojas cerradas y abiertas. Deben verse los perfiles y juntas estrechas, sin los huecos anteriores.
6. Probar también la puerta de la guarida. Confirmar a Alain los resultados y cualquier caso que siga fallando. B1 continúa abierta hasta esa confirmación. Multiplayer Play Mode no corresponde: este flujo sigue siendo local.

## Explicación para aprender

El destino de una mano no equivale al destino de la muñeca: al girarla, la palma cambia de posición. Por eso se calcula su orientación primero y se descuenta ese desplazamiento antes de resolver el brazo. La clase de calibración tiene una sola responsabilidad; el componente de alcance anima y la puerta controla su propio giro. Se mantiene la máquina de estados de la visita y se conserva la separación de responsabilidades del principio S de SOLID. Las pruebas numéricas detectan alcance imposible y choques geométricos, pero la integración con Animator y PhysX debe comprobarse en Play.
