"""Contactos de mano horneados en una capa propia; no modifica piernas ni escala de huesos."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'));scene=bpy.context.scene
catalog=json.loads((B/'preview_catalog.json').read_text());district=json.loads((B/'district.json').read_text());trace=json.loads((B/'preview_traces.json').read_text());errors=[]
for entry in catalog:
    rig=bpy.data.objects[entry['rig']]
    for track in list(rig.animation_data.nla_tracks):
        if track.name.startswith('R6_HandContacts'):rig.animation_data.nla_tracks.remove(track)
    if entry.get('cashier'):
        shop=next(s for s in district['shops'] if s['id']==entry['shop']);bpy.data.objects[entry['root']].location=Vector(shop['staff'])+Vector(shop['center'])
def intervals(values):
    result=[];start=None;previous=None
    for index,value in enumerate(values+[None],1):
        if value!=previous:
            if previous is not None:result.append((start,index-1,previous))
            start=index;previous=value
    return result
def solve(rig,grip,target):
    target=rig.matrix_world.inverted()@target
    spine=rig.pose.bones['Spine'];pivot=spine.head.copy();direction=target-rig.pose.bones['RightUpperArm'].head;direction.z=0
    if direction.length>.001:
        from mathutils import Quaternion
        q=Quaternion(Vector((0,0,1)).cross(direction.normalized()),math.radians(16));spine.matrix=Matrix.Translation(pivot)@q.to_matrix().to_4x4()@Matrix.Translation(-pivot)@spine.matrix;bpy.context.view_layer.update()
    for iteration in range(9):
        for name in ['RightLowerArm','RightUpperArm']:
            bone=rig.pose.bones[name];pivot=bone.head.copy();point=rig.matrix_world.inverted()@grip.matrix_world.translation
            a=point-pivot;b=target-pivot
            if a.length<.00001 or b.length<.00001:continue
            q=a.rotation_difference(b);bone.matrix=Matrix.Translation(pivot)@q.to_matrix().to_4x4()@Matrix.Translation(-pivot)@bone.matrix;bpy.context.view_layer.update()
    return (grip.matrix_world.translation-rig.matrix_world@target).length
def bake(entry,segments):
    rig=bpy.data.objects[entry['rig']];grip=bpy.data.objects[entry['grip']]
    track=rig.animation_data.nla_tracks.new();track.name='R6_HandContacts'
    names=['Spine','RightUpperArm','RightLowerArm','RightHand']
    for serial,(begin,end,target) in enumerate(segments):
        if end-begin<4:continue
        action=bpy.data.actions.new(rig.name+'_Contact_'+str(serial));start=max(1,begin-3);finish=min(2160,end+3)
        for frame,reach in [(start,False),(min(begin+3,end),True),(max(begin+3,end-3),True),(finish,False)]:
            rig.animation_data.action=None;scene.frame_set(frame);bpy.context.view_layer.update()
            if reach:errors.append({'actor':entry['root'],'frame':frame,'error_m':solve(rig,grip,Vector(target))})
            rig.animation_data.action=action
            for name in names:bone=rig.pose.bones[name];bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=name)
        rig.animation_data.action=None;action.use_fake_user=True
        strip=track.strips.new('Contact_'+str(serial),start,action);strip.frame_end=finish;strip.extrapolation='NOTHING';strip.blend_in=2;strip.blend_out=2
for entry in catalog:
    shop=next(s for s in district['shops'] if s['id']==entry['shop']);centre=Vector(shop['center']);segments=[]
    if entry.get('cashier'):
        values=[]
        for frame in range(2160):
            serving=any(row[frame]['state'] in ['Scanning','Paying','ReceivingReceipt','Collecting'] for i,row in enumerate(trace['actors']) if i//8==district['shops'].index(shop))
            values.append('scan' if serving else None)
        segments=[(a,b,Vector(shop['scan'])+centre) for a,b,_ in intervals(values)]
    else:
        index=entry['actor'];rows=trace['actors'][index][:2160];values=[]
        for row in rows:
            values.append('shelf'+str(row['station']) if row['state']=='PickingUp' else 'counter' if row['state'] in ['Placing','Scanning','Paying','ReceivingReceipt','Collecting'] else None)
        for begin,end,kind in intervals(values):segments.append((begin,end,Vector(shop['counter'] if kind=='counter' else shop['products'][int(kind[5:])])+centre))
    bake(entry,segments)
    print('CONTACTS_BAKED',entry['root'],len(segments),flush=True)
# Vuelve a situar los objetos después de corregir los brazos. La cinta lleva el producto hasta el escáner.
staff={r['shop']:bpy.data.objects[r['grip']] for r in catalog if r.get('cashier')}
for frame in range(1,2161):
    scene.frame_set(frame);bpy.context.view_layer.update()
    for entry in catalog:
        if entry.get('cashier') or entry['actor']%8>=4:continue
        row=trace['actors'][entry['actor']][frame-1];shop=next(s for s in district['shops'] if s['id']==entry['shop']);centre=Vector(shop['center']);grip=bpy.data.objects[entry['grip']]
        product=bpy.data.objects[entry['product']];cash=bpy.data.objects[entry['cash']];stage=row['stage'];state=row['state'];elapsed=row['stateSeconds']
        if stage=='Reserved':product.location=Vector(shop['products'][row['station']])+centre;product.rotation_euler=(0,0,0)
        elif stage=='InHand':product.matrix_world=grip.matrix_world
        elif stage=='Scanned':product.matrix_world=staff[shop['id']].matrix_world
        else:
            p=Vector(shop['counter']);scan=Vector(shop['scan'])
            if stage=='OnCounter' and state=='Scanning':p=p.lerp(scan,min(1,elapsed/1.2))
            if stage=='Paid' and state=='ReceivingReceipt':p=scan.lerp(p,min(1,elapsed/.8))
            product.location=p+centre;product.rotation_euler=(0,0,0)
        if stage in ['Reserved','InHand','OnCounter','Scanned','Paid']:product.keyframe_insert(data_path='location',frame=frame);product.keyframe_insert(data_path='rotation_euler',frame=frame)
        if state in ['Paying','ReceivingReceipt']:
            cash.matrix_world=grip.matrix_world if state=='Paying' else staff[shop['id']].matrix_world;cash.keyframe_insert(data_path='location',frame=frame);cash.keyframe_insert(data_path='rotation_euler',frame=frame)
for obj in scene.objects:
    if obj.animation_data and obj.animation_data.action:
        for curve in obj.animation_data.action.fcurves:
            for key in curve.keyframe_points:key.interpolation='CONSTANT' if curve.data_path in ['hide_render','hide_viewport'] else 'LINEAR'
(B/'reach_validation.json').write_text(json.dumps({'contacts':errors,'maximum_error_m':max(e['error_m'] for e in errors),'no_bone_scaling':True},indent=2))
scene.frame_set(932);scene.camera=bpy.data.objects['R6_CheckoutCamera'];bpy.ops.wm.save_as_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'),compress=True)
bindings=[(marker,marker.camera) for marker in scene.timeline_markers]
for marker,cam in bindings:marker.camera=None
for frame,cam,name in [(895,'R6_MarketCamera','Mercado_Fila_R6'),(932,'R6_CheckoutCamera','Caja_Manos_R6'),(1200,'R6_JewelryCamera','Joyeria_R6')]:scene.frame_set(frame);scene.camera=bpy.data.objects[cam];scene.render.filepath=str(B/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
print('CONTACT_REVIEW_READY',max(e['error_m'] for e in errors),flush=True)
