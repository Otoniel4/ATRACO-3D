import bpy,json,sys,math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Vector
B=Path(__file__).resolve().parent;sys.path.insert(0,str(sources9.r6()));import mesh_tools as M;from mesh_tools import Batch;from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(B/'Villa_Alarma_3000_R9.blend'))
colors={'cream':'E9DFC9','white':'F5F1E8','denim':'4A6FA5','coral':'DC7662','teal':'3F888D','gold':'D6AF52','wood':'AD805A','dark':'253C46','metal':'8C9EA4','glass':'91D4DE','floor':'C8CCC4','green':'759864','milk':'E9E9DC','red':'CE5852','blue':'477EB1','purple':'9E82B8','asphalt':'52616A'}
for name,value in colors.items():
    rgb=[int(value[i:i+2],16)/255 for i in [0,2,4]];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    material=bpy.data.materials.new('R9Props_'+name);material.use_nodes=True;material.diffuse_color=(*linear,.22 if name=='glass' else 1);node=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(*linear,1);node.inputs['Alpha'].default_value=.22 if name=='glass' else 1;node.inputs['Roughness'].default_value=.7;M.INDEX[name]=len(M.MATERIALS);M.MATERIALS.append(material)
(B/'prop_materials.json').write_text(json.dumps({'materials':[{'name':'R9Props_'+name,'r':int(value[0:2],16)/255,'g':int(value[2:4],16)/255,'b':int(value[4:6],16)/255,'a':.22 if name=='glass' else 1,'metallic':.5 if name=='metal' else 0,'roughness':.7} for name,value in colors.items()]},indent=2))
scene=bpy.data.scenes.new('R9_GoodsAndDoors');bpy.context.window.scene=scene
def save(name,batch,kind):
    root=bpy.data.objects.new(name,None);scene.collection.objects.link(root);mesh=bpy.data.objects.new(name+'_Mesh',batch.data(name));scene.collection.objects.link(mesh);mesh.parent=root;objects=[root,mesh]
    for label,p in [('Origin',(0,0,0)),('X',(1,0,0)),('Front',(0,-1,0))]:
        obj=bpy.data.objects.new('R9_Anchor_'+label,None);scene.collection.objects.link(obj);obj.parent=root;obj.location=p;objects.append(obj)
    export(B/'export'/kind/(name+'.fbx'),objects);bpy.data.batch_remove(ids=tuple(objects))
for name in ['MilkCarton','CoffeeCup','JewelryBox','FoldedShirt','ToolKit','CashNote','Receipt']:
    b=Batch()
    if name=='MilkCarton':b.box((0,0,.13),(.15,.13,.26),'milk');b.box((0,-.067,.12),(.13,.006,.09),'blue');b.cyl((.04,0,.275),.027,.025,'blue',8)
    elif name=='CoffeeCup':b.cyl((0,0,.10),.085,.20,'white',12,top=.10);b.cyl((0,0,.205),.10,.012,'dark',12);b.box((.115,0,.11),(.07,.035,.11),'white')
    elif name=='JewelryBox':b.box((0,0,.04),(.25,.20,.08),'purple');b.cyl((0,0,.095),.045,.025,'gold',10);b.ico((0,0,.125),(.035,.035,.045),'glass',1)
    elif name=='FoldedShirt':b.box((0,0,.045),(.27,.23,.09),'coral');b.box((0,-.015,.098),(.08,.04,.014),'white')
    elif name=='ToolKit':b.box((0,0,.09),(.30,.17,.18),'teal');b.box((0,0,.20),(.13,.03,.035),'dark')
    elif name=='CashNote':b.box((0,0,.004),(.20,.09,.008),'green')
    elif name=='Receipt':b.box((0,0,.003),(.08,.15,.006),'white')
    save(name,b,'Props')
for name,w,h in [('DoubleLeaf120',1.2,2.8),('DoubleLeaf110',1.1,2.65),('Shutter',4.8,2.65)]:
    b=Batch()
    for x in [.035,w-.035]:b.box((x,0,h/2),(.07,.10,h),'dark')
    for z in [.045,h-.045]:b.box((w/2,0,z),(w,.10,.09),'dark')
    if name=='Shutter':
        for i in range(1,11):b.box((w/2,0,h*i/11),(w-.08,.08,.20),'teal')
    else:
        b.box((w/2,0,h/2),(w-.14,.035,h-.15),'glass');b.box((w/2,0,.15),(w-.1,.105,.24),'teal')
        for y in [-.10,.10]:b.box((w-.17,y,1.22),(.035,.04,.36),'metal')
    save(name,b,'Doors')
print('R9_GOODS_DOORS_READY',flush=True)
