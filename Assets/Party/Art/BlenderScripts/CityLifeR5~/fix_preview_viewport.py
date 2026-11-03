"""Deja el inicio de la rutina y el corte de techo visibles al abrir la demo."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent;FILE=BASE/'Ciudad_Viva_Demo_R5.blend'
bpy.ops.wm.open_mainfile(filepath=str(FILE));scene=bpy.data.scenes['LifeR5_AnimatedDistrict'];bpy.context.window.scene=scene
for obj in scene.objects:
    if obj.name.startswith('Roof_'):obj.hide_set(True)
scene.frame_set(1);scene.camera=bpy.data.objects['LifeR5_StreetCamera']
bpy.ops.wm.save_as_mainfile(filepath=str(FILE),compress=True)
print('PREVIEW_VIEWPORT_READY',flush=True)
