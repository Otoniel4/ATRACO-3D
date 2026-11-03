"""Ocho segundos de movimiento real de las hojas y las briznas, renderizados a 12 fps."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Macetas_Pasto_Viento_R4.blend'))
scene=bpy.data.scenes['PlantersR4_Closeup'];bpy.context.window.scene=scene
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.frame_step=2
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=24
(BASE/'animation_frames').mkdir(exist_ok=True)
scene.render.filepath=str(BASE/'animation_frames/frame_')
bpy.ops.render.render(animation=True)
print('PLANT_WIND_FRAMES_READY',flush=True)
