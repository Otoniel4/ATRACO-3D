"""Poses de dedos para sujetar objetos, ajustadas sobre la mano real del elenco.

Para cada pose coloca un objeto de prueba en la palma y cierra cada articulación hasta que el dedo lo toca (no son
ángulos puestos a ojo). Usa el mismo criterio de ejes que CommerceFingerPose en Unity, así lo que se ve acá es lo que
aplica el juego. Salida: Art/Characters/Animations/hand_poses.json y capturas en docs/Capturas/Manos.

Uso: blender --background --factory-startup --python build_hand_poses.py
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent; ART = HERE.parent; DOCS = ART.parent / 'docs' / 'Capturas' / 'Manos'
DOCS.mkdir(parents=True, exist_ok=True)
FINGERS = ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky')
THICK = .009            # medio grosor de un dedo, en metros
STEP = 1.               # paso de búsqueda, en grados
LIMIT = {'finger': (90., 100., 70.), 'thumb': (50., 45., 60.)}
# Qué pose usa cada objeto del catálogo de los negocios.
OBJECTS = {
    'BotellaReserva': 'Cilindro', 'LataCola': 'Cilindro', 'Aceite': 'Cilindro', 'Vaso': 'Cilindro',
    'Leche': 'Caja', 'Cafe': 'Caja', 'Cereal': 'Caja', 'Lingote': 'Caja', 'Hamburguesa': 'Caja', 'Zapatilla': 'Caja',
    'Anillo': 'Pinza', 'Reloj': 'Pinza', 'Collar': 'Pinza',
    'Sobre': 'Plano', 'Pizza': 'Plano', 'Camiseta': 'Plano',
    'Maletin': 'Asa', 'Bolso': 'Asa',
}


def chain(finger):
    return [finger + str(n) + '.R' for n in ((1, 2, 3) if finger == 'Thumb' else (2, 3, 4))]


class Hand:
    """Mano derecha de un personaje importado, en reposo."""

    def __init__(self, path, offset):
        before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path))
        self.objects = set(bpy.data.objects) - before
        self.rig = next(o for o in self.objects if o.type == 'ARMATURE')
        for o in self.objects:
            if o.name.startswith('ShoppingBag_'): o.hide_render = True
            if o.animation_data: o.animation_data_clear()
        for bone in self.rig.pose.bones: bone.matrix_basis.identity()
        root = bpy.data.objects.new('Persona', None); bpy.context.scene.collection.objects.link(root)
        for o in self.objects:
            if o.parent is None: o.parent = root
        root.location = offset; bpy.context.view_layer.update()
        self.b = self.rig.pose.bones
        wrist, middle = self.head('Wrist.R'), self.head('Middle2.R')
        self.fingers = (middle - wrist).normalized()
        self.across = (self.head('Index2.R') - self.head('Pinky2.R')).normalized()
        # Normal que sale de la palma. Unity es zurdo y Blender diestro: allá la misma dirección es Cross(fingers, across).
        self.normal = self.across.cross(self.fingers).normalized()
        self.palm = middle - self.fingers * .025 + self.normal * .015
        # Eje de flexión de cada articulación, guardado en el espacio del hueso (igual que CommerceFingerPose).
        self.axis = {}
        for finger in FINGERS:
            names = chain(finger)
            for i, name in enumerate(names):
                direction = (self.head(names[i + 1]) - self.head(name)) if i + 1 < len(names) else (self.head(name) - self.head(self.b[name].parent.name))
                inward = (middle - self.head(name)) if finger == 'Thumb' else self.normal
                self.axis[name] = self.world(name).to_3x3().inverted() @ direction.cross(inward).normalized()

    def world(self, name): return self.rig.matrix_world @ self.b[name].matrix
    def head(self, name): return self.world(name).translation.copy()
    def tail(self, name): return self.rig.matrix_world @ self.b[name].tail

    def end(self, names, i): return self.head(names[i + 1]) if i + 1 < len(names) else self.tail(names[i])

    def bend(self, name, degrees):
        """Gira el hueso alrededor de su eje de flexión (lo mismo que localRotation *= AngleAxis en Unity)."""
        m = self.world(name); pivot = m.translation.copy()
        axis = (m.to_3x3() @ self.axis[name]).normalized()
        turned = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(degrees), 4, axis) @ Matrix.Translation(-pivot) @ m
        self.b[name].matrix = self.rig.matrix_world.inverted() @ turned
        bpy.context.view_layer.update()

    def wrap(self, finger, centre, axis, radius):
        """Cierra cada articulación hasta que el extremo de su falange toca el cilindro."""
        names = chain(finger); limits = LIMIT['thumb' if finger == 'Thumb' else 'finger']; angles = []
        def gap(i):
            to = self.end(names, i) - centre
            return (to - axis * to.dot(axis)).length - radius - THICK
        for i, name in enumerate(names):
            angle = 0.; best = gap(i)
            while angle < limits[i] and best > 0:
                self.bend(name, STEP); now = gap(i)
                if now > best + 1e-5: self.bend(name, -STEP); break   # ya pasó el punto más cercano
                angle += STEP; best = now
            angles.append(round(angle, 1))
        return angles

    def apply(self, pose):
        for finger in FINGERS:
            for name, angle in zip(chain(finger), pose[finger.lower()]): self.bend(name, angle)

    def pinch(self, gap):
        """El índice se dobla a medias y el pulgar se cierra hasta dejar entre las puntas el hueco de un objeto pequeño."""
        thumb, index = chain('Thumb'), chain('Index'); best = None
        for k in range(25, 71, 5):
            fore = [k, k * .8, k * .45]
            for name, angle in zip(index, fore): self.bend(name, angle)
            for t1 in range(0, 51, 10):
                for t2 in range(0, 46, 15):
                    for t3 in range(0, 61, 20):
                        for name, angle in zip(thumb, (t1, t2, t3)): self.bend(name, angle)
                        miss = abs((self.tail(thumb[-1]) - self.tail(index[-1])).length - gap - 2 * THICK)
                        for name, angle in reversed(list(zip(thumb, (t1, t2, t3)))): self.bend(name, -angle)
                        if best is None or miss < best[0]: best = (miss, {'thumb': [t1, t2, t3], 'index': fore})
            for name, angle in reversed(list(zip(index, fore))): self.bend(name, -angle)
        return best[1], best[0]


def material(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1); return m


def cylinder(centre, axis, radius, length, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=centre, vertices=24)
    o = bpy.context.object; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis)
    o.data.materials.append(mat); return o


def slab(centre, normal, along, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    o = bpy.context.object; o.scale = size
    x = along.normalized(); z = normal.normalized(); y = z.cross(x)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Matrix((x, y, z)).transposed().to_quaternion()
    o.data.materials.append(mat); return o


def build(hand, pose_id, mat, known=None):
    """Arma una pose en la mano y deja el objeto de prueba a la vista. Devuelve los ángulos."""
    f, a, n, p = hand.fingers, hand.across, hand.normal, hand.palm
    if pose_id == 'Plano':
        # Mano abierta bajo una hoja: dedos extendidos y el pulgar apenas cerrado sobre el borde.
        pose = known or {'thumb': [10, 5, 5], 'index': [0, 2, 2], 'middle': [0, 2, 2], 'ring': [0, 2, 2], 'pinky': [0, 3, 3]}
        hand.apply(pose); slab(p + f * .06 + n * .004, n, f, (.26, .14, .008), mat); return pose
    if pose_id == 'Pinza':
        if known: pose = known
        else:
            two, miss = hand.pinch(.012); print('PINZA hueco sin cerrar %.3f m' % miss)
            pose = {'thumb': [round(v, 1) for v in two['thumb']], 'index': [round(v, 1) for v in two['index']],
                    'middle': [round(v + 6, 1) for v in two['index']], 'ring': [70, 70, 45], 'pinky': [75, 70, 45]}
        hand.apply(pose)
        tip = (hand.tail('Thumb3.R') + hand.tail('Index4.R')) / 2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.006, location=tip); bpy.context.object.data.materials.append(mat)
        return pose
    # El punto de la palma (el mismo que usa el juego para apoyar el objeto) queda sobre la superficie del objeto.
    radius, shift = {'Cilindro': (.034, 0.), 'Caja': (.05, 0.), 'Asa': (.013, .02)}[pose_id]
    centre = p + f * shift + n * radius
    if known: pose = known; hand.apply(pose)
    else: pose = {finger.lower(): hand.wrap(finger, centre, a, radius) for finger in FINGERS}
    cylinder(centre, a, radius, .22, mat)
    return pose


def render(name, hands, view):
    """Una vista de cerca por mano, unidas en una sola tira (una pose por cuadro)."""
    import numpy
    scene = bpy.context.scene; size = 420; tiles = []
    scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.light = 'STUDIO'; scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_cavity = True; scene.display.shading.show_shadows = False
    scene.display.shading.background_type = 'WORLD'
    if scene.world is None: scene.world = bpy.data.worlds.new('Fondo')
    scene.world.color = (.22, .24, .27)
    scene.render.resolution_x = size; scene.render.resolution_y = size; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for i, hand in enumerate(hands):
        camera = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara')); scene.collection.objects.link(camera); scene.camera = camera
        middle = hand.palm + hand.fingers * .05
        toward = hand.across if view == 'costado' else hand.normal
        camera.location = middle + toward * 1.5
        # Los dedos apuntan a la derecha de la imagen en las dos vistas.
        z = toward.normalized(); x = (hand.fingers - z * hand.fingers.dot(z)).normalized(); y = z.cross(x)
        camera.rotation_euler = Matrix((x, y, z)).transposed().to_euler()
        camera.data.type = 'ORTHO'; camera.data.ortho_scale = .34; camera.data.clip_end = 1.75
        tile = str(DOCS / ('_tile_%d.png' % i)); scene.render.filepath = tile; bpy.ops.render.render(write_still=True)
        image = bpy.data.images.load(tile); tiles.append(numpy.array(image.pixels[:]).reshape(size, size, 4))
        bpy.data.images.remove(image); bpy.data.objects.remove(camera); Path(tile).unlink()
    strip = numpy.concatenate(tiles, axis=1)
    sheet = bpy.data.images.new('Tira', width=size * len(hands), height=size, alpha=True)
    sheet.pixels = strip.ravel().tolist(); sheet.filepath_raw = str(DOCS / name); sheet.file_format = 'PNG'; sheet.save()
    bpy.data.images.remove(sheet)


POSES = ('Cilindro', 'Caja', 'Pinza', 'Plano', 'Asa')
cast = sorted((ART / 'Characters/Cast').glob('NPC*.fbx'))
found = {}
# La primera pasada ajusta las poses sobre un hombre; la segunda las aplica tal cual a una mujer para comprobar que
# sirven en los dos tamaños de mano. Una hilera de manos: una pose en cada una, separadas a lo largo de los dedos cruzados.
for round_index, path in enumerate((cast[0], cast[1])):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = material('Objeto', (.95, .45, .1)); hands = []
    for i, pose_id in enumerate(POSES):
        hand = Hand(path, Vector((0, i * 4., 0)))
        if i == 0: assert hand.normal.z < -.5, 'La palma en reposo debe mirar hacia abajo: %s' % hand.normal
        pose = build(hand, pose_id, mat, found.get(pose_id))
        if round_index == 0: found[pose_id] = pose; print('POSE', pose_id, json.dumps(pose))
        hands.append(hand)
    tag = 'hombre' if round_index == 0 else 'mujer'
    # De costado (se ve cuánto cierra cada dedo) y desde la palma (se ve el pulgar y el objeto).
    render('manos_%s_costado.png' % tag, hands, 'costado')
    render('manos_%s_palma.png' % tag, hands, 'palma')

out = ART / 'Characters' / 'Animations' / 'hand_poses.json'
out.write_text(json.dumps({
    'source': 'Original Alarma: ajustadas en Blender sobre la mano del elenco (build_hand_poses.py)',
    'joints': 'Grados de flexión por articulación. Pulgar: Thumb1-3. Demás dedos: 2-4 (nudillo, media, punta).',
    'poses': [dict(id=pose_id, **found[pose_id]) for pose_id in POSES],
    'objects': [dict(id=k, pose=v) for k, v in OBJECTS.items()],
}, indent=1) + '\n', encoding='utf-8')
print('ESCRITO', out)
