"""Cámaras de revisión, desde los 4 km completos hasta escala de personaje."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
source=bpy.data.scenes['Map4Km_Overview'];manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
poi={p['id']:p for p in manifest['pois']}
(BASE/'renders').mkdir(exist_ok=True)

def make_view(name,center,offset,scale,size=(1700,1200),perspective=False):
    scene=bpy.data.scenes.get('Map4Km_'+name)
    exists=scene is not None
    if not exists:scene=bpy.data.scenes.new('Map4Km_'+name)
    scene.world=source.world
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine=source.render.engine;scene.view_settings.view_transform=source.view_settings.view_transform
    scene.view_settings.exposure=source.view_settings.exposure
    if not exists:
        for collection in source.collection.children:scene.collection.children.link(collection)
        for obj in source.collection.objects:
            if obj.type!='CAMERA':scene.collection.objects.link(obj)
        camera_data=bpy.data.cameras.new(name+'_Camera');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
    else:camera=scene.camera;camera_data=camera.data
    center=Vector(center);camera.location=center+Vector(offset);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='PERSP' if perspective else 'ORTHO';camera_data.ortho_scale=scale;camera_data.lens=30
    camera_data.clip_start=.10;camera_data.clip_end=30000
    scene.render.resolution_x,scene.render.resolution_y=size;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(BASE/'renders'/(name+'.png'))
    return scene

def cutaway(scene,identifier):
    # Una copia local de la colección del sector permite ocultar su techo sin modificar otras vistas.
    roof_names=[name for name in manifest['roof_objects'] if name.startswith(identifier)]
    roof_names+= {'Minimarket':['MilkRoof'],'Bank':['BankColumnsCoin']}.get(identifier,[])
    for name in roof_names:
        obj=bpy.data.objects[name]
        for collection in list(obj.users_collection):
            if collection.name.startswith('Sector_'):
                roof_collection=bpy.data.collections.get('Roofs_'+collection.name)
                if roof_collection is None:roof_collection=bpy.data.collections.new('Roofs_'+collection.name);collection.children.link(roof_collection)
                roof_collection.objects.link(obj);collection.objects.unlink(obj)
    def exclude(layer):
        if layer.collection.name.startswith('Roofs_'):layer.exclude=True
        for child in layer.children:exclude(child)
    exclude(scene.view_layers[0].layer_collection)

views=[]
views.append(make_view('Aerial',(0,0,0),(3400,-4400,6200),6500,(2000,1800)))
views.append(make_view('Plan',(0,0,0),(0,0,6000),4400,(2200,2200)))
views.append(make_view('Center',(0,0,0),(420,-650,700),740,(1800,1400)))
p=Vector(poi['Minimarket']['position'])
views.append(make_view('Street',p+Vector((0,-5,2.0)),(18,-28,10),52,(1800,1200),True))
views.append(make_view('Minimarket_Inside',p+Vector((0,0,1)),(13,-17,21),27,(1600,1300)));cutaway(views[-1],'Minimarket')
p=Vector(poi['Bank']['position'])
views.append(make_view('Bank_Inside',p+Vector((0,0,1)),(17,-20,24),34,(1600,1300)));cutaway(views[-1],'Bank')
views.append(make_view('ForestRiver',(-1580,-1510,0),(320,-440,510),650,(1700,1300)))
views.append(make_view('Plaza',(0,0,0),(66,-90,65),150,(1700,1200)))
# El archivo conserva cámaras accesibles como escenas en el selector de Blender.
bpy.context.window.scene=source
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
for scene in views:
    bpy.context.window.scene=scene;bpy.ops.render.render(write_still=True)
    print('MAP_VIEW_RENDERED',scene.name,flush=True)
print('MAP_VIEWS_SUCCESS',len(views),flush=True)
