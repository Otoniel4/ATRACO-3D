"""Arranca únicamente la revisión local de Blender; sin descargas ni cambios de preferencias globales."""
import addon_utils
import bpy

addon_utils.modules_refresh()
if addon_utils.enable('blender_mcp') is None:
    raise RuntimeError('El complemento blender_mcp no está instalado')
for scene in bpy.data.scenes:
    for source in ('polyhaven', 'sketchfab', 'polypizza', 'hyper3d', 'hunyuan3d', 'meshy', 'tripo'):
        key = 'blendermcp_use_' + source
        if hasattr(scene, key):
            setattr(scene, key, False)
bpy.ops.blendermcp.start_server()
print('HIDEOUT_REVIEW_CONNECTED', bpy.app.version_string)
