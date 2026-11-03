"""Captura de viewport en un Blender aislado: cámara de caja, clientes y nuevos objetos."""
import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Ciudad_Viva_Demo_R5.blend'))
def capture():
    try:
        if not bpy.context.window_manager.windows:return 1
        window=bpy.context.window_manager.windows[0];scene=bpy.data.scenes['LifeR5_AnimatedDistrict'];window.scene=scene;scene.frame_set(260)
        scene.camera=bpy.data.objects['LifeR5_CheckoutCamera']
        for obj in scene.objects:
            if obj.name.startswith('Roof_'):obj.hide_set(True)
        area=next(a for a in window.screen.areas if a.type=='VIEW_3D');space=area.spaces.active
        space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO';space.shading.show_shadows=False;space.shading.show_cavity=False
        space.overlay.show_overlays=False;space.overlay.show_relationship_lines=False;space.clip_end=2000
        space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0;space.region_3d.view_camera_offset=(0,0)
        scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.filepath=str(BASE/'renders/Viewport_Ciudad_Viva_R5.png')
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.object.select_all(action='DESELECT');bpy.ops.render.opengl(write_still=True,view_context=True)
        report={'captured':True,'method':'native viewport OpenGL, isolated process','blender':bpy.app.version_string,'frame':260}
    except Exception as error:report={'captured':False,'error':str(error)}
    (BASE/'viewport_status.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(capture,first_interval=3)
