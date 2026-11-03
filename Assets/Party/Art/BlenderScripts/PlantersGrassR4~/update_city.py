"""Reemplaza el follaje de macetas, conserva sus bases y añade pasto sobre superficies de césped."""
import bpy,sys,json,math,random,hashlib,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from flora import Flora,materials,C
from wind_nodes import create_group,attach
bpy.ops.wm.open_mainfile(filepath=str(BASE/'baseline/City_Trees_R3.blend'))
for s in bpy.data.scenes:
    if s.name.startswith('CityR3_'):s.name=s.name.replace('CityR3_','CityR4_')
scene=bpy.data.scenes['CityR4_StreetLevel'];bpy.context.window.scene=scene
root=bpy.data.objects['VillaAlarma_4000m'];original=list(root.children_recursive)
materials();wind=create_group();rng=random.Random(C['seed'])
centers=[Vector((-240,-287,0)),Vector((0,0,0)),Vector((-1012,-696,0))]


def distance(p):return min(math.hypot(p.x-c.x,p.y-c.y) for c in centers)


def face_hash(data,indices):
    value=hashlib.sha256()
    for i in indices:
        face=data.polygons[i];mat=data.materials[face.material_index]
        value.update((mat.name if mat else '').encode())
        value.update(str(tuple(tuple(data.vertices[v].co) for v in face.vertices)).encode())
    return value.hexdigest()


def tree_hash():
    value=hashlib.sha256();meshes={}
    for obj in sorted((o for o in original if o.type=='MESH' and o.data.name.startswith('TreeR3_')),key=lambda o:o.name):
        value.update(obj.name.encode());value.update(str(tuple(tuple(r) for r in obj.matrix_world)).encode())
        if obj.data.name not in meshes:
            geometry=hashlib.sha256()
            geometry.update(str([tuple(v.co) for v in obj.data.vertices]).encode())
            geometry.update(str([tuple(p.vertices) for p in obj.data.polygons]).encode())
            color=obj.data.color_attributes['WindMask'];geometry.update(str([tuple(c.color) for c in color.data]).encode())
            meshes[obj.data.name]=geometry.hexdigest()
        value.update(obj.data.name.encode());value.update(meshes[obj.data.name].encode())
        value.update(str([(m.name,m.node_group.name) for m in obj.modifiers if m.type=='NODES']).encode())
    return value.hexdigest()


before_trees=tree_hash()
by_data=collections.defaultdict(list)
for obj in original:
    if obj.type=='MESH' and not obj.data.name.startswith('TreeR3_'):by_data[obj.data].append(obj)
records=[];changed=[];component_total=0;flower_faces=0;wind_objects=0;planter_soils=0;pending_wind=[]
for data,objects in by_data.items():
    leaf_slots={i for i,m in enumerate(data.materials) if m and m.name.startswith('City4_leaf_')}
    if not leaf_slots:continue
    # Componentes conectadas: distingue los viejos poliedros de los tallos pequeños de mesa.
    faces=[p for p in data.polygons if p.material_index in leaf_slots]
    vertex_to_faces=collections.defaultdict(list)
    for face in faces:
        for v in face.vertices:vertex_to_faces[v].append(face.index)
    pending={f.index for f in faces};components=[]
    while pending:
        todo=[pending.pop()];indices=[];vertices=set()
        while todo:
            index=todo.pop();face=data.polygons[index];indices.append(index);vertices.update(face.vertices)
            for v in face.vertices:
                for other in vertex_to_faces[v]:
                    if other in pending:pending.remove(other);todo.append(other)
        if len(indices)>=12:components.append((indices,vertices))
    if not components:continue
    soil_faces=[p for p in data.polygons if data.materials[p.material_index] and data.materials[p.material_index].name=='City4_soil' and p.normal.z>.8]
    soils=[([tuple(data.vertices[v].co) for v in p.vertices],p.center.z) for p in soil_faces]
    planter_soils+=len(soils)*len(objects)
    shrubs=[];remove=set()
    for indices,vertices in components:
        vs=[data.vertices[v].co for v in vertices];low=Vector(tuple(min(v[a] for v in vs) for a in range(3)));high=Vector(tuple(max(v[a] for v in vs) for a in range(3)))
        center=(low+high)/2;size=high-low
        nearest=None
        for polygon,z in soils:
            x0,x1=min(p[0] for p in polygon),max(p[0] for p in polygon)
            y0,y1=min(p[1] for p in polygon),max(p[1] for p in polygon)
            if x0-.08<=center.x<=x1+.08 and y0-.08<=center.y<=y1+.08 and low.z-.25<=z<=center.z+.05:
                if nearest is None or abs(z-low.z)<abs(nearest-low.z):nearest=z
        z=nearest+.015 if nearest is not None else low.z+.025
        height=max(.18,high.z-z+.055)
        shrubs.append((tuple((center.x,center.y,z)),max(.18,size.x),max(.18,size.y),height))
        remove.update(indices)
    # Las flores anteriores eran poliedros; las nuevas son pequeñas corolas abiertas.
    oldflowers=[p.index for p in data.polygons if data.materials[p.material_index] and data.materials[p.material_index].name.startswith(('City4_flower_pink','City4_flower_yellow'))]
    remove.update(oldflowers);flower_faces+=len(oldflowers)*len(objects)
    keep=[p.index for p in data.polygons if p.index not in remove];before=face_hash(data,keep)
    used=sorted({v for i in keep for v in data.polygons[i].vertices});lookup={v:i for i,v in enumerate(used)}
    replacement=bpy.data.meshes.new(data.name+'_R4Base')
    replacement.from_pydata([tuple(data.vertices[v].co) for v in used],[],[tuple(lookup[v] for v in data.polygons[i].vertices) for i in keep]);replacement.update()
    for mat in data.materials:replacement.materials.append(mat)
    for p,index in zip(replacement.polygons,keep):p.material_index=data.polygons[index].material_index
    assert face_hash(replacement,range(len(replacement.polygons)))==before,data.name
    variants=[]
    for lod in range(3):
        batch=Flora(C['seed']+sum(data.name.encode()))
        for i,(p,w,d,h) in enumerate(shrubs):batch.shrub(p,w,d,h,lod,(i+sum(data.name.encode()))%4)
        variants.append(batch.data('PlantR4_'+data.name+f'_Foliage_LOD{lod}'))
    border=Flora()
    for polygon,z in soils:border.rim(polygon,z+.005)
    rim=border.data('PlantR4_'+data.name+'_Rims') if border.v else None
    for source in objects:
        source.data=replacement;p=source.matrix_world.translation;dist=distance(p)
        lod=0 if dist<C['near_radius_m'] else (1 if dist<C['middle_radius_m'] else 2)
        collection=source.users_collection[0]
        obj=bpy.data.objects.new(source.name+'_R4_Plants',variants[lod]);collection.objects.link(obj);obj.parent=source
        obj['MapRole']='potted_foliage' if soils else 'understory_foliage';obj['PlantLOD_R4']=lod
        if dist<C['near_radius_m']:pending_wind.append(obj);wind_objects+=1
        if rim:
            rim_obj=bpy.data.objects.new(source.name+'_R4_Rims',rim);collection.objects.link(rim_obj);rim_obj.parent=source;rim_obj['MapRole']='planter_rim'
        component_total+=len(shrubs)
        records.append({'source':source.name,'foliage':obj.name,'components':len(shrubs),'lod':lod,'wind_blender':dist<C['near_radius_m']})
    changed.append({'source_mesh':data.name,'instances':len(objects),'shrubs_per_instance':len(shrubs),'nonfoliage_hash':before})
    if len(changed)%10==0:print('PLANT_PROTOTYPES_BUILT',len(changed),flush=True)
print('POTTED_FOLIAGE_REPLACED',component_total,'components',len(changed),'prototypes',flush=True)
bpy.context.view_layer.update()
for obj in pending_wind:attach(obj,wind)

# Superficies reales: un rayo debe encontrar césped en el centro y cuatro extremos de cada parche.
# Se incluyen pavimentos, suelos y bases de edificios para no plantar encima de ellos.
vertices=[];polygons=[];allowed=[];floor_cache={}
for obj in original:
    if obj.type!='MESH' or obj.data.name.startswith('TreeR3_'):continue
    data=obj.data
    if data not in floor_cache:
        floor_cache[data]=[p for p in data.polygons if p.normal.z>.65]
    matrix=obj.matrix_world
    for face in floor_cache[data]:
        z=(matrix@face.center).z
        if not -1.1<z<1.5:continue
        vs=[matrix@data.vertices[v].co for v in face.vertices]
        if max(v.z for v in vs)-min(v.z for v in vs)>.08:continue
        start=len(vertices);vertices.extend(vs);polygons.append(tuple(range(start,start+len(vs))))
        mat=data.materials[face.material_index]
        allowed.append(bool(mat and mat.name.startswith('City4_grass')))
surface=BVHTree.FromPolygons(vertices,polygons,all_triangles=False)
print('GRASS_SURFACE_INDEX_READY',len(polygons),'faces',flush=True)


def ground(x,y):
    point,normal,index,dist=surface.ray_cast(Vector((x,y,1.65)),Vector((0,0,-1)),4)
    return point.z if index is not None and allowed[index] else None


grass_meshes=[]
for lod in range(3):
    b=Flora(244);b.grass(lod=lod);grass_meshes.append(b.data('PlantR4_CityGrass_LOD'+str(lod)))
sectors={o.name:o for o in root.children if o.name.startswith('Sector_')}
placed=collections.defaultdict(list);grass_records=[];grass_counts=[0,0,0];active_grass=0;pending_grass_wind=[]


def add_grass(x,y,yaw):
    global active_grass
    if len(grass_records)>=C['maximum_grass_patches'] or abs(x)>1985 or abs(y)>1985:return
    key=(math.floor(x/1.7),math.floor(y/1.7))
    if any(math.hypot(x-a,y-b)<1.52 for dx in [-1,0,1] for dy in [-1,0,1] for a,b in placed.get((key[0]+dx,key[1]+dy),[])):return
    z=ground(x,y)
    if z is None:return
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
        height=ground(x+math.cos(a+yaw)*.86,y+math.sin(a+yaw)*.86)
        if height is None or abs(height-z)>.035:return
    p=Vector((x,y,z+.007));dist=distance(p);lod=0 if dist<35 else (1 if dist<210 else 2)
    i=min(7,max(0,int((x+2000)//500)));j=min(7,max(0,int((y+2000)//500)));parent=sectors[f'Sector_{i:02d}_{j:02d}']
    obj=bpy.data.objects.new('R4_Grass',grass_meshes[lod]);bpy.data.collections[parent.name].objects.link(obj);obj.parent=parent
    obj.location=p-parent.matrix_world.translation;obj.rotation_euler.z=yaw;obj['MapRole']='detailed_grass';obj['GrassLOD_R4']=lod
    animated=dist<32 and active_grass<160
    if animated:pending_grass_wind.append(obj);active_grass+=1
    grass_counts[lod]+=1;placed[key].append((x,y));grass_records.append({'object':obj.name,'p':list(p),'lod':lod,'wind_blender':animated})
    if len(grass_records)%2000==0:print('GRASS_PATCHES_PLACED',len(grass_records),flush=True)


# Más detalle cerca de cámara; después, pequeños grupos repartidos por jardines y alcorques.
for center in centers:
    for i in range(-25,26):
        for j in range(-25,26):
            add_grass(center.x+i*2.8+rng.uniform(-.25,.25),center.y+j*2.8+rng.uniform(-.25,.25),rng.random()*math.tau)
for obj in original:
    if obj.type!='MESH':continue
    p=obj.matrix_world.translation
    if obj.get('MapRole')=='garden':
        for x,y in [(-8,-6),(8,-6),(-9,-4),(9,-4)]:
            q=obj.matrix_world@Vector((x,y,0));add_grass(q.x,q.y,rng.random()*math.tau)
    elif obj.data.name.startswith('TreeR3_'):
        a=rng.random()*math.tau;r=rng.uniform(1.8,3.0)
        add_grass(p.x+r*math.cos(a),p.y+r*math.sin(a),a)
    elif obj.get('MapRole')=='park_design':
        for j in range(120):add_grass(p.x+rng.uniform(-38,38),p.y+rng.uniform(-38,38),rng.random()*math.tau)
bpy.context.view_layer.update()
for obj in pending_grass_wind:attach(obj,wind)
assert tree_hash()==before_trees,'Cambió el arbolado R3'
for s in bpy.data.scenes:s.render.fps=C['fps'];s.frame_start=1;s.frame_end=192

# Vista del local de la captura: misma ciudad con las jardineras reconstruidas.
hero=next(o for o in original if o.type=='MESH' and o.name=='R2_Hero_Minimarket')
data=bpy.data.cameras.new('R4_PlanterDetailCamera');camera=bpy.data.objects.new(data.name,data)
detail=bpy.data.scenes.new('CityR4_PlanterDetail');detail.world=scene.world;detail.render.engine=scene.render.engine
for collection in scene.collection.children:detail.collection.children.link(collection)
for light in (o for o in scene.objects if o.type=='LIGHT'):detail.collection.objects.link(light)
detail.collection.objects.link(camera);detail.camera=camera
# Dos jardineras están junto a los laterales del frente, en coordenadas locales del negocio.
p=hero.matrix_world@Vector((-4.44,-6,.70));target=p+Vector((0,0,.15))
camera.location=p+Vector((3,-7,2.8));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=7.5;data.clip_end=30000
detail.view_settings.view_transform=scene.view_settings.view_transform;detail.view_settings.exposure=scene.view_settings.exposure
detail.render.resolution_x=1400;detail.render.resolution_y=1050;detail.render.resolution_percentage=100;detail.render.image_settings.file_format='PNG'
detail.render.fps=C['fps'];detail.frame_start=1;detail.frame_end=192
bpy.context.window.scene=detail;detail.frame_set(49)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
            area.spaces.active.clip_end=30000;area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
report={'world_size_m':[4000,4000],'shrub_components_replaced':component_total,'prototype_meshes_rebuilt':len(changed),
        'foliage_objects_added':len(records),'planter_soil_surfaces':planter_soils,'old_flower_faces_removed':flower_faces,
        'nonfoliage_faces_preserved':True,'trees_R3_preserved':True,'trees_hash':before_trees,
        'blender_animated_shrub_objects':wind_objects,'grass_patches':len(grass_records),'grass_lod_counts':grass_counts,
        'grass_animated_blender':active_grass,'grass_only_on_raycast_grass_surfaces':True,'unity_verified':False}
# Las variantes no usadas se regeneran desde la receta; no hace falta guardarlas en el mapa completo.
unused=[data for data in bpy.data.meshes if data.users-int(data.use_fake_user)==0]
for data in unused:data.use_fake_user=False;bpy.data.meshes.remove(data)
used_meshes={obj.data for obj in root.children_recursive if obj.type=='MESH'}
triangle_counts={data:sum(len(p.vertices)-2 for p in data.polygons) for data in used_meshes}
report['unused_meshes_removed']=len(unused)
report['instantiated_rest_triangles']=sum(triangle_counts[obj.data] for obj in root.children_recursive if obj.type=='MESH')
(BASE/'city_update.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(BASE/'plant_placements.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(BASE/'grass_placements.json').write_text(json.dumps(grass_records,indent=2),encoding='utf-8')
(BASE/'preserved_faces.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Jardineras_Pasto_R4.blend'),compress=True)
detail.render.filepath=str(BASE/'renders/Ciudad_Jardineras_R4.png');bpy.ops.render.render(write_still=True)
print('CITY_PLANTS_GRASS_R4_READY',json.dumps(report),flush=True)
