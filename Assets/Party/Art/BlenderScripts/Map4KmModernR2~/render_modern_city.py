"""Cámaras a escala humana, barrios y vistas completas. Las vistas de interiores excluyen techos."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
source=bpy.data.scenes['CityR2_Overview'];manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
sky=next((n for n in source.world.node_tree.nodes if n.type=='TEX_SKY'),None)
if sky is None:sky=source.world.node_tree.nodes.new('ShaderNodeTexSky')
sky_types={i.identifier for i in sky.bl_rna.properties['sky_type'].enum_items}
if 'NISHITA' in sky_types:
    sky.sky_type='NISHITA';sky.sun_elevation=math.radians(38);sky.sun_rotation=math.radians(130)
    sky.sun_intensity=.35;sky.air_density=1;sky.dust_density=.7;sky.ozone_density=1
background=next(n for n in source.world.node_tree.nodes if n.type=='BACKGROUND')
source.world.node_tree.links.new(sky.outputs['Color'],background.inputs['Color']);background.inputs['Strength'].default_value=.20
poi={p['id']:p for p in manifest['pois']};views=[]
(BASE/'renders').mkdir(exist_ok=True)

def view(name,center,offset,scale=None,size=(1800,1200),cutaway=False):
    key='CityR2_'+name;scene=bpy.data.scenes.get(key);exists=scene is not None
    if scene is None:scene=bpy.data.scenes.new(key)
    scene.world=source.world;scene.render.engine=source.render.engine
    scene.view_settings.view_transform=source.view_settings.view_transform
    scene.view_settings.look=source.view_settings.look;scene.view_settings.exposure=source.view_settings.exposure
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=192
    if not exists:
        for c in source.collection.children:scene.collection.children.link(c)
        for o in source.collection.objects:
            if o.type!='CAMERA':scene.collection.objects.link(o)
        data=bpy.data.cameras.new(key+'_Camera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
    else:cam=scene.camera;data=cam.data
    center=Vector(center);cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO' if scale else 'PERSP';data.ortho_scale=scale or 40;data.lens=44
    data.clip_start=.1;data.clip_end=30000
    if cutaway:
        def exclude(layer):
            if layer.collection.name.startswith(('R2_Roofs_','Roofs_')):layer.exclude=True
            for c in layer.children:exclude(c)
        exclude(scene.view_layers[0].layer_collection)
    scene.render.resolution_x,scene.render.resolution_y=size;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(BASE/'renders'/(name+'.png'))
    views.append(scene);return scene

view('Aerial',(0,0,0),(3400,-4400,6200),6500,(2000,1800))
view('Plan',(0,0,0),(0,0,6000),4400,(2200,2200))
view('Center',(0,0,0),(300,-440,410),520,(1800,1400))
p=Vector(poi['Minimarket']['position'])
view('ModernStreet',p+Vector((0,-2,2)),(18,-25,9),None,(1800,1200))
view('StreetLevel',p+Vector((0,-3,2)),(17,-24,2.2),None,(1800,1100))
view('Minimarket_Inside',p+Vector((0,0,1)),(14,-18,20),25,(1700,1300),True)
p=Vector(poi['Bank']['position'])
view('Bank_Inside',p+Vector((0,0,1)),(17,-21,22),31,(1700,1300),True)
view('BusinessDistrict',p+Vector((0,50,0)),(180,-240,140),330,(1800,1300))
p=Vector(poi['Restaurant']['position'])
view('Restaurant',p+Vector((0,0,2)),(20,-27,12),None,(1700,1150))
p=Vector(poi['Police']['position'])
view('Police_Inside',p+Vector((0,0,1)),(17,-20,22),30,(1700,1300),True)
view('Plaza',(0,0,1),(73,-98,62),151,(1800,1250))
view('ForestRiver',(-1580,-1510,0),(320,-440,510),650,(1800,1350))
# Se elige una casa moderna real de la ciudad, con el encuadre por su orientación de fachada.
houses=[o for o in source.objects if o.get('R2Asset')=='House_6']
house=min(houses,key=lambda o:(o.matrix_world.translation-Vector((-1050,-700,0))).length)
p=house.matrix_world.translation.copy();rotation=house.rotation_euler.z
offset=Vector((19,-29,13));offset.rotate(house.rotation_euler)
view('Residential',p+Vector((0,0,2)),offset,None,(1800,1200))
view('Neighborhood',p,(140,-180,170),235,(1800,1350))
bpy.context.window.scene=bpy.data.scenes['CityR2_ModernStreet']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_end=30000;space.overlay.show_overlays=False
            space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.region_3d.view_perspective='CAMERA'
            space.region_3d.view_camera_zoom=0;space.region_3d.view_camera_offset=(0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
for scene in views:
    bpy.context.window.scene=scene;bpy.ops.render.render(write_still=True)
    print('MODERN_CITY_RENDERED',scene.name,flush=True)
print('MODERN_CITY_RENDERS_READY',len(views),flush=True)
