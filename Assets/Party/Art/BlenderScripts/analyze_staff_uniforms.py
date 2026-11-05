"""Clasifica las prendas de los diez civiles del elenco para vestirlos con uniforme de empleado.

Mide, por material, el área y la altura media de sus caras en la pose de reposo: lo que cae en el torso es la parte
de arriba (camisa, chaqueta, chaleco) y lo que cae en las piernas es el pantalón o la falda. Piel, pelo, ojos,
cejas, aros, zapatos y la bolsa de compras se conservan.
Uso: blender -b --factory-startup -P analyze_staff_uniforms.py
Salida: Art/Characters/Cast/staff_uniform_slots.json
"""
import json
from pathlib import Path

import bpy

ART = Path(__file__).resolve().parent.parent
CAST = ART / "Characters" / "Cast"
KEEP = ("Skin", "Eyebrows", "Hair", "Eye", "Earrings", "Bag", "Brown.001")
TOP, BOTTOM = (.95, 1.65), (.3, .95)  # metros sobre el suelo


def measure(obj):
    data = {}
    world = obj.matrix_world
    for poly in obj.data.polygons:
        slot = obj.material_slots[poly.material_index].material if obj.material_slots else None
        if slot is None:
            continue
        area = poly.area * world.median_scale ** 2
        z = (world @ poly.center).z
        total, weighted = data.get(slot.name, (0.0, 0.0))
        data[slot.name] = (total + area, weighted + area * z)
    return {name: (area, weighted / area) for name, (area, weighted) in data.items() if area > 0}


models = {}
for path in sorted(CAST.glob("NPC*.fbx")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    body = next(o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("ShoppingBag_"))
    top, bottom = [], []
    for name, (area, height) in sorted(measure(body).items()):
        if any(k in name for k in KEEP) or area < .02:
            continue
        if TOP[0] <= height <= TOP[1]:
            top.append(name)
        elif BOTTOM[0] <= height < BOTTOM[1]:
            bottom.append(name)
        print("PRENDA", path.stem, name, round(area, 3), "m2", round(height, 2), "m")
    models[path.stem] = dict(top=top, bottom=bottom)
    print("UNIFORME", path.stem, "arriba", top, "abajo", bottom)
(CAST / "staff_uniform_slots.json").write_text(json.dumps(dict(models=[dict(model=k, **v) for k, v in models.items()]), indent=1), encoding="utf-8")
