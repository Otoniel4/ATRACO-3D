# Respaldo completo y limpieza autorizada — 2026-11-04

Alain solicitó subir a GitHub el proyecto guardado, incluidos los `.blend` y la escena vigente, y retirar contenido obsoleto. Confirmó que guardó y cerró Unity. Autorizó expresamente los 301 archivos del inventario `Assets/Party/Tools~/cleanup-manifest.json`. Es mantenimiento del respaldo; no cambia el orden ni completa tareas de juego.

## Contenido vigente preservado

- Unity 6000.3.27f2, ciudad de 2 × 2 km, Ciudad 3.0 B1. Escena: `Assets/Party/Generated/Ciudad2km/Scenes/Ciudad_2km.unity`.
- Las 891 dependencias locales transitivas de la escena, con sus archivos `.meta`. Ninguna figura entre los archivos retirados.
- Elenco modular `Art/Characters/Cast`, sus animaciones, `ModularCast.blend` y maestros CC0 Men/Women de Quaternius.
- Kit25, suelo de 64 sectores, siete modelos de locales/escondite, ocho vehículos, armas, herramientas, props, disfraces y tres interiores originales únicos para comisaría, alcantarilla y estacionamiento. El contenido útil para continuar el juego no se elimina por no aparecer todavía en la escena.
- Las once fuentes `.blend` existentes. `Villa_Alarma_R9_Ligera.blend` sigue siendo la fuente de `City25~/export_kit.py`; aunque su nombre sea R9, eliminarla impediría reconstruir el kit actual.
- Scripts, materiales, prefabs, controladores, configuración, referencias, capturas vigentes, GDD, licencias y documentación de aprendizaje.

La escena no fue regenerada ni editada. Huella SHA-256 antes y después de la limpieza:

```text
590a8bf68c9847bdc8c92da303317b842e3899650b26f125778ced6668e93402
```

## Retirada

301 archivos, 130.531.495 bytes, de los cuales 153 estaban versionados:

- 36 modelos del primer kit de ciudad e interiores ya sustituidos, con sus prefabs, metadatos y capturas correspondientes. Incluye el mapa estático antiguo de 6 × 6 km.
- La escena antigua `Scenes/Atraco.unity`, que tenía referencias sin resolver.
- Tres recetas antiguas: `build_city_map.py`, `build_city_kit.py` y `refine_belts.py`, con sus metadatos.
- Capturas de personajes rechazados, piezas modulares antiguas y vehículos reemplazados por v3.
- Cinco `.blend1`, respaldos automáticos de escenas anteriores, registros, cachés de Python y archivos de IDE regenerables.

El inventario enumera ruta, motivo, tamaño y SHA-256 de cada elemento. Los archivos que estaban en Git se recuperan desde el commit anterior `500be7c2ee500e6ebef386a1c4bdd2b2932af01c`. Además se verificó una copia recuperable de los 301 archivos antes de retirarlos:

```text
Library/AlarmaMaintenance/BeforeCleanup_500be7c.zip
SHA-256: 8a72bf83c84f0b991e86b6891edaad3d14dcecc000c55c2b9aee20924923053e
```

Este ZIP de obsoletos queda solo en el equipo actual, fuera del respaldo vigente. No se debe borrar esa copia si se desean conservar los respaldos automáticos antiguos que nunca estuvieron en Git. `Library` continúa excluida y Unity puede regenerar sus cachés.

## Cambios del respaldo

`.gitignore` ya incluye el arte de carpetas `~` y la ciudad generada vigente. Los otros intentos generados, respaldos automáticos y cachés siguen excluidos. Los binarios se almacenan en Git normal; no se depende de una cuota LFS.

GitHub bloquea archivos de más de 100 MiB. Solo la fuente R9 excede ese límite: su archivo original queda local y su ZIP íntegro fragmentado en partes de 48 MiB se guarda junto a ella. `Tools~/backup-manifest.json` registra el archivo original, su SHA-256 y las huellas de los archivos del respaldo. La restauración recupera el original byte por byte. Fuente del límite: [documentación de GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

`City25Builder` usa SHA-256 del contenido de sus once JSON de entrada, normalizando CRLF, en lugar de fechas del sistema. El registro existente se migró sin reconstruir la escena. Así un clon nuevo no la invalida solo porque cambien las fechas de checkout. Se configuró la escena vigente como escena de build, reemplazando SampleScene. Las recetas comunes de arte resuelven la ruta del proyecto desde su propio archivo, sin depender de `C:/Users/Alain/Atraco3D`.

## Recuperación y prueba manual en Unity

1. Clonar el repositorio en otro directorio. Ejecutar `Assets/Party/Tools~/Restore-Project.ps1` desde PowerShell; ver el comando completo en el README de la raíz. Debe terminar con «Respaldo verificado».
2. Instalar Unity 6000.3.27f2. Abrir el clon y esperar la importación y descarga de los paquetes declarados.
3. Abrir `Assets/Party/Generated/Ciudad2km/Scenes/Ciudad_2km.unity`. Comprobar que Console no tiene errores ni objetos con Missing Script.
4. Pulsar Play. Comprobar inicio dentro del escondite, caminar/correr, cámara, puertas con E, mapa con M y menú con Esc.
5. Recorrer una tienda y una avenida: comprobar productos, cajero, compradores, peatones, autos con conductor y semáforos.
6. Salir de Play y pulsar Alarma > Crear y probar juego. Con las mismas entradas debe reutilizar la escena guardada.

El agente no abrió Unity ni ejecutó Play. Esta prueba sigue a cargo de Alain. No se requiere Multiplayer Play Mode para esta comprobación local; Task 02 y la sincronización online siguen pendientes.

## Explicación para aprender

Git necesita guardar la escena y también los archivos que esta referencia; los `.meta` conservan esas conexiones mediante GUID. Las cachés se reconstruyen y no son parte del contenido fuente. El manifiesto aplica una huella SHA-256 a cada archivo para detectar cambios o pérdidas. El ZIP conserva una fuente demasiado grande sin alterar sus bytes. Separar creación, restauración y comprobación mantiene responsabilidades claras; aquí no se añade un patrón de juego nuevo ni se modifican los sistemas del runtime.

## Verificación del respaldo antes de publicar

- Los dos verificadores (PowerShell y Python) comprobaron todos los archivos del manifiesto y la fuente fragmentada.
- Un checkout limpio del índice de Git restauró la fuente grande y verificó el respaldo completo, sin usar Library ni archivos ignorados del proyecto original.
- Las once fuentes `.blend` restauradas coinciden byte por byte con las originales. La escena mantiene su SHA-256 original.
- El registro del constructor sigue coincidiendo después de cambiar fechas y finales de línea de los once JSON en la copia desechable.
- El restaurador rechazó sobrescribir una fuente local distinta y conservó sus bytes, comprobado solo en la copia desechable.
- Compilación de Alarma.City.Editor contra las DLL instaladas superada sin abrir Unity. Las 891 dependencias locales siguen presentes; cero referencias a GUID retirados, cero GUID duplicados y cero archivos importables sin `.meta`.

Estas pruebas comprueban integridad y restauración de archivos; no sustituyen Play ni la revisión visual de Alain.
