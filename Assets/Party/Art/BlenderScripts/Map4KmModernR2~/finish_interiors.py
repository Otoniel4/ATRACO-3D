"""Ajuste local de las divisiones de celdas tras la revisión, sin regenerar toda la ciudad."""
import bpy,sys,json
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
import mesh_tools as M
import modern_assets as A
import hero_businesses as H
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
source=bpy.context.window.scene
for name in json.loads((BASE/'palette.json').read_text(encoding='utf-8')):
    material=bpy.data.materials.get('City4_'+name)
    if material:M.INDEX[name]=len(M.MATERIALS);M.MATERIALS.append(material)
work=bpy.data.scenes.new('InteriorCorrection');bpy.context.window.scene=work;H.make('Police')
target=bpy.data.objects['R2_Hero_Police_Furniture'];old=target.data;old.name='Before_Police_Furniture'
target.data=A.PROTOTYPES['Hero_Police_Furniture'];target.data.name='CityR2_Hero_Police_Furniture'
bpy.context.window.scene=source;bpy.data.scenes.remove(work)
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
root=bpy.data.objects['VillaAlarma_4000m'];meshes=[o for o in root.children_recursive if o.type=='MESH']
manifest['evaluated_triangles']=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Villa_Alarma_Modern_R2.blend'))
print('INTERIOR_FINISHED')
