"""Limpia únicamente mallas sin usuarios y comprime el .blend; conserva las piezas usadas."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;FILE=BASE/'Villa_Alarma_Jardineras_Pasto_R4.blend'
bpy.ops.wm.open_mainfile(filepath=str(FILE))
root=bpy.data.objects['VillaAlarma_4000m']
def state():
    unique={o.data for o in root.children_recursive if o.type=='MESH'};result={}
    for data in unique:
        h=hashlib.sha256();h.update(str([tuple(v.co) for v in data.vertices]).encode())
        h.update(str([(tuple(p.vertices),p.material_index) for p in data.polygons]).encode())
        result[data.name]=h.hexdigest()
    return result
before=state();unused=[data for data in bpy.data.meshes if data.users-int(data.use_fake_user)==0]
for data in unused:data.use_fake_user=False;bpy.data.meshes.remove(data)
assert state()==before,'Se alteró una malla usada'
scene=bpy.data.scenes['CityR4_PlanterDetail'];bpy.context.window.scene=scene
hero=bpy.data.objects['R2_Hero_Minimarket'];p=hero.matrix_world@Vector((-4.44,-6,.70));target=p+Vector((0,0,.15))
scene.camera.location=p+Vector((3,-7,2.8));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.frame_set(49)
report=json.loads((BASE/'city_update.json').read_text())
used_meshes={obj.data for obj in root.children_recursive if obj.type=='MESH'}
counts={data:sum(len(p.vertices)-2 for p in data.polygons) for data in used_meshes}
report['unused_meshes_removed']=len(unused);report['used_meshes_unchanged_after_cleanup']=True
report['instantiated_rest_triangles']=sum(counts[o.data] for o in root.children_recursive if o.type=='MESH')
(BASE/'city_update.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(FILE),compress=True)
scene.render.filepath=str(BASE/'renders/Ciudad_Jardineras_R4.png');bpy.ops.render.render(write_still=True)
print('CITY_REVIEW_FINALIZED',json.dumps(report),flush=True)
