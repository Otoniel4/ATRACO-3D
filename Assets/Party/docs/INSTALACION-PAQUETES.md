# Atraco3D — Instalación de paquetes de Task 00

Fecha: 31 de octubre de 2026. Unity conservado: **6000.3.27f2**.

## Resultado

Los cinco paquetes faltantes se añadieron al manifiesto y el editor abierto los descargó del registro oficial de Unity. Cinemachine ya estaba instalado como dependencia del paquete de personajes y animación. Authentication quedó instalado como dependencia de los servicios. No se instalaron los antiguos SDK independientes de Lobby y Relay.

| Paquete | Versión resuelta y descargada |
| --- | --- |
| Netcode for GameObjects | `2.13.3` |
| Multiplayer Services | `2.4.1` |
| Multiplayer Play Mode | `2.0.2` |
| ProBuilder | `6.1.4` |
| Cloud Save | `3.4.2` |
| Cinemachine | `3.1.7` |
| Authentication | `3.8.0` |

## Verificación

- Las siete versiones aparecen en `Packages/packages-lock.json` y sus archivos están en `Library/PackageCache`.
- Unity completó la resolución de paquetes y una recarga de ensamblados después de recompilar.
- No se detectaron errores `CS` de compilación ni mensajes de compilación fallida en el tramo del registro generado durante la instalación.
- El registro contiene un aviso de Cinemachine sobre una referencia de ensamblado de muestras HDRP sin destino. El proyecto usa URP; la recompilación y la importación terminaron. No se modificaron archivos de paquetes para ocultar ese aviso.
- Se conservaron todas las dependencias directas que existían antes de instalar.
- `ProjectSettings/ProjectVersion.txt` permanece idéntico a la copia anterior.
- Se guardaron copias de seguridad del manifiesto, archivo de bloqueo y versión del editor en la carpeta de trabajo de esta sesión.
- No se ejecutó el juego ni se probó la conexión online.

## Archivos modificados o creados

- `C:\Users\Alain\Atraco3D\Packages\manifest.json`: cinco nuevas dependencias directas.
- `C:\Users\Alain\Atraco3D\Packages\packages-lock.json`: actualizado por Unity al resolver paquetes.
- `C:\Users\Alain\Atraco3D\AGENTS.md` y `C:\Users\Alain\Atraco3D\CLAUDE.md`: estado de paquetes actualizado.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\TASK-00-Entorno.md`: informe de entorno actualizado.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\GDD-REVISION.md`: estado de instalación actualizado.
- `C:\Users\Alain\Atraco3D\Assets\Party\docs\INSTALACION-PAQUETES.md` y su `.meta`: este informe.

Unity también genera archivos de caché, ensamblados y registros ignorados por Git.

## Pasos para Alain y cómo probarlo

1. En Unity, abre Package Manager y comprueba que los seis paquetes solicitados aparezcan en **In Project**. Los paquetes transitivos pueden aparecer bajo sus dependencias.
2. Abre **Window > General > Console** y comprueba el estado actual; comparte el texto exacto de cualquier error rojo.
3. Comprueba en el proyecto correcto de Unity Cloud la configuración de Relay, Lobby, Cloud Save y Authentication. Instalar un SDK no acredita la activación de su servicio en la cuenta.
4. Alain confirmó que Console no muestra errores y que los servicios están configurados. Task 00 se cierra con esa validación; Task 01 no se ha iniciado. La conexión online todavía no se ha probado.

## Explicación para aprender

El manifiesto solicita paquetes y Unity resuelve las versiones concretas de sus dependencias en el archivo de bloqueo. Authentication se añade porque los servicios lo necesitan. La descarga local y la configuración de Unity Cloud son pasos distintos. Esta tarea modifica el entorno y todavía no introduce código de juego ni patrones de arquitectura.

## Referencias oficiales

- [Manifiesto de proyecto en Unity 6.3](https://docs.unity3d.com/6000.3/Documentation/Manual/upm-manifestPrj.html).
- [Instalación del SDK de Multiplayer Services](https://docs.unity.com/en-us/mps-sdk/install-and-upgrade).
