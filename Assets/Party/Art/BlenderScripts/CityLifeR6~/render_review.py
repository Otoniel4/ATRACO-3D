"""Vídeo de revisión con tiempos reales de simulación, sin acelerar el movimiento."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'));scene=bpy.context.scene
for marker in scene.timeline_markers:marker.camera=None
data=bpy.data.cameras.new('R6_RestaurantCamera');restaurant=bpy.data.objects.new(data.name,data);scene.collection.objects.link(restaurant);target=Vector((18,-.3,.8));restaurant.location=target+Vector((4,5.5,10));restaurant.rotation_euler=(target-restaurant.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=14
segments=[(0,6,'LifeR6_StreetCamera','Paseo y acceso por la acera'),(22,8,'R6_MarketCamera','Seleccionar y tomar el producto'),(35,10,'R6_CheckoutCamera','Fila, escaneo, dinero y recibo'),(38,6,'R6_JewelryCamera','Compras en la joyeria'),(42,6,'R6_RestaurantCamera','Restaurante: producto y caja'),(80,6,'LifeR6_StreetCamera','Salida con bolsa y circulacion')]
street=next((o for o in scene.objects if o.type=='CAMERA' and 'StreetCamera' in o.name),None);assert street
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=16
folder=B/'video_frames';folder.mkdir(exist_ok=True);frames=[];index=0
for begin,seconds,name,label in segments:
    camera=bpy.data.objects.get(name) or street
    for sample in range(seconds*8):
        frame=round((begin+sample/8)*24)+1;scene.frame_set(frame);scene.camera=camera;path=folder/(str(index).zfill(5)+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        frames.append({'index':index,'source_frame':frame,'label':label});index+=1
    print('VIDEO_SEGMENT_READY',label,flush=True)
(B/'video_frames.json').write_text(json.dumps(frames,indent=2));print('VIDEO_FRAMES_READY',index,flush=True)
