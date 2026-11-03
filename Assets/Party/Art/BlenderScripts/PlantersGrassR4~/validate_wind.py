"""Comprueba raíces fijas, macetas inmóviles y cierre del bucle sobre las mallas evaluadas."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from flora import C
from wind_nodes import attach
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Macetas_Pasto_Viento_R4.blend'))
scene=bpy.data.scenes['PlantersR4_Closeup'];bpy.context.window.scene=scene
objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('PlantR4_')]
roots=0;root_motion=0;loop_error=0;motion={'shrub':0,'grass':0};max_error=0;parent_tested=False
direction=Vector((.93,-.35,0)).normalized();side=Vector((-direction.y,direction.x,0))
for obj in objects:
    if obj.modifiers:
        # También se comprueba una jerarquía girada y escalada, como los jardines de la ciudad.
        if not parent_tested:
            parent=bpy.data.objects.new('ValidationParent',None);scene.collection.objects.link(parent)
            parent.location=(3,-2,.3);parent.rotation_euler.z=.42;parent.scale=(1.1,1.1,1.1);obj.parent=parent
            bpy.context.view_layer.update();group=obj.modifiers[0].node_group;obj.modifiers.clear();attach(obj,group)
            parent_tested=True
    original=[v.co.copy() for v in obj.data.vertices];mask=obj.data.color_attributes['WindMask'].data
    assert all(all(math.isfinite(v) and -.00001<=v<=1.00001 for v in color.color) for color in mask),obj.name
    snapshots={};matrix=obj.matrix_world.copy();inverse=matrix.inverted()
    for frame in [1,49,97,145,193]:
        scene.frame_set(frame);evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        positions=[v.co.copy() for v in evaluated.data.vertices];snapshots[frame]=positions
        for i in range(0,len(original),max(1,len(original)//150)):
            p=matrix@original[i];r,g,b,a=mask[i].color;t=frame/24*math.tau/8;spatial=.037*p.x-.025*p.y
            gust=.65+.35*math.sin(2*t+spatial*.37+1.2)
            primary=r*.24*math.sin(t+spatial)*gust;branch=g*.09*math.sin(3*t+.35*p.x-.21*p.y)
            flutter=b*.045*math.sin(9*t+a*math.tau+.13*p.x-.11*p.y);vertical=b*.028*math.sin(13*t+a*math.tau*1.7)
            expected=inverse@(p+direction*(primary+branch)+side*flutter+Vector((0,0,vertical))) if obj.modifiers else original[i]
            max_error=max(max_error,(positions[i]-expected).length)
        for i,color in enumerate(mask):
            if max(color.color[:3])<1e-7:
                roots+=1;root_motion=max(root_motion,(positions[i]-original[i]).length)
    loop_error=max(loop_error,max((a-b).length for a,b in zip(snapshots[1],snapshots[193])))
    kind='grass' if 'Grass' in obj.name else 'shrub'
    if obj.modifiers:motion[kind]=max(motion[kind],max((a-b).length for a,b in zip(snapshots[1],snapshots[49])))
assert root_motion<1e-6,root_motion
assert loop_error<.0001,loop_error
assert max_error<.0001,max_error
assert all(value>.012 for value in motion.values()),motion
report={'static_root_samples':roots,'root_and_pot_motion_m':root_motion,'loop_error_m':loop_error,
        'formula_error_m':max_error,'sampled_motion_m':motion,'tested_objects':len(objects),'loop_seconds':8,
        'parent_rotation_scale_tested':parent_tested,'passed':True}
(BASE/'wind_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PLANT_WIND_VALIDATED',json.dumps(report),flush=True)
