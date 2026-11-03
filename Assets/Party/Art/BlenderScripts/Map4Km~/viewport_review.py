"""Captura OpenGL de revisión en una instancia aislada de Blender, sin tocar la sesión del artista."""
import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Villa_Alarma_4km.blend'))
def capture():
    try:
        if not bpy.context.window_manager.windows:return 1
        window=bpy.context.window_manager.windows[0]
        scene=bpy.data.scenes['Map4Km_Center'];window.scene=scene
        area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
        space=area.spaces.active
        assert 'CAMERA' in {i.identifier for i in bpy.types.RegionView3D.bl_rna.properties['view_perspective'].enum_items}
        space.clip_start=.1;space.clip_end=30000;space.overlay.show_overlays=False
        space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO'
        space.shading.show_shadows=True;space.shading.show_cavity=True
        space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
        space.region_3d.view_camera_offset=(0,0)
        scene.render.resolution_x=1600;scene.render.resolution_y=1244;scene.render.resolution_percentage=100
        scene.render.filepath=str(BASE/'renders/Viewport_Center.png');scene.render.image_settings.file_format='PNG'
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):
            bpy.ops.render.opengl(write_still=True,view_context=True)
        (BASE/'viewport_status.json').write_text(json.dumps({'captured':True,'blender':bpy.app.version_string,
            'method':'native viewport OpenGL, isolated process','file':'renders/Viewport_Center.png'}),encoding='utf-8')
        bpy.ops.wm.quit_blender()
    except Exception as error:
        (BASE/'viewport_status.json').write_text(json.dumps({'captured':False,'error':str(error)}),encoding='utf-8')
        bpy.ops.wm.quit_blender()
    return None
bpy.app.timers.register(capture,first_interval=3)
