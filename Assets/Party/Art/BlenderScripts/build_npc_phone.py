"""Celular de los NPC (testigo que graba y llama; Task 13 y 19): modelo low-poly de colores planos para la mano.

De pie y a escala real (7,4 × 15,2 × 0,9 cm): ancho en X, alto en Z y la pantalla mirando a -Y (en Unity: alto en Y y
pantalla hacia +Z). Origen en el centro. Piezas, todas placas de esquinas redondeadas en una sola malla:
  funda de color, marco y vidrio oscuros, pantalla con la cámara abierta (punto rojo de grabación y disparador),
  isla de cámaras con dos lentes y flash, logo y botones laterales.
El color de la funda cambia por personaje: Unity lo elige de «cases» en el json (NpcReactionAssets.MakePhone).
Uso: blender -b --factory-startup -P build_npc_phone.py   (o desde Blender por MCP, en una escena nueva)
Salida: Art/Props/Prop_NpcPhone.fbx, Prop_NpcPhone.json (colores), BlenderSources~/Alarma_NpcPhone.blend y la captura
docs/Capturas/npc_Celular.png (frente y dorso).
"""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ART = HERE.parent
NAME = 'Prop_NpcPhone'
OUT = ART / 'Props' / f'{NAME}.fbx'
SHOT = ART.parent / 'docs' / 'Capturas' / 'npc_Celular.png'
# Material → color sRGB. «unlit»: brilla igual de día y de noche (pantalla encendida).
COLORS = {
    'Celular_Funda': ('2F6F8F', False), 'Celular_Marco': ('15171A', False), 'Celular_Pantalla': ('5FB4DF', True),
    'Celular_Rec': ('E5484D', True), 'Celular_Claro': ('F2EBD6', True), 'Celular_Cristal': ('3A4F66', False),
    'Celular_Lente': ('0B0D10', False),
}
CASES = ['2F6F8F', 'C9684F', 'E6BB55', '87A885', 'A15A78', '2B2930', 'F2EBD6']  # fundas: una por personaje


def linear(hex_color):
    def channel(v):
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return tuple(channel(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4))


def material(name):
    found = bpy.data.materials.get(name)
    if found:
        return found
    color = (*linear(COLORS[name][0]), 1)
    made = bpy.data.materials.new(name)
    made.diffuse_color = color
    made.use_nodes = True
    shader = next(n for n in made.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .6
    return made


def outline(width, height, radius, steps):
    # Rectángulo de esquinas redondeadas en XZ (radius = mitad del lado: círculo), en sentido antihorario visto de frente.
    radius = min(radius, width / 2, height / 2)
    points = []
    for corner, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        cx, cz = sx * (width / 2 - radius), sz * (height / 2 - radius)
        for i in range(steps + 1):
            angle = math.radians(corner * 90 + 90 * i / steps)
            points.append((cx + radius * math.cos(angle), cz + radius * math.sin(angle)))
    clean = []
    for p in points:  # en un círculo las esquinas comparten puntos
        if not clean or (Vector(p) - Vector(clean[-1])).length > 1e-6:
            clean.append(p)
    if (Vector(clean[0]) - Vector(clean[-1])).length < 1e-6:
        clean.pop()
    return clean


def slab(mesh, slots, name, size, y, center=(0, 0), radius=.002, steps=2):
    # Placa entre y[0] (frente) e y[1] (dorso), con su material.
    index = slots.index(name)
    ring = outline(size[0], size[1], radius, steps)
    front = [mesh.verts.new((center[0] + x, y[0], center[1] + z)) for x, z in ring]
    back = [mesh.verts.new((center[0] + x, y[1], center[1] + z)) for x, z in ring]
    faces = [mesh.faces.new(front), mesh.faces.new(list(reversed(back)))]
    count = len(ring)
    for i in range(count):
        faces.append(mesh.faces.new((front[(i + 1) % count], front[i], back[i], back[(i + 1) % count])))
    for face in faces:
        face.material_index = index


def build():
    slots = list(COLORS)
    mesh = bmesh.new()
    disc = dict(steps=3)
    slab(mesh, slots, 'Celular_Funda', (.074, .152), (-.0045, .0045), radius=.010, steps=3)
    # Frente: marco de vidrio, pantalla con la app de cámara (muesca, punto rojo «grabando» y disparador).
    slab(mesh, slots, 'Celular_Marco', (.0705, .1485), (-.0052, -.0045), radius=.0085, steps=3)
    slab(mesh, slots, 'Celular_Pantalla', (.064, .139), (-.0056, -.0052), radius=.006)
    slab(mesh, slots, 'Celular_Marco', (.020, .0052), (-.0059, -.0056), center=(0, .0625), radius=.0026)
    slab(mesh, slots, 'Celular_Rec', (.0085, .0085), (-.0059, -.0056), center=(.0235, .0535), radius=.00425, **disc)
    slab(mesh, slots, 'Celular_Marco', (.064, .030), (-.0058, -.0056), center=(0, -.0545), radius=.006)  # barra de la app
    slab(mesh, slots, 'Celular_Claro', (.019, .019), (-.0061, -.0058), center=(0, -.054), radius=.0095, **disc)
    slab(mesh, slots, 'Celular_Rec', (.012, .012), (-.0064, -.0061), center=(0, -.054), radius=.006, **disc)
    slab(mesh, slots, 'Celular_Claro', (.009, .009), (-.0061, -.0058), center=(.022, -.054), radius=.002)  # galería
    # Dorso: isla con dos lentes y flash, y un logo redondo.
    slab(mesh, slots, 'Celular_Marco', (.031, .034), (.0045, .0062), center=(.0165, .053), radius=.008, steps=3)
    for z in (.0605, .0455):
        slab(mesh, slots, 'Celular_Cristal', (.0125, .0125), (.0062, .0072), center=(.0125, z), radius=.00625, **disc)
        slab(mesh, slots, 'Celular_Lente', (.0065, .0065), (.0072, .0076), center=(.0125, z), radius=.00325, **disc)
    slab(mesh, slots, 'Celular_Claro', (.005, .005), (.0062, .0068), center=(.0245, .053), radius=.0025, **disc)
    slab(mesh, slots, 'Celular_Marco', (.014, .014), (.0045, .0049), center=(0, -.008), radius=.007, **disc)
    # Botones: encendido a un lado, volumen al otro (de frente, -X es la derecha de quien lo mira).
    slab(mesh, slots, 'Celular_Marco', (.003, .017), (-.0015, .0015), center=(-.0372, .022), radius=.001, steps=1)
    slab(mesh, slots, 'Celular_Marco', (.003, .026), (-.0015, .0015), center=(.0372, .028), radius=.001, steps=1)
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    data = bpy.data.meshes.new(NAME + '_Mesh')
    mesh.to_mesh(data)
    mesh.free()
    for name in slots:
        data.materials.append(material(name))
    phone = bpy.data.objects.new(NAME, data)
    bpy.context.scene.collection.objects.link(phone)
    return phone


def export(phone):
    for o in bpy.context.scene.objects:
        o.select_set(o == phone)
    bpy.context.view_layer.objects.active = phone
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Mismos ajustes que el resto de los props (alarmart.export_asset).
    bpy.ops.export_scene.fbx(filepath=str(OUT), use_selection=True, object_types={'MESH'}, global_scale=1.0,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
                             use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
    triangles = sum(len(p.vertices) - 2 for p in phone.data.polygons)
    manifest = dict(model=OUT.name, size_m=[round(v, 4) for v in phone.dimensions], triangles=triangles,
                    caseMaterial='Celular_Funda', cases=CASES,
                    materials=[dict(name=name, color=color, unlit=unlit) for name, (color, unlit) in COLORS.items()])
    OUT.with_suffix('.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    source = ART / 'BlenderSources~' / 'Alarma_NpcPhone.blend'
    source.parent.mkdir(exist_ok=True)
    bpy.data.libraries.write(str(source), {phone}, fake_user=True)
    return triangles


def capture(phone):
    # Frente y dorso lado a lado, sobre fondo claro.
    scene = bpy.context.scene
    back = phone.copy()
    scene.collection.objects.link(back)
    phone.location, back.location = (-.055, 0, 0), (.055, 0, 0)
    phone.rotation_euler, back.rotation_euler = (0, 0, math.radians(-22)), (0, 0, math.radians(180 - 22))
    cam = bpy.data.objects.new('Camara_Celular', bpy.data.cameras.new('Camara_Celular'))
    scene.collection.objects.link(cam)
    cam.data.lens = 70
    cam.location = (0, -.62, .1)
    cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    old = (scene.camera, scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath, scene.world)
    world = bpy.data.worlds.new('Fondo_Celular')
    world.color = (.66, .74, .82)
    scene.camera, scene.render.engine, scene.world = cam, 'BLENDER_WORKBENCH', world
    scene.render.resolution_x, scene.render.resolution_y = 1000, 800
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_object_outline = True
    scene.render.filepath = str(SHOT)
    SHOT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    scene.camera, scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath, scene.world = old
    bpy.data.objects.remove(back, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.worlds.remove(world)
    phone.location, phone.rotation_euler = (0, 0, 0), (0, 0, 0)


def main():
    old = bpy.data.objects.get(NAME)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    phone = build()
    bpy.context.view_layer.update()
    triangles = export(phone)
    capture(phone)
    print('CELULAR', [round(v, 4) for v in phone.dimensions], triangles, 'triángulos', OUT.name)


main()
