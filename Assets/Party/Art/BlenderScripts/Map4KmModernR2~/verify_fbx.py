"""Prueba de ida y vuelta del mapa completo y dos sectores, sin abrir Unity."""
import bpy,json,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
def color_signature(obj):
    counts=Counter()
    for face in obj.data.polygons:
        material=obj.material_slots[face.material_index].material
        counts[material.name]+=len(face.vertices)-2
    return dict(counts)

# Compara asignación de color por pieza, incluso cuando varias instancias comparten malla.
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
root=bpy.data.objects['VillaAlarma_4000m'];cache={};expected={}
for obj in root.children_recursive:
    if obj.type!='MESH':continue
    key=obj.data.as_pointer()
    if key not in cache:cache[key]=color_signature(obj)
    expected[obj.name]=cache[key]
source_colors={}
for m in bpy.data.materials:
    if m.name.startswith('City4_') and m.use_nodes:
        shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        source_colors[m.name]=tuple(shader.inputs['Base Color'].default_value)
results=[]
for relative in ['Villa_Alarma_Modern_R2.fbx','sectors/Sector_00_00.fbx','sectors/Sector_04_04.fbx']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(BASE/'export'/relative))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert meshes and not any(o.type in {'CAMERA','LIGHT','ARMATURE'} for o in bpy.context.scene.objects)
    bpy.context.view_layer.update();lo=[float('inf')]*3;hi=[-float('inf')]*3
    for obj in meshes:
        for p in obj.bound_box:
            v=obj.matrix_world@Vector(p)
            for k in range(3):lo[k]=min(lo[k],v[k]);hi[k]=max(hi[k],v[k])
    size=[hi[k]-lo[k] for k in range(3)]
    if relative=='Villa_Alarma_Modern_R2.fbx':
        # La reimportación restaura Z vertical; la conversión FBX conserva Y arriba en destino.
        assert abs(size[0]-4000)<.02 and abs(size[1]-4000)<.02,(lo,hi)
        assert len(meshes)>22000,len(meshes)
        assert {o.name for o in meshes}==set(expected),'Piezas perdidas o duplicadas'
        imported_cache={}
        for obj in meshes:
            key=obj.data.as_pointer()
            if key not in imported_cache:imported_cache[key]=color_signature(obj)
            assert imported_cache[key]==expected[obj.name],('Colores por cara',obj.name)
        for material in bpy.data.materials:
            if material.name not in source_colors:continue
            shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            color=shader.inputs['Base Color'].default_value
            assert max(abs(color[i]-source_colors[material.name][i]) for i in range(3))<.005,material.name
    else:
        assert 499.9<=size[0]<700 and 499.9<=size[1]<700,(relative,size)
        assert max(abs(lo[0]),abs(lo[1]),abs(hi[0]),abs(hi[1]))<400,(relative,lo,hi)
    results.append({'file':relative,'mesh_objects':len(meshes),'minimum':lo,'maximum':hi,'size':size,'passed':True,
        'face_materials_verified':relative=='Villa_Alarma_Modern_R2.fbx'})
    print('FBX_VERIFIED',relative,len(meshes),flush=True)
(BASE/'fbx_validation.json').write_text(json.dumps({'blender':bpy.app.version_string,'files':results,'unity_verified':False},indent=2),encoding='utf-8')
print('MAP_FBX_VALIDATION_SUCCESS',flush=True)
