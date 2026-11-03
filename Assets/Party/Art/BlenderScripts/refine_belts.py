import alarmart as a
import bpy
import math
updated=[]
for name,entry in a.CATALOG.items():
    if entry["category"]!="Characters":continue
    root=entry["root"];changed=False
    for obj in a.descendants(root):
        if obj.type!="MESH" or not obj.name.split('.')[0].endswith("Belt") or obj.get("FittedBelt"):continue
        width=max(vertex.co.x for vertex in obj.data.vertices)-min(vertex.co.x for vertex in obj.data.vertices)
        scale=width/.45
        verts=[]
        for i in range(12):
            angle=i*math.tau/12
            for rx,ry,z in [(.218,.158,-.021),(.218,.158,.021),(.199,.139,.021),(.199,.139,-.021)]:
                verts.append((math.cos(angle)*rx*scale,math.sin(angle)*ry*scale,z*scale))
        faces=[]
        for i in range(12):
            for j in range(4):faces.append((i*4+j,((i+1)%12)*4+j,((i+1)%12)*4+(j+1)%4,i*4+(j+1)%4))
        data=bpy.data.meshes.new(name+"_FittedBelt");data.from_pydata(verts,[],faces);data.materials.append(a.mat("Navy"));data.update()
        obj.data=data;obj["FittedBelt"]=True;changed=True
    if changed:
        bpy.context.window.scene=root.users_scene[0]
        a.export_asset(name);updated.append(name)
bpy.context.window.scene=bpy.data.scenes["Alarma_CityMap_6x6"]
a.save_library();print("BELT_SILHOUETTES_REFINED",len(updated))
