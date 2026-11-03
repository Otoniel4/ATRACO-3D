"""Toñito: torso en V, hombros integrados y brazos proporcionados. Sin assets externos.
Ejecutar: blender -b --python-exit-code 1 -P build_gym_revision.py
"""
import bpy, bmesh, json, sys, math
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import build_cast as G

# Medidas canónicas en metros, anteriores a la escala del personaje de 1,88 m.
# Cintura fija; caja torácica más ancha y profunda para obtener un torso en V.
CHEST_PROFILE=[(.990,.118,.084),(1.055,.148,.094),(1.115,.189,.116),
               (1.175,.219,.132),(1.220,.228,.133),(1.248,.207,.112),
               (1.282,.046,.048)]
SHOULDER_OFFSET=.046
ELBOW_OFFSET=.024
WRIST_OFFSET=.018
ARM_RADII=[.037,.059,.067,.068,.058,.044,.052,.040,.029]
HEIGHT=1.88
WIDTH=1.48

def adjust_source_rig():
    """Desplaza articulaciones y geometría con las mismas medidas."""
    rig=next(o for o in G.TEMPLATE.objects if o.type=='ARMATURE')
    bpy.context.window.scene=G.TEMPLATE
    G.P.activate(rig);bpy.ops.object.mode_set(mode='EDIT')
    for side,prefix in [(1,'Left'),(-1,'Right')]:
        arm=rig.data.edit_bones[prefix+'UpperArm']
        forearm=rig.data.edit_bones[prefix+'LowerArm']
        shoulder=arm.head.copy()+Vector((side*SHOULDER_OFFSET,0,.004))
        elbow=arm.tail.copy()+Vector((side*ELBOW_OFFSET,0,0))
        wrist=forearm.tail.copy()+Vector((side*WRIST_OFFSET,0,0))
        rig.data.edit_bones[prefix+'Shoulder'].tail=shoulder
        arm.head=shoulder;arm.tail=elbow;forearm.head=elbow;forearm.tail=wrist
        hand=rig.data.edit_bones[prefix+'Hand'];hand.head=wrist
        hand.tail+=Vector((side*WRIST_OFFSET,0,0))
    bpy.ops.object.mode_set(mode='OBJECT')

def torso(name,color,offset=0):
    return G.loft(name,[(0,0,z,rx+offset,ry+offset) for z,rx,ry in CHEST_PROFILE],color,16,caps=False)

def set_ring_weights(obj,rig,ring_weights,n=10):
    for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
    for j,weights in enumerate(ring_weights):
        for name,value in weights.items():
            group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
            group.add(list(range(j*n,(j+1)*n)),value,'REPLACE')
    obj.parent=rig
    mod=obj.modifiers.new('Humanoid','ARMATURE');mod.object=rig

def skin(spec,rig):
    # Conserva exclusivamente las pantorrillas de la base aprobada bajo el pantalón corto.
    legs=G.SOURCE['LP_Body'].copy();legs.data=legs.data.copy();bpy.context.scene.collection.objects.link(legs)
    for mod in list(legs.modifiers):legs.modifiers.remove(mod)
    bm=bmesh.new();bm.from_mesh(legs.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not (.10<f.calc_center_median().z<.57 and abs(f.calc_center_median().x)<.235)],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.to_mesh(legs.data);bm.free()
    legs.data.materials.clear();legs.data.materials.append(G.mat(spec['skin']));G.bind(legs,rig)
    neck=G.loft('StrongNeck',[(0,0,1.245,.042,.042),(0,0,1.29,.040,.041),(0,0,1.35,.036,.037)],spec['skin'],10)
    G.bind(neck,rig,'Neck')
    thorax=torso('SkinThorax',spec['skin'],-.004)
    G.bind(thorax,rig,'Chest')
    parts=[legs,neck,thorax]
    for side,prefix in [(-1,'Right'),(1,'Left')]:
        upper=rig.data.bones[prefix+'UpperArm'];lower=rig.data.bones[prefix+'LowerArm']
        sh=upper.head_local.copy();el=upper.tail_local.copy();wr=lower.tail_local.copy()
        points=[sh+Vector((-side*.044,0,0)),sh+Vector((-side*.016,0,0)),sh,
                sh.lerp(el,.30),sh.lerp(el,.76),el,el.lerp(wr,.28),el.lerp(wr,.73),wr]
        arm=G.tube('GymArm',points,ARM_RADII,spec['skin'],10)
        weights=[{'Chest':.75,prefix+'Shoulder':.25},
                 {prefix+'Shoulder':.55,prefix+'UpperArm':.45},
                 {prefix+'Shoulder':.20,prefix+'UpperArm':.80},
                 {prefix+'UpperArm':1},{prefix+'UpperArm':.90,prefix+'LowerArm':.10},
                 {prefix+'UpperArm':.5,prefix+'LowerArm':.5},
                 {prefix+'LowerArm':1},{prefix+'LowerArm':1},
                 {prefix+'LowerArm':.6,prefix+'Hand':.4}]
        set_ring_weights(arm,rig,weights);parts.append(arm)
        direction=(wr-el).normalized()
        palm=G.box('Palm',wr+direction*.036,(.061,.046,.080),spec['skin'],.012)
        thumb=G.box('Thumb',wr+direction*.022+Vector((-side*.025,-.010,0)),(.025,.035,.040),spec['skin'],.008)
        hand=G.combine('Hand',[palm,thumb]);G.bind(hand,rig,prefix+'Hand');parts.append(hand)
    return G.combine('Body',parts)

def clothes(spec,rig):
    tank=torso('GymTank',spec['top'],.004)
    # Contorno continuo: los deltoides entran bajo la prenda, sin escalones ni cajas de tirantes.
    # El torso acompaña a columna y pecho, sin heredar pesos de los bíceps próximos.
    G.bind(tank,rig,'Chest')
    for group in list(tank.vertex_groups):tank.vertex_groups.remove(group)
    groups={n:tank.vertex_groups.new(name=n) for n in ['Hips','Spine','Chest']}
    for v in tank.data.vertices:
        if v.co.z<1.075:
            t=max(0,min(1,(v.co.z-.990)/.085));weights={'Hips':1-t,'Spine':t}
        else:
            t=max(0,min(1,(v.co.z-1.075)/.075));weights={'Spine':1-t,'Chest':t}
        for name,w in weights.items():
            if w:groups[name].add([v.index],w,'REPLACE')
    shorts=G.pants_mesh(spec);G.bind(shorts,rig)
    return G.combine('Outfit',[tank,shorts])

def equipment(spec,rig,outfit):
    # Sitúa el dibujo delante del pecho ensanchado; desplaza el mazo junto con la mano.
    items=[]
    verts=[(x,-.145,z) for x,z in [(-.06,1.184),(-.035,1.199),(0,1.185),(.035,1.199),(.06,1.184),(.047,1.15),(0,1.12),(-.047,1.15)]]
    heart=G.panel('Heart',verts,'CF5048');G.bind(heart,rig,'Chest');items.append(heart)
    label=G.text_mesh('MAMA',(0,-.148,1.154),.021,'F1EBD9')
    G.bind(label,rig,'Chest');items.append(label)
    x=-.402-WRIST_OFFSET
    for item in [G.tube('MalletHandle',[(x,0,.76),(x,0,.37)],[.018,.018],'9D744A',6),
                 G.box('MalletHead',(x,0,.335),(.25,.15,.14),'8B6542',.018)]:
        G.bind(item,rig,'RightHand');items.append(item)
    return G.combine('Accessories',items)

def main():
    # Conserva el elenco anterior dentro de una copia y sustituye solo su Toñito.
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/elenco_anterior.blend'))
    old=bpy.data.scenes['Cast_Player04_Muscle'];old.name='BeforeGym_Player04_Muscle'
    gallery=bpy.data.scenes['Cast_Gallery']
    G.source_setup();adjust_source_rig()
    spec=next(s for s in json.loads((BASE/'cast_catalog.json').read_text(encoding='utf-8')) if s['id']=='Player04_Muscle')
    spec['height']=HEIGHT;spec['width']=WIDTH
    G.visible_skin=skin;G.outfit=clothes;G.accessories=equipment
    record=G.build_character(spec)
    record['scene'].name='Cast_Player04_Muscle_Gym_R1'
    record['collection'].name='Player04_Muscle_Gym_R1_Actor'
    (BASE/'fbx').mkdir(exist_ok=True);(BASE/'renders').mkdir(exist_ok=True)
    info=G.export_character(record)
    (BASE/'manifest.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'characters':[info],'unity_avatars_verified':False},indent=2,ensure_ascii=False),encoding='utf-8')
    folder=BASE/'renders'/'Player04_Muscle'
    G.shot(record['scene'],(0,0,HEIGHT/2),(-4,-7,1),HEIGHT*1.11,(850,1050),folder/'three_quarter.png')
    # Cámara de trabajo legible al abrir la escena individual.
    G.shot(record['scene'],(0,0,HEIGHT/2),(0,-6,0),HEIGHT*1.10,(820,1000),folder/'front.png')
    for obj in gallery.objects:
        if obj.instance_collection and obj.instance_collection==next(c for c in old.collection.children if c.name.startswith('Player04_Muscle_Actor')):
            obj.instance_collection=record['collection']
    bpy.context.window.scene=gallery
    gallery.render.filepath=str(BASE/'renders'/'gallery.png');bpy.ops.render.render(write_still=True)
    bpy.context.window.scene=record['scene']
    (BASE/'gym_measures.json').write_text(json.dumps({'height_m':HEIGHT,'canonical_profile':CHEST_PROFILE,'arm_radii':ARM_RADII,
        'shoulder_offset':SHOULDER_OFFSET,'elbow_offset':ELBOW_OFFSET,'wrist_offset':WRIST_OFFSET},indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Alarma_Tonito_Gym_R1.blend'))
    print('GYM_REVISION_READY',info['triangles'],flush=True)

if __name__=='__main__':main()
