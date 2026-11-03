"""Aplica la corrección aprobada de Toñito a los otros 17 actores.
blender -b --python-exit-code 1 -P apply_cast_legs.py
"""
import bpy,bmesh,sys,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import character_primitives as P
from leg_tools import axis_at,map_height,move_point,bind_region,components,section

# Cada actor conserva su altura. La rodilla divide muslo/pantorrilla casi por mitades.
STANCE_FACTOR=.918
KNEE_MIDPOINT_OFFSET=-.002
KNEE_FORWARD=-.020
CALF_RADII=(.071,.068)
FEMALE_RADIUS_FACTOR=.75
MALE_RADIUS_FACTOR=.82
GARMENT_CLEARANCE=.006
PRESERVE_ID='Player04_Muscle'

def snapshot(rig):
    return {s:[rig.data.bones[s+'UpperLeg'].head_local.copy(),rig.data.bones[s+'LowerLeg'].head_local.copy(),rig.data.bones[s+'Foot'].head_local.copy()] for s in ['Left','Right']}

def fingerprint(scene):
    result=hashlib.sha256()
    for o in sorted((o for o in scene.objects if o.type in {'MESH','ARMATURE'}),key=lambda o:o.name):
        if o.type=='MESH':
            for v in o.data.vertices:
                result.update(struct.pack('3d',*v.co))
                for g in v.groups:result.update((o.vertex_groups[g.group].name+':'+str(g.weight)).encode())
            for p in o.data.polygons:result.update(str(tuple(p.vertices)).encode())
        else:
            for b in o.data.bones:
                result.update(struct.pack('6d',*(tuple(b.head_local)+tuple(b.tail_local))))
                for row in b.matrix_local:result.update(struct.pack('4d',*row))
    return result.hexdigest()

def adjust_joints(rig,shoes,height):
    old=snapshot(rig);scale=height/1.88
    P.activate(rig);bpy.ops.object.mode_set(mode='EDIT')
    for side,sign in [('Left',1),('Right',-1)]:
        hip,previous_knee,ankle=old[side];new_ankle=ankle.copy();new_ankle.x*=STANCE_FACTOR
        z=(hip.z+ankle.z)/2+KNEE_MIDPOINT_OFFSET*scale
        t=(hip.z-z)/(hip.z-ankle.z)
        knee=Vector((hip.x+(new_ankle.x-hip.x)*t,KNEE_FORWARD*scale,z))
        upper=rig.data.edit_bones[side+'UpperLeg'];lower=rig.data.edit_bones[side+'LowerLeg']
        upper.tail=knee;lower.head=knee;lower.tail=new_ankle
        upper.align_roll(Vector((0,1,0)));lower.align_roll(Vector((0,1,0)))
        dx=new_ankle.x-ankle.x
        foot=rig.data.edit_bones[side+'Foot'];foot.head=new_ankle;foot.tail.x+=dx
        toes=rig.data.edit_bones[side+'Toes'];toes.head=foot.tail.copy();toes.tail.x+=dx
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in shoes.data.vertices:
        side='Left' if v.co.x>0 else 'Right';v.co.x+=old[side][2].x*(STANCE_FACTOR-1)
    shoes.data.update()
    return old,snapshot(rig)

def warp_clothing(scene,rig,old,new,height,spec):
    garments=[];hip=old['Left'][0].z
    for obj in scene.objects:
        if obj.type!='MESH' or not any(n in obj.name for n in ['_Outfit','_Pants']):continue
        if spec.get('style')=='dress':
            # La falda conserva su caída y los pesos de Hips; ambas piernas pasan por debajo.
            garments.append((obj,None));continue
        if '_Pants' in obj.name:indices=set(range(len(obj.data.vertices)))
        else:
            indices=set()
            for part in components(obj):
                if min(obj.data.vertices[i].co.z for i in part)<hip-.04:indices.update(part)
        assert indices,(scene.name,obj.name)
        for i in indices:
            v=obj.data.vertices[i];side='Left' if v.co.x>=0 else 'Right'
            v.co=move_point(v.co,old[side],new[side])
        if 'review_hem_z' in obj:obj['review_hem_z']=map_height(obj['review_hem_z'],old['Left'],new['Left'])
        obj.data.update();bind_region(obj,rig,list(indices),height);garments.append((obj,indices))
    return garments

def make_legs(body,rig,new,height,spec,garments):
    scale=height/1.88;hip=new['Left'][0].z;knee=new['Left'][1].z;ankle=new['Left'][2].z
    limit=.28*spec.get('width',1)
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<hip-.02 and abs(v.co.x)<limit],context='VERTS')
    bm.to_mesh(body.data);bm.free();body.data.update()
    skin=body.data.materials[0];parts=[body]
    radii_factor=(FEMALE_RADIUS_FACTOR if spec.get('sex')=='female' or spec.get('approved') else MALE_RADIUS_FACTOR)*scale*spec.get('width',1)**.35
    shin=knee-ankle;thigh=hip-knee
    profile=[(ankle-.018*scale,.040,.043),(ankle+.035*scale,.043,.047),
             (ankle+shin*.35,.058,.060),(ankle+shin*.62,*CALF_RADII),
             (knee-.060*scale,.065,.062),(knee-.020*scale,.058,.056),
             (knee,.058,.056),(knee+.025*scale,.061,.059),
             (knee+thigh*.30,.077,.076),(knee+thigh*.65,.085,.075),(hip-.035*scale,.090,.075)]
    for side,sign in [('Left',1),('Right',-1)]:
        vertices=[];n=12
        for z,rx,ry in sorted(profile):
            center=axis_at(new[side],z);rx*=radii_factor;ry*=radii_factor
            center.y+=.006*scale*max(0,1-abs(z-(ankle+shin*.62))/(shin*.35))
            for obj,indices in garments:
                bounds=section(obj,z,sign,indices)
                if bounds:
                    xmin,xmax,ymin,ymax=bounds
                    # Deja margen bajo la tela, incluso entre los vértices del contorno poligonal.
                    rx=min(rx,max(.014*scale,.80*min(center.x-xmin,xmax-center.x)-GARMENT_CLEARANCE*scale))
                    ry=min(ry,max(.014*scale,.80*min(center.y-ymin,ymax-center.y)-GARMENT_CLEARANCE*scale))
            vertices.extend((center.x+rx*math.cos(2*math.pi*i/n),center.y+ry*math.sin(2*math.pi*i/n),z) for i in range(n))
        faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
        faces+=[tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
        leg=P.mesh('LegR3',vertices,faces,skin);bind_region(leg,rig,list(range(len(vertices))),height);parts.append(leg)
    return P.join(body.name,parts)

def main():
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/elenco_r2.blend'))
    catalog={s['id']:s for s in json.loads((BASE/'cast_catalog.json').read_text(encoding='utf-8'))}
    scenes=[s for s in bpy.data.scenes if s.name.startswith('RigReview_') and s.name!='RigReview_Gallery']
    records=[];changes=[]
    muscle=next(s for s in scenes if s.name=='RigReview_'+PRESERVE_ID);approved_fingerprint=fingerprint(muscle)
    for scene in scenes:
        identifier=scene.name.removeprefix('RigReview_');spec=catalog[identifier];bpy.context.window.scene=scene
        rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.hide_set(False)
        meshes=[o for o in scene.objects if o.type=='MESH'];height=max(v.co.z for o in meshes for v in o.data.vertices)
        if identifier!=PRESERVE_ID:
            body=next(o for o in meshes if '_Body' in o.name);shoes=next(o for o in meshes if '_Shoes' in o.name)
            old,new=adjust_joints(rig,shoes,height)
            garments=warp_clothing(scene,rig,old,new,height,spec)
            make_legs(body,rig,new,height,spec,garments)
            changes.append({'id':identifier,'old_knee':list(old['Left'][1]),'new_knee':list(new['Left'][1]),
                            'old_ankle':list(old['Left'][2]),'new_ankle':list(new['Left'][2])})
        scene.name='LegsR3_'+identifier
        meshes=[o for o in scene.objects if o.type=='MESH']
        records.append({'id':identifier,'label':spec['label'],'group':spec['group'],'height_m':height,
            'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'meshes':len(meshes),
            'bones':len(rig.data.bones),'approved_source':identifier==PRESERVE_ID})
        rig.hide_set(True);print('LEGS_R3',identifier,flush=True)
    assert fingerprint(muscle)==approved_fingerprint,'Se alteró el Toñito aprobado'
    bpy.data.scenes['RigReview_Gallery'].name='LegsR3_Gallery'
    bpy.context.window.scene=bpy.data.scenes['LegsR3_Gallery']
    (BASE/'manifest.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'characters':sorted(records,key=lambda x:x['id']),
        'unity_avatars_verified':False},indent=2,ensure_ascii=False),encoding='utf-8')
    (BASE/'changes.json').write_text(json.dumps({'modified_count':len(changes),'preserved_muscle_fingerprint':approved_fingerprint,'characters':changes},indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Alarma_CastLegs_R3.blend'))
    print('CAST_LEGS_R3_SUCCESS',len(changes),flush=True)

if __name__=='__main__':main()
