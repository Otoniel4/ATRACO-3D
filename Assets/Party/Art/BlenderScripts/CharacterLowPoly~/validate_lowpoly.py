"""Comprueba la cabeza low poly, el FBX real y el vínculo rígido con Head."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'character_lowpoly.blend'))
scene=bpy.data.scenes['Female_LowPoly'];bpy.context.window.scene=scene
roles=['LP_Body','LP_Jacket','LP_Top','LP_Pants','LP_Shoes','LP_Earrings','LP_Head','LP_Face','LP_Hair']
parts={n:scene.objects[n] for n in roles}
geometry={}
for name in ['LP_Body','LP_Head','LP_Hair']:
    bm=bmesh.new();bm.from_mesh(parts[name].data)
    assert all(e.is_manifold for e in bm.edges),name
    assert bm.calc_volume(signed=True)>0,name
    geometry[name]={'faces':len(bm.faces),'closed':True};bm.free()
face=parts['LP_Face']
ink_faces=[p for p in face.data.polygons if 'Ink' in face.data.materials[p.material_index].name]
assert ink_faces and all(p.normal.y<-.99 for p in ink_faces)
rig=scene.objects['LP_Armature']
for name in ['LP_Head','LP_Face','LP_Hair','LP_Earrings']:
    obj=parts[name];group=obj.vertex_groups['Head'].index
    assert all(len(v.groups)==1 and v.groups[0].group==group and abs(v.groups[0].weight-1)<1e-7 for v in obj.data.vertices)
with bpy.data.libraries.load(str(BASE/'baseline'/'character.blend'),link=False) as (src,dst):dst.scenes=['Character_Blockout_4x']
baseline=dst.scenes[0]
old={o.name.split('.')[0]:o for o in baseline.objects}
unchanged={}
for role in ['Jacket','Top','Pants','Shoes']:
    a=old[role].data.vertices;b=parts['LP_'+role].data.vertices
    assert len(a)==len(b)
    error=max((x.co-y.co).length for x,y in zip(a,b));assert error<1e-7
    unchanged[role]=error

# Reimportar el FBX en un archivo vacío, sin usar el rig que generó el archivo.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'export'/'character_lowpoly.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert {o.name for o in meshes}==set(roles) and len(rigs)==1
assert not any(o.type in {'CAMERA','LIGHT'} for o in bpy.context.scene.objects)
rig=rigs[0];assert len(rig.data.bones)==21 and 'Head' in rig.data.bones
def coords(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
    result=[evaluated.matrix_world@v.co for v in data.vertices];evaluated.to_mesh_clear();return result
rest={o.name:coords(o) for o in meshes};all_points=[p for points in rest.values() for p in points]
height=max(p.z for p in all_points)-min(p.z for p in all_points)
assert abs(height-1.65)<.002 and abs(min(p.z for p in all_points))<.002
for obj in meshes:
    assert all(sum(g.weight for g in v.groups)>1e-6 for v in obj.data.vertices),obj.name
initial={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
bone=rig.pose.bones['Head'];bone.rotation_mode='XYZ';bone.rotation_euler.z=math.radians(25)
bpy.context.view_layer.update()
deform=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@rig.matrix_world.inverted()
rigid_errors={}
for obj in meshes:
    if obj.name in ['LP_Head','LP_Face','LP_Hair','LP_Earrings']:
        error=max((a-deform@b).length for a,b in zip(coords(obj),rest[obj.name]))
        assert error<1e-5,(obj.name,error);rigid_errors[obj.name]=error
for bone in rig.pose.bones:bone.matrix_basis=initial[bone.name]
bpy.context.view_layer.update()
for obj in meshes:assert max((a-b).length for a,b in zip(coords(obj),rest[obj.name]))<1e-6
report={'blender_version':bpy.app.version_string,'height_m':height,'mesh_count':len(meshes),
 'bone_count':21,'geometry':geometry,'eyes_and_mouth_face_outward':True,
 'clothing_max_position_change_m':unchanged,'head_turn_25deg_errors_m':rigid_errors,
 'vertices_without_weights':0,'pose_recovery_passed':True,'unity_avatar_verified':False}
(BASE/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('LOWPOLY_VALIDATION_SUCCESS',height,len(meshes))
