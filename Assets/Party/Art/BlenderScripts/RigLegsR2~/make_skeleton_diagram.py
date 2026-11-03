"""Proyecta las posiciones reales de los huesos sobre el render frontal de Toñito."""
import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Alarma_RigLegs_R2.blend'))
scene=bpy.data.scenes['RigReview_Player04_Muscle'];bpy.context.window.scene=scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
width,height=820,1000
result=[]
for bone in rig.data.bones:
    ends=[]
    for p in [bone.head_local,bone.tail_local]:
        ndc=world_to_camera_view(scene,scene.camera,rig.matrix_world@p)
        ends.append([ndc.x*width,(1-ndc.y)*height])
    result.append({'bone':bone.name,'projected_endpoints':ends})
(BASE/'skeleton_projection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('SKELETON_PROJECTION_READY')
