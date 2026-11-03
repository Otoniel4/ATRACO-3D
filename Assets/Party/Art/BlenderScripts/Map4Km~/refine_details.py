"""Aplica los pequeños ajustes de revisión al archivo generado, sin reconstruir la ciudad."""
import bpy,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
from mesh_tools import Batch
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
scene=bpy.data.scenes['Map4Km_Overview'];bpy.context.window.scene=scene
config=json.loads((BASE/'map_config.json').read_text(encoding='utf-8'))
for name in config['palette']:
    M.INDEX[name]=len(M.MATERIALS);M.MATERIALS.append(bpy.data.materials['City4_'+name])
from urban_assets import make_modules
if bpy.data.meshes.get('Road_8m') is None:make_modules()
layout=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))
for obj in scene.objects:
    if obj.type=='MESH' and obj.name.startswith('Bridge_'):
        # Valores absolutos: repetir la corrección no ensancha ni baja otra vez el tablero.
        width=layout['lines'][int(obj.name.split('_')[1])]['width']+2.4
        for v in list(obj.data.vertices)[:8]:
            v.co.y=(1 if v.co.y>0 else -1)*width/2
            v.co.z=-.02 if v.co.z>-.2 else -.42
        obj.data.update()
def replace(name,batch):
    obj=bpy.data.objects[name];old=obj.data;old.name=name+'_BeforeDetail';obj.data=batch.data(name)
b=Batch();b.box((0,0,3.65),(1.7,1.4,.3),'cream');b.box((0,0,4.7),(1.5,1.2,2),'cream');b.text('LECHE',(0,-.62,4.7),.3,'coral');b.box((0,0,5.8),(1.6,1.3,.2),'coral');replace('MilkRoof',b)
b=Batch()
for x in [-6,-2,2,6]:b.cyl((x,-9,1.7),.35,3.4,'cream',10)
b.box((0,-8.2,3.65),(16,4,.35),'sand');b.cyl((0,0,5),1.5,.35,'gold',16,direction=(0,-1,0));b.text('$',(0,-.20,5),1.8,'cream');replace('BankColumnsCoin',b)
b=Batch();b.box((0,0,3.9),(1.2,1.2,.8),'cream');b.ico((0,0,5.1),(1.7,1.4,1.5),'glass',1);replace('RoofDiamond',b)
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
root=bpy.data.objects['VillaAlarma_4000m'];meshes=[o for o in root.children_recursive if o.type=='MESH']
manifest['evaluated_triangles']=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
print('MAP_DETAILS_REFINED')
