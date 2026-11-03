import alarmart as a
import math

a.new_scene("Interiors")
names=[]
def room(name,width,depth,color):
    a.begin(name,"City");names.append(name)
    a.box("Floor",(0,0,.04),(width,depth,.08),"Cream",.01)
    a.box("WallLeft",(-width/2,0,1.65),(.20,depth,3.3),color,.015)
    a.box("WallRight",(width/2,0,1.65),(.20,depth,3.3),color,.015)
    segment=(width-1.3)/2
    for y in [-depth/2,depth/2]:
        for side in [-1,1]:a.box("WallSegment",(side*(.65+segment/2),y,1.65),(segment,.2,3.3),color,.015)
        a.box("DoorHeader",(0,y,2.82),(1.3,.2,.96),color,.015)
        a.clone("Door_1m","Entrance" if y<0 else "RearExit",(0,y,0),0 if y<0 else math.pi)
    roof=a.box("Roof_Removable",(0,0,3.4),(width+.35,depth+.35,.20),color,.025)
    a.empty("EntrancePoint",(0,-depth/2-.5,0))
    a.empty("RearExitPoint",(0,depth/2+.5,0))
    a.empty("GuardPatrol_01",(-width*.3,depth*.25,0))
    a.clone("Prop_SecurityCamera","EntranceCamera",(-width*.4,depth*.45,2.8),math.pi)
    a.clone("Prop_AlarmBeacon","Alarm",(width*.4,-depth/2-.12,2.7))
    return roof
def end(roof):
    a.export_asset(names[-1]);roof.hide_set(True)

r=room("Interior_Minimarket",12,10,"Terracotta")
for x in [-3.8,0,3.8]:
    for y in [-1.8,1.2]:a.clone("Prop_RetailShelf","StockedAisle",(x,y,0))
for x in [-4.3,-2.8]:a.clone("Prop_Refrigerator","ColdDrinks",(x,3.8,0))
a.clone("Prop_Checkout","Checkout",(3.7,-3.7,0))
a.clone("Prop_Telephone","CashierPhone",(4,-3.7,1.04))
a.clone("Prop_Safe","BackOfficeSafe",(4,3.7,0))
for x in [1,2.1]:a.clone("Prop_StorageCrate","BackroomStock",(x,4,0))
a.box("BackroomPartition",(2.8,2.6,1.4),(5,.18,2.8),"Cream",.01)
end(r)
r=room("Interior_Jewelry",12,10,"Cream")
for x in [-3.5,0,3.5]:
    for y in [-1.8,1.8]:a.clone("Prop_JewelryDisplay","Display",(x,y,0))
a.clone("Prop_Checkout","JewelerDesk",(3.5,3.7,0))
a.clone("Prop_Safe","JewelrySafe",(-4,3.7,0))
for x in [-3,3]:a.clone("Prop_LaserEmitter","SecurityEmitter",(x,3,1.2))
end(r)
r=room("Interior_Bank",16,14,"Cream")
for x in [-4,-1.5,1,3.5]:
    a.clone("Prop_BankCounter","TellerCounter",(x,1.8,0))
    a.clone("Prop_OfficeMonitor","Terminal",(x,1.8,1.17))
    a.clone("Prop_Chair","TellerChair",(x,3.0,0))
for x in [-6,6]:a.clone("Prop_ATM","ATM",(x,-4.5,0))
for x in [-4,-2,0,2,4]:a.clone("Prop_Chair","WaitingChair",(x,-2.5,0))
a.box("VaultWallLeft",(-5,4.3,1.5),(5,.25,3),"Metal",.02)
a.box("VaultWallRight",(5,4.3,1.5),(5,.25,3),"Metal",.02)
a.clone("Prop_VaultDoor","VaultEntrance",(0,4.3,0))
for x in [-4,-2,2,4]:
    a.clone("Prop_Safe","DepositSafe",(x,6.1,0))
    a.clone("Prop_CashStack","CashBundle",(x,5.7,1.13))
end(r)
r=room("Interior_Hideout",12,10,"Teal")
a.clone("Prop_HideoutSofa","Sofa",(-3.5,2.8,0))
a.clone("Prop_RestaurantTable","PlanningTable",(-3,0,0))
a.clone("Prop_PlanningBoard","PlanningBoard",(2.8,3.5,0))
a.clone("Prop_ClothingRack","DisguiseWardrobe",(-4,4.2,0))
a.clone("Prop_OfficeDesk","EquipmentDesk",(3.8,-1.8,0))
a.clone("Prop_Toolbox","Tools",(3.6,-1.8,.79))
a.clone("Prop_VendingMachine","SecretEntranceDisguise",(4,-4,0))
for x in [1.5,3,4.5]:a.clone("Prop_LootBag","LootStorage",(x,3.8,0))
end(r)
r=room("Interior_Restaurant",12,10,"Coral")
for x in [-3,0,3]:
    for y in [-2,1]:
        a.clone("Prop_RestaurantTable","DiningTable",(x,y,0))
        for side in [-1,1]:a.clone("Prop_Chair","DiningChair",(x+side*.8,y,0),side*math.pi/2)
a.clone("Prop_FoodCounter","KitchenCounter",(-3.3,3.7,0))
a.clone("Prop_Refrigerator","KitchenFridge",(3.7,3.8,0))
end(r)
r=room("Interior_ClothingStore",12,10,"Berry")
for x in [-3.4,0,3.4]:
    for y in [0,2.5]:a.clone("Prop_ClothingRack","Clothes",(x,y,0))
for x in [-3.4,3.4]:a.clone("Prop_Mannequin","DisplayMannequin",(x,-3.7,0))
a.clone("Prop_Checkout","ClothesCheckout",(3.3,3.8,0))
end(r)
r=room("Interior_PoliceStation",14,12,"Navy")
for x in [-4,0,4]:
    a.clone("Prop_OfficeDesk","Desk",(x,-1.8,0))
    a.clone("Prop_OfficeMonitor","Monitor",(x,-1.8,.79))
    a.clone("Prop_Chair","OfficerChair",(x,-.9,0))
for x in [-4,0,4]:
    for bx in [-.9,-.6,-.3,0,.3,.6,.9]:a.beam("CellBar",(x+bx,3.5,0),(x+bx,3.5,2.6),.025,"Metal")
    a.box("CellBench",(x,5,.45),(1.8,.65,.15),"Metal",.02)
end(r)
r=room("Interior_UndergroundParking",18,16,"Metal")
for x in [-5,5]:
    for y in [-4,0,4]:a.box("SupportPillar",(x,y,1.65),(.55,.55,3.3),"Cream",.025)
for x in [-6,0,6]:
    a.clone("Car_Hatchback" if x==0 else "Car_Sedan","ParkedCar",(x,1.7,0))
    for side in [-1,1]:a.box("ParkingLine",(x+side*1.2,1.7,.095),(.08,5,.018),"Mustard",0)
a.clone("ParkingBarrier","Barrier",(2,-5,0))
end(r)
a.begin("Interior_SewerPassage","City");names.append("Interior_SewerPassage")
a.box("Walkway",(0,0,-.08),(3.8,12,.16),"Metal",.01)
for i in range(12):
    angle1=math.pi*i/12;angle2=math.pi*(i+1)/12
    x1,z1=1.9*math.cos(angle1),1.9*math.sin(angle1)
    x2,z2=1.9*math.cos(angle2),1.9*math.sin(angle2)
    a.mesh("TunnelSegment",[(x1,-6,z1),(x2,-6,z2),(x2,6,z2),(x1,6,z1)],[(0,1,2,3)],"Terracotta")
a.box("DrainChannel",(0,0,.015),(.5,12,.03),"Teal",0)
a.empty("PassageEntry",(0,-6,0));a.empty("PassageExit",(0,6,0))
a.export_asset(names[-1])
a.arrange(names,3,(21,21))
a.studio_floor((21,21),52)
a.camera((21,20,0),(40,-55,70),78)
a.save_library()
print("INTERIORS_CREATED",len(names),"decorated static interiors; no NPC or gameplay")
