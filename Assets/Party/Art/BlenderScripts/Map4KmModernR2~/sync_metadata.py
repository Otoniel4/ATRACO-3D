"""Actualiza el catálogo y las huellas con los límites finales, sin cambiar la geometría."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from layout_math import rect
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
bpy.context.window.scene=bpy.data.scenes['CityR2_Overview'];bpy.context.view_layer.update()
root=bpy.data.objects['VillaAlarma_4000m'];footprints=[]
for obj in root.children_recursive:
    if obj.type!='MESH' or obj.get('MapRole') not in ['building','hero_shell','gallery_business']:continue
    vertices=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    roof=bpy.data.objects.get(obj.name+'_ModernRoof')
    if roof:vertices.extend(roof.matrix_world@Vector(p) for p in roof.bound_box)
    footprints.append({'object':obj.name,'asset':obj.get('R2Asset',obj.data.name),'position':list(obj.matrix_world.translation),
        'polygon':rect(min(v.x for v in vertices),min(v.y for v in vertices),max(v.x for v in vertices),max(v.y for v in vertices))})
(BASE/'building_footprints_r2.json').write_text(json.dumps(footprints),encoding='utf-8')
catalog=json.loads((BASE/'asset_catalog.json').read_text(encoding='utf-8'))
for record in catalog:
    mesh=bpy.data.meshes[record['mesh']];record['triangles']=sum(len(p.vertices)-2 for p in mesh.polygons)
(BASE/'asset_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
print('R2_FINAL_METADATA_SYNCED',len(footprints),len(catalog))
