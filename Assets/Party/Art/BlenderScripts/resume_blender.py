import bpy
import json
import sys
from pathlib import Path

ART=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(ART/"BlenderSources~/Alarma_ArtLibrary.blend"))
script_folder=str(ART/"BlenderScripts")
if script_folder not in sys.path:sys.path.insert(0,script_folder)
import alarmart
for entry in json.loads((ART/"BlenderScripts/asset_catalog.json").read_text(encoding="utf-8")):
    root=bpy.data.objects.get(entry["name"])
    if root:
        alarmart.CATALOG[entry["name"]]={**entry,"root":root,"collection":root.users_collection[0]}
bpy.ops.blendermcp.start_server()
print("ALARMA_RESUMED",len(alarmart.CATALOG),"catalog entries")
