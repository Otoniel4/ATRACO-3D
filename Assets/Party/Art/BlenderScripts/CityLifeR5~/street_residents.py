"""Dos paseantes adicionales por local, sobre la explanada pública delante de su puerta."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
def add_street_residents(collection):
    catalog=json.loads((BASE/'animation_catalog.json').read_text());manifest=json.loads((BASE/'baseline/city_manifest.json').read_text());added=0
    configured=json.loads((BASE/'interior_placements.json').read_text())
    for serial,poi in enumerate(p for p in manifest['pois'] if p['id']!='Minimarket' and p['id'] in configured):
        shop=poi['id'];hero=bpy.data.objects['R2_Hero_'+shop];depth=poi['r2_building']['depth']
        for i,index in enumerate([ [4,6,8][serial%3], [5,7][serial%2] ]):
            name=f'ResidentStreet_{shop}_{i}'
            if bpy.data.objects.get(name):continue
            source=bpy.data.objects['Resident_'+catalog[index]['id']];mapping={}
            for old in [source]+list(source.children_recursive):
                obj=old.copy();obj.name=name+'_'+old.name;collection.objects.link(obj);mapping[old]=obj
            for old,obj in mapping.items():
                if old.parent in mapping:obj.parent=mapping[old.parent]
                for modifier in obj.modifiers:
                    if modifier.type=='ARMATURE' and modifier.object in mapping:modifier.object=mapping[modifier.object]
            root=mapping[source];root.name=name;root.animation_data_clear()
            rig=next(o for o in mapping.values() if o.type=='ARMATURE');rig.animation_data_clear();rig.animation_data_create()
            prefix=catalog[index]['rig'];idle=bpy.data.actions[prefix+'_Idle'];walk=bpy.data.actions[prefix+'_Walk']
            track=rig.animation_data.nla_tracks.new();strip=track.strips.new('Idle',1,idle);strip.repeat=12;strip.frame_end=577
            track=rig.animation_data.nla_tracks.new()
            for f in range(1,577,120):
                end=min(577,f+96);strip=track.strips.new('Walk',f,walk);strip.repeat=(end-f)/24;strip.frame_end=end;strip.blend_in=3;strip.blend_out=3;strip.extrapolation='NOTHING'
            yaw=math.pi/2 if i==0 else -math.pi/2
            for f in range(1,577,2):
                t=((f-1)/24+(5 if i else 0))%10
                if t<4:x=-2+t;desired=math.pi/2
                elif t<5:x=2;desired=-math.pi/2
                elif t<9:x=2-(t-5);desired=-math.pi/2
                else:x=-2;desired=math.pi/2
                delta=(desired-yaw+math.pi)%math.tau-math.pi;yaw+=max(-3.5*2/24,min(3.5*2/24,delta))
                p=hero.matrix_world@Vector((x,-depth/2-2.4-i*.8,0));root.location=p;root.rotation_euler.z=yaw
                root.keyframe_insert(data_path='location',frame=f);root.keyframe_insert(data_path='rotation_euler',frame=f)
            root['PreviewScripted']=True;root['CharacterId']=catalog[index]['id'];added+=1
    return added
