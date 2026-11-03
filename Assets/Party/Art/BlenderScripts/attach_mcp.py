import sys
sys.dont_write_bytecode = True
import sys
import traceback
from pathlib import Path
LOG=Path(r"C:\Users\Alain\Documents\Codex\2026-10-31\pued\work\blender-resume.log").open("w",encoding="utf-8",buffering=1)
sys.stdout=LOG
sys.stderr=LOG
try:
    import bpy
    import addon_utils
    import json
    ART=Path(r"C:\Users\Alain\Atraco3D\Assets\Party\Art")
    addon_utils.modules_refresh()
    module=addon_utils.enable("blender_mcp",default_set=True,persistent=True)
    if module is None:raise RuntimeError("Addon could not be enabled")
    bpy.ops.blendermcp.start_server()
    folder=str(ART/"BlenderScripts")
    if folder not in sys.path:sys.path.insert(0,folder)
    import alarmart
    for entry in json.loads((ART/"BlenderScripts/asset_catalog.json").read_text(encoding="utf-8")):
        root=bpy.data.objects.get(entry["name"])
        if root:
            alarmart.CATALOG[entry["name"]]={**entry,"root":root,"collection":root.users_collection[0]}
    print("ALARMA_RESUMED",len(alarmart.CATALOG),"entries, server",bpy.context.scene.blendermcp_server_running)
except Exception:
    traceback.print_exc()
