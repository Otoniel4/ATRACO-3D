"""Render de las jardineras en el minimercado y del pasto próximo, dentro del mapa real."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Jardineras_Pasto_R4.blend'))
scene=bpy.data.scenes['CityR4_PlanterDetail'];bpy.context.window.scene=scene;scene.frame_set(49)
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
scene.render.filepath=str(BASE/'renders/Ciudad_Jardineras_R4.png');bpy.ops.render.render(write_still=True)
print('CITY_PLANT_REVIEW_READY',flush=True)
