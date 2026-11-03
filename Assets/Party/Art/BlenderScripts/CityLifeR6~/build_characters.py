"""Conserva proporciones y piernas R3, aÃ±ade manos, agarres y cinco clips para el elenco completo."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from animation import pose,bake_actions
from sources import previous_revision;old=previous_revision();bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_Manos_R6.blend'))
with bpy.data.libraries.load(str(old/'Objetos_Locales_R5.blend'),link=False) as (src,dst):dst.meshes=['Life5_ShoppingBag']
catalog=json.loads((B/'hands_catalog.json').read_text());original=json.loads((old/'baseline/cast_catalog.json').read_text());report=[]
for row in catalog:
    scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']];scene.render.fps=24;scene.frame_start=1;scene.frame_end=49
    actions=bake_actions(rig);rig.animation_data.action=None;pose(rig,0,'CarryWalk')
    hand=rig.pose.bones['RightHand'];grip=bpy.data.objects.new('Grip_R6_'+row['id'],None);scene.collection.objects.link(grip);grip.parent=rig;grip.parent_type='BONE';grip.parent_bone='RightHand';bpy.context.view_layer.update()
    matrix=Matrix.Identity(4);matrix.translation=rig.matrix_world@(hand.matrix@Vector((0,.065,.012)));grip.matrix_world=matrix
    bag=bpy.data.objects.new('ShoppingBag_'+row['id'],bpy.data.meshes['Life5_ShoppingBag']);scene.collection.objects.link(bag);bag.parent=grip;bag.location=(0,0,0);bag.hide_render=True;bag.hide_viewport=True
    row.update({'grip':grip.name,'bag':bag.name,'clips':list(actions),'group':next(e['group'] for e in original if e['id']==row['id'])})
    # La galerÃ­a muestra las manos nuevas en reposo, sin esconder mangas o partes del cuerpo.
    rig.animation_data.action=None;pose(rig,0,'Idle');centre=rig.matrix_world@(rig.pose.bones['RightHand'].matrix@Vector((0,.055,0)))
    cam=scene.camera;cam.location=centre+Vector((-.25,-1,.18));cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.29
    scene.render.resolution_x=360;scene.render.resolution_y=420;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders'/('Mano_'+row['id']+'.png'));bpy.ops.render.render(write_still=True)
    rig.animation_data.action=actions['Idle'];scene.frame_set(1);report.append(row)
(B/'animation_catalog.json').write_text(json.dumps(report,indent=2));bpy.context.window.scene=bpy.data.scenes['LifeR6_NPC02_Denim']
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Elenco_Animado_R6.blend'),compress=True);print('ANIMATED_CAST_R6',len(report),flush=True)
