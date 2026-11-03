"""Estudio de referencias, no personaje ni rig de producción. No exportar a Unity."""
import bpy, math
from mathutils import Vector
from pathlib import Path
A=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
O=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Correccion-Personajes')
name='NPC01_ReferenceCalibration'
if name in bpy.data.scenes:raise RuntimeError('El estudio ya existe; revisar antes de regenerarlo')
scene=bpy.data.scenes.new(name);bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.resolution_x=900;scene.render.resolution_y=1050
scene.view_settings.view_transform='Standard'
def emission(name,color,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
 output=n.new('ShaderNodeOutputMaterial');shader=n.new('ShaderNodeEmission');shader.inputs['Color'].default_value=(*color,1)
 if image:
  tex=n.new('ShaderNodeTexImage');tex.image=image;m.node_tree.links.new(tex.outputs['Color'],shader.inputs['Color'])
 m.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);return m
blue=emission('Calibration_Blue',(.025,.20,.75));orange=emission('Calibration_Landmarks',(.9,.12,.025))
def line(label,points,material,width=.002):
 c=bpy.data.curves.new(label,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=1
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(label,c);scene.collection.objects.link(o);c.materials.append(material);o['Purpose']='Reference guide only; not final character';return o
def imageplane(view,file,width,center):
 im=bpy.data.images.load(str(A/'References~/NPC01_Calibrated'/file),check_existing=True);im.pack()
 w=width*.002;h=1.86;data=bpy.data.meshes.new('Reference_'+view)
 data.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)])
 uv=data.uv_layers.new(name='ReferenceUV')
 for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
 obj=bpy.data.objects.new('REFERENCE_ONLY_'+view,data);scene.collection.objects.link(obj);obj.location=center
 if view=='Side':obj.rotation_euler.z=-math.pi/2
 if view=='Back':obj.rotation_euler.z=math.pi
 data.materials.append(emission('ReferenceImage_'+view,(1,1,1),im));obj['DoNotExport']=True
 return obj
front=imageplane('Front','Front.png',539,(-.011,.25,.898))
side=imageplane('Side','Side.png',235,(.25,.005,.898))
back=imageplane('Back','Back.png',487,(.003,-.25,.898))
landmarks={'pelvis':(0,0,.91),'waist':(0,0,1.08),'sternum':(0,0,1.30),'neck':(0,0,1.48),'chin':(0,-.03,1.52),'crown':(0,0,1.80)}
line('Axis',[(0,0,0),(0,0,1.82)],blue,.001)
line('Trunk',[landmarks[k] for k in ('pelvis','waist','sternum','neck')],orange)
for sign in [-1,1]:
 arm=[(0,0,1.44),(sign*.22,0,1.44),(sign*.32,-.01,1.17),(sign*.405,-.04,.94),(sign*.435,-.07,.79)]
 leg=[(0,0,.91),(sign*.105,0,.88),(sign*.16,-.012,.48),(sign*.17,0,.16),(sign*.20,-.12,.06)]
 line('ArmLandmarks_'+str(sign),arm,orange);line('LegLandmarks_'+str(sign),leg,orange)
for z,label in [(0,'Ground'),(.16,'Ankles'),(.48,'Knees'),(.91,'Hips'),(1.17,'Elbows'),(1.44,'Shoulders'),(1.52,'Chin'),(1.80,'Crown')]:
 line('FrontLevel_'+label,[(-.56,-.01,z),(.56,-.01,z)],blue,.0009)
 line('SideLevel_'+label,[(-.01,-.26,z),(-.01,.26,z)],blue,.0009)
camera_data=bpy.data.cameras.new('CalibrationCamera');camera=bpy.data.objects.new('CalibrationCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=2.05
world=bpy.data.worlds.new('CalibrationWorld');world.use_nodes=True;scene.world=world
def view(which):
 for key,obj in [('Front',front),('Side',side),('Back',back)]:obj.hide_render=key!=which;obj.hide_set(key!=which)
 center=Vector((0,0,.90));direction={'Front':(0,-5,0),'Side':(-5,0,0),'Back':(0,5,0)}[which]
 camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 scene.render.filepath=str(O/('Calibracion-'+which+'.png'));bpy.ops.render.render(write_still=True)
for which in ['Side','Front']:view(which)
scene['Status']='Reference calibration only. New character anatomy and clothing NOT yet built.'
scene['HeightScale']='1.8 m; 900 pixels from crown to ground in the supplied drawing'
path=A/'BlenderSources~/NPC01_ReferenceCalibration.blend';bpy.data.libraries.write(str(path),{scene},fake_user=True)
print('REFERENCE_CALIBRATION_SAVED',str(path),'No character or rig delivered')
