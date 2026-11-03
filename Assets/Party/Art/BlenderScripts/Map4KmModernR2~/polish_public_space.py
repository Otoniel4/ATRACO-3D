"""Volúmenes finales de oficinas, accesos ajardinados y equipamiento de parques."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
from mesh_tools import Batch
import modern_assets as A
from layout_math import inside,overlap,point_segment,rect
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
scene=bpy.data.scenes['CityR2_Overview'];bpy.context.window.scene=scene
root=bpy.data.objects['VillaAlarma_4000m']
if root.get('PublicSpaceR2Finished'):print('PUBLIC_SPACE_ALREADY_FINISHED');raise SystemExit(0)
for name in json.loads((BASE/'palette.json').read_text(encoding='utf-8')):
    material=bpy.data.materials.get('City4_'+name)
    if material:M.INDEX[name]=len(M.MATERIALS);M.MATERIALS.append(material)
config=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'))
layout=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))
work=bpy.data.scenes.new('OfficeModeling');bpy.context.window.scene=work
for i in range(3):
    for suffix in ['', '_Roof']:
        old=bpy.data.meshes.get('CityR2_Tower_'+str(i)+suffix)
        if old:old.name='Before_'+old.name
    A.office(i)
bpy.context.window.scene=scene;bpy.data.scenes.remove(work)
sectors={s.name:s for s in root.children};batches={};trees=0

def clear(p,radius=1):
    return all(point_segment(p,l['a'],l['b'])>l['width']/2+radius for l in layout['lines']) and not any(inside(p,q) for q in layout['river'])

def sector_at(p):
    x=min(7,max(0,int((p[0]+2000)//500)));y=min(7,max(0,int((p[1]+2000)//500)))
    return sectors[f'Sector_{x:02d}_{y:02d}']

def geometry(batch,p,angle=0):
    parent=sector_at(p);target=batches.setdefault(parent.name,Batch())
    A.merge(target,batch,Matrix.Translation(Vector(p))@Matrix.Rotation(angle,4,'Z'))

def place(name,data,p):
    parent=sector_at(p);obj=bpy.data.objects.new(name,data);bpy.data.collections[parent.name].objects.link(obj);obj.parent=parent
    obj.location=Vector(p)-parent.matrix_world.translation;obj['MapRole']='public_space';return obj

for obj in list(root.children_recursive):
    asset=obj.get('R2Asset','')
    if not asset.startswith('Tower_'):continue
    obj.data=A.PROTOTYPES[asset]
    roof=bpy.data.objects[obj.name+'_ModernRoof'];roof.data=A.ROOFS[asset]
    p=obj.matrix_world.translation.copy();angle=obj.rotation_euler.z;rot=Matrix.Rotation(angle,3,'Z')
    b=Batch();b.box((0,-21,.025),(9,9,.05),'ivory')
    for x in [-4,-2,0,2,4]:b.box((x,-21,.055),(.025,9,.012),'stone')
    for x in [-19,19]:
        for y in [-20,19]:
            q=p+rot@Vector((x,y,0))
            if clear(q[:2],2):A.planter(b,(x,y,0),(3.2,1.3,.65),True)
    for x in [-21,21]:
        q=p+rot@Vector((x,5,0));q.z=0
        if clear(q[:2],4):
            tree=bpy.data.meshes['CityR2_Tree_'+str(trees%4)];place('R2_OfficeTree',tree,q);trees+=1
    geometry(b,(p.x,p.y,0),angle)

court=Batch();court.box((0,0,.06),(15,28,.12),'teal')
for x in [-7.3,7.3]:court.box((x,0,.135),(.08,27.6,.02),'marking')
for y in [-13.7,0,13.7]:court.box((0,y,.135),(14.6,.08,.02),'marking')
for y in [-10.5,10.5]:
    court.box((0,y,.14),(4.9,.08,.025),'marking')
    for x in [-2.45,2.45]:court.box((x,y+(-1.7 if y<0 else 1.7),.14),(.08,3.4,.025),'marking')
    court.box((0,math.copysign(13.4,y),1.6),(.12,.12,3.2),'charcoal')
    court.box((0,math.copysign(12.7,y),3.5),(1.8,.12,1.1),'ivory')
    court.box((0,math.copysign(12.0,y),3.1),(.58,.58,.04),'coral')
for i in range(40):
    a=i*math.tau/40;c=(i+1)*math.tau/40
    court.beam((1.8*math.cos(a),1.8*math.sin(a),.145),(1.8*math.cos(c),1.8*math.sin(c),.145),.035,'marking',5)
A.register('BasketballCourt',court,category='park')
play=Batch();play.box((0,0,.07),(12,12,.14),'sand')
for x in [-1.1,1.1]:
    for y in [-1,1]:play.box((x,y,1.1),(.14,.14,2.2),'charcoal')
play.box((0,0,1.65),(2.4,2.2,.14),'timber')
for i in range(6):play.box((0,2.4-i*.28,.15+i*.28),(1.2,.32,.15),'mustard')
play.add([(-.65,-1,1.7),(.65,-1,1.7),(.65,-4.0,.2),(-.65,-4.0,.2)],[(0,3,2,1)],'coral')
for x in [-.75,.75]:play.beam((x,-1,1.9),(x,-4,.40),.07,'mustard',6)
for x in [-1.1,1.1]:play.beam((x,-1,2.5),(x,1,2.5),.045,'teal',6)
A.register('Playground',play,category='park')
parks=0
for index,(bx,by) in enumerate(config['park_blocks']):
    if index%2:continue
    cx=-1600+(bx+.5)*160;cy=-1600+(by+.5)*160
    for name,dx,dy,w,d in [('BasketballCourt',-25,24,15,28),('Playground',25,-25,12,12)]:
        x,y=cx+dx,cy+dy;polygon=rect(x-w/2-.5,y-d/2-.5,x+w/2+.5,y+d/2+.5)
        if any(overlap(polygon,r) for r in layout['roads']):continue
        for tree in list(root.children_recursive):
            if tree.type=='MESH' and ('Tree_' in tree.data.name or 'ForestTree_' in tree.data.name):
                if inside(tree.matrix_world.translation[:2],polygon):bpy.data.objects.remove(tree,do_unlink=True)
        place('R2_'+name,A.PROTOTYPES[name],(x,y,0));parks+=1
for name,batch in batches.items():
    origin=sectors[name].matrix_world.translation;batch.vertices=[tuple(Vector(v)-origin) for v in batch.vertices]
    place('R2_CorporatePublicSpace_'+name,batch.data('R2_CorporatePublicSpace_'+name),origin)
root['PublicSpaceR2Finished']=True
bpy.context.view_layer.update()
catalog=json.loads((BASE/'asset_catalog.json').read_text(encoding='utf-8'));updated={e['id']:e for e in A.CATALOG}
catalog=[updated.pop(e['id'],e) for e in catalog]+list(updated.values())
(BASE/'asset_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'));meshes=[o for o in root.children_recursive if o.type=='MESH']
manifest.update({'mesh_objects':len(meshes),'evaluated_triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),
                 'new_prototypes':len(catalog),'park_equipment_sets':parks,'office_trees':trees})
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['CityR2_ModernStreet']
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
print('PUBLIC_SPACE_R2_FINISHED',trees,'office trees',parks,'park equipment sets',flush=True)
