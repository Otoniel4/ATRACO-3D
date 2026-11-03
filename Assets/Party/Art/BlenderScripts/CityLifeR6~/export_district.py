import bpy,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from fbx_utils import export
bpy.ops.wm.open_mainfile(filepath=str(B/'Distrito_Comercial_R6.blend'));root=bpy.data.objects['CityLifeR6_District'];export(B/'export/District_CityLife_R6.fbx',[root]+list(root.children_recursive));print('DISTRICT_EXPORT_UPDATED',flush=True)
