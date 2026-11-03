import bpy,json,sys
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
B=Path(__file__).resolve().parent;sys.path.insert(0,str(r6()));from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_Corregido_R8.blend'))
catalog=json.loads((r6()/'animation_catalog.json').read_text())
views=[('Player01_Thief','Idle',1,'Espalda',(2.7,4.5,2.1)),('Player01_Thief','Walk',7,'Caminar',(3,-5,2)),('Player01_Thief','Run',5,'Correr',(3,-5,2)),('Player01_Thief','Run',13,'Carrera_espalda',(3,5,2)),('NPC02_Denim','Walk',7,'Civil_caminando',(3,-5,2)),('Player04_Muscle','Run',5,'Musculo_corriendo',(3,-5,2))]
(B/'renders').mkdir(exist_ok=True)
for identifier,mode,frame,label,location in views:
    row=next(r for r in catalog if r['id']==identifier);scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name==mode);scene.frame_set(frame)
    bpy.data.objects[row['bag']].hide_render=True
    scene.camera.location=location;scene.camera.rotation_euler=(Vector((0,0,.93))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=2.1
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=420;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders'/(label+'.png'));bpy.ops.render.render(write_still=True)
    print('R8_RENDER',label,flush=True)
