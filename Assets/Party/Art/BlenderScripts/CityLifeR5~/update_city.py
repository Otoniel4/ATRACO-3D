"""Interiores detallados y revisión animada en una copia del mapa. Conserva el resto mediante huellas binarias."""
import bpy,json,sys,math,hashlib,array
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from fbx_utils import export
from street_residents import add_street_residents
bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/City_Plants_R4.blend'))
for scene in bpy.data.scenes:
    if scene.name.startswith('CityR4_'):scene.name=scene.name.replace('CityR4_','CityR5_')
source_scene=bpy.data.scenes['CityR5_StreetLevel'];bpy.context.window.scene=source_scene
root=bpy.data.objects['VillaAlarma_4000m'];original=list(root.children_recursive)
placements=json.loads((BASE/'interior_placements.json').read_text());catalog=json.loads((BASE/'prop_catalog.json').read_text())
targets=[bpy.data.objects['R2_Hero_'+shop+'_Furniture'] for shop in placements]
doors=[bpy.data.objects.get('R2_Hero_Minimarket_Door'+suffix) for suffix in ['', '.001']]
# Las hojas se identifican por su raíz y el material compartido; no se presupone el sufijo de objeto.
doors=[o for o in original if o.get('MapRole')=='door' and o.name.startswith('R2_Hero_Minimarket_Door')]
assert len(doors)==2
excluded=set(targets+doors);others=[o for o in original if o not in excluded]
def fingerprint(objects):
    value=hashlib.sha256();cache={}
    for obj in sorted(objects,key=lambda o:o.name):
        value.update(obj.name.encode());value.update(array.array('f',[v for row in obj.matrix_world for v in row]).tobytes())
        if obj.type!='MESH':continue
        data=obj.data
        if data not in cache:
            h=hashlib.sha256();coords=array.array('f',[0])*(len(data.vertices)*3);data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
            loops=array.array('I',[0])*len(data.loops);data.loops.foreach_get('vertex_index',loops);h.update(loops.tobytes())
            materials=array.array('I',[0])*len(data.polygons);data.polygons.foreach_get('material_index',materials);h.update(materials.tobytes())
            for mat in data.materials:h.update(mat.name.encode() if mat else b'None')
            attr=data.color_attributes.get('WindMask')
            if attr:
                colors=array.array('f',[0])*(len(attr.data)*4);attr.data.foreach_get('color',colors);h.update(colors.tobytes())
            cache[data]=h.digest()
        value.update(cache[data])
    return value.hexdigest()
before=fingerprint(others)
with bpy.data.libraries.load(str(BASE/'Objetos_Locales_R5.blend'),link=False) as (src,dst):dst.meshes=[r['mesh'] for r in catalog]
retained=[]
def retain_rear(source,minimum):
    data=source.data;by_vertex={};remaining=set(range(len(data.polygons)));keep=[]
    for p in data.polygons:
        for v in p.vertices:by_vertex.setdefault(v,[]).append(p.index)
    while remaining:
        stack=[remaining.pop()];faces=[];vertices=set()
        while stack:
            i=stack.pop();p=data.polygons[i];faces.append(i);vertices.update(p.vertices)
            for v in p.vertices:
                for n in by_vertex[v]:
                    if n in remaining:remaining.remove(n);stack.append(n)
        center=sum(data.vertices[v].co.y for v in vertices)/len(vertices)
        if center>=minimum:keep.extend(faces)
    used=sorted({v for i in keep for v in data.polygons[i].vertices});lookup={v:i for i,v in enumerate(used)}
    mesh=bpy.data.meshes.new('Life5_Preserved_'+source.name);mesh.from_pydata([tuple(data.vertices[v].co) for v in used],[],[tuple(lookup[v] for v in data.polygons[i].vertices) for i in keep]);mesh.update()
    for mat in data.materials:mesh.materials.append(mat)
    for p,i in zip(mesh.polygons,keep):p.material_index=data.polygons[i].material_index
    obj=bpy.data.objects.new(mesh.name,mesh);source.users_collection[0].objects.link(obj);obj.parent=source.parent;obj.matrix_world=source.matrix_world.copy()
    retained.append({'source':source.name,'faces_kept':len(keep),'reason':'vault room' if minimum>2 else 'jail cells'})
for source in targets:
    if source.name=='R2_Hero_Bank_Furniture':retain_rear(source,2.6)
    if source.name=='R2_Hero_Police_Furniture':retain_rear(source,.6)
new_objects=0
for shop,items in placements.items():
    hero=bpy.data.objects['R2_Hero_'+shop]
    for index,item in enumerate(items):
        obj=bpy.data.objects.new('InteriorR5_'+shop+'_'+item['asset']+'_'+str(index),bpy.data.meshes['Life5_'+item['asset']])
        hero.users_collection[0].objects.link(obj);obj.parent=hero;obj.location=item['position_blender'];obj.rotation_euler.z=item['yaw'];obj['MapRole']='detailed_interior';new_objects+=1
for source in targets:bpy.data.objects.remove(source,do_unlink=True)
old_figures=[o for o in bpy.data.objects if o.get('NotForExport') and o.type=='MESH' and o.data.name.startswith('ScaleCitizen_')]
for obj in old_figures:bpy.data.objects.remove(obj,do_unlink=True)
with bpy.data.libraries.load(str(BASE/'Ciudad_Viva_Demo_R5.blend'),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n.startswith(('Resident_','LiveR5_'))]
actors_collection=bpy.data.collections.new('LifeR5_AnimatedResidents')
for scene in bpy.data.scenes:
    if scene.name.startswith('CityR5_'):scene.collection.children.link(actors_collection)
for obj in dst.objects:actors_collection.objects.link(obj)
traces=json.loads((BASE/'preview_traces.json').read_text());animation_catalog=json.loads((BASE/'animation_catalog.json').read_text())
origin=bpy.data.objects['R2_Hero_Minimarket'].matrix_world.translation.copy()
for index,actor in enumerate(animation_catalog):
    obj=bpy.data.objects['Resident_'+actor['id']];obj.animation_data_clear()
    for row in traces['actors'][index]:
        f=row['frame']
        if f%2!=1 and f!=576:continue
        x,y,_=row['position'];height=.16*min(1,max(0,(y+5.4)/.6))
        obj.location=(origin.x+x+18,origin.y+y,origin.z+height);obj.rotation_euler.z=row['yaw']
        obj.keyframe_insert(data_path='location',frame=f);obj.keyframe_insert(data_path='rotation_euler',frame=f)
for door in doors:
    left=(door.location.x<0) if door.parent==bpy.data.objects['R2_Hero_Minimarket'] else door.matrix_world.translation.x<origin.x
    # Los pivotes originales están en el sector, por lo que se decide por posición mundial.
    left=door.matrix_world.translation.x<origin.x;angle=0;until=0
    for f in range(1,577):
        t=f/24
        if any(math.hypot(rows[f-1]['position'][0]+18,rows[f-1]['position'][1]+5.12)<2.4 for rows in traces['actors']):until=t+1.2
        angle+=max(-2.44/24,min(2.44/24,(1.309 if t<until else 0)-angle));door.rotation_euler.z=(0 if left else math.pi)+(-angle if left else angle)
        door.keyframe_insert(data_path='rotation_euler',frame=f)
bpy.context.view_layer.update();assert fingerprint(others)==before,'Se alteró geometría ajena a los interiores y puertas previstas'
extra_residents=add_street_residents(actors_collection)
scene=bpy.data.scenes.new('CityR5_LifeStreet');scene.world=source_scene.world;scene.render.engine=source_scene.render.engine
for collection in source_scene.collection.children:scene.collection.children.link(collection)
scene.collection.objects.link(root)
for obj in source_scene.objects:
    if obj.type=='LIGHT' and obj.name not in scene.objects:scene.collection.objects.link(obj)
data=bpy.data.cameras.new('CityR5_LifeCamera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
target=origin+Vector((0,-5,1));cam.location=target+Vector((15,-21,13));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=26;data.clip_end=30000
scene.view_settings.view_transform=source_scene.view_settings.view_transform;scene.view_settings.exposure=source_scene.view_settings.exposure
scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for s in bpy.data.scenes:
    if s.name.startswith('CityR5_'):s.render.fps=24;s.frame_start=1;s.frame_end=576
bpy.context.window.scene=scene;scene.frame_set(240)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0;area.spaces.active.clip_end=30000
unused=[data for data in bpy.data.meshes if data.users-int(data.use_fake_user)==0]
for data in unused:data.use_fake_user=False;bpy.data.meshes.remove(data)
report={'world_size_m':[4000,4000],'interiors_updated':len(placements),'new_fixture_instances':new_objects,
        'preserved_special_areas':retained,'old_scale_figures_removed':len(old_figures),'animated_preview_residents':10+extra_residents,'animated_doors':2,
        'noninterior_geometry_and_wind_masks_preserved':True,'preserved_sha256':before,'preview_only_not_unity_runtime':True,'unity_play_tested':False}
(BASE/'city_update.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Ciudad_Viva_R5.blend'),compress=True)
scene.render.filepath=str(BASE/'renders/Ciudad_4km_Viva_R5.png');bpy.ops.render.render(write_still=True)
# El mapa FBX se mantiene estático; los personajes animados se importan como prefabs separados.
bpy.context.window.scene=source_scene
export(BASE/'export/Map/Villa_Alarma_Ciudad_R5.fbx',[root]+list(root.children_recursive))
print('CITY_LIFE_R5_MAP_READY',json.dumps(report),flush=True)
