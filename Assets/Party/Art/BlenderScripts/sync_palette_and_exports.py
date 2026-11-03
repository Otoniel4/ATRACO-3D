import alarmart as a
import bpy

for name,hex_color in a.PALETTE.items():
    color=tuple(a.linear(int(hex_color[i:i+2],16)/255) for i in (0,2,4))
    material=a.mat(name)
    material.diffuse_color=(*color,1)
    shader=next(node for node in material.node_tree.nodes if node.type=="BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value=(*color,1)
exports=[name for name,entry in a.CATALOG.items() if "file" in entry]
for name in exports:
    bpy.context.window.scene=a.CATALOG[name]["root"].users_scene[0]
    a.export_asset(name)
bpy.context.window.scene=bpy.data.scenes["Alarma_CityMap_6x6"]
a.save_library()
print("PALETTE_AND_EXPORTS_SYNCHRONIZED",len(a.PALETTE),len(exports))
