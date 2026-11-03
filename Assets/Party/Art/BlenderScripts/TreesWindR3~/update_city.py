"""Sustituye solo vegetación de R2 y activa viento de previsualización cerca de las zonas de revisión."""
import bpy,sys,json,re,math,hashlib
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from tree_geometry import C
from wind_nodes import attach
sys.path.insert(0,str(BASE/'baseline'))
from layout_math import inside,point_segment
source=BASE/'baseline/City_Modern_R2.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
for scene in bpy.data.scenes:
    if scene.name.startswith('CityR2_'):scene.name=scene.name.replace('CityR2_','CityR3_')
scene=bpy.data.scenes['CityR3_StreetLevel'];bpy.context.window.scene=scene
root=bpy.data.objects['VillaAlarma_4000m']
def geometry_hash(objects):
    h=hashlib.sha256();seen=set()
    for obj in sorted(objects,key=lambda o:o.name):
        h.update(obj.name.encode());h.update(str(tuple(tuple(row) for row in obj.matrix_world)).encode())
        if obj.type=='MESH' and obj.data.as_pointer() not in seen:
            seen.add(obj.data.as_pointer());h.update(str([(tuple(v.co)) for v in obj.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in obj.data.polygons]).encode())
    return h.hexdigest()
targets=[o for o in root.children_recursive if o.type=='MESH' and re.match(r'CityR2_(ForestTree|Tree)_[0-5](\.|$)',o.data.name)]
target_set=set(targets);others=[o for o in root.children_recursive if o not in target_set]
before=geometry_hash(others)
# Índices espaciales: las copas nuevas no deben atravesar las fachadas de R2.
layout=json.loads((BASE/'baseline/layout.json').read_text(encoding='utf-8'));buildings={};roads={}
def cells(x0,y0,x1,y1):
    return ((x,y) for x in range(math.floor(x0/100),math.floor(x1/100)+1) for y in range(math.floor(y0/100),math.floor(y1/100)+1))
for building in others:
    if building.type!='MESH' or building.get('MapRole') not in ['building','hero_shell','gallery_business']:continue
    vertices=[building.matrix_world@Vector(p) for p in building.bound_box]
    box=(min(v.x for v in vertices),min(v.y for v in vertices),max(v.x for v in vertices),max(v.y for v in vertices),max(v.z for v in vertices))
    for key in cells(box[0],box[1],box[2],box[3]):buildings.setdefault(key,[]).append(box)
for road in layout['lines']:
    a,b=road['a'],road['b'];r=road['width']/2+1
    for key in cells(min(a[0],b[0])-r,min(a[1],b[1])-r,max(a[0],b[0])+r,max(a[1],b[1])+r):roads.setdefault(key,[]).append(road)
def free(p,radius,canopy_bottom):
    if abs(p.x)>1980 or abs(p.y)>1980:return False
    key=(math.floor(p.x/100),math.floor(p.y/100))
    if any(point_segment(p[:2],line['a'],line['b'])<line['width']/2+.6 for line in roads.get(key,[])):return False
    if any(inside(p[:2],polygon) for polygon in layout['river']):return False
    for k in cells(p.x-radius,p.y-radius,p.x+radius,p.y+radius):
        for x0,y0,x1,y1,z1 in buildings.get(k,[]):
            distance=math.hypot(max(x0-p.x,0,p.x-x1),max(y0-p.y,0,p.y-y1))
            if distance<.55 or (z1>canopy_bottom and distance<radius):return False
    return True
with bpy.data.libraries.load(str(BASE/'Arboles_Viento_R3.blend'),link=False) as (src,dst):
    dst.meshes=[n for n in src.meshes if n.startswith('TreeR3_')]
    dst.node_groups=[n for n in src.node_groups if n=='Trees_R3_NaturalWind']
catalog=json.loads((BASE/'catalog.json').read_text(encoding='utf-8'));group=bpy.data.node_groups['Trees_R3_NaturalWind']
centers=[Vector((-240,-287,0)),Vector((0,0,0)),Vector((-1012,-696,0))]
records=[];animated=0;lod_counts=[0,0,0];relocated=0;removed=0;pending=[];radii={}
for obj in targets:
    p=obj.matrix_world.translation.copy();old_data=obj.data.name;species=obj.get('R2Species')
    if species is None:species=int(re.search(r'Tree_([0-5])',old_data).group(1))
    distance=min(Vector((p.x-c.x,p.y-c.y,0)).length for c in centers)
    lod=0 if distance<C['near_radius_m'] else (1 if distance<C['middle_radius_m'] else 2)
    obj.data=bpy.data.meshes[catalog[species]['lods'][lod]['mesh']]
    if 'ForestTree_' in old_data:obj.scale=(obj.scale.x*1.25,obj.scale.y*1.25,obj.scale.z*1.30)
    if obj.data.name not in radii:radii[obj.data.name]=max(math.hypot(v.co.x,v.co.y) for v in obj.data.vertices)
    radius=radii[obj.data.name]*max(obj.scale.x,obj.scale.y)+.25
    canopy_bottom=p.z+catalog[species]['height_m']*.34*obj.scale.z
    if not free(p,radius,canopy_bottom):
        alternative=None
        for shift in [2,4,6,8,11,15,19,24]:
            for j in range(16):
                a=j*math.tau/16;q=p+Vector((math.cos(a)*shift,math.sin(a)*shift,0))
                if free(q,radius,canopy_bottom):alternative=q;break
            if alternative is not None:break
        if alternative is None:
            bpy.data.objects.remove(obj,do_unlink=True);removed+=1;continue
        obj.location+=alternative-p;p=alternative;relocated+=1
    obj['TreeSpeciesR3']=species;obj['TreeLOD_R3']=lod;obj['WindRGBAMask']=True
    pending.append((obj,distance<C['animated_radius_m']))
    lod_counts[lod]+=1
    records.append({'object':obj.name,'parent':obj.parent.name,'species':species,'lod':lod,
                    'position_blender':list(p),'scale':list(obj.scale),'rotation_z':obj.rotation_euler.z,'blender_wind':distance<C['animated_radius_m']})
bpy.context.view_layer.update()
for obj,enabled in pending:
    if enabled:attach(obj,group);animated+=1
after=geometry_hash(others);assert before==after,'Se alteró geometría ajena a vegetación'
for scene in bpy.data.scenes:
    scene.render.fps=C['fps'];scene.frame_start=1;scene.frame_end=C['fps']*C['loop_seconds']
bpy.context.window.scene=bpy.data.scenes['CityR3_StreetLevel'];bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False
            space.clip_end=30000;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
(BASE/'tree_placements.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
report={'trees_replaced':len(records),'blender_animated_near_review_zones':animated,'lod_counts':lod_counts,'trees_relocated_away_from_buildings':relocated,'trees_removed_without_clear_space':removed,
        'nonvegetation_geometry_sha256':before,'nonvegetation_preserved':True,'world_size_m':[4000,4000],
        'wind_loop_seconds':C['loop_seconds'],'unity_wind':'vertex shader; requires WindTree materials','unity_verified':False}
(BASE/'city_update.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Arboles_Viento_R3.blend'))
print('CITY_TREES_R3_READY',json.dumps(report),flush=True)
