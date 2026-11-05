# Alarma — ATRACO 3D

Proyecto Unity **6000.3.27f2**, URP. Estado guardado: ciudad de **2 × 2 km**, Ciudad 3.0 fase B1, escondite enterable, tráfico, peatones, semáforos y locales con compras. B1 sigue pendiente de la prueba de Alain; este respaldo no cierra tareas de juego.

## Recuperar en otro equipo

1. Instalar Git y Unity **6000.3.27f2**. Clonar este repositorio, sin usar una copia de carpetas seleccionadas.
2. Desde la raíz del clon, ejecutar en PowerShell:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Assets\Party\Tools~\Restore-Project.ps1
   ```

   Recupera la fuente `.blend` de más de 100 MiB desde su ZIP y verifica las huellas SHA-256 del respaldo. No necesita Python, Git LFS ni Blender para restaurar. No sobrescribe una fuente local diferente.
3. Abrir el proyecto con esa versión de Unity y esperar la descarga de paquetes y la importación.
4. Abrir `Assets/Party/Generated/Ciudad2km/Scenes/Ciudad_2km.unity` y pulsar Play. También se conserva **Alarma > Crear y probar juego**: su registro usa contenido en lugar de fechas para reutilizar la escena al clonar.

Alternativa con Python 3.10 o posterior:

```powershell
python .\Assets\Party\Tools~\backup_project.py restore
```

Se respaldan la escena y sus dependencias, fuentes de Blender, elenco y packs fuente CC0, FBX, materiales, animaciones, datos, scripts, paquetes declarados, configuración, referencias de diseño y capturas vigentes. `Library`, `Temp`, `Logs`, `UserSettings` y archivos de IDE son datos locales regenerables y no se suben. Las credenciales personales de Unity y la instalación de Blender/MCP se configuran en cada equipo; `.mcp.json` conserva la configuración existente, cuya ruta de `uvx` debe ajustarse si cambia la instalación.

## Mantener el respaldo

Guardar todo y cerrar Unity antes de actualizarlo. Desde la raíz:

```powershell
python .\Assets\Party\Tools~\backup_project.py snapshot
python .\Assets\Party\Tools~\backup_project.py verify
```

Después revisar los cambios, hacer commit y subirlos. `snapshot` actualiza el ZIP y el manifiesto; no confirma ni publica cambios. El manifiesto corresponde a la entrega guardada, por lo que es normal que detecte diferencias tras editar el proyecto hasta actualizarlo de nuevo.

Detalles: [respaldo y limpieza](Assets/Party/docs/RESPALDO-Y-LIMPIEZA.md), [tareas](TASKS.md), [licencias](Assets/Party/docs/LICENSES.md).
