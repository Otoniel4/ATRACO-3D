"""Zona comercial de revisión: tres negocios, puntos de rutina y obstáculos explícitos para NavMesh."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import props as P
bpy.ops.wm.read_factory_settings(use_empty=True)
catalog=json.loads((BASE/'prop_catalog.json').read_text());placements=json.loads((BASE/'interior_placements.json').read_text())
with bpy.data.libraries.load(str(BASE/'Objetos_Locales_R5.blend'),link=False) as (src,dst):dst.meshes=[r['mesh'] for r in catalog]
P.palette();scene=bpy.context.scene;scene.name='LifeR5_CommercialDistrict';scene.render.fps=24;scene.frame_start=1;scene.frame_end=576
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='BLENDER_EEVEE_NEXT'
root=bpy.data.objects.new('CityLifeR5_District',None);scene.collection.objects.link(root)
shops=['Minimarket','Clothing','Restaurant']
with bpy.data.libraries.load(str(BASE/'baseline/City_Plants_R4.blend'),link=False) as (src,dst):
    dst.meshes=[n for n in src.meshes if any(n.startswith('CityR2_Hero_'+s) and '_Furniture' not in n for s in shops)
                or any(n.startswith('PlantR4_CityR2_Hero_'+s) and '_Roof' not in n and ('Foliage_LOD0' in n or '_Rims' in n) for s in shops)]
definitions=[];proxies=[];material_catalog={}
def place(name,data,p,parent=root,yaw=0):
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=parent;obj.location=p;obj.rotation_euler.z=yaw;return obj
def proxy(p,size):proxies.append({'position':list(p),'size':list(size)})
for index,shop in enumerate(shops):
    x=(index-1)*18;shop_root=place('Shop_'+shop,None,(x,0,0))
    body=bpy.data.meshes.get('CityR2_Hero_'+shop+'_R4Base');assert body,shop
    place('Shell_'+shop,body,(0,0,0),shop_root)
    # El techo queda separado y oculto solo en la vista de corte para leer las rutinas.
    roof_data=bpy.data.meshes.get('CityR2_Hero_'+shop+'_Roof') or bpy.data.meshes['CityR2_Hero_'+shop+'_Roof_R4Base']
    roof=place('Roof_'+shop,roof_data,(0,0,0),shop_root);roof.hide_render=True
    door_data=bpy.data.meshes['CityR2_Hero_'+shop+'_Door']
    place('Door_'+shop+'_L',door_data,(-1.1,-5.12,0),shop_root)
    place('Door_'+shop+'_R',door_data,(1.1,-5.12,0),shop_root,math.pi)
    for data in list(bpy.data.meshes):
        if data.name.startswith('PlantR4_CityR2_Hero_'+shop) and ('Foliage_LOD0' in data.name or '_Rims' in data.name):
            place(shop+'_Planters',data,(0,0,0),shop_root)
    for serial,item in enumerate(placements[shop]):
        data=bpy.data.meshes['Life5_'+item['asset']];obj=place('Fixture_'+shop+'_'+item['asset']+'_'+str(serial),data,item['position_blender'],shop_root,item['yaw'])
        if item['collision']:
            row=next(r for r in catalog if r['id']==item['asset']);a=row['bounds_min'];b=row['bounds_max']
            local=(Vector(a)+Vector(b))/2;p=obj.matrix_world@local
            # Matriz global se actualiza de una vez al final: aquí la conversión es explícita.
            c,s=math.cos(item['yaw']),math.sin(item['yaw']);lx,ly,lz=local
            p=(x+item['position_blender'][0]+lx*c-ly*s,item['position_blender'][1]+lx*s+ly*c,item['position_blender'][2]+lz)
            sx,sy,sz=[b[k]-a[k] for k in range(3)];proxy(p,(abs(c)*sx+abs(s)*sy,abs(s)*sx+abs(c)*sy,sz))
    for side in [-1,1]:proxy((x+side*6,0,2.1),(.22,10,4.2))
    proxy((x,5,2.1),(12,.22,4.2))
    for sign in [-1,1]:proxy((x+sign*3.55,-5,2.1),(4.9,.22,4.2))
    browse=[-.8,-.35,.16] if shop=='Minimarket' else ([-2.2,-.2,.16] if shop=='Clothing' else [2,-.3,.16])
    queue=([[3,-2.05+i*.7,.16] for i in range(3)] if shop=='Minimarket' else
           ([[-i*.7,2.7,.16] for i in range(3)] if shop=='Clothing' else [[3,.65-i*.7,.16] for i in range(3)]))
    # La ropa necesita un pasillo lateral hasta la caja; NavMesh resuelve la ruta completa.
    exit_path=[[1,-2.05,.16],[0,-3.8,.16],[0,-6.6,.16]] if shop=='Minimarket' else (
        [[2.3,2.7,.16],[2.3,-2,.16],[0,-4,.16],[0,-6.6,.16]] if shop=='Clothing' else [[1.2,.65,.16],[1.8,-3.6,.16],[0,-6.6,.16]])
    definitions.append({'id':shop,'center':[x,0,0],
        'walk':[[-5,-8.7,.16],[5,-8.7,.16],[5,-6.9,.16],[0,-6.9,.16],[-5,-6.9,.16]],
        'entry':[[0,-6.6,.16],[0,-3.8,.16]],'browse':browse,'queue':queue,'exit':exit_path,
        'staff':[3,-4,.16] if shop=='Minimarket' else ([0,4.55,.16] if shop=='Clothing' else [3,2.55,.16]),
        'staffYaw':math.pi if shop=='Minimarket' else 0,'staffVariant':[9,6,4][index]})
floor=P.Batch();floor.box((0,-7.5,.08),(72,5,.16),'ivory');floor.box((0,-14,-.08),(80,8,.16),'dark')
for x in range(-36,37,3):floor.box((x,-14,.012),(1.6,.10,.025),'paper')
for x in range(-36,37,2):floor.box((x,-7.5,.165),(.015,5,.012),'stone')
place('District_Ground',floor.data('Life5_DistrictGround'),(0,0,0))
floors=[{'position':[0,-7.5,.08],'size':[72,5,.16]}]+[{'position':[(i-1)*18,0,.08],'size':[12,10,.16]} for i in range(3)]
scene.world=bpy.data.worlds.new('LifeR5_Day');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.74,.82,1);bg.inputs['Strength'].default_value=.7
sun=bpy.data.lights.new('LifeR5_Sun','SUN');sun.energy=3;sun.angle=.14
obj=bpy.data.objects.new(sun.name,sun);scene.collection.objects.link(obj);obj.rotation_euler=(.4,-.45,-.4)
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.4
data=bpy.data.cameras.new('LifeR5_StreetCamera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
target=Vector((-18,-2,.75));cam.location=target+Vector((10,-17,13));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=19
scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(BASE/'renders/Calle_Comercial_R5.png');bpy.context.view_layer.update()
for obj in scene.objects:
    if obj.name.startswith('Roof_'):obj.hide_set(True)
(BASE/'district.json').write_text(json.dumps({'shops':definitions,'obstacles':proxies,'floors':floors},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Distrito_Comercial_R5.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('COMMERCIAL_DISTRICT_READY',len(definitions),'shops',len(proxies),'obstacle proxies',flush=True)
