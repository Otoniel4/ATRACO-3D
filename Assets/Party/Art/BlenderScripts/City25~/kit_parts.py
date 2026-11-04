"""Herramientas comunes de los kits de la ciudad (calle, barrios): materiales planos con manifiesto para Unity,
primitivas con nombre, texto en malla liviana y unión de cada pieza en una sola malla exportada a FBX.

Convención de todo el kit: metros, frente hacia -Y (la calle), origen a ras del suelo.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import alarmart as a  # noqa: E402
from kit_fbx import export  # noqa: E402

FACE = (math.pi / 2, 0, 0)  # disco o texto con su cara hacia -Y


def measure(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


class Kit:
    """Un kit: carpeta de FBX, prefijo de materiales, colores y la lista de piezas que describe su manifiesto."""

    def __init__(self, out, prefix, colors):
        self.out, self.prefix, self.colors = Path(out), prefix, colors
        self.registry, self.pieces = {}, []
        self.out.mkdir(parents=True, exist_ok=True)

    # --- materiales ---
    def M(self, name):
        full = self.prefix + name
        m = bpy.data.materials.get(full)
        if m:
            return m
        spec = self.colors[name]
        hex_color, emission, alpha = spec if isinstance(spec, tuple) else (spec, 0.0, 1.0)
        color = tuple(a.linear(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4))
        m = bpy.data.materials.new(full)
        m.diffuse_color = (*color, alpha)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (*color, 1)
        bsdf.inputs['Roughness'].default_value = .7
        if emission:
            bsdf.inputs['Emission Color'].default_value = (*color, 1)
            bsdf.inputs['Emission Strength'].default_value = emission
        if alpha < 1:
            bsdf.inputs['Alpha'].default_value = alpha
            m.surface_render_method = 'BLENDED'
        self.registry[full] = (hex_color, emission, alpha)
        return m

    def use(self, obj, name):
        obj.data.materials.clear()
        obj.data.materials.append(self.M(name))
        return obj

    # --- primitivas ---
    # «parent» cuelga la parte de un grupo (por ejemplo, la bisagra de una puerta); sin él va a la raíz de la pieza.
    def B(self, name, loc, size, m, bevel=.01, rot=None, parent=None):
        return self.use(a.box(name, loc, size, 'Cream', bevel=bevel, rotation=rot, parent=parent), m)

    def C(self, name, loc, r, depth, m, verts=12, rot=None, parent=None):
        return self.use(a.cyl(name, loc, r, depth, 'Metal', vertices=verts, rotation=rot, parent=parent), m)

    def S(self, name, loc, scale, m, sub=2, parent=None):
        return self.use(a.sphere(name, loc, scale, 'Leaf', subdivisions=sub, parent=parent), m)

    def T(self, name, body, loc, size, m, rot=FACE, parent=None):
        # Texto convertido en malla con curvas de baja resolución: se lee igual y pesa una fracción.
        curve = bpy.data.curves.new(name + '_Font', 'FONT')
        curve.body, curve.size, curve.align_x, curve.align_y = body, size, 'CENTER', 'CENTER'
        curve.extrude, curve.resolution_u = .002, 2
        obj = bpy.data.objects.new(name, curve)
        a.COLLECTION.objects.link(obj)
        obj.parent, obj.location, obj.rotation_euler = parent or a.ROOT, loc, rot
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target='MESH')
        return self.use(bpy.context.object, m)

    def plate(self, name, points, y, m):
        # Polígono plano en el plano XZ con la cara hacia -Y.
        verts = [(x, y, z) for x, z in reversed(points)]
        return self.use(a.mesh(name, verts, [tuple(range(len(verts)))]), m)

    def solid(self, name, verts, m):
        # Prisma de 8 vértices (abajo 0-3, arriba 4-7) con normales hacia afuera.
        obj = self.use(a.mesh(name, verts, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]), m)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(obj.data)
        bm.free()
        return obj

    # --- piezas ---
    def begin(self, piece_id):
        a.begin('SK_' + piece_id, 'City/Kit25')

    def finish(self, piece_id, kind, recenter=True, **extra):
        """Une las partes en una malla y exporta. Con recenter=False el origen queda donde se diseñó (por ejemplo,
        el centro del lote o la línea de la cerca) y el manifiesto guarda dónde cae el centro de su planta."""
        root = a.ROOT
        bpy.context.view_layer.update()
        meshes = [o for o in a.descendants(root) if o.type == 'MESH']
        for o in meshes:
            world = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = world
        with bpy.context.temp_override(active_object=meshes[0], selected_editable_objects=meshes, selected_objects=meshes):
            bpy.ops.object.join()
        piece = meshes[0]
        piece.name = piece.data.name = piece_id
        with bpy.context.temp_override(active_object=piece, selected_editable_objects=[piece], object=piece):
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.data.objects.remove(root)
        bpy.context.view_layer.update()
        bm = bmesh.new()
        bm.from_mesh(piece.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=.0005)
        bm.to_mesh(piece.data)
        bm.free()
        lo, hi = measure(piece)
        shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)) if recenter else Vector((0, 0, 0))
        piece.data.transform(Matrix.Translation(-shift))
        piece.matrix_world = Matrix()
        lo, hi = measure(piece)
        info = dict(width=round(hi.x - lo.x, 2), depth=round(hi.y - lo.y, 2), height=round(hi.z - lo.z, 2),
                    triangles=sum(len(p.vertices) - 2 for p in piece.data.polygons))
        if not recenter:
            # Centro de la planta respecto del origen, en ejes del kit (+X derecha del modelo, +Y hacia atrás).
            info['center'] = [round((lo.x + hi.x) / 2, 3), round((lo.y + hi.y) / 2, 3)]
        export([piece], self.out / f'{piece_id}.fbx')
        self.pieces.append(dict(id=piece_id, group=self.out.name.lower(), kind=kind, parts=len(meshes), **info, **extra))
        return piece

    def write_materials(self, materials):
        entries = [dict(name=n, r=int(h[0:2], 16) / 255, g=int(h[2:4], 16) / 255, b=int(h[4:6], 16) / 255, a=al, metallic=0,
                        roughness=.7, emission=round(e * .5, 2)) for n, (h, e, al) in sorted(self.registry.items())]
        Path(materials).write_text(json.dumps(dict(materials=entries), indent=1), encoding='utf-8')

    def write(self, manifest, materials, source):
        Path(manifest).write_text(json.dumps(dict(source=source, front='-Y local (hacia la calle)', pieces=self.pieces),
                                             indent=1, ensure_ascii=False), encoding='utf-8')
        self.write_materials(materials)
        print('KIT', self.out.name, json.dumps([(p['id'], p['width'], p['depth'], p['height'], p['triangles']) for p in self.pieces]))


def review_stage(colors_kit):
    """Escena de revisión: cielo claro, Workbench con colores de material y una cámara. Devuelve (escena, cámara, colección)."""
    scene = bpy.context.scene
    work = bpy.data.collections.new('Revision')
    scene.collection.children.link(work)
    scene.render.engine = 'BLENDER_WORKBENCH'
    sky = bpy.data.worlds.new('Cielo')
    sky.color = (.62, .74, .9)
    scene.world = sky
    scene.view_settings.view_transform = 'Standard'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x, scene.render.resolution_y = 1800, 1000
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    work.objects.link(cam)
    scene.camera = cam
    colors_kit.colors.update(Asfalto='414B52', Acera='C9C6BE', Pasto='6E9A5C', Linea='F4F4F0', Lote='4E5257')

    def slab(name, x0, y0, x1, y1, z, m):
        data = bpy.data.meshes.new(name)
        data.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
        o = bpy.data.objects.new(name, data)
        work.objects.link(o)
        o.data.materials.append(colors_kit.M(m))
        return o

    def shoot(path, eye, target, lens):
        cam.location = eye
        cam.data.lens = lens
        cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    def load(fbx, name):
        # Importa un FBX del proyecto (autos, edificios) bajo un vacío para moverlo entero.
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(fbx))
        holder = bpy.data.objects.new(name, None)
        work.objects.link(holder)
        for o in [o for o in bpy.data.objects if o not in before]:
            if o.parent is None and o is not holder:
                o.parent = holder
        return holder

    return slab, shoot, load
