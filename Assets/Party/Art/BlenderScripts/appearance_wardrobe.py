"""Cabello y prendas propios derivados de la base humana, sin modelos descargados."""
import bpy,bmesh,math,random
from mathutils import Vector,noise
import appearance_female as af
from math import sin,cos,pi
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def fabric(name,color):return af.material(name,color,.82,True)
def shell(name,predicate,mat,offset=.008,clip=None,opening=None):
 source=bpy.data.objects['AF_Body'];obj=source.copy();obj.data=source.data.copy();obj.name='AF_'+name
 bpy.context.scene.collection.objects.link(obj);obj.parent=af.ROOT;obj.data.materials.clear();obj.data.materials.append(mat)
 obj.hide_render=False;obj.hide_set(False)
 for m in list(obj.modifiers):obj.modifiers.remove(m)
 bm=bmesh.new();bm.from_mesh(obj.data)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if not predicate(f.calc_center_median())],context='FACES')
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.normal_update()
 for v in bm.verts:v.co+=v.normal*offset
 if clip is not None:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,clip),plane_no=(0,0,1),clear_inner=True,dist=.00001)
 if opening:
  for x in [-opening,opening]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(x,0,0),plane_no=(1,0,0),dist=.00001)
  bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.calc_center_median().x)<opening-.00001 and f.calc_center_median().y<0],context='FACES')
  bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 bm.normal_update();bm.to_mesh(obj.data);bm.free()
 for p in obj.data.polygons:p.use_smooth=True
 rig=obj.modifiers.new('Diagnostic garment skin','ARMATURE');rig.object=bpy.data.objects['AF_DiagnosticRig'];rig.use_deform_preserve_volume=True
 solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.0018;solid.offset=0
 return obj
def front_panel(name,points,bvh,mat):
 verts=[(x,af.front_y(bvh,x,z,.0025),z) for x,z in points]
 obj=af.mesh(name,verts,[tuple(range(len(verts)))],mat)
 solid=obj.modifiers.new('Panel thickness','SOLIDIFY');solid.thickness=.001
 return obj
def seam(name,points,bvh,mat,r=.0007):return af.curve(name,[(x,af.front_y(bvh,x,z,.0032),z) for x,z in points],r,mat)
def wardrobe():
 af.ROOT=bpy.data.objects['AF_CharacterRoot']
 denim=fabric('Denim','385D7D');coral=fabric('CoralCotton','BB6256');sand=fabric('BeigeTwill','BDAF93');thread=fabric('Thread','A7A18D');darkthread=fabric('DenimThread','A0A9AC')
 metal=af.material('Metal','90918A',.35);shader=next(n for n in metal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Metallic'].default_value=.8
 tee=shell('CoralTop',lambda p:1.055<p.z<1.438 and abs(p.x)<.189,coral,.005,1.05)
 jacket=shell('DenimJacket',lambda p:(1.055<p.z<1.445 and abs(p.x)<.215) or (p.z>1.025 and p.z<1.44 and abs(p.x)>=.215),denim,.018,1.075,.060)
 pants=shell('WideTrousers',lambda p:p.z<1.085 and abs(p.x)<.265,sand,.010,.105)
 # Ampliar las piernas del pantalón respecto al eje de cada pierna, manteniendo el ajuste de la cintura.
 for v in pants.data.vertices:
  x,y,z=v.co
  if z<.88:
   side=1 if x>0 else -1
   cx=side*(.158 if z<.2 else .158-(z-.2)*.09)
   radii=[(.115,.035),(.15,.034),(.24,.046),(.34,.061),(.43,.057),(.465,.052),(.55,.068),(.67,.084),(.78,.095),(.88,.105)]
   radius=radii[-1][1]
   for (za,ra),(zb,rb) in zip(radii,radii[1:]):
    if z<=zb:radius=ra+(rb-ra)*max(0,min(1,(z-za)/(zb-za)));break
   target=.106+.004*sin(pi*max(0,min(1,(z-.105)/.775)))
   ycenter=0 if z<.36 else -.020*math.exp(-((z-.465)/.060)**2)
   angle=math.atan2(y-ycenter,x-cx)
   blend=1-smooth(.74,.88,z)
   v.co.x=x*(1-blend)+(cx+target*cos(angle))*blend
   if x>.003:v.co.x=max(.003,v.co.x)
   elif x<-.003:v.co.x=min(-.003,v.co.x)
   else:v.co.x=x
   v.co.y=y*(1-blend)+(.005+target*.98*sin(angle))*blend
   v.co.y+=.0012*sin(z*53+angle*4)*(1-smooth(.72,.88,z))
  if y>0 and .76<z<1.04 and abs(x)<.21:
   rear=.148*math.sqrt(max(0,1-(x/.225)**2))
   v.co.y+=max(0,rear-v.co.y)*math.exp(-((z-.88)/.105)**2)
 bm=bmesh.new();bm.from_mesh(pants.data)
 patch=[v for v in bm.verts if .77<v.co.z<.91 and abs(v.co.x)<.055]
 for _ in range(6):bmesh.ops.smooth_vert(bm,verts=patch,factor=.55,use_axis_x=True,use_axis_y=True,use_axis_z=True)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(pants.data);bm.free()
 pants.data.update();jacket.data.update();j=af.surface(jacket);p=af.surface(pants)
 # Solapas, bolsillos y costuras de la chaqueta.
 for s in [-1,1]:
  front_panel('DenimCollar',[(s*.056,1.435),(s*.114,1.389),(s*.078,1.350),(s*.038,1.417)],j,denim)
  x=s*.116
  points=[(x-.034,1.292),(x+.034,1.292),(x+.033,1.235),(x,1.225),(x-.033,1.235)]
  front_panel('ChestPocket',points,j,denim)
  seam('PocketStitch',[(x-.029,1.285),(x-.029,1.24),(x,1.231),(x+.029,1.24),(x+.029,1.285)],j,darkthread,.00045)
  front_panel('PocketFlap',[(x-.036,1.294),(x+.036,1.294),(x+.030,1.275),(x,1.268),(x-.030,1.275)],j,denim)
  af.ell('PocketSnap',(x,af.front_y(j,x,1.280,.005),1.280),(.0032,.0013,.0032),metal,20,10)
  seam('JacketEdge',[(s*.064,z) for z in [1.083+i*.32/35 for i in range(36)]],j,darkthread,.00055)
  # Costura delantera del pantalón y boca del bolsillo.
  seam('TrouserPocket',[(s*.062,1.068),(s*.09,1.043),(s*.132,1.012)],p,thread,.00065)
  seam('TrouserPleat',[(s*(.11+.05*(.8-z)),z) for z in [.80-i*.65/35 for i in range(36)]],p,sand,.0007)
 for z in [1.10,1.17,1.24,1.31,1.38]:
  x=-.067;af.ell('JacketButton',(x,af.front_y(j,x,z,.006),z),(.0033,.0015,.0033),metal,20,10)
 # Borde del cuello de la camiseta y puños doblados de denim.
 af.curve('TopNeckline',[(.057*cos(2*pi*i/64),.052*sin(2*pi*i/64),1.442+.007*sin(2*pi*i/64)) for i in range(65)],.0026,coral)
 for s in [-1,1]:
  center=Vector((s*.317,-.015,1.102));d=Vector((s*.07,-.014,-.20)).normalized();u=d.cross(Vector((0,1,0))).normalized();v=d.cross(u).normalized()
  af.curve('RolledCuff',[center+(u*cos(2*pi*i/64)+v*sin(2*pi*i/64))*.063 for i in range(65)],.006,denim)
 seam('TrouserFly',[(.007,z) for z in [1.075,1.045,1.012,.976]],p,thread,.0006)
 # Calzado con la forma de los pies de la base, suela y cordones pequeños.
 petrol=fabric('SneakerPetrol','234451');sole=af.material('ShoeSole','C8C4B5',.85)
 shoe=shell('Sneakers',lambda p:p.z<.151,petrol,.008)
 for v in shoe.data.vertices:
  if v.co.z<.035:v.co.z=.018
 shoe.data.update();shoe_surface=af.surface(shoe)
 for s in [-1,1]:
  center=s*.17
  points=[(center+.058*cos(2*pi*i/64),-.075+.14*sin(2*pi*i/64),.032) for i in range(65)]
  af.curve('ShoeWelt',points,.006,sole)
  for i in range(5):
   y=-.13+i*.015;z=.084+i*.009
   af.curve('ShoeLace',[(center-.026,y,z),(center+.026,y-.004,z+.004)],.0012,sole)
 return jacket,pants
def hair():
 af.ROOT=bpy.data.objects['AF_CharacterRoot'];mat=af.material('Hair','281F1B',.78,True)
 head=bpy.data.objects['AF_Body'];head_surface=af.surface(head)
 verts=[];count=128;steps=28
 for j in range(steps):
  t=j/(steps-1);theta=pi/2*t
  for i in range(count):
   a=2*pi*i/count;low=1.620+.070*max(0,-sin(a))-.050*max(0,sin(a))+.0015*sin(7*a)
   p=Vector((.096*cos(a)*cos(theta),.008+.087*sin(a)*cos(theta),low+(1.734-low)*sin(theta)))
   outward=(p-Vector((0,.008,1.64))).normalized()
   hit,normal,_,_=head_surface.ray_cast(p+outward*.3,-outward)
   verts.append(hit+normal*.002 if hit else p)
 faces=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(steps-1) for i in range(count)]
 obj=af.mesh('HairCap',verts,faces,mat);cap=af.surface(obj)
 parts=[obj]
 puff=af.ell('CurlyBun',(0,.047,1.765),(.072,.067,.070),mat,48,30)
 for v in puff.data.vertices:
  d=v.co-Vector((0,.047,1.765));v.co+=d.normalized()*.0035*noise.noise(v.co*140)
 parts.append(puff)
 random.seed(212)
 # Rizos finos sobre un volumen continuo; no esferas separadas o huecos en el moño.
 curves=bpy.data.curves.new('AF_DenseCurls','CURVE');curves.dimensions='3D';curves.bevel_depth=.00055;curves.bevel_resolution=1;curves.materials.append(mat)
 curlobj=bpy.data.objects.new('AF_DenseCurls',curves);bpy.context.scene.collection.objects.link(curlobj);curlobj.parent=af.ROOT;parts.append(curlobj)
 for i in range(3500):
  u=random.uniform(0,2*pi);z=random.uniform(-.85,1);r=math.sqrt(1-z*z)
  n=Vector((r*cos(u),r*sin(u),z));center=Vector((n.x*.073,n.y*.068+.047,n.z*.071+1.765))
  t=n.cross(Vector((0,0,1)))
  if t.length<.1:t=n.cross(Vector((1,0,0)))
  t.normalize();b=n.cross(t).normalized();radius=random.uniform(.0018,.0032)
  points=[]
  for k in range(13):
   a=k*2*pi*1.35/12
   points.append(center+(t*cos(a)+b*sin(a))*radius+n*(.0005+k*.0001))
  spline=curves.splines.new('POLY');spline.points.add(len(points)-1)
  for point,co in zip(spline.points,points):point.co=(*co,1)
 # Direcciones del cabello recogido, apoyadas sobre el casquete.
 for i in range(30):
  x=-.075+i*.15/29;points=[]
  for k in range(20):
   angle=-pi/2+pi*k/19
   p=Vector((x*.95,.008+.083*sin(angle),1.64+.10*cos(angle)))
   outward=(p-Vector((0,.008,1.64))).normalized()
   hit,normal,_,_=cap.ray_cast(p+outward*.30,-outward)
   if hit:points.append(hit+normal*.00035)
  if len(points)>2:parts.append(af.curve('SweptHair',points,.00016,mat))
 for s in [-1,1]:
  points=[]
  for i in range(50):
   t=i/49;x=s*(.075+.002*cos(t*9*pi));z=1.635-.09*t;points.append((x,af.front_y(head_surface,x,z,.003)+.0015*sin(t*9*pi),z))
  parts.append(af.curve('TempleCurl',points,.00065,mat))
 bpy.context.view_layer.update()
 for o in parts:af.head_parent(o)
 gold=af.material('EarringGold','C2A65E',.25);shader=next(n for n in gold.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Metallic'].default_value=.85
 for s in [-1,1]:
  points=[(s*.086,-.002+.008*cos(2*pi*i/40),1.585+.009*sin(2*pi*i/40)) for i in range(41)]
  o=af.curve('Earring',points,.0009,gold);bpy.context.view_layer.update();af.head_parent(o)
def finish_materials():
 for name,color in [('Iris','3D2B20'),('Sclera','BDB7AA'),('Lips','754935')]:
  m=bpy.data.materials['AF_'+name];node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(*af.rgb(color),1)
  if name=='Iris':node.inputs['Roughness'].default_value=.28;node.inputs['Coat Weight'].default_value=.35;node.inputs['Coat Roughness'].default_value=.08
  if name=='Lips':node.inputs['Roughness'].default_value=.60
 for o in bpy.context.scene.objects:
  if o.name.startswith('AF_Eyebrow') and o.type=='CURVE':o.data.bevel_depth=.00065
 m=bpy.data.materials['AF_Hair'];n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*af.rgb('1B1412'),1);n.inputs['Specular IOR Level'].default_value=.22
def mask_covered_skin():
 """Conservar el cuerpo completo oculto y mostrar solo piel que no está cubierta por prendas."""
 source=bpy.data.objects['AF_Body'];old=bpy.data.objects.get('AF_VisibleSkin')
 if old:bpy.data.objects.remove(old,do_unlink=True)
 obj=source.copy();obj.data=source.data.copy();obj.name='AF_VisibleSkin';bpy.context.scene.collection.objects.link(obj);obj.parent=af.ROOT
 obj.hide_render=False;obj.hide_set(False)
 bm=bmesh.new();bm.from_mesh(obj.data)
 keep=lambda p:p.z>1.435 or (abs(p.x)>.285 and p.z<1.075)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f.calc_center_median())],context='FACES')
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(obj.data);bm.free()
 source.hide_render=True;source.hide_set(True)
 obj['Purpose']='Visible skin only; full approved body preserved in hidden AF_Body'
 return obj
