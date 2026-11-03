"""Vista pequeña para revisar el arte sin cargar los 4 km: usa las mismas mallas de la ciudad."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
from mesh_tools import Batch
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.name='CityR2_Showcase'
names=['CityR2_'+key for key in ['House_6','House_7','House_0','Shop_1','Tower_0','Hero_Minimarket',
       'Hero_Minimarket_Furniture','Hero_Minimarket_Door','Hero_Restaurant','Hero_Restaurant_Furniture','Hero_Restaurant_Door',
       'Garden_0','Garden_1','CafeSet','Bench','Lamp']]
names += ['CityR2_'+key+'_Roof' for key in ['House_6','House_7','House_0','Shop_1','Tower_0','Hero_Minimarket','Hero_Restaurant']]
names += ['CityR2_Tree_'+str(i) for i in range(6)]
with bpy.data.libraries.load(str(BASE/'Villa_Alarma_Modern_R2.blend'),link=False) as (src,dst):
    dst.meshes=[name for name in src.meshes if name in names or name.startswith('Scale_')]
    dst.worlds=src.worlds[:1]
    dst.materials=[name for name in src.materials if name.startswith('City4_')]
scene.world=dst.worlds[0]
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
for link in list(background.inputs['Color'].links):scene.world.node_tree.links.remove(link)
background.inputs['Color'].default_value=(.70,.76,.82,1);background.inputs['Strength'].default_value=.5
for material in bpy.data.materials:
    if material.name.startswith('City4_'):
        M.INDEX[material.name[6:]]=len(M.MATERIALS);M.MATERIALS.append(material)
def place(key,p,roof=False):
    mesh=bpy.data.meshes['CityR2_'+key];obj=bpy.data.objects.new(key,mesh);scene.collection.objects.link(obj);obj.location=p
    if roof:place(key+'_Roof',p)
    return obj
for key,p in [('House_6',(-22,26,.18)),('House_7',(-6,26,.18)),('House_0',(10,26,.18)),
              ('Hero_Minimarket',(-24,-16,.18)),('Hero_Restaurant',(-8,-16,.18)),('Shop_1',(17,-16,.18)),('Tower_0',(33,31,.18))]:
    place(key,p,True)
    if key.startswith('Hero_'):
        place(key+'_Furniture',p);place(key+'_Door',(p[0]-1.1,p[1]-5.12,p[2]));place(key+'_Door',(p[0]+1.1,p[1]-5.12,p[2])).rotation_euler.z=math.pi
for x,name in [(-22,'Garden_0'),(-6,'Garden_1'),(10,'Garden_0')]:place(name,(x,26,0))
for i,p in enumerate([(-39,-8,0),(-39,17,0),(-36,42,0),(-15,43,0),(8,-36,0),(44,-4,0)]):place('Tree_'+str(i),p)
for x in [-11,-5]:place('CafeSet',(x,-26,.18))
for x in [-30,-10,10,30]:place('Lamp',(x,6.3,.18))
figures=[m for m in dst.meshes if m.name.startswith('Scale_')]
for i,mesh in enumerate(figures[:3]):
    obj=bpy.data.objects.new('ScalePerson_'+str(i),mesh);scene.collection.objects.link(obj);obj.location=(-26+i*2,-23,0)
b=Batch();b.box((0,8,-.12),(110,100,.24),'grass');b.box((0,0,.02),(110,8,.04),'asphalt')
for y in [-6,6]:b.box((0,y,.09),(110,4,.18),'ivory')
for x in range(-50,51,8):b.box((x,0,.052),(3,.12,.025),'mustard')
obj=bpy.data.objects.new('Showcase_Ground',b.data('Showcase_Ground'));scene.collection.objects.link(obj)
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.3
light=bpy.data.lights.new('ShowcaseSun','SUN');light.energy=3;light.angle=.07
obj=bpy.data.objects.new('ShowcaseSun',light);scene.collection.objects.link(obj);obj.rotation_euler=(.45,-.35,-.4)
data=bpy.data.cameras.new('ShowcaseCamera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
target=Vector((0,9,2));cam.location=target+Vector((72,-105,73));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=125;data.clip_end=1500
scene.render.resolution_x=1800;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.filepath=str(BASE/'renders/Showcase.png');bpy.ops.render.render(write_still=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_end=2000;space.overlay.show_overlays=False
            space.shading.type='MATERIAL';space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'CityR2_Showcase.blend'))
print('SMALL_SHOWCASE_READY',len(scene.objects))
