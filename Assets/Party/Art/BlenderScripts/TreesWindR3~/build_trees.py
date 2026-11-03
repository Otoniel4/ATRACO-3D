"""Genera la biblioteca natural y escenas pequeñas con viento reproducible, sin dependencias externas."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from tree_geometry import C,SPECIES,build_library
from wind_nodes import create_group,attach
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.name='Trees_R3_Gallery';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
LIBRARY=build_library();WIND=create_group()
scene.render.fps=C['fps'];scene.frame_start=1;scene.frame_end=C['fps']*C['loop_seconds']
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.25
scene.world=bpy.data.worlds.new('Trees_SoftDay');scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');background.inputs['Color'].default_value=(.65,.73,.81,1);background.inputs['Strength'].default_value=.55
sun=bpy.data.lights.new('Trees_Sun','SUN');sun.energy=3.2;sun.angle=math.radians(8)
obj=bpy.data.objects.new(sun.name,sun);scene.collection.objects.link(obj);obj.rotation_euler=(.5,-.45,-.3)
# Suelo neutral que permite leer las siluetas y las sombras de hojas reales.
mesh=bpy.data.meshes.new('Ground');mesh.from_pydata([(-100,-100,-.02),(100,-100,-.02),(100,100,-.02),(-100,100,-.02)],[],[(0,1,2,3)])
material=bpy.data.materials.new('Trees_Ground');material.use_nodes=True;shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=(.40,.47,.32,1);shader.inputs['Roughness'].default_value=1;material.diffuse_color=(.40,.47,.32,1)
mesh.materials.append(material);ground=bpy.data.objects.new('Ground',mesh);scene.collection.objects.link(ground)
for species in range(6):
    obj=bpy.data.objects.new('Wind_'+SPECIES[species][0],LIBRARY[species][0]);scene.collection.objects.link(obj);obj.location=((species-2.5)*10,0,0)
    bpy.context.view_layer.update();attach(obj,WIND)
camera_data=bpy.data.cameras.new('GalleryCamera');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
target=Vector((0,0,4));camera.location=target+Vector((17,-68,15));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=69;camera_data.clip_end=2000
scene.render.resolution_x=2000;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';(BASE/'renders').mkdir(exist_ok=True);scene.render.filepath=str(BASE/'renders/Gallery.png')
scene.frame_set(1);bpy.ops.render.render(write_still=True)
hero=bpy.data.scenes.new('Trees_R3_Wind_Closeup');hero.world=scene.world;hero.render.engine=scene.render.engine
hero.view_settings.view_transform=scene.view_settings.view_transform;hero.view_settings.exposure=scene.view_settings.exposure
hero.render.fps=C['fps'];hero.frame_start=1;hero.frame_end=scene.frame_end
for source in [ground,next(o for o in scene.objects if o.type=='LIGHT')]:hero.collection.objects.link(source)
for species,p in [(0,(0,0,0)),(2,(10,5,0)),(5,(-10,6,0))]:
    obj=bpy.data.objects.new('Hero_'+SPECIES[species][0],LIBRARY[species][0]);hero.collection.objects.link(obj);obj.location=p
    bpy.context.window.scene=hero;bpy.context.view_layer.update();attach(obj,WIND)
data=bpy.data.cameras.new('WindCloseCamera');cam=bpy.data.objects.new(data.name,data);hero.collection.objects.link(cam);hero.camera=cam
target=Vector((0,0,4.6));cam.location=target+Vector((6,-17,4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=11.8;data.clip_end=500
hero.render.resolution_x=1080;hero.render.resolution_y=1080;hero.render.resolution_percentage=100;hero.render.image_settings.file_format='PNG'
hero.render.filepath=str(BASE/'renders/Closeup.png');hero.frame_set(1);bpy.ops.render.render(write_still=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_end=2000;space.overlay.show_overlays=False;space.shading.type='MATERIAL'
            space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
catalog=[]
for species,meshes in LIBRARY.items():
    catalog.append({'id':species,'name':SPECIES[species][0],'height_m':SPECIES[species][1],
        'lods':[{'mesh':m.name,'vertices':len(m.vertices),'triangles':sum(len(p.vertices)-2 for p in m.polygons),'leaves':m['LeafCount']} for m in meshes]})
(BASE/'catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Arboles_Viento_R3.blend'))
print('NATURAL_TREES_READY',json.dumps(catalog),flush=True)
