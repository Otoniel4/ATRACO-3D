"""Arquitectura y vegetación propias. Las formas grandes y las juntas se modelan, sin texturas."""
import bpy,math,random
from mathutils import Vector,Matrix
import mesh_tools as M
from mesh_tools import Batch

COLORS={'ivory':'EEEDE6','stone':'BCBDB6','concrete':'9DA9AE','charcoal':'354550',
        'timber':'AA8059','brick':'B96D55','light_brick':'D69A7A','clear_glass':'91C3CB',
        'office_glass':'396977','steel':'718D96','leaf_light':'87B77B','leaf_mid':'589868',
        'leaf_deep':'326B50','leaf_shade':'28533E','jacaranda':'A49BD0','flower_pink':'DD9CA9',
        'flower_yellow':'E7CA69','soil':'675641','solar':'334E68','lamp_white':'F9EAD0'}
PROTOTYPES={};ROOFS={};CATALOG=[]

def setup_palette(config):
    for key in config['palette']:
        M.INDEX[key]=len(M.MATERIALS);M.MATERIALS.append(bpy.data.materials['City4_'+key])
    M.palette(COLORS)
    glass=bpy.data.materials['City4_clear_glass'];node=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Alpha'].default_value=.22;node.inputs['Roughness'].default_value=.18
    glass.diffuse_color=(.34,.63,.70,.22)
    if hasattr(glass,'surface_render_method'):
        allowed={i.identifier for i in glass.bl_rna.properties['surface_render_method'].enum_items}
        if 'DITHERED' in allowed:glass.surface_render_method='DITHERED'

def merge(target,source,matrix=None):
    start=len(target.vertices)
    target.vertices.extend(tuple(matrix@Vector(v)) if matrix else v for v in source.vertices)
    target.faces.extend(tuple(start+i for i in f) for f in source.faces);target.materials.extend(source.materials)

def register(name,batch,roof=None,category='prop'):
    data=batch.data('CityR2_'+name);data.use_fake_user=True;PROTOTYPES[name]=data
    if roof:
        data=roof.data('CityR2_'+name+'_Roof');data.use_fake_user=True;ROOFS[name]=data
    CATALOG.append({'id':name,'mesh':PROTOTYPES[name].name,'category':category,
                    'triangles':sum(len(f.vertices)-2 for f in PROTOTYPES[name].polygons),'roof':name in ROOFS})
    return name

def panel(b,x,z,w,h,door=False,glass=True):
    frame='charcoal';y=-.16
    for xx in [x-w/2,x+w/2]:b.box((xx,y,z),(.075,.20,h+.12),frame)
    for zz in [z-h/2,z+h/2]:b.box((x,y,zz),(w+.12,.20,.075),frame)
    if glass:b.box((x,y-.045,z),(w-.05,.024,h-.05),'clear_glass')
    if door:
        b.box((x+w*.33,y-.15,z),(.045,.06,.48),'steel')
        b.box((x,y-.05,.04),(w,.27,.06),'stone')
    else:
        b.box((x,y-.10,z-h/2-.04),(w+.22,.35,.08),'ivory')
        b.box((x,y-.07,z),(.045,.08,h),'charcoal')

def wall(b,width,height,origin,angle,openings,color='ivory'):
    """Paños con huecos reales. Cada abertura se expresa como x, z, ancho y alto."""
    local=Batch();cuts=sorted(set([-width/2,width/2]+[v for x,z,w,h,door in openings for v in [x-w/2,x+w/2]]))
    for left,right in zip(cuts,cuts[1:]):
        if right-left<.001:continue
        middle=(left+right)/2;previous=0
        spans=sorted((max(0,z-h/2),min(height,z+h/2)) for x,z,w,h,door in openings if x-w/2-1e-5<middle<x+w/2+1e-5)
        for bottom,top in spans+[(height,height)]:
            if bottom>previous:local.box((middle,0,(previous+bottom)/2),(right-left,.22,bottom-previous),color)
            previous=max(previous,top)
    for x,z,w,h,door in openings:
        if door=='HINGE':
            for xx in [x-w/2,x+w/2]:local.box((xx,-.16,z),(.09,.22,h+.12),'charcoal')
            local.box((x,-.16,z+h/2),(w+.12,.22,.09),'charcoal')
        else:panel(local,x,z,w,h,door)
    merge(b,local,Matrix.Translation(Vector(origin))@Matrix.Rotation(angle,4,'Z'))

def railing(b,a,c,z,height=.95):
    a,c=Vector(a),Vector(c);length=(c-a).length;count=max(1,math.ceil(length/1.25))
    b.beam((a.x,a.y,z+height),(c.x,c.y,z+height),.035,'charcoal',6)
    for i in range(count+1):
        p=a.lerp(c,i/count);b.box((p.x,p.y,z+height/2),(.045,.045,height),'charcoal')
    # Vidrio coloreado opaco para leer el balcón desde lejos.
    mid=(a+c)/2;angle=math.atan2(c.y-a.y,c.x-a.x)
    b.box((mid.x,mid.y,z+height*.52),(length,.025,height*.78),'office_glass',angle)

def planter(b,p,size=(1.8,.65,.45),flower=False):
    x,y,z=p;w,d,h=size;b.box((x,y,z+h/2),(w,d,h),'stone');b.box((x,y,z+h),(w-.12,d-.12,.04),'soil')
    if d>1.8:
        for i in range(max(3,int(w/.7))):
            for j in range(max(2,int(d/.8))):
                xx=x-w*.34+i*w*.68/max(1,int(w/.7)-1);yy=y-d*.30+j*d*.60/max(1,int(d/.8)-1)
                b.ico((xx,yy,z+h+.20),(.55,.55,.40),'leaf_mid' if (i+j)%2 else 'leaf_light',1)
        return
    count=max(2,int(w/.60))
    for i in range(count):
        xx=x-w*.36+i*(w*.72/max(1,count-1));b.ico((xx,y,z+h+.23),(.38,d*.50,.34),'leaf_mid',1)
        if flower:
            b.ico((xx,y-.07,z+h+.48),(.12,.12,.09),'flower_pink',1)

def chair(b,p,rotation=0,color='timber'):
    q=Batch();q.box((0,0,.46),(.48,.48,.07),color);q.box((0,.22,.77),(.48,.06,.46),color)
    for x in [-.18,.18]:
        for y in [-.18,.18]:q.box((x,y,.23),(.04,.04,.46),'charcoal')
    merge(b,q,Matrix.Translation(Vector(p))@Matrix.Rotation(rotation,4,'Z'))

def table(b,p,r=.62):
    x,y,z=p;b.cyl((x,y,z+.76),r,.075,'timber',12);b.cyl((x,y,z+.38),.065,.76,'charcoal',6)
    b.cyl((x,y,z+.04),.28,.06,'charcoal',8)
    b.cyl((x,y,z+.84),.10,.14,'ivory',8)
    for a in [0,2,4]:b.beam((x,y,z+.9),(x+.14*math.cos(a),y+.14*math.sin(a),z+1.08),.018,'leaf_mid',5)

def solar(roof,x,y,z):
    roof.box((x,y,z+.10),(2.4,1.25,.12),'charcoal');roof.box((x,y-.03,z+.18),(2.25,1.12,.035),'solar')
    for dx in [-.75,0,.75]:roof.box((x+dx,y-.03,z+.205),(.025,1.12,.015),'steel')
    roof.box((x,y,z+.21),(2.25,.025,.015),'steel')

def aircon(b,x,y,z):
    b.box((x,y,z+.35),(1.2,.8,.7),'stone')
    for yy in [-.24,-.08,.08,.24]:b.box((x,y+yy,z+.72),(1.0,.025,.025),'charcoal')
    b.cyl((x-.28,y,z+.74),.22,.02,'charcoal',10)

def roof_flat(roof,w,d,z,green=False):
    roof.box((0,0,z),(w+.30,d+.30,.22),'ivory')
    for side in [-1,1]:
        roof.box((side*w/2,0,z+.35),(.15,d,.55),'ivory')
        roof.box((0,side*d/2,z+.35),(w,.15,.55),'ivory')
    aircon(roof,w*.3,d*.3,z+.12)
    for x in [-1.35,1.35]:solar(roof,x,d*.18,z+.14)
    if green:planter(roof,(-w*.28,-d*.27,z+.12),(w*.28,d*.3,.25))

def house(index):
    """Doce villas de volumen escalonado, viviendas con porche y casas con cubierta a dos aguas."""
    old=index%6;w=11+old%3;d=13+old%2
    two=(index%3!=2);setback=index>=6 and two;height=6.25 if two else 3.2
    lower_height=3.15 if setback else height
    facade=['ivory','light_brick','ivory','sand','ivory','stone'][old]
    b=Batch();roof=Batch();b.box((0,0,-.10),(w,d,.20),'concrete');b.box((0,0,.08),(w,d,.16),'concrete')
    front=[(-w*.3,1.65,2.5,1.65,False),(0,1.16,1.3,2.32,True),(w*.3,1.65,2.5,1.65,False)]
    if two and not setback:front += [(x,4.75,2.4,1.75,False) for x in [-w*.29,0,w*.29]]
    wall(b,w,lower_height,(0,-d/2,0),0,front,facade)
    back=[(x,1.65,2.35,1.65,False) for x in [-w*.28,w*.28]]+[(0,1.16,1.3,2.32,True)]
    if two and not setback:back += [(x,4.75,2.1,1.7,False) for x in [-w*.28,w*.28]]
    wall(b,w,lower_height,(0,d/2,0),math.pi,back,facade)
    for side in [-1,1]:
        apertures=[(x,1.65,2.0,1.65,False) for x in [-d*.28,d*.28]]
        if two and not setback:apertures += [(x,4.75,2,1.7,False) for x in [-d*.28,d*.28]]
        wall(b,d,lower_height,(side*w/2,0,0),side*math.pi/2,apertures,facade)
    # Capa de madera y marquesina sobre la puerta, sin bloquear las ventanas.
    for x in [-.95,.95]:
        for dx in [-.12,.12]:b.box((x+dx,-d/2-.14,1.55),(.09,.08,3.0),'timber')
    b.box((0,-d/2-.80,2.70),(3.2,1.7,.16),'charcoal')
    for i in range(3):b.box((0,-d/2-.36-i*.4,.10-i*.025),(2.8+i*.2,.5,.12),'stone')
    if two:
        b.box((0,0,3.08),(w,d,.15),'ivory')
        if setback:
            uw,ud=w*.68,d*.60;ux,uy=-w*.15,d*.12
            for span,point,a in [(uw,(ux,uy-ud/2,3.15),0),(uw,(ux,uy+ud/2,3.15),math.pi),
                                  (ud,(ux+uw/2,uy,3.15),math.pi/2),(ud,(ux-uw/2,uy,3.15),-math.pi/2)]:
                wall(b,span,3.1,point,a,[(-span*.24,1.6,span*.34,2,False),(span*.24,1.6,span*.34,2,False)],'ivory')
            b.box((0,-d*.36,3.18),(w,d*.25,.12),'timber')
            railing(b,(-w/2,-d/2),(w/2,-d/2),3.25)
            for sign in [-1,1]:railing(b,(sign*w/2,-d/2),(sign*w/2,d/2),3.25)
            table(b,(w*.25,-d*.30,3.25),.5);chair(b,(w*.25,-d*.40,3.25))
            planter(b,(-w*.33,-d*.35,3.25),(1.8,.6,.4),True)
        elif index%2==0:
            b.box((0,-d/2-.6,3.05),(w*.7,1.3,.18),'concrete')
            railing(b,(-w*.35,-d/2-1.2),(w*.35,-d/2-1.2),3.15)
            for x in [-w*.35,w*.35]:railing(b,(x,-d/2-.05),(x,-d/2-1.2),3.15)
            planter(b,(w*.22,-d/2-.7,3.15),(1.4,.45,.25),True)
    # Sala y cocina reales, visibles a través del vidrio.
    b.box((-w*.28,-d*.2,.45),(2.6,.85,.55),'denim');b.box((-w*.28,-d*.17,.95),(2.6,.22,.7),'denim')
    b.box((-w*.28,-d*.35,.46),(1.6,.65,.12),'timber')
    b.box((w*.22,d*.3,.5),(3.0,.65,1),'ivory');b.box((w*.22,d*.3,1.04),(3.15,.75,.10),'charcoal')
    b.box((w*.4,d*.27,1.1),(.7,.75,2.2),'stone')
    for x in [-.6,.6]:chair(b,(x,0,.18),math.pi if x<0 else 0)
    table(b,(0,0,.05),.75)
    if two:
        bed_x=-w*.15 if setback else w*.27
        b.box((bed_x,d*.16,3.42),(2.0,2.25,.45),'timber');b.box((bed_x,d*.16,3.72),(1.9,2.2,.20),'cream')
        b.box((bed_x,d*.26,3.9),(1.8,.45,.16),'mint')
    if setback:
        part=Batch();roof_flat(part,uw,ud,height,False);merge(roof,part,Matrix.Translation(Vector((ux,uy,0))))
    elif index%3==1:
        # Cubierta inclinada, con aleros y tejas sugeridas por listones de cumbrera.
        x,y=w/2+.35,d/2+.35;h=height
        roof.add([(-x,-y,h),(x,-y,h),(x,y,h),(-x,y,h),(0,-y,h+1.6),(0,y,h+1.6)],
                 [(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)],'charcoal' if index<6 else 'brick')
        roof.box((0,0,h+1.63),(.18,d+.9,.16),'charcoal')
        roof.box((w*.28,d*.3,h+1.1),(.55,.65,1.9),'brick')
    else:roof_flat(roof,w,d,height,green=index%3==0)
    for sign in [-1,1]:planter(b,(sign*w*.34,-d/2-.7,.12),(1.8,.55,.5),True)
    register('House_'+str(index),b,roof,'residential')

def apartment(index):
    w=22+(index%2)*4;d=24;levels=3+index%3;height=levels*3.1;b=Batch();roof=Batch()
    facade=['ivory','light_brick','stone','ivory','sand','ivory'][index]
    b.box((0,0,-.10),(w,d,.20),'concrete');b.box((0,0,.10),(w,d,.20),'concrete')
    for side,angle,span,point in [(0,0,w,(0,-d/2,0)),(1,math.pi,w,(0,d/2,0)),
                                  (2,math.pi/2,d,(w/2,0,0)),(3,-math.pi/2,d,(-w/2,0,0))]:
        openings=[]
        for floor in range(levels):
            for i in range(4):
                x=-span*.36+i*span*.24
                openings.append((x,1.55+floor*3.1,span*.17,1.95,False))
        if side==0:
            openings=[o for o in openings if o[1]>2 or abs(o[0])>span*.20]
            openings.append((0,1.35,2.8,2.7,True))
        wall(b,span,height,point,angle,openings,facade)
        for floor in range(1,levels):
            local=Batch();z=floor*3.1
            for x in [-span*.28,span*.28]:
                local.box((x,-.75,z),(span*.40,1.5,.18),'ivory')
                railing(local,(x-span*.2,-1.40),(x+span*.2,-1.40),z+.1)
                if floor%2:planter(local,(x+span*.10,-.95,z+.12),(1.4,.5,.3))
            merge(b,local,Matrix.Translation(Vector(point))@Matrix.Rotation(angle,4,'Z'))
    for z in range(levels):b.box((0,0,z*3.1),(w+.20,d+.20,.16),'ivory')
    # Volumen vertical de escalera y marquesina diferencian los accesos.
    b.box((0,-d/2-.23,height/2),(2.9,.15,height),'office_glass')
    b.box((0,-d/2-1.2,2.9),(5,2.5,.18),'charcoal')
    roof_flat(roof,w,d,height,True)
    register('Apartment_'+str(index),b,roof,'apartments')

SHOP_LABELS=['PAN Y PUNTO','CAFE ESQUINA','FARMACIA','TECNO LAB','BICI TALLER','LIBROS',
             'MERCADO FRESCO','VERDE FLOR','SABOR URBANO','ESTUDIO NORTE','ROPA LOCAL','ESPACIO 21']

def shelf(b,p,w=2.4,levels=4,kind=0):
    x,y,z=p;b.box((x,y+.23,z+1.05),(w,.08,2.1),'ivory')
    for side in [-1,1]:b.box((x+side*w/2,y,z+1),(.06,.55,2),'charcoal')
    for row in range(levels):
        zz=z+.22+row*.48;b.box((x,y,zz),(w,.6,.06),'stone')
        for i in range(5):
            xx=x-w*.4+i*w*.2;color=['coral','mustard','mint','denim','cream'][(row+i+kind)%5]
            b.box((xx,y-.02,zz+.18),(w*.13,.35,.30),color)
            b.box((xx,y-.225,zz+.19),(w*.08,.015,.10),'cream')

def counter(b,p,w=2.5):
    x,y,z=p;b.box((x,y,z+.52),(w,.85,1.04),'timber');b.box((x,y,z+1.08),(w+.12,.95,.10),'ivory')
    b.box((x+w*.22,y,z+1.28),(.45,.12,.32),'charcoal');b.box((x+w*.22,y-.08,z+1.28),(.35,.02,.23),'office_glass')
    b.box((x-w*.26,y-.08,z+1.18),(.32,.30,.10),'steel')

def shop(index):
    old=index%6;w=19+(old%2)*3;d=20;levels=2 if index in [3,5,9,11] else 1
    h=3.8+3.1*(levels-1);b=Batch();roof=Batch();paint=['ivory','brick','ivory','charcoal','stone','sand'][old]
    b.box((0,0,-.10),(w,d,.20),'concrete');b.box((0,0,.09),(w,d,.18),'stone')
    opening=[(-w*.28,1.6,w*.35,2.7,False),(0,1.4,2.2,2.8,True),(w*.28,1.6,w*.35,2.7,False)]
    if levels>1:opening += [(x,5.3,2.8,1.8,False) for x in [-w*.32,0,w*.32]]
    wall(b,w,h,(0,-d/2,0),0,opening,paint)
    for side in [-1,1]:
        wall(b,d,h,(side*w/2,0,0),side*math.pi/2,[(y,1.8,3.3,2.1,False) for y in [-5,2,7]],paint)
    wall(b,w,h,(0,d/2,0),math.pi,[(0,1.15,1.3,2.3,True)],paint)
    sign='teal' if index%3==0 else 'charcoal'
    b.box((0,-d/2-.2,3.25),(w*.92,.30,.78),sign)
    b.text(SHOP_LABELS[index],(0,-d/2-.375,3.25),.47,'ivory')
    # Marquesina plana o toldo geométrico, con tirantes y faldón.
    b.box((0,-d/2-1.0,2.80),(w*.96,2.0,.12),'timber' if index%2 else 'ivory')
    for x in [-w*.43,w*.43]:b.beam((x,-d/2,3.0),(x,-d/2-1.7,2.83),.035,'charcoal',6)
    for x in [-w*.42,w*.42]:planter(b,(x,-d/2-1.2,.10),(1.4,.65,.5),index%2==0)
    counter(b,(w*.26,-d*.22,.12),3.5)
    if index in [0,1,8]:
        for x in [-w*.28,-w*.04]:
            for y in [-d*.25,d*.10]:
                table(b,(x,y,.12));chair(b,(x,y-.95,.12));chair(b,(x,y+.95,.12),math.pi)
        b.box((0,d*.37,.60),(w*.8,.9,1.2),'stone');b.box((0,d*.37,1.27),(w*.82,1.0,.12),'charcoal')
        b.box((w*.28,d*.36,1.8),(1.6,.85,1.1),'steel')
        for x in [-w*.25,0]:b.cyl((x,d*.37,1.36),.32,.08,'charcoal',12)
    elif index==9 or index==11:
        for x in [-w*.27,w*.27]:
            for y in [-2,4]:
                b.box((x,y,.85),(2.8,1.2,.12),'timber');b.box((x,y+.28,1.17),(.85,.10,.55),'charcoal');chair(b,(x,y-.9,.12))
    else:
        for x in [-w*.3,0,w*.3]:
            shelf(b,(x,d*.30,.12),3,kind=index)
            if index in [2,5,6,10]:shelf(b,(x,0,.12),2.7,kind=index)
    if levels>1:
        b.box((0,0,3.70),(w,d,.16),'ivory')
        for x in [-w*.3,w*.3]:
            b.box((x,0,4.6),(3,1.4,.14),'timber');chair(b,(x,-1,3.8))
    roof_flat(roof,w,d,h,True)
    register('Shop_'+str(index),b,roof,'shop_'+str(index))

# Sustituye la torre prismática de estudio por tres siluetas de oficina diferenciadas.
def office(index):
    levels=[6,8,10][index];b=Batch();roof=Batch();h=levels*3.3
    b.box((0,0,-.1),(30,30,.2),'concrete')
    top_volumes=[]
    for floor in range(levels):
        z=floor*3.3
        if floor<2:volumes=[(0,0,30,30)]
        elif index==0:volumes=[(0,2,24,25)]
        elif index==1:volumes=[(3,2,21,24)]
        else:volumes=[(-8.3,1,12,27),(8.3,1,12,27)]
        top_volumes=volumes
        for cx,cy,w,d in volumes:
            for side in range(4):
                a=side*math.pi/2;span=w if side%2==0 else d
                point=(cx+(w/2*math.sin(a)),cy-(d/2*math.cos(a)),z)
                local=Batch();local.box((0,0,1.65),(span,.15,3.3),'office_glass' if index!=1 else 'navy')
                count=max(2,round(span/3));step=span/count
                for bay in range(count+1):local.box((-span/2+bay*step,-.14,1.65),(.085,.16,3.3),'ivory' if index!=1 else 'timber')
                for bay in range(count):
                    if (floor+bay+side)%5==0:local.box((-span/2+(bay+.5)*step,-.09,1.05),(step-.14,.035,1.7),'steel')
                local.box((0,-.15,.06),(span,.25,.12),'charcoal')
                merge(b,local,Matrix.Translation(Vector(point))@Matrix.Rotation(a,4,'Z'))
        if floor==2:
            b.box((0,0,6.6),(30,30,.22),'ivory')
            for x in [-11,11]:planter(b,(x,-12,6.75),(4,1.3,.6))
            railing(b,(-15,-15),(15,-15),6.75)
        if index==2 and floor==5:b.box((0,1,z+1.5),(6,5,2.7),'office_glass')
    for cx,cy,w,d in top_volumes:
        part=Batch();roof_flat(part,w,d,h,True);merge(roof,part,Matrix.Translation(Vector((cx,cy,0))))
    # Pórtico, recepción y plaza de acceso mantienen la escala de peatón.
    b.box((0,-16,3.4),(12,2.4,.24),'ivory')
    for x in [-5.6,5.6]:b.box((x,-16.7,1.7),(.30,.30,3.4),'charcoal')
    b.box((0,-15.22,1.5),(4,.05,3),'clear_glass')
    for x in [-2,0,2]:b.box((x,-15.30,1.5),(.08,.08,3),'ivory')
    b.box((0,-15.35,4.1),(14,.20,.85),'charcoal')
    b.text(['NEXO · EMPRESAS','VERTICE · TECNOLOGIA','ALMA · OFICINAS'][index],(0,-15.47,4.1),.44,'ivory')
    for x in [-10,10]:planter(b,(x,-16,.1),(4,1.5,.65))
    register('Tower_'+str(index),b,roof,'office')

def warehouse(index):
    w=32;d=36;h=8;b=Batch();roof=Batch()
    b.box((0,0,-.10),(w,d,.20),'concrete');b.box((0,0,h/2),(w,d,h),'stone')
    for x in range(-15,16,2):b.box((x,-18.08,4),(.08,.12,8),'steel')
    for y in range(-17,18,2):
        for sign in [-1,1]:b.box((sign*16.08,y,4),(.12,.08,8),'steel')
    for x in [-7,3]:
        b.box((x,-18.18,2.35),(7.2,.20,4.7),'charcoal')
        for z in range(10):b.box((x,-18.30,.3+z*.44),(6.8,.10,.35),'concrete')
        for dx in [-3.8,3.8]:b.box((x+dx,-18.5,1),(.20,.20,2),'mustard')
    b.box((11.6,-18.20,1.2),(1.5,.12,2.4),'navy')
    b.box((0,-18.20,6.4),(26,.15,1.1),'charcoal');b.text(['LOGISTICA SUR','ALMACEN 24','TALLER INDUSTRIAL'][index],(0,-18.31,6.4),.65,'ivory')
    for sign in [-1,1]:
        for x in [-10,0,10]:
            local=Batch();panel(local,x,6.2,3.5,1.2)
            merge(b,local,Matrix.Translation(Vector((0,sign*18,0)))@Matrix.Rotation(math.pi if sign==1 else 0,4,'Z'))
    roof_flat(roof,w,d,h)
    for x in [-8,0,8]:
        for y in [-7,0,7]:solar(roof,x,y,h+.2)
    register('Warehouse_'+str(index),b,roof,'industry')

def tree(index,forest=False):
    rng=random.Random(2150+index);b=Batch();species=index%6
    if species==4:
        # Pino: tronco visible, ramas radiales y tres pisos irregulares.
        b.cyl((0,0,3.2),.22,6.4,'wood',8,top=.08)
        for level,(z,r) in enumerate([(3.4,2.8),(5.1,2.2),(6.7,1.6),(8.1,.9)]):
            b.cyl((0,0,z),r,2.8,['leaf_deep','leaf_mid','leaf_shade'][level%3],9,top=.1)
    elif species==5:
        b.cyl((0,0,3.8),.25,7.6,'wood',8,top=.14)
        for z in [i*.35 for i in range(20)]:b.cyl((0,0,z+.25),.26,.055,'timber',8)
        for i in range(10):
            a=i*math.tau/10;u=Vector((math.cos(a),math.sin(a),0));v=Vector((-math.sin(a),math.cos(a),0))
            mid=u*1.8+Vector((0,0,8.3));end=u*4.0+Vector((0,0,6.7))
            b.beam((0,0,7.6),mid,.045,'leaf_deep',5)
            for k in range(5):
                t=k/5;p=Vector((0,0,7.6)).lerp(mid,t) if t<.5 else mid.lerp(end,(t-.5)*2)
                for sign in [-1,1]:
                    tip=p+v*sign*(.65*(1-t)+.22)+u*.55+Vector((0,0,-.3))
                    b.add([p-u*.15,p+u*.55,tip],[(0,1,2)],'leaf_mid' if i%2 else 'leaf_light')
            b.add([mid-v*.18,end,mid+v*.18],[(0,1,2)],'leaf_mid')
    else:
        height=[6.8,7.6,6.4,8.5][species];b.cyl((0,0,1.8),.28,3.6,'wood',8,top=.17)
        # Ensanchamiento de la raíz y tres ramas con sección decreciente.
        b.cyl((0,0,.3),.45,.6,'wood',8,top=.27)
        clusters=[]
        for i in range(5):
            a=i*math.tau/5+.22*species;r=1.25+rng.uniform(-.3,.4);z=height-2+rng.uniform(-.4,.55)
            end=(r*math.cos(a),r*math.sin(a),z)
            b.beam((0,0,2.5),end,.11,'wood',6);clusters.append((end[0],end[1],z+.45))
        clusters += [(0,0,height-.45),(.3,-.2,height-1.8)]
        for i,p in enumerate(clusters):
            color=(['jacaranda','leaf_mid','jacaranda','jacaranda'][i%4] if species==2 else
                   ['leaf_mid','leaf_light','leaf_deep','leaf_mid'][i%4])
            size=(1.65+rng.random()*.25,1.55+rng.random()*.25,1.45+rng.random()*.45)
            b.ico(p,size,color,2)
            if species==3:
                for j in range(2):
                    a=rng.random()*math.tau;b.ico((p[0]+math.cos(a)*1.3,p[1]+math.sin(a)*1.3,p[2]),(.14,.14,.14),'mustard',1)
    if forest:
        for i,v in enumerate(b.vertices):b.vertices[i]=(v[0]*1.25,v[1]*1.25,v[2]*1.3)
    register(('ForestTree_' if forest else 'Tree_')+str(index),b,category='vegetation')

def garden(index):
    b=Batch();w=10.5;y=-11.0
    # Frente abierto para el acceso; zócalo, pilares y listones de madera.
    for sign in [-1,1]:
        b.box((sign*6,y,.18),(8.5,.22,.36),'stone')
        for z in [.55,.8,1.05]:b.box((sign*6,y,z),(8.5,.10,.12),'timber')
        for x in [sign*2,sign*10]:b.box((x,y,.65),(.26,.35,1.3),'ivory')
    for y0 in [-9.7,-10.4]:b.box((0,y0,.09),(1.65,.48,.08),'stone')
    for x in [-7.8,7.8]:planter(b,(x,-9.2,.02),(2.3,1,.35),True)
    b.box((2.3,-10.9,1.1),(.45,.35,.45),'charcoal');b.box((2.3,-11.1,1.2),(.30,.02,.04),'ivory')
    register('Garden_'+str(index),b,category='garden')

def street_props():
    b=Batch()
    for x in [-.8,.8]:b.box((x,0,.28),(.15,.7,.55),'charcoal')
    for y in [-.28,-.09,.09,.28]:b.box((0,y,.52),(2.1,.13,.08),'timber')
    for z in [.80,1.03]:b.box((0,.28,z),(2.1,.10,.16),'timber')
    register('Bench',b)
    b=Batch();b.cyl((0,0,3.6),.08,7.2,'charcoal',8)
    b.beam((0,0,7.1),(0,-1.8,7.0),.09,'charcoal',6);b.box((0,-1.8,6.98),(.45,.95,.14),'charcoal');b.box((0,-1.8,6.9),(.36,.80,.02),'lamp_white')
    register('Lamp',b)
    b=Batch();b.box((0,0,.55),(.62,.62,1.1),'charcoal');b.box((0,-.33,.80),(.40,.02,.18),'black')
    for z in [.16,.32,.48]:b.box((0,-.33,z),(.52,.025,.04),'timber')
    register('Bin',b)
    b=Batch();planter(b,(0,0,0),(2.4,1.0,.5),True);register('Planter',b)
    b=Batch();b.box((0,0,.10),(5,2,.20),'stone')
    for x in [-2.3,2.3]:b.box((x,.6,1.35),(.10,.10,2.7),'charcoal')
    b.box((0,.7,1.5),(4.8,.025,2.2),'clear_glass');b.box((0,0,2.8),(5.4,2.3,.20),'charcoal')
    b.box((0,-.2,2.70),(4.9,.5,.035),'lamp_white');b.box((1.65,.61,1.5),(.8,.04,1.7),'ivory')
    b.text('BUS',(1.65,.56,1.9),.26,'teal')
    for z in [1.1,1.3,1.5]:b.box((1.65,.55,z),(.56,.01,.025),'teal')
    for x in [-1.2,0]:chair(b,(x,.25,.1),math.pi)
    register('BusShelter',b)
    b=Batch();table(b,(0,0,0))
    for x,y,a in [(0,-1,0),(0,1,math.pi),(-1,0,-math.pi/2),(1,0,math.pi/2)]:chair(b,(x,y,0),a)
    b.cyl((0,0,1.45),.035,2.9,'charcoal',6)
    b.cyl((0,0,2.8),1.7,.65,'cream',10,top=.1);register('CafeSet',b)
    b=Batch();b.box((0,0,1.1),(.5,.4,2.2),'charcoal');b.box((0,-.22,1.55),(.36,.03,.55),'teal')
    b.beam((.3,-.1,1.8),(.6,-.15,1.3),.025,'black',6);b.beam((.6,-.15,1.3),(.35,-.2,.6),.025,'black',6)
    register('EVCharger',b)
    b=Batch()
    for x in [-1.8,-.6,.6,1.8]:
        b.beam((x,-.6,0),(x,-.6,.8),.035,'steel',6);b.beam((x,-.6,.8),(x,.6,.8),.035,'steel',6);b.beam((x,.6,.8),(x,.6,0),.035,'steel',6)
    register('BikeRack',b)
    b=Batch();b.box((0,0,.8),(6,2.8,1.6),'timber');b.box((0,0,1.65),(6.2,3,.15),'ivory')
    for x in [-2.8,2.8]:b.box((x,1.2,2),(.12,.12,4),'charcoal')
    b.box((0,0,3.8),(6.4,3.5,.22),'charcoal');b.box((0,-1.8,3.5),(6.2,.15,.7),'teal');b.text('CAFE DEL PATO',(0,-1.9,3.5),.36,'ivory')
    b.box((1.6,0,1.9),(.8,.6,.5),'steel')
    for x in [-1.8,-1.3,-.8]:b.cyl((x,-.6,1.82),.10,.24,'cream',8)
    register('FoodStand',b)

def create_library():
    for i in range(12):house(i);shop(i)
    for i in range(6):apartment(i);tree(i);tree(i,True);garden(i)
    for i in range(3):office(i);warehouse(i)
    street_props()
