"""Contrasta la deformación real de Geometry Nodes con la fórmula mundial y prueba el bucle."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from tree_geometry import C
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Arboles_Viento_R3.blend'))
scene=bpy.data.scenes['Trees_R3_Wind_Closeup'];bpy.context.window.scene=scene
obj=bpy.data.objects['Hero_Fresno'];obj.location=(7,-3,.18);obj.rotation_euler.z=.43;obj.scale=(1.1,.9,1.04)
mod=obj.modifiers['NaturalWind_R3']
values={'WorldOffset':tuple(obj.location),'Scale':tuple(obj.scale),'Yaw':obj.rotation_euler.z}
for item in mod.node_group.interface.items_tree:
    if item.item_type=='SOCKET' and item.in_out=='INPUT' and item.name in values:mod[item.identifier]=values[item.name]
bpy.context.view_layer.update();matrix=obj.matrix_world.copy();inverse=matrix.inverted()
colors=obj.data.color_attributes['WindMask'].data;original=[v.co.copy() for v in obj.data.vertices]
direction=Vector((C['wind_direction_unity_xz'][0],-C['wind_direction_unity_xz'][1],0)).normalized();perp=Vector((-direction.y,direction.x,0))
def reference(p,color,frame):
    world=matrix@p;x,y=world.x,world.y;r,g,b,a=color
    t=frame/C['fps']*C['wind_speed']*math.tau/C['loop_seconds'];spatial=.037*x-.025*y
    gust=.65+.35*math.sin(2*t+spatial*.37+1.2)
    primary=r*C['primary_amplitude_m']*math.sin(t+spatial)*gust
    branch=g*C['branch_amplitude_m']*math.sin(3*t+.35*x-.21*y)
    flutter=b*C['leaf_amplitude_m']*math.sin(9*t+a*math.tau+.13*x-.11*y)
    vertical=b*C['leaf_vertical_amplitude_m']*math.sin(13*t+a*math.tau*1.7)
    return inverse@(world+(direction*(primary+branch)+perp*flutter+Vector((0,0,vertical)))*C['wind_strength'])
snapshots={};max_error=0;root_motion=0
sample=range(0,len(original),max(1,len(original)//600))
for frame in [1,25,49,97,145,193]:
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(deps)
    positions=[v.co.copy() for v in evaluated.data.vertices];snapshots[frame]=positions
    for i in sample:max_error=max(max_error,(positions[i]-reference(original[i],colors[i].color,frame)).length)
    for i,p in enumerate(original):
        if p.z<=.001:root_motion=max(root_motion,(positions[i]-p).length)
loop_error=max((a-b).length for a,b in zip(snapshots[1],snapshots[193]))
leaf_motion=max((a-b).length for i,(a,b) in enumerate(zip(snapshots[1],snapshots[49])) if colors[i].color[2]>.5)
assert max_error<.0001,max_error
assert root_motion<1e-6,root_motion
assert loop_error<.0001,loop_error
assert leaf_motion>.08,leaf_motion
report={'formula_max_error_m':max_error,'root_motion_m':root_motion,'loop_error_m':loop_error,
        'leaf_motion_example_m':leaf_motion,'loop_seconds':C['loop_seconds'],'fps':C['fps'],
        'tested_frames':[1,25,49,97,145,193],'transform_test':'translation, yaw, nonuniform scale','passed':True}
(BASE/'wind_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('WIND_VALIDATED',json.dumps(report),flush=True)
