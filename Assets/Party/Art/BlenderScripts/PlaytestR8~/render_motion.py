import bpy,json
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_Corregido_R8.blend'));catalog=json.loads((r6()/'animation_catalog.json').read_text());row=next(r for r in catalog if r['id']=='Player01_Thief');scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
for t in rig.animation_data.nla_tracks:t.mute=True
rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name=='Run');bpy.data.objects[row['bag']].hide_render=True
scene.camera.location=(3,-5,2);scene.camera.rotation_euler=(Vector((0,0,.9))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.1
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.resolution_x=300;scene.render.resolution_y=400;scene.render.resolution_percentage=100
(B/'renders/run_frames').mkdir(parents=True,exist_ok=True)
for f in range(1,17):scene.frame_set(f);scene.render.filepath=str(B/'renders/run_frames'/str(str(f).zfill(3)+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export/Doors/Minimarket.fbx'));scene=bpy.context.scene
camera_data=bpy.data.cameras.new('DoorReview');camera=bpy.data.objects.new('DoorReview',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera.location=(3,-5,2.8);camera.rotation_euler=(Vector((.55,0,1.32))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=3.3
light_data=bpy.data.lights.new('Softbox','AREA');light_data.energy=450;light_data.shape='DISK';light_data.size=5;light=bpy.data.objects.new('Softbox',light_data);scene.collection.objects.link(light);light.location=(0,-3,5);light.rotation_euler=(Vector((.55,0,1.3))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.3,.3,.3);scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=450;scene.render.resolution_y=500;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders/Puerta_R8.png');bpy.ops.render.render(write_still=True)
print('MOTION_AND_DOOR_REVIEW_READY',flush=True)
