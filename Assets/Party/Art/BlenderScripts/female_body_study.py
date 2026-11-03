"""Una base femenina de estudio con topología conectada. No es el personaje final."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
ART=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
OUT=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Estudio-Cuerpo-Femenino');OUT.mkdir(exist_ok=True)
if 'FemaleBody_AnatomyStudy' in bpy.data.scenes:raise RuntimeError('El estudio ya existe; no sobrescribir')
scene=bpy.data.scenes.new('FemaleBody_AnatomyStudy');bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
verts=[];faces=[];finger_bones=[]
def vertex(p):verts.append(tuple(p));return len(verts)-1
def loop(points):return [vertex(p) for p in points]
def bridge(a,b):
 n=len(a);m=len(b);i=j=0
 while i<n or j<m:
  t1=(i+1)/n if i<n else 2;t2=(j+1)/m if j<m else 2
  if abs(t1-t2)<1e-6:
   faces.append((a[i%n],a[(i+1)%n],b[(j+1)%m],b[j%m]));i+=1;j+=1
  elif t1<t2:faces.append((a[i%n],a[(i+1)%n],b[j%m]));i+=1
  else:faces.append((a[i%n],b[(j+1)%m],b[j%m]));j+=1
def align(a,b):
 ca=sum((Vector(verts[i]) for i in a),Vector())/len(a);cb=sum((Vector(verts[i]) for i in b),Vector())/len(b)
 choices=[]
 for order in [b,list(reversed(b))]:
  for shift in range(len(b)):
   candidate=order[shift:]+order[:shift]
   score=sum(((Vector(verts[a[i]])-ca)-(Vector(verts[candidate[int(i*len(b)/len(a))]])-cb)).length_squared for i in range(len(a)))
   choices.append((score,candidate))
 return min(choices,key=lambda v:v[0])[1]
def ring_z(x,y,z,rx,ry,n,phase=0):return loop([(x+rx*cos(phase+2*pi*i/n),y+ry*sin(phase+2*pi*i/n),z) for i in range(n)])
def section(center,direction,radius,depth,n=8):
 d=Vector(direction).normalized();u=d.cross(Vector((0,1,0))).normalized();v=d.cross(u).normalized()
 return loop([Vector(center)+u*cos(2*pi*i/n)*radius+v*sin(2*pi*i/n)*depth for i in range(n)])

# Las dos piernas comparten el arco de la entrepierna; no son tubos superpuestos.
leg_top={}
for side in [-1,1]:
 rings=[]
 for z,x,y,rx,ry in [(.02,.17,-.075,.050,.125),(.045,.17,-.075,.054,.133),(.075,.165,-.045,.047,.095),(.115,.16,-.005,.035,.045),(.15,.158,0,.034,.039),(.24,.15,.006,.046,.051),(.34,.145,.005,.061,.064),(.43,.139,-.012,.057,.056),(.465,.137,-.020,.052,.053),(.495,.135,-.017,.055,.056),(.55,.127,-.003,.068,.070),(.67,.115,.008,.084,.086),(.78,.103,.006,.095,.096)]:
  rings.append(ring_z(side*x,y,z,rx,ry,8))
 for a,b in zip(rings,rings[1:]):bridge(a,b)
 faces.append(tuple(reversed(rings[0])))
 top=ring_z(side*.10,0,.875,.10,.10,8)
 inner=[3,4,5] if side==1 else [1,0,7]
 for j,index in enumerate(inner):verts[top[index]]=(0,(1-j)*.070,.875 if j!=1 else .81)
 bridge(rings[-1],top);leg_top[side]=top

# Soldar exclusivamente la costura central de las dos piernas.
remap={leg_top[-1][left]:leg_top[1][right] for left,right in [(1,3),(0,4),(7,5)]}
faces=[tuple(remap.get(v,v) for v in face) for face in faces]
bottom=[leg_top[1][i] for i in [5,6,7,0,1,2,3]]+[leg_top[-1][i] for i in [2,3,4,5,6]]
torso=[]
for z,rx,ry,y in [(.94,.19,.13,.01),(1.00,.171,.119,.005),(1.07,.139,.103,0),(1.15,.148,.105,0),(1.23,.172,.110,-.005),(1.30,.190,.112,-.007),(1.36,.197,.099,0),(1.415,.175,.081,.008),(1.445,.060,.052,0),(1.475,.052,.050,0)]:
 torso.append(ring_z(0,y,z,rx,ry,12,-pi/2))
bridge(bottom,torso[0])
for j,(a,b) in enumerate(zip(torso,torso[1:])):
 for i in range(12):
  if j in (5,6) and i in (2,3,8,9):continue
  faces.append((a[i],a[(i+1)%12],b[(i+1)%12],b[i]))

# Cabeza y cuello forman parte de la misma superficie. El rostro detallado queda fuera de este estudio.
previous=torso[-1]
for z,rx,ry,y in [(1.493,.046,.048,-.004),(1.51,.054,.055,-.01),(1.535,.070,.063,-.005),(1.57,.086,.071,0),(1.61,.092,.078,.004),(1.65,.091,.080,.006),(1.69,.081,.075,.008),(1.72,.055,.055,.01),(1.735,.020,.025,.01)]:
 current=ring_z(0,y,z,rx,ry,12,-pi/2)
 for idx in current:
  x,yy,zz=verts[idx]
  if yy<-.025:verts[idx]=(x,yy-.020*math.exp(-(x/.025)**2-((zz-1.58)/.035)**2),zz)
 bridge(previous,current);previous=current
faces.append(tuple(previous))

# Hombros conectados mediante aberturas de ocho vértices y muñecas con transición a la palma.
for side in [-1,1]:
 l,r=(2,4) if side==1 else (10,8)
 hole=[torso[5][l],torso[5][3 if side==1 else 9],torso[5][r],torso[6][r],torso[7][r],torso[7][3 if side==1 else 9],torso[7][l],torso[6][l]]
 points=[(side*.222,0,1.365),(side*.25,-.003,1.30),(side*.285,-.008,1.19),(side*.30,-.012,1.145),(side*.312,-.014,1.115),(side*.337,-.018,1.035),(side*.372,-.025,.94),(side*.382,-.029,.905)]
 radii=[(.065,.064),(.061,.061),(.048,.050),(.044,.045),(.043,.043),(.047,.046),(.034,.033),(.027,.026)]
 previous=hole
 for j,p in enumerate(points):
  d=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
  current=section(p,d,*radii[j]);current=align(previous,current);bridge(previous,current);previous=current
 wrist=Vector(points[-1]);d=(wrist-Vector(points[-2])).normalized();w=Vector((abs(d.z),0,side*abs(d.x))).normalized();dep=Vector((0,1,0))
 palm=[]
 for dist,width,depth in [(.006,.031,.020),(.042,.038,.022),(.078,.034,.017)]:
  center=wrist+d*dist
  coords=[center+w*width*(-1+j*.5)-dep*depth for j in range(5)]+[center+w*width*(1-j*.5)+dep*depth for j in range(5)]
  palm.append(loop(coords))
 bridge(previous,align(previous,palm[0]))
 thumb_edge=9 if side==1 else 4
 for k in range(2):
  a,b=palm[k],palm[k+1]
  for i in range(10):
   if k==0 and i==thumb_edge:continue
   faces.append((a[i],a[(i+1)%10],b[(i+1)%10],b[i]))
 hand=palm[-1]
 for finger in range(4):
  a=[hand[finger],hand[finger+1],hand[8-finger],hand[9-finger]]
  center=sum((Vector(verts[i]) for i in a),Vector())/4
  length=[.050,.064,.061,.044][finger];previous=a
  end=center+d*length+w*(finger-1.5)*.006
  finger_bones.append((f'Finger{finger+1}.{"R" if side==1 else "L"}',center,end))
  for fraction,scale in [(.34,.85),(.7,.70),(1,.42)]:
   point=center.lerp(end,fraction)
   current=loop([point+(Vector(verts[i])-center)*scale for i in a]);bridge(previous,current);previous=current
  faces.append(tuple(previous))
 a=[palm[0][thumb_edge],palm[0][(thumb_edge+1)%10],palm[1][(thumb_edge+1)%10],palm[1][thumb_edge]]
 center=sum((Vector(verts[i]) for i in a),Vector())/4
 end=center-w*side*.047+d*.044-dep*.006;previous=a
 finger_bones.append((f'Thumb.{"R" if side==1 else "L"}',center,end))
 for f,scale in [(.45,.65),(.8,.48),(1,.33)]:
  current=loop([center.lerp(end,f)+(Vector(verts[i])-center)*scale for i in a]);bridge(previous,current);previous=current
 faces.append(tuple(previous))

data=bpy.data.meshes.new('FemaleBody_ConnectedCage');data.from_pydata(verts,[],faces);data.update()
bm=bmesh.new();bm.from_mesh(data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
body=bpy.data.objects.new('FemaleBody_Study',data);scene.collection.objects.link(body)
for p in data.polygons:p.use_smooth=True
mat=bpy.data.materials.new('AnatomyStudy_Neutral');mat.diffuse_color=(.30,.43,.47,1);mat.use_nodes=True
node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(.30,.43,.47,1);node.inputs['Roughness'].default_value=.9;data.materials.append(mat)

# Esqueleto de diagnóstico: permite ensayar articulaciones. No sustituye el rig Humanoid final de Mixamo.
arm=bpy.data.armatures.new('FemaleStudy_Joints');rig=bpy.data.objects.new('FemaleStudy_DiagnosticRig',arm);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
specs=[('Hips',(0,0,.89),(0,0,1.01),None),('Spine',(0,0,1.01),(0,0,1.22),'Hips'),('Chest',(0,0,1.22),(0,0,1.405),'Spine'),('Neck',(0,0,1.405),(0,0,1.49),'Chest'),('Head',(0,0,1.49),(0,0,1.72),'Neck')]
for s,side in [('L',-1),('R',1)]:
 specs += [(f'Clavicle.{s}',(0,0,1.38),(side*.205,0,1.38),'Chest'),(f'UpperArm.{s}',(side*.205,0,1.38),(side*.30,-.012,1.145),f'Clavicle.{s}'),(f'Forearm.{s}',(side*.30,-.012,1.145),(side*.382,-.029,.905),f'UpperArm.{s}'),(f'Hand.{s}',(side*.382,-.029,.905),(side*.410,-.032,.835),f'Forearm.{s}'),(f'Thigh.{s}',(side*.10,0,.89),(side*.137,-.02,.465),'Hips'),(f'Shin.{s}',(side*.137,-.02,.465),(side*.158,0,.14),f'Thigh.{s}'),(f'Foot.{s}',(side*.158,0,.14),(side*.17,-.17,.045),f'Shin.{s}')]
for name,head,tail in finger_bones:specs.append((name,head,tail,'Hand.'+name.split('.')[-1]))
for name,head,tail,parent in specs:
 b=arm.edit_bones.new(name);b.head=head;b.tail=tail
 if parent:b.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
# Pesos deterministas por segmentos y regiones anatómicas, con hasta cuatro influencias normalizadas.
groups={name:body.vertex_groups.new(name=name) for name,_,_,_ in specs}
segments={name:(Vector(h),Vector(t)) for name,h,t,_ in specs}
def distance(p,a,b):
 d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-(a+d*t)).length
for v in data.vertices:
 p=v.co;x,y,z=p
 if abs(x)>.22 and z>.70:allowed=[n for n in groups if n.endswith('.'+('R' if x>0 else 'L')) and not n.startswith(('Thigh','Shin','Foot'))]+['Chest']
 elif z<.89:allowed=[n for n in groups if n.endswith('.'+('R' if x>0 else 'L')) and n.startswith(('Thigh','Shin','Foot'))]+['Hips']
 else:allowed=['Hips','Spine','Chest','Neck','Head']+[n for n in groups if n.startswith('Clavicle')]
 nearest=sorted([(distance(p,*segments[n]),n) for n in allowed])[:4]
 weights=[math.exp(-(d-nearest[0][0])/.025) for d,n in nearest];total=sum(weights)
 for (_,name),weight in zip(nearest,weights):groups[name].add([v.index],weight/total,'REPLACE')
mod=body.modifiers.new('Diagnostic deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
sub=body.modifiers.new('Study surface','SUBSURF');sub.levels=2;sub.render_levels=2
body['Status']='ANATOMY STUDY ONLY; not the completed reference character'
rig['Status']='Diagnostic joints only; final Mixamo rig and Humanoid pending'

camera_data=bpy.data.cameras.new('StudyCamera');camera=bpy.data.objects.new('StudyCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=1.98
scene.render.resolution_x=800;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
shade=scene.display.shading;shade.color_type='MATERIAL';shade.light='STUDIO';shade.show_specular_highlight=False;shade.show_cavity=False
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.shading.show_specular_highlight=False;area.spaces.active.shading.show_cavity=False;area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_perspective='CAMERA'
def capture(label,direction):
 center=Vector((0,0,.875));camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(OUT/(label+'.png'))
 area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
 with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=False)
bm=bmesh.new();bm.from_mesh(data)
report={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'bones':len(arm.bones),'unweighted_vertices':sum(not v.groups for v in data.vertices),'weight_sum_max_error':max(abs(sum(g.weight for g in v.groups)-1) for v in data.vertices)};bm.free()
(OUT/'Geometry-and-weights.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
capture('Base-front',(0,-5,.05));capture('Base-side',(-5,0,.05))
path=ART/'BlenderSources~/FemaleBody_AnatomyStudy.blend';bpy.data.libraries.write(str(path),{scene},fake_user=True)
print('ANATOMY_STUDY_SAVED',json.dumps(report))
