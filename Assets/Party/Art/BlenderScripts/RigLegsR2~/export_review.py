"""Exporta los 18 actores y captura pruebas de rodilla/cadera/hombro."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Alarma_RigLegs_R2.blend'))
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
only=set(sys.argv[sys.argv.index('--only')+1].split(',')) if '--only' in sys.argv else None

def shot(scene,center,direction,scale,path,size=(650,850)):
    bpy.context.window.scene=scene;camera=scene.camera;center=Vector(center)
    camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size;scene.render.resolution_percentage=100
    scene.render.filepath=str(path);scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    bpy.ops.render.render(write_still=True)

for actor in manifest['characters']:
    identifier=actor['id'];scene=bpy.data.scenes['RigReview_'+identifier];bpy.context.window.scene=scene
    rig=next(o for o in scene.objects if o.type=='ARMATURE');meshes=[o for o in scene.objects if o.type=='MESH']
    if only and identifier not in only:
        center=Vector((0,0,actor['height_m']/2));camera=scene.camera
        camera.location=center+Vector((0,-6,0));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=actor['height_m']*1.1
        scene.render.resolution_x=820;scene.render.resolution_y=1000
        continue
    rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[rig]:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    (BASE/'fbx').mkdir(exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(BASE/'fbx'/(identifier+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},
        apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,
        add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
    rig.hide_set(True)
    height=actor['height_m'];center=(0,0,height/2)
    folder=BASE/'renders'/identifier;folder.mkdir(parents=True,exist_ok=True)
    shot(scene,center,(0,-6,0),height*1.1,folder/'front.png',size=(820,1000))
    if identifier in {'NPC03_Tourist','NPC10_Cardigan','Player04_Muscle'}:
        shot(scene,center,(-6,0,0),height*1.1,folder/'side.png')
        shot(scene,center,(0,6,0),height*1.1,folder/'back.png',size=(820,1000))
        shot(scene,center,(-4,-7,.7),height*1.1,folder/'three_quarter.png',size=(820,1000))
    pose={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
    # Un paso amplio: la rodilla debe doblarse hacia atrás y el hombro soportar flexión.
    for name,angle in [('LeftUpperLeg',-25),('LeftLowerLeg',75),('LeftFoot',-35),
                       ('RightUpperArm',25),('RightLowerArm',45)]:
        b=rig.pose.bones[name];b.rotation_mode='XYZ';b.rotation_euler.x=math.radians(angle)
    bpy.context.view_layer.update()
    shot(scene,center,(-4,-7,.8),height*1.2,folder/'step_pose.png')
    for b in rig.pose.bones:b.matrix_basis=pose[b.name]
    # Flexión de las dos rodillas, vista lateral para ver giro y penetraciones.
    for prefix in ['Left','Right']:
        for name,angle in [('UpperLeg',-35),('LowerLeg',80),('Foot',-40)]:
            b=rig.pose.bones[prefix+name];b.rotation_mode='XYZ';b.rotation_euler.x=math.radians(angle)
    bpy.context.view_layer.update()
    shot(scene,center,(-6,-2,.3),height*1.2,folder/'double_knee_pose.png')
    for b in rig.pose.bones:b.matrix_basis=pose[b.name]
    bpy.context.view_layer.update()
    shot(scene,center,(0,-6,0),height*1.1,folder/'front.png',size=(820,1000))
    print('RIG_REVIEW_EXPORTED',identifier,flush=True)

gallery=bpy.data.scenes['RigReview_Gallery'];bpy.context.window.scene=gallery
gallery.render.filepath=str(BASE/'renders/gallery.png');bpy.ops.render.render(write_still=True)
bpy.context.window.scene=bpy.data.scenes['RigReview_Player04_Muscle']
# El archivo abre la cámara del actor, con el personaje a escala legible.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_camera_zoom=0;sp.region_3d.view_camera_offset=(0,0)
            sp.region_3d.view_location=(0,0,.94);sp.region_3d.view_distance=3
            allowed={i.identifier for i in sp.region_3d.bl_rna.properties['view_perspective'].enum_items}
            if 'CAMERA' in allowed:sp.region_3d.view_perspective='CAMERA'
            sp.overlay.show_extras=False
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Alarma_RigLegs_R2.blend'))
print('REVIEW_RENDER_SUCCESS',18,flush=True)
