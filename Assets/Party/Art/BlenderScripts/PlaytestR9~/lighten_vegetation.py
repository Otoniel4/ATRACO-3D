"""Aligera la vegetación de la ciudad R9 sin mover nada de sitio.

Árboles: de todos los LOD de cada especie se queda la reducción que conserva más superficie
de hojas dentro del presupuesto. Pasto: cada LOD se reduce solo si supera su presupuesto.
Follaje de macetas y jardineras: reducido.
Cada variante es una sola malla compartida por todas sus copias.
Lee Villa_Alarma_3000_R9.blend y guarda Villa_Alarma_3000_R9_Ligera.blend; el original no se modifica.
Uso: blender -b --factory-startup -P lighten_vegetation.py
Después: ALARMA_R9_WORLD=Villa_Alarma_3000_R9_Ligera.blend blender -b -P export_world.py
"""
import bpy, json, re, collections
from pathlib import Path

B = Path(__file__).resolve().parent
SOURCE = B / 'Villa_Alarma_3000_R9.blend'
TARGET = B / 'Villa_Alarma_3000_R9_Ligera.blend'

# Presupuestos ajustables. Subirlos da más hojas y más peso; volver a ejecutar tras cambiarlos.
TREE_BUDGET = 1800  # triángulos por árbol
GRASS_BUDGET = 600  # triángulos por mata de pasto; las más simples no se tocan
PLANT_RATIO = .15   # proporción que se conserva del follaje de macetas y jardineras


def tris(mesh):
    return sum(len(p.vertices) - 2 for p in mesh.polygons)


def foliage_area(mesh):
    # Las hojas son lo que se ve de lejos; tronco y tallos no cuentan.
    names = [m.name if m else '' for m in mesh.materials]
    return sum(p.area for p in mesh.polygons
               if p.material_index >= len(names) or not any(k in names[p.material_index] for k in ('Bark', 'Stem')))


def decimated(source, ratio):
    # El modificador Decimate conserva materiales y el atributo WindMask que usa el viento en Unity.
    temp = bpy.data.objects.new('Ligera_Temp', source)
    bpy.context.scene.collection.objects.link(temp)
    modifier = temp.modifiers.new('Ligera', 'DECIMATE')
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    mesh = bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    mesh.name = source.name + '_Ligera'
    bpy.data.objects.remove(temp)
    assert 'WindMask' in mesh.color_attributes or 'WindMask' not in source.color_attributes, mesh.name
    return mesh


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
root = bpy.data.objects['VillaAlarma_3000m']
objects = [o for o in root.children_recursive if o.type == 'MESH']
cache = {}
choice = {}


def best_lod(prefix, budget):
    # Un LOD detallado muy reducido suele conservar más hojas que uno simple; se mide en vez de suponerlo.
    if prefix not in cache:
        options = []
        for lod in sorted((m for m in bpy.data.meshes if re.fullmatch(re.escape(prefix) + r'_LOD\d', m.name)), key=lambda m: m.name):
            ratio = min(1, budget / max(1, tris(lod)))
            options.append(decimated(lod, ratio) if ratio < 1 else lod)
        cache[prefix] = max(options, key=foliage_area)
        for option in options:
            if option is not cache[prefix] and option.name.endswith('_Ligera'):
                bpy.data.meshes.remove(option)
        choice[prefix] = cache[prefix].name
    return cache[prefix]


def capped(mesh, budget):
    # Conserva cada variante y su reparto en el mapa; solo recorta las que superan el presupuesto.
    if mesh.name not in cache:
        ratio = budget / max(1, tris(mesh))
        cache[mesh.name] = decimated(mesh, ratio) if ratio < 1 else mesh
    return cache[mesh.name]


def replacement(mesh):
    name = mesh.name
    if name.startswith('PlantR4_CityGrass'):
        return 'grass', capped(mesh, GRASS_BUDGET)
    tree = re.match(r'(TreeR3_\w+?)_LOD\d$', name)
    if tree:
        return 'tree', best_lod(tree.group(1), TREE_BUDGET)
    if name.startswith('PlantR4_') and '_Foliage_' in name:
        key = (name, PLANT_RATIO)
        if key not in cache:
            cache[key] = decimated(mesh, PLANT_RATIO)
        return 'plant', cache[key]
    return None, mesh


before = collections.Counter(); after = collections.Counter(); count = collections.Counter(); object_slots = 0
for obj in objects:
    kind, mesh = replacement(obj.data)
    if kind is None:
        continue
    before[kind] += tris(obj.data); after[kind] += tris(mesh); count[kind] += 1
    object_slots += any(s.link == 'OBJECT' for s in obj.material_slots)
    obj.data = mesh

# El exportador FBX exige que los materiales vivan en la malla, no en el objeto.
assert object_slots == 0, f'{object_slots} objetos con materiales enlazados al objeto'
bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
total = sum(tris(o.data) for o in objects)
report = {
    'source': SOURCE.name, 'target': TARGET.name,
    'budgets': {'tree': TREE_BUDGET, 'grass': GRASS_BUDGET, 'plant_ratio': PLANT_RATIO},
    'chosen_meshes': choice,
    'objects': dict(count),
    'triangles_before': dict(before), 'triangles_after': dict(after),
    'city_triangles_after': total, 'unique_meshes_after': len({o.data for o in objects}),
}
(B / 'vegetation_lite.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET), compress=True)
print('VEGETATION_LITE', json.dumps(report), flush=True)
