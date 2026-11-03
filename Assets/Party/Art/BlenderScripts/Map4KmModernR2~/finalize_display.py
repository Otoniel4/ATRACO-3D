"""Encuadre inicial y sombreado de revisión; no modifica modelos ni materiales."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
bpy.context.window.scene=bpy.data.scenes['CityR2_StreetLevel']
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        space=area.spaces.active;space.clip_end=30000;space.clip_start=.1
        space.overlay.show_overlays=False;space.overlay.show_relationship_lines=False
        space.shading.show_shadows=False;space.shading.show_cavity=False
        space.shading.type='MATERIAL';space.shading.use_scene_world=True;space.shading.use_scene_lights=True
        space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0;space.region_3d.view_camera_offset=(0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
print('R2_DISPLAY_READY')
