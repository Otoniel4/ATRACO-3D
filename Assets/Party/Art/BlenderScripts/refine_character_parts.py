import alarmart as a
import bpy
import math

bpy.context.window.scene=bpy.data.scenes["Alarma_Characters"]
for name,entry in list(a.CATALOG.items()):
    if entry["category"]!="Characters" or name.startswith("Base"):continue
    for obj in entry["root"].children:
        if obj.name.split('.')[0]!="Shirt":continue
        materials=[slot.material for slot in obj.material_slots]
        female=entry["root"].get("BaseBody")=="BaseFemale_TPose";s=1.68/1.75 if female else 1
        rings=[(.86,.21,.15),(1.04,.20,.15),(1.30,.255,.17),(1.43,.245,.15)]
        verts=[(math.cos(i*math.tau/10)*rx*s,math.sin(i*math.tau/10)*ry*s,z*s) for z,rx,ry in rings for i in range(10)]
        faces=[tuple(reversed(range(10))),tuple(range(30,40))]
        for ring in range(3):
            for i in range(10):faces.append((ring*10+i,ring*10+(i+1)%10,(ring+1)*10+(i+1)%10,(ring+1)*10+i))
        data=bpy.data.meshes.new(name+"_FittedShirt");data.from_pydata(verts,[],faces);data.update()
        for material in materials:data.materials.append(material)
        obj.data=data
    a.export_asset(name)

parts=[
    ("Modular_Male_Shirt","Civilian_01",["Shirt","Sleeve"]),
    ("Modular_Female_Shirt","Civilian_06",["Shirt","Sleeve"]),
    ("Modular_Male_Trousers","Civilian_01",["PantsLeg","Belt"]),
    ("Modular_Female_Trousers","Civilian_06",["PantsLeg","Belt"]),
    ("Modular_Female_Skirt","Civilian_10",["Skirt","Belt"]),
    ("Modular_Male_Jacket","Civilian_04",["Shirt","Sleeve","JacketOpening"]),
    ("Modular_Female_Jacket","Civilian_09",["Shirt","Sleeve","JacketOpening"]),
    ("Modular_Hair_Short","Civilian_01",["HairCap"]),
    ("Modular_Hair_Long","Civilian_10",["HairCap","HairSide"]),
    ("Modular_Cap","Civilian_02",["CapCrown","CapVisor"]),
    ("Modular_Glasses","Civilian_03",["GlassesFrame","GlassesBridge"]),
    ("Modular_Guard_Uniform","Character_Guard",["Shirt","Sleeve","PantsLeg","Belt","Badge","Radio","RadioAntenna","CapCrown","CapVisor"]),
    ("Modular_Police_Uniform","Character_Police",["Shirt","Sleeve","PantsLeg","Belt","Badge","Radio","RadioAntenna","CapCrown","CapVisor"]),
    ("Modular_Player_Mask","Character_Player",["Mask","MaskEye"]),
    ("Modular_Shoes","Civilian_01",["Shoe"]),
]
for name,template,prefixes in parts:
    source=a.CATALOG[template]["root"]
    a.begin(name,"Characters")
    for obj in source.children:
        if obj.name.split('.')[0] in prefixes:
            copy=obj.copy();a.COLLECTION.objects.link(copy);copy.parent=a.ROOT
    a.ROOT["RigStatus"]="Modular geometry aligned to source T-pose; weight transfer pending Mixamo"
    a.ROOT["Template"]=template
    a.export_asset(name)
    # Las piezas sueltas se conservan en una colección oculta en la galería.
    for obj in a.descendants(a.ROOT):obj.hide_set(True)
a.save_library()
print("CHARACTERS_REFINED_AND_MODULAR_PARTS_EXPORTED",len(parts))
