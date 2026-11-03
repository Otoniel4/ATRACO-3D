"""Exportación estática: mapa ensamblado, 64 sectores locales y kit reutilizable."""
import bpy,json,sys,io,contextlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
scene=bpy.data.scenes['Map4Km_Overview'];bpy.context.window.scene=scene
world=bpy.data.objects['VillaAlarma_4000m'];sectors=sorted(world.children,key=lambda o:o.name)
OUT=BASE/'export';(OUT/'sectors').mkdir(parents=True,exist_ok=True);(OUT/'kit').mkdir(exist_ok=True)
# Elimina ranuras sin usar de cada malla compartida. Mantiene exactamente el color por cara.
compact={o.data for o in world.children_recursive if o.type=='MESH'}
compact.update(m for m in bpy.data.meshes if m.name in ['Road_8m','Road_14m','Road_22m','Sidewalk_4m','Wall_4m','Corner_1m','Window_2m','Door_Frame_1m','Door_Leaf_1m','Roof_4m','Crosswalk_4m'])
for mesh in compact:
    before=[p.material_index for p in mesh.polygons];used=sorted(set(before))
    materials=[mesh.materials[i] for i in used];mapping={old:new for new,old in enumerate(used)}
    mesh.materials.clear()
    for material in materials:mesh.materials.append(material)
    for face,index in zip(mesh.polygons,before):face.material_index=mapping[index]
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))

class ExportLog(io.TextIOBase):
    """Cuenta el aviso repetido de instancias del exportador 4.5 tras validar sus ranuras."""
    def __init__(self):self.pending='';self.repeated=0
    def write(self,value):
        self.pending+=value
        while '\n' in self.pending:
            line,self.pending=self.pending.split('\n',1)
            if line.startswith('WARNING: Cannot register a valid material index'):self.repeated+=1
            else:sys.__stdout__.write(line+'\n')
        return len(value)

def export(path,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.hide_set(False);obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    for obj in objects:
        if obj.type!='MESH':continue
        assert tuple(s.material for s in obj.material_slots)==tuple(obj.data.materials),obj.name
        assert all(f.material_index<len(obj.material_slots) for f in obj.data.polygons),obj.name
    log=ExportLog()
    with contextlib.redirect_stdout(log):
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},
            global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            bake_space_transform=False,bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE',use_custom_props=True)
    if log.repeated:print('SHARED_MESH_NOTICES',log.repeated,'material slots audited; face colors checked by verify_fbx.py',flush=True)

records=[]
for sector in sectors:
    original=sector.location.copy();sector.parent=None;sector.location=(0,0,0);bpy.context.view_layer.update()
    parts=[sector]+list(sector.children_recursive)
    export(OUT/'sectors'/(sector.name+'.fbx'),parts)
    sector.parent=world;sector.location=original;bpy.context.view_layer.update()
    records.append({'name':sector.name,'fbx':'sectors/'+sector.name+'.fbx','blender_origin':list(original),
                    'unity_origin_convention':[original.x,original.z,-original.y]})
    print('SECTOR_EXPORTED',sector.name,flush=True)
export(OUT/'Villa_Alarma_4km.fbx',[world]+list(world.children_recursive))
print('ASSEMBLED_MAP_EXPORTED',flush=True)
# Subconjunto propio compatible con Blender 4.5; la biblioteca original del proyecto no se modifica.
sources={c for c in bpy.data.collections if c.name.startswith('ASSET_')}
bpy.data.libraries.write(str(BASE/'baseline/own_art_subset_45.blend'),sources,fake_user=True,compress=True)
kit_scene=bpy.data.scenes.new('KitExport');bpy.context.window.scene=kit_scene
names=['House_'+str(i) for i in range(6)]+['Apartment_'+str(i) for i in range(6)]+['Shop_'+str(i) for i in range(6)]
names += ['Tower_'+str(i) for i in range(3)]+['Warehouse_'+str(i) for i in range(3)]
names += ['Tree_'+str(i) for i in range(4)]+['ForestTree_'+str(i) for i in range(4)]
names += ['Palm','Bench','Bin','Lamp','Signal','Stop','Recycle','Mailbox','Planter','Bollard','FoodStand','DuckFountain',
          'Car_Sedan','Car_Hatchback','Car_Taxi','Car_Police']
names += ['Road_8m','Road_14m','Road_22m','Sidewalk_4m','Wall_4m','Corner_1m','Window_2m','Door_Frame_1m','Door_Leaf_1m','Roof_4m','Crosswalk_4m']
kit=[]
for name in names:
    mesh=bpy.data.meshes.get(name)
    if mesh is None:continue
    obj=bpy.data.objects.new('Kit_'+name,mesh);kit_scene.collection.objects.link(obj)
    export(OUT/'kit'/(name+'.fbx'),[obj]);kit.append(name);bpy.data.objects.remove(obj,do_unlink=True)
(OUT/'sector_layout.json').write_text(json.dumps({'size_m':4000,'sector_size_m':500,'sectors':records,
    'assembled_map':'Villa_Alarma_4km.fbx','kit':kit,
    'coordinates':'Blender X,Y,Z; export -Z forward, Y up. Assembled FBX contains all placement transforms.'},indent=2),encoding='utf-8')
print('MAP_EXPORT_SUCCESS',len(records),'SECTORS',len(kit),'KIT_ASSETS',flush=True)
