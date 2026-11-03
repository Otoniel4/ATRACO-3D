"""Dos vistas de los árboles nuevos dentro de la ciudad. Retratos: render_portraits.py."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Arboles_Viento_R3.blend'))
for name in ['StreetLevel','Plaza']:
    scene=bpy.data.scenes['CityR3_'+name];bpy.context.window.scene=scene;scene.frame_set(49)
    scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=48
    scene.render.filepath=str(BASE/'renders'/('City_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('NATURAL_FOLIAGE_REVIEWS_READY',flush=True)
