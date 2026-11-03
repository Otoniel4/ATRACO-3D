import bpy,json,sys
from pathlib import Path
from review_sources import r6,r7,map1,map2
from mathutils import Vector
B=Path(__file__).resolve().parent;sys.path.insert(0,str(r6()));from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_Corregido_R8.blend'));catalog=json.loads((r6()/'animation_catalog.json').read_text());row=next(r for r in catalog if r['id']=='Player01_Thief');scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
for obj in list(scene.objects):
    if obj.name.startswith('Player01_Thief_BackStrap'):bpy.data.objects.remove(obj,do_unlink=True)
shoulder=rig.data.bones['LeftUpperArm'].head_local.z;bag=bpy.data.objects['Player01_Thief_Accessories'];lo=min(v.co.z for v in bag.data.vertices);hi=max(v.co.z for v in bag.data.vertices);delta=shoulder-.27-(lo+hi)/2
for v in bag.data.vertices:v.co.z+=delta
material=min([m for m in bpy.data.materials if m.name.startswith(('LP','Cast','Alarma','Skin','cloth'))] or list(bpy.data.materials),key=lambda m:sum(m.diffuse_color[:3]))
for sign in [-1,1]:
    points=[Vector((sign*.13,-.145,shoulder-.25)),Vector((sign*.13,-.13,shoulder-.035)),Vector((sign*.13,0,shoulder+.012)),Vector((sign*.13,.13,shoulder-.035)),Vector((sign*.13,.20,shoulder-.18))]
    vertices=[];faces=[]
    for p in points:vertices.extend([p+Vector((-.018,-.006,0)),p+Vector((.018,-.006,0)),p+Vector((.018,.006,0)),p+Vector((-.018,.006,0))])
    for i in range(len(points)-1):
        for k in range(4):faces.append((i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k))
    faces.extend([(0,3,2,1),tuple(range(len(vertices)-4,len(vertices)))])
    mesh=bpy.data.meshes.new('BackStrapFit');mesh.from_pydata(vertices,[],faces);mesh.materials.append(material);obj=bpy.data.objects.new('Player01_Thief_BackStrapFit',mesh);scene.collection.objects.link(obj);obj.parent=rig;obj.vertex_groups.new(name='Chest').add(list(range(len(vertices))),1,'REPLACE');obj.modifiers.new('Rig','ARMATURE').object=rig
rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=False
bpy.data.objects[row['bag']].hide_render=False;bpy.data.objects[row['bag']].hide_viewport=False
export(B/'export/Characters/Player01_Thief.fbx',[o for o in scene.objects if o.type in ['MESH','ARMATURE','EMPTY']],True)
for t in rig.animation_data.nla_tracks:t.mute=True
rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name=='Idle');scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(B/'Elenco_Corregido_R8.blend'),compress=True)
bpy.data.objects[row['bag']].hide_render=True
for mode,frame,label,location in [('Idle',1,'Espalda',(2.7,4.5,2.1)),('Walk',7,'Caminar',(3,-5,2)),('Run',5,'Correr',(3,-5,2)),('Run',13,'Carrera_espalda',(3,5,2))]:
    rig.animation_data.action=next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name==mode);scene.frame_set(frame);scene.camera.location=location;scene.camera.rotation_euler=(Vector((0,0,.93))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.1
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.resolution_x=420;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders'/(label+'.png'));bpy.ops.render.render(write_still=True)
print('BACKPACK_FIT',shoulder,delta,material.name,flush=True)
