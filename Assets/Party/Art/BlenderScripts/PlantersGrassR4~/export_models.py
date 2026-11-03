"""FBX para Unity: geometría de reposo, materiales por cara y RGBA de viento sin conversión."""
import bpy,json,contextlib,io,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;OUT=BASE/'export';(OUT/'kit').mkdir(parents=True,exist_ok=True)


class FilterLog(io.TextIOBase):
    def __init__(self):self.pending='';self.notices=0
    def write(self,value):
        self.pending+=value
        while '\n' in self.pending:
            line,self.pending=self.pending.split('\n',1)
            if line.startswith('WARNING: Cannot register a valid material index'):self.notices+=1
            else:print(line,file=sys.__stdout__)
        return len(value)


def export(path,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
        if obj.type=='MESH':assert tuple(s.material for s in obj.material_slots)==tuple(obj.data.materials),obj.name
    bpy.context.view_layer.objects.active=objects[0];log=FilterLog()
    with contextlib.redirect_stdout(log):
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},
            use_mesh_modifiers=False,global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Z',axis_up='Y',bake_space_transform=False,bake_anim=False,colors_type='LINEAR',
            add_leaf_bones=False,mesh_smooth_type='FACE',use_custom_props=True)
    if log.notices:print('SHARED_INSTANCE_NOTICES',log.notices,'material slots checked')


bpy.ops.wm.open_mainfile(filepath=str(BASE/'Macetas_Pasto_Viento_R4.blend'))
scene=bpy.data.scenes.new('PlantR4_Export');bpy.context.window.scene=scene
catalog=json.loads((BASE/'asset_catalog.json').read_text())
for entry in catalog:
    obj=bpy.data.objects.new(entry['mesh'],bpy.data.meshes[entry['mesh']]);scene.collection.objects.link(obj)
    export(OUT/'kit'/(entry['mesh']+'.fbx'),[obj]);bpy.data.objects.remove(obj,do_unlink=True)
for round_pot in [False,True]:
    label='Maceta_Salvia_R4' if round_pot else 'Jardinera_Florida_R4'
    root=bpy.data.objects.new(label,None);scene.collection.objects.link(root);objects=[root]
    pot=bpy.data.objects.new('Pot',bpy.data.meshes['PlantR4_Pot_Round' if round_pot else 'PlantR4_Pot_Rectangular'])
    scene.collection.objects.link(pot);pot.parent=root;objects.append(pot)
    for i in range(1 if round_pot else 4):
        variant=0 if round_pot else [1,2,3,1][i]
        obj=bpy.data.objects.new('Foliage',bpy.data.meshes[f'PlantR4_Shrub_{variant}_LOD0']);scene.collection.objects.link(obj)
        obj.parent=root;obj.location=(0,0,.56) if round_pot else (-1.01+i*.68,0,.53);objects.append(obj)
    export(OUT/'kit'/(label+'.fbx'),objects)
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
print('PLANT_KIT_EXPORTED',len(catalog)+2,flush=True)
if '--kit-only' in sys.argv:raise SystemExit(0)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Jardineras_Pasto_R4.blend'))
bpy.context.window.scene=bpy.data.scenes['CityR4_StreetLevel'];root=bpy.data.objects['VillaAlarma_4000m']
export(OUT/'Villa_Alarma_Jardineras_Pasto_R4.fbx',[root]+list(root.children_recursive))
print('CITY_PLANTS_GRASS_FBX_READY',flush=True)
