# Mitigación de Search durante la recarga — 2026-11-06

Alain reportó `On demand scheduler requested to import while stopped` al probar la revisión de puertas. La traza leída en `Editor.log` pasa por `UnityEditor.Search.SearchTask.OnBeforeAssemblyReload`, `CancelImmediate`, `SearchDatabase.ProcessIncrementalUpdates` y `AssetDatabaseExperimental.ProduceArtifactAsync`. El indexador intenta producir un artefacto cuando el planificador de importación está detenido durante la recarga. Esta traza concreta procede del código interno de Search; no contiene una llamada de Alarma.

Se mantiene Unity **6000.3.27f2**. Se aplicó una mitigación de configuración local, no un parche del motor ni una garantía de desaparición de cualquier otro error.

## Archivos modificados

- `UserSettings/Search.index`: `roots` pasa de `["Assets", "Packages"]` a `[]`; las demás propiedades se conservan.
- `UserSettings/Search.settings`: `indexOnEditorStartup` pasa de `true` a `false`.
- `Assets/Party/Tools~/SearchRecovery/configure_search.py`: permite aplicar, consultar y restaurar la configuración con el editor cerrado; verifica el respaldo mediante SHA-256.
- Este documento y su `.meta`.

El respaldo original y sus hashes están en `Library/Alarma/SearchRecovery/last-backup.json`. La modificación afecta al índice de búsqueda avanzada de assets y paquetes de este proyecto en este equipo. `UserSettings` es configuración local ignorada por Git; el script y esta guía permiten repetir la medida en otro equipo.

## Fundamento y alcance

Unity 6.3 usa un único índice de búsqueda. Un integrante del equipo de Unity publicó vaciar `roots` en `UserSettings/Search.index` como medida para desactivar el indexado ante un fallo de Search. Aquel reporte describe un fallo relacionado durante la recarga, pero no demuestra que esta versión tenga exactamente el mismo defecto. Aquí la elección se basa además en la traza local observada.

- [Índice de búsqueda en Unity 6.3](https://docs.unity.com/en-us/engine/6000.3/manual/unity-editor/editor-navigating-managing/editor-searching/search-overview/search-indexing/search-index-manager).
- [Mitigación publicada por Unity](https://discussions.unity.com/t/unity-editor-6-3-lts-keeps-crashing/1712397/3).

## Pasos para el editor y prueba

1. Abrir el proyecto con Unity 6000.3.27f2 y esperar a que termine de cargar.
2. En Console, pulsar **Clear** para distinguir mensajes antiguos de nuevos.
3. Pulsar **Alarma → Crear y probar juego**, salir de Play y volver a entrar. Comprobar que no reaparece el mensaje del planificador.
4. Continuar la prueba de entrada/salida del banco. Este ajuste no valida la animación ni sustituye la prueba pendiente de B1.
5. Si el mensaje reaparece, conservar su primera traza completa. No marcar esta mitigación como confirmada hasta que Alain lo pruebe.

El agente comprobó que solo cambian las dos preferencias previstas y que los originales quedan respaldados. No abrió Unity ni ejecutó Play. No hay commit de cierre.

Para consultar o restaurar desde la raíz del proyecto, con RTK disponible:

```powershell
rtk bypass python Assets/Party/Tools~/SearchRecovery/configure_search.py status
rtk bypass python Assets/Party/Tools~/SearchRecovery/configure_search.py restore
```

Restaurar exige cerrar Unity primero. La operación recupera ambas preferencias tal como estaban antes de esta mitigación.

## Explicación para aprender

El índice es una base auxiliar para buscar assets; no es la escena del juego. Unity reconstruye código e índices mediante procesos distintos, y la traza muestra una petición de indexado durante la parada de importación. Desactivar ese índice evita esa vía mientras conservamos la versión del editor. No se añadió lógica al juego ni un patrón nuevo; la herramienta tiene una sola responsabilidad y conserva un respaldo para revertir el cambio.
