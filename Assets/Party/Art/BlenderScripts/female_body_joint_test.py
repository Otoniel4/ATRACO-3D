"""Prueba de articulaciones de la base de estudio; no son animaciones del juego."""
import bpy,math
from mathutils import Vector
scene=bpy.data.scenes['FemaleBody_AnatomyStudy'];bpy.context.window.scene=scene
rig=bpy.data.objects['FemaleStudy_DiagnosticRig']
for bone in rig.pose.bones:
 bone.rotation_mode='XYZ';bone.rotation_euler=(0,0,0);bone.keyframe_insert('rotation_euler',frame=1)
rig.pose.bones['Forearm.R'].rotation_euler.x=math.radians(85)
rig.pose.bones['Thigh.L'].rotation_euler.x=math.radians(-30)
rig.pose.bones['Shin.L'].rotation_euler.x=math.radians(65)
for bone in rig.pose.bones:bone.keyframe_insert('rotation_euler',frame=30)
for bone in rig.pose.bones:bone.rotation_euler=(0,0,0);bone.keyframe_insert('rotation_euler',frame=60)
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='Diagnostic_Elbow_Knee_Only'
scene.frame_end=60;scene.frame_set(1)
print('Diagnostic pose keys: 1 rest; 30 elbow/knee; 60 rest')
