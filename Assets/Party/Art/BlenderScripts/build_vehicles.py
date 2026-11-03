import alarmart as a
import bpy
import math

a.new_scene("Vehicles")
names = []
configs = [
    ("Car_Sedan", "Apricot", 4.2, 1.52, "sedan"),
    ("Car_Hatchback", "Teal", 3.65, 1.55, "hatch"),
    ("Car_SUV", "Sage", 4.5, 1.80, "suv"),
    ("Car_Taxi", "Mustard", 4.2, 1.52, "taxi"),
    ("Car_Police", "Navy", 4.35, 1.58, "police"),
]
for name, color, length, height, kind in configs:
    root = a.begin(name, "Vehicles")
    root["RigStatus"] = "Static model; wheels, doors and driver seat ready for later dynamics"
    width = 1.78 if kind != "suv" else 1.92
    wheel_y = length * 0.31
    body = a.box("Body", (0, 0, 0.67), (width, length, 0.65), color, 0.10)
    for y in (-wheel_y, wheel_y):
        cutter = a.cyl("WheelArchCutter", (0, y, 0.35), 0.39, width + 0.4, vertices=12, rotation=(0, math.pi / 2, 0))
        bpy.context.view_layer.objects.active = body
        modifier = body.modifiers.new("Wheel arch", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    a.box("FrontBumper", (0, -length/2 - .015, .48), (width + .05, .14, .18), "Rubber", .03)
    a.box("RearBumper", (0, length/2 + .015, .48), (width + .05, .14, .18), "Rubber", .03)
    a.box("FrontGrille", (0, -length/2 - .071, .73), (.68, .035, .16), "Rubber", .01)
    for x in (-width * .33, width * .33):
        a.box("Headlight", (x, -length/2 - .072, .83), (.32, .04, .16), "Ivory", .025)
        a.box("TailLight", (x, length/2 + .075, .80), (.30, .04, .15), "PoliceRed", .02)
    roof_top = height - .08
    cabin_bottom = .99
    roof_front = -.54 if kind != "suv" else -.68
    roof_back = .65 if kind not in ("hatch", "suv") else length * .34
    glass_vertices = [(-width*.43,-1.04,cabin_bottom),(width*.43,-1.04,cabin_bottom),(width*.35,roof_front,roof_top),(-width*.35,roof_front,roof_top),(-width*.43,length*.32,cabin_bottom),(width*.43,length*.32,cabin_bottom),(width*.35,roof_back,roof_top),(-width*.35,roof_back,roof_top)]
    a.mesh("WindowCabin", glass_vertices, [(0,1,2,3),(4,7,6,5),(0,3,7,4),(1,5,6,2),(3,2,6,7)], "Glass")
    a.box("Roof", (0, (roof_front+roof_back)/2, roof_top+.035), (width*.72, roof_back-roof_front+.12, .08), color, .035)
    for side, x in (("L", -width*.51), ("R", width*.51)):
        for front, y in ((True,-.53), (False,.56)):
            label = "F" if front else "R"
            hinge_y = y - .48
            door = a.empty("Door_"+label+side, (x,hinge_y,.98))
            a.box("DoorPanel_"+label+side, (0,.49,-.18), (.07,.94,.52), "Ivory" if kind == "police" else color, .018, parent=door)
            a.box("DoorHandle_"+label+side, ((-.045 if side=="L" else .045),.78,.02), (.035,.18,.045), "Metal", .008, parent=door)
        a.box("Mirror_"+side, (x*1.08,-.85,1.12), (.19,.23,.12), color, .025)
        a.beam("MirrorArm_"+side, (x,-.85,1.08),(x*1.13,-.85,1.12),.022,"Metal")
        a.box("WindowPillar_"+side, (x*.84,.13,1.22), (.07,.08,.52), color,.008)
    for side,x in (("L",-width*.49),("R",width*.49)):
        for label,y in (("F",-wheel_y),("R",wheel_y)):
            wheel = a.empty("Wheel_"+label+side, (x,y,.35))
            a.cyl("Tire_"+label+side,(0,0,0),.34,.23,"Rubber",12,(0,math.pi/2,0),parent=wheel)
            outer = -.125 if side=="L" else .125
            a.cyl("Rim_"+label+side,(outer,0,0),.20,.025,"Metal",10,(0,math.pi/2,0),parent=wheel)
            a.cyl("Hub_"+label+side,(outer*1.1,0,0),.075,.028,"Navy",8,(0,math.pi/2,0),parent=wheel)
    a.empty("Seat_Driver",(-.43,-.25,.66))
    a.empty("Seat_Passenger",(.43,-.25,.66))
    a.empty("Seat_RearLeft",(-.43,.80,.66))
    a.empty("Seat_RearRight",(.43,.80,.66))
    a.empty("Trunk_LoadPoint",(0,length*.35,.9))
    for x in (-.42,.42):
        a.box("FrontSeat",(x,-.05,.85),(.51,.62,.17),"Navy",.04)
        a.box("SeatBack",(x,.22,1.12),(.51,.13,.57),"Navy",.04)
    a.box("Dashboard",(0,-.83,1.02),(1.4,.23,.15),"Navy",.025)
    a.torus("SteeringWheel",(-.43,-.65,1.17),.16,.025,"Rubber",rotation=(math.pi/2,0,0))
    if kind == "taxi":
        a.box("TaxiRoofSign",(0,.14,height+.14),(.73,.30,.24),"Mustard",.035)
        a.text("TaxiLabel","TAXI",(0,-.02,height+.14),.16,"Navy")
    if kind == "police":
        a.box("LightBarBase",(0,.12,height+.08),(1.15,.28,.08),"Rubber",.025)
        a.box("LightBarRed",(-.32,.12,height+.18),(.48,.29,.16),"PoliceRed",.025)
        a.box("LightBarBlue",(.32,.12,height+.18),(.48,.29,.16),"PoliceBlue",.025)
        a.text("PoliceHood","POLICE",(0,-1.30,1.005),.21,"Ivory",rotation=(0,0,0))
        a.cyl("Antenna",(.45,.60,height+.34),.012,.5,"Rubber",6)
    names.append(name)
    a.export_asset(name)
a.arrange(names,3,(3.6,6.0))
a.studio_floor((3.5,3),11)
a.camera((3.5,2.4,.6),(10,-16,14),17)
a.save_library()
print("VEHICLES_CREATED",names)
