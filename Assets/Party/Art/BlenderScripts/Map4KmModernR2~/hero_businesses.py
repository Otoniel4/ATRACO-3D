"""Locales principales nuevos: envolvente con huecos, mobiliario específico, techo y puertas independientes."""
import math
from mesh_tools import Batch
import modern_assets as A

LABELS={'Minimarket':'MINI TODO · MERCADO','MallJewelry':'BRILLA BRILLA · JOYERIA','Bank':'BANCO SIN PRISA',
        'Police':'POLICIA · DISTRITO CENTRAL','Hideout':'TALLER EL PRIMO','FenceGear':'DON TRUEQUE · EQUIPO',
        'PaintGarage':'CAMALEON · AUTO STUDIO','Clothing':'NI ME VISTE · ROPA','Restaurant':'PIZZA PANICO'}

def fridge(b,x,y,z=0):
    b.box((x,y,z+1.10),(1.2,.85,2.2),'ivory');b.box((x,y-.45,z+1.2),(1.05,.06,1.7),'office_glass')
    for row in range(4):
        zz=z+.4+row*.44;b.box((x,y-.46,zz),(1.02,.04,.045),'steel')
        for xx in [-.32,0,.32]:b.cyl((x+xx,y-.50,zz+.15),.08,.24,'coral' if row%2 else 'mint',7)
    b.box((x+.43,y-.51,z+1.2),(.035,.06,.5),'steel')

def cctv(b,x,y,z):
    b.box((x,y,z),(.12,.4,.12),'charcoal');b.box((x,y-.3,z-.05),(.35,.6,.23),'ivory')
    b.cyl((x,y-.62,z-.05),.075,.04,'black',8,direction=(0,-1,0))

def computer(b,x,y,z):
    b.box((x,y,z+.12),(.35,.24,.24),'charcoal');b.box((x,y,z+.38),(.65,.11,.43),'charcoal')
    b.box((x,y-.065,z+.38),(.55,.02,.32),'office_glass');b.box((x,y-.4,z+.02),(.55,.25,.04),'steel')

def office_desk(b,x,y):
    b.box((x,y,.79),(2.6,1.15,.14),'timber')
    for side in [-1,1]:b.box((x+side*.95,y,.39),(.25,.9,.78),'ivory')
    computer(b,x,y,.86);A.chair(b,(x,y+.95,0),math.pi)

def clothing(b,x,y):
    for dx in [-1.2,1.2]:b.box((x+dx,y,.90),(.08,.65,1.8),'charcoal')
    b.beam((x-1.2,y,1.8),(x+1.2,y,1.8),.035,'steel',6)
    for i in range(6):
        xx=x-1+i*.40;color=['coral','denim','mint','mustard','ivory','lavender'][i]
        b.box((xx,y,1.17),(.28,.40,.80),color)
        b.box((xx-.18,y,1.43),(.17,.45,.35),color);b.box((xx+.18,y,1.43),(.17,.45,.35),color)
        b.beam((xx,y,1.65),(xx,y,1.80),.015,'steel',5)

def leaf(door_width,glass=True):
    b=Batch();w=door_width;h=2.65
    for x in [0,w]:b.box((x,0,h/2),(.075,.12,h),'charcoal')
    for z in [.04,h]:b.box((w/2,0,z),(w,.12,.08),'charcoal')
    b.box((w/2,0,h/2),(w-.06,.025,h-.08),'clear_glass' if glass else 'teal')
    b.box((w*.85,-.10,1.25),(.04,.05,.42),'steel')
    return b

def make(identifier):
    w,d,h=(16,14,4.8) if identifier=='Bank' else ((14,12,4.4) if identifier=='Police' else (12,10,4.2))
    b=Batch();furniture=Batch();roof=Batch();accent='denim' if identifier=='Police' else ('charcoal' if identifier=='MallJewelry' else 'teal')
    b.box((0,0,-.10),(w,d,.20),'concrete');b.box((0,0,.08),(w,d,.16),'stone')
    door_width=4.8 if identifier=='PaintGarage' else 2.2
    pane_width=(w-door_width)/2-.55
    openings=[(0,1.35,door_width,2.7,'HINGE')]
    openings += [(sign*(door_width/2+.22+pane_width/2),1.75,pane_width,2.85,False) for sign in [-1,1]]
    A.wall(b,w,h,(0,-d/2,0),0,openings,'ivory')
    for side in [-1,1]:A.wall(b,d,h,(side*w/2,0,0),side*math.pi/2,[(-d*.22,1.95,2.4,2.3,False),(d*.22,1.95,2.4,2.3,False)],'ivory')
    A.wall(b,w,h,(0,d/2,0),math.pi,[(-w*.28,2.3,2,1.4,False),(0,1.35,1.2,2.7,'HINGE'),(w*.28,2.3,2,1.4,False)],'ivory')
    b.box((0,-d/2-.20,3.55),(w+.3,.32,.8),accent)
    b.text(LABELS[identifier],(0,-d/2-.385,3.55),min(.44,w/len(LABELS[identifier])*1.45),'ivory')
    b.box((0,-d/2-.90,3.05),(w+.4,1.85,.15),'timber')
    for x in [-w*.45,w*.45]:b.box((x,-d/2-1.6,1.55),(.14,.14,3.1),'charcoal')
    for x in [-w*.37,w*.37]:A.planter(b,(x,-d/2-1,.12),(1.5,.55,.45),True)
    for x in [-w*.43,w*.43]:b.box((x,-d/2-.15,2.95),(.24,.25,.10),'lamp_white')
    A.roof_flat(roof,w,d,h,identifier in ['Restaurant','Clothing'])
    roof.box((0,-d*.25,h+.15),(w*.34,d*.25,.15),'charcoal')
    roof.box((0,-d*.25,h+.25),(w*.32,d*.23,.08),'clear_glass')
    cctv(furniture,-w/2+.4,d/2-.4,3.2)
    # Interruptor, alarma y reloj dan escala humana a los paños interiores.
    furniture.box((w/2-.15,-d*.25,1.3),(.08,.18,.3),'charcoal')
    furniture.cyl((0,d/2-.16,3.15),.35,.04,'charcoal',16,direction=(0,-1,0))
    furniture.cyl((0,d/2-.20,3.15),.30,.02,'cream',16,direction=(0,-1,0))
    furniture.box((0,d/2-.23,3.23),(.025,.015,.2),'charcoal')
    furniture.box((.09,d/2-.23,3.15),(.2,.015,.025),'charcoal')
    if identifier=='Minimarket':
        for x in [-3.4,0,3.4]:
            for y in [-.7,1.8]:A.shelf(furniture,(x,y,.12),2.5,4,int(x)%3)
        for x in [-4,-2,2,4]:fridge(furniture,x,d/2-.65,.12)
        A.counter(furniture,(3,-d/2+1.7,.12),3.0)
        for x in [-4,-3.2]:
            furniture.box((x,-3,.42),(.65,.6,.65),'teal')
            for dx in [-.2,0,.2]:furniture.ico((x+dx,-3,.85),(.12,.12,.12),'mustard',1)
        # Caja de leche geométrica apoyada en la cubierta.
        roof.box((w*.32,d*.25,h+.75),(1.0,.85,1.3),'ivory');roof.box((w*.32,d*.25,h+1.45),(1.08,.93,.15),'coral')
    elif identifier=='Bank':
        for x in [-5,-1.6,1.8,5.2]:
            A.counter(furniture,(x,0,.12),2.7)
            furniture.box((x,.25,1.65),(2.7,.06,.95),'clear_glass');A.chair(furniture,(x,1.1,.12),math.pi)
        for x in [-4,-1.8,.4,2.6]:A.chair(furniture,(x,-3.8,.12))
        for x in [-6.4,6.4]:
            furniture.box((x,-4.6,1.1),(.9,.7,2.2),'charcoal');furniture.box((x,-5.0,1.5),(.65,.04,.55),'office_glass')
            furniture.box((x,-5.05,.90),(.45,.04,.08),'steel')
        # Cámara acorazada y puerta circular visible en el fondo.
        for sign in [-1,1]:furniture.box((sign*4.9,3,1.9),(6.2,.24,3.8),'stone')
        furniture.box((0,3,3.4),(3.6,.24,.8),'stone')
        furniture.cyl((0,3,1.7),1.5,.25,'steel',20,direction=(0,-1,0))
        furniture.cyl((0,2.82,1.7),1.15,.10,'charcoal',20,direction=(0,-1,0))
        furniture.cyl((0,2.74,1.7),.4,.08,'gold',12,direction=(0,-1,0))
        for a in [0,math.pi/2,math.pi,math.pi*1.5]:furniture.beam((0,2.68,1.7),(.58*math.cos(a),2.68,1.7+.58*math.sin(a)),.04,'steel',6)
        for x in [-5,5]:office_desk(furniture,x,5)
        for x in [-5,-2,1,4]:
            furniture.cyl((x,-2.2,.5),.035,1,'steel',8);furniture.cyl((x,-2.2,.05),.18,.08,'steel',8)
        furniture.beam((-5,-2.2,.95),(4,-2.2,.95),.035,'navy',6)
    elif identifier=='MallJewelry':
        for x in [-3.6,0,3.6]:
            for y in [-1.5,1.2]:
                furniture.box((x,y,.5),(2.3,1.1,1),'ivory');furniture.box((x,y,1.25),(2.3,1.1,.5),'clear_glass')
                furniture.box((x,y,1.0),(2.12,.92,.05),'charcoal')
                for xx in [-.65,0,.65]:
                    furniture.cyl((x+xx,y,1.1),.15,.05,'gold',10);furniture.ico((x+xx,y,1.22),(.13,.13,.16),'glass',1)
        A.counter(furniture,(0,3.7,.12),3.0)
        for x in [-4,4]:furniture.box((x,4.3,1.5),(1.2,.9,2.8),'charcoal')
    elif identifier=='Police':
        A.counter(furniture,(-3,-2,.12),4);office_desk(furniture,3,-1)
        for separator in [-6,-2,2,6]:furniture.box((separator,3.2,1.55),(.12,4.8,3.1),'stone')
        for x in [-4,0,4]:
            for xx in [-1.6,-1.2,-.8,-.4,0,.4,.8,1.2,1.6]:furniture.box((x+xx,.8,1.5),(.06,.06,3),'steel')
            furniture.box((x,3.5,.45),(2.2,.75,.3),'concrete')
            furniture.box((x,4.8,1.0),(1.8,.9,.6),'charcoal');furniture.box((x,4.8,1.38),(1.8,.9,.15),'denim')
    elif identifier=='Restaurant':
        A.counter(furniture,(2.7,1.5,.12),4.5)
        furniture.box((0,4.0,.55),(9,.7,1.1),'steel');furniture.box((0,4.0,1.15),(9,.85,.10),'charcoal')
        furniture.box((3.2,3.9,1.7),(2.2,.85,1.2),'steel');furniture.box((3.2,3.44,1.6),(1.5,.05,.5),'black')
        furniture.box((3.2,3.8,2.7),(2.6,1.1,.25),'steel');furniture.box((3.2,4,3.2),(.8,.6,.9),'steel')
        for x in [-3.2,0,3.2]:
            for y in [-3,-.8] if x<1 else [-2.8]:
                A.table(furniture,(x,y,.12),.55);A.chair(furniture,(x-.85,y,.12),-math.pi/2);A.chair(furniture,(x+.85,y,.12),math.pi/2)
        for x in [1.7,2.7,3.7]:furniture.cyl((x,1.5,1.32),.35,.07,'mustard',12)
    elif identifier=='Clothing':
        for x in [-3.4,0,3.4]:clothing(furniture,x,2.3)
        for x in [-3.4,3.4]:clothing(furniture,x,-.8)
        A.counter(furniture,(0,3.7,.12),2.6)
        for x in [-3.6,3.6]:
            furniture.cyl((x,-3.9,.12),.42,.18,'stone',12)
            furniture.box((x,-3.9,.62),(.45,.28,.85),'coral' if x<0 else 'denim')
            furniture.ico((x,-3.9,1.43),(.23,.2,.26),'cream',1)
            for dx in [-.15,.15]:furniture.beam((x+dx,-3.9,.5),(x+dx,-3.9,.15),.075,'charcoal',6)
    elif identifier=='PaintGarage':
        for x in [-2.2,2.2]:
            furniture.box((x,0,1.5),(.35,.45,3),'denim');furniture.box((x,0,.3),(.6,4,.20),'charcoal')
        furniture.box((0,0,.25),(4,4.5,.20),'steel')
        furniture.box((0,4,.5),(8,.8,1),'coral');furniture.box((0,4,1.08),(8.2,.9,.12),'charcoal')
        for x in [-3,-1,1,3]:
            furniture.box((x,4.2,1.8),(1.1,.15,1.3),'charcoal')
            for z in [1.5,1.8,2.1]:furniture.box((x,4.09,z),(.75,.08,.06),'steel')
        for x in [-4,4]:
            for z in [.5,1.2]:furniture.cyl((x,2,z),.45,.40,'black',12,direction=(0,1,0))
    elif identifier=='FenceGear':
        for x in [-3.8,0,3.8]:A.shelf(furniture,(x,3.8,.12),2.4,4,1)
        A.counter(furniture,(3,-1.7,.12),3.5)
        for x in [-3,0]:
            furniture.box((x,0,.55),(1.3,1.2,1.1),'wood');furniture.box((x,0,1.17),(1.1,.8,.16),'teal')
            furniture.box((x,0,1.5),(.4,.4,.5),'charcoal')
    else:
        office_desk(furniture,2,2.8)
        furniture.box((-3,1.5,.5),(3,.9,.7),'denim');furniture.box((-3,1.8,1.0),(3,.23,.7),'denim')
        furniture.box((-3,-.2,.55),(1.7,.8,.12),'timber')
        furniture.box((0,4.7,2.0),(3.2,.15,1.8),'charcoal');furniture.box((0,4.59,2.0),(2.9,.03,1.5),'cream')
        for x,y in [(-.8,1.8),(.2,2.2),(.8,1.6)]:furniture.box((x,4.56,y),(.5,.02,.3),'coral')
        for x in [-4,4]:furniture.box((x,3.8,1.1),(1.1,.8,2.2),'teal')
    A.register('Hero_'+identifier,b,roof,'hero_business')
    A.register('Hero_'+identifier+'_Furniture',furniture,category='interior')
    A.register('Hero_'+identifier+'_Door',leaf(door_width/2 if identifier!='PaintGarage' else door_width,True),category='hinged_door')
    A.register('Hero_'+identifier+'_RearDoor',leaf(1.2,False),category='hinged_door')
    return {'id':identifier,'width':w,'depth':d,'height':h,'door_width':door_width}

def make_all():return {identifier:make(identifier) for identifier in LABELS}
