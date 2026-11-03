"""Personajes propios basados en las 14 referencias de Alain; Blender 5.2, metros."""
import bpy, bmesh, math, json, random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin, cos, pi

ART=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
OUT=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Personajes-V2')
OUT.mkdir(parents=True,exist_ok=True)
SCENE_NAME='Alarma_Characters_ReferenceV2'
COL=None
ROOT=None
SKIN='SkinTan'
FEMALE=False
COLORS={
 'SkinTan':'B87850','SkinDark':'855137','SkinWarm':'C99169','SkinLight':'E3B18A',
 'LipTan':'A45F4F','LipDark':'653C34','LipLight':'BD7B70','EyeWhite':'EEE9DB',
 'Iris':'65422E','Pupil':'171916','Black':'202329','Navy':'202B45','Denim':'477AA5',
 'Sky':'73A3DA','Blue':'235BC0','Petrol':'265469','Orange':'E76D23','Olive':'666B43',
 'Sand':'CFC1A0','Cream':'EEE6D6','White':'F2EFE7','Coral':'D76C58','Lavender':'AA8CD4',
 'Burgundy':'883B48','Charcoal':'414348','Sage':'7A8964','Mustard':'DCAC3D','Green':'3F6152',
 'Brown':'704B34','Copper':'9D4929','HairBrown':'4B3024','HairBlack':'28221F',
 'Metal':'8C9298','Gold':'D7B957','Sole':'D3CFC2','Stitch':'B6AF9E','DarkStitch':'333D44',
}
def mat(name):
 key='Alarma_NPC2_'+name
 m=bpy.data.materials.get(key)
 if m:return m
 m=bpy.data.materials.new(key);m.use_nodes=True
 rgb=tuple(int(COLORS[name][i:i+2],16)/255 for i in (0,2,4))
 linear=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)
 m.diffuse_color=(*linear,1)
 shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 shader.inputs['Base Color'].default_value=(*linear,1)
 shader.inputs['Roughness'].default_value=.68 if name.startswith('Skin') else .82
 return m
def mesh(name,verts,faces,color,smooth=True):
 data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
 obj=bpy.data.objects.new(name,data);COL.objects.link(obj);obj.parent=ROOT
 data.materials.append(mat(color))
 for face in data.polygons:face.use_smooth=smooth
 return obj
def ell(name,center,radii,color,segments=20,rings=12):
 verts=[(center[0],center[1],center[2]-radii[2])]
 for j in range(1,rings):
  v=-pi/2+pi*j/rings
  for i in range(segments):
   u=2*pi*i/segments
   verts.append((center[0]+radii[0]*cos(v)*cos(u),center[1]+radii[1]*cos(v)*sin(u),center[2]+radii[2]*sin(v)))
 verts.append((center[0],center[1],center[2]+radii[2]));top=len(verts)-1
 faces=[(0,1+(i+1)%segments,1+i) for i in range(segments)]
 for j in range(rings-2):
  for i in range(segments):
   a=1+j*segments+i;b=1+j*segments+(i+1)%segments
   faces.append((a,b,b+segments,a+segments))
 faces.extend((top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments) for i in range(segments))
 return mesh(name,verts,faces,color)
def tube(name,points,radii,color,sides=12,cap=True,depth=1):
 points=[Vector(p) for p in points];verts=[]
 for j,p in enumerate(points):
  tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
  axis=Vector((0,1,0))
  if abs(tangent.dot(axis))>.95:axis=Vector((1,0,0))
  u=tangent.cross(axis).normalized();v=tangent.cross(u).normalized()
  for i in range(sides):
   angle=2*pi*i/sides
   verts.append(tuple(p+u*(cos(angle)*radii[j])+v*(sin(angle)*radii[j]*depth)))
 faces=[]
 for j in range(len(points)-1):
  for i in range(sides):faces.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
 if cap:faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))])
 return mesh(name,verts,faces,color)
def line(name,points,radius,color,sides=6):return tube(name,points,[radius]*len(points),color,sides)
def box(name,center,size,color,bevel=.008):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
 for v in bm.verts:v.co=Vector((v.co.x*size[0],v.co.y*size[1],v.co.z*size[2]))
 if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bevel,min(size)*.38),segments=3,affect='EDGES')
 bm.normal_update();data=bpy.data.meshes.new(name+'_Mesh');bm.to_mesh(data);bm.free()
 obj=bpy.data.objects.new(name,data);COL.objects.link(obj);obj.parent=ROOT;obj.location=center
 data.materials.append(mat(color))
 for p in data.polygons:p.use_smooth=True
 return obj
def loft(name,rings,color,segments=32,gap=0,fold=0):
 # Anillos anatómicos: z, semiancho, profundidad, centro Y.
 verts=[];count=segments+1 if gap else segments
 for j,(z,rx,ry,y) in enumerate(rings):
  for i in range(count):
   angle=(-pi/2+gap)+(2*pi-2*gap)*i/segments if gap else 2*pi*i/segments
   wrinkle=fold*sin(j*2.4+i*1.8)*sin(pi*j/(len(rings)-1))
   verts.append(((rx+wrinkle)*cos(angle),y+(ry+wrinkle*.5)*sin(angle),z))
 faces=[]
 for j in range(len(rings)-1):
  for i in range(count-1 if gap else count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
 if not gap:faces.extend([tuple(reversed(range(count))),tuple((len(rings)-1)*count+i for i in range(count))])
 return mesh(name,verts,faces,color)
def ellipse_line(name,center,rx,ry,radius,color):
 pts=[(center[0]+rx*cos(2*pi*i/48),center[1]+ry*sin(2*pi*i/48),center[2]) for i in range(49)]
 return line(name,pts,radius,color)
def label(name,text,center,size,color,back=False):
 curve=bpy.data.curves.new(name+'_Font','FONT');curve.body=text;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size;curve.extrude=.0005;curve.resolution_u=3
 obj=bpy.data.objects.new(name,curve);COL.objects.link(obj);obj.parent=ROOT;obj.location=center
 obj.rotation_euler=(pi/2,0,pi if back else 0);curve.materials.append(mat(color))
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.object.convert(target='MESH');return bpy.context.object

def arm_points(side,tpose=False):
 if tpose:return [(side*.215,0,1.435),(side*.37,0,1.435),(side*.49,0,1.435),(side*.63,-.005,1.435),(side*.75,-.012,1.435)]
 return [(side*.215,0,1.435),(side*.31,0,1.31),(side*.40,-.014,1.17),(side*.47,-.02,1.035),(side*.53,-.025,.92)]
def anatomy(female=False,tpose=False):
 parts=[]
 torso=[(.82,.17,.112,.015),(.89,.204 if female else .186,.13,.015),(1.0,.17 if female else .18,.125,0),(1.10,.15 if female else .181,.112,0),(1.20,.177 if female else .208,.125,0),(1.32,.205 if female else .232,.132,0),(1.405,.198 if female else .23,.107,.01),(1.46,.13,.083,.008),(1.49,.065,.061,0)]
 parts.append(loft('Body_Torso',torso,SKIN))
 parts.append(loft('Body_Neck',[(1.43,.068,.062,0),(1.49,.058,.056,0),(1.56,.063,.06,0)],SKIN,24))
 # Cabeza con mandíbula, pómulos y nariz integrados, sin cara esférica superpuesta.
 profiles=[(1.558,.035,.050,-.012),(1.565,.062,.063,-.009),(1.585,.082,.073,-.001),(1.615,.096,.081,0),(1.65,.104,.087,.002),(1.69,.109,.090,.005),(1.73,.109,.093,.009),(1.77,.105,.091,.010),(1.805,.088,.079,.013),(1.83,.050,.052,.014),(1.839,.004,.006,.014)]
 verts=[];n=48
 for z,rx,ry,y in profiles:
  for i in range(n):
   a=2*pi*i/n;x=rx*cos(a);yy=y+ry*sin(a)
   front=max(0,-sin(a))**12
   nose=.051*math.exp(-((x/.019)**2)-(((z-1.663)/.045)**2))
   chin=.009*math.exp(-((x/.055)**2)-(((z-1.565)/.02)**2))
   socket=.005*math.exp(-(((abs(x)-.047)/.022)**2)-(((z-1.697)/.019)**2))
   yy-=front*(nose+chin-socket)
   verts.append((x*.96 if female else x,yy,z))
 faces=[]
 for j in range(len(profiles)-1):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.extend([tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))])
 head=mesh('Body_Head',verts,faces,SKIN)
 bpy.context.view_layer.objects.active=head
 sub=head.modifiers.new('Facial surface','SUBSURF');sub.levels=2
 bpy.ops.object.modifier_apply(modifier=sub.name)
 parts.append(head)
 for side in [-1,1]:
  parts.append(ell('Body_Ear',(side*.107,.004,1.671),(.019,.023,.039),SKIN,16,10))
  parts.append(ell('Body_NostrilWing',(side*.018,-.105,1.655),(.017,.020,.012),SKIN,16,10))
  points=arm_points(side,tpose)
  parts.append(tube('Body_Arm',points,[.072,.066,.045,.047,.032],SKIN,20))
  p=Vector(points[-1]);d=(p-Vector(points[-2])).normalized();cross=Vector((d.z,0,-d.x)).normalized()
  palmcenter=p+d*.047
  palm=ell('Body_Palm',palmcenter,(.039,.025,.061),SKIN,16,10)
  # El eje largo de la palma sigue la dirección del antebrazo.
  rot=Vector((0,0,1)).rotation_difference(d)
  for v in palm.data.vertices:v.co=palmcenter+rot@(v.co-palmcenter)
  parts.append(palm)
  for finger in range(4):
   offset=(finger-1.5)*.017
   start=p+d*.080+cross*offset
   length=[.061,.072,.067,.052][finger]
   tip=start+d*length+cross*offset*.13
   parts.append(tube('Body_Finger_%d'%finger,[start,start+d*length*.36,start+d*length*.72,tip],[.010,.0095,.008,.0055],SKIN,10))
   parts.append(ell('Body_Fingertip',tip,(.006,.008,.007),SKIN,12,8))
  start=p+d*.021+cross*side*.029
  end=p+d*.081+cross*side*.065
  parts.append(tube('Body_Thumb',[start,(start+end)/2,end],[.015,.012,.009],SKIN,12))
  parts.append(ell('Body_ThumbTip',end,(.010,.011,.011),SKIN,12,8))
  centers=[(side*.100,0,.91),(side*.107,0,.79),(side*.112,-.005,.64),(side*.115,-.025,.51),(side*.116,0,.40),(side*.116,.01,.28),(side*.116,0,.145)]
  parts.append(tube('Body_Leg',centers,[.100 if female else .094,.095,.077,.060,.067,.052,.036],SKIN,24,depth=1.04))
  parts.append(ell('Body_Foot',(side*.116,-.065,.078),(.053,.135,.070),SKIN,20,12))
 return parts
def unify_body(parts,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name=name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 rem=body.modifiers.new('Continuous skin','REMESH');rem.mode='VOXEL';rem.voxel_size=.0055;rem.use_smooth_shade=True
 bpy.ops.object.modifier_apply(modifier=rem.name)
 relax=body.modifiers.new('Skin relaxation','SMOOTH');relax.factor=.8;relax.iterations=8;bpy.ops.object.modifier_apply(modifier=relax.name)
 dec=body.modifiers.new('Base density','DECIMATE');dec.ratio=.42;bpy.ops.object.modifier_apply(modifier=dec.name)
 for p in body.data.polygons:p.use_smooth=True
 body.data.update()
 return body

def face(hair='HairBrown',variant=0):
 lip={'SkinDark':'LipDark','SkinLight':'LipLight'}.get(SKIN,'LipTan')
 for side in [-1,1]:
  xc=side*.046;zc=1.697
  # Almendra ocular; los párpados rodean la córnea, sin globos salientes.
  verts=[(xc,-.090,zc)];n=40
  for i in range(n):
   a=2*pi*i/n;xx=.031*cos(a);zz=(.014 if sin(a)>=0 else .010)*sin(a)
   verts.append((xc+xx,-.079+.008*abs(xx/.031),zc+zz+side*xx*.03))
  mesh('Eye_Sclera',verts,[(0,i+1,(i+1)%n+1) for i in range(n)],'EyeWhite')
  ell('Eye_Iris',(xc,-.091,zc),(.0105,.002,.0115),'Iris',20,12)
  ell('Eye_Pupil',(xc,-.093,zc),(.0055,.0012,.0065),'Pupil',16,10)
  ell('Eye_Catchlight',(xc-.003,-.0945,zc+.0035),(.0024,.0008,.0024),'White',12,8)
  for upper in [True,False]:
   pts=[]
   for i in range(21):
    a=pi*i/20 if upper else pi+pi*i/20
    xx=.032*cos(a);zz=(.015 if upper else .011)*sin(a)
    pts.append((xc+xx,-.080+.008*abs(xx/.032),zc+zz+side*xx*.03))
   line('UpperLid' if upper else 'LowerLid',pts,.0038 if upper else .003,SKIN,8)
   if upper:line('LashLine',[(x,y-.001,z-.001) for x,y,z in pts],.0013,'HairBlack',6)
  brow=[(xc+side*x,-.084+.012*(abs(x)/.035),1.727+z) for x,z in [(-.029,-.005),(-.014,.001),(.003,.003),(.024,-.001),(.035,-.008)]]
  tube('Eyebrow',brow,[.003,.006,.006,.004,.001],hair,8,depth=.5)
  ell('Ear_Concha',(side*.117,-.014,1.675),(.007,.009,.020),lip,12,10)
  ell('Nostril',(side*.018,-.120,1.650),(.006,.0025,.0035),lip,12,8)
  # Sutil relieve en las mejillas para definir el rostro desde tres ángulos.
 upper=[(-.029,-.079,1.620),(-.014,-.089,1.624),(0,-.094,1.622),(.014,-.089,1.624),(.029,-.079,1.620)]
 lower=[(-.029,-.080,1.619),(-.014,-.090,1.615),(0,-.094,1.614),(.014,-.090,1.615),(.029,-.080,1.619)]
 tube('UpperLip',upper,[.001,.0035,.003,.0035,.001],lip,8,depth=.6)
 tube('LowerLip',lower,[.001,.0035,.004,.0035,.001],lip,8,depth=.7)
 line('MouthCrease',[(-.027,-.083,1.619),(0,-.096,1.619),(.027,-.083,1.619)],.0009,'LipDark',6)

def hair_cap(color,style):
 # Casquete con línea de nacimiento; abertura inferior y mechones geométricos propios.
 n=40;rings=10;verts=[]
 for j in range(rings+1):
  t=j/rings
  for i in range(n):
   a=2*pi*i/n
   low=1.70+.062*max(0,-sin(a))-.022*max(0,sin(a))
   theta=(pi/2)*t
   verts.append((.114*cos(a)*cos(theta),.012+.099*sin(a)*cos(theta),low+(1.858-low)*sin(theta)))
 faces=[]
 for j in range(rings):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 cap=mesh('Hair_Cap',verts,faces,color)
 random.seed(150+len(style))
 if style=='curls':
  for j in range(110):
   theta=random.uniform(.13,1.53);a=random.uniform(0,2*pi)
   center=Vector((.112*cos(a)*cos(theta),.008+.105*sin(a)*cos(theta),1.755+.10*sin(theta)))
   r=random.uniform(.012,.021)
   ell('Hair_Curl',center,(r,r*.86,r*.80),color,12,8)
   pts=[center+Vector((r*.7*cos(t*.4),r*.7*sin(t*.4),.004+t*.0005)) for t in range(14)]
   line('Curl_Definition',pts,.0025,color,6)
 if style=='afro':
  ell('Hair_PuffVolume',(0,.065,1.89),(.090,.080,.084),color,24,16)
  for i in range(45):
   a=random.random()*2*pi;v=random.random()*pi
   ell('Hair_PuffCurl',(.081*cos(a)*sin(v),.065+.072*sin(a)*sin(v),1.89+.070*cos(v)),(.025,.023,.025),color,10,6)
 elif style in ('bun','ponytail','braid'):
  ell('Hair_Tie',(0,.108,1.754),(.043,.032,.039),'Black',16,10)
  if style=='bun':
   ell('Hair_Bun',(0,.098,1.811),(.071,.060,.066),color)
   for i in range(8):
    a=2*pi*i/8
    line('Hair_BunGroove',[(.063*cos(a),.09+.050*sin(a),1.78),(.06*cos(a+.3),.09+.050*sin(a+.3),1.83),(.025*cos(a+.5),.09+.02*sin(a+.5),1.87)],.003,'HairBlack',6)
  elif style=='braid':
   for j in range(12):
    for side in [-1,1]:ell('Hair_Braid',(side*.017*cos(j*pi/2),.11+.01*sin(j*.5),1.75-j*.028),(.025-j*.001,.027-j*.001,.026),color,14,8)
   ellipse_line('Hair_BraidTie',(0,.1,1.43),.020,.024,.004,'Cream')
  else:
   for j in range(7):ell('Hair_Ponytail',(.025*sin(j*.4),.115+.013*j,1.76-.027*j),(.040-j*.003,.032,.053),color,16,10)
 elif style=='bob':
  for side in [-1,1]:
   for j in range(6):
    a=j*pi/7
    ell('Hair_Bob',(side*(.092+.012*sin(a)),.015+.066*cos(a),1.67),(.032,.042,.11),color,16,10)
 if style not in ('curls','afro','cropped'):
  surface=BVHTree.FromPolygons([v.co.copy() for v in cap.data.vertices],[list(p.vertices) for p in cap.data.polygons])
  for i in range(15):
   x=-.10+i*.20/14;pts=[]
   for j in range(18):
    a=-pi/2+pi*j/17
    height=.112*math.sqrt(max(.08,1-(x/.122)**2))
    point=Vector((x+.009*sin(pi*j/17),.012+.104*sin(a),1.750+height*cos(a)))
    outward=(point-Vector((0,.01,1.75))).normalized()
    hit,normal,_,_=surface.ray_cast(point+outward*.3,-outward)
    pts.append(hit+normal*.002 if hit else point)
   tube('Hair_SweptLock',pts,[.001+.006*sin(pi*j/17) for j in range(18)],color,8)

def torso_rings(extra=0):
 return [(z,rx+extra,ry+extra,y) for z,rx,ry,y in [(.91,.207 if FEMALE else .195,.14,0),(.96,.202 if FEMALE else .196,.14,0),(1.04,.173 if FEMALE else .19,.13,0),(1.12,.166 if FEMALE else .195,.128,0),(1.23,.195 if FEMALE else .224,.145,-.001),(1.34,.22 if FEMALE else .246,.143,0),(1.415,.213 if FEMALE else .245,.115,.006),(1.445,.18,.095,.007),(1.49,.074,.067,0)]]
def collar(color,style='shirt'):
 if style in ('shirt','jacket'):
  for side in [-1,1]:
   verts=[(side*.065,-.045,1.50),(side*.11,-.088,1.437),(side*.056,-.143,1.385),(side*.017,-.105,1.45)]
   mesh('Collar_Lapel',verts,[(0,1,2,3)],color,False)
  ellipse_line('Collar_Back',(0,.008,1.485),.067,.062,.009,color)
 else:ellipse_line('Crew_Neck',(0,0,1.485),.070,.067,.008,color)
def shirt(color,long=True,open_front=False,style='shirt'):
 main=[loft('Garment_Top',torso_rings(.004),color,fold=.0017)]
 # Hombros cerrados por un canesú que une el cuello y la manga.
 for side in [-1,1]:
  points=arm_points(side);n=5 if long else 3
  points[0]=(side*.12,0,1.34);points[1]=(side*.26,0,1.35)
  radii=([.09,.080,.058,.060,.043] if long else [.09,.080,.070])
  main.append(tube('Garment_Sleeve',points[:n],radii,color,24,depth=1.05))
  end=Vector(points[n-1]);d=(end-Vector(points[n-2])).normalized()
  tube('Sleeve_Cuff',[end-d*.020,end,end+d*.009],[radii[-1]*1.03]*3,color,24)
  if long:
   for t in [.61,.69,.82]:
    p=Vector(points[0]).lerp(Vector(points[-1]),t)
    line('Sleeve_Fold',[p+Vector((-.025,-.046,0)),p+Vector((0,-.057,.012)),p+Vector((.027,-.043,0))],.002,color)
 unify_body(main,'Garment_Top_Continuous')
 collar(color,style)
 ellipse_line('Top_Hem',(0,0,.924),.211 if FEMALE else .202,.146,.009,color)
 if open_front:
  # Camiseta interior visible bajo las dos solapas.
  c='Coral' if color=='Denim' else ('Black' if color=='Burgundy' else 'Cream')
  # Panel visible de camiseta en la abertura central de la chaqueta.
  panel=[(x,-.16,.94+i*.52/32) for i in range(33) for x in [-.027,.027]]
  mesh('Undershirt_Front',panel,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(32)],c)
  for side in [-1,1]:
   points=[(side*.032,-.148,.94),(side*.029,-.139,1.12),(side*.035,-.153,1.33),(side*.025,-.111,1.44)]
   line('Front_Seam',points,.0022,'Metal' if color=='Orange' else color)
 else:
  line('Center_Seam',[(0,-.148,.95),(0,-.135,1.12),(0,-.153,1.33)],.0015,color)

def pants(color,kind='cargo'):
 short=kind=='shorts';wide=kind=='wide';skort=kind=='skort'
 main=[loft('Trouser_Hips',[(.78,.045,.08,.01),(.84,.14,.11,.01),(.90,.215 if FEMALE else .205,.15,0),(.94,.194 if FEMALE else .199,.142,0)],color,32,fold=.0015)]
 for side in [-1,1]:
  if short or skort:
   zs=[.51,.54,.63,.75,.85,.92];rads=[.105,.108,.109,.115,.12,.115]
  else:
   zs=[.13,.15,.18,.27,.38,.48,.52,.56,.65,.76,.86,.92]
   rads=[.085,.087,.083,.080,.083,.078,.079,.084,.096,.108,.115,.111]
   if wide:rads=[.123,.125,.126,.128,.125,.118,.115,.115,.115,.119,.12,.116]
  rings=[(z,r,r*.94,.01+(-.015 if .45<z<.6 else 0)) for z,r in zip(zs,rads)]
  obj=loft('Trouser_Leg',rings,color,24,fold=.0025);obj.location.x=side*.112;main.append(obj)
  z=zs[1]
  ellipse_line('Trouser_Hem',(side*.112,.012,z),rads[1],rads[1]*.95,.005,color)
  # Costuras laterales, bolsillos traseros y pliegues visibles.
  line('Trouser_OuterSeam',[(side*(.112+r),.01,z) for z,r in zip(zs,rads)],.0014,color)
  box('Back_Pocket',(side*.10,.146,.86),(.11,.012,.103),color,.004)
  line('Pocket_Seam',[(side*.1-.047,.155,.91),(side*.1-.047,.155,.825),(side*.1,.157,.81),(side*.1+.047,.155,.825),(side*.1+.047,.155,.91)],.0012,'Stitch' if color=='Denim' else color)
  if kind in ('cargo','work','uniform'):
   pocket=box('Cargo_Pocket',(side*.206,-.005,.66),(.045,.135,.155),color,.009)
   box('Cargo_Flap',(side*.231,-.008,.725),(.013,.143,.033),color,.004)
   box('Cargo_Snap',(side*.239,-.037,.722),(.008,.018,.009),'Metal',.002)
  if not short:
   for z in [.20,.45,.53]:
    line('Trouser_Fold',[(side*.112-.055,-.071,z),(side*.112,-.092,z+.012),(side*.112+.05,-.066,z+.023)],.002,color)
 unify_body(main,'Trouser_Continuous')
 # Costura de bragueta y presillas.
 line('Trouser_Fly',[(.008,-.151,.96),(.008,-.157,.88),(.022,-.145,.84)],.0017,color)
 for x in [-.16,-.08,.08,.16]:box('Belt_Loop',(x,-.15*math.sqrt(max(.1,1-(x/.23)**2)),.926),(.012,.014,.031),color,.003)
 ell('Trouser_Button',(0,-.154,.93),(.009,.004,.009),'Metal',12,8)
def shoes(color,boot=False):
 for side in [-1,1]:
  x=side*.116
  loft('Shoe_Upper',[(.047,.073,.16,-.065),(.065,.073,.159,-.065),(.10,.069,.148,-.060),(.125,.060,.111,-.035),(.15,.052,.062,.006),(.23 if boot else .16,.051,.057,.012)],color,32).location.x=x
  loft('Shoe_Sole',[(.014,.068,.153,-.065),(.021,.075,.165,-.065),(.044,.075,.165,-.065),(.052,.071,.158,-.065)],'Black' if boot else 'Sole',32).location.x=x
  box('Shoe_Tongue',(x,-.078,.142),(.071,.015,.091 if boot else .064),color,.005)
  for i in range(5 if boot else 4):
   z=.095+i*.019;y=-.124+i*.013
   line('Shoe_Lace',[(x-.031,y,z),(x+.03,y-.003,z+.009)],.002,'Black' if boot else 'Cream')
   for s in [-1,1]:ell('Shoe_Eyelet',(x+s*.034,y,z),(.004,.003,.004),'Metal',10,6)
  for j in range(5):box('Sole_Tread',(x,-.19+j*.064,.012),(.115,.024,.008),'Black' if boot else 'Sole',.002)
  line('Shoe_Welt',[(x-.068,-.19,.047),(x-.073,-.05,.047),(x-.060,.055,.047),(x+.060,.055,.047),(x+.073,-.05,.047),(x+.068,-.19,.047)],.0018,color)

def top_details(style,color):
 if style in ('bomber','hoodie','track','security_f','police_f'):
  if style=='bomber':ellipse_line('Bomber_Collar',(0,0,1.485),.074,.068,.012,color)
  for s in [-1,1]:
   line('Slanted_Pocket',[(s*.145,-.12,1.04),(s*.117,-.142,1.13)],.004,'Orange' if style=='security_f' else color)
  if style not in ('hoodie',):
   line('Zipper',[(0,-.156,.94),(0,-.139,1.14),(0,-.153,1.32),(0,-.10,1.47)],.0024,'Orange' if style=='security_f' else 'Metal')
   box('Zipper_Pull',(.005,-.162,1.19),(.012,.006,.027),'Metal',.002)
 if style in ('denim','police_m','plaid'):
  for s in [-1,1]:
   box('Chest_Pocket',(s*.112,-.138,1.29),(.102,.014,.114),color,.005)
   box('Pocket_Flap',(s*.112,-.150,1.341),(.108,.012,.029),color,.003)
   ell('Pocket_Button',(s*.112,-.160,1.337),(.0055,.003,.0055),'Metal',12,8)
  for i in range(6):ell('Shirt_Button',(.027,-.145,1.02+i*.065),(.005,.003,.005),'Metal',12,8)
 if style=='denim':
  for s in [-1,1]:line('Denim_Stitch',[(s*.185,-.093,.95),(s*.178,-.103,1.16),(s*.20,-.11,1.37)],.0014,'Sand')
 if style=='hoodie':
  ell('Hood_Back',(0,.105,1.43),(.12,.084,.115),color,24,16)
  for s in [-1,1]:
   line('Hood_Drawstring',[(s*.065,-.086,1.45),(s*.060,-.16,1.35),(s*.057,-.16,1.24)],.003,'Cream')
   box('Cord_Tip',(s*.057,-.16,1.235),(.006,.008,.015),'Cream',.001)
  box('Kangaroo_Pocket',(0,-.15,1.055),(.25,.012,.10),color,.01)
 if style=='work':
  mesh('Overall_Bib',[(-.19,-.153,.95),(.19,-.153,.95),(-.135,-.155,1.28),(.135,-.155,1.28)],[(0,1,3,2)],'Sage')
  box('Bib_Pocket',(0,-.159,1.15),(.17,.015,.11),'Sage',.006)
  for s in [-1,1]:
   line('Overall_Strap',[(s*.10,-.155,1.23),(s*.13,-.12,1.39),(s*.115,0,1.46),(s*.10,.12,1.28)],.016,'Sage',8)
   box('Overall_Buckle',(s*.105,-.174,1.25),(.033,.008,.036),'Metal',.004)
 if style=='vest':
  loft('Padded_Vest',torso_rings(.021),'Navy',32,gap=.16,fold=.001)
  for j in range(7):
   z=.97+j*.065
   points=[]
   for i in range(33):
    a=-pi/2+.17+(2*pi-.34)*i/32
    rx=.222 if z<1.2 else .26
    points.append((rx*cos(a),.159*sin(a),z))
   line('Vest_Quilting',points,.003,'Navy',8)
  collar('Navy','jacket')
 if style=='track':
  for s in [-1,1]:
   # Paneles de color, construidos como superficies, sin textura descargada.
   obj=loft('Track_Panel',[(1.0,.211,.15,0),(1.17,.205,.145,0),(1.35,.253,.15,0)],'Green',32,gap=1.08)
   if s==1:obj.rotation_euler.z=pi
 if style=='cardigan':
  for i in range(5):ell('Cardigan_Button',(.035,-.15,1.02+i*.073),(.009,.004,.009),'Brown',12,8)
 if style=='plaid':
  # Rejilla en geometría compartida con el tejido; sin imagen proyectada.
  for z in [1.00,1.095,1.19,1.285,1.38]:
   for s in [-1,1]:line('Plaid_Horizontal',[(s*.035,-.158,z),(s*.10,-.143,z),(s*.17,-.111,z)],.009,'Sand',6)
  for x in [-.15,-.075,.075,.15]:line('Plaid_Vertical',[(x,-.143,.95),(x,-.141,1.14),(x,-.145,1.36)],.007,'Sand',6)

def duty(kind):
 female=kind.endswith('_f');guard=kind.startswith('security')
 color='Petrol' if guard and female else ('Charcoal' if guard else ('Navy' if female else 'Sky'))
 if kind=='security_m':
  loft('Security_Vest',torso_rings(.018),'Charcoal',32,gap=.018)
  for s in [-1,1]:
   box('Vest_FrontPouch',(s*.105,-.172,1.115),(.115,.055,.152),'Black',.009)
   box('Vest_PouchFlap',(s*.105,-.20,1.18),(.118,.015,.037),'Charcoal',.005)
   box('Vest_YellowPanel',(s*.145,-.14,1.387),(.105,.015,.043),'Mustard',.004)
  for z in [1.23,1.28,1.33]:line('Vest_Row',[(-.19,-.138,z),(-.10,-.17,z),(0,-.17,z),(.10,-.17,z),(.19,-.138,z)],.002,'Black')
  box('Security_ChestBadge',(.10,-.175,1.315),(.13,.013,.044),'Mustard',.002)
  label('Security_ChestText','SEGURIDAD',(.10,-.184,1.315),.017,'Black')
 if kind=='security_f':
  for s in [-1,1]:line('Orange_ChestTrim',[(s*.025,-.157,1.30),(s*.12,-.146,1.305),(s*.21,-.09,1.32)],.004,'Orange')
  label('Security_ChestText','SEGURIDAD',(.105,-.155,1.35),.014,'White')
 if not guard:
  for s in [-1,1]:
   box('Epaulette',(s*.15,-.015,1.475),(.105,.06,.015),'Navy',.003)
   ell('Epaulette_Button',(s*.115,-.02,1.485),(.006,.006,.003),'Metal',12,8)
  box('Police_ChestBadge',(.112,-.159,1.35),(.105,.012,.035),'Navy',.003)
  label('Police_ChestText','POLICIA',(.112,-.168,1.35),.018,'White')
  # Gorra con corona ajustada y visera curva.
  ell('Cap_Crown',(0,.006,1.815),(.119,.11,.075),'Navy',28,16)
  ell('Cap_Visor',(0,-.114,1.795),(.118,.096,.013),'Navy',28,8)
  label('Cap_Text','POLICIA',(0,-.101,1.838),.025,'White')
  for i in range(5):
   a=i*pi/2.5
   line('Cap_Seam',[(.117*cos(a),.006+.11*sin(a),1.80),(.09*cos(a),.006+.08*sin(a),1.86),(0,.006,1.89)],.0012,'Navy')
 # Cinturón y radio. Las referencias se modelan sin armas; las armas serán accesorios del sistema de juego.
 ellipse_line('Duty_Belt',(0,0,.965),.218,.153,.020,'Black')
 box('Belt_Buckle',(0,-.171,.963),(.062,.018,.044),'Metal',.005)
 box('Buckle_Inset',(0,-.182,.963),(.042,.004,.027),'Black',.003)
 for s in [-1,1]:box('Duty_Pouch',(s*.16,-.125,.957),(.06,.06,.093),'Black',.008)
 x=-.20 if female else .22;z=1.36 if female else .99;y=-.10 if female else -.025
 box('Radio',(x,y,z),(.055,.044,.095),'Black',.008)
 line('Radio_Antenna',[(x,y,z+.04),(x,y,z+.135)],.004,'Black')
 for j in range(4):box('Radio_Grille',(x,y-.024,z+.015-j*.009),(.036,.003,.003),'Metal',.001)
 ell('Radio_LED',(x+.014,y-.026,z+.034),(.003,.002,.003),'Green',10,6)
 if female:line('Radio_Cable',[(x,-.10,z-.04),(x*.78,-.14,z-.11),(x*.65,-.14,z-.23),(x,-.10,z-.06)],.003,'Black')
 label('Uniform_BackText','SEGURIDAD' if guard else 'POLICIA',(0,.165,1.355),.035,'White',True)

def fit_details(style):
 """Ajustar costuras y apliques a la superficie real, no a planos flotantes."""
 objects=list(ROOT.children_recursive)
 top=next(o for o in objects if o.name.startswith('Garment_Top_Continuous'))
 pants_obj=next(o for o in objects if o.name.startswith('Trouser_Continuous'))
 def tree(obj):
  return BVHTree.FromPolygons([obj.matrix_local@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])
 bpy.context.view_layer.update();tops=tree(top);bottom=tree(pants_obj)
 lines=('Front_Seam','Center_Seam','Zipper','Slanted_Pocket','Denim_Stitch','Plaid_','Orange_ChestTrim','Radio_Cable')
 for obj in objects:
  if obj.type!='MESH':continue
  key=obj.name.split('.')[0]
  if key in ('Trouser_Fold','Trouser_OuterSeam','Sleeve_Fold'):
   bpy.data.objects.remove(obj,do_unlink=True);continue
  if key.startswith(lines):
   for start in range(0,len(obj.data.vertices),6):
    vertices=list(obj.data.vertices)[start:start+6]
    p=sum((obj.matrix_local@v.co for v in vertices),Vector())/len(vertices)
    hit,_,_,_=tops.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)))
    if hit:
     for vert in vertices:vert.co.y+=hit.y-.0025-p.y
  if key=='Undershirt_Front':
   for vert in obj.data.vertices:
    p=obj.matrix_local@vert.co
    hit,_,_,_=tops.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)))
    if hit:
     p.y=hit.y-.0020
     vert.co=obj.matrix_local.inverted()@p
  if key=='Epaulette' or key=='Epaulette_Button':
   center=obj.location.copy();hit,_,_,_=tops.ray_cast(Vector((center.x,center.y,2)),Vector((0,0,-1)))
   if hit:obj.location.z=hit.z+(.008 if key=='Epaulette' else .020)
  if key in ('Chest_Pocket','Pocket_Flap','Pocket_Button','Police_ChestBadge','Police_ChestText','Security_ChestText','Radio','Radio_LED','Radio_Grille','Zipper_Pull','Shirt_Button','Cardigan_Button'):
   center=obj.location.copy()
   if center.length>0:
    hit,_,_,_=tops.ray_cast(Vector((center.x,-1,center.z)),Vector((0,1,0)))
    if hit:obj.location.y=hit.y-(.030 if key=='Radio' else .023 if key in ('Police_ChestText','Security_ChestText') else .010)
    if key=='Security_ChestText' and style=='security_m':obj.location.y=-.191
 if style=='police_f':
  bm=bmesh.new();bm.from_mesh(top.data)
  for co,no in [((0,0,1.345),(0,0,1)),((.07,0,0),(1,0,0)),((-.07,0,0),(1,0,0)),((.265,0,0),(1,0,0)),((-.265,0,0),(1,0,0)),((0,.015,0),(0,1,0))]:
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=co,plane_no=no,dist=.00001)
  bm.to_mesh(top.data);bm.free();top.data.update()
  top.data.materials.append(mat('Blue'));idx=len(top.data.materials)-1
  for face in top.data.polygons:
   c=face.center
   if (c.z>1.345 and abs(c.x)>.07) or (abs(c.x)>.265 and c.y<.015):face.material_index=idx
 if style=='track':
  top.data.materials.append(mat('Green'));idx=len(top.data.materials)-1
  for face in top.data.polygons:
   c=face.center
   if abs(c.x)>.24 or (c.z>1.34 and abs(c.x)>.09):face.material_index=idx
  for obj in list(ROOT.children_recursive):
   if obj.name.startswith('Track_Panel'):bpy.data.objects.remove(obj,do_unlink=True)
 if style=='plaid':
  top.data.materials.append(mat('Sand'));idx=len(top.data.materials)-1
  for face in top.data.polygons:
   p=face.center
   if ((p.x+.5)% .09)<.020 or ((p.z+.5)% .09)<.020:face.material_index=idx
  for obj in list(ROOT.children_recursive):
   if obj.name.startswith('Plaid_'):bpy.data.objects.remove(obj,do_unlink=True)
 # Tapar el nacimiento del pelo bajo la gorra y retirar mechones que la atraviesen.
 if style.startswith('police'):
  for obj in list(ROOT.children):
   if obj.name.startswith(('Hair_SweptLock','Cap_Seam')):bpy.data.objects.remove(obj,do_unlink=True)

SPECS=[
 ('01_Civil_Male_Bomber',False,'SkinTan','HairBrown','curls','Orange','Olive','White','bomber','cargo',False),
 ('02_Civil_Female_Denim',True,'SkinDark','HairBlack','afro','Denim','Sand','Petrol','denim','wide',False),
 ('03_Civil_Male_Turquoise',False,'SkinLight','HairBrown','wavy','Petrol','Sand','Mustard','shirt','shorts',False),
 ('04_Civil_Female_Lavender',True,'SkinWarm','HairBrown','braid','Lavender','Charcoal','Lavender','hoodie','jogger',False),
 ('05_Civil_Male_Burgundy',False,'SkinDark','HairBlack','cropped','Burgundy','Sole','Brown','jersey','chino',True),
 ('06_Civil_Female_Overalls',True,'SkinLight','Copper','wavy','Mustard','Sage','Sand','work','work',True),
 ('07_Civil_Male_PaddedVest',False,'SkinWarm','HairBlack','wavy','Mustard','Denim','Charcoal','vest','chino',True),
 ('08_Civil_Female_Tracksuit',True,'SkinTan','HairBlack','bob','Cream','Burgundy','Black','track','cargo',False),
 ('09_Civil_Male_Plaid',False,'SkinWarm','HairBlack','bun','Burgundy','Sand','Brown','plaid','chino',False),
 ('10_Civil_Female_Cardigan',True,'SkinLight','HairBrown','ponytail','Sky','Green','Brown','cardigan','skort',True),
 ('11_Security_Male',False,'SkinDark','HairBlack','curls','Charcoal','Black','Black','security_m','uniform',True),
 ('12_Security_Female',True,'SkinWarm','HairBrown','bun','Petrol','Petrol','Black','security_f','uniform',True),
 ('13_Police_Male',False,'SkinTan','HairBlack','cropped','Sky','Navy','Black','police_m','uniform',True),
 ('14_Police_Female',True,'SkinLight','HairBrown','bun','Navy','Navy','Black','police_f','uniform',True),
]
def begin(name):
 global COL,ROOT
 if bpy.data.objects.get(name):raise RuntimeError('Ya existe '+name+'; no sobrescribir una revisión')
 COL=bpy.data.collections.new(name+'_Parts');bpy.context.scene.collection.children.link(COL)
 ROOT=bpy.data.objects.new(name,None);COL.objects.link(ROOT)
 ROOT['ReferenceRevision']='Alain 2026-10-31';ROOT['RigStatus']='Awaiting Mixamo rig and weight transfer';ROOT['VisualApproval']='Pending'
 return ROOT
def setup():
 if SCENE_NAME not in bpy.data.scenes:
  scene=bpy.data.scenes.new(SCENE_NAME);scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 else:scene=bpy.data.scenes[SCENE_NAME]
 bpy.context.window.scene=scene
 scene.render.resolution_x=1100;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
 scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
 shade=scene.display.shading;shade.color_type='MATERIAL';shade.light='STUDIO';shade.show_specular_highlight=False;shade.show_cavity=False
 if scene.world is None:scene.world=bpy.data.worlds.new('NPC2_StudioWorld')
 shade.background_type='WORLD';scene.world.color=(.25,.25,.25)
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    shade=area.spaces.active.shading;shade.color_type='MATERIAL';shade.light='STUDIO';shade.show_cavity=False;shade.cavity_type='BOTH';shade.show_specular_highlight=False
    shade.cavity_ridge_factor=.6;shade.cavity_valley_factor=.65;shade.curvature_ridge_factor=.5;shade.curvature_valley_factor=.5
    area.spaces.active.overlay.show_overlays=False
 return scene
def base(female):
 global SKIN,FEMALE
 FEMALE=female;SKIN='SkinLight'
 name='NPC2_BaseFemale_APose' if female else 'NPC2_BaseMale_APose'
 if bpy.data.objects.get(name):return bpy.data.objects[name]
 root=begin(name);parts=anatomy(female);body=unify_body(parts,name+'_Skin')
 root['BaseHeightMeters']=1.839;root['RestPose']='A pose'
 return root
def tpose_base(female):
 global SKIN,FEMALE
 FEMALE=female;SKIN='SkinLight'
 name='NPC2_BaseFemale_TPose' if female else 'NPC2_BaseMale_TPose'
 root=bpy.data.objects.get(name)
 if root:return root
 root=begin(name);parts=anatomy(female,tpose=True);unify_body(parts,name+'_Skin')
 root['RestPose']='T pose for Mixamo';root['BodyHeightMeters']=1.839
 export(root)
 for obj in [root]+list(root.children_recursive):obj.hide_set(True)
 return root
def build(index):
 global SKIN,FEMALE
 setup();spec=SPECS[index-1]
 name,FEMALE,SKIN,hair,hstyle,top,bottom,shoe,style,pkind,boot=spec
 source=base(FEMALE)
 # base() establece temporalmente el color de piel.
 SKIN=spec[2]
 root=begin('NPC2_'+name)
 for original in source.children:
  if original.type=='MESH':
   obj=original.copy();obj.data=original.data.copy();COL.objects.link(obj);obj.parent=root;obj.name='Skin_'+name
   # Ocultar la piel cubierta evita intersecciones; los cuerpos cerrados originales se conservan para el rig.
   bm=bmesh.new();bm.from_mesh(obj.data)
   long=style not in ('shirt','work','police_m','security_m')
   def exposed(v):
    x,y,z=v.co
    if z>1.54 or (z>1.47 and abs(x)<.085):return True
    if abs(x)>.26:
     side=1 if x>0 else -1;points=arm_points(side)
     d=Vector(points[-1])-Vector(points[0]);t=(v.co-Vector(points[0])).dot(d)/d.length_squared
     return t>(.94 if long else .52)
    if pkind in ('shorts','skort'):return .15<z<.51
    return False
   bmesh.ops.delete(bm,geom=[v for v in bm.verts if not exposed(v)],context='VERTS');bm.to_mesh(obj.data);bm.free()
   obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=mat(SKIN)
 face(hair,index);hair_cap(hair,hstyle)
 shirt(top,long=style not in ('shirt','work','police_m','security_m'),open_front=style in ('bomber','denim','shirt','plaid','cardigan'),style='shirt' if style in ('shirt','denim','plaid','police_m','security_m') else 'crew')
 pants(bottom,pkind);shoes(shoe,boot);top_details(style,top)
 if style.startswith(('security','police')):duty(style)
 fit_details(style)
 if index==10:
  random.seed(10)
  for side in [-1,1]:
   for i in range(9):ell('Freckle',(side*(.049+random.uniform(-.02,.026)),-.083,1.66+random.uniform(-.009,.01)),(.0014,.0008,.0012),'Brown',8,6)
 if FEMALE:root.scale=(.935,.935,.935)
 root['ReferenceFile']=spec[0][:2]+'_'+('seguridad' if style.startswith('security') else 'policia' if style.startswith('police') else 'civil')+'_'+('mujer' if FEMALE else 'hombre')+'.png'
 root['Role']='Security' if style.startswith('security') else 'Police' if style.startswith('police') else 'Civilian'
 root['Weapons']='None in reference model; attach gameplay equipment separately'
 bpy.context.view_layer.update()
 for obj in [source]+list(source.children_recursive):obj.hide_set(True)
 frame(root)
 print('NPC2_BUILT',root.name,len(root.children_recursive),'parts')
 return root
def frame(root,view='three_quarter'):
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':obj.hide_set(obj not in root.children_recursive)
 scene=bpy.context.scene
 camera=scene.camera
 if not camera:
  data=bpy.data.cameras.new('NPC2_ReviewCamera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
 camera.data.type='ORTHO';camera.data.ortho_scale=2.13
 center=root.location+Vector((0,0,.90))
 directions={'front':(0,-5,.18),'right':(5,0,.18),'back':(0,5,.18),'three_quarter':(3,-6,.8)}
 camera.location=center+Vector(directions[view]);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
def export(root):
 scene=bpy.context.scene
 old_location=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');saved=[];temp=[]
 for obj in [root]+list(root.children_recursive):
  saved.append((obj,obj.hide_get()));obj.hide_set(False);obj.select_set(True)
  if obj.type=='MESH':
   data=obj.data;slots=[(s.link,s.material) for s in obj.material_slots];copy=data.copy();obj.data=copy;copy.materials.clear()
   for _,m in slots:copy.materials.append(m)
   for s in obj.material_slots:s.link='DATA'
   temp.append((obj,data,copy,slots))
 bpy.context.view_layer.objects.active=root
 folder=ART/'Characters/ReferenceV2';folder.mkdir(parents=True,exist_ok=True);path=folder/(root.name+'.fbx')
 try:bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False)
 finally:
  for obj,data,copy,slots in temp:
   obj.data=data
   for slot,(link,m) in zip(obj.material_slots,slots):
    slot.link=link
    if link=='OBJECT':slot.material=m
   bpy.data.meshes.remove(copy)
  for obj,hidden in saved:obj.hide_set(hidden)
  root.location=old_location
 return str(path)
def gallery():
 scene=bpy.data.scenes[SCENE_NAME];bpy.context.window.scene=scene
 roots=[bpy.data.objects['NPC2_'+s[0]] for s in SPECS]
 for i,root in enumerate(roots):
  root.location=((i%7)*1.6,(i//7)*2.4,0)
  for obj in [root]+list(root.children_recursive):obj.hide_set(False);obj.hide_render=False
 for root in [o for o in scene.objects if o.type=='EMPTY' and o.name.startswith('NPC2_Base')]:
  for obj in [root]+list(root.children_recursive):obj.hide_set(True);obj.hide_render=True
 camera=scene.camera;center=Vector((4.8,1.2,.9))
 camera.location=center+Vector((3,-12,5));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.data.ortho_scale=12
 scene.render.resolution_x=1700;scene.render.resolution_y=1000
 bpy.context.view_layer.update()
def studio():
 scene=bpy.data.scenes[SCENE_NAME]
 if not bpy.data.objects.get('NPC2_StudioFloor'):
  data=bpy.data.meshes.new('NPC2_StudioFloor_Mesh')
  data.from_pydata([(-12,-12,-.018),(22,-12,-.018),(22,18,-.018),(-12,18,-.018)],[],[(0,1,2,3)])
  obj=bpy.data.objects.new('NPC2_StudioFloor',data);scene.collection.objects.link(obj);data.materials.append(mat('Cream'))
 for name,location,power,size in [('Key',(2,-4,7),650,7),('Fill',(11,-1,5),400,6),('Rim',(4,7,6),800,6)]:
  key='NPC2_Studio'+name
  if bpy.data.objects.get(key):continue
  data=bpy.data.lights.new(key,'AREA');data.energy=power;data.shape='DISK';data.size=size
  obj=bpy.data.objects.new(key,data);scene.collection.objects.link(obj);obj.location=location
  obj.rotation_euler=(Vector((4.8,1.2,.9))-obj.location).to_track_quat('-Z','Y').to_euler()
 scene.world.use_nodes=True
 node=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
 node.inputs['Color'].default_value=(.45,.45,.45,1);node.inputs['Strength'].default_value=.35
 transforms=[e.identifier for e in scene.view_settings.bl_rna.properties['view_transform'].enum_items]
 if 'AgX' in transforms:scene.view_settings.view_transform='AgX'
 scene.view_settings.exposure=-.3
 floor=bpy.data.objects['NPC2_StudioFloor'];floor.hide_set(False);floor.hide_render=False
def save():
 scene=bpy.data.scenes[SCENE_NAME]
 native=ART/'BlenderSources~/Alarma_Characters_ReferenceV2.blend'
 bpy.data.libraries.write(str(native),{scene},fake_user=True)
 catalog=[]
 for root in scene.objects:
  if root.type=='EMPTY' and root.name.startswith('NPC2_'):
   meshes=[o for o in root.children_recursive if o.type=='MESH']
   catalog.append({'name':root.name,'file':str(ART/'Characters/ReferenceV2'/(root.name+'.fbx')),'meshes':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in m.data.polygons) for m in meshes),'rig':'pending Mixamo','approval':'pending'})
 (ART/'BlenderScripts/npc_v2_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
 (OUT/'Catalogo.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
 palette={'colors':[{'name':'NPC2_'+k,'hex':v} for k,v in COLORS.items()]}
 (ART/'Materials/NPC2_Palette.json').write_text(json.dumps(palette,indent=2),encoding='utf-8')
 print('NPC2_SAVED',len(catalog),str(native))
