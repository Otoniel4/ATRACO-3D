"""Hojas originales para accesos modernos: cristal, marco, zócalo y tiradores visibles."""
import bpy,json,sys
from pathlib import Path
from review_sources import r6,r7,map1,map2
B=Path(__file__).resolve().parent;sys.path.insert(0,str(r6()));from fbx_utils import export
bpy.ops.wm.read_factory_settings(use_empty=True)
colors={'DoorR8_Frame':(.07,.12,.15,1),'DoorR8_Glass':(.24,.62,.68,.38),'DoorR8_Handle':(.66,.72,.72,1),'DoorR8_Kick':(.12,.23,.28,1)}
materials={}
for name,color in colors.items():
    m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color;materials[name]=m
def box(objects,name,location,size,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[material]);objects.append(o)
world=json.loads((r7()/'world.json').read_text())
for door in world['doors']:
    objects=[];w,h=(4.8,3.4) if door['single'] else (1.1,2.65)
    for x in [.035,w-.035]:box(objects,'DoorSide',(x,0,h/2),(.07,.10,h),'DoorR8_Frame')
    for z in [.045,h-.045]:box(objects,'DoorRail',(w/2,0,z),(w,.10,.09),'DoorR8_Frame')
    if door['single']:
        for i in range(1,11):box(objects,'ShutterSlat',(w/2,0,h*i/11),(w-.08,.08,.22),'DoorR8_Kick')
    else:
        box(objects,'Glass',(w/2,0,h/2),(w-.14,.035,h-.15),'DoorR8_Glass')
        box(objects,'KickPlate',(w/2,0,.15),(w-.1,.105,.24),'DoorR8_Kick')
        for y in [-.10,.10]:box(objects,'DoorHandle',(w-.17,y,1.22),(.035,.04,.36),'DoorR8_Handle')
    root=bpy.data.objects.new('Door_'+door['id'],None);bpy.context.scene.collection.objects.link(root)
    for o in objects:o.parent=root
    export(B/'export/Doors'/(door['id']+'.fbx'),[root]+objects)
    bpy.data.batch_remove(ids=tuple(objects+[root]))
(B/'door_materials.json').write_text(json.dumps({'materials':[{'name':name,'r':c[0],'g':c[1],'b':c[2],'a':c[3],'metallic':.3 if 'Glass' not in name else 0,'roughness':.4} for name,c in colors.items()]},indent=2))
print('DOORS_R8_EXPORTED',len(world['doors']),flush=True)
