import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'));scene=bpy.context.scene
def aim(name,target,offset,scale):
    obj=bpy.data.objects[name];target=Vector(target);obj.location=target+Vector(offset);obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler();obj.data.ortho_scale=scale;return obj
market=aim('R6_MarketCamera',(-18,-.4,.7),(4,5.5,10),14)
jewelry=aim('R6_JewelryCamera',(0,0,.7),(4,5.5,10),14)
close=aim('R6_CheckoutCamera',(-15,-2.7,1),(-2.6,1.8,2.4),3.9)
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for f,cam in [(1,scene.camera),(400,market),(850,close),(1000,market),(1120,close),(1220,jewelry),(1700,market)]:marker=scene.timeline_markers.new('Review_'+str(f),frame=f);marker.camera=cam
# Evita una vuelta entera al cruzar -pi/pi, con giros máximos de 15 grados por fotograma.
trace=json.loads((B/'preview_traces.json').read_text())
for i in range(24):
    root=bpy.data.objects['R6_Resident_'+str(i)];action=root.animation_data.action;curve=next(c for c in action.fcurves if c.data_path=='rotation_euler' and c.array_index==2);yaw=trace['actors'][i][0]['yaw']
    for key,row in zip(curve.keyframe_points,trace['actors'][i]):
        delta=(row['yaw']-yaw+math.pi)%math.tau-math.pi;yaw+=max(-math.pi/12,min(math.pi/12,delta));key.co.y=yaw
scene.frame_set(925);scene.camera=close;bpy.ops.wm.save_as_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'),compress=True)
for frame,cam,name in [(895,market,'Mercado_Fila_R6'),(932,close,'Caja_Manos_R6'),(1200,jewelry,'Joyeria_R6')]:
    scene.frame_set(frame);scene.camera=cam;scene.render.filepath=str(B/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PREVIEW_REVIEW_FIXED',flush=True)
