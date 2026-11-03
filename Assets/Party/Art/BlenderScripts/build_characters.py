import alarmart as a
import bpy
import bmesh
import math

a.new_scene("Characters")
names=[]
for name,female,height in [("BaseMale_TPose",False,1.75),("BaseFemale_TPose",True,1.68)]:
    a.begin(name,"Characters");names.append(name)
    parts=[]
    def form(label,point,size):
        obj=a.sphere(label,point,size,"SkinMedium",2);parts.append(obj);return obj
    form("Pelvis",(0,0,.86),(.205 if female else .19,.13,.18))
    form("Waist",(0,0,1.03),(.145 if female else .18,.12,.22))
    form("Chest",(0,0,1.25),(.215 if female else .24,.14,.24))
    form("Neck",(0,0,1.49),(.065,.065,.11))
    form("Head",(0,-.005,1.64),(.125,.12,.155))
    for side in [-1,1]:
        parts.append(a.beam("Thigh",(side*.1,0,.85),(side*.105,0,.49),.092 if female else .095,"SkinMedium",10))
        form("Knee",(side*.105,-.004,.46),(.075,.077,.088))
        parts.append(a.beam("Shin",(side*.105,0,.46),(side*.11,0,.14),.065,"SkinMedium",10))
        form("Foot",(side*.11,-.065,.075),(.075,.155,.075))
        shoulder=.20 if female else .22
        parts.append(a.beam("UpperArm",(side*shoulder,0,1.40),(side*.48,0,1.40),.067,"SkinMedium",10))
        form("Elbow",(side*.48,0,1.40),(.06,.06,.06))
        parts.append(a.beam("Forearm",(side*.48,0,1.40),(side*.74,0,1.40),.05,"SkinMedium",10))
        form("Hand",(side*.79,-.015,1.40),(.075,.045,.045))
        form("Thumb",(side*.755,-.055,1.36),(.04,.035,.035))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts: part.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    body=bpy.context.object;body.name=name+"_Body"
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    remesh=body.modifiers.new("Unified closed body","REMESH")
    remesh.mode="VOXEL";remesh.voxel_size=.018;remesh.use_smooth_shade=False
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    decimate=body.modifiers.new("Low-poly body","DECIMATE")
    decimate.ratio=.24;decimate.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    low=min(v.co.z for v in body.data.vertices);high=max(v.co.z for v in body.data.vertices)
    scale=height/(high-low)
    for vertex in body.data.vertices:
        vertex.co.x*=scale;vertex.co.y*=scale;vertex.co.z=(vertex.co.z-low)*scale
    bm=bmesh.new();bm.from_mesh(body.data)
    nonmanifold=sum(not edge.is_manifold for edge in bm.edges);bm.free()
    if nonmanifold:raise RuntimeError(name+" has non-manifold edges: "+str(nonmanifold))
    a.ROOT["RigStatus"]="Unrigged closed T-pose body; waiting for Mixamo"
    a.ROOT["BodyHeightMeters"]=height
    a.ROOT["NonManifoldEdges"]=nonmanifold
    a.export_asset(name)

def outfit(name,female,shirt,pants,skin,hair,style,uniform=None):
    root=a.begin(name,"Characters");names.append(name)
    base="BaseFemale_TPose" if female else "BaseMale_TPose"
    instance=a.clone(base,name+"_Base",(0,0,0))
    for item in a.descendants(instance):
        if item.type=="MESH":
            item.material_slots[0].link="OBJECT";item.material_slots[0].material=a.mat(skin)
    s=1.68/1.75 if female else 1
    verts=[(-.21,-.15,.86),(.21,-.15,.86),(.21,.15,.86),(-.21,.15,.86),(-.25,-.16,1.43),(.25,-.16,1.43),(.25,.16,1.43),(-.25,.16,1.43)]
    a.mesh("Shirt",[(x*s,y*s,z*s) for x,y,z in verts],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],shirt)
    for side in [-1,1]:
        a.beam("Sleeve",(side*.20*s,0,1.40*s),(side*(.67 if style=="jacket" else .38)*s,0,1.40*s),.084*s,shirt,10)
        if not (female and style=="skirt"):
            a.beam("PantsLeg",(side*.105*s,0,.84*s),(side*.11*s,0,.15*s),.103*s,pants,10)
        a.box("Shoe",(side*.11*s,-.065*s,.075*s),(.17*s,.31*s,.13*s),"Navy",.025)
    if female and style=="skirt":
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.29*s,radius2=.21*s,depth=.43*s)
        skirt=a.link(bpy.context.object,"Skirt",pants);skirt.location=(0,0,.68*s)
    a.box("Belt",(0,0,.88*s),(.45*s,.31*s,.045*s),"Navy",.01)
    for x in [-.047,.047]:
        a.sphere("EyeWhite",(x*s,-.116*s,1.635*s),(.030*s,.016*s,.027*s),"Ivory",2)
        a.sphere("EyePupil",(x*s,-.133*s,1.635*s),(.012*s,.008*s,.015*s),"HairBlack",1)
    a.sphere("Nose",(0,-.135*s,1.59*s),(.021*s,.03*s,.025*s),skin,1)
    a.box("Mouth",(0,-.12*s,1.548*s),(.044*s,.009*s,.009*s),"Terracotta",.002)
    a.sphere("HairCap",(0,.005*s,1.735*s),(.133*s,.123*s,.085*s),hair,2)
    if style in ["jacket","skirt"]:
        for x in [-.1,.1]:a.sphere("HairSide",(x*s,.04*s,1.59*s),(.055*s,.10*s,.16*s),hair,1)
    if style=="cap" or uniform:
        a.cyl("CapCrown",(0,0,1.775*s),.14*s,.09*s,"Navy" if uniform else shirt,12)
        a.box("CapVisor",(0,-.13*s,1.74*s),(.26*s,.18*s,.025*s),"Navy" if uniform else shirt,.015)
    if style=="glasses":
        for x in [-.05,.05]:a.torus("GlassesFrame",(x*s,-.145*s,1.635*s),.035*s,.005*s,"Navy",rotation=(math.pi/2,0,0),scale=(1,1,.75))
        a.beam("GlassesBridge",(-.015*s,-.145*s,1.635*s),(.015*s,-.145*s,1.635*s),.005,"Navy")
    if style=="jacket":
        a.box("JacketOpening",(0,-.17*s,1.16*s),(.075*s,.015*s,.48*s),"Cream",.003)
    if uniform:
        a.box("Badge",(-.12,-.17,1.29),(.065,.018,.08),"Mustard",.008)
        a.box("Radio",(.14,-.17,1.12),(.075,.04,.12),"Rubber",.01)
        a.cyl("RadioAntenna",(.14,-.17,1.24),.006,.12,"Rubber",6)
    if uniform=="guard":
        a.beam("GuardBaton",(.79,-.04,1.40),(.79,-.04,.86),.026,"Rubber",10)
    if uniform=="police":
        a.clone("Weapon_Pistol","PoliceHolsteredPistol",(.25,0,.69))
    if uniform=="player":
        a.box("Mask",(0,-.15,1.61),(.24,.04,.09),"Rubber",.025)
        for x in [-.047,.047]:a.sphere("MaskEye",(x,-.179,1.635),(.028,.012,.023),"Ivory",1)
        a.box("Backpack",(0,.19,1.12),(.30,.20,.43),"Teal",.04)
    root["RigStatus"]="Visual composition; Mixamo skeleton and clothing weight transfer pending"
    root["BaseBody"]=base
    root["OutfitStyle"]=style
    a.export_asset(name)

colors=[("Coral","Navy","SkinLight","HairBrown","short"),("Teal","Wood","SkinMedium","HairBlack","cap"),("Mustard","Navy","SkinDeep","HairBlack","glasses"),("Cream","Teal","SkinMedium","HairBrown","jacket"),("Berry","Navy","SkinLight","HairGold","skirt")]
for index in range(10):
    shirt,pants,skin,hair,style=colors[index%5]
    outfit("Civilian_%02d"%(index+1),index>=5,shirt,pants,skin,hair,style)
outfit("Character_Guard",False,"Metal","Navy","SkinMedium","HairBlack","short","guard")
outfit("Character_Police",False,"PoliceBlue","Navy","SkinDeep","HairBlack","short","police")
outfit("Character_Player",False,"Terracotta","Navy","SkinLight","HairBrown","jacket","player")
a.arrange(names,5,(2.25,2.3))
a.studio_floor((4.5,2.3),9)
a.camera((4.5,2.2,.85),(5,-12,8),13.8)
a.save_library()
print("CHARACTERS_CREATED",len(names),"two closed manifold bases and 13 unrigged visual compositions")
