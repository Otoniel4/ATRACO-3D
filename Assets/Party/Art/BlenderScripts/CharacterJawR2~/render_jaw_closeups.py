import bpy,sys,json
from pathlib import Path
from mathutils import Vector
folder=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(folder/'character.blend'))
scene=bpy.data.scenes['Character_Blockout_4x'];bpy.context.window.scene=scene
body=scene.objects['Body']
print('NECK_BOUNDARY',body.get('HeadNeckBoundaryVertices'))
camera=scene.camera;center=Vector((0,-.008,1.435))
out=folder/'jaw_closeups';out.mkdir(exist_ok=True)
scene.render.resolution_x=540;scene.render.resolution_y=660
camera.data.ortho_scale=.46
for view,d in [('front',(0,-6,0)),('side',(-6,0,0)),('three_quarter',(-4,-6,0))]:
    camera.location=center+Vector(d);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True)
