"""Vídeo de la revisión de Blender: simulación local horneada, no captura del juego Unity."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Ciudad_Viva_Demo_R5.blend'))
scene=bpy.data.scenes['LifeR5_AnimatedDistrict'];bpy.context.window.scene=scene
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.frame_start=1;scene.frame_end=576;scene.frame_step=2
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=24
(BASE/'animation_frames').mkdir(exist_ok=True);scene.render.filepath=str(BASE/'animation_frames/frame_')
bpy.ops.render.render(animation=True)
print('CITY_LIFE_FRAMES_READY',288,flush=True)
