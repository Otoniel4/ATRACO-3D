"""Villa Alarma, mapa propio low poly 4×4 km. Escena estática, en metros.
blender -b --python-exit-code 1 -P build_map.py
"""
import bpy,math,json,random,sys
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from mesh_tools import Batch,palette,world_matrix
from layout_math import bounds,rect,disk,clip_half,difference,point_segment,inside,strip,overlap
from urban_assets import PROTOTYPES,make_library,load_own_library,register
C=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'))
L=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))
RNG=random.Random(C['seed']);SECTORS={};BATCHES={};PLACEMENTS=[];POIS=[];ROOFS=[];FOOTPRINTS=[]
HALF=C['world_size_m']/2;STEP=C['sector_size_m'];SCENE=None;ROOT=None;REFERENCE=None
ROAD_CLEARANCE=[strip(l['a'],l['b'],l['width']+6) for l in L['lines']]
ASSET_BOUNDS={}

def sector_for(x,y):return min(7,max(0,int((x+HALF)//STEP))),min(7,max(0,int((y+HALF)//STEP)))
def batch_for(x,y,layer):
    key=(*sector_for(x,y),layer)
    if key not in BATCHES:BATCHES[key]=Batch()
    return BATCHES[key]
def obj_mesh(name,data,position,rotation=0,role='prop'):
    i,j=sector_for(position[0],position[1]);entry=SECTORS[i,j]
    obj=bpy.data.objects.new(name,data);entry['collection'].objects.link(obj);obj.parent=entry['root']
    obj.location=Vector(position)-entry['origin'];obj.rotation_euler.z=rotation;obj['MapRole']=role
    return obj
def place(asset,p,rotation=0,role='prop',name=None):
    obj=obj_mesh(name or asset,PROTOTYPES[asset],p,rotation,role)
    PLACEMENTS.append({'name':obj.name,'asset':asset,'position':list(p),'rotation_z':rotation,'role':role,'sector':list(sector_for(p[0],p[1]))})
    return obj
def generated(name,batch,p,rotation=0,role='detail'):
    register(name,batch);return place(name,p,rotation,role)
def surface(poly,z,color,layer):
    x0,y0,x1,y1=bounds(poly)
    for i in range(max(0,int((x0+HALF)//STEP)),min(7,int((x1+HALF)//STEP))+1):
        for j in range(max(0,int((y0+HALF)//STEP)),min(7,int((y1+HALF)//STEP))+1):
            clipped=poly
            box=rect(-HALF+i*STEP,-HALF+j*STEP,-HALF+(i+1)*STEP,-HALF+(j+1)*STEP)
            for a,b in zip(box,box[1:]+box[:1]):clipped=clip_half(clipped,a,b)
            if clipped:
                batch=batch_for(-HALF+(i+.5)*STEP,-HALF+(j+.5)*STEP,layer)
                batch.add([(x,y,z) for x,y in clipped],[tuple(range(len(clipped)))],color)
def mark_box(p,size,color,angle=0):batch_for(*p[:2],'Markings').box(p,size,color,angle)
def water_at(p):return any(inside(p,poly) for poly in L['river'])
def clear(p,radius=0):
    if not (-1985+radius<p[0]<1985-radius and -1985+radius<p[1]<1985-radius):return False
    if math.hypot(*p)<72+radius:return False
    for line in L['lines']:
        if point_segment(p,line['a'],line['b'])<line['width']/2+radius+3:return False
    for a,b in zip(C['river_path'],C['river_path'][1:]):
        if point_segment(p,a,b)<C['river_width_m']/2+radius+5:return False
    return True
def zone(x,y):
    if x>640 and y>0:return 'services'
    if 160<x<800 and -160<y<960:return 'financial'
    if abs(x)<640 and abs(y)<640:return 'commercial'
    if x>800 and y<-640:return 'outskirts'
    return 'residential'
def block_center(b):return (-1600+(b[0]+.5)*160,-1600+(b[1]+.5)*160)

def building_footprint(asset,p,angle):
    if asset not in ASSET_BOUNDS:
        vs=PROTOTYPES[asset].vertices;ASSET_BOUNDS[asset]=(min(v.co.x for v in vs),min(v.co.y for v in vs),max(v.co.x for v in vs),max(v.co.y for v in vs))
    polygon=rect(*ASSET_BOUNDS[asset]);co,si=math.cos(angle),math.sin(angle)
    return [(p[0]+x*co-y*si,p[1]+x*si+y*co) for x,y in polygon]

def building_clear(asset,p,angle):
    polygon=building_footprint(asset,p,angle)
    if any(not(-1985<x<1985 and -1985<y<1985) for x,y in polygon):return False
    if any(overlap(polygon,q) for q in ROAD_CLEARANCE):return False
    if any(overlap(polygon,q) for q in L['river']):return False
    if inside((0,0),polygon) or min(point_segment((0,0),a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1]))<72:return False
    return True

def setup():
    global SCENE,ROOT,REFERENCE
    bpy.ops.wm.read_factory_settings(use_empty=True)
    SCENE=bpy.context.scene;SCENE.name='Map4Km_Overview';SCENE.unit_settings.system='METRIC';SCENE.unit_settings.scale_length=1
    try:SCENE.render.engine='BLENDER_EEVEE_NEXT'
    except TypeError:SCENE.render.engine='BLENDER_EEVEE'
    SCENE.view_settings.view_transform='Standard';SCENE.view_settings.exposure=-.35
    SCENE.world=bpy.data.worlds.new('VillaAlarmaWorld');SCENE.world.use_nodes=True
    n=next(n for n in SCENE.world.node_tree.nodes if n.type=='BACKGROUND');n.inputs['Color'].default_value=(.70,.76,.84,1);n.inputs['Strength'].default_value=.45
    data=bpy.data.lights.new('MapSun','SUN');data.energy=3.0;data.color=(1,.93,.83);data.angle=math.radians(3)
    obj=bpy.data.objects.new('MapSun',data);SCENE.collection.objects.link(obj);obj.rotation_euler=(math.radians(25),math.radians(-30),math.radians(-25))
    ROOT=bpy.data.objects.new('VillaAlarma_4000m',None);SCENE.collection.objects.link(ROOT)
    ROOT['WorldSizeMeters']=4000;ROOT['Status']='Static art, pending visual approval and Unity integration'
    REFERENCE=bpy.data.collections.new('ScaleReferences_NotExported');SCENE.collection.children.link(REFERENCE)
    for i in range(8):
        for j in range(8):
            name=f'Sector_{i:02d}_{j:02d}';collection=bpy.data.collections.new(name);SCENE.collection.children.link(collection)
            origin=Vector((-2000+(i+.5)*500,-2000+(j+.5)*500,0))
            root=bpy.data.objects.new(name,None);collection.objects.link(root);root.parent=ROOT;root.location=origin
            root['GridX']=i;root['GridY']=j;SECTORS[i,j]={'root':root,'collection':collection,'origin':origin}
    palette(C['palette']);make_library()

def ground_and_roads(holes):
    cutters=L['river']+[rect(*hole) for hole in holes]
    for i in range(8):
        for j in range(8):
            tile=rect(-2000+i*500,-2000+j*500,-1500+i*500,-1500+j*500)
            for p in difference([tile],cutters):surface(p,0,'grass','Ground')
    for p in L['river']:
        # Recorta al mundo exacto de 4 km, incluidas las curvas que llegan al límite.
        q=p
        world=rect(-2000,-2000,2000,2000)
        for a,b in zip(world,world[1:]+world[:1]):q=clip_half(q,a,b)
        if q:surface(q,-.85,'water','Water')
    for p in L['roads']:surface(p,.04,'asphalt','Roads')
    for p in L['sidewalks']:surface(p,.18,'cream','Sidewalks')
    surface(disk(0,0,48,48),.18,'sand','Plaza')
    # Ribera clara que sigue la curva; nunca tapa el cauce.
    for a,b in zip(C['river_path'],C['river_path'][1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
        for sign in [-1,1]:
            off=sign*38;pa=(a[0]+nx*off,a[1]+ny*off);pb=(b[0]+nx*off,b[1]+ny*off)
            from layout_math import strip
            for p in difference([strip(pa,pb,5)],L['river']):surface(p,.02,'sand','RiverWalk')

def street_details():
    lines=L['lines']
    for n,line in enumerate(lines):
        a,b=line['a'],line['b'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length;angle=math.atan2(uy,ux)
        for s in range(6,int(length)-5,9):
            p=(a[0]+ux*s,a[1]+uy*s)
            if math.hypot(*p)<76:continue
            if any(point_segment(p,q['a'],q['b'])<q['width']/2+4 for m,q in enumerate(lines) if m!=n and abs(ux*(q['b'][1]-q['a'][1])-uy*(q['b'][0]-q['a'][0]))>1):continue
            mark_box((*p,.056),(4,.16,.015),'mustard',angle)
        # Puentes planos con barandillas donde una vía atraviesa el río.
        hits=[s for s in range(0,int(length),4) if water_at((a[0]+ux*s,a[1]+uy*s))]
        if hits:
            groups=[];run=[hits[0]]
            for s in hits[1:]:
                if s-run[-1]>5:groups.append(run);run=[]
                run.append(s)
            groups.append(run)
            for k,run in enumerate(groups):
                mid=(run[0]+run[-1])/2;span=run[-1]-run[0]+14;p=(a[0]+ux*mid,a[1]+uy*mid,.04)
                bridge=Batch();bridge.box((0,0,-.22),(span,line['width']+2.4,.40),'metal')
                for sign in [-1,1]:
                    y=sign*(line['width']/2+1.0)
                    bridge.beam((-span/2,y,1.05),(span/2,y,1.05),.075,'teal')
                    for x in range(-int(span/2),int(span/2)+1,5):bridge.box((x,y,.55),(.16,.16,1.1),'cream')
                generated(f'Bridge_{n}_{k}',bridge,p,angle,'bridge')
    for x in range(-1600,1441,160):
        for y in range(-1600,1601,160):
            if math.hypot(x,y)<90 or water_at((x,y)):continue
            wx=22 if x in [-320,0,640] else 14;wy=22 if y in [-320,0,640] else 14
            # Cebras fuera del rectángulo central del cruce.
            for sign in [-1,1]:
                for v in range(-int(wx/2)+1,int(wx/2),2):mark_box((x+v,y+sign*(wy/2+2.4),.062),(.85,3.0,.018),'marking')
                for v in range(-int(wy/2)+1,int(wy/2),2):mark_box((x+sign*(wx/2+2.4),y+v,.062),(3.0,.85,.018),'marking')
            if x in [-320,0,640] or y in [-320,0,640]:
                for sign in [-1,1]:place('Signal',(x+sign*(wx/2+1.7),y-sign*(wy/2+1.7),.18),0 if sign==1 else math.pi)
            elif (x+y)%320==0:place('Stop',(x+wx/2+1.4,y-wy/2-1.5,.18))
    for i in range(48):
        a=i*math.tau/48
        mark_box((56*math.cos(a),56*math.sin(a),.062),(2.6,.15,.02),'marking',a+math.pi/2)
    # Mobiliario espaciado por los lados de las manzanas.
    for x in range(-1600,1441,160):
        w=22 if x in [-320,0,640] else 14
        for y in range(-1520,1600,160):
            if math.hypot(x,y)<90 or water_at((x,y)):continue
            place('Lamp',(x+w/2+2,y,.18),math.pi/2)
            if RNG.random()<.48:
                p=(x+w/2-1.45,y+19,.05)
                if not water_at(p[:2]):place(RNG.choice(['Car_Sedan','Car_Hatchback','Car_Taxi']),p,0,'parked_vehicle')

def park(cx,cy,large=False):
    for path in [rect(cx-43,cy-2,cx+43,cy+2),rect(cx-2,cy-43,cx+2,cy+43)]:
        for piece in difference([path],L['roads']):surface(piece,.025,'sand','ParkPaths')
    for dx,dy in [(-32,-32),(32,-32),(-32,32),(32,32),(-48,0),(48,0)]:
        if clear((cx+dx,cy+dy),4):place('Tree_'+str(RNG.randrange(4)),(cx+dx,cy+dy,0),RNG.random()*6)
    for dx in [-12,12]:
        if clear((cx+dx,cy-5),2):place('Bench',(cx+dx,cy-5,.02))
        if clear((cx+dx,cy+5),2):place('Planter',(cx+dx,cy+5,.02))
    if large and clear((cx,cy),12):place('DuckFountain',(cx,cy,0))

def blocks_and_houses(reserved):
    for bx in range(19):
        for by in range(20):
            if (bx,by) in reserved:continue
            cx,cy=block_center((bx,by));district=zone(cx,cy)
            if cx<-1180 and cy<-1080:continue
            if [bx,by] in C['park_blocks']:park(cx,cy,True);continue
            if district=='financial':candidates=[(-40,-40),(40,-40),(-40,40),(40,40)]
            elif district=='outskirts':candidates=[(-42,-40),(42,-40),(-42,40),(42,40)]
            else:candidates=[(x,y) for y in [-60,60] for x in [-52,-25,25,52]]+[(x,y) for x in [-40,40] for y in [-21,21]]
            for index,(dx,dy) in enumerate(candidates):
                variant=RNG.randrange(6)
                if district=='financial':asset='Tower_'+str(index%3);rotation=0 if dy<0 else math.pi;radius=23
                elif district=='outskirts':
                    asset='Warehouse_'+str(index%3);rotation=0 if dy<0 else math.pi;radius=25;dy=math.copysign(40,dy)
                else:
                    kind='House' if district=='residential' else ('Shop' if district=='commercial' else 'Apartment')
                    asset=kind+'_'+str(variant);radius=11 if kind=='House' else 18
                    rotation=(0 if dy<0 else math.pi) if abs(dy)>40 else (math.pi if dy<0 else 0)
                    # Lleva fachadas pequeñas hasta su acera, sin escalar edificios.
                    if kind=='House':
                        if abs(dy)>40:dy=math.copysign(56,dy)
                    elif abs(dy)>40:dy=math.copysign(52,dy)
                p=(cx+dx,cy+dy,.18)
                if not building_clear(asset,p,rotation):continue
                place(asset,p,rotation,'building')
                FOOTPRINTS.append({'asset':asset,'position':list(p),'polygon':building_footprint(asset,p,rotation),'district':district})
                if district=='residential' and RNG.random()<.45:
                    yard=Batch()
                    for sign in [-1,1]:
                        yard.box((sign*6,-9,.55),(6,.13,1.1),'cream')
                        for xx in [sign*3,sign*6,sign*9]:yard.box((xx,-9,.6),(.18,.20,1.2),'sand')
                    generated('Garden_'+str(len(FOOTPRINTS)),yard,p,rotation,'garden')
                for tx,ty in [(-8,8),(8,8)]:
                    co,si=math.cos(rotation),math.sin(rotation);tree=(p[0]+tx*co-ty*si,p[1]+tx*si+ty*co)
                    if clear(tree,2.8):place('Tree_'+str(variant%4),(*tree,0),role='street_tree')
            # Árboles y patios; pequeños atajos atraviesan el interior de las manzanas.
            if clear((cx,cy),5):
                surface(rect(cx-2,cy-45,cx+2,cy+45),.025,'sand','Alleys')
                for dx in [-24,24]:
                    if clear((cx+dx,cy+8),4):place('Tree_'+str(RNG.randrange(4)),(cx+dx,cy+8,0))
                if district=='commercial':place('Bench',(cx-5,cy,.03));place('Bin',(cx+5,cy,.03))

def interior(asset,p,label,doors):
    place(asset,p,role='interior',name=label+'_Furnished')
    if asset+'_Roof' in PROTOTYPES:
        roof=place(asset+'_Roof',p,role='removable_roof',name=label+'_Roof');ROOFS.append(roof)
    transform=Matrix.Translation(Vector(p))
    for i,entry in enumerate(doors.get(asset,[])):
        matrix=transform@entry['matrix'];obj=place(entry['asset'],matrix.translation,role='door',name=label+'_Door_'+str(i))
        obj.rotation_euler=(matrix.to_quaternion().to_matrix()@Matrix.Rotation(1.1 if i%2==0 else -1.1,3,'Z')).to_euler()
        obj['HingeOrigin']=True;obj['DoorStatus']='Static open pose, no interaction code'

def business_sign(identifier,label,width,p,color='teal'):
    b=Batch();b.box((0,0,3.38),(width,.24,.86),color);b.text(label,(0,-.14,3.38),min(.62,width/max(len(label),1)*1.35),'cream')
    for i in range(12):b.box((-width/2+(i+.5)*width/12,-.70,2.82),(width/12,1.35,.12),'cream' if i%2 else 'coral')
    return generated(identifier+'_Sign',b,p,role='landmark_sign')

def hero_pois(doors):
    source={'market':'Interior_Minimarket','jewelry':'Interior_Jewelry','bank':'Interior_Bank','police':'Interior_PoliceStation',
            'hideout':'Interior_Hideout','clothing':'Interior_ClothingStore','restaurant':'Interior_Restaurant','gear':'Interior_Hideout','garage':'Interior_Hideout'}
    for entry in C['pois']:
        kind=entry['type'];identifier=entry['id']
        if kind=='plaza':
            if 'PlazaFountain' not in PROTOTYPES:
                data=PROTOTYPES['DuckFountain'].copy();data.name='PlazaFountain'
                for v in data.vertices:v.co.x*=1.8;v.co.y*=1.8;v.co.z*=1.6
                PROTOTYPES['PlazaFountain']=data
            place('PlazaFountain',(0,0,.18),role='landmark');POIS.append(entry|{'position':[0,0,.18]});continue
        cx,cy=block_center(entry['block']);p=(cx,cy-47,.18)
        if kind in source:
            asset=source[kind];interior(asset,p,identifier,doors)
            depth=14 if kind=='bank' else (12 if kind=='police' else 10);width=16 if kind=='bank' else (14 if kind=='police' else 12)
            business_sign(identifier,{'market':'MINI TODO','jewelry':'BRILLA BRILLA','bank':'BANCO SIN PRISA','police':'POLICIA',
                'hideout':'TALLER EL PRIMO','clothing':'NI ME VISTE','restaurant':'PIZZA PANICO','gear':'DON TRUEQUE','garage':'CAMALEON'}[kind],width,(p[0],p[1]-depth/2-.15,p[2]),'denim' if kind=='police' else 'teal')
            if kind in ['market','jewelry','clothing','restaurant','gear','garage']:
                b=Batch()
                for sign in [-1,1]:
                    xx=sign*width*.28;yy=-depth/2-.14
                    b.box((xx,yy,1.55),(3.1,.12,2.15),'cream');b.box((xx,yy-.075,1.55),(2.85,.035,1.92),'navy')
                    b.box((xx,yy-.10,1.55),(.07,.025,1.92),'glass')
                    b.box((xx,yy-.12,.55),(3.3,.35,.15),'sand')
                generated(identifier+'_Shopfront',b,p,role='shopfront')
            surface(rect(cx-22,cy-79,cx+22,cy-32),.17,'sand','BusinessAprons')
            if kind=='bank':
                b=Batch()
                for x in [-6,-2,2,6]:b.cyl((x,-9,1.7),.35,3.4,'cream',10)
                b.box((0,-8.2,3.65),(16,4,.35),'sand');b.cyl((0,0,5),1.5,.35,'gold',16,direction=(0,-1,0));b.text('$',(0,-.20,5),1.8,'cream')
                generated('BankColumnsCoin',b,p,role='landmark')
            elif kind=='market':
                b=Batch();b.box((0,0,3.65),(1.7,1.4,.3),'cream');b.box((0,0,4.7),(1.5,1.2,2.0),'cream');b.text('LECHE',(0,-.62,4.7),.3,'coral');b.box((0,0,5.8),(1.6,1.3,.2),'coral');generated('MilkRoof',b,p,role='landmark')
            elif kind=='jewelry':
                b=Batch();b.box((0,0,3.9),(1.2,1.2,.8),'cream');b.ico((0,0,5.1),(1.7,1.4,1.5),'glass',1);generated('RoofDiamond',b,p,role='landmark')
                # Galería comercial con tienda y restaurante vecinos y corredor peatonal.
                for dx,neighbor in [(-21,'Interior_ClothingStore'),(21,'Interior_Restaurant')]:
                    if clear((p[0]+dx,p[1]),10):interior(neighbor,(p[0]+dx,p[1],p[2]),identifier+str(dx),doors)
            if kind=='police':
                place('Car_Police' if 'Car_Police' in PROTOTYPES else 'Car_Sedan',(cx+13,cy-63,.18),math.pi/2,'parked_vehicle')
            for dx in [-18,18]:
                if clear((cx+dx,cy-42),3):place('Tree_1',(cx+dx,cy-42,.18));place('Bench',(cx+dx,cy-64,.18))
            for dx,dy in [(-46,-55),(46,-55),(-42,50),(0,50),(42,50),(-54,8),(54,8)]:
                asset='Shop_1' if entry['district']=='commercial' else 'House_2';position=(cx+dx,cy+dy,.18);rotation=math.pi if dy>0 else 0
                if building_clear(asset,position,rotation):
                    place(asset,position,rotation,'building');FOOTPRINTS.append({'asset':asset,'position':list(position),'polygon':building_footprint(asset,position,rotation),'district':entry['district']})
            POIS.append(entry|{'position':list(p),'entrance':[p[0],p[1]-depth/2-.8,p[2]],'rear_exit':[p[0],p[1]+depth/2+.8,p[2]],'interior_asset':asset})
        elif kind=='parking':
            parking(cx,cy);POIS.append(entry|{'position':[cx,cy,-3.3],'entrance':[cx,cy-35,.18],'rear_exit':[cx+13,cy+14,.18]})
        elif kind in ['metro','sewer']:
            stair_portal(identifier,cx,cy,kind);POIS.append(entry|{'position':[cx,cy,.18],'entrance':[cx,cy-5,.18],'lower_access':[cx,cy+3,-4]})
        park(cx,cy+20)
    # Plaza circular, accesos radiales y mobiliario cómico.
    for i in range(8):
        angle=(i+.5)*math.tau/8;x,y=34*math.cos(angle),34*math.sin(angle)
        bed=[]
        for radius,a in [(20,angle-.25),(42,angle-.25),(42,angle+.25),(20,angle+.25)]:bed.append((radius*math.cos(a),radius*math.sin(a)))
        surface(bed,.22,'sage','PlazaGardens')
        for da in [-.12,0,.12]:place('Tree_'+str(i%4),(34*math.cos(angle+da),34*math.sin(angle+da),.22))
        place('Bench',(x*.52,y*.52,.18),angle+math.pi/2)
        place('Planter',(x*.87,y*.87,.18),angle);place('Bin',(x*.72+2,y*.72,.18))
    for x in [-28,28]:place('FoodStand',(x,0,.18),0,role='landmark')

def stair_portal(identifier,x,y,kind):
    b=Batch()
    for sign in [-1,1]:b.box((sign*1.48,0,-.12),(.24,9,.22),'sand')
    b.box((0,4,-4.15),(3.2,2,.25),'metal')
    for i in range(24):
        z=.18-i*(4.18/24);yy=-4.0+i*.32
        b.box((0,yy,z-.10),(2.4,.34,.20),'cream')
    for sign in [-1,1]:b.box((sign*1.5,0,1.0),(.20,9,2.0),'terracotta' if kind=='sewer' else 'teal')
    b.box((0,-4.2,2.7),(3.5,.5,.3),'cream')
    label='M' if kind=='metro' else 'ACCESO';b.text(label,(0,-4.51,2.7),1.0 if kind=='metro' else .35,'coral')
    generated(identifier+'_Stairs',b,(x,y,0),role='escape_route')

def parking(x,y):
    b=Batch();b.box((0,0,-3.5),(30,28,.3),'metal')
    for xx in [-13,0,13]:
        for yy in [-10,2,12]:b.box((xx,yy,-1.6),(.45,.45,3.4),'cream')
    b.box((-15,0,-1.6),(.25,28,3.4),'metal');b.box((15,0,-1.6),(.25,28,3.4),'metal');b.box((0,14,-1.6),(30,.25,3.4),'metal')
    # Acceso de 6 m, apto para autos, en vez de una puerta peatonal.
    for side in [-1,1]:b.box((side*9,-14,-1.6),(12,.3,3.4),'metal')
    ramp=[(-3,-36,.18),(3,-36,.18),(3,-14,-3.34),(-3,-14,-3.34)]
    b.add(ramp,[(0,1,2,3)],'asphalt');generated('UndergroundParking',b,(x,y,0),role='interior')
    approach=Batch();approach.quad((-4,-70,4,-36),.18,'asphalt')
    approach.add([(-4,-73,.04),(4,-73,.04),(4,-70,.18),(-4,-70,.18)],[(0,1,2,3)],'asphalt')
    generated('ParkingDriveway',approach,(x,y,0),role='escape_route')
    roof=Batch();roof.box((0,0,.04),(30,28,.25),'sand');ROOFS.append(generated('ParkingRoof',roof,(x,y,0),role='removable_roof'))
    for xx in [-9,-3,3,9]:
        place('Car_Hatchback' if xx<0 else 'Car_Sedan',(x+xx,y+4,-3.34),0,'parked_vehicle')
        for side in [-1,1]:mark_box((x+xx+side*1.25,y+4,-3.32),(.09,5,.02),'marking')
    business_sign('Parking','BAJO PERFIL',12,(x,y-36,0))

def forest_and_tunnels():
    for i in range(2900):
        x,y=RNG.uniform(-1970,1970),RNG.uniform(-1970,1970)
        forest=(x<-1000 and y<-950) or abs(x)>1650 or abs(y)>1680
        if forest and clear((x,y),4):place('Tree_'+str(i%4),(x,y,0),RNG.random()*math.tau,'forest')
    for x in range(-1960,-1160,14):
        for y in range(-1960,-1080,14):
            p=(x+RNG.uniform(-3,3),y+RNG.uniform(-3,3))
            if clear(p,5):place('ForestTree_'+str(RNG.randrange(4)),(*p,0),RNG.random()*math.tau,'forest')
    # Cerros facetados al norte y oeste, fuera de las calzadas.
    for i in range(12):
        x=-1740 if i<6 else -1300+(i-6)*480;y=-1000+i*400 if i<6 else 1740
        if not clear((x,y),55):continue
        b=Batch();n=9;r=55;h=RNG.uniform(16,38)
        vs=[(r*math.cos(k*math.tau/n),r*math.sin(k*math.tau/n),0) for k in range(n)]+[(0,0,h)]
        b.add(vs,[(k,(k+1)%n,n) for k in range(n)],'sage');generated('LowPolyHill_'+str(i),b,(x,y,0),role='landform')
    start=next(p for p in POIS if p['id']=='SewerCity')['position'];end=next(p for p in POIS if p['id']=='SewerExit')['position']
    points=[(start[0],start[1]+3,-4),(start[0],end[1]+3,-4),(end[0],end[1]+3,-4)]
    segments=[]
    for a,b in zip(points,points[1:]):
        a,b=Vector(a),Vector(b);count=math.ceil((b-a).length/80)
        segments.extend((a.lerp(b,i/count),a.lerp(b,(i+1)/count)) for i in range(count))
    for i,(a,b) in enumerate(segments):
        length=(b-a).length;direction=(b-a).normalized();normal=Vector((-direction.y,direction.x,0));batch=Batch()
        for k in range(12):
            t0=k*math.pi/12;t1=(k+1)*math.pi/12
            u=normal*(1.8*math.cos(t0))+Vector((0,0,2.3*math.sin(t0)));v=normal*(1.8*math.cos(t1))+Vector((0,0,2.3*math.sin(t1)))
            batch.add([a+u,a+v,b+v,b+u],[(0,1,2,3)],'terracotta')
        batch.add([a-normal*1.8,a+normal*1.8,b+normal*1.8,b-normal*1.8],[(0,1,2,3)],'metal')
        # El lote contiene coordenadas mundiales y se agrupa por sector al volcar superficies.
        for f,m in zip(batch.faces,batch.materials):
            pts=[batch.vertices[v] for v in f];center=tuple(sum(p[k] for p in pts)/len(pts) for k in range(3))
            dst=batch_for(*center[:2],'Sewer');dst.add(pts,[tuple(range(len(pts)))],m)
    (BASE/'escape_routes.json').write_text(json.dumps({'sewer_centerline':[list(p) for p in points],
        'routes':[{'poi':p['id'],'entrance':p.get('entrance'),'rear_exit':p.get('rear_exit')} for p in POIS if 'entrance' in p],
        'status':'static geometry; no movement or network'},indent=2),encoding='utf-8')

def flush_batches():
    for (i,j,layer),batch in BATCHES.items():
        if not batch.faces:continue
        origin=SECTORS[i,j]['origin'];batch.vertices=[tuple(Vector(v)-origin) for v in batch.vertices]
        data=batch.data(f'{layer}_{i:02d}_{j:02d}');obj=bpy.data.objects.new(data.name,data);entry=SECTORS[i,j]
        entry['collection'].objects.link(obj);obj.parent=entry['root'];obj['MapRole']=layer

def scale_figures():
    # Figuras propias solo para comprobar el estilo y la escala en las capturas; no se exportan.
    with bpy.data.libraries.load(str(BASE/'baseline/own_characters.blend'),link=False) as (src,dst):
        dst.scenes=[n for n in src.scenes if n in ['LegsR3_NPC01_Bomber','LegsR3_NPC02_Denim','LegsR3_NPC04_Lavender']]
    saved=bpy.context.window.scene
    for i,source in enumerate(dst.scenes):
        bpy.context.window.scene=source;rig=next(o for o in source.objects if o.type=='ARMATURE')
        for side,sign in [('Left',1),('Right',-1)]:
            bone=rig.pose.bones[side+'UpperArm'];head=bone.head.copy()
            bone.matrix=Matrix.Translation(head)@Matrix.Rotation(sign*.40,4,'Y')@Matrix.Translation(-head)@bone.matrix
        bpy.context.view_layer.update();batch=Batch();deps=bpy.context.evaluated_depsgraph_get()
        for obj in source.objects:
            if obj.type!='MESH':continue
            evaluated=obj.evaluated_get(deps);batch.imported(evaluated,obj.matrix_world)
        data=batch.data('ScaleCitizen_'+str(i));p=next(p for p in POIS if p['id']=='Minimarket')['entrance']
        obj=bpy.data.objects.new(data.name,data);REFERENCE.objects.link(obj);obj.location=(p[0]-4+i*2.5,p[1]-2,.18);obj['NotForExport']=True
    bpy.context.window.scene=saved

def cameras_and_save():
    data=bpy.data.cameras.new('MapCamera');camera=bpy.data.objects.new('MapCamera',data);SCENE.collection.objects.link(camera);SCENE.camera=camera
    data.type='ORTHO';data.ortho_scale=6500;data.clip_start=.1;data.clip_end=30000
    camera.location=(3400,-4400,6000);camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
    SCENE.render.resolution_x=2100;SCENE.render.resolution_y=1900;SCENE.render.resolution_percentage=100
    SCENE.render.image_settings.file_format='PNG'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.clip_end=30000;space.overlay.show_extras=False;space.region_3d.view_distance=4500
                allowed={i.identifier for i in space.region_3d.bl_rna.properties['view_perspective'].enum_items}
                if 'CAMERA' in allowed:space.region_3d.view_perspective='CAMERA'
    mesh_objects=[o for entry in SECTORS.values() for o in entry['collection'].objects if o.type=='MESH']
    manifest={'name':C['name'],'world_size_m':[4000,4000],'area_km2':16,'sector_size_m':500,'sector_grid':[8,8],
        'sector_count':64,'building_count':sum(p['role']=='building' for p in PLACEMENTS),
        'mesh_objects':len(mesh_objects),'unique_meshes':len({o.data for o in mesh_objects}),
        'evaluated_triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in mesh_objects),
        'pois':POIS,'sectors':[{'id':e['root'].name,'blender_origin':list(e['origin']),'objects':len(e['collection'].objects)-1} for e in SECTORS.values()],
        'roof_objects':[o.name for o in ROOFS],'unity_runtime_verified':False,'status':'static design'}
    (BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    (BASE/'placements.json').write_text(json.dumps(PLACEMENTS,separators=(',',':')),encoding='utf-8')
    (BASE/'building_footprints.json').write_text(json.dumps(FOOTPRINTS,separators=(',',':')),encoding='utf-8')
    bpy.context.window.scene=SCENE;bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
    print('MAP4_READY',len(mesh_objects),'MESH_OBJECTS',manifest['building_count'],'BUILDINGS',manifest['evaluated_triangles'],'TRIANGLES',flush=True)

def main():
    setup()
    library=BASE/'baseline/own_art_subset_45.blend'
    if not library.exists():library=BASE/'baseline/own_art_library.blend'
    doors=load_own_library(library)
    reserved={tuple(p['block']) for p in C['pois'] if 'block' in p}
    holes=[]
    for poi in C['pois']:
        if poi['type'] not in ['parking','metro','sewer']:continue
        x,y=block_center(poi['block'])
        if poi['type']=='parking':holes.extend([(x-15,y-14,x+15,y+14),(x-3.3,y-36,x+3.3,y-14)])
        else:holes.append((x-1.3,y-4.5,x+1.3,y+4.5))
    ground_and_roads(holes);street_details();blocks_and_houses(reserved);hero_pois(doors);forest_and_tunnels();flush_batches();scale_figures();cameras_and_save()

if __name__=='__main__':main()
