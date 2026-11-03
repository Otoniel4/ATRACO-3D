"""Ajustar las dos bases desde la estructura continua aprobada por Alain."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ART=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
OUT=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Bases-Corporales');OUT.mkdir(exist_ok=True)
NAME='BodyBases_Refined'
if bpy.data.scenes.get(NAME):raise RuntimeError('La revisión ya existe. No sobrescribir sin inspeccionarla.')
source=bpy.data.objects['FemaleBody_Study'];source_rig=bpy.data.objects['FemaleStudy_DiagnosticRig']
scene=bpy.data.scenes.new(NAME);bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.frame_end=60
def gaussian(z,center,width):return math.exp(-((z-center)/width)**2)
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def interpolate(z,pairs):
 pairs=sorted(pairs)
 if z<=pairs[0][0]:return pairs[0][1]
 for (a,x),(b,y) in zip(pairs,pairs[1:]):
  if z<=b:return x+(y-x)*(z-a)/(b-a)
 return pairs[-1][1]
def warp(point,gender):
 x,y,z=point;sign=1 if x>=0 else -1
 torso=1-smooth(.21,.30,abs(x))
 front=max(0,min(1,-y/.10));back=max(0,min(1,y/.12))
 if gender=='Female':
  change=-.075*gaussian(z,1.085,.075)+.070*gaussian(z,.935,.10)
  x=x*(1+change*torso)
  y+=.006*gaussian(z,1.085,.08)*front*torso
  y+=.020*gaussian(z,.91,.10)*back*torso
  y-=.012*gaussian(z,1.275,.065)*gaussian(abs(point[0]),.075,.055)*front*torso
  if z<.86:
   cx=sign*interpolate(z,[(.15,.158),(.34,.145),(.465,.137),(.67,.115),(.78,.103),(.875,.10)])
   x=cx+(x-cx)*(1+.035*gaussian(z,.72,.11))
  return Vector((x,y,z))
 # Varón esbelto: pecho y clavículas algo más anchos; pelvis más estrecha.
 factor=interpolate(z,[(.86,.94),(.94,.92),(1.00,1.00),(1.07,1.10),(1.15,1.10),(1.23,1.14),(1.30,1.16),(1.36,1.15),(1.415,1.13),(1.445,1.18),(1.48,1.15),(1.53,1.10),(1.60,1.05),(1.75,1.04)])
 arm=smooth(.205,.30,abs(x))*smooth(.73,.86,z)*(1-smooth(1.43,1.49,z))
 arm_cx=sign*interpolate(z,[(.78,.410),(.905,.382),(.94,.372),(1.035,.337),(1.115,.312),(1.145,.30),(1.19,.285),(1.30,.25),(1.365,.222)])
 muscle=1+.12*gaussian(z,1.27,.12)+.07*gaussian(z,1.045,.07)
 arm_x=arm_cx+sign*.025+(x-arm_cx)*muscle
 x=x*factor*(1-arm)+arm_x*arm
 depth=1+.15*gaussian(z,1.28,.16)+.05*gaussian(z,1.08,.10)
 y=y*(depth*(1-arm)+muscle*arm)
 y-=.008*gaussian(z,1.29,.07)*gaussian(abs(point[0]),.09,.07)*front*torso
 y+=.005*gaussian(z,1.09,.10)*front*torso
 if z<.85:
  cx=sign*interpolate(z,[(.15,.158),(.34,.145),(.465,.137),(.67,.115),(.78,.103),(.875,.10)])
  strength=1+.07*gaussian(z,.68,.11)+.045*gaussian(z,.32,.10)
  leg_x=cx*1.02+(point[0]-cx)*strength
  blend=1-smooth(.77,.85,z);x=x*(1-blend)+leg_x*blend
  y=point[1]*(1+.07*gaussian(z,.68,.11)+.04*gaussian(z,.32,.10))
 return Vector((x*1.015,y*1.015,z*1.045))

roots={};bodies={};rigs={};reports={}
for gender,offset in [('Female',-.65),('Male',.65)]:
 root=bpy.data.objects.new(gender+'Base_Root',None);scene.collection.objects.link(root);root.location.x=offset;roots[gender]=root
 rig=source_rig.copy();rig.data=source_rig.data.copy();rig.name=gender+'Base_DiagnosticRig';scene.collection.objects.link(rig);rig.parent=root;rig.animation_data_clear();rigs[gender]=rig
 body=source.copy();body.data=source.data.copy();body.name=gender+'Base_Refined';scene.collection.objects.link(body);body.parent=root;body.animation_data_clear();bodies[gender]=body
 for v in body.data.vertices:v.co=warp(v.co,gender)
 for m in body.modifiers:
  if m.type=='ARMATURE':m.object=rig
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for bone in rig.data.edit_bones:
  bone.head=warp(bone.head.copy(),gender);bone.tail=warp(bone.tail.copy(),gender)
 bpy.ops.object.mode_set(mode='OBJECT')
 for bone in rig.pose.bones:
  bone.rotation_mode='XYZ';bone.rotation_euler=(0,0,0);bone.location=(0,0,0);bone.scale=(1,1,1);bone.keyframe_insert('rotation_euler',frame=1)
 rig.pose.bones['Forearm.R'].rotation_euler.x=math.radians(85)
 rig.pose.bones['Thigh.L'].rotation_euler.x=math.radians(-30)
 rig.pose.bones['Shin.L'].rotation_euler.x=math.radians(65)
 for bone in rig.pose.bones:bone.keyframe_insert('rotation_euler',frame=30)
 for bone in rig.pose.bones:bone.rotation_euler=(0,0,0);bone.keyframe_insert('rotation_euler',frame=60)
 if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name=gender+'_Diagnostic_JointTest'
 body['Status']='Body shape revision requested by Alain. Clothing and final rig pending.'
 rig['Status']='Diagnostic armature; not final Mixamo/Humanoid rig.'
 bm=bmesh.new();bm.from_mesh(body.data)
 reports[gender]={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'bones':len(rig.data.bones),'unweighted_vertices':sum(not v.groups for v in body.data.vertices),'weight_error':max(abs(sum(g.weight for g in v.groups)-1) for v in body.data.vertices)};bm.free()
 for z,label in [(1.07,'waist'),(.94,'hips'),(1.30,'chest')]:
  section=[warp(v.co,gender) for v in source.data.vertices if abs(v.co.z-z)<1e-5 and abs(v.co.x)<.205]
  reports[gender][label+'_cage_width_m']=max(p.x for p in section)-min(p.x for p in section)

camera_data=bpy.data.cameras.new('BodyBases_Camera');camera=bpy.data.objects.new('BodyBases_Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
shade=scene.display.shading;shade.color_type='MATERIAL';shade.light='STUDIO';shade.show_specular_highlight=False;shade.show_cavity=False
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.shading.show_specular_highlight=False;area.spaces.active.shading.show_cavity=False;area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_perspective='CAMERA'
def capture(gender,view,frame=1):
 scene.frame_set(frame);bpy.context.view_layer.update()
 for key,body in bodies.items():body.hide_set(gender!='Both' and key!=gender)
 for rig in rigs.values():rig.hide_set(False)
 center=Vector((0 if gender=='Both' else roots[gender].location.x,0,.90))
 direction={'Front':(0,-5,.03),'Side':(-5,0,.03),'Back':(0,5,.03),'Quarter':(3,-6,1)}[view]
 camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 camera_data.ortho_scale=3.2 if gender=='Both' else 2.1
 scene.render.resolution_x=1500 if gender=='Both' else 800;scene.render.resolution_y=1050
 scene.render.filepath=str(OUT/(gender+'-'+view+('-Pose' if frame==30 else '')+'.png'))
 area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
 with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=False)
def sample(body,frame):
 scene.frame_set(frame);bpy.context.view_layer.update()
 obj=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=obj.to_mesh();values=[v.co.copy() for v in mesh.vertices];obj.to_mesh_clear();return values
for gender,body in bodies.items():
 a=sample(body,1);b=sample(body,30);c=sample(body,60)
 reports[gender]['moved_vertices_pose']=sum((p-q).length>1e-5 for p,q in zip(a,b))
 reports[gender]['reset_error']=max((p-q).length for p,q in zip(a,c))
 reports[gender]['finite_positions']=all(math.isfinite(f) for values in (a,b,c) for v in values for f in v)
 capture(gender,'Front');capture(gender,'Side');capture(gender,'Back');capture(gender,'Quarter',30)
capture('Both','Front')
for body in bodies.values():body.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');bodies['Female'].select_set(True);bpy.context.view_layer.objects.active=bodies['Female']
(OUT/'Validacion.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
path=ART/'BlenderSources~/BodyBases_Refined.blend';bpy.data.libraries.write(str(path),{scene},fake_user=True)
print('BODY_BASES_REFINED',json.dumps(reports))
