"""Reimporta el lote y verifica los colliders de hojas frente a toda la estructura, en ambos sentidos."""
import itertools
import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ART=HERE.parents[2]
OUT=ART.parents[2]/'Library/Alarma/DoorReview36'
faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
ignored=('Detail_','FloorTiles','CeilingLight','Aisle','Sign','Awning','Rug','Runner','LoungeRug','CubicleRug','VipCarpet','BankStripe')
original=bpy.context.scene
report={}

for path in sorted((OUT/'City/Shops').glob('Local_*.fbx')):
    scene=bpy.data.scenes.new('Sweep_'+path.stem);bpy.context.window.scene=scene
    # Evitar que nombres de las escenas de revisión añadan sufijos al comparar hojas.
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    objects=set(bpy.data.objects)-before
    leaves=[next(o for o in objects if o.name.split('.')[0]=='DoorLeaf_'+side) for side in ('L','R')]
    moving=set(sum((list(l.children_recursive) for l in leaves),[]))
    static=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]))
            for o in objects if o.type=='MESH' and o not in moving and not o.name.startswith(ignored)]
    count=0
    for leaf in leaves:
        inv=leaf.matrix_world.inverted()
        structural=[o for o in leaf.children_recursive if o.type=='MESH' and not o.name.startswith(('DoorBar_','DoorHandle_','Detail_'))]
        points=[inv@(o.matrix_world@v.co) for o in structural for v in o.data.vertices]
        lo,hi=[Vector([fn(v[i] for v in points) for i in range(3)]) for fn in (min,max)]
        # Solo 1 mm para caras coplanares con el piso, frente a los 12 mm del runtime.
        for i in range(3):lo[i]+=.001;hi[i]-=.001
        box=[leaf.matrix_world@Vector(p) for p in itertools.product(*zip(lo,hi))]
        pivot=leaf.matrix_world.translation
        for angle in range(-85,86):
            rotation=Matrix.Rotation(math.radians(angle),3,'Z')
            query=BVHTree.FromPolygons([pivot+rotation@(p-pivot) for p in box],faces)
            hits=[name for name,tree in static if tree.overlap(query)]
            assert not hits,(path.stem,leaf.name,angle,hits)
            count+=1
    report[path.stem]={'full_box_sweep_samples':count,'both_directions':True}
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.window.scene=original
    bpy.data.scenes.remove(scene)

assert len(report)==7
(HERE/'sweep-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
