import bpy,json,math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_sources_r9 as sources9
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'Villa_Alarma_3000_R9.blend'));lines=json.loads((sources9.map1()/'layout.json').read_text(encoding='utf-8'))['lines'];minimum=1e9
for o in bpy.data.objects['VillaAlarma_3000m'].children_recursive:
    if o.type!='MESH' or not o.name.startswith('R9_'):continue
    for vertex in o.data.vertices:
        p=o.matrix_world@vertex.co
        for line in lines:
            ax,ay=line['a'];bx,by=line['b'];dx,dy=bx-ax,by-ay;t=max(0,min(1,((p.x-ax)*dx+(p.y-ay)*dy)/max(.001,dx*dx+dy*dy)));distance=math.hypot(p.x-ax-t*dx,p.y-ay-t*dy)-line['width']/2;minimum=min(minimum,distance)
assert minimum>.25,minimum
(B/'road_clearance.json').write_text(json.dumps({'passed':True,'minimum_new_geometry_clearance_from_road_m':minimum},indent=2));print('ROAD_CLEARANCE_PASS',minimum,flush=True)
