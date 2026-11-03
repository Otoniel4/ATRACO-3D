$ErrorActionPreference='Stop'
$blenderExecutable='C:\Users\Alain\Documents\Codex\2026-10-31\pued\work\blender45-portable\blender-4.5.15-windows-x64\blender.exe'
$reviewDirectory=$PSScriptRoot
$helper=Start-Process -FilePath $blenderExecutable -ArgumentList @('--python',"$reviewDirectory\viewport_capture.py") -WindowStyle Hidden -PassThru -RedirectStandardOutput "$reviewDirectory\viewport.log" -RedirectStandardError "$reviewDirectory\viewport_error.log"
Write-Output "ISOLATED_VIEWPORT_PID $($helper.Id)"
