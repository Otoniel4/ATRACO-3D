"""Elenco propio low poly de Alarma. Blender 4.5/5.x; sin recursos descargados.
blender -b --python-exit-code 1 -P build_cast.py
Opcional: -- --only NPC01_Bomber,NPC04_Lavender,Player04_Muscle
"""
import bpy,bmesh,math,json,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import character_primitives as P

# Medidas base en metros. El elenco conserva las proporciones de la cabeza aprobada.
SHIRT_HEM=.990;WAIST=1.008;CROTCH=.785;SHORT_HEM=.525
SLEEVE_RADIUS=.060;HAND_SIZE=(.054,.040,.074)
GALLERY_SPACING=2.20;GALLERY_ROW_HEIGHT=2.28
MATS={};TEMPLATE=None;SOURCE={};TREE=None;WEIGHTS=[]

def mat(color):
    if color not in MATS:MATS[color]=P.material('Cast_'+color,color)
    return MATS[color]

def new_scene(name):
    if bpy.data.scenes.get(name):raise RuntimeError('Ya existe la escena '+name)
    scene=bpy.data.scenes.new(name);bpy.context.window.scene=scene
    scene.world=TEMPLATE.world.copy();scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    try:scene.render.engine='BLENDER_EEVEE_NEXT'
    except TypeError:scene.render.engine='BLENDER_EEVEE'
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    scene.render.resolution_percentage=100;scene.render.film_transparent=False
    for original in TEMPLATE.objects:
        if original.type in {'CAMERA','LIGHT'}:
            obj=original.copy();obj.data=original.data.copy();scene.collection.objects.link(obj)
            obj.hide_set(False)
            if obj.type=='CAMERA':scene.camera=obj
    return scene

def source_setup():
    global TEMPLATE,SOURCE,TREE,WEIGHTS
    with bpy.data.libraries.load(str(BASE/'baseline'/'approved_female.blend'),link=False) as (src,dst):dst.scenes=['Female_LowPoly']
    TEMPLATE=dst.scenes[0];TEMPLATE.name='Cast_Source_Approved'
    SOURCE={o.name.split('.')[0]:o for o in TEMPLATE.objects}
    body=SOURCE['LP_Body'];TREE=KDTree(len(body.data.vertices))
    WEIGHTS=[]
    for v in body.data.vertices:
        TREE.insert(v.co,v.index)
        WEIGHTS.append({body.vertex_groups[g.group].name:g.weight for g in v.groups})
    TREE.balance()

def mesh(name,verts,faces,color):return P.mesh(name,verts,faces,mat(color))
def box(name,center,size,color,bevel=.006):return P.bevel_box(name,center,size,bevel,mat(color))
def ico(name,center,size,color,level=1):return P.ico(name,center,size,mat(color),level)
def combine(name,items):return P.join(name,items)
def apply(obj,mod):P.activate(obj);bpy.ops.object.modifier_apply(modifier=mod.name)

def bind(obj,rig,bone=None,dress=False):
    for g in list(obj.vertex_groups):obj.vertex_groups.remove(g)
    if bone:
        obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))),1,'REPLACE')
    else:
        groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones}
        for v in obj.data.vertices:
            if dress and v.co.z<.99:
                groups['Hips'].add([v.index],1,'REPLACE');continue
            neighbors=TREE.find_n(v.co,3);scores=[1/max(d,.0001)**2 for _,_,d in neighbors];total=sum(scores);weights={}
            for (_,index,_),score in zip(neighbors,scores):
                for name,w in WEIGHTS[index].items():weights[name]=weights.get(name,0)+w*score/total
            length=sum(weights.values())
            for name,w in weights.items():
                if w>1e-6:groups[name].add([v.index],w/length,'REPLACE')
    obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted()
    for m in list(obj.modifiers):obj.modifiers.remove(m)
    mod=obj.modifiers.new('Humanoid','ARMATURE');mod.object=rig
    return obj

def loft(name,rings,color,n=12,caps=True,open_front=False):
    verts=[(x+rx*math.cos(-math.pi/2+2*math.pi*i/n),y+ry*math.sin(-math.pi/2+2*math.pi*i/n),z)
           for x,y,z,rx,ry in rings for i in range(n)]
    faces=[]
    for j in range(len(rings)-1):
        for i in range(n):
            if open_front and i in [0,n-1]:continue
            faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    if caps and not open_front:faces += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
    return mesh(name,verts,faces,color)

def tube(name,points,radii,color,n=8):
    points=[Vector(p) for p in points];verts=[]
    for j,p in enumerate(points):
        d=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
        axis=Vector((0,1,0))
        if abs(d.dot(axis))>.95:axis=Vector((1,0,0))
        u=d.cross(axis).normalized();v=d.cross(u).normalized()
        verts += [p+(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n))*radii[j] for i in range(n)]
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(points)-1) for i in range(n)]
    faces += [tuple(reversed(range(n))),tuple((len(points)-1)*n+i for i in range(n))]
    return mesh(name,verts,faces,color)

def surface(obj):return BVHTree.FromPolygons([v.co.copy() for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])
def panel(name,verts,color,surf=None,back=False):
    verts=[Vector(v) for v in verts]
    if surf:
        for v in verts:
            hit,_,_,_=surf.ray_cast(Vector((v.x,1 if back else -1,v.z)),Vector((0,-1 if back else 1,0)))
            if hit:v.y=hit.y+(.0035 if back else -.0035)
    faces=[tuple(range(len(verts)))]
    if back:faces=[tuple(reversed(faces[0]))]
    obj=mesh(name,verts,faces,color)
    if surf and len(verts)==4 and (max(v.x for v in verts)-min(v.x for v in verts)>.095 or max(v.z for v in verts)-min(v.z for v in verts)>.10):
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=6,use_grid_fill=True)
        for v in bm.verts:
            hit,_,_,_=surf.ray_cast(Vector((v.co.x,1 if back else -1,v.co.z)),Vector((0,-1 if back else 1,0)))
            if hit:v.co.y=hit.y+(.0035 if back else -.0035)
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    if obj.data.polygons and ((obj.data.polygons[0].normal.y<0) if back else (obj.data.polygons[0].normal.y>0)):
        bm=bmesh.new();bm.from_mesh(obj.data)
        for f in bm.faces:f.normal_flip()
        bm.to_mesh(obj.data);bm.free()
    return obj

def text_mesh(text,position,size,color,back=False):
    data=bpy.data.curves.new('Label','FONT');data.body=text;data.size=size;data.align_x='CENTER';data.resolution_u=1
    obj=bpy.data.objects.new('Label',data);bpy.context.scene.collection.objects.link(obj)
    obj.location=position;obj.rotation_euler=(math.pi/2,0,math.pi if back else 0);data.materials.append(mat(color))
    P.activate(obj)
    allowed={x.identifier for x in bpy.ops.object.convert.get_rna_type().properties['target'].enum_items}
    if 'MESH' not in allowed:raise RuntimeError('Conversión a malla no disponible')
    bpy.ops.object.convert(target='MESH');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return obj

def bone_points(side):
    prefix='Left' if side==1 else 'Right';rig=next(o for o in TEMPLATE.objects if o.type=='ARMATURE')
    return rig.data.bones[prefix+'UpperArm'].head_local.copy(),rig.data.bones[prefix+'LowerArm'].tail_local.copy()

def visible_skin(spec,rig):
    body=SOURCE['LP_Body'].copy();body.data=body.data.copy();bpy.context.scene.collection.objects.link(body)
    for m in list(body.modifiers):body.modifiers.remove(m)
    bm=bmesh.new();bm.from_mesh(body.data)
    def keep(p):
        if p.z>1.235 and abs(p.x)<.10:return False
        if (spec.get('shorts') or spec['style']=='dress') and .10<p.z<SHORT_HEM+.045 and abs(p.x)<.235:return True
        if spec.get('girth',1)>1.1:return False
        side=1 if p.x>=0 else -1;sh,wr=bone_points(side);axis=wr-sh
        t=(p-sh).dot(axis)/axis.length_squared;nearest=sh+axis*t
        return abs(p.x)>.12 and (p-nearest).length<.09 and max(-.15,spec['sleeve']-.05)<t<1.025
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f.calc_center_median())],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free()
    body.data.materials.clear();body.data.materials.append(mat(spec['skin']))
    if len(body.data.polygons)>250:
        dec=body.modifiers.new('Visible skin low poly','DECIMATE');dec.ratio=.42;apply(body,dec)
    if spec.get('girth',1)!=1:
        for v in body.data.vertices:
            if abs(v.co.x)>.12 and v.co.z>.72:
                sh,wr=bone_points(1 if v.co.x>0 else -1);axis=wr-sh;t=max(0,min(1,(v.co-sh).dot(axis)/axis.length_squared))
                center=sh+axis*t;v.co=center+(v.co-center)*spec['girth']
    bind(body,rig)
    neck=loft('Neck',[(0,0,1.24,.033,.035),(0,0,1.29,.033,.035),(0,0,1.35,.033,.035)],spec['skin'],10)
    bind(neck,rig)
    hands=[neck]
    for side in [-1,1]:
        sh,wr=bone_points(side);direction=(wr-sh).normalized();girth=spec.get('girth',1)
        if girth>1.1:
            prefix='Left' if side==1 else 'Right';source_rig=next(o for o in TEMPLATE.objects if o.type=='ARMATURE')
            elbow=source_rig.data.bones[prefix+'UpperArm'].tail_local.copy()
            arm=tube('MuscleArm',[sh-direction*.012,sh.lerp(elbow,.25),sh.lerp(elbow,.80),elbow,elbow.lerp(wr,.3),elbow.lerp(wr,.8),wr],
                [r*girth for r in [.060,.067,.060,.047,.053,.039,.031]],spec['skin'],8)
            bind(arm,rig);hands.append(arm)
        palm=box('Palm',wr+direction*.033,tuple(x*(girth**.4) for x in HAND_SIZE),'252A34' if spec.get('gloves') else spec['skin'],.012)
        palm.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        thumb=box('Thumb',wr+direction*.018+Vector((-side*.023,-.009,0)),(.024,.034,.039),'252A34' if spec.get('gloves') else spec['skin'],.007)
        hand=combine('Hand',[palm,thumb]);bind(hand,rig,('Left' if side==1 else 'Right')+'Hand');hands.append(hand)
    result=combine('Body',[body]+hands)
    return result

def pants_mesh(spec):
    """Dos piernas soldadas a una pelvis de quads, sin bloques superpuestos."""
    verts=[];faces=[];tops={};hem=SHORT_HEM if spec.get('shorts') else .095
    def ring(x,z,rx,ry):
        ids=list(range(len(verts),len(verts)+8))
        verts.extend((x+rx*math.cos(2*math.pi*i/8),ry*math.sin(2*math.pi*i/8),z) for i in range(8));return ids
    def bridge(a,b):faces.extend((a[i],a[(i+1)%len(a)],b[(i+1)%len(b)],b[i]) for i in range(len(a)))
    for side in [-1,1]:
        width=.107 if spec.get('culottes') else .071
        levels=[(hem,.146 if spec.get('shorts') else .151,width,.090),
                (hem+.018,.143 if spec.get('shorts') else .149,width,.091),
                (.665,.106,.082,.100)]
        if not spec.get('shorts'):levels.insert(2,(.414,.126,.074,.097))
        rings=[ring(side*x,z,rx,ry) for z,x,rx,ry in levels]
        for a,b in zip(rings,rings[1:]):bridge(a,b)
        top=ring(side*.097,.876,.097,.117)
        inner=[3,4,5] if side==1 else [1,0,7]
        for j,i in enumerate(inner):verts[top[i]]=(0,(1-j)*.119,.822 if j!=1 else .777)
        bridge(rings[-1],top);tops[side]=top
    remap={tops[-1][l]:tops[1][r] for l,r in [(1,3),(0,4),(7,5)]}
    faces=[tuple(remap.get(i,i) for i in f) for f in faces]
    lower=[tops[1][i] for i in [5,6,7,0,1,2,3]]+[tops[-1][i] for i in [2,3,4,5,6]]
    for z,rx,ry in [(.911,.167,.117),(.990,.137,.099),(WAIST,.134,.097)]:
        upper=list(range(len(verts),len(verts)+12))
        verts.extend((rx*math.cos(-math.pi/2+2*math.pi*i/12),ry*math.sin(-math.pi/2+2*math.pi*i/12),z) for i in range(12))
        bridge(lower,upper);lower=upper
    obj=mesh('Trousers',verts,faces,spec['pants'])
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    sub=obj.modifiers.new('Rounded low-poly cage','SUBSURF');sub.levels=1;apply(obj,sub)
    return obj

def outfit(spec,rig):
    style=spec['style'];girth=spec.get('girth',1);parts=[]
    opening=style in ['jacket','cardigan','vest','security_vest']
    def torso(color,offset=0,opened=False):
        zs=[SHIRT_HEM,1.075,1.165,1.225,1.278]
        if style=='stripes':zs=[SHIRT_HEM+i*.020 for i in range(13)]+[1.255,1.278]
        if style=='plaid':zs=[SHIRT_HEM+i*.035 for i in range(8)]+[1.255,1.278]
        rings=[]
        for z in zs:
            t=max(0,min(1,(z-SHIRT_HEM)/.235));rx=.112+(.068 if spec['sex']=='male' else .051)*t;ry=.076+.031*t
            if z>1.225:rx=.043;ry=.043
            rings.append((0,0,z,rx+offset,ry+offset))
        return loft('Torso',rings,color,n=24 if style=='plaid' else 12,open_front=opened)
    if opening:parts.append(torso(spec['inner']))
    outer=torso(spec['top'],.010 if opening else .004,opening)
    parts.append(outer);surf=surface(outer)
    if style=='stripes':
        outer.data.materials.append(mat('282B33'))
        for p in outer.data.polygons:
            z=sum(outer.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)
            p.material_index=int((z-SHIRT_HEM)/.033)%2
    for side in [-1,1]:
        sh,wr=bone_points(side);d=wr-sh;fraction=spec['sleeve'];color=spec['inner'] if style in ['vest','security_vest'] else spec['top']
        if fraction>.01:
            points=[sh+d*fraction*i/5 for i in range(6)]
            sleeve=tube('Sleeve',points,[(SLEEVE_RADIUS-.014*i/5)*girth for i in range(6)],color)
            if style=='stripes':
                sleeve.data.materials.append(mat('282B33'))
                for p in sleeve.data.polygons:p.material_index=(p.index//8)%2
            parts.append(sleeve)
            end=sh+d*fraction
            parts.append(tube('Cuff',[end-d.normalized()*.020,end+d.normalized()*.010],[.049*girth,.049*girth],color))
        if style in ['jacket','plaid','cardigan','security_vest','security_jacket','police_shirt','police_jacket']:
            verts=[(side*.038,-.045,1.279),(side*.090,-.083,1.224),(side*.060,-.112,1.208)]
            parts.append(panel('Collar',verts,spec['top'],surf))
        if style in ['jacket','plaid','security_vest','police_shirt','police_jacket']:
            x=side*.088;z=1.158
            parts.append(panel('ChestPocket',[(x-.027,-.1,z+.026),(x+.027,-.1,z+.026),(x+.025,-.1,z-.029),(x,-.1,z-.036),(x-.025,-.1,z-.029)],spec['top'],surf))
    if style=='vest':
        for z in [1.015,1.070,1.125,1.180]:
            for side in [-1,1]:parts.append(panel('Padding',[(side*.07-.030,-.1,z),(side*.07+.03,-.1,z),(side*.07+.03,-.1,z+.007),(side*.07-.03,-.1,z+.007)],'263A58',surf))
    if style=='security_vest':
        for side in [-1,1]:parts.append(panel('SecurityYellow',[(side*.10-.034,-.1,1.203),(side*.10+.034,-.1,1.203),(side*.10+.034,-.1,1.228),(side*.10-.034,-.1,1.228)],'E6BF39',surf))
    if style=='hoodie':
        parts.append(ico('Hood',(0,.093,1.255),(.105,.067,.083),spec['top'],2))
        parts.append(panel('KangarooPocket',[(-.08,-.1,1.045),(.08,-.1,1.045),(.059,-.1,1.105),(-.059,-.1,1.105)],spec['top'],surf))
        for side in [-1,1]:parts.append(tube('Cord',[(side*.025,-.101,1.26),(side*.025,-.112,1.17)],[.002,.002],'EDE7D9',4))
    if style=='muscle':
        for side in [-1,1]:parts.append(box('TankStrap',(side*.113,0,1.235),(.053,.112,.033),spec['top'],.005))
    if style in ['sport','security_jacket','police_jacket']:
        trim='E7942A' if spec['group']=='security' else ('3A83C7' if spec['group']=='police' else '60876C')
        parts.append(panel('ChestTrim',[(-.14,-.1,1.19),(.14,-.1,1.19),(.14,-.1,1.207),(-.14,-.1,1.207)],trim,surf))
        parts.append(panel('Zipper',[(-.004,-.1,1.005),(.004,-.1,1.005),(.004,-.1,1.255),(-.004,-.1,1.255)],trim,surf))
    if style=='plaid':
        outer.data.materials.append(mat('E8D4B2'))
        for p in outer.data.polygons:
            if len(p.vertices)==4:p.material_index=(p.index//24+p.index%24)%2
        for z in [1.025,1.070,1.115,1.160,1.205]:
            parts.append(panel('Button',[(.004*math.cos(2*math.pi*i/6),0,z+.004*math.sin(2*math.pi*i/6)) for i in range(6)],'34323A',surf))
    if style=='overalls':
        parts.append(panel('Bib',[(-.096,-.1,1.00),(.096,-.1,1.00),(.080,-.1,1.180),(-.080,-.1,1.180)],spec['pants'],surf))
        for side in [-1,1]:
            parts.append(panel('Strap',[(side*.06-.012,-.1,1.15),(side*.06+.012,-.1,1.15),(side*.07+.012,-.1,1.25),(side*.07-.012,-.1,1.25)],spec['pants'],surf))
            parts.append(box('Buckle',(side*.065,-.112,1.17),(.025,.010,.023),'C1B481',.003))
    # Pantalón modular de piernas separadas y cintura común.
    if style=='dress':
        skirt=loft('Skirt',[(0,0,.565,.255,.162),(0,0,.70,.225,.140),(0,0,.88,.172,.114),(0,0,WAIST,.134,.099)],spec['pants'])
        parts.append(skirt)
        skirt_surf=surface(skirt)
        for i in range(12):
            x=(-.16+(i%4)*.105);z=.63+(i//4)*.115
            parts.append(panel('PolkaDot',[(x+.009*math.cos(2*math.pi*j/6),0,z+.009*math.sin(2*math.pi*j/6)) for j in range(6)],'E7D7EA',skirt_surf))
    else:
        parts.append(pants_mesh(spec))
        for side in [-1,1]:
            if spec['group'] in ['security','police'] or spec['id'] in ['NPC01_Bomber','NPC08_Sport']:
                x=side*.174
                parts.append(box('CargoPocket',(x,-.015,.66),(.030,.115,.13),spec['pants'],.006))
    if spec['group'] in ['police','security']:
        parts.append(loft('DutyBelt',[(0,0,.988,.141,.104),(0,0,1.014,.141,.104)],'282C34'))
        parts.append(box('BeltBuckle',(0,-.108,1.002),(.039,.012,.027),'AFB4B5',.003))
    result=combine('Outfit',parts);bind(result,rig,dress=style=='dress')
    return result

def shoes(spec,rig):
    items=[]
    for side in [-1,1]:
        parts=[box('Sole',(side*.151,-.055,.025),(.130,.250,.050),'E8E2D5',.012),
               box('ShoeUpper',(side*.151,-.046,.078),(.119,.232,.090),spec['shoe'],.026)]
        shoe=combine('Shoe',parts);bind(shoe,rig,('Left' if side==1 else 'Right')+'Foot');items.append(shoe)
    return combine('Shoes',items)

def face_and_hair(spec,rig):
    head=SOURCE['LP_Head'].copy();head.data=head.data.copy();bpy.context.scene.collection.objects.link(head)
    head.data.materials.clear();head.data.materials.append(mat(spec['skin']));bind(head,rig,'Head')
    items=[];ink='282022';cream='EEE7D8';hair=spec['hair_color']
    if spec.get('mask'):items.append(box('EyeMask',(0,-.100,1.465),(.144,.010,.045),'242731',.008))
    for side in [-1,1]:
        x=side*.044;eyez=1.465;eyex=.010;eyeh=.014
        if spec['expression']=='grin':eyeh=.010
        eye_y=-.103
        if spec.get('mask'):
            items.append(panel('EyeWhite',[(x+.014*math.cos(2*math.pi*i/8),-.108,eyez+.017*math.sin(2*math.pi*i/8)) for i in range(8)],cream))
            eye_y=-.109
        items.append(panel('Eye',[(x+eyex*math.cos(2*math.pi*i/8),eye_y,eyez+eyeh*math.sin(2*math.pi*i/8)) for i in range(8)],ink))
        items.append(ico('EyeGlint',(x-.003,eye_y-.002,eyez+.004),(.0025,.0015,.0025),cream))
        tilt=(.006 if side==1 else -.002) if spec['expression']=='raised_brow' else .001
        items.append(panel('Brow',[(x-.015,-.103,1.492),(x+.015,-.103,1.492+tilt),(x+.015,-.103,1.496+tilt),(x-.015,-.103,1.496)],hair))
    nose_scale=spec.get('nose_scale',1)
    points=[(-.009,-.100,1.422),(.009,-.100,1.422),(.009,-.100,1.447),(-.009,-.100,1.447),(0,-.100-.016*nose_scale,1.428)]
    items.append(mesh('Nose',points,[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],spec['skin']))
    if spec['expression']=='grin':
        items.append(panel('Grin',[(-.026,-.103,1.413),(.026,-.103,1.413),(.019,-.103,1.398),(-.019,-.103,1.398)],cream))
    else:
        pts=[(-.020,1.410),(-.010,1.405),(0,1.404),(.010,1.405),(.020,1.410 if spec['expression']!='smirk' else 1.415)]
        verts=[(x,-.103,z+dz) for x,z in pts for dz in [-.0012,.0012]]
        items.append(mesh('Smile',verts,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(4)],ink))
    if spec.get('stache'):
        width=.032 if spec['stache']=='big' else .024
        stache_color='563D2C' if spec['id']=='Player03_Distractor' else hair
        for side in [-1,1]:items.append(panel('Mustache',[(side*.003,-.108,1.425),(side*width,-.108,1.428),(side*(width+.003),-.108,1.417),(side*.007,-.108,1.418)],stache_color))
    if spec.get('beard'):items.append(panel('Goatee',[(-.012,-.101,1.390),(.012,-.101,1.390),(.008,-.101,1.374),(-.008,-.101,1.374)],hair))
    if spec.get('freckles'):
        for side in [-1,1]:
            for i in range(3):
                x=side*(.023+i*.007);z=1.439+(i%2)*.005
                items.append(panel('Freckle',[(x+.0018*math.cos(2*math.pi*j/5),-.102,z+.0018*math.sin(2*math.pi*j/5)) for j in range(5)],'A16440'))
    if spec.get('glasses'):
        kind=spec['glasses'];w=.073 if kind=='huge' else .060;h=.055 if kind=='huge' else .044
        for side in [-1,1]:
            x=side*.044
            if kind=='round':
                pts=[(x+.028*math.cos(2*math.pi*i/12),-.112,1.465+.026*math.sin(2*math.pi*i/12)) for i in range(13)]
                items.append(tube('RoundGlasses',pts,[.0025]*13,'51443B',4))
            else:
                for z in [1.465-h/2,1.465+h/2]:items.append(box('GlassesFrame',(x,-.112,z),(w,.008,.004),'28313B',.001))
                for xx in [x-w/2,x+w/2]:items.append(box('GlassesFrame',(xx,-.112,1.465),(.004,.008,h),'28313B',.001))
        items.append(box('GlassesBridge',(0,-.112,1.470),(.030,.008,.005),'51443B',.001))
    face=combine('Face',items);bind(face,rig,'Head')
    # Peinados y sombreros comparten el lenguaje de masas facetadas.
    kind=spec['hair'];parts=[]
    parts.append(box('HairCap',(0,.004,1.541),(.213,.177,.068),hair,.027))
    if kind in ['quiff','sidepart','pixie']:
        count=4 if kind!='pixie' else 3
        for i in range(count):
            obj=ico('Quiff',(-.067+i*.041,-.028,1.574+(i%2)*.008),(.043,.055,.031),hair)
            obj.rotation_euler.y=-.2+i*.07;parts.append(obj)
    if kind in ['bun','manbun','ponytail','braid','capbun']:
        if kind in ['ponytail','braid']:
            for i in range(7):parts.append(ico('Tail',((-.008 if i%2 else .008),.105+i*.006,1.552-i*.035),(.030-i*.002,.029-i*.001,.030),hair))
        else:parts.append(ico('Bun',(0,.065,1.588),(.050,.049,.049),hair,2))
    if kind=='bob':
        for side in [-1,1]:parts.append(box('Bob',(side*.097,.016,1.457),(.031,.142,.170),hair,.013))
    if kind=='wig':
        for i in range(11):
            a=2*math.pi*i/11;parts.append(ico('WigCurl',(.083*math.cos(a),.063*math.sin(a),1.556),(.039,.036,.035),hair))
    if kind in ['cap','capbun','routercap','beanie','tinybeanie']:
        hatcolor='293F68' if spec['group']=='police' else ('CE5B3D' if kind=='routercap' else ('E7812D' if kind=='tinybeanie' else '292C36'))
        capscale=spec.get('cap_scale',1)
        parts.append(box('Cap',(0,.001,1.571),(.226*capscale,.185*capscale,.065),hatcolor,.027))
        if kind not in ['beanie','tinybeanie']:
            parts.append(box('Visor',(0,-.106,1.545),(.214*capscale,.100,.018),hatcolor,.010))
        if kind=='routercap':
            parts.append(box('Router',(0,.005,1.629),(.11,.078,.047),'E5E3DA',.008))
            for side in [-1,1]:parts.append(tube('Antenna',[(side*.04,.01,1.65),(side*.050,.01,1.755)],[.006,.004],'36404B',6))
    if spec.get('goggles'):
        for side in [-1,1]:parts.append(box('Goggle',(side*.045,-.073,1.562),(.057,.029,.034),'515B61',.008));parts.append(box('Lens',(side*.045,-.090,1.562),(.045,.006,.023),'B6D3D4',.005))
    hairstyle=combine('Hair',parts);bind(hairstyle,rig,'Head')
    for obj in [head,face,hairstyle]:obj['region']='head'
    return [head,face,hairstyle]

def accessories(spec,rig,outfit_obj):
    parts=[];style=spec['style']
    clothing_surface=surface(outfit_obj)
    def add(obj,bone='Chest'):bind(obj,rig,bone);parts.append(obj);return obj
    if spec.get('radio'):
        add(box('Radio',(.132,-.045,1.006),(.043,.030,.079),'2B323B',.006),'Hips')
        add(tube('RadioAntenna',[(.132,-.045,1.046),(.132,-.045,1.125)],[.004,.003],'2B323B',5),'Hips')
    if spec['group']=='security':
        add(tube('Baton',[(-.155,.018,.77),(-.155,.018,.99)],[.012,.012],'292E36',6),'Hips')
        add(tube('BatonGrip',[(-.155,.018,.96),(-.155,.018,1.035)],[.016,.016],'3B414A',6),'Hips')
    if spec['group']=='police':
        add(box('Holster',(-.154,.008,.925),(.048,.054,.115),'242A34',.007),'Hips')
        grip=box('HolsteredGrip',(-.154,-.003,1.000),(.027,.036,.052),'3D444E',.004)
        grip.rotation_euler.y=.22
        P.activate(grip);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);add(grip,'Hips')
    if spec['group'] in ['police','security']:
        label='POLICIA' if spec['group']=='police' else 'SEGURIDAD'
        for back in [False,True]:
            text=text_mesh(label,(0,.119 if back else -.119,1.185),.029 if back else .026,'EFE7CE',back)
            for v in text.data.vertices:
                hit,_,_,_=clothing_surface.ray_cast(Vector((v.co.x,1 if back else -1,v.co.z)),Vector((0,-1 if back else 1,0)))
                if hit:v.co.y=hit.y+(.0025 if back else -.0025)
            add(text)
        hit,_,_,_=clothing_surface.ray_cast(Vector((-.092,-1,1.195)),Vector((0,1,0)))
        add(box('Badge',(-.092,hit.y-.006 if hit else -.108,1.195),(.027,.009,.034),'D5BA5C',.005))
    if spec.get('heart'):
        verts=[(x,-.112,z) for x,z in [(-.06,1.184),(-.035,1.199),(0,1.185),(.035,1.199),(.06,1.184),(.047,1.15),(0,1.12),(-.047,1.15)]]
        add(panel('Heart',verts,'CF5048'))
        add(text_mesh('MAMA',(0,-.115,1.154),.021,'F1EBD9'))
    if spec.get('loot_bag'):
        add(ico('LootBag',(-.235,.105,.86),(.19,.145,.235),'C4A06B',2),'Hips')
        add(box('BagKnot',(-.235,.105,1.106),(.065,.060,.065),'B68C54',.008),'Hips')
        add(text_mesh('$',(-.285,-.044,.86),.115,'496D42'),'Hips')
    if spec.get('laptop'):
        add(box('LaptopBackpack',(0,.162,1.07),(.245,.10,.29),'5C7182',.014),'Chest')
        for i,color in enumerate(['E2B644','A6BA69','D77456']):add(box('Sticker',(-.065+i*.065,.217,1.10),(.044,.005,.043),color,.003),'Chest')
    if spec.get('purse'):
        add(box('Purse',(-.405,-.005,.635),(.15,.075,.13),'B64656',.023),'RightHand')
        pts=[(-.405+.05*math.cos(math.pi*i/8),-.005,.697+.048*math.sin(math.pi*i/8)) for i in range(9)]
        add(tube('PurseHandle',pts,[.006]*9,'8D3D4B',5),'RightHand')
    if spec.get('hammer'):
        add(tube('MalletHandle',[(-.402,0,.76),(-.402,0,.37)],[.018,.018],'9D744A',6),'RightHand')
        add(box('MalletHead',(-.402,0,.335),(.25,.15,.14),'8B6542',.018),'RightHand')
    return combine('Accessories',parts) if parts else None

def warp_actor(spec,parts,rig):
    width=spec['width'];head_scale=spec.get('head_scale',1)
    anchor=Vector((0,-.015,1.3325))
    for obj in parts:
        if obj.get('region')=='head':
            for v in obj.data.vertices:v.co=anchor+(v.co-anchor)*head_scale
    high=max(v.co.z for o in parts for v in o.data.vertices);factor=spec['height']/high
    for obj in parts:
        for v in obj.data.vertices:v.co=Vector((v.co.x*width,v.co.y,v.co.z*factor))
        obj.data.update()
    P.activate(rig);bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:
        bone.head=(bone.head.x*width,bone.head.y,bone.head.z*factor)
        bone.tail=(bone.tail.x*width,bone.tail.y,bone.tail.z*factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    return factor

def build_character(spec):
    scene=new_scene('Cast_'+spec['id'])
    actor=bpy.data.collections.new(spec['id']+'_Actor');scene.collection.children.link(actor)
    original=next(o for o in TEMPLATE.objects if o.type=='ARMATURE')
    rig=original.copy();rig.data=original.data.copy();scene.collection.objects.link(rig);rig.name=spec['id']+'_Rig'
    if spec.get('approved'):
        parts=[]
        for name in ['LP_Body','LP_Jacket','LP_Top','LP_Pants','LP_Shoes','LP_Earrings','LP_Head','LP_Face','LP_Hair']:
            obj=SOURCE[name].copy();obj.data=obj.data.copy();scene.collection.objects.link(obj);obj.parent=rig
            for m in obj.modifiers:
                if m.type=='ARMATURE':m.object=rig
            parts.append(obj)
        spec['height']=1.65;factor=1
    else:
        parts=[visible_skin(spec,rig),outfit(spec,rig),shoes(spec,rig)]+face_and_hair(spec,rig)
        extra=accessories(spec,rig,parts[1])
        if extra:parts.append(extra)
        factor=warp_actor(spec,parts,rig)
    for obj in parts+[rig]:
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        actor.objects.link(obj)
        obj.hide_set(False)
    for i,obj in enumerate(parts):
        role=obj.name.split('.')[0].replace('LP_','');obj.name=spec['id']+'_'+role
        obj['character_id']=spec['id']
        if not spec.get('approved'):P.flat(obj)
    rig.hide_set(True);rig.hide_render=True
    return {'spec':spec,'scene':scene,'collection':actor,'parts':parts,'rig':rig,'scale_z':factor}

def shot(scene,center,direction,scale,size,path):
    bpy.context.window.scene=scene;cam=scene.camera;center=Vector(center)
    cam.location=center+Vector(direction);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)

def export_character(record):
    spec=record['spec'];scene=record['scene'];parts=record['parts'];rig=record['rig'];identifier=spec['id']
    bpy.context.window.scene=scene;rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT')
    for obj in parts+[rig]:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    path=BASE/'fbx'/(identifier+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','ARMATURE'},
        apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,
        add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
    rig.hide_set(True)
    height=spec['height'];folder=BASE/'renders'/identifier;folder.mkdir(parents=True,exist_ok=True)
    shot(scene,(0,0,height/2),(0,-6,0),height*1.10,(620,820),folder/'front.png')
    shot(scene,(0,0,height/2),(-6,0,0),height*1.10,(620,820),folder/'side.png')
    shot(scene,(0,0,height/2),(0,6,0),height*1.10,(620,820),folder/'back.png')
    head=[o for o in parts if 'Head' in o.name or o.get('region')=='head']
    centers=[v.co.z for o in head for v in o.data.vertices]
    center_z=(min(centers)+max(centers))/2 if centers else height*.88
    shot(scene,(0,-.01,center_z),(-4,-6,0),.46*(height/1.65),(540,620),folder/'head.png')
    return {'id':identifier,'label':spec['label'],'group':spec['group'],'height_m':height,
            'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts),
            'meshes':len(parts),'bones':len(rig.data.bones),'approved_source':bool(spec.get('approved'))}

def gallery(records,name='Cast_Gallery'):
    scene=new_scene(name)
    scene.view_settings.exposure=-.70
    for i,record in enumerate(records):
        col=i%6;row=i//6;rows=(len(records)+5)//6;x=(col-2.5)*GALLERY_SPACING;z=(rows-1-row)*GALLERY_ROW_HEIGHT
        instance=bpy.data.objects.new(record['spec']['id']+'_Display',None);scene.collection.objects.link(instance)
        instance.instance_type='COLLECTION';instance.instance_collection=record['collection'];instance.location=(x,0,z)
        box('DisplayPlinth',(x,0,z-.035),(1.65,.75,.06),'BBC2C3',.015)
        label=text_mesh(record['spec']['label'],(x,-.40,z-.20),.095,'EDE8DD')
    for obj in list(scene.objects):
        if obj.type=='LIGHT':bpy.data.objects.remove(obj,do_unlink=True)
    for name,pos,power in [('GalleryKey',(0,-7,8),2300),('GalleryFill',(-6,-4,5),1400),('GalleryRim',(5,3,8),1600)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=10;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
        obj.location=pos;obj.rotation_euler=(Vector((0,0,2.5))-obj.location).to_track_quat('-Z','Y').to_euler()
    rows=(len(records)+5)//6
    center_z=((rows-1)*GALLERY_ROW_HEIGHT+1.80)/2
    camera=scene.camera;camera.location=(0,-20,center_z);camera.rotation_euler=(Vector((0,0,center_z))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=13.4;scene.render.resolution_x=3600;scene.render.resolution_y=max(700,round(3600*(rows*2.3)/13.4))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.region_3d.view_location=(0,0,center_z);space.region_3d.view_distance=8
                space.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
                allowed={v.identifier for v in space.region_3d.bl_rna.properties['view_perspective'].enum_items}
                if 'CAMERA' in allowed:space.region_3d.view_perspective='CAMERA'
                space.overlay.show_extras=False
    return scene

def main(only=None,save=True):
    source_setup();catalog=json.loads((BASE/'cast_catalog.json').read_text(encoding='utf-8'))
    if only:catalog=[s for s in catalog if s['id'] in only]
    records=[];manifest=[]
    (BASE/'fbx').mkdir(exist_ok=True);(BASE/'renders').mkdir(exist_ok=True)
    for spec in catalog:
        record=build_character(spec);records.append(record)
        if save:manifest.append(export_character(record))
        print('CHARACTER_READY',spec['id'],flush=True)
    scene=gallery(records)
    if save:
        scene.render.filepath=str(BASE/'renders'/'gallery.png');bpy.ops.render.render(write_still=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Alarma_LowPoly_Cast.blend'),copy=True)
        (BASE/'manifest.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'characters':manifest,'unity_avatars_verified':False},indent=2,ensure_ascii=False),encoding='utf-8')
    return records,scene

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    main(args.only.split(',') if args.only else None)
