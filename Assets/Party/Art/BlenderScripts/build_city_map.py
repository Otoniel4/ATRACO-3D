import alarmart as a
import math

a.box=a.fast_box
a.new_scene("CityMap_6x6")
a.begin("CityMap_6x6_StaticDesign","City")
a.ROOT["MapStatus"]="Static art layout, not a playable or networked city"
a.ROOT["BlockCountX"]=6;a.ROOT["BlockCountY"]=6
widths=[8 if i%2==0 else 20 for i in range(13)]
centers=[];cursor=-88
for size in widths:
    centers.append(cursor+size/2);cursor+=size
for ix in range(13):
    for iy in range(13):
        if ix%2 and iy%2:continue
        x,y=centers[ix],centers[iy]
        if ix%4==0 and iy%4==0:
            a.clone("Road_Intersection_8m","MainIntersection",(x,y,0))
            for dx,dy,rotation in [(4.5,4.5,math.pi),(-4.5,-4.5,0)]:a.clone("TrafficLight_Vehicle","TrafficSignal",(x+dx,y+dy,0),rotation)
        else:
            a.box("RoadPatch",(x,y,-.1),(widths[ix],widths[iy],.2),"Asphalt",0)
            if ix%2==0 and iy%2:
                for dy in [-7,-3,1,5,9]:a.box("LaneMark",(x,y+dy,.01),(.13,2,.02),"Mustard",0)
            if iy%2==0 and ix%2:
                for dx in [-7,-3,1,5,9]:a.box("LaneMark",(x+dx,y,.01),(2,.13,.02),"Mustard",0)

key={(0,0):("Interior_Minimarket","MINIMARKET"),(1,0):("Interior_Jewelry","JEWELRY"),(2,0):("Interior_Bank","BANK"),(0,1):("Interior_ClothingStore","CLOTHING"),(1,1):("Interior_Restaurant","RESTAURANT"),(2,1):("Interior_PoliceStation","POLICE"),(0,2):("Interior_Hideout","HIDEOUT"),(1,2):("Interior_UndergroundParking","PARKING")}
for bx in range(6):
    for by in range(6):
        x,y=centers[bx*2+1],centers[by*2+1]
        a.box("BlockSidewalk",(x,y,.08),(20,20,.16),"Cream",.02)
        if (bx,by) in key:
            asset,label=key[bx,by]
            a.clone(asset,"Local_"+label,(x,y,.17))
            depth={"Interior_Bank":14,"Interior_PoliceStation":12,"Interior_UndergroundParking":16}.get(asset,10)
            a.box("BusinessSign",(x,y-depth/2-.15,2.9),(7,.12,.65),"Teal" if by==0 else "Terracotta",.04)
            a.text("BusinessName",label,(x,y-depth/2-.225,2.9),.43,"Cream")
            a.text("RoofBusinessName",label,(x,y,3.72),.80,"Ivory",rotation=(0,0,0))
        else:
            floors=1+(bx*3+by)%3;color=["Apricot","Cream","Coral","Mustard","Sage","Terracotta"][(bx+by)%6]
            height=floors*3.1
            a.box("BuildingBody",(x,y,height/2+.17),(13.5,13.5,height),color,.06)
            a.box("Roof",(x,y,height+.26),(14,14,.20),"Terracotta" if color!="Terracotta" else "Teal",.04)
            a.box("RoofParapet",(x,y+6.6,height+.53),(14,.24,.65),"Cream",.02)
            a.clone("Door_1m","BuildingEntrance",(x,y-6.84,.17))
            for floor in range(floors):
                z=1.7+floor*3.1
                for dx in [-4.8,-1.6,1.6,4.8]:
                    if floor==0 and abs(dx)<2:continue
                    a.box("WindowTrim",(x+dx,y-6.79,z),(1.65,.13,1.65),"Ivory",.015)
                    a.box("WindowGlass",(x+dx,y-6.87,z),(1.43,.03,1.43),"Glass",.008)
                for dy in [-3.2,1.5,4.5]:
                    a.box("SideWindow",(x+6.79,y+dy,z),(.04,1.5,1.6),"Glass",.01)
            a.box("ACUnit",(x+3,y+2,height+.65),(1.5,1,.6),"Metal",.03)
        for dx,dy in [(-8,-7),(8,7)]:a.clone("Tree_Round" if (bx+by)%2 else "Tree_Palm","StreetTree",(x+dx,y+dy,.17))
        a.clone("StreetLight","StreetLight",(x-8.7,y-8.7,.17))
        a.clone("Bench_City","StreetBench",(x+5,y-8.7,.17))
        a.clone("TrashBin_City","StreetBin",(x+7,y-8.7,.17))
        if (bx+by)%5==0:a.clone("Car_Taxi" if bx%2 else "Car_Sedan","ParkedVehicle",(x-11.5,y-3,0))

a.box("CityTerrain",(0,0,-.30),(193,193,.40),"Sage",.04)
a.box("River",(101,0,-.18),(16,210,.20),"Glass",0)
a.box("RiverRightBank",(122,0,-.30),(26,193,.40),"Sage",0)
for y in [-56,28]:
    bridge=a.clone("Bridge_8m","RiverBridge",(101,y,.1),math.pi/2)
    bridge.scale=(1,3.25,1)
a.box("Highway",(0,104,-.08),(210,14,.2),"Asphalt",0)
for x in range(-98,100,8):a.box("HighwayMark",(x,104,.03),(4,.16,.02),"Ivory",0)
for x in [-85,-57,-29,-1,27,55,83]:a.box("BoundaryBollard",(x,-91,.45),(.3,.3,.9),"Terracotta",.025)
a.clone("Interior_SewerPassage","SewerExit",(93,65,-1.3),math.pi/2)
a.empty("CityOrigin",(0,0,0))
a.empty("PlayerSpawn_DesignOnly",(-70,-77,.2))
a.export_asset("CityMap_6x6_StaticDesign")
a.camera((9,9,1),(165,-225,245),294)
a.save_library()
print("CITY_MAP_CREATED 36 blocks, continuous streets, decorated key buildings, static signals, river and highway")
