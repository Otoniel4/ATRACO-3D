"""Árboles propios: ramas curvas, hojas plegadas individuales y máscaras de viento por vértice."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
C=json.loads((BASE/'settings.json').read_text(encoding='utf-8'))
SPECIES=[('Fresno',8.5,3.2),('Olivo',6.4,2.8),('Jacaranda',8.0,3.3),('Citrico',6.0,2.6),('Pino',9.6,3.1),('Palmera',8.2,4.1)]
MATERIALS=[];INDEX={}

def create_materials():
    for name,hexcolor in C['palette'].items():
        rgb=[int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
        linear=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]
        mat=bpy.data.materials.new('WindTree_'+name);mat.use_nodes=True;mat.diffuse_color=(*linear,1)
        shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value=(*linear,1);shader.inputs['Roughness'].default_value=.82
        if name.startswith(('Leaf','Olive','Citrus','Pine','Palm','Flower')):
            shader.inputs['Subsurface Weight'].default_value=.055;mat.use_backface_culling=False
        INDEX[name]=len(MATERIALS);MATERIALS.append(mat)

class TreeMesh:
    def __init__(self,height,radius,lod,seed):
        self.height=height;self.radius=radius;self.lod=lod;self.rng=random.Random(seed)
        self.vertices=[];self.faces=[];self.colors=[];self.materials=[];self.leaves=0
    def masks(self,p,tip=0,phase=0):
        z=max(0,p[2]);r=0 if z<=.05 else min(1,z/self.height)**1.8
        branch=min(1,max(0,(z-1.5)/(self.height-1.5)))**1.1*min(1,math.hypot(p[0],p[1])/(self.radius*.9))
        return (r,branch,tip,phase)
    def add(self,vs,fs,color,tips=None,phase=0):
        offset=len(self.vertices);self.vertices.extend(tuple(p) for p in vs)
        self.colors.extend(self.masks(p,tips[i] if tips else 0,phase) for i,p in enumerate(vs))
        self.faces.extend(tuple(offset+j for j in f) for f in fs);self.materials.extend([INDEX[color]]*len(fs))
    def branch(self,points,radii,color='Bark',sides=None):
        points=[Vector(p) for p in points];sides=sides or [8,6,5][self.lod];vs=[]
        for i,(p,r) in enumerate(zip(points,radii)):
            tangent=points[min(i+1,len(points)-1)]-points[max(0,i-1)]
            frame=tangent.to_track_quat('Z','Y').to_matrix()
            for j in range(sides):
                a=j*math.tau/sides;vs.append(p+frame@Vector((r*math.cos(a),r*math.sin(a),0)))
        faces=[]
        for i in range(len(points)-1):
            for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
        faces += [tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))]
        self.add(vs,faces,color)
    def leaf(self,base,direction,length,width,color,phase=None):
        # La selección por hoja conserva el mismo árbol entre niveles de detalle.
        if self.rng.random()>C['lod_leaf_keep'][self.lod]:return
        scale=C['lod_leaf_scale'][self.lod];length*=scale;width*=scale
        base=Vector(base);u=Vector(direction).normalized()
        normal=Vector((self.rng.uniform(-1,1),self.rng.uniform(-1,1),self.rng.uniform(.15,1))).normalized()
        side=u.cross(normal).normalized();normal=side.cross(u).normalized()
        vs=[base,base+u*length*.27-side*width*.34,base+u*length*.55-side*width*.52,
            base+u*length,base+u*length*.55+side*width*.52,base+u*length*.27+side*width*.34,
            base+u*length*.48+normal*width*.16]
        tips=[0,.24,.62,1,.62,.24,.45];flex=min(1,max(.24,length/(scale*.28)))
        self.add(vs,[(0,1,6),(1,2,6),(2,3,6),(3,4,6),(4,5,6),(5,0,6)],color,[x*flex for x in tips],self.rng.random() if phase is None else phase)
        self.leaves+=1
    def fruit(self,p,r,color):
        p=Vector(p);vs=[p+Vector(v)*r for v in [(0,0,1),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,-1)]]
        self.add(vs,[(0,1,2),(0,2,3),(0,3,4),(0,4,1),(5,2,1),(5,3,2),(5,4,3),(5,1,4)],color)
    def data(self,name):
        data=bpy.data.meshes.new(name);data.from_pydata(self.vertices,[],self.faces);data.update()
        used=sorted(set(self.materials));mapping={old:new for new,old in enumerate(used)}
        for i in used:data.materials.append(MATERIALS[i])
        for p,index in zip(data.polygons,self.materials):p.material_index=mapping[index]
        colors=data.color_attributes.new(name='WindMask',type='FLOAT_COLOR',domain='POINT')
        colors.data.foreach_set('color',[c for value in self.colors for c in value]);data.color_attributes.active_color=colors
        data['Species']=name.split('_')[1];data['LeafCount']=self.leaves;data['WindChannels']='R trunk; G branches; B leaf tip; A leaf phase'
        data.use_fake_user=True
        return data

def trunk(tree,height,lean=.25):
    points=[(lean*math.sin(t*1.7),lean*.6*math.sin(t*2.5),height*t) for t in [0,.08,.22,.40,.58,.76,.9,1]]
    radii=[.38,.29,.24,.20,.155,.115,.065,.015]
    tree.branch(points,radii)
    for i in range(6):
        a=i*math.tau/6;p=(.85*math.cos(a),.85*math.sin(a),.015)
        tree.branch([p,(p[0]*.35,p[1]*.35,.26),(0,0,.7)],[.07,.15,.18],sides=5)

def broadleaf(species,lod):
    name,height,radius=SPECIES[species];tree=TreeMesh(height,radius,lod,C['seed']+species*100)
    rng=random.Random(C['seed']+species*513);trunk(tree,height*.90,.25 if species!=1 else .45)
    colors= ['OliveSun','OliveGreen','OliveShade'] if species==1 else (['CitrusSun','CitrusGreen','CitrusShade'] if species==3 else ['LeafSun','LeafGreen','LeafShade'])
    branches=12 if species!=1 else 15
    for i in range(branches):
        a=i*2.39996+rng.uniform(-.2,.2);z0=height*(.33+.025*(i%4));z1=height*(.58+.35*(i/(branches-1)))
        reach=radius*math.sqrt(max(.25,1-((z1-height*.76)/(height*.34))**2))*rng.uniform(.87,1.05)
        start=Vector((.1*math.sin(a),.1*math.cos(a),z0));end=Vector((reach*math.cos(a),reach*math.sin(a),z1))
        mid=start.lerp(end,.48)+Vector((0,0,.35));tip=end+Vector((.25*math.cos(a),.25*math.sin(a),.12))
        tree.branch([start,mid,end,tip],[.095,.052,.022,.005],sides=7 if lod==0 else 5)
        for shoot in range(14 if species!=1 else 16):
            if lod==2 and shoot%2:continue
            t=.30+shoot*.048;origin=start.lerp(end,min(.99,t))+Vector((0,0,.25*math.sin(t*math.pi)))
            aa=a+(1 if shoot%2 else -1)*rng.uniform(.5,1.5)
            length=rng.uniform(.8,1.35);delta=Vector((math.cos(aa),math.sin(aa),rng.uniform(-.45,.85)))*length
            target=origin+delta
            tree.branch([origin,origin.lerp(target,.55)+Vector((0,0,.06)),target],[.025,.014,.004],sides=5 if lod==0 else 4)
            pairs=11 if species not in [1,2] else (13 if species==1 else 18)
            for j in range(pairs):
                p=origin.lerp(target,(j+.65)/(pairs+.3));axis=delta.normalized();side=Vector((-axis.y,axis.x,0))
                for sign in [-1,1]:
                    direction=(side*sign+axis*.28+Vector((0,0,rng.uniform(-.25,.45)))).normalized()
                    size=(.26 if species==2 else (.29 if species==1 else .43))*rng.uniform(.78,1.20)
                    width=size*(.30 if species in [1,2] else .50)
                    tree.leaf(p,direction,size,width,colors[(i+j+(sign>0))%3])
                if species==2 and (i+j+shoot)%17==0 and lod<2:
                    for k in range(3):tree.fruit(p+Vector((.06*k,0,-.05*k)),.045,'Flower' if k%2 else 'FlowerLight')
            if species==3 and shoot%3==0:tree.fruit(origin.lerp(target,.72)+Vector((0,0,-.16)),.095,'Fruit')
    return tree.data(f'TreeR3_{name}_LOD{lod}')

def pine(lod):
    name,height,r=SPECIES[4];tree=TreeMesh(height,r,lod,C['seed']+400);rng=random.Random(411)
    trunk(tree,height,.12)
    for level in range(6):
        z=height*(.23+level*.12);reach=r*(1-level*.125)
        for i in range(7):
            a=i*math.tau/7+level*.55;u=Vector((math.cos(a),math.sin(a),0));origin=Vector((0,0,z));tip=origin+u*reach+Vector((0,0,.20))
            mid=origin.lerp(tip,.55)+Vector((0,0,-.25))
            tree.branch([origin,mid,tip],[.075,.045,.006],sides=6 if lod==0 else 4)
            for j in range(7):
                if lod==2 and j%2:continue
                p=origin.lerp(tip,.25+j*.105);v=Vector((-u.y,u.x,.3))
                for sign in [-1,1]:
                    end=p+v*sign*(.6-j*.04)+u*.2
                    tree.branch([p,end],[.014,.003],sides=4)
                    for k in range(10):
                        q=p.lerp(end,(k+.3)/10)
                        direction=(Vector((math.cos(a+k*.9),math.sin(a+k*.9),.6))).normalized()
                        tree.leaf(q,direction,.36+rng.random()*.15,.065,['PineSun','PineGreen','PineShade'][(i+k)%3])
    return tree.data(f'TreeR3_{name}_LOD{lod}')

def palm(lod):
    name,h,r=SPECIES[5];tree=TreeMesh(h,r,lod,C['seed']+500);rng=random.Random(511)
    points=[(.35*math.sin(t*1.6),.18*t*t,h*t) for t in [0,.13,.28,.44,.60,.76,.88,1]]
    tree.branch(points,[.34,.28,.25,.23,.21,.19,.16,.14],sides=10 if lod==0 else 6)
    if lod<2:
        for i in range(32):
            t=(i+.5)/33;p=Vector((.35*math.sin(t*1.6),.18*t*t,h*t));tree.branch([p-Vector((0,0,.014)),p+Vector((0,0,.014))],[.245-.09*t,.245-.09*t],'BarkLight',sides=8)
    crown=Vector(points[-1])
    for i in range(15):
        a=i*2.39996;u=Vector((math.cos(a),math.sin(a),0));side=Vector((-u.y,u.x,0));length=rng.uniform(2.7,4.2)
        curve=[]
        for j in range(9):
            t=j/8;curve.append(crown+u*length*t+Vector((0,0,1.4*math.sin(math.pi*t)-1.4*t*t)))
        tree.branch(curve,[.048*(1-j/9)+.005 for j in range(9)],'PalmShade',sides=5)
        for j in range(19):
            t=(j+1)/21;k=min(7,int(t*8));p=curve[k].lerp(curve[k+1],t*8-k)
            for sign in [-1,1]:
                direction=(side*sign+u*.38+Vector((0,0,-.40))).normalized();size=(.95*(1-t)+.12)*rng.uniform(.9,1.1)
                tree.leaf(p,direction,size,.12,['PalmSun','PalmGreen','PalmShade'][(i+j)%3])
    return tree.data(f'TreeR3_{name}_LOD{lod}')

def build_library():
    create_materials();result={}
    for species in range(6):
        result[species]=[]
        for lod in range(3):result[species].append(pine(lod) if species==4 else (palm(lod) if species==5 else broadleaf(species,lod)))
    return result
