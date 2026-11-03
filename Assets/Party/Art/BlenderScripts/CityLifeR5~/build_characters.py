"""Copia los diez civiles aprobados, sin modificar sus mallas ni pesos, y crea cinco clips propios."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from animation import pose,bake_actions
bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/Cast_R3.blend'))
with bpy.data.libraries.load(str(BASE/'Objetos_Locales_R5.blend'),link=False) as (src,dst):dst.meshes=['Life5_ShoppingBag']
report=[];catalog=json.loads((BASE/'baseline/cast_catalog.json').read_text());actors=[r for r in catalog if r['group']=='civil']
for index,entry in enumerate(actors):
    identifier=entry['id'];scene=bpy.data.scenes['LegsR3_'+identifier];scene.name='LifeR5_'+identifier;bpy.context.window.scene=scene
    scene.render.fps=24;scene.frame_start=1;scene.frame_end=49
    rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.hide_set(False)
    actions=bake_actions(rig);rig.animation_data.action=None;pose(rig,0,'CarryWalk')
    bag=bpy.data.objects.new('ShoppingBag_'+identifier,bpy.data.meshes['Life5_ShoppingBag']);scene.collection.objects.link(bag)
    bag.parent=rig;bag.parent_type='BONE';bag.parent_bone='RightHand';bpy.context.view_layer.update()
    hand=rig.pose.bones['RightHand'];grip=rig.matrix_world@(hand.matrix@Vector((0,hand.length*.7,0)))
    matrix=Matrix.Identity(4);matrix.translation=grip;bag.matrix_world=matrix;bag.hide_render=True
    rig.animation_data.action=actions['Walk'];scene.frame_set(5)
    # Apoyo medido en los zapatos evaluados de todos los civiles.
    shoes=[o for o in scene.objects if o.type=='MESH' and any(t in o.name.lower() for t in ['shoes','shoe'])]
    minimum=math.inf
    for frame in range(1,26,3):
        scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
        for obj in shoes:
            evaluated=obj.evaluated_get(deps)
            minimum=min(minimum,min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices))
    if not shoes:raise RuntimeError('No se identificaron zapatos de '+identifier)
    report.append({'id':identifier,'rig':rig.name,'scene':scene.name,'bones':len(rig.data.bones),'clips':list(actions),
                   'shoe_min_z_m':minimum,'bag':bag.name,'source_meshes_and_weights_edited':False})
    if index in [0,1]:
        scene.frame_set(6);camera=scene.camera;target=Vector((0,0,.82));camera.location=target+Vector((3,-6,1.3))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=2.2
        scene.render.resolution_x=650;scene.render.resolution_y=800;scene.render.resolution_percentage=100
        scene.render.filepath=str(BASE/'renders'/('Paso_'+identifier+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(1)
(BASE/'animation_catalog.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['LifeR5_NPC02_Denim']
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Civiles_Animados_R5.blend'),compress=True)
print('CIVILIANS_ANIMATED',json.dumps(report),flush=True)
