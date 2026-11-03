"""Primitivas propias, colores planos y geometría compartida. Unidades: metros."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
MATERIALS=[];INDEX={}

def palette(colors):
    for name,value in colors.items():
        rgb=[int(value[i:i+2],16)/255 for i in (0,2,4)]
        rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
        m=bpy.data.materials.new('City4_'+name);m.use_nodes=True;m.diffuse_color=rgba
        shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value=rgba;shader.inputs['Roughness'].default_value=.85
        INDEX[name]=len(MATERIALS);MATERIALS.append(m)

class Batch:
    def __init__(self):self.vertices=[];self.faces=[];self.materials=[]
    def add(self,vertices,faces,color,matrix=None):
        offset=len(self.vertices)
        self.vertices.extend(tuple(matrix@Vector(p)) if matrix else tuple(p) for p in vertices)
        self.faces.extend(tuple(offset+i for i in f) for f in faces)
        self.materials.extend([INDEX[color] if isinstance(color,str) else color]*len(faces))
    def box(self,p,size,color,rotation=0):
        x,y,z=(v/2 for v in size)
        vertices=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
        matrix=Matrix.Translation(Vector(p))@Matrix.Rotation(rotation,4,'Z')
        self.add(vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],color,matrix)
    def quad(self,rect,z,color):
        x0,y0,x1,y1=rect;self.add([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[(0,1,2,3)],color)
    def cyl(self,p,r,depth,color,n=8,top=None,direction=None):
        top=r if top is None else top
        vertices=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),-depth/2) for i in range(n)]
        vertices += [(top*math.cos(i*math.tau/n),top*math.sin(i*math.tau/n),depth/2) for i in range(n)]
        faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(reversed(range(n))),tuple(range(n,2*n))]
        matrix=Matrix.Translation(Vector(p))
        if direction:matrix=matrix@Vector(direction).to_track_quat('Z','Y').to_matrix().to_4x4()
        self.add(vertices,faces,color,matrix)
    def beam(self,a,b,r,color,n=6):
        a,b=Vector(a),Vector(b);self.cyl((a+b)/2,r,(b-a).length,color,n,direction=b-a)
    def ico(self,p,size,color,level=1):
        bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=level,radius=1)
        bm.verts.ensure_lookup_table();vs=[(v.co.x*size[0]+p[0],v.co.y*size[1]+p[1],v.co.z*size[2]+p[2]) for v in bm.verts]
        self.add(vs,[tuple(v.index for v in f.verts) for f in bm.faces],color);bm.free()
    def text(self,label,p,size,color):
        data=bpy.data.curves.new('SignFont','FONT');data.body=label;data.size=size;data.align_x='CENTER';data.align_y='CENTER';data.resolution_u=1
        obj=bpy.data.objects.new('SignTemp',data);bpy.context.scene.collection.objects.link(obj)
        obj.location=p;obj.rotation_euler=(math.pi/2,0,0)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        allowed={i.identifier for i in bpy.ops.object.convert.get_rna_type().properties['target'].enum_items}
        if 'MESH' not in allowed:raise RuntimeError('No se puede convertir texto')
        bpy.ops.object.convert(target='MESH')
        self.add([obj.matrix_world@v.co for v in obj.data.vertices],[tuple(f.vertices) for f in obj.data.polygons],color)
        bpy.data.objects.remove(obj,do_unlink=True)
    def imported(self,obj,transform):
        slot_colors=[]
        for slot in obj.material_slots:
            material=slot.material
            rgba=material.diffuse_color
            if material.use_nodes:
                shader=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                if shader:rgba=shader.inputs['Base Color'].default_value
            index=min(range(len(MATERIALS)),key=lambda i:sum((MATERIALS[i].diffuse_color[k]-rgba[k])**2 for k in range(3)))
            slot_colors.append(index)
        offset=len(self.vertices);self.vertices.extend(tuple(transform@v.co) for v in obj.data.vertices)
        for face in obj.data.polygons:
            self.faces.append(tuple(offset+i for i in face.vertices));self.materials.append(slot_colors[face.material_index])
    def data(self,name):
        data=bpy.data.meshes.new(name);data.from_pydata(self.vertices,[],self.faces);data.update()
        for m in MATERIALS:data.materials.append(m)
        for face,index in zip(data.polygons,self.materials):face.material_index=index
        return data

def world_matrix(obj):
    return world_matrix(obj.parent)@obj.matrix_parent_inverse@obj.matrix_basis if obj.parent else obj.matrix_basis.copy()

def subtract_rect(rect,hole):
    x0,y0,x1,y1=rect;a,b,c,d=hole
    l,r=max(x0,a),min(x1,c);s,t=max(y0,b),min(y1,d)
    if l>=r or s>=t:return [rect]
    return [q for q in [(x0,y0,l,y1),(r,y0,x1,y1),(l,y0,r,s),(l,t,r,y1)] if q[2]>q[0] and q[3]>q[1]]
