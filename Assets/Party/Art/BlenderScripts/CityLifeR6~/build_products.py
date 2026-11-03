"""Productos, billete ambiental y recibo originales; ningún recurso descargado."""
import bpy,sys,json,math
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import props as P
bpy.ops.wm.read_factory_settings(use_empty=True);P.palette();scene=bpy.context.scene;scene.name='Products_R6';root=bpy.data.objects.new('Products_R6',None);scene.collection.objects.link(root)
def save(name,batch):
    obj=bpy.data.objects.new(name,batch.data(name));scene.collection.objects.link(obj);obj.parent=root;return obj
b=P.Batch();b.box((0,0,.06),(.075,.075,.12),'ivory');b.box((0,0,.125),(.075,.075,.02),'orange');b.box((0,-.038,.06),(.055,.002,.075),'green');b.cyl((.018,0,.147),.012,.018,'paper',n=8);save('JuiceCarton',b)
b=P.Batch();b.box((0,0,.018),(.10,.08,.036),'dark');b.box((0,0,.040),(.105,.085,.009),'gold');b.box((0,0,.047),(.077,.06,.006),'dark');b.ico((0,0,.060),(.012,.012,.012),'teal');save('JewelryBox',b)
b=P.Batch();b.box((0,0,.024),(.15,.11,.048),'ivory');b.box((0,0,.051),(.155,.115,.007),'orange');b.box((0,0,.056),(.09,.05,.003),'paper');save('FoodBox',b)
b=P.Batch();b.box((0,0,.002),(.13,.058,.004),'green');b.box((0,0,.0045),(.11,.043,.001),'ivory');b.ico((0,0,.006),(.018,.018,.001),'green');save('CashNote',b)
b=P.Batch();b.box((0,0,.001),(.055,.105,.002),'paper')
for i in range(5):b.box((0,-.037+i*.015,.0025),(.034,.003,.001),'dark')
save('Receipt',b)
bpy.ops.wm.save_as_mainfile(filepath=str(B/'Productos_Compra_R6.blend'),compress=True);print('PRODUCTS_READY',flush=True)
