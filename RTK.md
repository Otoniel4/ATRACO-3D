# RTK en Atraco3D

RTK se usa explícitamente en cada comando de terminal. No es necesario configurar hooks globales para este flujo.

```powershell
rtk gain
rtk git status --short
rtk git diff
rtk read AGENTS.md
rtk read Packages/manifest.json
rtk bypass rg --files Assets
rtk bypass rg -n 'patron' Assets/Party
```

`rtk read` usa contenido completo por defecto (`--level none`). Para revisar código y documentos fuente no aplicar filtros que omitan requisitos.

En Windows, `rtk ls` puede fallar si no existe `ls` en PATH. Usar PowerShell a través de `rtk bypass`, con argumentos literales o un archivo `.ps1` revisado:

```powershell
rtk bypass powershell -NoProfile -Command 'Get-ChildItem -LiteralPath Assets'
rtk bypass powershell -NoProfile -File C:\ruta\script-revisado.ps1
```

`rtk bypass` ejecuta sin filtrar, manteniendo el registro de uso. Evitar cadenas anidadas con interpolación de PowerShell.

Respetar los permisos del espacio de trabajo. No ejecutar `rtk init -g` ni modificar ajustes globales como parte de una tarea del proyecto.

Git: un commit por tarea después de la prueba y confirmación de Alain. No añadir Library, Temp, Logs, UserSettings ni archivos generados del IDE.
