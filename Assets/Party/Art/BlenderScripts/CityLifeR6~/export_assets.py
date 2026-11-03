"""ExportaciÃ³n reproducible para Unity: cuerpos propios, manos, cinco clips, productos y distrito."""
import bpy,json,sys,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from fbx_utils import export
from sources import previous_revision;old=previous_revision();colors={}
def collect():
    for mat in bpy.data.materials:
        rgba=mat.diffuse_color;metallic=0;roughness=.8
        if mat.use_nodes:
            n=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if n:rgba=(*n.inputs['Base Color'].default_value[:3],n.inputs['Alpha'].default_value);metallic=n.inputs['Metallic'].default_value;roughness=n.inputs['Roughness'].default_value
        rgb=[v*12.92 if v<=.0031308 else 1.055*max(v,0)**(1/2.4)-.055 for v in rgba[:3]];colors[mat.name]={'name':mat.name,'r':rgb[0],'g':rgb[1],'b':rgb[2],'a':rgba[3],'metallic':metallic,'roughness':roughness}
for file in (old/'export/Props').glob('*.fbx'):shutil.copy2(file,B/'export/Props'/file.name)
bpy.ops.wm.open_mainfile(filepath=str(B/'Productos_Compra_R6.blend'));collect()
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH':export(B/'export/Props'/(obj.name+'.fbx'),[obj])
bpy.ops.wm.open_mainfile(filepath=str(B/'Distrito_Comercial_R6.blend'));collect();root=bpy.data.objects['CityLifeR6_District'];export(B/'export/District_CityLife_R6.fbx',[root]+list(root.children_recursive))
bpy.ops.wm.open_mainfile(filepath=str(B/'Elenco_Animado_R6.blend'));collect();catalog=json.loads((B/'animation_catalog.json').read_text())
for row in catalog:
    scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']];rig.animation_data.action=None
    for track in rig.animation_data.nla_tracks:track.mute=False
    bpy.data.objects[row['bag']].hide_render=False;bpy.data.objects[row['bag']].hide_viewport=False
    export(B/'export/Characters'/(row['id']+'.fbx'),[o for o in scene.objects if o.type in ['MESH','ARMATURE','EMPTY']],True)
    for track in rig.animation_data.nla_tracks:track.mute=True
(B/'materials.json').write_text(json.dumps({'color_space':'sRGB','materials':list(colors.values())},indent=2))
(B/'unity_characters.json').write_text(json.dumps({'characters':[{'id':r['id'],'rig':r['rig']} for r in catalog if r['group']=='civil']},indent=2))
support=old/'Unity/SharedSupport~'
if support.exists():shutil.copytree(support,B/'Unity/SharedSupport~',dirs_exist_ok=True)
print('ASSETS_EXPORTED',len(catalog),'characters; 37 props; district',flush=True)
