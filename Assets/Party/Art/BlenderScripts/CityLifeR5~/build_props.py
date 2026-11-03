"""Construye el kit detallado y los nueve interiores, sin descargar recursos."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import props as P
bpy.ops.wm.read_factory_settings(use_empty=True);P.make_library()
scene=bpy.context.scene;scene.name='LifeR5_PropKit';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='BLENDER_EEVEE_NEXT';scene.world=bpy.data.worlds.new('LifeR5_Daylight');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.74,.82,1);bg.inputs['Strength'].default_value=.7
light=bpy.data.lights.new('LifeR5_Sun','SUN');light.energy=3;light.angle=.13
obj=bpy.data.objects.new(light.name,light);scene.collection.objects.link(obj);obj.rotation_euler=(.4,-.5,-.4)
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.4
for i,(name,data) in enumerate(P.LIB.items()):
    obj=bpy.data.objects.new('Kit_'+name,data);scene.collection.objects.link(obj);obj.location=((i%7)*3.5,(i//7)*3.4,0)
camera_data=bpy.data.cameras.new('LifeR5_KitCamera');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
target=Vector((10,4.7,.5));camera.location=target+Vector((15,-23,20));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=29
scene.render.resolution_x=1800;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
(BASE/'renders').mkdir(exist_ok=True);scene.render.filepath=str(BASE/'renders/Objetos_Locales_R5.png')
placements={key:[] for key in ['Minimarket','MallJewelry','Bank','Police','Hideout','Restaurant','Clothing','PaintGarage','FenceGear']}
def put(shop,asset,x,y,z=.16,yaw=0,collision=True):
    placements[shop].append({'asset':asset,'position_blender':[x,y,z],'yaw':yaw,'collision':collision})
for x in [-3.4,0,3.4]:put('Minimarket','Gondola',x,.7)
for x in [-4,-2,2,4]:put('Minimarket','DisplayFridge',x,4.5)
put('Minimarket','Checkout',3,-3.1);put('Minimarket','ProduceBins',-3.8,-2.9)
for j in range(4):put('Minimarket','ShoppingBasket',-5,-3.6,.16+j*.045,collision=False)
for x in [-3.5,0,3.5]:
    for y in [.3,2.5]:put('MallJewelry','JewelryCase',x,y)
put('MallJewelry','Checkout',0,3.8)
for x in [-3.5,3.5]:put('MallJewelry','NecklaceBust',x,2.5,1.57,collision=False)
for x in [-5,-1.6,1.8,5.2]:put('Bank','OfficeDesk',x,.8);put('Bank','OfficeChair',x,2.0,yaw=math.pi)
for x in [-6.4,6.4]:put('Bank','ATM',x,-4.6)
for x in [-4,-1.8,.4,2.6]:put('Bank','OfficeChair',x,-4.2)
for x,y in [(-5,-2.4),(-2,-2.4),(1,-2.4),(4,-2.4)]:put('Bank','QueuePost',x,y)
put('Bank','VaultDoor',0,2.5)
put('Police','Checkout',-3,-2);put('Police','OfficeDesk',3,-2);put('Police','OfficeChair',3,-.8,yaw=math.pi)
put('Police','Locker',-6.3,-3,yaw=math.pi/2)
put('Police','PlanningBoard',-6.7,-.2,yaw=math.pi/2);put('Police','Sofa',3,-4)
put('Hideout','Sofa',-3,0);put('Hideout','OfficeDesk',2,2.7);put('Hideout','OfficeChair',2,3.9,yaw=math.pi)
put('Hideout','PlanningBoard',0,4.5);put('Hideout','EquipmentShelf',-4,3.7);put('Hideout','ToolCabinet',4,0)
put('Restaurant','Checkout',3,1.8);put('Restaurant','CoffeeMachine',3.6,1.8,1.22,collision=False)
put('Restaurant','PizzaOven',4.3,3.8)
for x,y in [(-3,-2.2),(-.3,-2.2),(-3,.6)]:
    put('Restaurant','DiningTable',x,y)
    for dy,yaw in [(-.95,math.pi),(.95,0)]:put('Restaurant','DiningChair',x,y+dy,yaw=yaw)
    put('Restaurant','PizzaPlate',x,y,.99,collision=False)
for x in [-3.4,3.4]:
    put('Clothing','ClothingRack',x,1.5);put('Clothing','Mannequin',x,-3.5)
put('Clothing','FoldedClothesTable',0,1.1);put('Clothing','Checkout',0,3.8,yaw=math.pi)
for x in [-4,4]:put('PaintGarage','ToolCabinet',x,3.5)
put('PaintGarage','Compressor',-4.5,-1.5);put('PaintGarage','OfficeDesk',3.8,-2.9)
put('PaintGarage','VehicleLift',0,0)
for x in [-3.7,0,3.7]:put('FenceGear','EquipmentShelf',x,3.8)
put('FenceGear','Checkout',3,-1.9);put('FenceGear','ToolCabinet',-3,0);put('FenceGear','Compressor',-3,-2.5)
for shop in placements:
    back=5.8 if shop in ['Bank','Police'] else 4.7
    put(shop,'SecurityCamera',-5.3,back,3.3,collision=False)
    put(shop,'WallClock',0,back,3.15,collision=False)
(BASE/'prop_catalog.json').write_text(json.dumps(P.CATALOG,indent=2),encoding='utf-8')
(BASE/'interior_placements.json').write_text(json.dumps(placements,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Objetos_Locales_R5.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('DETAILED_INTERIORS_READY',len(P.CATALOG),'prototypes',sum(map(len,placements.values())),'placements',flush=True)
