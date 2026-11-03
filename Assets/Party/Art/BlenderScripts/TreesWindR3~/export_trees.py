"""FBX de reposo con WindMask: el viento lo aporta Geometry Nodes en Blender y el shader en Unity."""
import bpy,json,io,contextlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
class ExportLog(io.TextIOBase):
    def __init__(self):self.pending='';self.count=0
    def write(self,value):
        self.pending+=value
        while '\n' in self.pending:
            line,self.pending=self.pending.split('\n',1)
            if line.startswith('WARNING: Cannot register a valid material index'):self.count+=1
            else:print(line,file=__import__('sys').__stdout__)
        return len(value)
def export(path,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    for obj in objects:
        if obj.type=='MESH':assert tuple(s.material for s in obj.material_slots)==tuple(obj.data.materials),obj.name
    log=ExportLog()
    with contextlib.redirect_stdout(log):
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},
            use_mesh_modifiers=False,global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Z',axis_up='Y',bake_space_transform=False,bake_anim=False,colors_type='LINEAR',
            add_leaf_bones=False,mesh_smooth_type='FACE',use_custom_props=True)
    if log.count:print('SHARED_INSTANCE_NOTICES',log.count,'material layouts audited')

OUT=BASE/'export';(OUT/'trees').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Arboles_Viento_R3.blend'))
scene=bpy.data.scenes.new('TreeExport');bpy.context.window.scene=scene
catalog=json.loads((BASE/'catalog.json').read_text(encoding='utf-8'))
for species in catalog:
    for lod in species['lods']:
        obj=bpy.data.objects.new(lod['mesh'],bpy.data.meshes[lod['mesh']]);scene.collection.objects.link(obj)
        export(OUT/'trees'/(obj.name+'.fbx'),[obj]);bpy.data.objects.remove(obj,do_unlink=True)
print('TREE_FBX_EXPORTED',18,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Arboles_Viento_R3.blend'))
scene=bpy.data.scenes['CityR3_StreetLevel'];bpy.context.window.scene=scene;root=bpy.data.objects['VillaAlarma_4000m']
export(OUT/'Villa_Alarma_Arboles_Viento_R3.fbx',[root]+list(root.children_recursive))
print('CITY_WIND_FBX_EXPORTED',flush=True)
