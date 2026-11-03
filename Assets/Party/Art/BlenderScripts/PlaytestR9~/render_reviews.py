import bpy,json,math,sys
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;B.joinpath('renders').mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(B/'Villa_Alarma_3000_R9.blend'));scene=bpy.context.scene
outside=[]
for obj in scene.objects:
    if obj.type=='MESH':
        pts=[obj.matrix_world@Vector(p) for p in obj.bound_box];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
        if hi[0]<-270 or lo[0]>-165 or hi[1]<-320 or lo[1]>-222:outside.append(obj)
bpy.data.batch_remove(ids=tuple(outside));print('REVIEW_FOCUSED',len(outside),flush=True)
for p in json.loads((B/'district.json').read_text(encoding='utf-8'))['pois'][:6]:
    light=bpy.data.lights.new('Interior cálido','POINT');light.energy=180;light.color=(1,.89,.76);ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=(p['position'][0],-p['position'][2],3.2)
def render(label,location,target,scale=0):
    scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.type='ORTHO' if scale else 'PERSP';scene.camera.data.ortho_scale=scale or 10;scene.camera.data.lens=24;scene.camera.data.clip_start=.05;scene.camera.data.clip_end=300
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders'/(label+'.png'));bpy.ops.render.render(write_still=True);print('R9_RENDER',label,flush=True)
render('Barrio_y_escondite',(-215,-342,56),(-215,-271,0),128)
render('Mercado_interior',(-215,-295.1,2.1),(-215,-286,1.1))
render('Escondite',(-240,-293,2.1),(-240,-286,1.3))
worldscene=scene;catalog=json.loads((sources9.r6()/'animation_catalog.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_R9.blend'));row=next(r for r in catalog if r['id']=='Player01_Thief');scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
for t in rig.animation_data.nla_tracks:t.mute=True
rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name=='Run');bpy.data.objects[row['bag']].hide_render=True
scene.camera.location=(3,-5,2);scene.camera.rotation_euler=(Vector((0,0,.90))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.15;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.resolution_x=300;scene.render.resolution_y=420;scene.render.resolution_percentage=100
(B/'renders/run_frames').mkdir(exist_ok=True)
for f in range(1,21):scene.frame_set(f);scene.render.filepath=str(B/'renders/run_frames'/str(str(f).zfill(3)+'.png'));bpy.ops.render.render(write_still=True)
print('R9_PREVIEW_READY',flush=True)
