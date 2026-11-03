"""Revisión artística R2 de los 4 km. Conserva el trazado, sustituye arquitectura y completa lugares."""
import bpy,sys,json,math,random
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
from mesh_tools import Batch
from layout_math import point_segment,inside,rect
import modern_assets as A
import hero_businesses as H
C=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'))
L=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))
RNG=random.Random(21112026)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/v1_map.blend'))
for scene in bpy.data.scenes:
    if scene.name.startswith('Map4Km_'):scene.name=scene.name.replace('Map4Km_','CityR2_')
scene=bpy.data.scenes['CityR2_Overview'];bpy.context.window.scene=scene
WORLD=bpy.data.objects['VillaAlarma_4000m']
# Convertir rótulos en una escena vacía evita reevaluar la ciudad para cada letra.
workbench=bpy.data.scenes.new('R2_Modeling_Workbench');bpy.context.window.scene=workbench
A.setup_palette(C);A.create_library();HERO=H.make_all()
bpy.context.window.scene=scene;bpy.data.scenes.remove(workbench)
SECTORS={s.name:s for s in WORLD.children};ROOFS=[];BUILDINGS=[];ADDED=[];PATHS={}

def clear(p,radius=0):
    x,y=p[:2]
    if not(-1990+radius<x<1990-radius and -1990+radius<y<1990-radius):return False
    for l in L['lines']:
        if point_segment((x,y),l['a'],l['b'])<l['width']/2+radius+.35:return False
    if any(inside((x,y),poly) for poly in L['river']):return False
    return True

def sector_at(p):
    i=min(7,max(0,int((p[0]+2000)//500)));j=min(7,max(0,int((p[1]+2000)//500)))
    name=f'Sector_{i:02d}_{j:02d}';return SECTORS[name],bpy.data.collections[name]

def place(name,data,p,rotation=0,role='r2_detail',roof=False):
    parent,collection=sector_at(p)
    if roof:
        key='R2_Roofs_'+collection.name;child=bpy.data.collections.get(key)
        if child is None:child=bpy.data.collections.new(key);collection.children.link(child)
        collection=child
    obj=bpy.data.objects.new(name,data);collection.objects.link(obj);obj.parent=parent
    obj.location=Vector(p)-parent.matrix_world.translation;obj.rotation_euler.z=rotation;obj['MapRole']=role
    if roof:ROOFS.append(obj.name)
    ADDED.append(obj.name);return obj

def prototype(name,p,angle=0,role='r2_detail'):return place('R2_'+name,A.PROTOTYPES[name],p,angle,role)

def generated(name,batch,p=(0,0,0),angle=0,role='r2_detail'):
    return place(name,batch.data(name),p,angle,role)

manifest=json.loads((BASE/'baseline/manifest_v1.json').read_text(encoding='utf-8'))
POIS=manifest['pois']
# Se retiran las piezas planas de la revisión anterior de los lugares que se reconstruyen.
for obj in list(WORLD.children_recursive):
    if obj.type!='MESH':continue
    if obj.get('MapRole')=='garden' or obj.name in ['MilkRoof','RoofDiamond','BankColumnsCoin'] or any(obj.name.startswith(id+'_') or obj.name.startswith(id+'-') for id in HERO):
        bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
for obj in list(WORLD.children_recursive):
    if obj.type!='MESH':continue
    key=obj.data.name.split('.')[0];role=obj.get('MapRole','')
    if role=='building' and key.startswith(('House_','Apartment_','Shop_','Tower_','Warehouse_')):
        old=int(key.split('_')[1]);p=obj.matrix_world.translation.copy();angle=obj.rotation_euler.z
        serial=int(abs(p.x)*7+abs(p.y)*11)
        target=key
        if key.startswith(('House_','Shop_')):target=key.split('_')[0]+'_'+str(old+(6 if serial%5 in [0,2,3] else 0))
        obj.data=A.PROTOTYPES[target];obj['R2Asset']=target
        roof=place(obj.name+'_ModernRoof',A.ROOFS[target],p,angle,'removable_roof',True)
        vertices=list(obj.data.vertices)+list(roof.data.vertices)
        x0=min(v.co.x for v in vertices);x1=max(v.co.x for v in vertices);y0=min(v.co.y for v in vertices);y1=max(v.co.y for v in vertices)
        co,si=math.cos(angle),math.sin(angle)
        poly=[(p.x+x*co-y*si,p.y+x*si+y*co) for x,y in rect(x0,y0,x1,y1)]
        BUILDINGS.append({'object':obj.name,'asset':target,'position':list(p),'polygon':poly})
        if target.startswith('House_'):
            prototype('Garden_'+str(old),(p.x,p.y,0),angle,'garden')
            length=8
            for distance in range(8,23):
                point=p+Matrix.Rotation(angle,3,'Z')@Vector((0,-distance,0))
                if not clear(point,1):break
                length=distance
            if length>8:
                sector,_=sector_at(p);batch=PATHS.setdefault(sector.name,Batch())
                vertices=[tuple(Vector((p.x,p.y,.035))+Matrix.Rotation(angle,3,'Z')@Vector((x,y,0)))
                          for x,y in [(-.8,-8),(.8,-8),(.8,-length),(-.8,-length)]]
                batch.add(vertices,[(0,3,2,1)],'stone')
        if target.startswith('Shop_') and (old%3 in [0,1]):
            local=Vector((-4.5,-13.6,0));q=Vector(p)+Matrix.Rotation(angle,3,'Z')@local
            # Conjunto pequeño junto al escaparate, fuera de la circulación vial.
            if clear(q,1.5):prototype('CafeSet',q,angle,'sidewalk_furniture')['TerraceSetbackR2']=True
    elif key.startswith(('Tree_','ForestTree_')):
        p=obj.matrix_world.translation.copy();forest=key.startswith('ForestTree_') or role=='forest'
        species=RNG.choices(range(6),[30,25,12,14,14,5])[0]
        obj.data=A.PROTOTYPES[('ForestTree_' if forest else 'Tree_')+str(species)]
        obj['R2Species']=species
        if forest:
            dx,dy=RNG.uniform(-4.5,4.5),RNG.uniform(-4.5,4.5);q=p+Vector((dx,dy,0))
            if clear(q,5):obj.location+=Vector((dx,dy,0))
        scale=RNG.uniform(.84,1.18);obj.scale=(scale,scale,scale*RNG.uniform(.94,1.08));obj.rotation_euler.z=RNG.random()*math.tau
    elif key in ['Bench','Lamp','Bin','Planter','FoodStand']:
        obj.data=A.PROTOTYPES[key]
print('CITY_R2_ARCHITECTURE_SWAPPED',len(BUILDINGS),flush=True)
for sector_name,batch in PATHS.items():
    origin=SECTORS[sector_name].matrix_world.translation
    batch.vertices=[tuple(Vector(v)-origin) for v in batch.vertices]
    generated('R2_HouseAccess_'+sector_name,batch,origin,role='pedestrian_access')

def apron(p,identifier,w,d):
    b=Batch();front=-d/2
    # Despiece de pavimento frente al local y banda accesible continua de 2 metros.
    b.box((0,front-3.5,-.02),(w+8,5,.04),'ivory')
    for x in range(-int(w/2)-3,int(w/2)+4,2):b.box((x,front-3.5,.01),(.025,5,.015),'stone')
    for y in [front-2,front-4,front-6]:b.box((0,y,.012),(w+8,.025,.015),'stone')
    # Aparcamiento visible y jardineras en la explanada.
    for x in [-10,10]:
        for y in [front-8,front-13]:
            b.box((x,y,.02),(2.7,.07,.025),'marking')
        b.box((x-1.35,front-10.5,.02),(.07,5,.025),'marking')
        A.planter(b,(x,front-16,.02),(3,1.1,.5),True)
    if identifier=='Restaurant':
        for x in [-3,3]:
            local=Vector((x,front-4.5,0));prototype('CafeSet',Vector(p)+local,role='cafe_terrace')
    if identifier in ['Bank','Police','Minimarket']:prototype('BikeRack',Vector(p)+Vector((-w/2-2,front-3,.02)),role='bicycle_rack')
    generated('R2_'+identifier+'_PublicSpace',b,p,role='business_landscape')

for poi in POIS:
    id=poi['id']
    if id not in HERO:continue
    p=Vector(poi['position']);spec=HERO[id];w,d=spec['width'],spec['depth']
    prototype('Hero_'+id,p,role='hero_shell')
    prototype('Hero_'+id+'_Furniture',p,role='furnished_interior')
    place('R2_'+id+'_Roof',A.ROOFS['Hero_'+id],p,role='removable_roof',roof=True)
    # Hoja de acceso abatible con origen real en la bisagra, sin código de interacción.
    if id=='PaintGarage':
        door=prototype('Hero_'+id+'_Door',p+Vector((-spec['door_width']/2,-d/2-.12,0)),role='door');door.rotation_euler.z=-math.pi*.48
    else:
        for sign in [-1,1]:
            hinge=p+Vector((sign*spec['door_width']/2,-d/2-.12,0))
            door=prototype('Hero_'+id+'_Door',hinge,math.pi if sign>0 else 0,role='door')
            door.rotation_euler.z+=sign*.22;door['HingeOrigin']=True
    rear=prototype('Hero_'+id+'_RearDoor',p+Vector((.6,d/2+.12,0)),math.pi-.35,'door');rear['HingeOrigin']=True
    poi['r2_building']=spec;poi['interior_asset']='Hero_'+id+'_Furniture'
    poi['entrance']=[p.x,p.y-d/2-.8,p.z];poi['rear_exit']=[p.x,p.y+d/2+.8,p.z]
    apron(p,id,w,d)
    if id=='PaintGarage':
        car=bpy.data.meshes.get('Car_Hatchback')
        if car:place('R2_Garage_ServiceCar',car,p+Vector((0,0,.35)),0,'parked_vehicle')
    if id=='MallJewelry':
        for dx,n in [(-22,10),(22,1)]:
            q=p+Vector((dx,0,0));name='Shop_'+str(n)
            if not clear(q,17):continue
            prototype(name,q,role='gallery_business');place('R2_Gallery_Roof',A.ROOFS[name],q,role='removable_roof',roof=True)
print('CITY_R2_HERO_INTERIORS',len(HERO),flush=True)

def plaza():
    b=Batch()
    # Círculos concéntricos de piedra delimitan la fuente y las zonas de estancia.
    for radius in [12,15,46]:
        for i in range(96):
            a=i*math.tau/96;c=(i+1)*math.tau/96
            b.add([(radius*math.cos(a),radius*math.sin(a),.215),((radius+.18)*math.cos(a),(radius+.18)*math.sin(a),.215),
                   ((radius+.18)*math.cos(c),(radius+.18)*math.sin(c),.215),(radius*math.cos(c),radius*math.sin(c),.215)],[(0,1,2,3)],'ivory')
    for angle in [i*math.pi/4 for i in range(8)]:
        for radius in [22,29,36,43]:
            x,y=radius*math.cos(angle),radius*math.sin(angle)
            b.box((x,y,.205),(1.6,2.8,.03),'ivory',angle)
    # Chorros de agua geométricos alrededor del pato, apoyados en el vaso de la fuente.
    for i in range(8):
        a=i*math.tau/8;r=6.3
        start=Vector((r*math.cos(a),r*math.sin(a),.9));mid=Vector((r*.65*math.cos(a),r*.65*math.sin(a),3.8));end=Vector((r*.4*math.cos(a),r*.4*math.sin(a),1.0))
        last=start
        for step in range(1,10):
            t=step/9;p=(1-t)**2*start+2*(1-t)*t*mid+t*t*end;b.beam(last,p,.045,'glass',5);last=p
        b.cyl((start.x,start.y,.9),.13,.30,'steel',8)
    # Pérgolas de madera en las dos bandas laterales, con mesas y luminarias.
    for sign in [-1,1]:
        cx=sign*23;cy=-11
        for dx in [-4,4]:
            for dy in [-3,3]:b.box((cx+dx,cy+dy,1.9),(.16,.16,3.5),'charcoal')
        for dy in [-3,3]:b.box((cx,cy+dy,3.7),(8.5,.18,.22),'timber')
        for dx in [i*.7 for i in range(-6,7)]:b.box((cx+dx,cy,3.85),(.20,6.7,.20),'timber')
        for dx in [-2,2]:
            A.table(b,(cx+dx,cy,.2));A.chair(b,(cx+dx,cy-1.1,.2));A.chair(b,(cx+dx,cy+1.1,.2),math.pi)
        A.planter(b,(cx,cy+4,.2),(6.5,1.0,.6),True)
    # Jardineras y luminarias bajas aportan capas al paseo.
    for i in range(8):
        a=(i+.5)*math.pi/4;x,y=43.5*math.cos(a),43.5*math.sin(a)
        A.planter(b,(x,y,.2),(2.8,.9,.50),True)
        b.box((x*.95,y*.95,.65),(.25,.25,.90),'charcoal');b.box((x*.95,y*.95,1.10),(.20,.20,.05),'lamp_white')
    generated('R2_Plaza_PublicRealm',b,(0,0,0),role='plaza_design')
    # Cebras radiales y refugios peatonales fuera de los ocho accesos.
    crossings=Batch()
    for i in range(8):
        a=i*math.pi/4;u=Vector((math.cos(a),math.sin(a),0));v=Vector((-math.sin(a),math.cos(a),0))
        for j in range(6):
            p=u*(49.5+j*2.6)+v*12.5;crossings.box((p.x,p.y,.075),(1.2,3.2,.025),'marking',a)
    generated('R2_Plaza_Crossings',crossings,role='road_markings')
plaza()

def additional_landscape():
    # Paradas de bus en aceras, puntos de carga y zonas de descanso de los parques.
    for x,y,angle in [(-320+14,160,math.pi/2),(14,-480,math.pi/2),(640+14,160,math.pi/2)]:
        if clear((x,y),1):prototype('BusShelter',(x,y,.18),angle,'bus_shelter')
    for poi in POIS:
        if poi['id'] in ['Parking','Metro']:
            x,y=poi['position'][:2]
            for dx in [-8,8]:prototype('EVCharger',(x+dx,y-8,.18),role='ev_charger')
    # Macizos irregulares y rocas de ribera: se rompe la cuadrícula del bosque anterior.
    rocks=Batch();shrubs=Batch()
    for i in range(360):
        x,y=RNG.uniform(-1965,-1150),RNG.uniform(-1950,-1100)
        if not clear((x,y),3):continue
        if i%3==0:
            rocks.ico((x,y,.40),(RNG.uniform(.5,1.4),RNG.uniform(.6,1.7),RNG.uniform(.4,.9)),'stone',1)
        else:
            shrubs.ico((x,y,.55),(1.1,1.0,.9),'leaf_shade' if i%2 else 'leaf_mid',1)
    # Se divide esta geometría por sector para mantener pequeñas las coordenadas locales.
    for name,batch in [('RiverRocks',rocks),('ForestUnderstory',shrubs)]:
        groups={}
        for face,color in zip(batch.faces,batch.materials):
            vertices=[batch.vertices[i] for i in face];p=tuple(sum(v[k] for v in vertices)/len(vertices) for k in range(3));s,_=sector_at(p)
            groups.setdefault(s.name,Batch()).add(vertices,[tuple(range(len(vertices)))],color)
        for sector_name,b in groups.items():
            origin=SECTORS[sector_name].matrix_world.translation;b.vertices=[tuple(Vector(v)-origin) for v in b.vertices]
            generated('R2_'+name+'_'+sector_name,b,origin,role='landscape')
    # Parques de barrio: pérgola, pavimento de estancia, bancos, mesas y jardineras.
    for bx,by in C['park_blocks']:
        x=-1600+(bx+.5)*160;y=-1600+(by+.5)*160;b=Batch()
        for dx,dy in [(-18,-18),(18,18)]:
            if not clear((x+dx,y+dy),6):continue
            b.box((dx,dy,.08),(10,8,.16),'ivory')
            for xx in [-4,4]:
                for yy in [-3,3]:b.box((dx+xx,dy+yy,1.7),(.15,.15,3.4),'charcoal')
            for xx in [-4,-3,-2,-1,0,1,2,3,4]:b.box((dx+xx,dy,3.5),(.18,7,.15),'timber')
            A.table(b,(dx,dy,.18));A.chair(b,(dx,dy-1.1,.18));A.chair(b,(dx,dy+1.1,.18),math.pi)
            for sign in [-1,1]:A.planter(b,(dx+sign*4,dy,.18),(1,4,.5),True)
        generated('R2_Park_'+str(bx)+'_'+str(by),b,(x,y,0),role='park_design')
    # Entradas de metro con marquesina, baranda y tótem informativo.
    for poi in POIS:
        if poi['id']!='Metro':continue
        x,y,z=poi['position'];b=Batch()
        for xx in [-2,2]:
            for yy in [-4.5,4.5]:b.box((xx,yy,1.9),(.12,.12,3.8),'charcoal')
            b.beam((xx,-4.5,3.8),(xx,4.5,3.8),.06,'charcoal',6)
        b.box((0,0,3.8),(4.5,10,.12),'clear_glass');b.box((2.8,-4.5,1.8),(.6,.5,3.6),'teal')
        b.text('M',(2.8,-4.78,2.8),.65,'ivory');generated('R2_Metro_Canopy',b,(x,y,z),role='metro_entrance')
additional_landscape()
bpy.context.view_layer.update()
# Depuración de versiones sin usuarios en esta copia independiente, conservando el kit nuevo.
keep=set(A.PROTOTYPES.values())|set(A.ROOFS.values())
for mesh in bpy.data.meshes:
    if mesh not in keep and mesh.use_fake_user and mesh.users==1:mesh.use_fake_user=False
for s in list(bpy.data.scenes):
    if not s.name.startswith('CityR2_'):bpy.data.scenes.remove(s)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
scene=bpy.data.scenes['CityR2_Overview'];bpy.context.window.scene=scene
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.30
look_items={i.identifier for i in scene.view_settings.bl_rna.properties['look'].enum_items}
if 'AgX - Medium High Contrast' in look_items:scene.view_settings.look='AgX - Medium High Contrast'
sun=next(o for o in scene.objects if o.type=='LIGHT');sun.data.energy=3;sun.data.angle=math.radians(4)
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');background.inputs['Strength'].default_value=.60
meshes=[o for o in WORLD.children_recursive if o.type=='MESH']
triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
manifest.update({'revision':'R2 modern city','pois':POIS,'roof_objects':ROOFS,'building_count':len(BUILDINGS),
                 'mesh_objects':len(meshes),'evaluated_triangles':triangles,'new_prototypes':len(A.CATALOG),
                 'state':'visual design, no animation or game dynamics','source':'baseline/v1_map.blend'})
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
(BASE/'building_footprints_r2.json').write_text(json.dumps(BUILDINGS),encoding='utf-8')
(BASE/'asset_catalog.json').write_text(json.dumps(A.CATALOG,indent=2),encoding='utf-8')
(BASE/'palette.json').write_text(json.dumps(C['palette']|A.COLORS,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
print('MODERN_CITY_R2_SAVED',len(BUILDINGS),'buildings',len(meshes),'meshes',triangles,'triangles',flush=True)
