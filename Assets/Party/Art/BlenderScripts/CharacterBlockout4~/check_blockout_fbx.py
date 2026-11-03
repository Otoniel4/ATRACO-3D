"""Verifica el FBX real en un proceso Blender nuevo, sin depender del .blend."""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector

base=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(base/'export'/'character.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
expected={'Body','Jacket','Top','Pants','Shoes','Hair','Earrings'}
assert {o.name for o in meshes}==expected, [o.name for o in meshes]
assert len(rigs)==1
rig=rigs[0]
required={'Hips','Spine','Chest','Neck','Head'}
for side in ['Left','Right']:
    required.update(side+n for n in ['Shoulder','UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot','Toes'])
assert set(rig.data.bones.keys())==required
assert not any(o.type in {'CAMERA','LIGHT'} for o in bpy.context.scene.objects)

def coordinates(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=evaluated.to_mesh()
    result=[evaluated.matrix_world@v.co for v in data.vertices]
    evaluated.to_mesh_clear()
    return result

rest={o.name:coordinates(o) for o in meshes}
initial_pose={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
points=[p for values in rest.values() for p in values]
height=max(p.z for p in points)-min(p.z for p in points)
assert abs(height-1.65)<.002, height
assert abs(min(p.z for p in points))<.002
checks={}
for obj in meshes:
    unweighted=sum(sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in required)<1e-6 for v in obj.data.vertices)
    assert unweighted==0, (obj.name,unweighted)
    assert any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers)
    checks[obj.name]={'vertices':len(obj.data.vertices),'unweighted_vertices':unweighted}

for name,angle in [('LeftUpperArm',20),('LeftLowerArm',30),('LeftUpperLeg',12),('LeftLowerLeg',35)]:
    bone=rig.pose.bones[name];bone.rotation_mode='XYZ';bone.rotation_euler.x=math.radians(angle)
bpy.context.view_layer.update()
for obj in meshes:
    posed=coordinates(obj)
    assert len(posed)==len(rest[obj.name])
    movements=[(a-b).length for a,b in zip(posed,rest[obj.name])]
    assert all(math.isfinite(p) for p in movements)
    checks[obj.name]['test_pose_max_displacement_m']=max(movements)
    assert max(movements)<.7
assert checks['Body']['test_pose_max_displacement_m']>.01

for bone in rig.pose.bones:bone.matrix_basis=initial_pose[bone.name]
bpy.context.view_layer.update()
for obj in meshes:
    error=max((a-b).length for a,b in zip(coordinates(obj),rest[obj.name]))
    assert error<1e-6, (obj.name,error)
    checks[obj.name]['rest_recovery_error_m']=error

report={'blender_version':bpy.app.version_string,'fbx_import_passed':True,
        'height_m':height,'ground_z':min(p.z for p in points),'meshes':checks,
        'bone_count':len(required),'bones':sorted(required),'cameras_or_lights':False,
        'pose_and_rest_recovery_passed':True,'unity_avatar_verified':False}
(base/'export'/'roundtrip.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FBX_ROUNDTRIP_SUCCESS',height,len(meshes),len(required),flush=True)

# Verificar además el archivo editable que se entrega al artista.
bpy.ops.wm.open_mainfile(filepath=str(base/'character.blend'))
scene=bpy.data.scenes['Character_Blockout_4x']
bpy.context.window.scene=scene
objects={name:scene.objects[name] for name in expected}
for obj in objects.values():
    assert obj.location.length<1e-7 and obj.rotation_euler.to_matrix().is_identity
    assert (obj.scale-Vector((1,1,1))).length<1e-7
body=objects['Body'];bm=bmesh.new();bm.from_mesh(body.data)
assert all(len(f.verts)==4 for f in bm.faces)
assert all(e.is_manifold for e in bm.edges)
assert bm.calc_volume(signed=True)>0
body_faces=len(bm.faces);bm.free()
assert any(m.type=='MIRROR' and m.use_axis[0] for m in body.modifiers)
graph=scene.objects['SOURCE_SkinGraph']
assert {'MIRROR','SKIN','SUBSURF'}<={m.type for m in graph.modifiers}
refs=[scene.objects['REF_'+v] for v in ['front','side','back']]
assert all(o.type=='EMPTY' and o.empty_display_type=='IMAGE' and o.data.packed_file for o in refs)
report['editable_blend']={'checked':True,'body_closed_all_quads':True,'body_faces':body_faces,
    'origins_zero_scale_one_rotation_zero':True,'skin_graph_and_mirror_present':True,
    'packed_reference_empties':3}
(base/'export'/'roundtrip.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BLEND_SOURCE_SUCCESS',body_faces,flush=True)
