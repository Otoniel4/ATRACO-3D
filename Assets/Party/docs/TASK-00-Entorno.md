# Alarma / Atraco3D — Task 00: entorno y verificación

Fecha: 31 de octubre de 2026. Estado: Task 00 completada; paquetes verificados y entorno aceptado por Alain.

## Revisión de los documentos

Se revisaron `CLAUDE_2.md`, `AGENTS_1.md` y `TASKS_2.md`. El plan describe un juego cooperativo de atracos con autoridad del host, arquitectura por módulos, arte propio low-poly y desarrollo por tareas. Se mantiene su orden: esta entrega solo aborda Task 00.

Las instrucciones entregadas y el proyecto real difieren:

- Los documentos originales indican Unity `6000.5.8f1`; el proyecto usa `6000.3.27f2`. Alain confirmó conservar esta versión. No se cambió el editor ni se modificó `ProjectVersion.txt`.
- AI Navigation y Timeline ya están instalados; no hay que reinstalarlos.
- Al comenzar faltaban varios paquetes que los documentos describían como instalados. Ahora están descargados y resueltos; se detallan abajo.
- Alain entregó el GDD de 18 páginas. Se conserva una copia íntegra en `Assets/Party/docs/GDD.pdf`; las diferencias detectadas se registran en `Assets/Party/docs/GDD-REVISION.md`.
- No había repositorio Git ni `.gitignore`.
- Alain confirmó `C:\Users\Alain\Atraco3D\Assets\Party` como carpeta del contenido del juego.

## Herramientas y dependencias verificadas

RTK responde a `rtk gain`; Caveman está disponible y se usa para las respuestas breves. RTK advierte que no hay hook automático: la invocación explícita `rtk ...` funciona y no requiere modificar la configuración global. `rtk ls` no encuentra el ejecutable `ls` en Windows; `RTK.md` documenta la alternativa con PowerShell a través de RTK.

| Paquete | Identificador | Estado observado |
| --- | --- | --- |
| Universal RP | `com.unity.render-pipelines.universal` | Instalado: `17.3.0` |
| Input System | `com.unity.inputsystem` | Instalado: `1.20.1` |
| AI Navigation | `com.unity.ai.navigation` | Instalado: `2.0.16` |
| Timeline | `com.unity.timeline` | Instalado: `1.8.13` |
| Multiplayer Center | `com.unity.multiplayer.center` | Instalado: `1.0.1` |
| Netcode for GameObjects | `com.unity.netcode.gameobjects` | Instalado: `2.13.3` |
| Multiplayer Services | `com.unity.services.multiplayer` | Instalado: `2.4.1` |
| Multiplayer Play Mode | `com.unity.multiplayer.playmode` | Instalado: `2.0.2` |
| Cinemachine | `com.unity.cinemachine` | Instalado: `3.1.7` |
| ProBuilder | `com.unity.probuilder` | Instalado: `6.1.4` |
| Cloud Save | `com.unity.services.cloudsave` | Instalado: `3.4.2` |
| Authentication | `com.unity.services.authentication` | Instalado: `3.8.0` |

Multiplayer Center no sustituye Netcode ni Multiplayer Services. Multiplayer Services reúne las funciones de Lobby y Relay; para este proyecto nuevo se instala ese SDK, siguiendo la documentación oficial, en lugar de añadir los antiguos SDK independientes.

La configuración local contiene un identificador de proyecto de Unity Cloud. Eso permite constatar una vinculación guardada, pero no demuestra que Relay, Lobby, Authentication o Cloud Save estén habilitados y accesibles desde la cuenta.

## Archivos preparados

- `C:\Users\Alain\Atraco3D\.gitignore`: excluye cachés de Unity, compilaciones y archivos generados del IDE; conserva assets y `.meta`.
- `C:\Users\Alain\Atraco3D\AGENTS.md`: reglas entregadas y apéndice con el estado real del entorno.
- `C:\Users\Alain\Atraco3D\CLAUDE.md`: reglas entregadas y el mismo apéndice de entorno.
- `C:\Users\Alain\Atraco3D\TASKS.md`: copia del plan entregado, con todas las tareas todavía pendientes.
- `C:\Users\Alain\Atraco3D\RTK.md`: comandos explícitos y alternativa compatible con Windows.
- `C:\Users\Alain\Atraco3D\Assets\Party.meta`: metadatos de la carpeta confirmada.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs.meta`: metadatos de documentación.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\TASK-00-Entorno.md`: este informe.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\TASK-00-Entorno.md.meta`: metadatos del informe.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\GDD.pdf` y su `.meta`: copia íntegra del diseño recibido.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\GDD-REVISION.md` y su `.meta`: revisión del diseño y diferencias respecto al plan.
- `C:\Users\Alain\Atraco3D\.git\`: repositorio local, sin commit de cierre.

No se ha escrito código del juego ni se han modificado escenas o la versión del editor. Se añadieron cinco dependencias al manifiesto y Unity regeneró su archivo de bloqueo. Cinemachine ya estaba instalado como dependencia del paquete de personajes y animación añadido por Alain. La estructura de módulos corresponde a Task 01.

## Pasos para el editor y Unity Cloud

Actualización: la instalación de los pasos 2 a 4 ya fue realizada por el agente con autorización de Alain. Alain confirmó que Console no muestra errores y que los servicios están configurados. No es necesario reinstalar paquetes.

1. Abre el proyecto existente con Unity `6000.3.27f2`. No aceptes una migración de versión como parte de esta tarea.
2. Abre **Window > Package Manager**. Selecciona **Unity Registry**.
3. Instala **Netcode for GameObjects**, **Multiplayer Services**, **Multiplayer Play Mode**, **Cinemachine**, **ProBuilder** y **Cloud Save**. Usa la versión compatible que ofrezca Package Manager para este editor. Si no aparece el nombre, usa el botón **+ > Install package by name** con el identificador de la tabla. Deja que Unity resuelva las dependencias; no fuerces versiones inventadas.
4. Comprueba que Authentication quede instalado como dependencia. No añadas los SDK antiguos independientes de Relay y Lobby al instalar Multiplayer Services.
5. Espera a que terminen la resolución de paquetes, la importación y la compilación.
6. En **Edit > Project Settings > Services**, comprueba que el proyecto vinculado sea el correcto para Atraco3D.
7. En Unity Dashboard, dentro de ese mismo proyecto, completa la configuración inicial que soliciten **Relay**, **Lobby** y **Cloud Save**. Verifica **Authentication** para el inicio de sesión anónimo previsto en Task 02. Alain confirmó esta configuración durante el cierre de Task 00; la conectividad real se probará en Task 02.
8. Comprueba que la ventana Project muestre `Assets/Party`. No hace falta crear escenas ni prefabs en Task 00.

## Cómo probarlo

1. En Package Manager, filtra **In Project** y comprueba todos los paquetes de la tabla. Authentication puede aparecer como dependencia.
2. Abre **Window > General > Console**. Espera a que Unity termine y verifica que no haya errores rojos de compilación o resolución de paquetes. Si hay errores, comparte el texto exacto.
3. Comprueba que aparezca el menú o ventana **Multiplayer Play Mode**. La prueba de conexión entre dos jugadores corresponde a Task 02; aún no existe el prototipo necesario.
4. Comprueba en Unity Dashboard el estado de los servicios del proyecto correcto.
5. Resultado comunicado por Alain: Console sin errores y servicios configurados. El agente volvió a verificar los paquetes, los archivos instalados y el repositorio. La versión `6000.3.27f2` está confirmada y el GDD integrado.

Task 00 marcada como `[x]` tras la confirmación de Alain. Su cierre se registra con `task-00: preparar entorno de desarrollo`. Task 01 sigue pendiente.

## Explicación para aprender

El manifiesto declara los paquetes solicitados y el archivo de bloqueo registra sus versiones resueltas. Ambos describen mejor el entorno real que una lista escrita previamente. Git guarda los archivos fuente; `.gitignore` evita guardar cachés que Unity puede regenerar. Los archivos `.meta` conservan la identidad de los assets y sí deben guardarse. Esta tarea prepara el entorno: todavía no aplica patrones de juego ni clases SOLID. La separación de responsabilidades empezará en Task 01.

## Referencias oficiales

- [Unity 6.3: instalar un paquete por nombre](https://docs.unity3d.com/6000.3/Documentation/Manual/upm-ui-quick.html).
- [Instalar Multiplayer Services y relación con Lobby y Relay](https://docs.unity.com/en-us/mps-sdk/install-and-upgrade).
- [Instalar Cloud Save, Authentication y vincular el proyecto](https://docs.unity.com/en-us/cloud-save/get-started).
