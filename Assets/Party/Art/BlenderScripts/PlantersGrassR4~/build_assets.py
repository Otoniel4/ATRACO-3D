"""Kit de macetas, arbustos y pasto con tres LOD y una escena de revisión animada."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from flora import Flora,materials,C
from wind_nodes import create_group,attach
bpy.ops.wm.read_factory_settings(use_empty=True);materials();wind=create_group()
catalog=[];meshes={}
for variant in range(4):
    for lod in range(3):
        b=Flora(137+variant);b.shrub((0,0,0),.78,.68,.68,lod,variant)
        name=f'PlantR4_Shrub_{variant}_LOD{lod}';meshes[name]=b.data(name)
for lod in range(3):
    b=Flora(244);b.grass(lod=lod);name=f'PlantR4_Grass_LOD{lod}';meshes[name]=b.data(name)
b=Flora(53);b.rectangular_pot();meshes['PlantR4_Pot_Rectangular']=b.data('PlantR4_Pot_Rectangular')
b=Flora(54);b.round_pot();meshes['PlantR4_Pot_Round']=b.data('PlantR4_Pot_Round')
scene=bpy.context.scene;scene.name='PlantersR4_Closeup';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.fps=C['fps'];scene.frame_start=1;scene.frame_end=192
scene.world=bpy.data.worlds.new('Garden_Daylight');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.73,.82,1);bg.inputs['Strength'].default_value=.65
sun=bpy.data.lights.new('Garden_Sun','SUN');sun.energy=3.0;sun.angle=math.radians(12)
obj=bpy.data.objects.new(sun.name,sun);scene.collection.objects.link(obj);obj.rotation_euler=(.45,-.6,-.5)
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.4

def place(name,p=(0,0,0),yaw=0,animated=True):
    obj=bpy.data.objects.new(name,meshes[name]);scene.collection.objects.link(obj);obj.location=p;obj.rotation_euler.z=yaw
    bpy.context.view_layer.update()
    if animated:attach(obj,wind)
    return obj

place('PlantR4_Pot_Rectangular',(-.55,.3,0),animated=False)
for i in range(4):place('PlantR4_Shrub_'+str([1,2,3,1][i])+'_LOD0',(-1.56+i*.68,.3,.53),i*.6)
place('PlantR4_Pot_Round',(1.55,.3,0),animated=False)
plant=place('PlantR4_Shrub_0_LOD0',(1.55,.3,.56));plant.scale=(1.04,1.04,1.15);bpy.context.view_layer.update()
plant.modifiers.clear();attach(plant,wind)
for i in range(5):
    for j in range(3):place('PlantR4_Grass_LOD0',(-2.8+i*1.15,-1.15-j*.75,.005),(i+j)*.67)
floor=Flora();floor.box((0,1,-.07),(30,20,.12),'Stone');floor.box((0,-2.1,-.015),(7,3.5,.04),'GrassShade')
# Bordillo y juntas legibles junto al césped, sin cruzar el follaje de las macetas.
floor.box((0,-.5,.04),(7,.14,.12),'StoneRim')
for x in [-3,-1,1,3]:floor.box((x,1.25,.002),(.012,3.4,.005),'Charcoal')
obj=bpy.data.objects.new('Garden_ReviewGround',floor.data('Garden_ReviewGround'));scene.collection.objects.link(obj)
data=bpy.data.cameras.new('PlanterReviewCamera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
target=Vector((0,-.8,.62));camera.location=target+Vector((4.9,-7.2,4.4));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=6.6;data.clip_end=200
scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=48
(BASE/'renders').mkdir(exist_ok=True);scene.render.filepath=str(BASE/'renders/Macetas_Pasto_R4.png');scene.frame_set(49)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
            area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
for name,data in meshes.items():catalog.append({'mesh':name,'vertices':len(data.vertices),
    'triangles':sum(len(p.vertices)-2 for p in data.polygons),'leaves':data['Leaves'],'grass_blades':data['GrassBlades']})
(BASE/'asset_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Macetas_Pasto_Viento_R4.blend'))
bpy.ops.render.render(write_still=True)
print('PLANT_ASSETS_READY',len(catalog),flush=True)
