"""Retratos aislados al origen, independientes de la escena de galería."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from wind_nodes import attach
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(BASE/'Arboles_Viento_R3.blend'),link=False) as (src,dst):
    dst.meshes=[n for n in src.meshes if n.startswith('TreeR3_') and n.endswith('LOD0')]
    dst.node_groups=[n for n in src.node_groups if n=='Trees_R3_NaturalWind'];dst.worlds=src.worlds[:1]
scene=bpy.context.scene;scene.world=dst.worlds[0]
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.25
scene.render.fps=24;scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
sun=bpy.data.lights.new('Sun','SUN');sun.energy=3.2;sun.angle=.12;obj=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(obj);obj.rotation_euler=(.5,-.45,-.3)
data=bpy.data.cameras.new('PortraitCamera');camera=bpy.data.objects.new('PortraitCamera',data);scene.collection.objects.link(camera);scene.camera=camera
target=Vector((0,0,4.5));camera.location=target+Vector((5,-20,4));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=12
body=bpy.data.objects.new('PortraitTree',dst.meshes[0]);scene.collection.objects.link(body);bpy.context.view_layer.update();attach(body,dst.node_groups[0])
for item in json.loads((BASE/'catalog.json').read_text(encoding='utf-8')):
    body.data=bpy.data.meshes[item['lods'][0]['mesh']];scene.frame_set(49);bpy.context.view_layer.update()
    scene.render.filepath=str(BASE/'renders'/('Wind_'+item['name']+'.png'));bpy.ops.render.render(write_still=True)
print('TREE_PORTRAITS_READY')
