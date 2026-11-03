"""Revisión de las piernas del elenco propio. Blender 4.5+, sin assets externos.
blender -b --python-exit-code 1 -P correct_leg_alignment.py
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import character_primitives as P

# Toñito, coordenadas finales en metros. Muslo y pantorrilla de longitud semejante.
MUSCLE_KNEE=(.178,-.020,.565)
MUSCLE_ANKLE_X=.205
# Z, radio lateral, profundidad. La superficie continúa dentro del pantalón y del zapato.
MUSCLE_LEG_PROFILE=[(.106,.040,.043),(.16,.043,.047),(.28,.058,.060),
                    (.40,.071,.068),(.49,.065,.062),(.54,.058,.056),
                    (.565,.058,.056),(.59,.061,.059),(.66,.077,.076),
                    (.78,.085,.075),(.91,.090,.075)]
KNEE_BLEND=.055
HIP_BLEND=.14
FIX_SHORTS={'NPC03_Tourist','NPC10_Cardigan','Player04_Muscle'}

def actor_id(scene):
    if scene.name.startswith('Cast_Player04_Muscle_Gym_R1'):return 'Player04_Muscle'
    return scene.name.removeprefix('Cast_')

def axis_at(rig,side,z):
    prefix='Left' if side==1 else 'Right'
    knee=rig.data.bones[prefix+'LowerLeg'].head_local
    bone=rig.data.bones[prefix+('LowerLeg' if z<=knee.z else 'UpperLeg')]
    a,b=bone.head_local,bone.tail_local
    return a.lerp(b,(z-a.z)/(b.z-a.z))

def skin_weights(obj,rig):
    obj.parent=rig
    for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
    names=['Hips']+[s+n for s in ['Left','Right'] for n in ['UpperLeg','LowerLeg','Foot']]
    groups={n:obj.vertex_groups.new(name=n) for n in names}
    for v in obj.data.vertices:
        prefix='Left' if v.co.x>=0 else 'Right'
        hip=rig.data.bones[prefix+'UpperLeg'].head_local.z
        knee=rig.data.bones[prefix+'LowerLeg'].head_local.z
        ankle=rig.data.bones[prefix+'Foot'].head_local.z
        if abs(v.co.x)<.012:weights={'Hips':1}
        elif v.co.z>hip-HIP_BLEND:
            t=max(0,min(1,(v.co.z-(hip-HIP_BLEND))/HIP_BLEND));weights={'Hips':t,prefix+'UpperLeg':1-t}
        elif v.co.z>knee+KNEE_BLEND:weights={prefix+'UpperLeg':1}
        elif v.co.z>knee-KNEE_BLEND:
            t=(v.co.z-knee+KNEE_BLEND)/(2*KNEE_BLEND);weights={prefix+'UpperLeg':t,prefix+'LowerLeg':1-t}
        elif v.co.z<ankle+.065:
            t=max(0,min(1,(v.co.z-ankle+.015)/.08));weights={prefix+'LowerLeg':t,prefix+'Foot':1-t}
        else:weights={prefix+'LowerLeg':1}
        for n,w in weights.items():
            if w>1e-7:groups[n].add([v.index],w,'REPLACE')
    mod=next((m for m in obj.modifiers if m.type=='ARMATURE'),None)
    if mod is None:mod=obj.modifiers.new('Humanoid','ARMATURE')
    mod.object=rig

def repair_female_clothing(scene,rig):
    """Impide que manos/pies arrastren costuras de pantalón y piernas arrastren la chaqueta."""
    pants=next(o for o in scene.objects if o.type=='MESH' and '_Pants' in o.name)
    skin_weights(pants,rig)
    for obj in [o for o in scene.objects if o.type=='MESH' and any(n in o.name for n in ['_Jacket','_Top'])]:
        original=[{obj.vertex_groups[g.group].name:g.weight for g in v.groups} for v in obj.data.vertices]
        for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
        groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones}
        # Conserva los pesos válidos de las mangas; reasigna solo influencias ajenas a la prenda.
        for vertex,weights in zip(obj.data.vertices,original):
            invalid=sum(weights.pop(name) for name in list(weights) if any(n in name for n in ['Leg','Foot','Toes']))
            head=weights.pop('Head',0)
            if head:weights['Neck']=weights.get('Neck',0)+head
            if invalid:
                if abs(vertex.co.x)>.19:
                    side='Left' if vertex.co.x>0 else 'Right'
                    elbow=rig.data.bones[side+'LowerArm'].head_local
                    name=side+('LowerArm' if vertex.co.z<elbow.z else 'UpperArm')
                else:name='Hips' if vertex.co.z<rig.data.bones['Spine'].head_local.z else 'Spine'
                weights[name]=weights.get(name,0)+invalid
            total=sum(weights.values())
            for name,weight in weights.items():
                if weight>1e-7:groups[name].add([vertex.index],weight/total,'REPLACE')

def change_muscle_bones(rig,shoes):
    previous={s:rig.data.bones[s+'Foot'].head_local.x for s in ['Left','Right']}
    P.activate(rig);bpy.ops.object.mode_set(mode='EDIT')
    for side,prefix in [(1,'Left'),(-1,'Right')]:
        upper=rig.data.edit_bones[prefix+'UpperLeg'];lower=rig.data.edit_bones[prefix+'LowerLeg']
        knee=Vector((side*MUSCLE_KNEE[0],MUSCLE_KNEE[1],MUSCLE_KNEE[2]))
        ankle=lower.tail.copy();ankle.x=side*MUSCLE_ANKLE_X
        upper.tail=knee;lower.head=knee;lower.tail=ankle
        upper.align_roll(Vector((0,1,0)));lower.align_roll(Vector((0,1,0)))
        dx=side*MUSCLE_ANKLE_X-previous[prefix]
        foot=rig.data.edit_bones[prefix+'Foot'];foot.head=ankle;foot.tail.x+=dx
        toes=rig.data.edit_bones[prefix+'Toes'];toes.head=foot.tail.copy();toes.tail.x+=dx
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in shoes.data.vertices:
        prefix='Left' if v.co.x>0 else 'Right';side=1 if v.co.x>0 else -1
        v.co.x+=side*MUSCLE_ANKLE_X-previous[prefix]
    shoes.data.update()

def replace_muscle_legs(body,rig):
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<.82 and abs(v.co.x)<.40],context='VERTS')
    bm.to_mesh(body.data);bm.free();body.data.update()
    # El material de piel ya existe en la malla original.
    skin=next(m for m in body.data.materials if m.name.startswith('Cast_B17B52'))
    items=[body]
    for side in [-1,1]:
        verts=[];n=12
        for z,rx,ry in MUSCLE_LEG_PROFILE:
            center=axis_at(rig,side,z)
            # Pantorrilla algo más llena hacia atrás, sin desplazar la articulación.
            back=.008*max(0,1-abs(z-.40)/.20)
            verts.extend((center.x+rx*math.cos(2*math.pi*i/n),center.y+back+ry*math.sin(2*math.pi*i/n),z) for i in range(n))
        faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(MUSCLE_LEG_PROFILE)-1) for i in range(n)]
        faces+=[tuple(reversed(range(n))),tuple((len(MUSCLE_LEG_PROFILE)-1)*n+i for i in range(n))]
        leg=P.mesh('AlignedLeg',verts,faces,skin);skin_weights(leg,rig);items.append(leg)
    return P.join(body.name,items)

def remove_old_trousers(obj):
    # La ropa se conserva; se reemplaza únicamente su componente conectado más bajo.
    bm=bmesh.new();bm.from_mesh(obj.data);pending=set(bm.verts);components=[]
    while pending:
        start=pending.pop();part={start};stack=[start]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in pending:pending.remove(v);part.add(v);stack.append(v)
        components.append(part)
    trousers=min(components,key=lambda c:min(v.co.z for v in c))
    material_index=next(iter(trousers)).link_faces[0].material_index
    material=obj.data.materials[material_index]
    # Recupera la escala vertical real del borde superior original, sin aproximarla desde el tobillo.
    vertical_scale=max(v.co.z for v in trousers)/1.008
    bmesh.ops.delete(bm,geom=list(trousers),context='VERTS');bm.to_mesh(obj.data);bm.free();obj.data.update()
    return material,vertical_scale

def centered_shorts(spec,rig,material,scale):
    width=spec['width']
    hem=.525*scale;verts=[];faces=[];tops={}
    def ring(side,z,rx,ry):
        center=axis_at(rig,side,z);ids=list(range(len(verts),len(verts)+8))
        verts.extend((center.x+rx*math.cos(2*math.pi*i/8),center.y+ry*math.sin(2*math.pi*i/8),z) for i in range(8));return ids
    def bridge(a,b):faces.extend((a[i],a[(i+1)%len(a)],b[(i+1)%len(b)],b[i]) for i in range(len(a)))
    for side in [-1,1]:
        radius=(.107 if spec.get('culottes') else .077)*width
        lower=[ring(side,z,rx,ry) for z,rx,ry in [
            (hem,radius,.093),(hem+.018*scale,radius,.093),(.665*scale,.082*width,.103)]]
        for a,b in zip(lower,lower[1:]):bridge(a,b)
        ids=list(range(len(verts),len(verts)+8))
        verts.extend((side*.097*width+.097*width*math.cos(2*math.pi*i/8),.117*math.sin(2*math.pi*i/8),.876*scale) for i in range(8))
        inner=[3,4,5] if side==1 else [1,0,7]
        for j,i in enumerate(inner):verts[ids[i]]=(0,(1-j)*.119,(.822 if j!=1 else .777)*scale)
        bridge(lower[-1],ids);tops[side]=ids
    remap={tops[-1][l]:tops[1][r] for l,r in [(1,3),(0,4),(7,5)]}
    faces=[tuple(remap.get(i,i) for i in face) for face in faces]
    lower=[tops[1][i] for i in [5,6,7,0,1,2,3]]+[tops[-1][i] for i in [2,3,4,5,6]]
    for z,rx,ry in [(.911,.167,.117),(.990,.137,.099),(1.008,.134,.097)]:
        upper=list(range(len(verts),len(verts)+12))
        verts.extend((rx*width*math.cos(-math.pi/2+2*math.pi*i/12),ry*math.sin(-math.pi/2+2*math.pi*i/12),z*scale) for i in range(12))
        bridge(lower,upper);lower=upper
    obj=P.mesh('CenteredShorts',verts,faces,material)
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    P.activate(obj);mod=obj.modifiers.new('Low poly rounded cage','SUBSURF');mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Borde continuo y horizontal; queda centrado en el mismo eje que la pierna.
    bm=bmesh.new();bm.from_mesh(obj.data)
    for side in [-1,1]:
        boundary={v for e in bm.edges if e.is_boundary for v in e.verts if v.co.z<hem+.09 and v.co.x*side>0}
        mean=sum(v.co.x for v in boundary)/len(boundary);mean_y=sum(v.co.y for v in boundary)/len(boundary)
        target=axis_at(rig,side,hem)
        for v in boundary:v.co.x+=target.x-mean;v.co.y+=target.y-mean_y;v.co.z=hem
    bm.to_mesh(obj.data);bm.free();obj.data.update();P.flat(obj);skin_weights(obj,rig)
    return obj

def main():
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/elenco_gym_r1.blend'))
    catalog={s['id']:s for s in json.loads((BASE/'cast_catalog.json').read_text(encoding='utf-8'))}
    scenes=[s for s in bpy.data.scenes if s.name.startswith('Cast_') and s.name!='Cast_Gallery' and not s.name.startswith('Cast_Source_')]
    manifest=[]
    for scene in scenes:
        identifier=actor_id(scene);bpy.context.window.scene=scene
        rig=next(o for o in scene.objects if o.type=='ARMATURE')
        rig.hide_set(False)
        if identifier=='NPC02_Denim':repair_female_clothing(scene,rig)
        if identifier in FIX_SHORTS:
            body=next(o for o in scene.objects if o.type=='MESH' and '_Body' in o.name)
            outfit=next(o for o in scene.objects if o.type=='MESH' and '_Outfit' in o.name)
            if identifier=='Player04_Muscle':
                shoes=next(o for o in scene.objects if o.type=='MESH' and '_Shoes' in o.name)
                change_muscle_bones(rig,shoes);replace_muscle_legs(body,rig)
            material,scale=remove_old_trousers(outfit);shorts=centered_shorts(catalog[identifier],rig,material,scale)
            outfit['review_hem_z']=.525*scale
            P.join(outfit.name,[outfit,shorts])
        meshes=[o for o in scene.objects if o.type=='MESH']
        for obj in meshes+[rig]:obj['rig_review']='R2_2026-11-01'
        scene.name='RigReview_'+identifier
        height=max(v.co.z for obj in meshes for v in obj.data.vertices)
        manifest.append({'id':identifier,'label':catalog[identifier]['label'],'group':catalog[identifier]['group'],
                         'height_m':height,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
                         'meshes':len(meshes),'bones':len(rig.data.bones),'approved_source':identifier=='NPC02_Denim'})
        rig.hide_set(True)
    bpy.data.scenes['Cast_Gallery'].name='RigReview_Gallery'
    (BASE/'manifest.json').write_text(json.dumps({'characters':sorted(manifest,key=lambda s:s['id']),
        'blender_version':bpy.app.version_string,'unity_avatars_verified':False},indent=2,ensure_ascii=False),encoding='utf-8')
    bpy.context.window.scene=bpy.data.scenes['RigReview_Player04_Muscle']
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Alarma_RigLegs_R2.blend'))
    print('LEG_ALIGNMENT_CORRECTED',len(manifest),flush=True)

if __name__=='__main__':main()
