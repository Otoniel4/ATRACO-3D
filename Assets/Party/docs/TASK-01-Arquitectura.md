# Alarma — Task 01: arquitectura base

Estado: implementación compilada en Unity 6000.3.27f2 y nueve pruebas EditMode superadas. Alain validó la tarea con una captura que muestra 9 pruebas correctas y autorizó continuar con Blender. Task 01 marcada para su commit de cierre.

## Qué se implementó

Todo el código, los assets de comprobación y las pruebas están en `C:\Users\Alain\Atraco3D\Assets\Party`.

- Trece módulos en `Scripts`: Core, Player, Animation, Networking, AI, City, Traffic, Heist, Police, Vehicles, Economy, UI y Audio.
- Un Assembly Definition por módulo. Core no referencia a los otros módulos; cada módulo restante solo referencia a Core. No se incorporaron dependencias de red a contratos comunes.
- Cinco contratos en `Alarma.Core.Contracts`: IInteractable, IDamageable, IDetectable, IArrestable e IIntimidatable.
- Canales ScriptableObject para señales sin datos, enteros y decimales. La base genérica evita repetir la publicación de eventos con datos.
- Un listener de señal sin datos configurable desde el Inspector, con alta y baja de suscripción en OnEnable y OnDisable.
- Tres assets de comprobación en `Data/Events`: ArchitectureSignal, ArchitectureCounter y ArchitectureValue.
- Carpeta de arte con Characters, City, Vehicles, Props, Weapons, Animations, Materials y BlenderScripts; también Prefabs, Scenes y Data.
- Pruebas EditMode y un menú de validación disponibles solo en el editor.
- README de arquitectura con responsabilidades, contratos, uso de canales y límites de la implementación.

Los módulos que todavía no tienen lógica solo contienen su Assembly Definition. Su existencia prepara la organización; no significa que ya haya movimiento, IA, vehículos o red. Los canales son avisos locales y no sincronizan datos entre jugadores.

## Archivos creados y modificados

Los scripts principales están en:

- `C:\Users\Alain\Atraco3D\Assets\Party\Scripts\Core\Contracts\`: los cinco contratos, un archivo `.cs` por interfaz.
- `C:\Users\Alain\Atraco3D\Assets\Party\Scripts\Core\Events\`: EventChannel.cs, VoidEventChannel.cs, IntEventChannel.cs, FloatEventChannel.cs y VoidEventChannelListener.cs.
- `C:\Users\Alain\Atraco3D\Assets\Party\Scripts\Core\Editor\ArchitectureTestRunner.cs` y su Assembly Definition exclusivo del editor.
- `C:\Users\Alain\Atraco3D\Assets\Party\Tests\EditMode\EventChannelTests.cs` y su Assembly Definition de pruebas.
- `C:\Users\Alain\Atraco3D\Assets\Party\README.md`.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\TASK-01-Arquitectura.md`: este informe.

Se generaron los `.meta` necesarios y `.gitkeep` para conservar las carpetas vacías en Git. El inventario completo está en la entrega `Task-01-Archivos.txt`.

También se modificaron `C:\Users\Alain\Atraco3D\TASKS.md`, `C:\Users\Alain\Atraco3D\AGENTS.md` y `C:\Users\Alain\Atraco3D\CLAUDE.md` para registrar el nuevo orden autorizado. No se cambiaron paquetes ni la versión de Unity.

## Nuevo orden confirmado por Alain

1. Terminar y aceptar Task 01.
2. Task 03: conectar Blender mediante MCP y comprobar exportación.
3. Producir y aprobar el estilo, mapa, personajes, ropa, vehículos, accesorios, armas y herramientas.
4. Preparar clips de animación.
5. Task 02: prototipo de red.
6. Integrar las dinámicas: animación en juego, caminar, correr, interacción, semáforos, tráfico y demás sistemas.

Se conservan los identificadores originales. Se añadió Task 03.8 para las armas y herramientas del GDD, cuya producción no tenía una tarea de arte explícita. El cambio de prioridad no marca tareas como terminadas ni omite las pruebas online.

## Validación automática

Comprobación completada en el editor del proyecto: **9 casos ejecutados, 9 correctos, 0 fallidos y 0 omitidos**. Se generaron los ensamblados Alarma.Core, Alarma.Core.Editor y Alarma.Core.EditModeTests. No se registraron errores C# durante la compilación de esta entrega. También se validaron las trece definiciones de módulos y la unicidad de los GUID de los nuevos assets.

Las nueve pruebas cubren: publicación sin oyentes; múltiples suscriptores; baja efectiva; baja durante una notificación; independencia entre assets; tres valores enteros; conservación de un valor decimal. El ejecutor guarda resultados NUnit en `C:\Users\Alain\Atraco3D\Library\Alarma\Task01Results.xml`.

## Pasos para el editor

1. Conserva Unity `6000.3.27f2` y espera a que termine la importación.
2. En Project, revisa las carpetas dentro de `Assets/Party` y los tres assets en `Data/Events`.
3. Abre Console y comprueba que no haya errores rojos. Los módulos vacíos todavía no generan código de juego.
4. Abre **Alarma > Validation > Run Architecture Tests** para repetir las pruebas cuando quieras. También están en **Window > General > Test Runner > EditMode > Alarma.Core.EditModeTests**.

## Cómo probarlo

1. Ejecuta las pruebas EditMode. Deben pasar los nueve casos, sin fallos ni omisiones.
2. Para una prueba visual opcional, crea una escena de comprobación y guárdala dentro de `Assets/Party/Scenes`.
3. Añade un cubo y un GameObject vacío independiente llamado EventListener.
4. En EventListener añade **Alarma > Events > Void Event Channel Listener**. Asigna ArchitectureSignal a Channel.
5. En Response, pulsa **+**, arrastra el cubo y elige **GameObject > SetActive(bool)** con el valor desmarcado.
6. Entra en Play Mode. Selecciona el asset ArchitectureSignal en Project, abre su menú contextual del Inspector y ejecuta **Raise Event**. El cubo debe desactivarse.
7. Sal de Play Mode. Esta escena solo comprueba el canal; no implementa mecánicas del juego. No se necesita Multiplayer Play Mode porque esta tarea no incluye red.
8. Validación recibida: Alain confirmó el resultado y adjuntó una captura con 9 pruebas correctas, 0 fallidas y 0 omitidas. Task 01 marcada como `[x]` para su commit de cierre.

## Explicación para aprender

Los Assembly Definitions separan el código en módulos y controlan sus dependencias. Las interfaces describen capacidades sin exigir una clase concreta. Los canales aplican Observer: un emisor publica y los oyentes reaccionan sin conocerse entre ellos. Cada pieza tiene una responsabilidad concreta y los contratos son pequeños, aplicando S e I de SOLID. Los módulos dependen de Core y sus abstracciones, aplicando D. La base genérica permite crear otro tipo de canal sin modificar los existentes, aplicando O.

## Referencia técnica

[Guía oficial de Unity sobre canales de eventos con ScriptableObjects](https://unity.com/how-to/scriptableobjects-event-channels-game-code). La API de pruebas se consultó directamente en el Test Framework `1.6.0` instalado.
