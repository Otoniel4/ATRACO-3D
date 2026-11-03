"""Plantas propias de hojas reales y pasto de cintas plegadas; ninguna textura o modelo externo."""
from pathlib import Path
import json, math, random
import bpy
from mathutils import Vector

BASE=Path(__file__).resolve().parent
C=json.loads((BASE/'settings.json').read_text(encoding='utf-8'))
MATERIALS={}


def materials():
    for name,value in C['palette'].items():
        mat=bpy.data.materials.get('WindPlant_'+name)
        if mat is None:
            rgb=[int(value[i:i+2],16)/255 for i in [0,2,4]]
            linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
            mat=bpy.data.materials.new('WindPlant_'+name);mat.use_nodes=True
            mat.diffuse_color=(*linear,1)
            node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            node.inputs['Base Color'].default_value=(*linear,1);node.inputs['Roughness'].default_value=.88
            if any(token in name for token in ['Leaf','Sage','Flower','Grass']):
                node.inputs['Subsurface Weight'].default_value=.05
            mat.use_backface_culling=False
        MATERIALS[name]=mat


class Flora:
    def __init__(self,seed=0):
        self.v=[];self.f=[];self.mat=[];self.mask=[];self.rng=random.Random(seed)
        self.leaves=0;self.blades=0

    def add(self,vertices,faces,color,masks=None):
        start=len(self.v);self.v.extend(tuple(p) for p in vertices)
        self.f.extend(tuple(start+i for i in f) for f in faces)
        self.mat.extend([color]*len(faces));self.mask.extend(masks or [(0,0,0,0)]*len(vertices))

    def flex(self,p,root,height,tip=0,phase=0,grass=False):
        t=min(1,max(0,(p[2]-root[2])/max(height,.01)))
        # Son factores relativos a las amplitudes R3: maceta y raíces permanecen inmóviles.
        return (.19*t*t,.20*t*t,.28*tip*t,phase) if not grass else (.14*t*t,.13*t*t,.24*tip*t,phase)

    def branch(self,points,radii,root,height,sides=5):
        points=[Vector(p) for p in points];vertices=[]
        for i,(p,r) in enumerate(zip(points,radii)):
            u=points[min(i+1,len(points)-1)]-points[max(0,i-1)]
            rotation=u.to_track_quat('Z','Y').to_matrix()
            vertices.extend(p+rotation@Vector((r*math.cos(j*math.tau/sides),r*math.sin(j*math.tau/sides),0)) for j in range(sides))
        faces=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j)
               for i in range(len(points)-1) for j in range(sides)]
        faces.extend([tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))])
        self.add(vertices,faces,'Stem',[self.flex(p,root,height) for p in vertices])

    def leaf(self,p,direction,length,width,color,root,height,lod=0):
        if self.rng.random()>C['lod_leaf_keep'][lod]:return
        length*=C['lod_leaf_scale'][lod];width*=C['lod_leaf_scale'][lod]
        p=Vector(p);u=Vector(direction).normalized()
        n=Vector((self.rng.uniform(-.6,.6),self.rng.uniform(-.6,.6),self.rng.uniform(.4,1)))
        side=u.cross(n).normalized();normal=side.cross(u).normalized()
        vertices=[p,p+u*length*.28-side*width*.37,p+u*length*.63-side*width*.5,
                  p+u*length,p+u*length*.63+side*width*.5,p+u*length*.28+side*width*.37,
                  p+u*length*.48+normal*width*.17]
        phase=self.rng.random()
        self.add(vertices,[(0,1,6),(1,2,6),(2,3,6),(3,4,6),(4,5,6),(5,0,6)],color,
                 [self.flex(v,root,height,t,phase) for v,t in zip(vertices,[0,.2,.6,1,.6,.2,.45])])
        self.leaves+=1

    def shrub(self,center,width,depth,height,lod=0,variant=0):
        root=Vector(center);rng=self.rng
        for i in range(C['shrub_stems']):
            a=i*2.39996+rng.uniform(-.15,.15)
            reach=.24+.18*(i%3);top=height*rng.uniform(.66,1.0)
            end=root+Vector((math.cos(a)*width*reach,math.sin(a)*depth*reach,top))
            mid=root.lerp(end,.48)+Vector((0,0,height*.10))
            points=[root,mid,end];self.branch(points,[.014,.009,.0025],root,height,5 if lod==0 else 3)
            for j in range(C['shrub_leaf_pairs']):
                t=.15+j*.08;p=root.lerp(end,t)+Vector((0,0,height*.10*math.sin(t*math.pi)))
                tangent=(end-root).normalized();side=Vector((-math.sin(a),math.cos(a),0))
                for sign in [-1,1]:
                    d=side*sign*.8+tangent*.5+Vector((0,0,rng.uniform(-.15,.4)))
                    size=min(.19,max(.075,width*.18))*rng.uniform(.78,1.12)
                    palette=['LeafSun','LeafGreen','LeafShade'] if variant%3 else ['SageSun','SageGreen','LeafShade']
                    self.leaf(p,d,size,size*(.49 if variant%3 else .32),palette[(i+j)%3],root,height,lod)
            if variant%2 and i%2==0 and lod<2:
                flower=end+Vector((0,0,.025));petal_color='FlowerPink' if variant%4==1 else 'FlowerCream'
                for k in range(5):
                    b=k*math.tau/5
                    self.leaf(flower,(math.cos(b),math.sin(b),.1),.060,.038,petal_color,root,height,0)
                self.pebble(flower,.019,'FlowerHeart',root,height)

    def blade(self,p,height,width,angle,bend):
        p=Vector(p);u=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-u.y,u.x,0))
        vertices=[];tips=[]
        for t in [0,.36,.72]:
            center=p+u*bend*t*t+Vector((0,0,height*t));w=width*(1-t*.65)
            vertices.extend([center-side*w*.5,center+u*w*.22,center+side*w*.5]);tips.extend([t,t,t])
        vertices.append(p+u*bend+Vector((0,0,height)));tips.append(1)
        faces=[(row*3+k,row*3+k+1,(row+1)*3+k+1,(row+1)*3+k) for row in range(2) for k in range(2)]
        faces.extend([(6,7,9),(7,8,9)])
        phase=self.rng.random();color=self.rng.choices(['GrassSun','GrassGreen','GrassShade','GrassDry'],[24,45,25,6])[0]
        self.add(vertices,faces,color,[self.flex(v,p,height,t,phase,True) for v,t in zip(vertices,tips)])
        self.blades+=1

    def grass(self,center=(0,0,0),lod=0,extent=None):
        center=Vector(center);extent=extent or C['grass_tile_m'];rng=self.rng
        # Los centros de grupos permanecen entre LOD; se reduce el número de grupos.
        count=C['grass_tufts'][lod]
        for i in range(count):
            a=rng.random()*math.tau;r=math.sqrt(rng.random())*extent*.46
            base=center+Vector((r*math.cos(a),r*math.sin(a),0))
            for j in range(C['grass_blades_per_tuft'][lod]):
                a=rng.random()*math.tau;spread=rng.random()*.055
                p=base+Vector((math.cos(a)*spread,math.sin(a)*spread,0))
                h=rng.uniform(*C['grass_height_m'])*(1 if lod==0 else 1.12)
                self.blade(p,h,rng.uniform(.012,.027)*(1 if lod==0 else 1.4),a,h*rng.uniform(.22,.6))

    def box(self,p,size,color):
        p=Vector(p);x,y,z=[v*.5 for v in size]
        self.add([p+Vector(v) for v in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]],
                 [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],color)

    def pebble(self,p,r,color='Pebble',root=None,height=1):
        p=Vector(p);vertices=[p+Vector(v)*r for v in [(0,0,.6),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,-.4)]]
        self.add(vertices,[(0,1,2),(0,2,3),(0,3,4),(0,4,1),(5,2,1),(5,3,2),(5,4,3),(5,1,4)],color,
                 [self.flex(v,root,height) for v in vertices] if root else None)

    def rim(self,polygon,z):
        # Borde sobre el sustrato existente; mantiene intacta la maceta original.
        points=[Vector((p[0],p[1],z)) for p in polygon];center=sum(points,Vector())/len(points)
        inner=[center+(p-center)*.96 for p in points];outer=[center+(p-center)*1.045 for p in points]
        n=len(points);vertices=outer+inner+[p+Vector((0,0,.045)) for p in outer+inner]
        faces=[]
        for i in range(n):
            j=(i+1)%n;faces.extend([(i,j,j+2*n,i+2*n),(i+n,i+3*n,j+3*n,j+n),(i+2*n,j+2*n,j+3*n,i+3*n)])
        self.add(vertices,faces,'StoneRim')

    def rectangular_pot(self,width=2.7,depth=.9,height=.5):
        self.box((0,0,height/2),(width,depth,height),'Stone')
        self.box((0,0,height+.005),(width-.10,depth-.10,.025),'Soil')
        self.rim([(-width/2+.04,-depth/2+.04),(width/2-.04,-depth/2+.04),
                  (width/2-.04,depth/2-.04),(-width/2+.04,depth/2-.04)],height+.015)
        for x in [-width*.3,0,width*.3]:
            for y in [-depth*.3,depth*.3]:self.pebble((x,y,height+.03),.045)

    def round_pot(self,r=.46,h=.62):
        sides=12;vertices=[]
        for radius,z in [(r*.76,0),(r,h*.94),(r*1.04,h),(r*.86,h),(r*.80,h-.09)]:
            vertices.extend((radius*math.cos(j*math.tau/sides),radius*math.sin(j*math.tau/sides),z) for j in range(sides))
        faces=[(level*sides+j,level*sides+(j+1)%sides,(level+1)*sides+(j+1)%sides,(level+1)*sides+j)
               for level in range(4) for j in range(sides)]
        faces.append(tuple(reversed(range(sides))));self.add(vertices,faces,'Terracotta')
        self.add([(r*.79*math.cos(j*math.tau/sides),r*.79*math.sin(j*math.tau/sides),h-.075) for j in range(sides)],
                 [tuple(range(sides))],'Soil')

    def data(self,name):
        data=bpy.data.meshes.new(name);data.from_pydata(self.v,[],self.f);data.update()
        names=list(dict.fromkeys(self.mat));mapping={n:i for i,n in enumerate(names)}
        for n in names:data.materials.append(MATERIALS[n])
        for poly,color in zip(data.polygons,self.mat):poly.material_index=mapping[color]
        attr=data.color_attributes.new(name='WindMask',type='FLOAT_COLOR',domain='POINT')
        attr.data.foreach_set('color',[x for value in self.mask for x in value]);data.color_attributes.active_color=attr
        data['Leaves']=self.leaves;data['GrassBlades']=self.blades;data.use_fake_user=True
        return data
