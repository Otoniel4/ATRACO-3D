import alarmart as a
import bpy
import json
from pathlib import Path

for scene in bpy.data.scenes:
    if scene.name.startswith("Alarma_"):
        scene.view_settings.view_transform="Standard"
        scene.view_settings.exposure=.25
bpy.context.window.scene=bpy.data.scenes["Alarma_StyleGuide"]
names=[]
for index,color in enumerate(a.PALETTE):
    name="Palette_"+color;names.append(name)
    if name not in a.CATALOG:
        a.begin(name,"Materials")
        a.box("ColorChip",(0,0,.1),(.75,.6,.2),color,.04)
        a.text("Label",color.upper(),(0,-.32,.08),.07,"Navy")
a.arrange(names,6,(1,1));a.camera((2.5,1.5,0),(4,-7,9),8.2)
manifest=[{"name":name,"scene":entry["root"].users_scene[0].name,"category":entry["category"],"file":entry["file"]} for name,entry in a.CATALOG.items() if "file" in entry]
(Path(__file__).resolve().parent / "art-qa-manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
a.save_library()
print("QA_MANIFEST_READY",len(manifest),"exported assets; palette",len(a.PALETTE))
