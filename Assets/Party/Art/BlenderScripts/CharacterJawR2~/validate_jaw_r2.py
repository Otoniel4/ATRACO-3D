"""Comprueba el alcance local y la geometría de la corrección mandibular."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils.kdtree import KDTree
args=sys.argv[sys.argv.index('--')+1:]
folder=Path(args[0]).resolve()
old=Path(args[1]).resolve() if len(args)>1 else folder/'baseline'
roles=['Body','Jacket','Top','Pants','Shoes','Hair','Earrings']
def load(path):
    bpy.ops.wm.open_mainfile(filepath=str(path/'character.blend'))
    scene=bpy.data.scenes['Character_Blockout_4x'];bpy.context.window.scene=scene
    return {name:[tuple(v.co) for v in scene.objects[name].data.vertices] for name in roles}
before=load(old);after=load(folder)
def max_distance(a,b):
    tree=KDTree(len(b))
    for i,p in enumerate(b):tree.insert(p,i)
    tree.balance()
    return max(tree.find(p)[2] for p in a)
scope={}
for name in roles:
    a,b=before[name],after[name]
    if name=='Body':
        cutoff=1.315*.9739211102411005+1e-7
        a=[p for p in a if p[2]<=cutoff];b=[p for p in b if p[2]<=cutoff]
    error=max(max_distance(a,b),max_distance(b,a))
    assert len(a)==len(b) and error<1e-6,(name,len(a),len(b),error)
    scope[name]={'compared_vertices':len(a),'max_change_m':error,'region':'below head-neck junction' if name=='Body' else 'whole object'}
body=bpy.context.scene.objects['Body'];bm=bmesh.new();bm.from_mesh(body.data)
info={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),
      'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
      'minimum_face_area_m2':min(f.calc_area() for f in bm.faces),
      'minimum_edge_length_m':min(e.calc_length() for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True)}
assert info['faces']==info['quads'] and info['nonmanifold_edges']==0
assert info['minimum_face_area_m2']>1e-12 and info['minimum_edge_length_m']>1e-7
assert info['signed_volume_m3']>0
bm.free()
assert all(math.isfinite(c) for p in after['Body'] for c in p)
result={'local_scope_passed':True,'body_geometry':info,'unchanged_regions':scope}
(folder/'jaw_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('JAW_VALIDATION_SUCCESS',json.dumps(info))
