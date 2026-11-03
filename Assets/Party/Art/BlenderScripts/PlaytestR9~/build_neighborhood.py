"""Ciudad 3 km y barrio funcional coherente: una sola referencia espacial para geometría, puertas y tareas."""
import bpy,bmesh,json,math,sys,collections
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parent;R6=sources9.r6();R8=sources9.r8();R7=sources9.r7();sys.path.insert(0,str(R6));from mesh_tools import Batch,palette
HALF=1500;FLOOR=.20;D=12;W=16
SPECS=[('Hideout',(-240,-290),'EL ESCONDITE','',9),('Minimarket',(-215,-290),'MINI TODO · MERCADO','MilkCarton',9),('MallJewelry',(-190,-290),'BRILLA · JOYERIA','JewelryBox',7),('Restaurant',(-215,-265),'CAFE PANICO','CoffeeCup',3),('Clothing',(-190,-265),'BUENA PINTA · ROPA','FoldedShirt',5),('FenceGear',(-190,-240),'DON TRUEQUE · EQUIPO','ToolKit',8)]
CLEAR=[(c[0]-11,c[1]-12,c[0]+11,c[1]+8) for _,c,*_ in SPECS]+[(-251,-305,-179,-297),(-226,-280,-179,-272),(-201,-255,-179,-247),(-179,-305,-173,-232)]
COLORS={'cream':'E9DFC9','white':'F5F1E8','denim':'4A6FA5','coral':'DC7662','teal':'3F888D','gold':'D6AF52','wood':'AD805A','dark':'253C46','metal':'8C9EA4','glass':'91D4DE','floor':'C8CCC4','green':'759864','milk':'E9E9DC','red':'CE5852','blue':'477EB1','purple':'9E82B8','asphalt':'52616A'}
bpy.ops.wm.open_mainfile(filepath=str(R6/'Villa_Alarma_Compras_R6.blend'));scene=bpy.context.scene;scene.frame_set(1);root=bpy.data.objects['VillaAlarma_4000m'];root.name='VillaAlarma_3000m';palette(COLORS)
for m in list(bpy.data.materials):
    if m.name.startswith('City4_glass') and m.use_nodes:
        node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Alpha'].default_value=.22
removed=set();changed=set();drop=[];old=json.loads((R8/'world.json').read_text(encoding='utf-8'));original={p['source']:(c['id'],p['node']) for c in old['cells'] for p in c['parts']};print('R9_SOURCE_LOADED',flush=True)
def corners(o):return [o.matrix_world@Vector(p) for p in o.bound_box]
def bounds(o):
    ps=corners(o);return Vector(tuple(min(p[k] for p in ps) for k in range(3))),Vector(tuple(max(p[k] for p in ps) for k in range(3)))
# Elimina los cuatro comercios trasladados y su escondite anterior, más la zona que se reconstruirá.
for identifier in ['Hideout','Minimarket','MallJewelry','Restaurant','Clothing','FenceGear']:
    obj=bpy.data.objects.get('R2_Hero_'+identifier)
    if obj:
        for o in list(obj.children_recursive)+[obj]:removed.add(o.name);bpy.data.objects.remove(o,do_unlink=True)
for obj in list(root.children_recursive):
    if obj.type!='MESH':continue
    lo,hi=bounds(obj);role=obj.get('MapRole','')
    overlap=any(hi.x>r[0] and lo.x<r[2] and hi.y>r[1] and lo.y<r[3] for r in CLEAR)
    small=max(hi.x-lo.x,hi.y-lo.y)<120
    if hi.x<=-HALF or lo.x>=HALF or hi.y<=-HALF or lo.y>=HALF or (overlap and small and role not in ['Ground','Roads','Sidewalks','Markings','Water']):
        removed.add(obj.name);drop.append(obj);continue
    if overlap and not small and role in ['potted_foliage','planter_rim','garden','detailed_grass','business_landscape','landscape']:
        obj.data=obj.data.copy();bm=bmesh.new();bm.from_mesh(obj.data)
        unwanted=[f for f in bm.faces if any(r[0]<(obj.matrix_world@f.calc_center_median()).x<r[2] and r[1]<(obj.matrix_world@f.calc_center_median()).y<r[3] for r in CLEAR)]
        bmesh.ops.delete(bm,geom=unwanted,context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(obj.data);bm.free();changed.add(obj.name)
    # Los pequeños elementos no se cortan por la mitad en el borde del mundo.
    if min(lo.x,lo.y)<-HALF or max(hi.x,hi.y)>HALF:
        if max(hi.x-lo.x,hi.y-lo.y)<100:
            removed.add(obj.name);drop.append(obj);continue
        obj.data=obj.data.copy();bm=bmesh.new();bm.from_mesh(obj.data);inv=obj.matrix_world.inverted()
        for position,normal in [(Vector((-HALF,0,0)),Vector((1,0,0))),(Vector((HALF,0,0)),Vector((-1,0,0))),(Vector((0,-HALF,0)),Vector((0,1,0))),(Vector((0,HALF,0)),Vector((0,-1,0)))]:
            local=inv@position;n=obj.matrix_world.to_3x3().transposed()@normal;bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=local,plane_no=n,clear_inner=True,dist=.001)
        bm.to_mesh(obj.data);bm.free();obj.data.update();changed.add(obj.name)
bpy.data.batch_remove(ids=tuple(drop));print('R9_CROPPED',len(drop),len(changed),flush=True)
for collection in list(bpy.data.collections):
    if collection.name.startswith(('LifeR5_Animated','LifeR6_Animated')):
        for o in list(collection.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(collection)
def emit(name,batch,parent,role='detailed_interior'):
    obj=bpy.data.objects.new(name,batch.data(name));scene.collection.objects.link(obj);obj.parent=parent;obj['MapRole']=role;return obj
def box(batch,p,size,c):batch.box(p,size,c)
def sign(batch,text,p,size=.35,color='white'):batch.text(text,p,size,color)
def sofa(b,x,y):
    box(b,(x,y,.43),(3,1,.6),'denim');box(b,(x,y+.4,.9),(3,.22,.8),'denim')
    for xx in [-1.45,1.45]:box(b,(x+xx,y,.75),(.22,1,.6),'wood')
def shelf(b,x,y,kind):
    if kind=='MallJewelry':
        box(b,(x,y,.49),(2.1,1.1,.98),'wood');box(b,(x,y,1),(2.15,1.1,.06),'dark')
        for dx in [-.6,.6]:b.ico((x+dx,y,1.13),(.14,.10,.16),'gold',1)
        return
    for side in [-1,1]:box(b,(x+side*1.05,y,.85),(.08,.65,1.7),'wood')
    for row,z in enumerate([.18,.67,.99,1.55]):
        box(b,(x,y,z),(2.12,1.1 if row==2 else .65,.06),'wood')
        for i,dx in enumerate([-.75,-.38,.38,.75]):
            color=['milk','red','blue','gold'][i]
            if kind=='Clothing':
                for j in range(3):box(b,(x+dx,y,z+.04+j*.06),(.27,.23,.055),['coral','denim','teal'][(i+j)%3])
            elif kind=='FenceGear':
                box(b,(x+dx,y,z+.105),(.28,.17,.18),'teal');box(b,(x+dx,y,z+.215),(.12,.035,.035),'dark')
            elif kind=='Restaurant':
                b.cyl((x+dx,y,z+.12),.085,.21,'white',10);b.cyl((x+dx,y,z+.23),.08,.01,'dark',10)
            elif row==0:b.cyl((x+dx,y,z+.12),.085,.20,color,10)
            elif row==1:b.ico((x+dx,y,z+.13),(.14,.10,.08),'gold',1)
            else:
                box(b,(x+dx,y,z+.15),(.18,.14,.28),color);box(b,(x+dx,y-.074,z+.15),(.13,.008,.08),'white')
    if kind=='Minimarket':sign(b,'ALIMENTOS',(x,y-.34,1.88),.18,'teal')

def product(b,kind,p=(0,0,0)):
    x,y,z=p
    if kind=='MilkCarton':
        box(b,(x,y,z+.13),(.15,.13,.26),'milk');box(b,(x,y-.067,z+.12),(.13,.006,.09),'blue');b.cyl((x+.04,y,z+.275),.027,.025,'blue',8)
    elif kind=='CoffeeCup':
        b.cyl((x,y,z+.10),.085,.20,'white',12,top=.10);b.cyl((x,y,z+.205),.10,.012,'dark',12);box(b,(x+.115,y,z+.11),(.07,.035,.11),'white')
    elif kind=='JewelryBox':
        box(b,(x,y,z+.04),(.25,.20,.08),'purple');b.cyl((x,y,z+.095),.045,.025,'gold',10);b.ico((x,y,z+.125),(.035,.035,.045),'glass',1)
    elif kind=='FoldedShirt':
        box(b,(x,y,z+.045),(.27,.23,.09),'coral');box(b,(x,y-.015,z+.098),(.08,.04,.014),'white')
    elif kind=='ToolKit':
        box(b,(x,y,z+.09),(.30,.17,.18),'teal');box(b,(x,y,z+.20),(.13,.03,.035),'dark')
    elif kind=='CashNote':box(b,(x,y,z+.004),(.20,.09,.008),'green')
    elif kind=='Receipt':box(b,(x,y,z+.003),(.08,.15,.006),'white')
for identifier,centre,label,kind,staff in SPECS:
    parent=bpy.data.objects.new('R9_Hero_'+identifier,None);scene.collection.objects.link(parent);parent.parent=root;parent.location=(*centre,0)
    shell=Batch();box(shell,(0,0,.10),(W,D,.20),'floor')
    for x in [-W/2,W/2]:box(shell,(x,0,2.1),(.22,D,3.8),'cream')
    box(shell,(0,D/2,2.1),(W,.22,3.8),'cream')
    for x in [-4.7,4.7]:
        box(shell,(x,-D/2,.45),(6.6,.16,.50),'wood');box(shell,(x,-D/2,1.75),(6.6,.045,2.15),'glass')
    for x in [-W/2,-1.25,1.25,W/2]:box(shell,(x,-D/2,1.65),(.12,.18,2.9),'dark')
    box(shell,(0,-D/2,3.35),(W,.24,1.1),'teal' if identifier!='MallJewelry' else 'dark');sign(shell,label,(0,-6.14,3.4),.43)
    emit(parent.name+'_Shell',shell,parent,'hero_shell')
    roof=Batch();box(roof,(0,0,4.05),(W+.4,D+.4,.22),'cream');emit(parent.name+'_Roof',roof,parent,'removable_roof')
    furniture=Batch()
    if identifier=='Hideout':
        sofa(furniture,-3,3.6);box(furniture,(-3,1.7,.45),(2.5,1.1,.12),'wood')
        box(furniture,(3.4,4.4,1.35),(5,.28,2.3),'dark');sign(furniture,'NUESTRO PRÓXIMO GOLPE',(3.4,4.22,2.1),.27,'gold')
        for x in [1.8,3.4,5]:box(furniture,(x,4.19,1.3),(1.2,.03,.75),'cream')
        for x in [-6,-5.2,-4.4,-3.6]:box(furniture,(x,5.35,1.15),(.7,.65,1.9),'teal')
        box(furniture,(4,-3.8,.5),(3,1.1,1),'wood');sign(furniture,'BIENVENIDO AL ESCONDITE',(0,5.8,3.1),.4,'dark')
    else:
        for x,y in [(-4.9,1.65),(-2.1,1.65),(-4.9,-1.15)]:shelf(furniture,x,y,identifier)
        box(furniture,(3.0,.25,.46),(.7,3,.92),'wood');box(furniture,(3.0,.25,.95),(.82,3.08,.08),'cream')
        box(furniture,(3.0,.80,1.13),(.38,.22,.27),'dark');box(furniture,(2.82,.79,1.20),(.025,.20,.15),'blue')
        box(furniture,(2.95,0,1.01),(.18,.25,.035),'dark');box(furniture,(3.08,1.2,1.02),(.17,.13,.06),'metal')
        sign(furniture,'CAJA',(3,5.86,2.7),.5,'teal')
        if identifier=='Restaurant':
            box(furniture,(5.8,3.7,.65),(2.5,2.8,1.3),'metal');box(furniture,(5.8,3.7,1.35),(2.6,2.9,.08),'dark')
            for x in [5.0,5.7,6.4]:b=Batch();b.cyl((x,3.7,1.51),.2,.30,'metal',12);emit('R9_CoffeeMachine_'+str(x),b,parent)
        if identifier=='Clothing':
            for x in [-5.5,-3,-.5,2]:box(furniture,(x,5,1.2),(1.4,.4,1.8),'denim' if x<0 else 'coral')
        if identifier=='Minimarket':
            for x in [-5.5,-3,-.5]:box(furniture,(x,5.3,1.2),(2,.8,2),'white');box(furniture,(x,4.85,1.3),(1.8,.04,1.5),'glass')
    emit(parent.name+'_Interior',furniture,parent)
    marks=Batch()
    if kind:
        for y in [0,-.7,-1.4]:marks.cyl((2.1,y,.204),.20,.006,'gold',16)
    emit(parent.name+'_FloorMarks',marks,parent,'floor_marking')
    # Anclas exactas de las hojas: su origen coincide con la jambas, nunca con el centro del local.
    for side in [-1,1]:
        anchor=bpy.data.objects.new('DoorAnchor_'+identifier+('_L' if side<0 else '_R'),None);scene.collection.objects.link(anchor);anchor.parent=parent;anchor.location=(side*1.2,-6,FLOOR)
apron=Batch();covered=[]
from mesh_tools import subtract_rect
for rect in CLEAR:
    pieces=[rect]
    for previous in covered:pieces=[part for piece in pieces for part in subtract_rect(piece,previous)]
    for x0,y0,x1,y1 in pieces:box(apron,((x0+x1)/2,(y0+y1)/2,.09),(x1-x0,y1-y0,.18),'floor')
    covered.append(rect)
emit('R9_Apron',apron,root,'pedestrian_access')
for identifier,centre,label,kind,staff in SPECS:
    if not kind:continue
    parent=bpy.data.objects['R9_Hero_'+identifier]
    # Pequeños carteles exteriores y bancos, fuera de los carriles de circulación.
    furniture=Batch();sign(furniture,'ABIERTO · ENTRA Y ELIGE',(0,-6.19,2.95),.24,'white');emit(parent.name+'_OpenSign',furniture,parent,'floor_marking')
# Macetas y follaje del kit propio aprobado; colocación sobre sus bases, fuera de caminos y puertas.
kit=sources9.plants()/'Macetas_Pasto_Viento_R4.blend'
with bpy.data.libraries.load(str(kit),link=False) as (src,dst):dst.meshes=['PlantR4_Pot_Rectangular','PlantR4_Shrub_0_LOD0']
for i,target in enumerate([(-250,-295),(-181,-281),(-225,-270),(-200,-245),(-181,-256),(-249,-284),(-225,-259),(-181,-233)]):
    for mesh,size,base,role in [(dst.meshes[0],(1.3,.65,.45),.18,'planter_rim'),(dst.meshes[1],(1.3,.65,.75),.66,'potted_foliage')]:
        minimum=Vector(tuple(min(v.co[k] for v in mesh.vertices) for k in range(3)));maximum=Vector(tuple(max(v.co[k] for v in mesh.vertices) for k in range(3)));scale=Vector(tuple(size[k]/max(.001,maximum[k]-minimum[k]) for k in range(3)));middle=(minimum+maximum)/2
        obj=bpy.data.objects.new('R9_Planter_'+str(i)+'_'+role,mesh);scene.collection.objects.link(obj);obj.parent=root;obj.scale=scale;obj.location=(target[0]-middle.x*scale.x,target[1]-middle.y*scale.y,base-minimum.z*scale.z);obj['MapRole']=role
bpy.context.view_layer.update()
# Una única malla de obstáculos alimenta los grafos de las cinco tiendas.
collidable={'hero_shell','detailed_interior','building','prop','sidewalk_furniture','planter_rim','parked_vehicle','pedestrian_access','Ground','Roads','Sidewalks'}
verts=[];faces=[]
for o in root.children_recursive:
    if o.type!='MESH' or o.get('MapRole') not in collidable:continue
    lo,hi=bounds(o)
    if hi.x<-256 or lo.x>-170 or hi.y<-310 or lo.y>-228:continue
    n=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend([n+i for i in p.vertices] for p in o.data.polygons)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
def unity(p):return [float(p[0]),float(p[2]),float(-p[1])]
def free(x,y,z):
    for dx,dy in [(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25),(.18,.18),(-.18,-.18),(.18,-.18),(-.18,.18)]:
        p,_,_,_=bvh.ray_cast(Vector((x+dx,y+dy,z+.35)),Vector((0,0,1)),1.35)
        if p is not None:return False
    return True
shops=[];doors=[];pois=[]
for identifier,centre,label,kind,staff in SPECS:
    cx,cy=centre;pois.append({'id':identifier,'label':label,'position':unity((cx,cy,FLOOR+.025)),'yaw':0})
    doors.append({'id':identifier,'file':'Doors/DoubleLeaf.fbx','single':False,'leaves':[{'position':unity((cx-1.2,cy-6,FLOOR)),'yaw':0},{'position':unity((cx+1.2,cy-6,FLOOR)),'yaw':180}],'threshold':unity((cx,cy-6,FLOOR))})
    if not kind:continue
    ids={};nodes=[]
    for iy in range(22):
        y=-9.8+iy*.7
        for ix in range(21):
            x=-7+ix*.7;z=FLOOR if y>-6 else .18
            if free(cx+x,cy+y,z):ids[ix,iy]=len(nodes);nodes.append({'v':unity((cx+x,cy+y,z)),'links':[]})
    for (ix,iy),index in ids.items():
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            if (ix+dx,iy+dy) not in ids:continue
            j=ids[ix+dx,iy+dy];a,b=nodes[index]['v'],nodes[j]['v']
            if all(free(a[0]+(b[0]-a[0])*t,-a[2]-(b[2]-a[2])*t,a[1]+(b[1]-a[1])*t) for t in [.25,.5,.75]):nodes[index]['links'].append(j)
    def points(values):
        result=[]
        for x,y in values:
            closest=min(nodes,key=lambda n:(n['v'][0]-cx-x)**2+(n['v'][2]+cy+y)**2)
            assert math.hypot(closest['v'][0]-cx-x,closest['v'][2]+cy+y)<.71,(identifier,x,y)
            p=closest['v'];result.append({'v':[p[0]-cx,-p[2]-cy,p[1]]})
        return result
    shops.append({'id':identifier,'product':kind,'priceCents':{'MilkCarton':750,'JewelryBox':18500,'CoffeeCup':450,'FoldedShirt':2500,'ToolKit':4000}[kind],
        'staffVariant':staff,'staffYaw':-math.pi/2,'origin':unity((cx,cy,0)),'staffWorld':unity((cx+3.7,cy,FLOOR)),
        'walk':points([(-6.3,-9.1),(6.3,-9.1),(6.3,-8.4),(-6.3,-8.4)]),'entry':points([(0,-8.4),(0,-6.3),(0,-4.9)]),
        'browseStations':points([(-4.9,.7),(-2.1,.7),(-4.9,-2.1)]),'queue':points([(2.1,0),(2.1,-.7),(2.1,-1.4)]),'exit':points([(0,-4.2),(0,-6.3),(0,-8.4),(-6.3,-8.4)]),
        'products':[{'v':[x,y,1.04]} for x,y in [(-4.9,1.25),(-2.1,1.25),(-4.9,-1.55)]],'counter':[2.64,0,1.0],'scan':[3.0,0,1.0],'receipt':[2.66,.50,1.0],'till':[3.10,.8,1.10],'nodes':nodes})
assert len(shops)==5
(B/'district.json').write_text(json.dumps({'shops':shops,'doors':doors,'pois':pois,'spawn':unity((-240,-290,FLOOR+.025)),'lobby_slots':[unity((-240+x,-290+y,FLOOR+.025)) for x,y in [(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)]]},indent=2))
(B/'map_changes.json').write_text(json.dumps({'removed':sorted(removed),'changed':sorted(changed),'world_size_m':[3000,3000],'new_core_shops':5,'new_hideout':True},indent=2))
scene.name='R9_Barrio_3000m';scene.camera.location=(-210,-345,42);scene.camera.rotation_euler=(Vector((-247,-278,0))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=128
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Villa_Alarma_3000_R9.blend'),compress=True);print('R9_NEIGHBORHOOD_READY',len(root.children_recursive),[(s['id'],len(s['nodes'])) for s in shops],flush=True)
