import bpy,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import props as P
bpy.ops.wm.open_mainfile(filepath=str(B/'Distrito_Comercial_R6.blend'));P.palette()
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('R6_FoodDisplay'):bpy.data.objects.remove(obj,do_unlink=True)
batch=P.Batch();batch.box((0,0,.47),(.32,.18,.94),'wood');batch.box((0,0,.925),(.36,.20,.05),'metal');batch.box((0,-.095,.55),(.24,.01,.24),'paper');batch.text('MENU',(0,-.102,.55),.045,'dark')
mesh=batch.data('PickupDisplay_R6');shop=next(s for s in json.loads((B/'district.json').read_text())['shops'] if s['id']=='Restaurant')
for i,point in enumerate(shop['products']):
    obj=bpy.data.objects.new('R6_FoodDisplay_'+str(i),mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=bpy.data.objects['Shop_Restaurant'];obj.location=(point[0],point[1],.16)
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Distrito_Comercial_R6.blend'),compress=True);print('FOOD_DISPLAYS_READY',flush=True)
