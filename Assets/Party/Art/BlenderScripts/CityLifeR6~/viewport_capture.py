"""Captura de viewport nativo en un Blender aislado; no controla la instancia del usuario."""
import bpy,json
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Ciudad_Compras_R6.blend'))
def capture():
    try:
        window=bpy.context.window_manager.windows[0];scene=bpy.data.scenes['LifeR6_Shopping'];window.scene=scene
        for marker in scene.timeline_markers:marker.camera=None
        scene.frame_set(932);scene.camera=bpy.data.objects['R6_CheckoutCamera']
        for obj in scene.objects:
            if obj.name.startswith('Roof_'):obj.hide_set(True)
        area=next(a for a in window.screen.areas if a.type=='VIEW_3D');space=area.spaces.active;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO';space.overlay.show_overlays=False;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
        scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.filepath=str(B/'renders/Viewport_Compras_R6.png');region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
        report={'captured':True,'method':'native Blender viewport, isolated hidden process','frame':932,'version':bpy.app.version_string}
    except Exception as error:report={'captured':False,'error':str(error)}
    (B/'viewport_status.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(capture,first_interval=3)
