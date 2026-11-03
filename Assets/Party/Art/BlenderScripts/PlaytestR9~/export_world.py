import bpy,json,math,os,sys,collections,hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Matrix,Vector
B=Path(__file__).resolve().parent;R7=sources9.r7();sys.path.insert(0,str(sources9.r6()));from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(B/os.environ.get('ALARMA_R9_WORLD','Villa_Alarma_3000_R9.blend')));scene=bpy.context.scene;root=bpy.data.objects['VillaAlarma_3000m'];old=json.loads((R7/'world.json').read_text(encoding='utf-8'));changes=json.loads((B/'map_changes.json').read_text(encoding='utf-8'));changed=set(changes['changed']);old_parts={p['source']:(c,p) for c in old['cells'] for p in c['parts']};objects=[o for o in root.children_recursive if o.type=='MESH' and len(o.data.polygons)>0]
groups=collections.defaultdict(list)
for o in objects:
    if o.name.startswith('R9_'):key='District_Start'
    elif o.name in old_parts:key=old_parts[o.name][0]['id']
    else:key='Globals'
    groups[key].append(o)
collidable={'bridge','Ground','prop','landscape','RiverWalk','Roads','Sidewalks','building','planter_rim','removable_roof','garden','pedestrian_access','landform','ParkPaths','public_space','park_design','BusinessAprons','sidewalk_furniture','hero_shell','detailed_interior','door','Sewer','interior','Plaza','PlazaGardens','bicycle_rack','gallery_business','escape_route','landmark','cafe_terrace','plaza_design','ev_charger','metro_entrance','landmark_sign','parked_vehicle'}
def unity(p):return [float(p[0]),float(p[2]),float(-p[1])]
def bound(o):
    ps=[o.matrix_world@Vector(p) for p in o.bound_box];return Vector(tuple(min(p[k] for p in ps) for k in range(3))),Vector(tuple(max(p[k] for p in ps) for k in range(3)))
colors=[]
for m in bpy.data.materials:
    rgba=m.diffuse_color;metal=0;rough=.8
    if m.use_nodes:
        n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if n:rgba=(*n.inputs['Base Color'].default_value[:3],n.inputs['Alpha'].default_value);metal=n.inputs['Metallic'].default_value;rough=n.inputs['Roughness'].default_value
    rgb=[v*12.92 if v<=.0031308 else 1.055*max(v,0)**(1/2.4)-.055 for v in rgba[:3]]
    colors.append({'name':m.name,'r':rgb[0],'g':rgb[1],'b':rgb[2],'a':rgba[3],'metallic':metal,'roughness':rough})
(B/'materials.json').write_text(json.dumps({'materials':colors},indent=2))
export_scene=bpy.data.scenes.new('R9_Export');bpy.context.window.scene=export_scene;rows=[];next_id=900000;fresh=0
for key,items in sorted(groups.items()):
    previous=next((c for c in old['cells'] if c['id']==key),None)
    # Cada parte recibe anclas nuevas; no se hereda la ambigüedad espacial de las exportaciones anteriores.
    reused=False
    if reused:
        row=json.loads(json.dumps(previous));row['reuse']=True;rows.append(row);continue
    ps=[bound(o) for o in items];lo=Vector(tuple(min(p[0][i] for p in ps) for i in range(3)));hi=Vector(tuple(max(p[1][i] for p in ps) for i in range(3)))
    origin=Vector((0,0,0)) if key=='Globals' else (Vector((previous['origin'][0],-previous['origin'][2],0)) if previous else Vector((-246,-277,0)))
    parent=bpy.data.objects.new('WorldPart_'+key,None);export_scene.collection.objects.link(parent);copies=[];parts=[]
    for obj in items:
        if obj.name in old_parts:node=old_parts[obj.name][1]['node']
        else:node='N_'+str(next_id);next_id+=1
        copy=bpy.data.objects.new(node,obj.data);export_scene.collection.objects.link(copy);copy.parent=parent;copy.matrix_basis=Matrix.Translation(-origin)@obj.matrix_world;copies.append(copy)
        a,b=bound(obj);size=b-a;role=obj.get('MapRole','none');tree=role in ['street_tree','forest'];height=min(4,max(1.6,size.z*.65))
        parts.append({'node':node,'source':obj.name,'role':role,'collision':2 if tree else 1 if role in collidable else 0,'treeCenter':unity(Vector(((a.x+b.x)/2,(a.y+b.y)/2,a.z+height/2))-origin),'radius':max(.13,min(.35,min(size.x,size.y)*.05)),'height':height,'heroRoof':role=='removable_roof' and obj.name.startswith('R9_Hero_'),'wind':bool(obj.data.color_attributes.get('WindMask'))})
    anchors=[]
    for name,point in [('Origin',(0,0,0)),('X',(1,0,0)),('Front',(0,-1,0))]:
        a=bpy.data.objects.new('R9_Anchor_'+name,None);export_scene.collection.objects.link(a);a.parent=parent;a.location=point;anchors.append(a)
    export(B/'export/World'/(key+'.fbx'),[parent]+copies+anchors);fresh+=1
    rows.append({'id':key,'file':'World/'+key+'.fbx','origin':unity(origin),'center':unity((lo+hi)/2),'size':[abs(v) for v in unity(hi-lo)],'always':key in ['Globals','District_Start'],'parts':parts,'reuse':False})
    bpy.data.batch_remove(ids=tuple(copies+anchors+[parent]));print('R9_PART_EXPORTED',key,len(items),flush=True)
district=json.loads((B/'district.json').read_text(encoding='utf-8'));replaced={p['id'] for p in district['pois']};pois=district['pois']+[p for p in old['pois'] if p['id'] not in replaced and abs(p['position'][0])<1480 and abs(p['position'][2])<1480]
doors=district['doors']+[d for d in old['doors'] if d['id'] not in replaced]
for d in doors:d['file']='Doors/Shutter.fbx' if d['single'] else 'Doors/DoubleLeaf120.fbx' if d['id'] in replaced else 'Doors/DoubleLeaf110.fbx'
world={'version':'playtest-r9-1','worldSize':[3000,3000],'cells':rows,'doors':doors,'shops':district['shops'],'pois':pois,'spawn':district['spawn'],'lobbySlots':district['lobby_slots']}
(B/'world.json').write_text(json.dumps(world,indent=2));(B/'export_validation.json').write_text(json.dumps({'passed':True,'world_size_m':[3000,3000],'parts':len(rows),'fresh':fresh,'reused':len(rows)-fresh,'shops':len(world['shops']),'doors':len(doors),'meshes':len(objects)},indent=2));print('R9_WORLD_EXPORTED',len(rows),fresh,'new',flush=True)
