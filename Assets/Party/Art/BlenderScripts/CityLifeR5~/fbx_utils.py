"""Exportación propia con materiales por cara, ejes Unity y máscaras RGBA lineales."""
import bpy,io,contextlib,sys
class ExportLog(io.TextIOBase):
    def __init__(self):self.pending='';self.count=0
    def write(self,value):
        self.pending+=value
        while '\n' in self.pending:
            line,self.pending=self.pending.split('\n',1)
            if line.startswith('WARNING: Cannot register a valid material index'):self.count+=1
            else:print(line,file=sys.__stdout__)
        return len(value)
def export(path,objects,animated=False):
    path.parent.mkdir(parents=True,exist_ok=True);bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.hide_set(False);obj.select_set(True)
        if obj.type=='MESH':assert tuple(s.material for s in obj.material_slots)==tuple(obj.data.materials),obj.name
    bpy.context.view_layer.objects.active=next((o for o in objects if o.type=='ARMATURE'),objects[0]);log=ExportLog()
    with contextlib.redirect_stdout(log):
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY','ARMATURE'} if animated else {'MESH','EMPTY'},
            use_mesh_modifiers=animated,global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            bake_space_transform=False,add_leaf_bones=False,mesh_smooth_type='FACE',colors_type='LINEAR',bake_anim=animated,
            bake_anim_use_all_actions=False,bake_anim_use_nla_strips=animated,bake_anim_simplify_factor=0,bake_anim_step=1,use_custom_props=True)
    if log.count:print('SHARED_MATERIAL_NOTICES',log.count,'slots checked')
