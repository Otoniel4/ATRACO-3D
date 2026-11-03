import alarmart as a
import bpy
import math

a.new_scene("ExtraDesigns")
names=[]
for name,template,shirt in [("Disguise_Chicken","Civilian_01","Mustard"),("Disguise_Tourist","Civilian_03","Coral"),("Disguise_PizzaCourier","Civilian_02","Terracotta"),("Disguise_Construction","Civilian_01","Mustard"),("Disguise_Grandparent","Civilian_03","Cream")]:
    root=a.begin(name,"Characters");names.append(name)
    instance=a.clone(template,name+"_Wearer",(0,0,0))
    for obj in a.descendants(instance):
        if obj.type=="MESH" and ("Shirt" in obj.name or "Sleeve" in obj.name):
            obj.material_slots[0].link="OBJECT";obj.material_slots[0].material=a.mat(shirt)
    root["RigStatus"]="Static costume; Mixamo rig and weights pending"
    if name.endswith("Chicken"):
        a.sphere("ChickenBody",(0,0,1.12),(.33,.28,.43),"Mustard",2)
        a.sphere("ChickenHood",(0,0,1.68),(.19,.17,.19),"Mustard",2)
        a.mesh("Beak",[(-.08,-.16,1.63),(.08,-.16,1.63),(0,-.33,1.61),(-.08,-.16,1.57),(.08,-.16,1.57)],[(0,1,2),(3,2,4),(0,2,3),(1,4,2),(0,3,4,1)],"Apricot")
        for y in [-.07,0,.07]:a.sphere("Comb",(0,y,1.89),(.045,.05,.065),"PoliceRed",1)
        for side in [-1,1]:
            a.sphere("CostumeWing",(side*.48,0,1.4),(.24,.08,.11),"Mustard",1)
            a.sphere("ChickenEye",(side*.075,-.153,1.73),(.035,.02,.04),"Ivory",2)
            a.sphere("Pupil",(side*.075,-.172,1.73),(.015,.008,.022),"Rubber",1)
    elif name.endswith("Tourist"):
        a.cyl("SunHat",(0,0,1.78),.16,.10,"Cream",12)
        a.cyl("HatBrim",(0,0,1.73),.24,.025,"Cream",12)
        a.box("Camera",(0,-.23,1.14),(.22,.10,.14),"Navy",.02)
        a.cyl("CameraLens",(0,-.30,1.14),.055,.08,"Metal",12,(math.pi/2,0,0))
        a.beam("CameraStrapL",(-.09,-.17,1.17),(-.04,-.12,1.45),.008,"Rubber")
        a.beam("CameraStrapR",(.09,-.17,1.17),(.04,-.12,1.45),.008,"Rubber")
    elif name.endswith("PizzaCourier"):
        a.box("PizzaBox",(.84,-.03,1.37),(.42,.42,.065),"Cream",.015)
        a.text("PizzaLogo","PIZZA",(.84,-.03,1.406),.085,"Terracotta",rotation=(0,0,0))
    elif name.endswith("Construction"):
        a.cyl("Helmet",(0,0,1.77),.15,.12,"Mustard",12)
        a.cyl("HelmetBrim",(0,0,1.72),.19,.025,"Mustard",12)
        for x in [-.13,.13]:a.box("ReflectiveStripe",(x,-.17,1.15),(.04,.02,.43),"Ivory",.003)
        cone=a.clone("TrafficCone","CarriedCone",(-.83,0,1.13));cone.scale=(.4,.4,.4)
    else:
        for obj in a.descendants(instance):
            if obj.type=="MESH" and "Hair" in obj.name:
                obj.material_slots[0].link="OBJECT";obj.material_slots[0].material=a.mat("Ivory")
        a.beam("WalkingCane",(.79,-.02,.04),(.79,-.02,1.4),.025,"Wood",10)
        a.beam("CaneHandle",(.79,-.02,1.4),(.79,-.14,1.4),.026,"Wood",10)
    a.export_asset(name)

a.begin("Vehicle_ArmoredTruck","Vehicles");names.append("Vehicle_ArmoredTruck")
a.box("Chassis",(0,0,.55),(2.15,5.8,.30),"Navy",.05)
a.box("Cab",(0,-1.65,1.28),(2.1,1.9,1.55),"Teal",.09)
a.box("Windshield",(0,-2.62,1.6),(1.7,.035,.65),"Glass",.025)
a.box("CargoVault",(0,1.05,1.58),(2.2,3.7,2.25),"Metal",.05)
for side,x in [("L",-1.08),("R",1.08)]:
    for label,y in [("F",-1.75),("R",1.9)]:
        pivot=a.empty("Wheel_"+label+side,(x,y,.42))
        a.cyl("Tire",(0,0,0),.42,.27,"Rubber",12,(0,math.pi/2,0),parent=pivot)
        a.cyl("Hub",(-.145 if side=="L" else .145,0,0),.24,.025,"Metal",10,(0,math.pi/2,0),parent=pivot)
    door=a.empty("Door_"+side,(x,-2.35,1.3));a.box("DoorPanel",(0,.55,0),(.06,1.05,1.28),"Teal",.018,parent=door)
for x in [-.52,.52]:
    door=a.empty("RearDoorPivot",(x*2,2.94,1.5));a.box("RearDoor",(-x,0,0),(1.0,.08,1.9),"Navy",.02,parent=door)
    a.box("Headlight",(x,-2.64,.92),(.32,.05,.18),"Ivory",.025)
a.empty("Seat_Driver",(-.5,-1.65,.8));a.empty("LootVaultPoint",(0,1,1.1));a.export_asset(names[-1])

a.begin("Vehicle_PoliceHelicopter","Vehicles");names.append("Vehicle_PoliceHelicopter")
a.sphere("Fuselage",(0,0,1.35),(.95,1.7,.8),"Navy",2)
a.sphere("Canopy",(0,-1.05,1.53),(.78,.75,.58),"Glass",2)
a.beam("TailBoom",(0,1.0,1.45),(0,4.3,1.75),.19,"Navy",10)
a.mesh("TailFin",[(-.04,3.8,1.65),(-.04,4.4,1.65),(-.04,4.3,2.75),(.04,3.8,1.65),(.04,4.4,1.65),(.04,4.3,2.75)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],"Teal")
rotor=a.empty("MainRotorPivot",(0,0,2.35));a.cyl("RotorMast",(0,0,-.15),.08,.3,"Metal",10,parent=rotor)
for angle in [0,math.pi/2]:a.box("RotorBlade",(0,0,.025),(6.8,.20,.045),"Rubber",.008,rotation=(0,0,angle),parent=rotor)
tail=a.empty("TailRotorPivot",(-.22,4.15,1.85))
for angle in [0,math.pi/2]:a.box("TailBlade",(0,0,0),(.045,1.15,.10),"Rubber",.008,rotation=(angle,0,0),parent=tail)
for side in [-1,1]:
    a.beam("LandingSkid",(side*.95,-1.6,.15),(side*.95,1.2,.15),.06,"Metal",10)
    for y in [-.9,.8]:a.beam("SkidStrut",(side*.60,y,.9),(side*.95,y,.15),.045,"Metal",8)
a.cyl("Searchlight",(0,-1.0,.65),.18,.25,"Ivory",12,rotation=(.35,0,0))
a.ROOT["DynamicState"]="Static art; rotor and searchlight separated; flight not implemented"
a.export_asset(names[-1])
a.begin("Road_PoliceBarricade","City");names.append("Road_PoliceBarricade")
for x in [-1.1,1.1]:a.box("Leg",(x,0,.5),(.1,.6,1.0),"Metal",.015)
for i in range(8):a.box("Stripe",(-1.4+i*.4,0,.80),(.4,.13,.30),"Ivory" if i%2 else "PoliceRed",.008)
a.export_asset(names[-1])
a.arrange(names,4,(4.4,6.5));a.studio_floor((6.6,4),16);a.camera((6.5,3.5,1),(15,-22,20),26)
a.save_library();print("EXTRA_DESIGNS_CREATED",len(names))
