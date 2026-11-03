import alarmart as a
import bpy

a.new_scene("ScaleReference")
a.begin("Reference_ScaleBoard","Materials")
a.box("OneMeterCube",(-2.5,0,.5),(1,1,1),"Apricot",.025)
a.clone("BaseMale_TPose","ReferencePerson",(0,0,0))
a.clone("Door_1m","ReferenceDoor",(2.2,0,0))
a.clone("Car_Sedan","ReferenceCar",(5.4,0,0))
for label,x in [("1 M CUBE",-2.5),("1.75 M PERSON",0),("DOOR",2.2),("CAR 4.2 M",5.4)]:
    a.text("ScaleLabel",label,(x,-2.8,.02),.20,"Navy",rotation=(0,0,0))
a.studio_floor((1.7,0),9)
a.camera((1.6,0,.5),(8,-14,11),12)
bpy.data.scenes["Alarma_Interiors"].camera.data.ortho_scale=90
a.save_library()
print("SCALE_REFERENCE_READY cube 1m, person 1.75m, door, car 4.2m")
