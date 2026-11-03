"""Actualiza la revisiÃ³n animada del mapa de 4 km sin tocar edificios, Ã¡rboles ni mÃ¡scaras de viento."""
import bpy,json,sys,math,hashlib,array
from pathlib import Path
from mathutils import Matrix,Vector
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from fbx_utils import export
from sources import previous_revision;old=previous_revision();bpy.ops.wm.open_mainfile(filepath=str(old/'Villa_Alarma_Ciudad_Viva_R5.blend'))
scene=bpy.data.scenes['CityR5_LifeStreet'];bpy.context.window.scene=scene;root=bpy.data.objects['VillaAlarma_4000m']
old_collection=bpy.data.collections.get('LifeR5_AnimatedResidents')
removed_residents=len([o for o in old_collection.all_objects if o.type=='ARMATURE']) if old_collection else 0
if old_collection:
    for obj in list(old_collection.all_objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(old_collection)
case=bpy.data.objects.get('InteriorR5_MallJewelry_JewelryCase_3');assert case and tuple(case.location[:2])==(0,2.5);bpy.data.objects.remove(case,do_unlink=True)
doors=[o for o in root.children_recursive if o.get('MapRole')=='door' and any(o.name.startswith('R2_Hero_'+s+'_Door') for s in ['Minimarket','MallJewelry','Restaurant'])]
def fingerprint(objects):
    value=hashlib.sha256();cache={}
    for obj in sorted(objects,key=lambda o:o.name):
        value.update(obj.name.encode());value.update(array.array('f',[v for row in obj.matrix_world for v in row]).tobytes())
        if obj.type!='MESH':continue
        data=obj.data
        if data not in cache:
            h=hashlib.sha256();coords=array.array('f',[0])*(len(data.vertices)*3);data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
            loops=array.array('I',[0])*len(data.loops);data.loops.foreach_get('vertex_index',loops);h.update(loops.tobytes())
            indices=array.array('I',[0])*len(data.polygons);data.polygons.foreach_get('material_index',indices);h.update(indices.tobytes())
            for mat in data.materials:h.update(mat.name.encode() if mat else b'None')
            attr=data.color_attributes.get('WindMask')
            if attr:
                colors=array.array('f',[0])*(len(attr.data)*4);attr.data.foreach_get('color',colors);h.update(colors.tobytes())
            cache[data]=h.digest()
        value.update(cache[data])
    return value.hexdigest()
others=[o for o in root.children_recursive if o not in doors];before=fingerprint(others)
with bpy.data.libraries.load(str(B/'Ciudad_Compras_R6.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith(('R6_Resident_','R6_Cashier_','R6_Product_','R6_Money_','R6_Receipt_','R6_ShelfStock_','R6_FoodDisplay_','Door_'))]
loaded={o.name:o for o in dst.objects};catalog=json.loads((B/'preview_catalog.json').read_text());district=json.loads((B/'district.json').read_text())
collection=bpy.data.collections.new('LifeR6_AnimatedShopping')
for s in bpy.data.scenes:
    if s.name.startswith('CityR5_'):s.collection.children.link(collection);s.frame_start=1;s.frame_end=2160;s.render.fps=24
groups={}
for shop in district['shops']:
    hero=bpy.data.objects['R2_Hero_'+shop['id']];group=bpy.data.objects.new('R6_World_'+shop['id'],None);collection.objects.link(group);group.matrix_world=hero.matrix_world@Matrix.Translation(Vector((-shop['center'][0],0,0)));groups[shop['id']]=group
for obj in loaded.values():
    if obj.name.startswith('Door_'):continue
    if obj.name.startswith('R6_FoodDisplay_'):
        scene.collection.objects.link(obj);obj.parent=bpy.data.objects['R2_Hero_Restaurant'];continue
    collection.objects.link(obj)
for entry in catalog:
    actor=loaded[entry['root']];actor.parent=groups[entry['shop']]
    if not entry.get('cashier'):
        action=actor.animation_data.action;curves={c.array_index:c for c in action.fcurves if c.data_path=='location'}
        for key in curves[2].keyframe_points:
            y=curves[1].evaluate(key.co.x);key.co.y=.16*min(1,max(0,(y+5.4)/.6))
        for role in ['product','cash','receipt']:loaded[entry[role]].parent=groups[entry['shop']]
for obj in loaded.values():
    if obj.name.startswith('R6_ShelfStock_'):
        shop=next(s for s in district['shops'] if obj.name.startswith('R6_ShelfStock_'+s['id']));obj.parent=groups[shop['id']]
for door in doors:
    shop=next(s for s in district['shops'] if door.name.startswith('R2_Hero_'+s['id']+'_Door'))
    local=bpy.data.objects['R2_Hero_'+shop['id']].matrix_world.inverted()@door.matrix_world.translation
    source=loaded['Door_'+shop['id']+('_L' if local.x<0 else '_R')];door.animation_data_clear();door.animation_data_create().action=source.animation_data.action
for obj in list(loaded.values()):
    if obj.name.startswith('Door_'):bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update();assert fingerprint(others)==before,'Se alterÃ³ geometrÃ­a protegida del mapa'
scene.name='CityR6_ShoppingStreet';scene.frame_set(925);origin=bpy.data.objects['R2_Hero_Minimarket'].matrix_world.translation
scene.camera.location=origin+Vector((12,-20,13));target=origin+Vector((0,-4,1));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
report={'world_size_m':[4000,4000],'previous_residents_replaced':removed_residents,'animated_residents':27,'shopping_businesses':3,'removed_blocking_jewelry_case':1,'added_pickup_displays':3,'preserved_geometry_and_wind_sha256':before,'protected_object_count':len(others),'geometry_and_wind_preserved':True,'preview_only_not_unity_play':True}
(B/'map_validation.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(B/'Villa_Alarma_Compras_R6.blend'),compress=True)
scene.frame_set(1);export(B/'export/Map/Villa_Alarma_Ciudad_R6.fbx',[root]+list(root.children_recursive));print('MAP_R6_UPDATED',json.dumps(report),flush=True)
