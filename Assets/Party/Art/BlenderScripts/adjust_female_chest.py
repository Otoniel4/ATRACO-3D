"""Aumento leve y reversible del pecho femenino; no modifica las otras proporciones."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ART=Path(r'C:\Users\Alain\Atraco3D\Assets\Party\Art')
OUT=Path(r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Ajuste-Pecho-Femenino');OUT.mkdir(exist_ok=True)
scene=bpy.data.scenes['BodyBases_Refined'];bpy.context.window.scene=scene;scene.frame_set(1)
body=bpy.data.objects['FemaleBase_Refined'];male=bpy.data.objects['MaleBase_Refined']
male_before=[tuple(v.co) for v in male.data.vertices]
if body.data.shape_keys is None:body.shape_key_add(name='Basis')
basis=body.data.shape_keys.reference_key
key=body.data.shape_keys.key_blocks.get('ChestVolume_Slight') or body.shape_key_add(name='ChestVolume_Slight')
changed=[]
for i,(point,base) in enumerate(zip(key.data,basis.data)):
 point.co=base.co.copy();x,y,z=base.co
 if 1.15<z<1.39 and abs(x)<.19 and y<-.025:
  weight=math.exp(-((abs(x)-.075)/.055)**2-((z-1.275)/.06)**2)
  delta=.045*weight*min(1,max(0,-y/.105))
  point.co.y-=delta
  if delta>1e-6:changed.append((i,delta))
key.value=1
def capture(label,direction,before=False):
 key.value=0 if before else 1
 body.hide_set(False);male.hide_set(True);scene.frame_set(1);bpy.context.view_layer.update()
 center=Vector((-.65,0,.88));scene.camera.location=center+Vector(direction)
 scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.05
 scene.render.resolution_x=800;scene.render.resolution_y=1050;scene.render.filepath=str(OUT/(label+'.png'))
 area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
 with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=False)
capture('Perfil-antes',(-5,0,.02),True)
capture('Perfil-ajustado',(-5,0,.02))
capture('Frente-ajustado',(0,-5,.02))
capture('Tres-cuartos',(3,-6,.6))
key.value=1;body.hide_set(False);male.hide_set(False)
center=Vector((0,0,.90));scene.camera.location=center+Vector((0,-5,.03));scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=3.2
scene.render.resolution_x=1500;scene.render.resolution_y=1050
scene.render.filepath=r'C:\Users\Alain\Documents\Codex\2026-10-31\pued\outputs\Bases-Corporales\Both-Front.png'
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=False)
assert male_before==[tuple(v.co) for v in male.data.vertices]
report={'modified_female_control_vertices':len(changed),'max_control_displacement_m':max(d for _,d in changed),'male_geometry_unchanged':True,'shape_key':'ChestVolume_Slight','value':key.value,'scope':'Only the front chest region of the female base'}
(OUT/'Ajuste.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(ART/'BlenderSources~/BodyBases_Refined.blend'),{scene},fake_user=True)
print('FEMALE_CHEST_ADJUSTED',json.dumps(report))
