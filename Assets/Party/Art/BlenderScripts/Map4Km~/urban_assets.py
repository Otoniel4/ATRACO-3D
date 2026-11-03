"""Biblioteca propia low poly. Prototipos reutilizables; no se descarga contenido."""
import bpy,math
from mathutils import Matrix,Vector
from mesh_tools import Batch,world_matrix
PROTOTYPES={}

def register(name,batch):
    PROTOTYPES[name]=batch.data(name);PROTOTYPES[name].use_fake_user=True;return name

def window(b,x,y,z,w=1.3,h=1.6,side=False):
    if side:
        b.box((x,y,z),(.12,w+.22,h+.22),'cream');b.box((x+.073,y,z),(.025,w,h),'navy')
        b.box((x+.09,y,z),(.025,.055,h),'glass')
    else:
        b.box((x,y,z),(w+.22,.14,h+.22),'cream');b.box((x,y-.084,z),(w,.025,h),'navy')
        b.box((x,y-.102,z),(.055,.025,h),'glass')
        b.box((x,y-.18,z-h/2-.08),(w+.35,.42,.14),'sand')

def building(name,w,d,floors,color,style):
    b=Batch();height=floors*3.2
    b.box((0,0,height/2),(w,d,height),color);b.box((0,0,.20),(w+.18,d+.18,.40),'sand')
    b.box((0,-d/2-.11,1.18),(1.55,.15,2.36),'cream');b.box((0,-d/2-.20,1.12),(1.22,.08,2.24),'teal')
    b.box((.42,-d/2-.26,1.0),(.10,.07,.10),'gold')
    for floor in range(floors):
        z=1.55+floor*3.2
        for x in [-w*.33,0,w*.33]:
            if floor==0 and x==0:continue
            window(b,x,-d/2-.05,z,min(1.7,w*.14),1.6)
        for y in [-d*.30,d*.30]:window(b,w/2+.03,y,z,1.4,1.5,True)
        if floor>0:b.box((0,0,floor*3.2),(w+.2,d+.2,.18),'cream')
    if style=='house':
        x,y=w/2+.45,d/2+.45;z=height
        b.add([(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z),(0,-y,z+2.2),(0,y,z+2.2)],[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)],'terracotta')
        b.box((w*.27,d*.2,height+1.2),(.8,.9,2.0),'cream')
        b.box((0,-d/2-1.1,2.7),(w*.65,2.3,.18),'terracotta')
        for x in [-w*.28,w*.28]:b.box((x,-d/2-1.9,1.3),(.18,.18,2.6),'cream')
    else:
        b.box((0,0,height+.15),(w+.55,d+.55,.3),'cream')
        for side in [-1,1]:b.box((side*w/2,0,height+.50),(.20,d+.4,.70),color)
        b.box((0,d/2,height+.50),(w,.20,.70),color)
        b.box((w*.25,d*.15,height+.55),(1.7,1.2,.75),'metal')
    if style=='shop':
        for x in [-w*.28,w*.28]:window(b,x,-d/2-.06,1.55,w*.25,2.0)
        b.box((0,-d/2-.3,3.0),(w*.88,.23,.75),'teal')
        for i in range(10):b.box((-w*.45+(i+.5)*w*.09,-d/2-.85,2.55),(w*.09,1.6,.12),'cream' if i%2 else 'coral')
    if style=='tower':
        for z in range(4,int(height),4):b.box((0,-d/2-.07,z),(w*.9,.10,.15),'gold')
        b.box((0,0,height+1.8),(w*.6,d*.6,3.3),'teal');b.beam((0,0,height+3),(0,0,height+8),.15,'gold')
    if style=='warehouse':
        b.box((0,-d/2-.15,2.3),(w*.43,.18,4.6),'navy')
        for z in [.7,1.4,2.1,2.8,3.5,4.2]:b.box((0,-d/2-.26,z),(w*.42,.05,.07),'metal')
        b.box((w*.28,-d/2-1.1,4.8),(w*.8,2.5,.2),'mustard')
    return register(name,b)

def make_library():
    make_modules()
    for i,color in enumerate(['apricot','coral','mint','cream','lavender','mustard']):
        building('House_'+str(i),11+(i%3),13+(i%2),1+(i%3==0),color,'house')
        building('Apartment_'+str(i),22+(i%2)*4,24,2+i%3,color,'flat')
        building('Shop_'+str(i),19+i%2*3,20,1+i%2,color,'shop')
    for i,color in enumerate(['teal','denim','navy']):building('Tower_'+str(i),30,30,3+i,color,'tower')
    for i,color in enumerate(['cream','terracotta','denim']):building('Warehouse_'+str(i),32,36,2,color,'warehouse')
    for i in range(4):
        b=Batch();b.cyl((0,0,1.7),.20,3.4,'wood',7)
        b.ico((0,0,4.0),(1.7,1.6,2.0),['leaf','sage','mint','dark_leaf'][i],2)
        b.ico((1.0,.2,3.6),(1.1,1.2,1.2),'leaf',1);register('Tree_'+str(i),b)
        forest=PROTOTYPES['Tree_'+str(i)].copy();forest.name='ForestTree_'+str(i)
        for v in forest.vertices:v.co.x*=1.6;v.co.y*=1.6;v.co.z*=1.5
        PROTOTYPES['ForestTree_'+str(i)]=forest
    b=Batch();b.cyl((0,0,2.5),.23,5.0,'wood',7)
    for i in range(8):
        a=i*math.tau/8;x,y=math.cos(a),math.sin(a)
        b.add([(0,0,5),(x-y*.3,y+x*.3,5.7),(x*3,y*3,4.5),(x+y*.3,y-x*.3,5.7)],[(0,1,2),(0,2,3)],'leaf')
    register('Palm',b)
    b=Batch()
    for x in [-.6,.6]:b.box((x,0,.25),(.09,.55,.5),'navy')
    for y in [-.20,0,.20]:b.box((0,y,.52),(1.7,.16,.08),'wood')
    for z in [.78,1.02]:b.box((0,.26,z),(1.7,.08,.16),'wood')
    register('Bench',b)
    b=Batch();b.cyl((0,0,.48),.28,.96,'teal',10);b.cyl((0,0,.96),.32,.08,'navy',10);b.box((0,-.28,.75),(.28,.03,.12),'black');register('Bin',b)
    b=Batch();b.cyl((0,0,2.8),.065,5.6,'navy',8);b.beam((0,0,5.55),(0,-1.25,5.4),.075,'navy');b.box((0,-1.25,5.35),(.38,.72,.15),'mustard');register('Lamp',b)
    b=Batch();b.cyl((0,0,2.6),.06,5.2,'navy');b.beam((0,0,5.2),(0,-2.0,5.2),.07,'navy');b.box((0,-2.0,4.70),(.45,.40,1.1),'black')
    for z,color in [(5.02,'red'),(4.72,'mustard'),(4.42,'leaf')]:b.cyl((0,-2.23,z),.115,.04,color,8,direction=(0,-1,0))
    register('Signal',b)
    b=Batch();b.cyl((0,0,1.25),.045,2.5,'metal',6);b.cyl((0,-.02,2.12),.40,.07,'red',8,direction=(0,-1,0));b.text('PARE',(0,-.065,2.12),.19,'cream');register('Stop',b)
    b=Batch();b.box((0,0,.60),(1.4,.6,1.2),'teal');b.box((0,-.32,.87),(1.1,.03,.42),'black');b.text('RECICLA',(0,-.345,.45),.17,'cream');register('Recycle',b)
    b=Batch();b.box((0,0,.45),(.48,.48,.90),'coral');b.box((0,-.255,.65),(.30,.03,.08),'navy');register('Mailbox',b)
    b=Batch();b.box((0,0,.25),(2.4,1.0,.50),'cream')
    for x in [-.7,0,.7]:b.ico((x,0,.9),(.65,.5,.65),'leaf',1)
    register('Planter',b)
    b=Batch();b.cyl((0,0,.55),.4,1.1,'black',8);b.box((0,-.41,.8),(.4,.03,.3),'mustard');register('Bollard',b)
    b=Batch();b.box((0,0,.8),(6,2.5,1.6),'terracotta');b.box((0,0,1.7),(6.1,2.7,.2),'cream');b.box((0,-1.3,1.0),(4.9,.1,.7),'navy');b.text('TACOS SIN RASTRO',(0,-1.38,1.65),.35,'cream');register('FoodStand',b)
    b=Batch();b.cyl((0,0,.22),5.6,.44,'cream',16);b.cyl((0,0,.47),5.1,.10,'water',16);b.cyl((0,0,.9),1.0,1.0,'sand',10)
    b.ico((0,0,2.0),(1.8,1.3,1.2),'mustard',2);b.ico((0,-.7,3.25),(1.0,.9,1.0),'mustard',2);b.box((0,-1.63,3.05),(1.1,.7,.3),'coral')
    for x in [-.47,.47]:b.ico((x,-1.41,3.48),(.12,.08,.14),'navy',1)
    register('DuckFountain',b)

def make_modules():
    for name,width in [('Road_8m',8),('Road_14m',14),('Road_22m',22)]:
        b=Batch();b.box((0,0,-.1),(width,8,.2),'asphalt');b.box((0,0,.008),(.15,4,.016),'mustard');register(name,b)
    b=Batch();b.box((0,0,-.09),(4,4,.18),'cream');register('Sidewalk_4m',b)
    b=Batch();b.box((0,0,1.5),(4,.22,3),'cream');register('Wall_4m',b)
    b=Batch();b.box((.4,0,1.5),(1,.2,3),'cream');b.box((0,.4,1.5),(.2,1,3),'cream');register('Corner_1m',b)
    b=Batch();window(b,0,0,1.3,1.8,1.6);register('Window_2m',b)
    b=Batch()
    for x in [-.55,.55]:b.box((x,0,1.15),(.10,.20,2.3),'cream')
    b.box((0,0,2.25),(1.2,.20,.10),'cream');register('Door_Frame_1m',b)
    b=Batch();b.box((.5,0,1.10),(1,.10,2.20),'teal');b.box((.5,-.065,1.45),(.78,.025,1.05),'glass');b.box((.9,-.10,1.0),(.08,.08,.08),'gold');register('Door_Leaf_1m',b)
    b=Batch();b.box((0,0,.1),(4,4,.2),'terracotta')
    for x in [-1.9,1.9]:b.box((x,0,.35),(.20,4,.50),'cream')
    b.box((0,1.9,.35),(4,.20,.50),'cream');register('Roof_4m',b)
    b=Batch()
    for x in [-1.75,-1.25,-.75,-.25,.25,.75,1.25,1.75]:b.box((x,0,.008),(.30,3,.016),'marking')
    register('Crosswalk_4m',b)

def load_own_library(path):
    wanted=['Interior_Minimarket','Interior_Jewelry','Interior_Bank','Interior_Hideout','Interior_Restaurant','Interior_ClothingStore','Interior_PoliceStation',
            'Car_Sedan','Car_Hatchback','Car_Taxi','Car_Police','Prop_SecurityCamera','Prop_Safe','Prop_Toolbox','Prop_RetailShelf']
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=['ASSET_'+n for n in wanted if 'ASSET_'+n in src.collections]
    interiors={}
    for collection in dst.collections:
        root=next(o for o in collection.objects if o.type=='EMPTY' and o.get('AlarmaCategory'))
        inverse=world_matrix(root).inverted();base=Batch();roof=Batch();doors=[]
        for obj in [root]+list(root.children_recursive):
            if obj.type!='MESH':continue
            ancestor=obj.parent;pivot=None
            while ancestor and ancestor!=root:
                if 'DoorPivot' in ancestor.name:pivot=ancestor;break
                ancestor=ancestor.parent
            if pivot:
                entry=next((d for d in doors if d['pivot']==pivot),None)
                if entry is None:entry={'pivot':pivot,'batch':Batch()};doors.append(entry)
                entry['batch'].imported(obj,world_matrix(pivot).inverted()@world_matrix(obj))
            elif 'Roof_Removable' in obj.name:roof.imported(obj,inverse@world_matrix(obj))
            else:base.imported(obj,inverse@world_matrix(obj))
        register(root.name,base)
        if roof.faces:register(root.name+'_Roof',roof)
        door_entries=[]
        for i,d in enumerate(doors):
            name=root.name+'_Door_'+str(i);register(name,d['batch'])
            door_entries.append({'asset':name,'matrix':inverse@world_matrix(d['pivot'])})
        if root.name.startswith('Interior_'):interiors[root.name]=door_entries
    return interiors
