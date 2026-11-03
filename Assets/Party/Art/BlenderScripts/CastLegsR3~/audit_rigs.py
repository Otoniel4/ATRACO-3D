"""Comprobaciones de alineación, cadenas y cobertura del pantalón del elenco R2."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Alarma_CastLegs_R3.blend'))

def section(obj,z):
    points=[]
    for edge in obj.data.edges:
        a,b=(obj.matrix_world@obj.data.vertices[i].co for i in edge.vertices)
        if (a.z-z)*(b.z-z)<0:
            p=a.lerp(b,(z-a.z)/(b.z-a.z))
            if p.x>.001:points.append(p)
    if not points:return None
    low=min(v.x for v in points);high=max(v.x for v in points)
    return {'center_x':(low+high)/2,'xmin':low,'xmax':high,
            'ymin':min(v.y for v in points),'ymax':max(v.y for v in points)}

results=[]
for scene in bpy.data.scenes:
    if not scene.name.startswith('LegsR3_') or scene.name=='LegsR3_Gallery':continue
    bpy.context.window.scene=scene;identifier=scene.name.removeprefix('LegsR3_')
    rig=next(o for o in scene.objects if o.type=='ARMATURE');meshes=[o for o in scene.objects if o.type=='MESH']
    height=max(v.co.z for obj in meshes for v in obj.data.vertices)
    error=0;symmetry=0;axis_error=0;crossed=0;negative_scale=False;misassigned_garment_vertices=0
    for prefix in ['Left','Right']:
        for a,b in [('UpperLeg','LowerLeg'),('LowerLeg','Foot'),('Foot','Toes')]:
            pa,pb=rig.data.bones[prefix+a],rig.data.bones[prefix+b]
            assert pb.parent==pa
            error=max(error,(pa.tail_local-pb.head_local).length)
        for role in ['UpperLeg','LowerLeg']:
            bone=rig.data.bones[prefix+role]
            axis=bone.matrix_local.to_3x3().col[1].normalized()
            axis_error=max(axis_error,(axis-(bone.tail_local-bone.head_local).normalized()).length)
    for role in ['UpperLeg','LowerLeg','Foot','Toes']:
        l,r=rig.data.bones['Left'+role],rig.data.bones['Right'+role]
        for a,b in [(l.head_local,r.head_local),(l.tail_local,r.tail_local)]:
            symmetry=max(symmetry,(a-Vector((-b.x,b.y,b.z))).length)
    for obj in meshes:
        negative_scale|=obj.matrix_world.to_3x3().determinant()<=0
        if not any(s in obj.name for s in ['Body','Outfit','Pants','Shoes']):continue
        for v in obj.data.vertices:
            if v.co.z>height*.4 or abs(v.co.x)<.045:continue
            wrong='Right' if v.co.x>0 else 'Left'
            if sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name.startswith(wrong))>.02:crossed+=1
    for obj in meshes:
        if not any(n in obj.name for n in ['_Pants','_Outfit']):continue
        for v in obj.data.vertices:
            if v.co.z>height*.40:continue
            forbidden=sum(g.weight for g in v.groups if any(n in obj.vertex_groups[g.group].name for n in ['Arm','Hand','Shoulder','Head','Neck','Chest']))
            if forbidden>.001:misassigned_garment_vertices+=1
    assert misassigned_garment_vertices==0,(identifier,misassigned_garment_vertices)
    if identifier=='NPC02_Denim':
        for obj in meshes:
            if any(n in obj.name for n in ['_Jacket','_Top']):
                assert not any(g.weight>.001 for v in obj.data.vertices for g in v.groups if any(n in obj.vertex_groups[g.group].name for n in ['Leg','Foot','Toes','Head'])),obj.name
    assert error<1e-6 and symmetry<1e-6 and axis_error<1e-5 and not negative_scale and crossed==0,identifier
    lower=rig.data.bones['LeftLowerLeg'];upper=rig.data.bones['LeftUpperLeg']
    checks=[]
    for fraction in [.10,.18,.25,.30,.34,.38]:
        z=height*fraction;bone=lower if z<lower.head_local.z else upper
        a,b=bone.head_local,bone.tail_local;center=a.lerp(b,(z-a.z)/(b.z-a.z))
        sections={}
        for obj in meshes:
            if any(n in obj.name for n in ['Body','Outfit','Pants','Shoes']):
                cut=section(obj,z)
                if cut:cut['bone_offset_x']=cut['center_x']-center.x;sections[obj.name]=cut
        checks.append({'z':z,'bone_x':center.x,'meshes':sections})
    hem_check=None
    if identifier in {'NPC03_Tourist','NPC10_Cardigan','Player04_Muscle'}:
        body=next(o for o in meshes if '_Body' in o.name);outfit=next(o for o in meshes if '_Outfit' in o.name)
        hem=outfit['review_hem_z']
        skin=section(body,hem+.004);fabric=section(outfit,hem+.004)
        assert skin and fabric,identifier
        margins={'inner':skin['xmin']-fabric['xmin'],'outer':fabric['xmax']-skin['xmax'],
                 'front':skin['ymin']-fabric['ymin'],'back':fabric['ymax']-skin['ymax']}
        assert min(margins.values())>.002,(identifier,margins)
        center=upper.head_local.lerp(upper.tail_local,(hem+.004-upper.head_local.z)/(upper.tail_local.z-upper.head_local.z))
        offset=fabric['center_x']-center.x
        assert abs(offset)<.008,(identifier,offset)
        hem_check={'hem_z':hem,'cloth_offset_x':offset,'clearance_m':margins}
        if identifier=='Player04_Muscle':
            # También revisa la parte oculta del muslo, para evitar piel atravesando la tela.
            for z in [.65,.70,.75,.80,.85,.89]:
                inner,outer=section(body,z),section(outfit,z)
                assert inner and outer
                assert inner['xmin']>outer['xmin']+.002 and inner['xmax']<outer['xmax']-.002,(identifier,z,'lateral')
                assert inner['ymin']>outer['ymin']+.002 and inner['ymax']<outer['ymax']-.002,(identifier,z,'depth')
    expected_knee=(upper.head_local.z+lower.tail_local.z)/2-.002*height/1.88
    assert abs(lower.head_local.z-expected_knee)<.003,identifier
    results.append({'id':identifier,'bones':len(rig.data.bones),'chain_gap_m':error,'symmetry_error_m':symmetry,
                    'bone_axis_error':axis_error,'wrong_side_leg_weights':crossed,'hem_check':hem_check,
                    'misassigned_lower_garment_vertices':misassigned_garment_vertices,
                    'knee':list(lower.head_local),'sections':checks})
assert len(results)==18
(BASE/'audit_after.json').write_text(json.dumps({'audited_count':18,'characters':results,
    'unity_humanoid_verified':False,'diagnostics_only_no_animation_clips':True},indent=2),encoding='utf-8')
for result in results:
    print('RIG_AUDIT',result['id'],'gap',round(result['chain_gap_m'],6),'hem',result['hem_check'])
print('RIG_AUDIT_SUCCESS',18,flush=True)
