"""Apariencia humana original sobre la base aprobada. Materiales y geometría propios."""
import bpy,bmesh,math,random,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
from math import sin,cos,pi
ART=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
OUT=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Apariencia-Mujer');OUT.mkdir(exist_ok=True)
SCENE='FemaleAppearance_Study'
ROOT=None
def rgb(value):
 c=[int(value[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)
def material(name,color,rough=.65,detail=False):
 key='AF_'+name;m=bpy.data.materials.get(key)
 if m:return m
 m=bpy.data.materials.new(key);m.use_nodes=True;m.diffuse_color=(*rgb(color),1)
 shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 shader.inputs['Base Color'].default_value=(*rgb(color),1);shader.inputs['Roughness'].default_value=rough
 if detail:
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=650
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.00015
  m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],shader.inputs['Normal'])
 if name=='Skin':
  shader.inputs['Subsurface Weight'].default_value=.06;shader.inputs['Subsurface Scale'].default_value=.012
 return m
def mesh(name,verts,faces,mat,parent=None):
 data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
 obj=bpy.data.objects.new('AF_'+name,data);bpy.context.scene.collection.objects.link(obj);obj.parent=parent or ROOT;data.materials.append(mat)
 for face in data.polygons:face.use_smooth=True
 return obj
def ell(name,center,radii,mat,segments=32,rings=18):
 verts=[Vector(center)+Vector((0,0,-radii[2]))]
 for j in range(1,rings):
  v=-pi/2+pi*j/rings
  for i in range(segments):
   a=2*pi*i/segments;verts.append(Vector(center)+Vector((radii[0]*cos(a)*cos(v),radii[1]*sin(a)*cos(v),radii[2]*sin(v))))
 verts.append(Vector(center)+Vector((0,0,radii[2])));top=len(verts)-1
 faces=[(0,1+(i+1)%segments,1+i) for i in range(segments)]
 for j in range(rings-2):
  for i in range(segments):faces.append((1+j*segments+i,1+j*segments+(i+1)%segments,1+(j+1)*segments+(i+1)%segments,1+(j+1)*segments+i))
 faces.extend((top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments) for i in range(segments))
 return mesh(name,verts,faces,mat)
def curve(name,points,radius,mat):
 data=bpy.data.curves.new('AF_'+name,'CURVE');data.dimensions='3D';data.resolution_u=3;data.bevel_depth=radius;data.bevel_resolution=2
 spline=data.splines.new('POLY');spline.points.add(len(points)-1)
 for p,co in zip(spline.points,points):p.co=(*co,1)
 obj=bpy.data.objects.new('AF_'+name,data);bpy.context.scene.collection.objects.link(obj);obj.parent=ROOT;data.materials.append(mat);return obj
def surface(obj):return BVHTree.FromPolygons([v.co.copy() for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])
def front_y(bvh,x,z,offset=0):
 hit,normal,_,_=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
 return hit.y-offset if hit else -.075-offset
def head_parent(obj):
 # Parenting rígido a Head con transformación local preservada.
 rig=bpy.data.objects['AF_DiagnosticRig'];matrix=obj.matrix_world.copy()
 obj.parent=rig;obj.parent_type='BONE';obj.parent_bone='Head';obj.matrix_world=matrix
def create_base():
 global ROOT
 if bpy.data.scenes.get(SCENE):raise RuntimeError('La apariencia ya existe; revisar antes de regenerar')
 source=bpy.data.objects['FemaleBase_Refined'];bpy.context.window.scene=bpy.data.scenes['BodyBases_Refined'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get();evaluated=source.evaluated_get(deps)
 data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
 scene=bpy.data.scenes.new(SCENE);bpy.context.window.scene=scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 ROOT=bpy.data.objects.new('AF_CharacterRoot',None);scene.collection.objects.link(ROOT)
 rig=bpy.data.objects['FemaleBase_DiagnosticRig'].copy();rig.data=rig.data.copy();rig.name='AF_DiagnosticRig';scene.collection.objects.link(rig);rig.parent=ROOT
 rig.animation_data_clear()
 for bone in rig.pose.bones:bone.rotation_euler=(0,0,0)
 body=source.copy();body.data=data;body.name='AF_Body';body.parent=ROOT;scene.collection.objects.link(body);body.animation_data_clear()
 for mod in list(body.modifiers):body.modifiers.remove(mod)
 if all(v.groups for v in data.vertices):
  mod=body.modifiers.new('Diagnostic skin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
 body.data.materials.clear();body.data.materials.append(material('Skin','85523C',.59,True))
 for p in data.polygons:p.use_smooth=True
 body['Source']='Approved FemaleBase_Refined with ChestVolume_Slight baked at rest'
 body['Status']='Appearance work in progress; not GTA asset or final game rig'
 return body
def create_face():
 body=bpy.data.objects['AF_Body'];skin=material('Skin','A57051');lip=material('Lips','885340',.55)
 for v in body.data.vertices:
  x,y,z=v.co
  if z<1.50 or y>-.025:continue
  front=max(0,min(1,-y/.065))
  def g(xc,zc,sx,sz):return math.exp(-((x-xc)/sx)**2-((z-zc)/sz)**2)
  delta=-.010*g(0,1.615,.008,.032)-.020*g(0,1.591,.011,.011)
  delta-=.006*(g(.010,1.583,.006,.006)+g(-.010,1.583,.006,.006))
  delta+=.003*(g(.0315,1.635,.014,.010)+g(-.0315,1.635,.014,.010))
  delta-=.003*(g(.0315,1.650,.023,.006)+g(-.0315,1.650,.023,.006))
  delta-=.0035*(g(.047,1.603,.020,.016)+g(-.047,1.603,.020,.016))
  delta-=.003*g(0,1.553,.022,.007)+.003*g(0,1.522,.023,.012)
  v.co.y+=delta*front
 body.data.update();bvh=surface(body)
 eye_mat=material('Sclera','D9D4C5',.26);iris_mat=material('Iris','533B27',.35);pupil=material('Pupil','131511',.18);hair=material('Hair','281F1B',.72)
 shadow=material('Crease','533626',.8)
 objects=[]
 for side in [-1,1]:
  x=side*.0315;z=1.635;cy=-.0615;r=.013
  # Solo la superficie visible de la esclerótica; el resto queda cubierto por el párpado.
  verts=[(x,cy-r,z)]
  for i in range(48):
   a=2*pi*i/48;dx=.014*cos(a);dz=.0045*sin(a)
   verts.append((x+dx,cy-math.sqrt(max(.000001,r*r-dx*dx-dz*dz)),z+dz))
  objects.append(mesh('ScleraAperture',verts,[(0,1+i,1+(i+1)%48) for i in range(48)],eye_mat))
  for label,radius,mat,offset in [('Iris',.0058,iris_mat,.00015),('Pupil',.0023,pupil,.00030)]:
   verts=[(x,cy-r-offset,z)]
   for i in range(48):
    a=2*pi*i/48;dx=radius*cos(a);opening=.0044*math.sqrt(max(0,1-(dx/.014)**2));dz=max(-opening,min(opening,radius*sin(a)));verts.append((x+dx,cy-math.sqrt(r*r-dx*dx-dz*dz)-offset,z+dz))
   objects.append(mesh(label,verts,[(0,1+i,1+(i+1)%48) for i in range(48)],mat))
  # Superficie anular del párpado: abertura estrecha que cubre el globo ocular.
  verts=[];count=48;steps=5
  for j in range(steps):
   t=j/(steps-1)
   for i in range(count):
    a=2*pi*i/count;dx=(.0128*(1-t)+.018*t)*cos(a);dz=(.0048*(1-t)+.009*t)*sin(a)+side*dx*.05
    inner_y=cy-math.sqrt(max(.000001,r*r-(.0128*cos(a))**2-(.0048*sin(a))**2))-.0003
    outer_y=front_y(bvh,x+dx,z+dz,.0002)
    verts.append((x+dx,inner_y*(1-t)+outer_y*t,z+dz))
  faces=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(steps-1) for i in range(count)]
  # El reborde fino se integra visualmente en la superficie de la cara, sin un parche anular superpuesto.
  rim=[]
  for i in range(count+1):
   a=2*pi*i/count;dx=.0142*cos(a);dz=.0048*sin(a)
   y=cy-math.sqrt(max(.000001,r*r-dx*dx-dz*dz))-.0002
   rim.append((x+dx,y,z+dz))
  objects.append(curve('LidEdge',rim,.0006,skin))
  highlight=material('EyeHighlight','E3DCCE',.15)
  objects.append(ell('EyeHighlight',(x-.002,cy-r-.0005,z+.0022),(.0006,.00025,.0006),highlight,16,8))
  brow=[]
  for i in range(14):
   xx=side*(.014+i*.038/13);zz=1.651+.004*sin(pi*i/13)-.001*i/13
   brow.append((xx,front_y(bvh,xx,zz,.0009),zz))
  objects.append(curve('Eyebrow',brow,.0012,hair))
  for i in range(24):
   t=i/23;xx=side*(.014+t*.038);zz=1.651+.004*sin(pi*t)-.001*t;y=front_y(bvh,xx,zz,.001)
   objects.append(curve('BrowHair',[(xx,y,zz-.001),(xx+side*.001,y-.0003,zz+.0015)],.00011,hair))
  # Oreja: volumen y hélix discreta, sin aros o piezas grandes superpuestas.
  ear=ell('Ear',(side*.082,.004,1.607),(.012,.013,.025),skin,24,16);objects.append(ear)
  points=[(side*(.088+.003*sin(2*pi*i/40)),.004+.009*cos(2*pi*i/40),1.608+.019*sin(2*pi*i/40)) for i in range(41)]
  objects.append(curve('EarHelix',points,.0016,skin))
  nx=side*.010;nz=1.581;ny=front_y(bvh,nx,nz,.0005)
  objects.append(ell('Nostril',(nx,ny+.0005,nz),(.002,.0006,.0008),shadow,20,10))
 # Labios cerrados con perfil continuo y volumen moderado.
 for upper in (True,False):
  verts=[]
  for j in range(4):
   t=j/3
   for i in range(33):
    x=-.022+i*.044/32;s=sin(pi*i/32);seam=1.5525+.0008*abs(x/.022)
    edge=seam+(.0065*s*(1-.28*math.exp(-(x/.004)**2)) if upper else -.006*s)
    z=seam*(1-t)+edge*t;y=front_y(bvh,x,z,.0007+.0018*s*sin(pi*t))
    verts.append((x,y,z))
  faces=[(j*33+i,j*33+i+1,(j+1)*33+i+1,(j+1)*33+i) for j in range(3) for i in range(32)]
  objects.append(mesh('UpperLip' if upper else 'LowerLip',verts,faces,lip))
 crease=[(x,front_y(bvh,x,1.5525+.0008*abs(x/.022),.0011),1.5525+.0008*abs(x/.022)) for x in [-.021+i*.042/32 for i in range(33)]]
 objects.append(curve('MouthLine',crease,.00035,shadow))
 bpy.context.view_layer.update()
 for obj in objects:head_parent(obj)
def studio():
 scene=bpy.data.scenes[SCENE]
 world=bpy.data.worlds.new('AF_StudioWorld');world.use_nodes=True
 n=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');n.inputs['Color'].default_value=(.25,.25,.25,1);n.inputs['Strength'].default_value=.3;scene.world=world
 transforms=[i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items]
 if 'AgX' in transforms:scene.view_settings.view_transform='AgX'
 for name,pos,energy,size in [('Key',(1.3,-2,2.7),150,1.7),('Fill',(-1.8,-1,2.2),100,2),('Rim',(0,1.2,2.5),200,1.5)]:
  data=bpy.data.lights.new('AF_'+name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
  obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector((0,0,1.4))-obj.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('AF_Camera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera;data.type='ORTHO'
def render(label,portrait=True,direction=(1,-4,.2)):
 scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene;scene.frame_set(1)
 center=Vector((0,0,1.60 if portrait else .89));scene.camera.location=center+Vector(direction);scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=.40 if portrait else 2.10
 scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/(label+'.png'))
 bpy.ops.render.render(write_still=True)
def save():
 path=ART/'BlenderSources~/FemaleAppearance_Study.blend';bpy.data.libraries.write(str(path),{bpy.data.scenes[SCENE]},fake_user=True);print('APPEARANCE_SAVED',str(path))
