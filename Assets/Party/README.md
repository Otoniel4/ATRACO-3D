# Alarma — Arquitectura base

Proyecto Unity `6000.3.27f2`. Todo el contenido propio del juego se guarda en `Assets/Party`.

## Referencias

- Diseño: `docs/GDD.pdf`.
- Desarrollo: `TASKS.md` en la raíz del proyecto; su sección de orden vigente recoge las instrucciones más recientes de Alain.
- Validación de esta entrega: `docs/TASK-01-Arquitectura.md`.

## Módulos y dependencias

`Scripts` contiene trece módulos con un Assembly Definition por módulo. Cada uno tiene su namespace raíz `Alarma.<Módulo>`. Core no depende de los demás y cada módulo restante solo referencia Core. Las referencias a paquetes concretos o a otro módulo se añadirán cuando una implementación realmente las necesite.

| Módulo | Responsabilidad prevista |
| --- | --- |
| Core | Contratos comunes y canales de eventos locales. |
| Player | Entrada, movimiento y estado del jugador. |
| Animation | Adaptadores de Animator y parámetros de animación. |
| Networking | Conexiones, servicios online y validación de acciones de red. |
| AI | Percepción, decisiones y navegación comunes de NPC. |
| City | Configuración y generación de la ciudad. |
| Traffic | Semáforos y tráfico. |
| Heist | Locales, alerta, acceso y botín. |
| Police | Búsqueda, persecución y arrestos. |
| Vehicles | Conducción, asientos y estados de vehículos. |
| Economy | Dinero de la banda, compras y progresión. |
| UI | Presentación de datos y respuestas a eventos. |
| Audio | Mezcla y respuestas sonoras. |

Los módulos sin implementación contienen solo su definición de ensamblado. No se han añadido clases vacías para simular sistemas terminados. Unity no necesita generar una DLL para un módulo que todavía no contiene scripts.

Los subensamblados `Alarma.Core.Editor` y `Alarma.Core.EditModeTests` solo se compilan para el editor; no forman parte de una build del juego. El primero ejecuta las comprobaciones y el segundo contiene las pruebas NUnit.

## Contratos

Los contratos están en `Alarma.Core.Contracts` y no dependen de Netcode ni de un tipo concreto de jugador:

- `IInteractable`: presenta la acción y su duración en segundos, consulta si puede realizarse y permite ejecutarla. La duración debe ser no negativa en las implementaciones. La validación de distancia y autoridad se añadirá en su sistema, antes de ejecutar la interacción.
- `IDamageable`: recibe una cantidad de daño y su origen; el origen puede ser `null` para daño del entorno. Quien implemente vida y combate validará cantidades y reglas en el host.
- `IDetectable`: ofrece un punto de detección y si el objeto puede ser detectado. No calcula visión ni distancias.
- `IArrestable`: indica si el objetivo admite arresto y permite arrestarlo identificando al policía. No decide por sí mismo quién tiene autoridad de red.
- `IIntimidatable`: inicia y termina la intimidación identificando su origen. Así una futura implementación podrá distinguir varios jugadores apuntando al mismo NPC; dejar de apuntar uno no debe cancelar a los demás.

`GameObject` y `Transform` pertenecen al motor común, no a un módulo de juego. Un adaptador de red convertirá las referencias de red a estas referencias locales y validará la petición antes de invocar el contrato. Los contratos describen capacidades; todavía no implementan daño, interacción, arresto ni intimidación.

## Canales de eventos

`Alarma.Core.Events` contiene tres tipos de canal ScriptableObject:

- `VoidEventChannel`: una señal sin datos.
- `IntEventChannel`: transmite un entero.
- `FloatEventChannel`: transmite un número decimal.

Los dos tipos con datos reutilizan `EventChannel<T>`. Los eventos son miembros `event`, por lo que un consumidor externo puede suscribirse, pero no reemplazar la lista de oyentes ni invocarla directamente. `Raise` notifica de forma síncrona a los suscriptores del asset concreto. No hay un bus estático global y dos assets distintos no comparten oyentes.

Ejemplo de suscripción desde un componente futuro:

```csharp
private void OnEnable()
{
    moneyChanged.Raised += UpdateMoneyLabel;
}

private void OnDisable()
{
    moneyChanged.Raised -= UpdateMoneyLabel;
}
```

Cada suscripción debe tener su baja correspondiente. Los canales no borran silenciosamente las suscripciones al deshabilitar un asset. Una excepción de un oyente se mantiene visible; el canal no la captura ni promete que los siguientes oyentes se ejecuten después de esa excepción.

Estos eventos **son locales**: no son RPC, no replican datos y no reemplazan al estado autoritativo del host. Cuando haya red, los sistemas publicarán el estado local confirmado para que UI y audio reaccionen sin conocer el sistema que lo originó.

`VoidEventChannelListener` conecta un canal sin datos con un `UnityEvent` configurable en el Inspector. Se suscribe al activarse y se da de baja al desactivarse. Conserva la referencia del canal realmente suscrito para liberar la referencia correcta. Si cambias su campo Channel durante Play Mode, desactiva y vuelve a activar el componente para aplicar ese cambio.

En `Data/Events` hay tres assets de comprobación sin reglas de juego: `ArchitectureSignal`, `ArchitectureCounter` y `ArchitectureValue`. No representan vida, dinero ni estado de un atraco.

## Comprobación

1. Espera a que Unity importe y compile los scripts.
2. Abre **Alarma > Validation > Run Architecture Tests**. Ejecuta únicamente la asamblea EditMode de esta tarea y guarda el resultado en `Library/Alarma/Task01Results.xml`.
3. También puedes usar **Window > General > Test Runner > EditMode** y ejecutar `Alarma.Core.EditModeTests`.
4. Deben pasar nueve casos: publicación sin oyentes, múltiples oyentes, baja, baja durante una notificación, independencia entre assets y datos enteros/decimales.

La petición de validación automática usa un archivo fijo en `Library/Alarma/RunTask01Tests.request`. Solo ejecuta las pruebas cuando existe esa petición explícita y el editor está disponible; no se ejecutan pruebas en cada importación normal.

## Organización de arte y siguiente fase

`Art` dispone de `Characters`, `City`, `Vehicles`, `Props`, `Weapons`, `Animations`, `Materials` y `BlenderScripts`. Son carpetas preparadas; todavía no contienen modelos. Se mantienen escala de un metro por unidad, colores planos y modelos propios creados con Blender.

Por decisión de Alain: después de aceptar Task 01 se conecta Blender y se producen los diseños del mapa, personajes, accesorios, vehículos, armas y herramientas. La red, movimiento, semáforos y tráfico se implementarán después. Los criterios técnicos de prueba online se conservan para esa fase.

## Explicación para aprender

Los ensamblados marcan qué código puede conocer a qué módulo. Las interfaces describen capacidades sin exigir una clase concreta. Los canales aplican Observer: un sistema publica un cambio y otros reaccionan sin referenciarlo. Core concentra contratos comunes, no las decisiones de todo el juego. Así se aplican responsabilidades separadas, interfaces pequeñas y dependencias hacia abstracciones.

## Referencia técnica

[Guía oficial de Unity: canales de eventos con ScriptableObjects](https://unity.com/how-to/scriptableobjects-event-channels-game-code). La API del ejecutor de pruebas se verificó contra el Test Framework `1.6.0` instalado en este proyecto.
