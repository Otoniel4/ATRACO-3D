"""Objetos propios low poly con detalles de función, geometría compartida y colores planos."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
import mesh_tools as M
from mesh_tools import Batch
BASE=Path(__file__).resolve().parent;C=json.loads((BASE/'settings.json').read_text())
LIB={};CATALOG=[]


def palette():
    for name,value in C['palette'].items():
        rgb=[int(value[i:i+2],16)/255 for i in [0,2,4]]
        rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
        mat=bpy.data.materials.get('Life5_'+name) or bpy.data.materials.new('Life5_'+name);mat.use_nodes=True;mat.diffuse_color=rgba
        shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value=rgba;shader.inputs['Roughness'].default_value=.72
        if name in ['metal','gold']:shader.inputs['Metallic'].default_value=.65
        if name=='glass':shader.inputs['Alpha'].default_value=.16;shader.inputs['Roughness'].default_value=.18
        M.INDEX[name]=len(M.MATERIALS);M.MATERIALS.append(mat)


def merge(target,source,p=(0,0,0),angle=0,scale=1):
    transform=Matrix.Translation(Vector(p))@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)
    target.add(source.vertices,source.faces,0,transform)
    target.materials[-len(source.faces):]=source.materials


def chamfer(b,p,size,color,cut=.035):
    x,y,z=[a*.5 for a in size];c=min(cut,x*.4,y*.4)
    ring=[(-x+c,-y),(x-c,-y),(x,-y+c),(x,y-c),(x-c,y),(-x+c,y),(-x,y-c),(-x,-y+c)]
    vertices=[(p[0]+xx,p[1]+yy,p[2]+zz) for zz in [-z,z] for xx,yy in ring]
    faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    b.add(vertices,faces,color)


def buttons(b,p,nx=3,ny=4,spacing=.045):
    for x in range(nx):
        for y in range(ny):b.box((p[0]+x*spacing,p[1]+y*spacing,p[2]),(.028,.028,.012),'ivory' if y<3 else 'green')


def bottle(b,p,color='teal',r=.055,h=.23):
    x,y,z=p;b.cyl((x,y,z+h*.40),r,h*.8,color,8);b.cyl((x,y,z+h*.85),r*.50,h*.16,color,8)
    b.cyl((x,y,z+h*.98),r*.55,h*.07,'ivory',8);b.cyl((x,y,z+h*.43),r*1.012,h*.29,'paper',8)


def carton(b,p,color='denim'):
    x,y,z=p;b.box((x,y,z+.13),(.13,.11,.26),color)
    b.add([(x-.065,y-.055,z+.26),(x+.065,y-.055,z+.26),(x+.065,y+.055,z+.26),(x-.065,y+.055,z+.26),
           (x-.065,y,z+.32),(x+.065,y,z+.32)],[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],'paper')
    b.box((x,y-.058,z+.14),(.09,.008,.09),'cream')


def gondola():
    b=Batch();w=2.4;d=.85
    for x in [-w/2,w/2]:b.box((x,0,1.05),(.055,d,2.1),'metal')
    b.box((0,.35,1.05),(w,.045,2.1),'ivory')
    for level in range(5):
        z=.15+level*.39;b.box((0,0,z),(w,.88,.045),'metal');b.box((0,-.45,z+.035),(w,.045,.09),'teal')
        for j in range(8):
            x=-1.02+j*.29
            if level%3==0:bottle(b,(x,-.05,z+.03),['teal','coral','green'][j%3])
            elif level%3==1:carton(b,(x,-.03,z+.03),['denim','orange','mint'][j%3])
            else:
                b.cyl((x,0,z+.14),.085,.20,['red','yellow','green'][j%3],10);b.cyl((x,0,z+.245),.088,.015,'metal',10)
            b.box((x,-.477,z+.035),(.13,.006,.045),'paper')
    return b


def fridge():
    b=Batch();chamfer(b,(0,0,1.15),(1.15,.80,2.3),'ivory')
    b.box((0,-.43,1.20),(1.02,.025,1.87),'screen')
    for level in range(5):
        z=.29+level*.37;b.box((0,-.46,z),(.98,.10,.03),'metal')
        for j in range(5):bottle(b,(-.38+j*.19,-.46,z+.025),['coral','teal','green'][level%3],.045,.25)
    b.box((0,-.50,1.22),(1.0,.012,1.91),'glass')
    for x in [-.53,.53]:b.box((x,-.50,1.23),(.05,.04,1.99),'dark')
    for z in [.24,2.21]:b.box((0,-.50,z),(1.10,.04,.05),'dark')
    b.box((.44,-.55,1.25),(.035,.06,.56),'metal')
    for x in range(10):b.box((-.45+x*.10,-.42,.13),(.045,.025,.10),'dark')
    b.box((0,-.50,2.25),(.80,.02,.05),'paper');return b


def terminal():
    b=Batch();chamfer(b,(0,0,.035),(.22,.33,.07),'dark',.018)
    b.box((0,.07,.09),(.16,.13,.025),'screen');buttons(b,(-.06,-.09,.08),3,3,.047)
    b.box((0,-.17,.07),(.13,.015,.02),'rubber');return b


def register():
    b=Batch();chamfer(b,(0,0,.10),(.48,.40,.20),'ivory')
    b.box((0,-.21,.09),(.37,.016,.075),'dark');b.box((0,-.225,.11),(.10,.018,.018),'metal')
    b.cyl((0,.06,.29),.035,.25,'metal',8)
    b.box((0,.06,.46),(.43,.07,.28),'dark');b.box((0,.016,.46),(.37,.012,.22),'screen')
    for x in [-.12,0,.12]:b.box((x,.007,.47),(.07,.005,.04),'mint')
    b.box((.24,.05,.16),(.15,.18,.12),'dark');b.box((.24,-.02,.235),(.11,.09,.004),'paper')
    return b


def checkout():
    b=Batch();chamfer(b,(0,0,.48),(3.0,.98,.96),'teal')
    b.box((0,0,1.0),(3.1,1.10,.10),'ivory');b.box((-.55,0,1.06),(1.42,.73,.025),'rubber')
    for x in [-1.22,.12]:b.cyl((x,0,1.07),.07,.78,'metal',10,direction=(0,1,0))
    b.box((.38,-.03,1.075),(.34,.34,.018),'screen');merge(b,register(),(.82,.06,1.06),math.pi)
    merge(b,terminal(),(.48,.30,1.065),math.pi)
    for x in [-1.2,-.4,.4,1.2]:b.box((x,-.502,.55),(.025,.02,.70),'dark')
    return b


def produce():
    b=Batch();chamfer(b,(0,0,.43),(1.8,.95,.86),'wood')
    for x in [-.86,0,.86]:b.box((x,0,.88),(.045,.92,.20),'cream')
    for y in [-.45,.45]:b.box((0,y,.88),(1.8,.045,.20),'cream')
    for i in range(8):
        for j in range(3):b.ico((-.73+i*.20,-.26+j*.24,.94+(i%2)*.035),(.11,.105,.105),['red','green','orange'][i%3],1)
    b.box((0,-.50,.74),(.58,.025,.18),'dark');b.text('FRESCO',(0,-.518,.75),.10,'paper');return b


def basket():
    b=Batch();b.box((0,0,.025),(.38,.28,.05),'teal')
    for z in [.08,.15,.22]:
        for y in [-.15,.15]:b.box((0,y,z),(.40,.025,.025),'teal')
        for x in [-.20,.20]:b.box((x,0,z),(.025,.30,.025),'teal')
    for i in range(6):
        x=-.19+i*.076
        for y in [-.15,.15]:b.box((x,y,.13),(.016,.025,.25),'teal')
    for side in [-1,1]:
        b.beam((side*.17,-.12,.23),(side*.17,0,.43),.012,'dark',5)
        b.beam((side*.17,0,.43),(side*.17,.12,.23),.012,'dark',5)
    return b


def bag():
    b=Batch();chamfer(b,(0,0,-.17),(.28,.16,.34),'paper',.025)
    b.box((0,-.086,-.17),(.15,.008,.11),'teal')
    for y in [-.065,.065]:
        for side in [-1,1]:b.beam((side*.07,y,-.015),(side*.07,y,.09),.009,'wood',5)
        b.beam((-.07,y,.09),(.07,y,.09),.009,'wood',5)
    return b


def display_case():
    b=Batch();chamfer(b,(0,0,.45),(2.25,1.0,.9),'ivory')
    b.box((0,0,.93),(2.1,.86,.04),'dark')
    for x in [-1.10,1.10]:
        for y in [-.48,.48]:b.box((x,y,1.15),(.025,.025,.47),'gold')
    for y in [-.48,.48]:b.box((0,y,1.15),(2.2,.012,.45),'glass')
    b.box((0,0,1.39),(2.25,1.0,.025),'glass')
    for x in [-.65,0,.65]:
        b.box((x,0,.98),(.49,.55,.035),'denim')
        for j in range(12):
            a=j*math.tau/12;b.beam((x+.13*math.cos(a),.16*math.sin(a),1.03),(x+.13*math.cos(a+.5),.16*math.sin(a+.5),1.03),.012,'gold',5)
        b.ico((x,-.14,1.06),(.045,.035,.06),'glass',1)
    return b


def necklace_bust():
    b=Batch();b.cyl((0,0,.025),.20,.05,'gold',10)
    b.cyl((0,0,.22),.13,.40,'ivory',10,top=.22)
    b.cyl((0,0,.47),.075,.13,'ivory',10)
    for j in range(16):
        a=j*math.tau/16;b.beam((.17*math.cos(a),-.12+.025*math.sin(a),.35+.10*math.sin(a)),
            (.17*math.cos(a+.393),-.12+.025*math.sin(a+.393),.35+.10*math.sin(a+.393)),.012,'gold',5)
    b.ico((0,-.15,.23),(.04,.02,.05),'glass',1);return b


def desk():
    b=Batch();chamfer(b,(0,0,.77),(2.4,.95,.12),'wood')
    for x in [-.92,.92]:chamfer(b,(x,0,.36),(.39,.78,.72),'ivory')
    for x in [-.92,.92]:
        for z in [.24,.48]:b.box((x,-.405,z),(.29,.025,.035),'metal')
    b.cyl((.18,.12,.94),.03,.28,'metal',6);b.box((.18,.12,1.16),(.72,.055,.43),'dark')
    b.box((.18,.086,1.16),(.65,.01,.36),'screen');b.box((.18,-.25,.85),(.50,.19,.035),'dark')
    for i in range(10):
        for j in range(3):b.box((-.035+i*.047,-.31+j*.045,.872),(.03,.028,.008),'ivory')
    b.box((.67,-.20,.86),(.075,.12,.035),'dark')
    for j in range(4):b.box((-.70,-.06,.84+j*.006),(.35,.40,.005),'paper')
    return b


def chair():
    b=Batch();chamfer(b,(0,0,.48),(.48,.48,.12),'denim')
    chamfer(b,(0,.23,.82),(.48,.10,.55),'denim');b.cyl((0,0,.26),.04,.40,'metal',8)
    for i in range(5):
        a=i*math.tau/5;b.beam((0,0,.13),(.30*math.cos(a),.30*math.sin(a),.08),.022,'metal',5)
        b.cyl((.30*math.cos(a),.30*math.sin(a),.05),.045,.035,'rubber',6,direction=(-math.sin(a),math.cos(a),0))
    return b


def atm():
    b=Batch();chamfer(b,(0,0,1.02),(.92,.72,2.04),'dark',.07)
    b.box((0,-.38,1.35),(.60,.04,.44),'metal');b.box((0,-.405,1.35),(.47,.012,.33),'screen')
    for side in [-1,1]:
        for z in [1.24,1.35,1.46]:b.box((side*.27,-.416,z),(.035,.025,.04),'ivory')
    buttons(b,(-.08,-.44,.99),3,4,.052)
    b.box((0,-.40,.75),(.42,.045,.07),'rubber');b.box((.27,-.40,1.02),(.18,.025,.035),'green')
    b.text('CAJERO',(0,-.371,1.83),.12,'paper');return b


def stanchion():
    b=Batch();b.cyl((0,0,.03),.19,.06,'metal',12);b.cyl((0,0,.52),.03,.98,'metal',8)
    b.cyl((0,0,1.0),.055,.09,'dark',8);return b


def clothing_rack():
    b=Batch()
    for x in [-1.10,1.10]:b.box((x,0,.92),(.05,.06,1.84),'metal');b.box((x,0,.04),(.10,.75,.07),'dark')
    b.beam((-1.1,0,1.82),(1.1,0,1.82),.028,'metal',8)
    for i in range(7):
        x=-.90+i*.30;color=['coral','denim','mint','cream'][i%4]
        b.beam((x,0,1.80),(x,0,1.64),.008,'metal',5)
        b.beam((x,0,1.66),(x-.12,0,1.54),.01,'wood',5);b.beam((x,0,1.66),(x+.12,0,1.54),.01,'wood',5)
        chamfer(b,(x,0,1.16),(.20,.37,.75),color,.025)
        for side in [-1,1]:b.box((x,side*.24,1.42),(.18,.17,.22),color)
        b.box((x-.11,-.10,1.31),(.01,.06,.10),'paper')
    return b


def folded_table():
    b=Batch();chamfer(b,(0,0,.78),(2.0,1.0,.10),'wood')
    for x in [-.8,.8]:b.box((x,0,.38),(.09,.80,.76),'dark')
    for x in [-.65,0,.65]:
        for j in range(4):chamfer(b,(x,0,.87+j*.07),(.47,.52,.065),['denim','coral','mint','cream'][j],.025)
    return b


def mannequin():
    b=Batch();b.cyl((0,0,.035),.30,.07,'dark',12)
    for x in [-.11,.11]:b.beam((x,0,.08),(x,0,.78),.055,'ivory',6)
    b.cyl((0,0,1.05),.18,.62,'cream',8,top=.23)
    b.ico((0,0,1.59),(.13,.12,.17),'ivory',1)
    for side in [-1,1]:b.beam((side*.21,0,1.3),(side*.32,0,.93),.05,'ivory',6)
    b.box((0,0,1.10),(.38,.25,.45),'teal');return b


def coffee_machine():
    b=Batch();chamfer(b,(0,0,.25),(.75,.48,.50),'metal')
    b.box((0,-.26,.15),(.62,.14,.035),'dark');b.box((0,-.29,.12),(.57,.17,.018),'metal')
    for x in [-.18,.18]:
        b.cyl((x,-.27,.32),.05,.11,'dark',8);b.beam((x,-.31,.32),(x,-.45,.32),.02,'rubber',6)
        b.cyl((x,-.27,.22),.012,.10,'metal',6)
    for x in [-.24,-.08,.08,.24]:b.cyl((x,-.25,.43),.024,.025,'dark',8,direction=(0,-1,0))
    return b


def oven():
    b=Batch();chamfer(b,(0,0,.55),(1.4,.85,1.1),'metal')
    b.box((0,-.45,.57),(1.20,.03,.66),'dark');b.box((0,-.47,.57),(1.05,.015,.48),'screen')
    b.box((0,-.50,.88),(.95,.055,.035),'metal')
    for x in [-.45,-.15,.15,.45]:b.cyl((x,-.46,1.0),.045,.055,'dark',10,direction=(0,-1,0))
    for z in [.10,.16,.22]:b.box((0,-.44,z),(1.2,.02,.025),'dark')
    return b


def pizza():
    b=Batch();b.cyl((0,0,.015),.34,.03,'ivory',16);b.cyl((0,0,.043),.29,.05,'orange',16)
    b.cyl((0,0,.072),.25,.012,'yellow',16)
    for i in range(9):
        a=i*2.39996;r=.06+.02*i;b.cyl((r*math.cos(a),r*math.sin(a),.085),.035,.014,'red',8)
    return b


def dining_table():
    b=Batch();b.cyl((0,0,.78),.64,.07,'wood',14);b.cyl((0,0,.39),.045,.76,'dark',8)
    b.cyl((0,0,.04),.35,.06,'dark',10)
    for x in [-.28,.28]:
        b.cyl((x,0,.83),.17,.022,'ivory',12)
        b.box((x+.20,0,.84),(.016,.20,.008),'metal');b.box((x-.20,0,.84),(.012,.20,.008),'metal')
        b.cyl((x,.30,.90),.05,.17,'glass',8,top=.065)
    b.box((0,.25,.89),(.13,.08,.14),'paper');return b


def toolbox():
    b=Batch();chamfer(b,(0,0,.46),(.95,.55,.92),'coral')
    for z in [.20,.39,.58,.77]:
        b.box((0,-.29,z),(.83,.025,.14),'red');b.box((0,-.315,z+.02),(.56,.03,.025),'metal')
    for x in [-.36,.36]:
        for y in [-.20,.20]:b.cyl((x,y,.06),.06,.04,'rubber',8,direction=(1,0,0))
    for i in range(5):b.beam((-.32+i*.15,-.07,.95),(-.32+i*.15,.20,.95),.015,'metal',6)
    b.box((.50,.0,.75),(.10,.50,.035),'metal');return b


def compressor():
    b=Batch();b.cyl((0,0,.42),.27,.85,'teal',12,direction=(1,0,0));chamfer(b,(0,0,.79),(.38,.36,.22),'dark')
    for x in [-.35,.35]:b.cyl((x,.19,.15),.14,.08,'rubber',10,direction=(0,1,0))
    b.cyl((.12,-.23,.84),.07,.025,'paper',12,direction=(0,-1,0));b.beam((.12,-.25,.84),(.14,-.25,.88),.007,'dark',5)
    points=[(.40,-.1,.7),(.65,-.2,.3),(.55,-.3,.1),(.35,-.3,.2),(.65,-.4,.4)]
    for a,c in zip(points,points[1:]):b.beam(a,c,.017,'rubber',5)
    return b


def equipment_shelf():
    b=Batch()
    for x in [-1,1]:b.box((x,0,1.0),(.05,.55,2),'dark')
    for z in [.15,.65,1.15,1.65]:
        b.box((0,0,z),(2.0,.55,.04),'wood')
        for i in range(6):
            x=-.82+i*.33;chamfer(b,(x,0,z+.13),(.20,.18,.22),['teal','dark','orange'][i%3],.02)
            b.beam((x-.05,0,z+.24),(x-.05,0,z+.37),.009,'dark',5)
            b.box((x,.0,z+.16),(.12,.19,.05),'screen')
    return b


def locker():
    b=Batch();chamfer(b,(0,0,1.0),(1.4,.60,2.0),'teal')
    for x in [-.46,0,.46]:
        b.box((x,-.31,1),(.43,.025,1.9),'mint');b.box((x+.14,-.34,1.05),(.025,.035,.18),'metal')
        for z in [1.65,1.73,1.81]:b.box((x,-.33,z),(.25,.01,.025),'dark')
        b.box((x,-.34,1.42),(.11,.008,.06),'paper')
    return b


def sofa():
    b=Batch();chamfer(b,(0,0,.36),(2.5,.85,.55),'denim',.08)
    chamfer(b,(0,.36,.80),(2.5,.22,.72),'teal',.08)
    for x in [-1.15,1.15]:chamfer(b,(x,0,.64),(.24,.94,.53),'teal',.07)
    for x in [-.70,0,.70]:chamfer(b,(x,-.05,.65),(.66,.63,.15),'denim',.07)
    return b


def planning_board():
    b=Batch();b.box((0,0,1.6),(2.8,.13,1.8),'wood');b.box((0,-.08,1.6),(2.65,.025,1.65),'cream')
    for i in range(8):
        x=-1.02+(i%4)*.68;z=1.15+(i//4)*.88;b.box((x,-.10,z),(.47,.015,.55),['paper','mint','pink'][i%3])
        b.ico((x,-.13,z+.22),(.025,.02,.025),'red',1)
    for x in [-1.05,-.35,.35]:b.beam((x,-.13,1.48),(x+.65,-.13,1.85),.01,'coral',4)
    return b


def dining_chair():
    b=Batch();chamfer(b,(0,0,.46),(.48,.48,.09),'wood')
    chamfer(b,(0,0,.52),(.43,.43,.065),'mint')
    for x in [-.18,.18]:
        for y in [-.18,.18]:b.beam((x,y,.04),(x,y,.46),.025,'wood',6)
    for x in [-.19,.19]:b.beam((x,.19,.43),(x,.24,.95),.025,'wood',6)
    chamfer(b,(0,.23,.81),(.45,.07,.28),'wood');return b


def vault_door():
    b=Batch();center=(0,0,1.52)
    b.cyl(center,1.52,.28,'metal',24,direction=(0,-1,0))
    b.cyl((0,-.18,1.52),1.39,.13,'dark',24,direction=(0,-1,0))
    b.cyl((0,-.27,1.52),1.27,.06,'metal',24,direction=(0,-1,0))
    b.cyl((0,-.34,1.52),.18,.08,'gold',12,direction=(0,-1,0))
    for i in range(12):
        a=i*math.tau/12;b.cyl((1.16*math.cos(a),-.325,1.52+1.16*math.sin(a)),.055,.035,'dark',8,direction=(0,-1,0))
    for i in range(5):
        a=i*math.tau/5;b.beam((0,-.40,1.52),(.50*math.cos(a),-.40,1.52+.50*math.sin(a)),.03,'gold',6)
    b.box((.76,-.35,1.4),(.27,.10,.40),'dark');b.box((.76,-.41,1.49),(.18,.014,.09),'screen')
    for x in range(3):
        for z in range(3):b.box((.69+x*.065,-.414,1.25+z*.06),(.038,.012,.035),'ivory')
    return b


def vehicle_lift():
    b=Batch();b.box((0,0,.09),(4.2,4.5,.18),'metal')
    for x in [-2.2,2.2]:
        b.box((x,0,1.5),(.35,.45,3),'denim');b.box((x,0,.04),(.65,.85,.08),'dark')
        b.box((x,0,.38),(.48,.62,.28),'metal');b.box((x,-.25,1.12),(.20,.10,.32),'dark')
        for y in [-1.4,1.4]:b.box((x*.50,y,.22),(2.2,.20,.18),'dark')
    for x in [-1.65,1.65]:b.box((x,0,.195),(.50,4.3,.03),'rubber')
    return b


def security_camera():
    b=Batch();b.box((0,.12,0),(.22,.05,.22),'metal');b.beam((0,.10,0),(0,-.13,-.06),.035,'metal',6)
    chamfer(b,(0,-.30,-.07),(.25,.43,.17),'ivory',.025)
    b.cyl((0,-.54,-.07),.07,.035,'dark',10,direction=(0,-1,0));b.cyl((0,-.565,-.07),.047,.01,'screen',10,direction=(0,-1,0))
    b.ico((.09,-.52,-.02),(.015,.012,.015),'red',1);return b


def wall_clock():
    b=Batch();b.cyl((0,0,0),.30,.045,'dark',20,direction=(0,-1,0));b.cyl((0,-.03,0),.27,.015,'paper',20,direction=(0,-1,0))
    for i in range(12):
        a=i*math.tau/12;b.beam((.22*math.cos(a),-.045,.22*math.sin(a)),(.25*math.cos(a),-.045,.25*math.sin(a)),.008,'dark',4)
    b.beam((0,-.05,0),(-.10,-.05,.09),.012,'dark',5);b.beam((0,-.055,0),(.17,-.055,.10),.008,'coral',5);return b


def make_library():
    palette()
    factories={'Gondola':gondola,'DisplayFridge':fridge,'Checkout':checkout,'ProduceBins':produce,
        'ShoppingBasket':basket,'ShoppingBag':bag,'CardTerminal':terminal,'CashRegister':register,
        'JewelryCase':display_case,'NecklaceBust':necklace_bust,'OfficeDesk':desk,'OfficeChair':chair,
        'ATM':atm,'QueuePost':stanchion,'ClothingRack':clothing_rack,'FoldedClothesTable':folded_table,
        'Mannequin':mannequin,'CoffeeMachine':coffee_machine,'PizzaOven':oven,'PizzaPlate':pizza,
        'DiningTable':dining_table,'ToolCabinet':toolbox,'Compressor':compressor,'EquipmentShelf':equipment_shelf,
        'Locker':locker,'Sofa':sofa,'PlanningBoard':planning_board,'DiningChair':dining_chair,
        'VaultDoor':vault_door,'VehicleLift':vehicle_lift,'SecurityCamera':security_camera,'WallClock':wall_clock}
    for name,factory in factories.items():
        batch=factory();mesh=batch.data('Life5_'+name);mesh.use_fake_user=True;LIB[name]=mesh
        CATALOG.append({'id':name,'mesh':mesh.name,'triangles':sum(len(f.vertices)-2 for f in mesh.polygons),
            'bounds_min':[min(v.co[k] for v in mesh.vertices) for k in range(3)],
            'bounds_max':[max(v.co[k] for v in mesh.vertices) for k in range(3)]})
    return LIB
