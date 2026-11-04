"""Exportación FBX común al kit y al suelo de la ciudad de 2 × 2 km: mismos ejes y escala para que Unity
los trate igual (frente del kit = -Y de Blender)."""
import bpy


def export(objects, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True,
                             global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=False, add_leaf_bones=False, mesh_smooth_type='FACE', colors_type='LINEAR', bake_anim=False)
