"""Previsualización real de ocho segundos, a 24 fps, sin interpolar imágenes."""
import bpy,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Arboles_Viento_R3.blend'))
scene=bpy.data.scenes['Trees_R3_Wind_Closeup'];bpy.context.window.scene=scene
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
(BASE/'animation_frames').mkdir(exist_ok=True)
scene.render.filepath=str(BASE/'animation_frames/frame_');scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(animation=True)
print('WIND_ANIMATION_FRAMES_READY',scene.frame_end,flush=True)
