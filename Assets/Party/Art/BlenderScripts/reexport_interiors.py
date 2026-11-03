import alarmart as a
import bpy
bpy.context.window.scene=bpy.data.scenes["Alarma_Interiors"]
names=[name for name in a.CATALOG if name.startswith("Interior_")]
for name in names:a.export_asset(name)
a.save_library()
print("INTERIORS_REEXPORTED_WITH_MATERIALS",len(names))
