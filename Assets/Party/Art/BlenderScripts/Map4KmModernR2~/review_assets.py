"""Revisión de las piezas maestras antes de multiplicarlas por la ciudad."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
import modern_assets as A
bpy.ops.wm.read_factory_settings(use_empty=True)
C=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'));M.palette(C['palette'])
A.setup_palette({'palette':{}});A.create_library()
scene=bpy.context.scene;scene.name='CityR2_AssetReview'
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.25
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs['Color'].default_value=(.6,.7,.8,1);background.inputs['Strength'].default_value=.5
data=bpy.data.lights.new('Sun','SUN');data.energy=3;obj=bpy.data.objects.new('Sun',data);scene.collection.objects.link(obj);obj.rotation_euler=(.45,-.35,-.4)
ground=M.Batch();ground.box((0,0,-.12),(180,150,.20),'grass');obj=bpy.data.objects.new('Ground',ground.data('Ground'));scene.collection.objects.link(obj)
for name,p in [('House_0',(-15,-13,0)),('House_7',(1,-13,0)),('Shop_1',(-15,14,0)),('Tower_0',(24,24,0))]:
    obj=bpy.data.objects.new(name,A.PROTOTYPES[name]);scene.collection.objects.link(obj);obj.location=p
    roof=bpy.data.objects.new(name+'_Roof',A.ROOFS[name]);scene.collection.objects.link(roof);roof.location=p
for i in range(6):
    obj=bpy.data.objects.new('Tree_'+str(i),A.PROTOTYPES['Tree_'+str(i)]);scene.collection.objects.link(obj);obj.location=(-28+i*10,-33,0)
data=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',data);scene.collection.objects.link(cam);scene.camera=cam
data.clip_end=1000;data.lens=43
(BASE/'renders').mkdir(exist_ok=True)
for name,center,offset in [('House_Master',(-15,-13,2),(18,-24,12)),('Shop_Master',(-15,14,2),(19,-26,12)),('Trees_Master',(-3,-33,4),(29,-44,17))]:
    data.type='ORTHO' if name=='Trees_Master' else 'PERSP';data.ortho_scale=70
    cam.location=Vector(center)+Vector(offset);cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
    scene.render.filepath=str(BASE/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
(BASE/'asset_catalog_review.json').write_text(json.dumps(A.CATALOG,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Assets_Modern_R2.blend'))
print('MODERN_ASSETS_REVIEW_READY',len(A.CATALOG))
