"""Blender 4.x: revisión R1 de proporciones, referencias, rig y FBX.

Uso: blender -b -P build_character.py
Opcional: blender -b -P build_character.py -- --auto-fit --fit-iterations 4
Por defecto conserva las proporciones corregidas manualmente.
No borra escenas del usuario. Las rutas se resuelven junto a este archivo.
"""
import bpy,bmesh,math,json,sys,argparse,statistics
from pathlib import Path
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi

# ---------------------------------------------------------------------------
# 1. MEDIDAS EDITABLES. Metros, X lateral, -Y frente, Z arriba.
# ---------------------------------------------------------------------------
HEIGHT=1.65
HEADS_TALL=6.5
SHOULDER_HALF=.154
BODY_DEPTH=.150
WAIST_DEPTH=.090
HIP_DEPTH=.100
WAIST_RADIUS=.123
HIP_RADIUS=.165
HIP_Z=.900
WAIST_Z=1.015
CHEST_Z=1.245
NECK_Z=1.325
HEAD_CENTER_Z=1.455
HEAD_WIDTH=.2153
HEAD_DEPTH=.250
CHIN_HEIGHT_FACTOR=.22
NECK_CAGE_CUT_Z=1.315
HEAD_PROFILE_REFERENCE_CENTER=1.455
HEAD_PROFILE_REFERENCE_HEIGHT=1.65/6.5
# Z, semiancho/cabeza, profundidad frontal/cabeza, trasera/cabeza, centro Y.
# Se conserva el torso Skin y se reemplaza solamente su extremo de cabeza.
HEAD_RING_PROFILE=[
 (1.345,.31,.29,.29,.006),
 (1.370,.31,.30,.29,.004),
 (1.400,.36,.72,.31,-.012),
 (1.422,.66,.82,.54,-.009),
 (1.448,.89,.90,.85,-.003),
 (1.480,.94,.94,.96,.000),
 (1.510,.88,.91,.97,.004),
 (1.540,.73,.80,.85,.005),
 (1.565,.48,.55,.59,.005),
 (1.582,.21,.25,.27,.005)]
HEAD_TOP_Z=1.588
FACE_PLANE_EXPONENT=.65
HEAD_HEIGHT=HEIGHT/HEADS_TALL
ARM_ANGLE_DEG=61.0             # Descenso desde horizontal, calzado con la lámina.
UPPER_ARM_LENGTH=.235
LOWER_ARM_LENGTH=.215
UPPER_ARM_RADIUS=.051
WRIST_RADIUS=.025
HAND_LENGTH=.080
KNEE_Z=.425
ANKLE_Z=.105
LEG_SPREAD=.155
THIGH_RADIUS=.092
KNEE_RADIUS=.055
ANKLE_RADIUS=.032
JACKET_HEM_Z=1.050
JACKET_OFFSET=.018
JACKET_OPEN_HALF=.060
CUFF_ARM_FRACTION=.71
CUFF_WIDTH=.055
CUFF_OVERLAP=.012
TOP_HEM_Z=1.070
PANTS_WAIST_Z=1.035
PANTS_HIP_RADIUS=.166
PANTS_LEG_RADIUS=.123
PANTS_DEPTH=.123
PANTS_HEM_FLARE_X=1.12
PANTS_HEM_FLARE_Y=1.20
PANTS_HEM_Z=.075
PANTS_CROTCH_DROP=.055
SHOE_LENGTH=.255
SHOE_WIDTH=.125
SOLE_HEIGHT=.035
SHOE_HEIGHT=.133
BUN_RADIUS=.075
BUN_CENTER_Z=1.615
HAIR_CAP_EXTRA=.005
EARRING_RADIUS=.0065
SUBDIVISION_LEVEL=2
MAX_FIT_ITERATIONS=4
MAX_WIDTH_UPDATE=.08          # Límite por iteración; evita cambios bruscos.
REASONABLE_MEAN_ERROR=.18     # Tolerancia de blockout, no de escultura final.
REASONABLE_IOU=.60
REASONABLE_MAX_WIDTH_ERROR=.25 # Evita aceptar una media que oculte un perfil malo.
REFERENCE_CHROMA_THRESHOLD=.055
REFERENCE_DARK_THRESHOLD=.20
RENDER_ALPHA_THRESHOLD=.35
NECK_MEASUREMENT_FRACTION=.82 # Cuello desnudo en la hoja; .80 corta el cuello de la chaqueta.
DETAILS={                    # Medidas de detalles secundarios, también en metros.
 'cloth_thickness':.002,'cuff_extra_offset':.005,'pocket_half_width':.032,
 'panel_offset':.003,'top_offset':.005,'seam_radius':.00065,
 'seam_surface_offset':.0004,'curl_radius':.0022,'hoop_wire_radius':.0012,
 'neck_radius_x':.035,'neck_radius_y':.037,'pelvis_radius_factor':.135/.165,
 'rib_radius_x':.150,'elbow_radius_x':.041,'elbow_radius_y':.038,
 'forearm_radius_x':.045,'forearm_radius_y':.038,'palm_radius_x':.032,
 'palm_radius_y':.025,'calf_radius_x':.055,'calf_radius_y':.052}
# Guías secundarias: coordenadas y perfiles en metros; los factores de forma
# que aparecen después en las funciones son proporciones sin unidades.
BODY_GUIDES={
 'rib_drop':.10,'shoulder_drop':.005,'chin_y':-.005,'head_y':-.004,
 'chin_radius':.054,'crown_tip_radius':.030,'hip_x':.09,'hip_drop':.045,
 'hip_depth':.095,'thigh_x':.105,'thigh_drop':.19,'thigh_depth':.085,
 'knee_x':.130,'knee_y':-.012,'calf_x':.14,'calf_y':.008,
 'ankle_depth':.035,'foot_y':-.080,'foot_z':.045,'foot_width':.046,
 'foot_depth':.060,'toe_y':-.155,'toe_z':.042,'toe_width':.038,'toe_depth':.043,
 'neck_bone_extra':.040,'foot_bone_y':-.10,'toe_bone_y':-.19}
JACKET_GUIDES={'neck_margin':.025,'sleeve_min_z':.925,'panel_depth':.004,
               'pocket_x':.105,'pocket_drop':.075}
CHEST_POCKET_OUTLINE=[(-.032,0,.034),(.032,0,.034),(.032,0,-.026),(0,0,-.034),(-.032,0,-.026)]
FLAP_OUTLINE=[(-.035,-.003,.037),(.035,-.003,.037),(.029,-.005,.017),(0,-.005,.011),(-.029,-.005,.017)]
COLLAR_OUTLINE=[(.043,-.046,.022),(.105,-.080,-.030),(.072,-.120,-.070),(.025,-.068,-.005)]
PANTS_GUIDES={'lower_support_z':.18,'lower_x_offset':.005,'thigh_x':.11,
 'thigh_drop':.20,'minimum_gap':.010,'saddle_x':.10,'saddle_drop':.045,
 'hip_raise':.025,'hip_depth_multiplier':.98,'waist_support_drop':.015,'waist_extra_x':.015,
 'waist_extra_y':.014,'waist_rim_extra_x':.014,'waist_rim_extra_y':.013,
 'back_pocket_x':.090,'back_pocket_raise':.050}
BACK_POCKET_OUTLINE=[(-.032,0,.030),(.032,0,.030),(.030,0,-.027),(0,0,-.035),(-.030,0,-.027)]
SHOE_PROFILE={'center_y':-.070,'bevel_z':.008,'upper_mid_y':-.065,'upper_mid_z':.075,
              'collar_y':-.018,'collar_base_z':.115}
HAIR_GUIDES={'cap_y':.008,'cap_raise':.010,'cap_cut_z':.080,'bun_y':.035,
             'curl_amplitude':.003,'curl_y':-.070,'curl_top_z':.095,
             'curl_length':.150,'earring_drop':.045}
REFERENCE_ALPHA=.38
SCENE_NAME='Character_Blockout_4x'
PALETTE={'Skin':'8B5A3C','Denim':'4A6FA5','Coral':'E8705F','Beige':'D9C9AE',
         'Navy':'1F3B5C','Cream':'EDE6D6','Hair':'1A1210','Gold':'C9A24A'}
BASE=Path(__file__).resolve().parent
REFS=BASE/'refs';RENDERS=BASE/'renders';EXPORT=BASE/'export'
PARAMETER_NAMES=[name for name,value in tuple(globals().items())
                 if name.isupper() and isinstance(value,(int,float,dict,list,tuple))]
GENERATED=[];MATERIALS={};NORMALIZATION=(1.0,0.0);GRAPH=None

# ---------------------------------------------------------------------------
# 2. UTILIDADES DE MALLA Y MATERIALES. Sin assets ni texturas descargados.
# ---------------------------------------------------------------------------
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def material(name):
 if name in MATERIALS:return MATERIALS[name]
 m=bpy.data.materials.new('Blockout_'+name);m.use_nodes=True
 c=tuple(linear(int(PALETTE[name][i:i+2],16)/255) for i in (0,2,4))
 m.diffuse_color=(*c,1)
 node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 node.inputs['Base Color'].default_value=(*c,1);node.inputs['Roughness'].default_value=.8
 if name=='Gold':node.inputs['Metallic'].default_value=.7
 MATERIALS[name]=m;return m
def mesh(name,verts,faces,color):
 data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
 obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);data.materials.append(material(color));GENERATED.append(obj)
 for p in data.polygons:p.use_smooth=True
 return obj
def activate(obj):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
def apply(obj,modifier):activate(obj);bpy.ops.object.modifier_apply(modifier=modifier.name)
def clean(obj):
 bm=bmesh.new();bm.from_mesh(obj.data)
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
def join(name,parts):
 bpy.ops.object.select_all(action='DESELECT')
 for obj in parts:obj.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=parts[0];obj.name=name
 activate(obj);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 clean(obj);return obj
def ellipsoid(name,center,size,color,segments=24,rings=12,texture=.0):
 verts=[(center[0],center[1],center[2]-size[2])]
 for j in range(1,rings):
  v=-pi/2+pi*j/rings
  for i in range(segments):
   a=2*pi*i/segments;r=1+texture*sin(a*7+v*3)*cos(v*9)
   verts.append((center[0]+size[0]*cos(v)*cos(a)*r,center[1]+size[1]*cos(v)*sin(a)*r,center[2]+size[2]*sin(v)*r))
 verts.append((center[0],center[1],center[2]+size[2]));top=len(verts)-1
 faces=[(0,1+(i+1)%segments,1+i) for i in range(segments)]
 for j in range(rings-2):
  for i in range(segments):faces.append((1+j*segments+i,1+j*segments+(i+1)%segments,1+(j+1)*segments+(i+1)%segments,1+(j+1)*segments+i))
 faces.extend((top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments) for i in range(segments))
 return mesh(name,verts,faces,color)
def tube(name,points,radii,color,sides=12):
 points=[Vector(p) for p in points];verts=[]
 for j,p in enumerate(points):
  d=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized();axis=Vector((0,1,0))
  if abs(d.dot(axis))>.95:axis=Vector((1,0,0))
  u=d.cross(axis).normalized();v=d.cross(u).normalized()
  verts.extend(p+(u*cos(2*pi*i/sides)+v*sin(2*pi*i/sides))*radii[j] for i in range(sides))
 faces=[(j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i) for j in range(len(points)-1) for i in range(sides)]
 faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))]);return mesh(name,verts,faces,color)
def ring_mesh(name,rings,color,n=24):
 verts=[(x+rx*cos(2*pi*i/n),y+ry*sin(2*pi*i/n),z) for x,y,z,rx,ry in rings for i in range(n)]
 faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rings)-1) for i in range(n)]
 return mesh(name,verts,faces,color)
def arm_points(side):
 a=math.radians(ARM_ANGLE_DEG);d=Vector((side*cos(a),-.025,-sin(a))).normalized()
 shoulder=Vector((side*SHOULDER_HALF,0,CHEST_Z-BODY_GUIDES['shoulder_drop']));elbow=shoulder+d*UPPER_ARM_LENGTH;wrist=elbow+d*LOWER_ARM_LENGTH
 return shoulder,elbow,wrist,wrist+d*HAND_LENGTH

# ---------------------------------------------------------------------------
# 3. REFERENCIAS: lectura de silueta, altura física y Empties de imagen.
# ---------------------------------------------------------------------------
def image_mask(path,reference=False):
 image=bpy.data.images.load(str(path),check_existing=False);w0,h0=image.size
 w=max(32,round(w0*256/h0));image.scale(w,256);pixels=list(image.pixels[:]);rows=[]
 for y in range(256):
  row=[]
  for x in range(w):
   i=((255-y)*w+x)*4;r,g,b,a=pixels[i:i+4]
   yes=(max(r,g,b)-min(r,g,b)>REFERENCE_CHROMA_THRESHOLD or (r+g+b)/3<REFERENCE_DARK_THRESHOLD) if reference else a>RENDER_ALPHA_THRESHOLD
   row.append(bool(yes))
  rows.append(row)
 bpy.data.images.remove(image)
 positions=[(x,y) for y,row in enumerate(rows) for x,v in enumerate(row) if v]
 if not positions:raise RuntimeError('No se detectó silueta en '+str(path))
 xs,ys=zip(*positions);box=[min(xs),min(ys),max(xs),max(ys)]
 return {'rows':rows,'width':w,'height':256,'original_size':[w0,h0],'box':box}
def width_at(mask,fraction,central=False):
 x0,y0,x1,y1=mask['box'];yc=y1-fraction*(y1-y0);values=[]
 for y in range(max(0,round(yc)-2),min(256,round(yc)+3)):
  row=[x for x,v in enumerate(mask['rows'][y]) if v]
  if row:
   if central:
    runs=[];start=previous=row[0]
    for x in row[1:]:
     if x>previous+1:runs.append((start,previous));start=x
     previous=x
    runs.append((start,previous));mid=(x0+x1)/2
    left,right=min(runs,key=lambda run:abs((run[0]+run[1])/2-mid))
   else:left,right=min(row),max(row)
   values.append((right-left)/(y1-y0))
 return statistics.median(values) if values else 0
def metrics(mask):
 x0,y0,x1,y1=mask['box']
 result={'head_width':width_at(mask,.88),'shoulder_width':width_at(mask,.74),
  'hip_width':width_at(mask,.54),'knee_width':width_at(mask,.27),'hem_width':width_at(mask,.09),
  'overall_width':(x1-x0)/(y1-y0),'neck_width':width_at(mask,NECK_MEASUREMENT_FRACTION,True),
  'pelvis_width':width_at(mask,.54,True)}
 center=round((x0+x1)/2);split=0
 for y in range(y1-5,y0,-1):
  row=mask['rows'][y];left=any(row[x0:max(x0,center-3)]);right=any(row[min(x1,center+3):x1+1])
  if left and right and not any(row[max(0,center-1):center+2]):split=(y1-y)/(y1-y0)
  elif split>.1:break
 result['leg_split_height']=split;return result
def calibration(mask):
 w,h=mask['original_size'];x0,y0,x1,y1=mask['box']
 # Convertir las coordenadas de análisis al tamaño original.
 px=HEIGHT/((y1-y0)*h/256)
 return {'pixel_m':px,'center_px':(x0+x1)/2*w/mask['width'],'feet_px':y1*h/256,
  'camera_height_m':h*px,'camera_z':(y1*h/256-h/2)*px,'size':[w,h]}
def setup_references(reference_masks):
 coll=bpy.data.collections.new('References_Only');bpy.context.scene.collection.children.link(coll)
 for view in ['front','side','back']:
  c=calibration(reference_masks[view]);w,h=c['size'];obj=bpy.data.objects.new('REF_'+view,None);coll.objects.link(obj)
  obj.empty_display_type='IMAGE';obj.data=bpy.data.images.load(str(REFS/(view+'.png')),check_existing=True)
  obj.data.pack()             # El .blend también funciona fuera de esta carpeta.
  obj.empty_display_size=max(w,h)*c['pixel_m'];obj.color=(1,1,1,REFERENCE_ALPHA);obj.empty_image_depth='BACK';obj.hide_render=True
  shift=(w/2-c['center_px'])*c['pixel_m']
  if view=='front':obj.location=(shift,-.65,c['camera_z']);obj.rotation_euler=(pi/2,0,0)
  elif view=='side':obj.location=(.65,-shift,c['camera_z']);obj.rotation_euler=(pi/2,0,-pi/2)
  else:obj.location=(-shift,.65,c['camera_z']);obj.rotation_euler=(pi/2,0,pi)
  obj['ReferenceHeightMeters']=HEIGHT;obj['FootBaselineZ']=0.0

# ---------------------------------------------------------------------------
# 4. BODY: grafo simétrico, Mirror, Skin y subdivisión; jaula editable.
# ---------------------------------------------------------------------------
def build_body():
 global GRAPH
 points=[];edges=[];radii=[]
 def add(p,r,parent=None):
  index=len(points);points.append(p);radii.append(r)
  if parent is not None:edges.append((parent,index))
  return index
 pelvis=add((0,0,HIP_Z),(HIP_RADIUS*DETAILS['pelvis_radius_factor'],HIP_DEPTH))
 waist=add((0,0,WAIST_Z),(WAIST_RADIUS,WAIST_DEPTH),pelvis)
 ribs=add((0,0,CHEST_Z-BODY_GUIDES['rib_drop']),(DETAILS['rib_radius_x'],BODY_DEPTH),waist)
 chest=add((0,0,CHEST_Z),(DETAILS['rib_radius_x'],BODY_DEPTH*.94),ribs)
 neck=add((0,0,NECK_Z),(DETAILS['neck_radius_x'],DETAILS['neck_radius_y']),chest)
 chin=add((0,BODY_GUIDES['chin_y'],HEAD_CENTER_Z-HEAD_HEIGHT*CHIN_HEIGHT_FACTOR),(BODY_GUIDES['chin_radius'],)*2,neck)
 middle=add((0,BODY_GUIDES['head_y'],HEAD_CENTER_Z),(HEAD_WIDTH/2,HEAD_DEPTH/2),chin)
 crown=add((0,0,HEAD_CENTER_Z+HEAD_HEIGHT*.36),(HEAD_WIDTH*.40,HEAD_DEPTH*.43),middle)
 add((0,0,HEAD_CENTER_Z+HEAD_HEIGHT*.48),(BODY_GUIDES['crown_tip_radius'],)*2,crown)
 shoulder,elbow,wrist,hand=arm_points(1)
 upper=add(shoulder,(UPPER_ARM_RADIUS,UPPER_ARM_RADIUS),chest)
 upper_mid=add(shoulder.lerp(elbow,.45),(UPPER_ARM_RADIUS*.93,UPPER_ARM_RADIUS*.9),upper)
 joint=add(elbow,(DETAILS['elbow_radius_x'],DETAILS['elbow_radius_y']),upper_mid)
 lower=add(elbow.lerp(wrist,.43),(DETAILS['forearm_radius_x'],DETAILS['forearm_radius_y']),joint)
 end=add(wrist,(WRIST_RADIUS,WRIST_RADIUS),lower)
 add(hand,(DETAILS['palm_radius_x'],DETAILS['palm_radius_y']),end)
 hip=add((BODY_GUIDES['hip_x'],0,HIP_Z-BODY_GUIDES['hip_drop']),(THIGH_RADIUS,BODY_GUIDES['hip_depth']),pelvis)
 thigh=add((BODY_GUIDES['thigh_x'],0,HIP_Z-BODY_GUIDES['thigh_drop']),(THIGH_RADIUS*.92,BODY_GUIDES['thigh_depth']),hip)
 knee=add((BODY_GUIDES['knee_x'],BODY_GUIDES['knee_y'],KNEE_Z),(KNEE_RADIUS,KNEE_RADIUS),thigh)
 calf=add((BODY_GUIDES['calf_x'],BODY_GUIDES['calf_y'],(KNEE_Z+ANKLE_Z)/2),(DETAILS['calf_radius_x'],DETAILS['calf_radius_y']),knee)
 ankle=add((LEG_SPREAD,0,ANKLE_Z),(ANKLE_RADIUS,BODY_GUIDES['ankle_depth']),calf)
 foot=add((LEG_SPREAD,BODY_GUIDES['foot_y'],BODY_GUIDES['foot_z']),(BODY_GUIDES['foot_width'],BODY_GUIDES['foot_depth']),ankle)
 add((LEG_SPREAD,BODY_GUIDES['toe_y'],BODY_GUIDES['toe_z']),(BODY_GUIDES['toe_width'],BODY_GUIDES['toe_depth']),foot)
 data=bpy.data.meshes.new('Body_SkinGraph');data.from_pydata(points,edges,[]);data.update()
 obj=bpy.data.objects.new('Body',data);bpy.context.scene.collection.objects.link(obj);GENERATED.append(obj);data.materials.append(material('Skin'))
 mirror=obj.modifiers.new('Symmetry graph X','MIRROR');mirror.use_axis[0]=True;mirror.use_clip=True
 skin=obj.modifiers.new('Anatomical Skin','SKIN');skin.use_smooth_shade=True;skin.branch_smoothing=.6
 bpy.context.view_layer.update()
 layer=obj.data.skin_vertices[0].data
 for entry,r in zip(layer,radii):entry.radius=r
 layer[pelvis].use_root=True
 # Conservar el grafo editable como fuente oculta; se excluye del FBX.
 GRAPH=obj.copy();GRAPH.data=obj.data.copy();GRAPH.name='SOURCE_SkinGraph';bpy.context.scene.collection.objects.link(GRAPH);GRAPH.hide_render=True;GRAPH.hide_set(True);GENERATED.append(GRAPH)
 apply(obj,mirror);apply(obj,skin)
 subdiv=obj.modifiers.new('Blockout subdivision','SUBSURF');subdiv.levels=SUBDIVISION_LEVEL;apply(obj,subdiv)
 clean(obj)
 refine_head_cage(obj)
 # Mirror activo en la malla final para mantener edición simétrica en X.
 mirror=obj.modifiers.new('Mirror X editable','MIRROR');mirror.use_axis[0]=True;mirror.use_bisect_axis[0]=True;mirror.use_clip=True;mirror.merge_threshold=.0001
 for p in obj.data.polygons:p.use_smooth=True
 return obj

def refine_head_cage(obj):
 """Une una jaula de cabeza y mandíbula al cuello, sin costura ni triangulación."""
 bm=bmesh.new();bm.from_mesh(obj.data)
 # Cortar por filas existentes conserva quads; después se nivela la frontera.
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>NECK_CAGE_CUT_Z],context='FACES')
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 edges=[e for e in bm.edges if e.is_boundary]
 boundary={v for e in edges for v in e.verts}
 if not boundary or len(boundary)%2:raise RuntimeError('Frontera de cuello no válida para quads')
 # Recorrer la conectividad real evita cruzar diagonales en el puente.
 start=min(boundary,key=lambda v:math.atan2(v.co.y,v.co.x));ordered=[start];previous=None;current=start
 while True:
  neighbors=[e.other_vert(current) for e in current.link_edges if e.is_boundary and e.other_vert(current)!=previous]
  if not neighbors:raise RuntimeError('Frontera de cuello abierta')
  following=neighbors[0]
  if following==start:break
  ordered.append(following);previous,current=current,following
  if len(ordered)>len(boundary):raise RuntimeError('Frontera de cuello ambigua')
 if len(ordered)!=len(boundary):raise RuntimeError('Más de una frontera en el cuerpo')
 signed_area=sum(v.co.x*ordered[(i+1)%len(ordered)].co.y-ordered[(i+1)%len(ordered)].co.x*v.co.y for i,v in enumerate(ordered))
 direction=1 if signed_area>0 else -1
 angles=[-pi+direction*2*pi*i/len(ordered) for i in range(len(ordered))]
 obj['HeadNeckBoundaryVertices']=len(ordered)
 for vertex,a in zip(ordered,angles):
  vertex.co=(DETAILS['neck_radius_x']*cos(a),DETAILS['neck_radius_y']*sin(a),NECK_CAGE_CUT_Z)
 previous_ring=ordered;n=len(ordered)
 def head_z(z):return HEAD_CENTER_Z+(z-HEAD_PROFILE_REFERENCE_CENTER)*HEAD_HEIGHT/HEAD_PROFILE_REFERENCE_HEIGHT
 for z,rx,front,back,cy in HEAD_RING_PROFILE:
  z=head_z(z)
  ring=[]
  for a in angles:
   sy=sin(a)
   y=cy+HEAD_DEPTH/2*(front*(-abs(sy)**FACE_PLANE_EXPONENT) if sy<0 else back*sy)
   ring.append(bm.verts.new((HEAD_WIDTH/2*rx*cos(a),y,z)))
  for i in range(n):bm.faces.new((previous_ring[i],previous_ring[(i+1)%n],ring[(i+1)%n],ring[i]))
  previous_ring=ring
 top=bm.verts.new((0,HEAD_RING_PROFILE[-1][-1],head_z(HEAD_TOP_Z)))
 for i in range(0,n,2):bm.faces.new((previous_ring[i],previous_ring[(i+1)%n],previous_ring[(i+2)%n],top))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if any(not e.is_manifold for e in bm.edges) or any(len(f.verts)!=4 for f in bm.faces):
  raise RuntimeError('La jaula refinada debe quedar cerrada y en quads')
 bm.to_mesh(obj.data);bm.free();obj.data.update()

# ---------------------------------------------------------------------------
# 5. PRENDAS, PELO, CALZADO Y AROS: objetos y colores separados.
# ---------------------------------------------------------------------------
def garment(name,body,color,predicate,offset,bisects=()):
 obj=body.copy();obj.data=body.data.copy();obj.name=name;bpy.context.scene.collection.objects.link(obj);GENERATED.append(obj)
 for mod in list(obj.modifiers):obj.modifiers.remove(mod)
 obj.data.materials.clear();obj.data.materials.append(material(color))
 bm=bmesh.new();bm.from_mesh(obj.data)
 for point,normal in bisects:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,dist=.00001)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if not predicate(f.calc_center_median())],context='FACES')
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.normal_update()
 for v in bm.verts:v.co+=v.normal*offset
 bm.to_mesh(obj.data);bm.free()
 solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=DETAILS['cloth_thickness'];apply(obj,solid);clean(obj);return obj
def build_jacket(body):
 sh,el,wr,ha=arm_points(1);axis=(wr-sh).normalized();length=(wr-sh).length;end=sh+(wr-sh)*CUFF_ARM_FRACTION
 def keep(p):
  torso=abs(p.x)<SHOULDER_HALF*1.05
  if torso:return JACKET_HEM_Z<p.z<NECK_Z+JACKET_GUIDES['neck_margin'] and not(abs(p.x)<JACKET_OPEN_HALF and p.y<0)
  q=Vector((abs(p.x),p.y,p.z));t=(q-sh).dot(axis)/length
  return p.z>JACKET_GUIDES['sleeve_min_z'] and t<CUFF_ARM_FRACTION
 planes=[((0,0,JACKET_HEM_Z),(0,0,1)),((JACKET_OPEN_HALF,0,0),(1,0,0)),((-JACKET_OPEN_HALF,0,0),(1,0,0)),(end,axis),((-end.x,end.y,end.z),(-axis.x,axis.y,axis.z))]
 jacket=garment('Jacket',body,'Denim',keep,JACKET_OFFSET,planes);parts=[jacket]
 cloth_surface=BVHTree.FromPolygons([v.co.copy() for v in jacket.data.vertices],[list(p.vertices) for p in jacket.data.polygons])
 body_surface=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 def project(obj):
  for v in obj.data.vertices:
   hit,_,_,_=cloth_surface.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
   if hit:v.co.y=hit.y-DETAILS['panel_offset']
   else:
    hit,_,_,_=body_surface.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
    if hit:v.co.y=hit.y-JACKET_OFFSET-DETAILS['panel_offset']
  bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update()
  for f in bm.faces:
   if f.normal.y>0:f.normal_flip()
  bm.to_mesh(obj.data);bm.free()
 for side in [-1,1]:
  d=Vector((side*axis.x,axis.y,axis.z));center=Vector((side*end.x,end.y,end.z))-d*CUFF_OVERLAP
  def keep_cuff(p):return side*p.x>SHOULDER_HALF*.9 and abs((p-center).dot(d))<CUFF_WIDTH/2
  # El puño sigue la misma superficie que la manga, incluso después del ajuste.
  cuff=garment('RolledCuff',body,'Denim',keep_cuff,JACKET_OFFSET+DETAILS['cuff_extra_offset'],
               [(center-d*CUFF_WIDTH/2,d),(center+d*CUFF_WIDTH/2,d)])
  parts.append(cuff)
  # Cuello y bolsillos de pecho de baja resolución, para esculpir después.
  y=-BODY_DEPTH-JACKET_OFFSET-JACKET_GUIDES['panel_depth'];x=side*JACKET_GUIDES['pocket_x'];z=CHEST_Z-JACKET_GUIDES['pocket_drop']
  pocket_scale=DETAILS['pocket_half_width']/CHEST_POCKET_OUTLINE[1][0]
  parts.append(mesh('ChestPocket',[(x+dx*pocket_scale,y+dy,z+dz) for dx,dy,dz in CHEST_POCKET_OUTLINE],[(0,1,2,3,4)],'Denim'))
  parts.append(mesh('PocketFlap',[(x+dx,y+dy,z+dz) for dx,dy,dz in FLAP_OUTLINE],[(0,1,2,3,4)],'Denim'))
  parts.append(mesh('ShirtCollar',[(side*dx,dy,NECK_Z+dz) for dx,dy,dz in COLLAR_OUTLINE],[(0,1,2,3)],'Denim'))
 for part in parts:
  if part.name.startswith(('ChestPocket','PocketFlap','ShirtCollar')):project(part)
 return join('Jacket',parts)
def build_top(body):
 return garment('Top',body,'Coral',lambda p:TOP_HEM_Z<p.z<NECK_Z+DETAILS['top_offset'] and abs(p.x)<SHOULDER_HALF*.9,DETAILS['top_offset'],[((0,0,TOP_HEM_Z),(0,0,1)),((0,0,NECK_Z),(0,0,1))])
def build_pants():
 verts=[];faces=[];tops={}
 def ring(x,y,z,rx,ry,n=8):
  indices=list(range(len(verts),len(verts)+n));verts.extend((x+rx*cos(2*pi*i/n),y+ry*sin(2*pi*i/n),z) for i in range(n));return indices
 def bridge(a,b):faces.extend((a[i],a[(i+1)%len(a)],b[(i+1)%len(b)],b[i]) for i in range(len(a)))
 for side in [-1,1]:
  rings=[]
  for z,cx in [(PANTS_HEM_Z,LEG_SPREAD),(PANTS_GUIDES['lower_support_z'],LEG_SPREAD-PANTS_GUIDES['lower_x_offset']),(KNEE_Z,BODY_GUIDES['knee_x']),(HIP_Z-PANTS_GUIDES['thigh_drop'],PANTS_GUIDES['thigh_x'])]:
   lower=z<=PANTS_GUIDES['lower_support_z']
   r=min(PANTS_LEG_RADIUS*(PANTS_HEM_FLARE_X if lower else 1),cx-PANTS_GUIDES['minimum_gap'])
   rings.append(ring(side*cx,0,z,r,PANTS_DEPTH*(PANTS_HEM_FLARE_Y if lower else 1)))
  for a,b in zip(rings,rings[1:]):bridge(a,b)
  top=ring(side*PANTS_GUIDES['saddle_x'],0,HIP_Z,PANTS_GUIDES['saddle_x'],PANTS_DEPTH)
  inner=[3,4,5] if side==1 else [1,0,7]
  for j,i in enumerate(inner):verts[top[i]]=(0,(1-j)*PANTS_DEPTH*1.05,HIP_Z-PANTS_CROTCH_DROP if j!=1 else HIP_Z-PANTS_CROTCH_DROP-PANTS_GUIDES['saddle_drop'])
  bridge(rings[-1],top);tops[side]=top
 remap={tops[-1][l]:tops[1][r] for l,r in [(1,3),(0,4),(7,5)]}
 faces=[tuple(remap.get(v,v) for v in f) for f in faces]
 bottom=[tops[1][i] for i in [5,6,7,0,1,2,3]]+[tops[-1][i] for i in [2,3,4,5,6]]
 previous=bottom
 for z,rx,ry in [(HIP_Z+PANTS_GUIDES['hip_raise'],PANTS_HIP_RADIUS,PANTS_DEPTH*PANTS_GUIDES['hip_depth_multiplier']),(PANTS_WAIST_Z-PANTS_GUIDES['waist_support_drop'],WAIST_RADIUS+PANTS_GUIDES['waist_extra_x'],WAIST_DEPTH+PANTS_GUIDES['waist_extra_y']),(PANTS_WAIST_Z,WAIST_RADIUS+PANTS_GUIDES['waist_rim_extra_x'],WAIST_DEPTH+PANTS_GUIDES['waist_rim_extra_y'])]:
  current=list(range(len(verts),len(verts)+12));verts.extend((rx*cos(-pi/2+2*pi*i/12),ry*sin(-pi/2+2*pi*i/12),z) for i in range(12));bridge(previous,current);previous=current
 pants=mesh('Pants',verts,faces,'Beige');clean(pants)
 sub=pants.modifiers.new('Cloth blockout smoothing','SUBSURF');sub.levels=1;apply(pants,sub)
 parts=[pants]
 surface=BVHTree.FromPolygons([v.co.copy() for v in pants.data.vertices],[list(p.vertices) for p in pants.data.polygons])
 for side in [-1,1]:
  x=side*PANTS_GUIDES['back_pocket_x'];y=PANTS_DEPTH*1.10+DETAILS['panel_offset'];z=HIP_Z+PANTS_GUIDES['back_pocket_raise']
  pocket=mesh('BackPocket',[(x+dx,y+dy,z+dz) for dx,dy,dz in BACK_POCKET_OUTLINE],[(0,1,2,3,4)],'Beige')
  for vertex in pocket.data.vertices:
   hit,_,_,_=surface.ray_cast(Vector((vertex.co.x,1,vertex.co.z)),Vector((0,-1,0)))
   if hit:vertex.co.y=hit.y+DETAILS['panel_offset']
  parts.append(pocket)
  points=[]
  for i in range(33):
   direction=Vector((cos(2*pi*i/32),sin(2*pi*i/32),0))
   origin=Vector((side*BODY_GUIDES['knee_x'],0,KNEE_Z));hit,normal,_,_=surface.ray_cast(origin,direction)
   points.append(hit+normal*DETAILS['seam_surface_offset'] if hit else origin+direction*min(PANTS_LEG_RADIUS,PANTS_DEPTH))
  parts.append(tube('KneeSeam',points,[DETAILS['seam_radius']]*len(points),'Beige',6))
 return join('Pants',parts)
def build_shoes():
 parts=[]
 for side in [-1,1]:
  x=side*LEG_SPREAD
  sole=ring_mesh('Sole',[(x,SHOE_PROFILE['center_y'],0,SHOE_WIDTH*.47,SHOE_LENGTH*.48),(x,SHOE_PROFILE['center_y'],SHOE_PROFILE['bevel_z'],SHOE_WIDTH/2,SHOE_LENGTH/2),(x,SHOE_PROFILE['center_y'],SOLE_HEIGHT,SHOE_WIDTH/2,SHOE_LENGTH/2)],'Cream',24)
  # Cerrar la base y la unión con el empeine.
  bm=bmesh.new();bm.from_mesh(sole.data);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bm.to_mesh(sole.data);bm.free();parts.append(sole)
  upper=ring_mesh('ShoeUpper',[(x,SHOE_PROFILE['center_y'],SOLE_HEIGHT,SHOE_WIDTH*.48,SHOE_LENGTH*.48),(x,SHOE_PROFILE['upper_mid_y'],SHOE_PROFILE['upper_mid_z'],SHOE_WIDTH*.46,SHOE_LENGTH*.44),(x,SHOE_PROFILE['collar_y'],SHOE_PROFILE['collar_base_z'],SHOE_WIDTH*.37,SHOE_LENGTH*.28),(x,0,SHOE_HEIGHT,SHOE_WIDTH*.32,SHOE_LENGTH*.20)],'Navy',24);parts.append(upper)
 return join('Shoes',parts)
def build_hair():
 parts=[]
 center=(0,HAIR_GUIDES['cap_y'],HEAD_CENTER_Z+HAIR_GUIDES['cap_raise']);size=(HEAD_WIDTH/2+HAIR_CAP_EXTRA,HEAD_DEPTH/2+HAIR_CAP_EXTRA,HEAD_HEIGHT*.52)
 cap=ellipsoid('HairCap',center,size,'Hair',32,16)
 bm=bmesh.new();bm.from_mesh(cap.data)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z<HEAD_CENTER_Z+HAIR_GUIDES['cap_cut_z']],context='FACES');bm.to_mesh(cap.data);bm.free();clean(cap);parts.append(cap)
 parts.append(ellipsoid('CurlyBun',(0,HAIR_GUIDES['bun_y'],BUN_CENTER_Z),(BUN_RADIUS,BUN_RADIUS*.95,BUN_RADIUS),'Hair',32,20,.07))
 for side in [-1,1]:
  points=[]
  for i in range(30):
   t=i/29;points.append((side*(HEAD_WIDTH*.42+HAIR_GUIDES['curl_amplitude']*sin(t*6*pi)),HAIR_GUIDES['curl_y']+HAIR_GUIDES['curl_amplitude']*cos(t*6*pi),HEAD_CENTER_Z+HAIR_GUIDES['curl_top_z']-HAIR_GUIDES['curl_length']*t))
  parts.append(tube('LooseCurl',points,[DETAILS['curl_radius']]*len(points),'Hair',8))
 return join('Hair',parts)
def build_earrings():
 parts=[]
 for side in [-1,1]:
  points=[(side*HEAD_WIDTH*.47,EARRING_RADIUS*cos(2*pi*i/24),HEAD_CENTER_Z-HAIR_GUIDES['earring_drop']+EARRING_RADIUS*sin(2*pi*i/24)) for i in range(25)]
  parts.append(tube('SmallHoop',points,[DETAILS['hoop_wire_radius']]*len(points),'Gold',8))
 return join('Earrings',parts)
def build_character():
 global NORMALIZATION
 body=build_body();parts=[body,build_jacket(body),build_top(body),build_pants(),build_shoes(),build_hair(),build_earrings()]
 low=min(v.co.z for obj in parts for v in obj.data.vertices);high=max(v.co.z for obj in parts for v in obj.data.vertices);scale=HEIGHT/(high-low);NORMALIZATION=(scale,low)
 for obj in parts:
  for v in obj.data.vertices:v.co=Vector((v.co.x*scale,v.co.y*scale,(v.co.z-low)*scale))
  obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1);obj.data.update()
 for v in GRAPH.data.vertices:v.co=Vector((v.co.x*scale,v.co.y*scale,(v.co.z-low)*scale))
 for entry in GRAPH.data.skin_vertices[0].data:entry.radius=(entry.radius[0]*scale,entry.radius[1]*scale)
 source_sub=GRAPH.modifiers.new('Source subdivision preview','SUBSURF');source_sub.levels=SUBDIVISION_LEVEL
 return parts

# ---------------------------------------------------------------------------
# 6. RENDER Y AJUSTE ITERATIVO DE SILUETA, CON MÉTRICAS Y LÍMITES EXPLÍCITOS.
# ---------------------------------------------------------------------------
def render_views(scene,parts,camera,references,iteration):
 masks={}
 for view in ['front','side','back']:
  c=calibration(references[view]);w,h=c['size'];offset=(w/2-c['center_px'])*c['pixel_m']
  center=Vector((offset,0,c['camera_z'])) if view=='front' else Vector((0,-offset,c['camera_z'])) if view=='side' else Vector((-offset,0,c['camera_z']))
  direction={'front':(0,-6,0),'side':(-6,0,0),'back':(0,6,0)}[view]
  camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
  camera.data.ortho_scale=c['camera_height_m']*max(1,w/h);scene.render.resolution_x=w;scene.render.resolution_y=h
  folder=RENDERS/('iteration_%02d'%iteration);folder.mkdir(exist_ok=True)
  scene.render.filepath=str(folder/(view+'.png'));bpy.ops.render.render(write_still=True)
  masks[view]=image_mask(folder/(view+'.png'))
 return masks
def compare(references,renders):
 report={};errors=[];ious=[]
 for view in references:
  ref=references[view];out=renders[view];a=metrics(ref);b=metrics(out)
  differences={k:(b[k]/a[k]-1) if a[k]>.001 else None for k in a}
  intersection=sum(x and y for r,s in zip(ref['rows'],out['rows']) for x,y in zip(r,s));union=sum(x or y for r,s in zip(ref['rows'],out['rows']) for x,y in zip(r,s));iou=intersection/max(1,union)
  report[view]={'reference':a,'render':b,'relative_difference':differences,'silhouette_iou':iou}
  errors.extend(abs(v) for k,v in differences.items() if v is not None and k!='leg_split_height');ious.append(iou)
 clipped={v:out['box'][0]<=0 or out['box'][2]>=out['width']-1 for v,out in renders.items()}
 mean=statistics.mean(errors);maximum=max(errors)
 return {'views':report,'mean_proportion_error':mean,'max_width_error':maximum,'mean_iou':statistics.mean(ious),'clipped_horizontal':clipped,'score':mean+.6*(1-statistics.mean(ious))+.3*sum(clipped.values()),'reasonable':mean<=REASONABLE_MEAN_ERROR and maximum<=REASONABLE_MAX_WIDTH_ERROR and statistics.mean(ious)>=REASONABLE_IOU and not any(clipped.values())}
def adjust(report):
 g=globals();views=report['views']
 def ratio(key,view='front'):
  data=views[view];return data['reference'][key]/max(.001,data['render'][key])
 def change(name,factor):g[name]*=max(1-MAX_WIDTH_UPDATE,min(1+MAX_WIDTH_UPDATE,factor))
 change('HEAD_WIDTH',ratio('head_width')**.7);change('SHOULDER_HALF',ratio('shoulder_width')**.7)
 change('PANTS_HIP_RADIUS',ratio('hip_width')**.6);change('PANTS_LEG_RADIUS',(ratio('knee_width')*ratio('hem_width'))**.25)
 change('PANTS_DEPTH',ratio('knee_width','side')**.5);change('BODY_DEPTH',ratio('shoulder_width','side')**.7)
 change('HEAD_DEPTH',ratio('head_width','side')**.5)
 scale,_=NORMALIZATION
 target_width=views['front']['reference']['overall_width']*HEIGHT
 cosine=max(.15,min(.90,(target_width/(2*scale)-SHOULDER_HALF-.020)/(UPPER_ARM_LENGTH+LOWER_ARM_LENGTH+HAND_LENGTH)))
 desired=math.degrees(math.acos(cosine))
 g['ARM_ANGLE_DEG']=max(38,min(72,.25*ARM_ANGLE_DEG+.75*desired))
 d=views['front']['reference']['leg_split_height']-views['front']['render']['leg_split_height']
 g['HIP_Z']=max(.76,min(.90,HIP_Z+max(-.015,min(.015,d*HEIGHT*.4))))
def cleanup_generated():
 for obj in list(GENERATED):
  try:
   if obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
  except ReferenceError:pass
 GENERATED.clear()

# ---------------------------------------------------------------------------
# 7. ARMATURE HUMANOIDE Y PESOS AUTOMÁTICOS. No se sustituyen por pesos ficticios.
# ---------------------------------------------------------------------------
def build_rig(parts):
 scale,low=NORMALIZATION
 def p(v):return Vector((v[0]*scale,v[1]*scale,(v[2]-low)*scale))
 data=bpy.data.armatures.new('Humanoid');rig=bpy.data.objects.new('Armature',data);bpy.context.scene.collection.objects.link(rig)
 activate(rig);bpy.ops.object.mode_set(mode='EDIT')
 bones=[('Hips',(0,0,HIP_Z),(0,0,WAIST_Z),None),('Spine',(0,0,WAIST_Z),(0,0,CHEST_Z-BODY_GUIDES['rib_drop']),'Hips'),('Chest',(0,0,CHEST_Z-BODY_GUIDES['rib_drop']),(0,0,CHEST_Z),'Spine'),('Neck',(0,0,CHEST_Z),(0,0,NECK_Z+BODY_GUIDES['neck_bone_extra']),'Chest'),('Head',(0,0,NECK_Z+BODY_GUIDES['neck_bone_extra']),(0,0,HEAD_CENTER_Z+HEAD_HEIGHT*.40),'Neck')]
 for label,side in [('Left',1),('Right',-1)]:
  sh,el,wr,ha=arm_points(side)
  hip=(side*BODY_GUIDES['hip_x'],0,HIP_Z-BODY_GUIDES['hip_drop']);knee=(side*BODY_GUIDES['knee_x'],BODY_GUIDES['knee_y'],KNEE_Z)
  ankle=(side*LEG_SPREAD,0,ANKLE_Z);foot=(side*LEG_SPREAD,BODY_GUIDES['foot_bone_y'],BODY_GUIDES['foot_z']);toe=(side*LEG_SPREAD,BODY_GUIDES['toe_bone_y'],BODY_GUIDES['foot_z'])
  bones += [(label+'Shoulder',(0,0,CHEST_Z),sh,'Chest'),(label+'UpperArm',sh,el,label+'Shoulder'),(label+'LowerArm',el,wr,label+'UpperArm'),(label+'Hand',wr,ha,label+'LowerArm'),(label+'UpperLeg',hip,knee,'Hips'),(label+'LowerLeg',knee,ankle,label+'UpperLeg'),(label+'Foot',ankle,foot,label+'LowerLeg'),(label+'Toes',foot,toe,label+'Foot')]
 for name,head,tail,parent in bones:
  bone=data.edit_bones.new(name);bone.head=p(head);bone.tail=p(tail)
  if parent:bone.parent=data.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
 # El operador Bone Heat se ejecuta por malla y se comprueba después.
 checks={}
 for obj in parts:
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
  error=None
  try:bpy.ops.object.parent_set(type='ARMATURE_AUTO')
  except RuntimeError as exc:error=str(exc)
  unweighted=sum(not v.groups or sum(g.weight for g in v.groups)<.00001 for v in obj.data.vertices)
  checks[obj.name]={'bone_heat_message':error,'bone_heat_unweighted':unweighted,'repair_method':None}
  if unweighted and obj!=parts[0]:
   # Reparación automática por interpolación de los pesos Bone Heat del cuerpo.
   # No se asignan pesos de huesos a mano ni se omite la comprobación.
   missing=[v.index for v in obj.data.vertices if not v.groups or sum(g.weight for g in v.groups)<.00001]
   for source_group in parts[0].vertex_groups:
    if obj.vertex_groups.get(source_group.name) is None:obj.vertex_groups.new(name=source_group.name)
   repair_name='__WeightRepairMask';mask=obj.vertex_groups.new(name=repair_name);mask.add(missing,1,'REPLACE')
   transfer=obj.modifiers.new('Automatic missing weight repair','DATA_TRANSFER');transfer.object=parts[0]
   transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'};transfer.vert_mapping='POLYINTERP_NEAREST';transfer.vertex_group=mask.name
   transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME'
   activate(obj)
   while list(obj.modifiers).index(transfer)>0:bpy.ops.object.modifier_move_up(modifier=transfer.name)
   apply(obj,transfer)
   existing_mask=obj.vertex_groups.get(repair_name)
   if existing_mask:obj.vertex_groups.remove(existing_mask)
   checks[obj.name]['repair_method']='Automatic nearest-face interpolation from Body Bone Heat weights'
  activate(obj);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
  unweighted=sum(not v.groups or sum(g.weight for g in v.groups)<.00001 for v in obj.data.vertices)
  checks[obj.name]['unweighted_vertices']=unweighted
  if unweighted:raise RuntimeError('Pesos incompletos después de la reparación: '+obj.name+' '+str(checks[obj.name]))
 return rig,checks

# ---------------------------------------------------------------------------
# 8. VALIDACIÓN, FBX PARA UNITY Y RESUMEN DE FIDELIDAD.
# ---------------------------------------------------------------------------
def validate(parts,rig):
 info={}
 for obj in parts:
  bm=bmesh.new();bm.from_mesh(obj.data)
  info[obj.name]={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'origin':list(obj.location),'scale':list(obj.scale)};bm.free()
 return {'objects':info,'bones':[b.name for b in rig.data.bones],'unity_avatar_verified':False}
def export_fbx(parts,rig):
 bpy.ops.object.select_all(action='DESELECT')
 for obj in parts+[rig]:obj.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(EXPORT/'character.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=True,add_leaf_bones=False,bake_anim=False,use_armature_deform_only=True,use_mesh_modifiers=True,mesh_smooth_type='FACE')
def save_report(history,comparison,validation,weights,parameters):
 report={'blender_version':bpy.app.version_string,'height_m':HEIGHT,'iterations':history,'final_comparison':comparison,'parameters':parameters,'mesh_and_rig':validation,'automatic_weights':weights,'normalization_scale_and_ground':list(NORMALIZATION),'manual_sculpt_required':['rasgos faciales y orejas','dedos y anatomía fina de manos/pies','pliegues y grosor del denim','curls y línea de nacimiento del cabello','ajuste fino de pesos en hombros, cadera y puños'],'export_settings':{'apply_scalings':'FBX All','forward':'-Z','up':'Y','apply_transform':True,'leaf_bones':False}}
 (BASE/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 lines=['# Verificación del blockout','',f'Blender ejecutado: {bpy.app.version_string}. Altura objetivo: {HEIGHT:.2f} m.',f'Error medio de proporciones: {comparison["mean_proportion_error"]:.1%}. IoU media de silueta: {comparison["mean_iou"]:.3f}.',f'Criterio de coincidencia razonable alcanzado: {comparison["reasonable"]}.','','Las medidas son comparaciones de silueta 2D; no demuestran por sí solas anatomía correcta.','', '| Vista | Cabeza | Hombros | Cadera | Pantalón/rodilla | Bajo pantalón |','|---|---:|---:|---:|---:|---:|']
 for view,data in comparison['views'].items():
  d=data['relative_difference'];lines.append('|'+view+'|'+'|'.join(f'{d[k]:+.1%}' if d[k] is not None else 'n/d' for k in ['head_width','shoulder_width','hip_width','knee_width','hem_width'])+'|')
 lines +=['','Un valor positivo indica que el render resulta más ancho que la referencia. Son anchuras de silueta en filas a altura fija; hombros incluye la manga y no mide directamente la distancia entre articulaciones. Las diferencias de pose o perspectiva de la hoja pueden impedir coincidencia simultánea de las tres vistas.',
  '',f'Ángulo de brazos revisado: {ARM_ANGLE_DEG:.1f} grados por debajo de la horizontal. Las medidas revisadas se conservan por defecto; --auto-fit permite activar el ajuste automático opcional.',
  '', '| Vista | Entrepierna visible referencia/altura | Entrepierna render/altura |', '|---|---:|---:|']
 for view,data in comparison['views'].items():
  lines.append(f'|{view}|{data["reference"]["leg_split_height"]:.1%}|{data["render"]["leg_split_height"]:.1%}|')
 lines +=['','La altura de la abertura entre piernas mide el pantalón, no la longitud anatómica del fémur. No puede estimarse de forma fiable de perfil con las dos piernas superpuestas.',
  '','## Preparado','Skin y Mirror X; prendas separadas; materiales planos; rig humanoide y pesos automáticos; FBX con las opciones pedidas. El grafo original queda oculto como SOURCE_SkinGraph. Body es una jaula continua en quads. Prendas, pelo y calzado contienen bordes abiertos intencionales y pequeños paneles independientes: no se presentan como volúmenes estancos.',
  '', 'Bone Heat se ejecuta por malla. Los vértices sin peso de accesorios o ropa se reparan automáticamente por interpolación de los pesos del cuerpo; report.json registra los recuentos exactos. Esta comprobación no equivale a una revisión artística completa de las deformaciones.',
  '','## Escultura y revisión manual pendientes','Rostro, orejas, dedos, anatomía fina, pliegues, costuras finas y rizos individuales. Revisar deformaciones con el rig antes de producir animaciones. La jerarquía es apta para configurar Humanoid; no se ha validado un Avatar dentro de Unity. Apply Transform usa bake_space_transform del exportador de Blender y debe comprobarse al importar el rig.',
  '','No se descargaron modelos ni texturas. Las referencias son recortes frontal, lateral y posterior de la lámina 02_civil_mujer.png suministrada por el usuario.']
 (BASE/'verification.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--fit-iterations',type=int,default=MAX_FIT_ITERATIONS);parser.add_argument('--no-fit',action='store_true');parser.add_argument('--auto-fit',action='store_true',help='Opcional: permite cambiar automáticamente las medidas revisadas.')
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 for folder in [RENDERS,EXPORT]:folder.mkdir(exist_ok=True)
 for view in ['front','side','back']:
  if not (REFS/(view+'.png')).exists():raise FileNotFoundError('Falta la referencia '+str(REFS/(view+'.png')))
 if bpy.data.scenes.get(SCENE_NAME):raise RuntimeError('La escena de este script ya existe; ejecuta en un archivo nuevo para no borrar tu trabajo.')
 references={view:image_mask(REFS/(view+'.png'),True) for view in ['front','side','back']}
 scene=bpy.data.scenes.new(SCENE_NAME);bpy.context.window.scene=scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 try:scene.render.engine='BLENDER_EEVEE_NEXT'
 except TypeError:scene.render.engine='BLENDER_EEVEE'
 scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
 scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('BlockoutWorld');scene.world.use_nodes=True
 next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.5
 setup_references(references)
 data=bpy.data.cameras.new('OrthographicCamera');camera=bpy.data.objects.new('OrthographicCamera',data);scene.collection.objects.link(camera);data.type='ORTHO';scene.camera=camera
 for name,pos,power,size in [('Key',(2,-3,4),250,4),('Fill',(-3,-1,2),150,3),('Back',(0,3,3),220,3)]:
  light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector((0,0,1))-obj.location).to_track_quat('-Z','Y').to_euler()
 history=[];best=None;parts=None
 for iteration in range(max(1,args.fit_iterations)):
  if parts:cleanup_generated()
  parts=build_character();renders=render_views(scene,parts,camera,references,iteration);comparison=compare(references,renders)
  parameters={name:globals()[name] for name in PARAMETER_NAMES};history.append({'iteration':iteration,'parameters':parameters,'comparison':comparison})
  print('FIT',iteration,'error',round(comparison['mean_proportion_error'],4),'iou',round(comparison['mean_iou'],4),flush=True)
  if (best is None or
      (comparison['reasonable'] and not best['comparison']['reasonable']) or
      (comparison['reasonable']==best['comparison']['reasonable'] and comparison['score']<best['score'])):
   best={'score':comparison['score'],'iteration':iteration,'parameters':parameters.copy(),'comparison':comparison}
  if comparison['reasonable'] or args.no_fit or not args.auto_fit:break
  if iteration+1<args.fit_iterations:adjust(comparison)
 if best['iteration']!=history[-1]['iteration']:
  globals().update(best['parameters']);cleanup_generated();parts=build_character();renders=render_views(scene,parts,camera,references,len(history));comparison=compare(references,renders)
  final_folder=RENDERS/('iteration_%02d'%len(history))
 else:final_folder=RENDERS/('iteration_%02d'%history[-1]['iteration'])
 import shutil
 for view in ['front','side','back']:shutil.copy2(final_folder/(view+'.png'),RENDERS/(view+'.png'))
 rig,weights=build_rig(parts);validation=validate(parts,rig);export_fbx(parts,rig)
 bpy.ops.object.select_all(action='DESELECT');parts[0].select_set(True);bpy.context.view_layer.objects.active=parts[0]
 # Archivo de trabajo completo: al abrirlo muestra la escena del personaje.
 # copy=True conserva el archivo que el artista tuviera abierto al ejecutar.
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    space=area.spaces.active;space.clip_start=.001;space.clip_end=100
    space.region_3d.view_location=(0,0,HEIGHT/2);space.region_3d.view_distance=2.5
    space.region_3d.view_rotation=Euler((pi/2,0,0)).to_quaternion();space.region_3d.view_perspective='ORTHO'
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'character.blend'),copy=True)
 save_report(history,comparison,validation,weights,{name:globals()[name] for name in PARAMETER_NAMES})
 print('CHARACTER_BUILD_SUCCESS',bpy.app.version_string,str(EXPORT/'character.fbx'),flush=True)
if __name__=='__main__':main()
