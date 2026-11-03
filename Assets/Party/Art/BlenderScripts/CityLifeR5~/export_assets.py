import bpy,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from fbx_utils import export
colors={}
def collect_colors():
    for mat in bpy.data.materials:
        rgba=mat.diffuse_color;metallic=0;roughness=.8
        if mat.use_nodes:
            node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if node:
                rgba=(*node.inputs['Base Color'].default_value[:3],node.inputs['Alpha'].default_value)
                metallic=node.inputs['Metallic'].default_value;roughness=node.inputs['Roughness'].default_value
        rgb=[v*12.92 if v<=.0031308 else 1.055*max(v,0)**(1/2.4)-.055 for v in rgba[:3]]
        colors[mat.name]={'name':mat.name,'r':rgb[0],'g':rgb[1],'b':rgb[2],'a':rgba[3],'metallic':metallic,'roughness':roughness}
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Objetos_Locales_R5.blend'));collect_colors()
scene=bpy.data.scenes.new('ExportProps');bpy.context.window.scene=scene
for row in json.loads((BASE/'prop_catalog.json').read_text()):
    obj=bpy.data.objects.new(row['id'],bpy.data.meshes[row['mesh']]);scene.collection.objects.link(obj)
    export(BASE/'export/Props'/(row['id']+'.fbx'),[obj]);bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Distrito_Comercial_R5.blend'));collect_colors()
root=bpy.data.objects['CityLifeR5_District'];export(BASE/'export/District_CityLife_R5.fbx',[root]+list(root.children_recursive))
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Civiles_Animados_R5.blend'));collect_colors()
catalog=json.loads((BASE/'animation_catalog.json').read_text())
for row in catalog:
    scene=bpy.data.scenes[row['scene']];bpy.context.window.scene=scene;rig=bpy.data.objects[row['rig']]
    rig.animation_data.action=None
    for track in rig.animation_data.nla_tracks:track.mute=False
    bag=bpy.data.objects[row['bag']];bag.hide_render=False;bag.hide_viewport=False
    export(BASE/'export/Characters'/(row['id']+'.fbx'),[o for o in scene.objects if o.type in ['MESH','ARMATURE']],True)
    for track in rig.animation_data.nla_tracks:track.mute=True
(BASE/'materials.json').write_text(json.dumps({'color_space':'sRGB material property values','materials':list(colors.values())},indent=2),encoding='utf-8')
(BASE/'unity_characters.json').write_text(json.dumps({'characters':[{'id':r['id'],'rig':r['rig']} for r in catalog]},indent=2),encoding='utf-8')
district=json.loads((BASE/'district.json').read_text())
for shop in district['shops']:
    for key in ['walk','entry','queue','exit']:shop[key]=[{'v':p} for p in shop[key]]
(BASE/'unity_district.json').write_text(json.dumps(district,indent=2),encoding='utf-8')
print('LIFE_R5_ASSETS_EXPORTED',len(json.loads((BASE/'prop_catalog.json').read_text())),'props',10,'animated characters',1,'district',flush=True)
