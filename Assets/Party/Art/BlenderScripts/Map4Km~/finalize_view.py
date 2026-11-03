"""Guarda el encuadre inicial del archivo entregable. No altera geometría ni exportaciones."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
bpy.context.window.scene=bpy.data.scenes['Map4Km_Center']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        space=area.spaces.active;space.clip_end=30000;space.clip_start=.1
        space.overlay.show_overlays=False
        space.shading.type='SOLID';space.shading.color_type='MATERIAL'
        space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
        space.region_3d.view_camera_offset=(0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
print('MAP_INITIAL_VIEW_SAVED')
