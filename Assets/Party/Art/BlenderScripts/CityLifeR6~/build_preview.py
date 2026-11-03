"""Reproduce trazas del dominio C#; la animación de caminar depende del desplazamiento real."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from animation import pose
bpy.ops.wm.open_mainfile(filepath=str(B/'Distrito_Comercial_R6.blend'));scene=bpy.context.scene;scene.name='LifeR6_Shopping';scene.render.fps=24;scene.frame_start=1;scene.frame_end=2160
catalog=json.loads((B/'animation_catalog.json').read_text());civils=[c for c in catalog if c['group']=='civil'];trace=json.loads((B/'preview_traces.json').read_text());district=json.loads((B/'district.json').read_text())
names=set()
for row in civils:names.update(row['objects']+[row['rig'],row['grip'],row['bag']])
with bpy.data.libraries.load(str(B/'Elenco_Animado_R6.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in names]
sources={o.name:o for o in dst.objects}
with bpy.data.libraries.load(str(B/'Productos_Compra_R6.blend'),link=False) as (src,dst):dst.meshes=['JuiceCarton','JewelryBox','FoodBox','CashNote','Receipt']
roots=[];rigs=[];grips=[];copies=[]
def key_visibility(obj,visible,frame):
    obj.hide_render=not visible;obj.hide_viewport=not visible;obj.keyframe_insert(data_path='hide_render',frame=frame);obj.keyframe_insert(data_path='hide_viewport',frame=frame)
def linear(obj):
    if not obj.animation_data:return
    action=obj.animation_data.action
    if action:
        for curve in action.fcurves:
            for key in curve.keyframe_points:key.interpolation='LINEAR' if curve.data_path not in ['hide_render','hide_viewport'] else 'CONSTANT'
def clone(row,label):
    copied={}
    for name in row['objects']+[row['rig'],row['grip'],row['bag']]:
        src=sources[name];obj=src.copy();obj.name=label+'_'+name;scene.collection.objects.link(obj);copied[src]=obj
    root=bpy.data.objects.new(label,None);scene.collection.objects.link(root)
    for src,obj in copied.items():
        if src.parent in copied:obj.parent=copied[src.parent]
        for mod in obj.modifiers:
            if mod.type=='ARMATURE' and mod.object in copied:mod.object=copied[mod.object]
    rig=copied[sources[row['rig']]];rig.parent=root;rig.animation_data_clear();rig.animation_data_create();grip=copied[sources[row['grip']]];bag=copied[sources[row['bag']]]
    actions={mode:bpy.data.actions[row['rig']+'_'+mode] for mode in row['clips']}
    track=rig.animation_data.nla_tracks.new();track.name='IdleBase';strip=track.strips.new('IdleBase',1,actions['Idle']);strip.repeat=45;strip.frame_end=2161
    return root,rig,grip,bag,actions
for index in range(24):
    shop=district['shops'][index//8];variant=(index%8+(index//8)*3)%10
    if variant==shop['staffVariant']:variant=(variant+1)%10
    row=civils[variant];root,rig,grip,bag,actions=clone(row,'R6_Resident_'+str(index));roots.append(root);rigs.append(rig);grips.append(grip);copies.append({'root':root.name,'rig':rig.name,'grip':grip.name,'actor':index,'shop':shop['id']})
    track=rig.animation_data.nla_tracks.new();track.name='Task';rows=trace['actors'][index][:2160];begin=1;mode=rows[0]['mode']
    for sample in rows[1:]+[{'frame':2161,'mode':'END'}]:
        if sample['mode']==mode:continue
        if mode!='Idle':
            action=actions[mode];strip=track.strips.new(mode,begin,action);strip.repeat=max(.01,(sample['frame']-begin)/(action.frame_range[1]-action.frame_range[0]));strip.frame_end=sample['frame'];strip.extrapolation='NOTHING';strip.blend_in=min(2,(sample['frame']-begin)/3);strip.blend_out=min(2,(sample['frame']-begin)/3)
        begin=sample['frame'];mode=sample['mode']
    previous_bag=None
    for sample in rows:
        frame=sample['frame'];root.location=sample['position'];root.rotation_euler.z=sample['yaw'];root.keyframe_insert(data_path='location',frame=frame);root.keyframe_insert(data_path='rotation_euler',frame=frame)
        if sample['carrying']!=previous_bag:key_visibility(bag,sample['carrying'],frame);previous_bag=sample['carrying']
    linear(root)
    # Producto y dinero son objetos independientes; sus transferencias se hornean desde las mismas fases.
    product=bpy.data.objects.new('R6_Product_'+str(index),bpy.data.meshes[shop['product']]);scene.collection.objects.link(product)
    cash=bpy.data.objects.new('R6_Money_'+str(index),bpy.data.meshes['CashNote']);scene.collection.objects.link(cash)
    receipt=bpy.data.objects.new('R6_Receipt_'+str(index),bpy.data.meshes['Receipt']);scene.collection.objects.link(receipt)
    copies[-1].update({'product':product.name,'cash':cash.name,'receipt':receipt.name})
    if index%8>=4:
        for obj in [product,cash,receipt]:key_visibility(obj,False,1)
for index,shop in enumerate(district['shops']):
    row=civils[shop['staffVariant']];root,rig,grip,bag,actions=clone(row,'R6_Cashier_'+str(index));root.location=(shop['center'][0]+shop['staff'][0],shop['staff'][1],.16);root.rotation_euler.z=shop['staffYaw'];bag.hide_render=bag.hide_viewport=True
    track=rig.animation_data.nla_tracks.new();track.name='Service'
    for event in trace['events']:
        if event['actor']//8!=index or event['action'] not in ['Placed','Paid']:continue
        begin=int(event['time']*24)+1
        if begin>2130:continue
        # Los eventos de un mismo cliente pueden solaparse; una banda continua evita tirones y tiras duplicadas.
        if track.strips and begin<track.strips[-1].frame_end:continue
        strip=track.strips.new('ScanAndCollect',begin,actions['Pay']);strip.frame_end=begin+32;strip.extrapolation='NOTHING';strip.blend_in=3;strip.blend_out=3
    copies.append({'root':root.name,'rig':rig.name,'grip':grip.name,'shop':shop['id'],'cashier':True})
cashiergrips={r['shop']:bpy.data.objects[r['grip']] for r in copies if r.get('cashier')}
for frame in range(1,2161):
    scene.frame_set(frame);bpy.context.view_layer.update()
    for index in range(24):
        if index%8>=4:continue
        row=trace['actors'][index][frame-1];shop=district['shops'][index//8];root=roots[index];grip=grips[index];stage=row['stage'];state=row['state'];station=row['station']
        product=bpy.data.objects['R6_Product_'+str(index)];cash=bpy.data.objects['R6_Money_'+str(index)];receipt=bpy.data.objects['R6_Receipt_'+str(index)]
        visible=stage in ['Reserved','InHand','OnCounter','Scanned','Paid']
        if stage=='Reserved':product.location=Vector(shop['products'][station])+Vector(shop['center'])
        elif stage=='InHand':product.matrix_world=grip.matrix_world
        elif stage=='Scanned':product.matrix_world=cashiergrips[shop['id']].matrix_world
        else:product.location=Vector(shop['counter'])+Vector(shop['center']);product.rotation_euler=(0,0,0)
        key_visibility(product,visible,frame)
        if visible:product.keyframe_insert(data_path='location',frame=frame);product.keyframe_insert(data_path='rotation_euler',frame=frame)
        cash_visible=state in ['Paying','ReceivingReceipt'];cash.matrix_world=grip.matrix_world if state=='Paying' else cashiergrips[shop['id']].matrix_world
        key_visibility(cash,cash_visible,frame)
        if cash_visible:cash.keyframe_insert(data_path='location',frame=frame);cash.keyframe_insert(data_path='rotation_euler',frame=frame)
        receipt_visible=state in ['ReceivingReceipt','Collecting'];receipt.location=Vector(shop['receipt'])+Vector(shop['center']);key_visibility(receipt,receipt_visible,frame)
    for shop in district['shops']:
        near=any(math.hypot(trace['actors'][i][frame-1]['position'][0]-shop['center'][0],trace['actors'][i][frame-1]['position'][1]+5.12)<2.2 for i in range(24))
        for leaf in ['L','R']:
            door=bpy.data.objects['Door_'+shop['id']+'_'+leaf];base=0 if leaf=='L' else math.pi;target=base+((-1 if leaf=='L' else 1)*1.309 if near else 0)
            door.rotation_euler.z += max(-.10,min(.10,target-door.rotation_euler.z));door.keyframe_insert(data_path='rotation_euler',frame=frame)
for obj in scene.objects:linear(obj)
for shop in district['shops']:
    for j,point in enumerate(shop['products']):
        data=bpy.data.meshes[shop['product']];obj=bpy.data.objects.new('R6_ShelfStock_'+shop['id']+str(j),data);scene.collection.objects.link(obj);obj.location=Vector(point)+Vector(shop['center'])+Vector((.16,0,0))
# Cámaras de inspección: mercado, joyería y una vista próxima de caja.
def camera(name,target,offset,scale):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);target=Vector(target);obj.location=target+Vector(offset);obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;return obj
market=camera('R6_MarketCamera',(-18,-.2,.7),(7,-9,10),14);jewelry=camera('R6_JewelryCamera',(0,0,.7),(7,-9,10),14);close=camera('R6_CheckoutCamera',(-15.0,-2.7,1),(3.7,1.5,2.7),5)
for f,cam in [(1,scene.camera),(241,market),(721,close),(1100,jewelry),(1600,market)]:marker=scene.timeline_markers.new('Review_'+str(f),frame=f);marker.camera=cam
scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=24
for obj in scene.objects:
    if obj.name.startswith('Roof_'):obj.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.overlay.show_overlays=False;area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
(B/'preview_catalog.json').write_text(json.dumps(copies,indent=2))
scene.frame_set(740);bpy.ops.wm.save_as_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'),compress=True)
for frame,cam,name in [(480,market,'Mercado_Fila_R6'),(800,close,'Caja_Manos_R6'),(1200,jewelry,'Joyeria_R6')]:
    scene.frame_set(frame);scene.camera=cam;scene.render.filepath=str(B/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
print('SHOPPING_PREVIEW_READY',len(copies),'actors',flush=True)
