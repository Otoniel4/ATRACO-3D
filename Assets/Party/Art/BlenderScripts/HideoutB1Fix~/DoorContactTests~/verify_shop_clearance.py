"""Verifica el barrido de los FBX comerciales con el ajuste aplicado por City25Kit."""
import itertools
import math
import os
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
def mesh_tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                 [tuple(p.vertices) for p in obj.data.polygons])

folder = Path(os.environ.get("ALARMA_SHOP_FBX_REVIEW_DIR", "Assets/Party/Art/City/Shops"))
for f in sorted(folder.glob("Local_*.fbx")):
    if f.stem == "Local_Escondite": continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(f.resolve()))
    left, right = [next(o for o in bpy.data.objects if o.name.split(".")[0] == "DoorLeaf_" + side) for side in ("L","R")]
    for leaf in (left, right):
        for o in leaf.children_recursive:
            if o.name.startswith("DoorFrame_"):
                shifted = o.matrix_world.copy()
                shifted.translation.z -= .045
                o.matrix_world = shifted
    bpy.context.view_layer.update()
    moving = set(left.children_recursive + right.children_recursive)
    ignored = ("Detail_", "FloorTiles", "CeilingLight", "Aisle", "Sign", "Awning", "Rug", "Runner", "LoungeRug", "CubicleRug", "VipCarpet", "BankStripe")
    static = [(o.name,mesh_tree(o)) for o in bpy.data.objects if o.type == 'MESH' and o not in moving
              and not o.name.startswith(ignored)]
    for leaf in (left,right):
        pivot=leaf.matrix_world.translation
        inv=leaf.matrix_world.inverted()
        structural=[o for o in leaf.children_recursive if o.type=="MESH" and not o.name.startswith(("DoorBar_","Detail_"))]
        points=[inv @ (o.matrix_world @ v.co) for o in structural for v in o.data.vertices]
        lo,hi=[Vector([fn(v[i] for v in points) for i in range(3)]) for fn in (min,max)]
        if any(o.name.startswith("DoorFrame_") for o in leaf.children_recursive):
            local_width=leaf.matrix_world.to_3x3() @ Vector((1,0,0))
            trim=min((hi.x-lo.x)*.18,.14/local_width.length)
            if (lo.x+hi.x)>0: lo.x+=trim
            else: hi.x-=trim
        else:
            assert max(abs((leaf.matrix_world @ p).x) for p in points) < 1.10, leaf.name
        for axis in range(3):
            scale=leaf.matrix_world.to_scale()[axis]
            lo[axis]+=.012/scale
            hi[axis]-=.012/scale
        box=[leaf.matrix_world @ Vector(p) for p in itertools.product(*zip(lo,hi))]
        for direction in (-1,1):
            hits=[]
            for angle in range(1,86):
                rot=Matrix.Rotation(math.radians(direction*angle),3,'Z')
                query=BVHTree.FromPolygons([pivot+rot @ (v-pivot) for v in box],faces)
                names=[name for name,tree in static if tree.overlap(query)]
                if names:
                    hits.append((angle,names))
                    break
            print(f.stem, leaf.name, direction, hits or "clear")
            assert not hits
