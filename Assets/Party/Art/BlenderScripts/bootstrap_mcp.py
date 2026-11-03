import sys
sys.dont_write_bytecode = True
"""Activar el puente revisado en una sesión nueva, sin tocar la sesión anterior."""
import addon_utils
import bpy
import json
from pathlib import Path

addon_utils.modules_refresh()
module = addon_utils.enable("blender_mcp", default_set=True, persistent=True)
if module is None:
    raise RuntimeError("No se pudo activar blender_mcp; revisar el registro de Blender")

scene = bpy.data.scenes.new("Alarma_Workshop")
if bpy.context.window:
    bpy.context.window.scene = scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
disabled = []
for item in bpy.data.scenes:
    for prop in ("polyhaven", "sketchfab", "polypizza", "hyper3d", "hunyuan3d", "meshy", "tripo"):
        name = "blendermcp_use_" + prop
        if hasattr(item, name):
            setattr(item, name, False)
            disabled.append(name)

bpy.ops.wm.save_userpref()
bpy.ops.blendermcp.start_server()
status = {"blender": bpy.app.version_string, "scene": scene.name, "server_running": scene.blendermcp_server_running, "download_integrations_disabled": sorted(set(disabled))}
Path(r"C:\Users\Alain\Documents\Codex\2026-10-31\pued\work\blender-bootstrap-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
print("ALARMA_MCP_READY", json.dumps(status))
