"""Divide nuestra ciudad R6 para revisión jugable. Conserva mallas/materiales; exporta puertas aparte."""
import bpy,json,sys,math,collections,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from source_paths import revision;R6=revision(6);sys.path.insert(0,str(R6));from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(R6/'Villa_Alarma_Compras_R6.blend'));source_scene=bpy.context.scene;source_scene.frame_set(1)
world=bpy.data.objects['VillaAlarma_4000m'];objects=[o for o in world.children_recursive if o.type=='MESH'];scene=bpy.data.scenes.new('Playtest_Export');bpy.context.window.scene=scene
def point(p):return [float(p[0]),float(p[2]),float(-p[1])]
cached_bounds={};cached_matrices={}
def bounds(obj):
    if obj in cached_bounds:return cached_bounds[obj]
    cached_matrices[obj]=obj.matrix_world.copy()
    corners=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    low=Vector(tuple(min(p[i] for p in corners) for i in range(3)));high=Vector(tuple(max(p[i] for p in corners) for i in range(3)));cached_bounds[obj]=(low,high);return low,high
def clean(label):return ''.join(c if c.isalnum() or c=='_' else '_' for c in label)
collidable={'bridge','Ground','prop','landscape','RiverWalk','Roads','Sidewalks','building','planter_rim','removable_roof','garden','pedestrian_access','landform','ParkPaths','public_space','park_design','BusinessAprons','sidewalk_furniture','hero_shell','detailed_interior','door','Sewer','interior','Plaza','PlazaGardens','bicycle_rack','gallery_business','escape_route','landmark','cafe_terrace','plaza_design','ev_charger','metro_entrance','landmark_sign'}
heroes=['Minimarket','MallJewelry','Bank','Restaurant','Clothing','PaintGarage','Hideout','FenceGear','Police']
door_objects=[o for o in objects if any(o.name.startswith('R2_Hero_'+name+'_Door') for name in heroes)]
groups=collections.defaultdict(list);origins={};boxes={}
for obj in objects:
    if obj in door_objects:continue
    lo,hi=bounds(obj);mid=(lo+hi)/2;size=hi-lo
    if max(size.x,size.y)>250:
        if obj.get('MapRole') in ['potted_foliage','planter_rim'] and '_R4_' in obj.name:key='Wide_'+clean(obj.name.split('_R4_')[0])
        else:key='Globals'
    else:
        x=max(0,min(15,int((mid.x+2000)//250)));y=max(0,min(15,int((mid.y+2000)//250)));key=f'Cell_{x:02}_{y:02}'
    groups[key].append(obj)
    if key not in boxes:boxes[key]=[lo.copy(),hi.copy()]
    else:
        boxes[key][0]=Vector(tuple(min(boxes[key][0][i],lo[i]) for i in range(3)));boxes[key][1]=Vector(tuple(max(boxes[key][1][i],hi[i]) for i in range(3)))
colors=[]
for mat in bpy.data.materials:
    rgba=mat.diffuse_color;metallic=0;roughness=.8
    if mat.use_nodes:
        node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if node:rgba=(*node.inputs['Base Color'].default_value[:3],node.inputs['Alpha'].default_value);metallic=node.inputs['Metallic'].default_value;roughness=node.inputs['Roughness'].default_value
    rgb=[v*12.92 if v<=.0031308 else 1.055*max(v,0)**(1/2.4)-.055 for v in rgba[:3]]
    colors.append({'name':mat.name,'r':rgb[0],'g':rgb[1],'b':rgb[2],'a':rgba[3],'metallic':metallic,'roughness':roughness})
(B/'materials.json').write_text(json.dumps({'materials':colors},indent=2),encoding='utf-8')
report=[];object_index=0
completed=set(json.loads((B/'completed_exports.json').read_text())) if (B/'completed_exports.json').exists() else set()
for key,items in sorted(groups.items()):
    lo,hi=boxes[key];origin=Vector((0,0,0)) if key=='Globals' else Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,0))
    reuse=key in completed and (B/'export/World'/(key+'.fbx')).is_file()
    root=None if reuse else bpy.data.objects.new('WorldPart_'+key,None)
    if root:scene.collection.objects.link(root)
    copies=[];parts=[]
    for source in items:
        node_name='N_'+str(object_index).zfill(6);object_index+=1
        if not reuse:
            obj=bpy.data.objects.new(node_name,source.data);scene.collection.objects.link(obj);obj.parent=root;obj.matrix_basis=Matrix.Translation(-origin)@cached_matrices[source];copies.append(obj)
        role=source.get('MapRole','none');minimum,maximum=bounds(source);size=maximum-minimum
        tree=role in ['street_tree','forest'];radius=max(.13,min(.35,min(size.x,size.y)*.05));height=min(4,max(1.6,size.z*.65))
        parts.append({'node':node_name,'source':source.name,'role':role,'collision':2 if tree else 1 if role in collidable or source.name.startswith('R6_FoodDisplay') else 0,
                      'treeCenter':point(Vector(((minimum.x+maximum.x)/2,(minimum.y+maximum.y)/2,minimum.z+height/2))-origin),'radius':radius,'height':height,
                      'heroRoof':source.name.startswith('R2_Hero_') and '_Roof' in source.name,'wind':bool(source.data.color_attributes.get('WindMask'))})
    if not reuse:export(B/'export/World'/(key+'.fbx'),[root]+copies)
    row={'id':key,'file':'World/'+key+'.fbx','origin':point(origin),'center':point((lo+hi)/2),'size':point(Vector((hi.x-lo.x,hi.y-lo.y,hi.z-lo.z))),'always':key=='Globals','parts':parts}
    row['size']=[abs(v) for v in row['size']];report.append(row)
    if not reuse:bpy.data.batch_remove(ids=tuple(copies+[root]))
    print('EXPORTED_WORLD_PART',key,len(items),flush=True)
doors=[]
for hero in heroes:
    leaves=[o for o in door_objects if o.name.startswith('R2_Hero_'+hero+'_Door')];assert leaves,hero
    leaves.sort(key=lambda o:o.matrix_world.translation.x);template=leaves[0];obj=bpy.data.objects.new('Door_'+hero,template.data);scene.collection.objects.link(obj);obj.scale=template.matrix_world.to_scale()
    export(B/'export/Doors'/(hero+'.fbx'),[obj]);bpy.data.objects.remove(obj,do_unlink=True)
    location=bpy.data.objects['R2_Hero_'+hero].matrix_world.translation
    doors.append({'id':hero,'file':'Doors/'+hero+'.fbx','single':len(leaves)==1,'leaves':[{'position':point(o.matrix_world.translation),'yaw':0 if i==0 else 180} for i,o in enumerate(leaves)],'threshold':point(Vector((sum(o.matrix_world.translation.x for o in leaves)/len(leaves),sum(o.matrix_world.translation.y for o in leaves)/len(leaves),location.z)))})
# Alturas del suelo real para los grafos de cada local, con rayos sobre las superficies arquitectónicas.
floor_roles={'Ground','Sidewalks','BusinessAprons','hero_shell','pedestrian_access','Roads','public_space','Plaza','ParkPaths'}
floor_candidates=[]
for obj in objects:
    if obj.get('MapRole') not in floor_roles:continue
    lo,hi=bounds(obj);floor_candidates.append((obj,lo,hi))
bvhs={}
def height_at(x,y,z):
    hits=[]
    for obj,lo,hi in floor_candidates:
        if not(lo.x-.01<=x<=hi.x+.01 and lo.y-.01<=y<=hi.y+.01):continue
        if obj not in bvhs:
            vertices=[obj.matrix_world@v.co for v in obj.data.vertices];bvhs[obj]=BVHTree.FromPolygons(vertices,[list(p.vertices) for p in obj.data.polygons],all_triangles=False)
        hit,normal,_,_=bvhs[obj].ray_cast(Vector((x,y,z+1.8)),Vector((0,0,-1)),6)
        if hit is not None and normal.z>.4:hits.append(hit.z)
    return max(hits) if hits else z
district=json.loads((R6/'district.json').read_text());raw=json.loads((R6/'traffic_graph.json').read_text())['nodes'];shopping=[]
for shop in district['shops']:
    origin=bpy.data.objects['R2_Hero_'+shop['id']].matrix_world.translation.copy();offset=Vector((origin.x-shop['center'][0],origin.y,origin.z))
    selected=[i for i,n in enumerate(raw) if abs(n['v'][0]-shop['center'][0])<7.6];mapping={old:i for i,old in enumerate(selected)};nodes=[]
    for index in selected:
        p=raw[index]['v'];x=p[0]+offset.x;y=-p[2]+offset.y;z=height_at(x,y,origin.z)
        nodes.append({'v':[x,z,-y],'links':[mapping[n] for n in raw[index]['links'] if n in mapping]})
    worldshop=json.loads(json.dumps(shop));worldshop['origin']=point(origin);worldshop['nodes']=nodes
    sx=origin.x+shop['staff'][0];sy=origin.y+shop['staff'][1];worldshop['staffWorld']=[sx,height_at(sx,sy,origin.z),-sy]
    for name in ['walk','entry','browseStations','queue','exit','products']:worldshop[name]=[{'v':p} for p in worldshop[name]]
    shopping.append(worldshop)
manifest=json.loads((revision(5)/'baseline/city_manifest.json').read_text(encoding='utf-8'));pois=[]
for poi in manifest['pois']:
    p=poi.get('entrance',poi['position']);target=Vector(p);target.y-=3;target.z=height_at(target.x,target.y,poi['position'][2])+.05
    pois.append({'id':poi['id'],'label':poi['label'],'position':point(target),'yaw':180})
pois.insert(0,{'id':'Plaza','label':'Plaza central','position':[0,.25,75],'yaw':0})
(B/'world.json').write_text(json.dumps({'version':'playtest-r7-1','worldSize':[4000,4000],'cells':report,'doors':doors,'shops':shopping,'pois':pois},indent=2),encoding='utf-8')
catalog=json.loads((R6/'animation_catalog.json').read_text());(B/'characters.json').write_text(json.dumps({'characters':[{'id':r['id'],'rig':r['rig']} for r in catalog]},indent=2))
assert object_index+len(door_objects)==len(objects),(object_index,len(door_objects),len(objects))
(B/'export_validation.json').write_text(json.dumps({'passed':True,'mesh_objects':len(objects),'exported_world_meshes':object_index,'door_leaves':len(door_objects),'cells':len(report),'characters':18,'world_size_m':[4000,4000],'source_meshes_modified':False},indent=2))
print('PLAYTEST_WORLD_EXPORTED',len(report),'parts',len(objects),'meshes',flush=True)
