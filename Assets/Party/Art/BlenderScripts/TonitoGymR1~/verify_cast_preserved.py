"""Comprueba que el archivo integrado conserva los otros 17 actores exactamente."""
import bpy,json,hashlib,struct
from pathlib import Path
BASE=Path(__file__).resolve().parent

def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    result={}
    for scene in bpy.data.scenes:
        if scene.name.startswith('Cast_') and scene.name!='Cast_Gallery' and not scene.name.startswith('Cast_Source_Approved') and 'Muscle' not in scene.name:
            data=[]
            for obj in scene.objects:
                if obj.type!='MESH':continue
                digest=hashlib.sha256()
                for row in obj.matrix_world:
                    digest.update(struct.pack('4d',*row))
                for v in obj.data.vertices:digest.update(struct.pack('3d',*v.co))
                for p in obj.data.polygons:
                    digest.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
                    digest.update(struct.pack('I',p.material_index))
                for m in obj.data.materials:
                    node=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
                    if node:digest.update(struct.pack('4d',*node.inputs['Base Color'].default_value))
                data.append(digest.hexdigest())
            result[scene.name]=sorted(data)
    return result

before=inspect(BASE/'baseline/elenco_anterior.blend')
after=inspect(BASE/'Alarma_Tonito_Gym_R1.blend')
assert len(before)==17 and before==after,'Se modificó otro actor del elenco'
gallery=bpy.data.scenes['Cast_Gallery']
displays=[o for o in gallery.objects if o.instance_collection]
assert len(displays)==18
muscle=next(o for o in displays if o.name.startswith('Player04_Muscle_Display'))
assert muscle.instance_collection.name.startswith('Player04_Muscle_Gym_R1_Actor')
(BASE/'preservation.json').write_text(json.dumps({'other_actors_unchanged':17,'gallery_actors':18,'updated_instance':muscle.name,'mesh_hashes':after},indent=2),encoding='utf-8')
print('CAST_PRESERVATION_SUCCESS',17,flush=True)
