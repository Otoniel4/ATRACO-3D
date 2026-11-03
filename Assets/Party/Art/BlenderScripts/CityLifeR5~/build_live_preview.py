"""Hornea una revisión de paseos, entrada, fila, pago y salida. Conserva geometría y pesos R3."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Distrito_Comercial_R5.blend'))
scene=bpy.context.scene;scene.name='LifeR5_AnimatedDistrict';scene.frame_start=1;scene.frame_end=576
catalog=json.loads((BASE/'animation_catalog.json').read_text());old=json.loads((BASE/'cast_inspection.json').read_text())
names=set()
for actor in catalog:
    source=next(s for s in old if s['scene']=='LegsR3_'+actor['id'])
    names.update(o['name'] for o in source['objects']);names.update([actor['rig'],actor['bag']])
with bpy.data.libraries.load(str(BASE/'Civiles_Animados_R5.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in names]
sources={o.name:o for o in dst.objects};traces=json.loads((BASE/'preview_traces.json').read_text());roots=[]
for index,actor in enumerate(catalog):
    source=next(s for s in old if s['scene']=='LegsR3_'+actor['id']);object_names=[actor['rig'],actor['bag']]+[o['name'] for o in source['objects']]
    copied={}
    for name in object_names:
        obj=sources[name].copy();obj.name='LiveR5_'+name;scene.collection.objects.link(obj);copied[sources[name]]=obj
    root=bpy.data.objects.new('Resident_'+actor['id'],None);scene.collection.objects.link(root);roots.append(root)
    for src,obj in copied.items():
        if src.parent in copied:obj.parent=copied[src.parent]
        for modifier in obj.modifiers:
            if modifier.type=='ARMATURE' and modifier.object in copied:modifier.object=copied[modifier.object]
    rig=copied[sources[actor['rig']]];rig.parent=root;rig.hide_set(False);rig.animation_data_clear();rig.animation_data_create()
    actions={mode:bpy.data.actions[actor['rig']+'_'+mode] for mode in actor['clips']}
    base=rig.animation_data.nla_tracks.new();base.name='IdleBase';strip=base.strips.new('IdleBase',1,actions['Idle']);strip.repeat=12;strip.frame_end=577
    track=rig.animation_data.nla_tracks.new();track.name='Routine';bag=copied[sources[actor['bag']]]
    samples=traces['actors'][index];segments=[];begin=1;mode=samples[0]['mode']
    for row in samples[1:]+[{'frame':577,'mode':'END'}]:
        if row['mode']==mode:continue
        segments.append((begin,row['frame'],mode));begin=row['frame'];mode=row['mode']
    for begin,end,mode in segments:
        if mode=='Idle':continue
        action=actions[mode];strip=track.strips.new(mode,begin,action);length=action.frame_range[1]-action.frame_range[0]
        strip.repeat=max(.1,(end-begin)/length);strip.frame_end=end;strip.extrapolation='NOTHING'
        strip.blend_in=min(3,(end-begin)/3);strip.blend_out=min(3,(end-begin)/3)
    last_carry=None
    for row in samples:
        f=row['frame']
        if f%2==1 or f==576:
            root.location=row['position'];root.rotation_euler.z=row['yaw'];root.keyframe_insert(data_path='location',frame=f);root.keyframe_insert(data_path='rotation_euler',frame=f)
        if row['carrying']!=last_carry:
            bag.hide_render=not row['carrying'];bag.hide_viewport=not row['carrying']
            bag.keyframe_insert(data_path='hide_render',frame=f);bag.keyframe_insert(data_path='hide_viewport',frame=f);last_carry=row['carrying']
    root['PreviewScripted']=True;root['CharacterId']=actor['id']
for leaf in ['L','R']:
    door=bpy.data.objects['Door_Minimarket_'+leaf];base_yaw=0 if leaf=='L' else math.pi;angle=0;until=0
    for frame in range(1,577):
        t=frame/24
        if any(math.hypot(rows[frame-1]['position'][0]+18,rows[frame-1]['position'][1]+5.12)<2.4 for rows in traces['actors']):until=t+1.2
        target=1.309 if t<until else 0;angle+=max(-2.44/24,min(2.44/24,target-angle))
        door.rotation_euler.z=base_yaw+(-angle if leaf=='L' else angle);door.keyframe_insert(data_path='rotation_euler',frame=frame)
# Se alternan exterior e interior para poder ver la caja y la salida con bolsa.
data=bpy.data.cameras.new('LifeR5_CheckoutCamera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
target=Vector((-17.1,-2.0,.75));camera.location=target+Vector((7,8,8));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=13.2
for frame,cam in [(1,scene.camera),(145,camera),(481,scene.camera)]:
    marker=scene.timeline_markers.new('Review_'+str(frame),frame=frame);marker.camera=cam
for source in list(sources.values()):
    if source.users==0:bpy.data.objects.remove(source)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
scene.frame_set(240);bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Ciudad_Viva_Demo_R5.blend'),compress=True)
scene.render.filepath=str(BASE/'renders/Clientes_Comprando_R5.png');bpy.ops.render.render(write_still=True)
scene.frame_set(1);scene.render.filepath=str(BASE/'renders/Peatones_Calle_R5.png');bpy.ops.render.render(write_still=True)
print('CITY_LIFE_PREVIEW_READY',len(roots),'animated residents',len(traces['purchases']),'purchases',flush=True)
