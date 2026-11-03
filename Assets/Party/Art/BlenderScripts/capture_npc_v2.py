"""Capturas reales del viewport de Blender para revisión, sin retocar el modelo."""
import bpy
import npc_v2 as npc

def capture(index,views=('front','right','back')):
 root=bpy.data.objects['NPC2_'+npc.SPECS[index-1][0]]
 scene=bpy.data.scenes[npc.SCENE_NAME];bpy.context.window.scene=scene
 scene.render.resolution_x=650;scene.render.resolution_y=850
 area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
 region=next(r for r in area.regions if r.type=='WINDOW')
 for view in views:
  npc.frame(root,view)
  scene.render.filepath=str(npc.OUT/(root.name+'-'+view+'.png'))
  with bpy.context.temp_override(area=area,region=region):
   bpy.ops.render.opengl(write_still=True,view_context=False)
 print('CAPTURED',root.name,list(views))
