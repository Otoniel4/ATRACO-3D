"""Revisión cuadro a cuadro de las animaciones de uso de los objetos, antes de probar en Unity.

Reproduce HeldItemView con los mismos datos del juego: pose de sostener (Data/Items/HoldPoses.asset y el ajuste de cada
Item_<id>.asset), movimiento de la acción (Data/Items/item_actions.json), torso inclinado desde el abdomen y manos con IK
de dos huesos a Grip_R y Grip_L. Dibuja los cuadros clave de cada acción desde tres cuartos y de costado.
Uso: blender -b --factory-startup -P preview_item_actions.py [-- palanca gancho ...]
Salida: Previews~/acciones/<id>.png (hoja con los cuadros) y Previews~/acciones/informe.json (si los brazos llegan).
"""
import json
import math
import re
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from preview_hold_poses import load, palm_of, point_fingers, solve  # noqa: E402

PARTY = HERE.parents[1]
ART = PARTY / 'Art'
ITEMS = PARTY / 'Data' / 'Items'
CAST = ART / 'Characters' / 'Cast' / 'Player01_Thief.fbx'
OUT = ART / 'Previews~' / 'acciones'
CLIPS = ART / 'Characters' / 'Animations'
# Rehén de prueba para las acciones con otra persona (bridas): arrodillado, de espaldas al jugador y con las manos atrás,
# a PARTNER_DISTANCE metros delante. Solo sirve para revisar; su pose y su lógica en el juego son de Task 13.
PARTNER = CAST.parent / 'NPC01_Bomber.fbx'
PARTNER_DISTANCE = .62
STYLES = ['Unset', 'Pistol', 'Long', 'OneHandUpright', 'OneHandPointing', 'TwoHandTablet', 'TwoHandCanister']
TWO_HANDED = {'Pistol', 'Long', 'TwoHandTablet', 'TwoHandCanister'}
SHOW = ['palanca', 'ganzua', 'taladro', 'cortavidrios', 'hackeo', 'bridas', 'gancho', 'humo', 'termita', 'pistola', 'escopeta']
FRAME_W, FRAME_H, MAX_FRAMES = 420, 560, 8


# Unity (x derecha, y arriba, z adelante, mano izquierda) → Blender con el personaje mirando a -Y (mano derecha).
def to_blender(v):
    return Vector((-v[0], -v[2], v[1]))


def unity_turn(axis, degrees):
    return Quaternion(to_blender(axis), -math.radians(degrees))  # el cambio de mano invierte el sentido del giro


def unity_euler(e):
    # Quaternion.Euler de Unity: primero z, luego x, luego y.
    return unity_turn((0, 1, 0), e[1]) @ unity_turn((1, 0, 0), e[0]) @ unity_turn((0, 0, 1), e[2])


def vector(text, key):
    m = re.search(r'(?m)^\s+' + key + r': \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+)\}', text)
    return Vector([float(v) for v in m.groups()]) if m else Vector()


def hold_poses():
    text = (ITEMS / 'HoldPoses.asset').read_text(encoding='utf-8')
    poses = {}
    for block in re.split(r'\n  - style: ', text)[1:]:
        poses[STYLES[int(block.split('\n')[0])]] = {k: vector(block, k) for k in ('offset', 'euler', 'rightFingers', 'leftFingers')}
    return poses


def item_specs():
    source = (PARTY / 'Scripts' / 'Player' / 'Editor' / 'ItemAssets.cs').read_text(encoding='utf-8')
    found = re.findall(r'Id = "(\w+)", Hold = HoldStyle\.(\w+), Name = "[^"]*", Model = "(\w+)"', source)
    specs = {}
    for item, style, model in found:
        asset = ITEMS / f'Item_{item}.asset'
        text = asset.read_text(encoding='utf-8') if asset.exists() else ''
        specs[item] = dict(style=style, model=model, offset=vector(text, 'holdOffset'), euler=vector(text, 'holdEuler'))
    return specs


def evaluate(pairs, t):
    # Curva suave por pares (tiempo, valor), igual que ItemActionAssets en Unity: pasa exactamente por cada punto y no se
    # pasa de largo (tangente plana en los picos y en los tramos quietos, acotada en las subidas).
    if not pairs:
        return 0.0
    ts, vs = pairs[0::2], pairs[1::2]
    if t <= ts[0]:
        return vs[0]
    if t >= ts[-1]:
        return vs[-1]
    n = len(ts)

    def slope(i):
        if i in (0, n - 1):
            return 0.0
        a = (vs[i] - vs[i - 1]) / (ts[i] - ts[i - 1])
        b = (vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i])
        if a * b <= 0:
            return 0.0
        return math.copysign(min(abs(a + b) / 2, 3 * min(abs(a), abs(b))), a)

    for i in range(n - 1):
        if ts[i] <= t <= ts[i + 1]:
            dt = ts[i + 1] - ts[i]
            s = (t - ts[i]) / dt
            return ((2 * s ** 3 - 3 * s ** 2 + 1) * vs[i] + (s ** 3 - 2 * s ** 2 + s) * dt * slope(i)
                    + (-2 * s ** 3 + 3 * s ** 2) * vs[i + 1] + (s ** 3 - s ** 2) * dt * slope(i + 1))
    return vs[-1]


def action_pose(action, t):
    c = action['curves']
    get = lambda name: evaluate(c.get(name), t)  # noqa: E731
    return dict(offset=Vector((get('side'), get('up'), get('forward'))), euler=Vector((get('pitch'), get('yaw'), get('roll'))),
                lean=Vector((get('leanForward'), get('leanTwist'), get('leanSide'))), left=max(0.0, min(1.0, get('leftHand'))),
                crouch=get('crouch'), kneel=max(0.0, min(1.0, get('kneel'))), step=get('step'),
                head=Vector((get('headPitch'), get('headTurn'), 0)),
                free=Vector((get('leftSide'), get('leftUp'), get('leftForward'))), has_free='leftForward' in c)


def key_times(action):
    # Los cuadros que se dibujan: los tiempos de las claves de las curvas y el momento del efecto.
    times = {round(action['curves'][k][i], 3) for k in action['curves'] for i in range(0, len(action['curves'][k]), 2)}
    times.add(round(action['trigger'], 3))
    times = sorted(t for t in times if .01 < t < .99)
    if len(times) < 3:
        times = sorted(set(times) | {.3, .75})
    merged = []
    for t in times:
        if not merged or t - merged[-1] > .035:
            merged.append(t)
    if len(merged) > MAX_FRAMES:
        merged = [merged[round(i * (len(merged) - 1) / (MAX_FRAMES - 1))] for i in range(MAX_FRAMES)]
    return merged


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    world = bpy.data.worlds.new('Cielo')
    world.color = (.66, .74, .82)
    scene.world = world
    scene.view_settings.view_transform = 'Standard'
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x, scene.render.resolution_y = FRAME_W, FRAME_H
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = 34
    # Rótulo con el nombre y el tiempo del cuadro, pegado a la cámara.
    label = bpy.data.objects.new('Rotulo', bpy.data.curves.new('Rotulo', 'FONT'))
    scene.collection.objects.link(label)
    label.parent = cam
    label.data.size = .03
    label.location = (-.33, -.44, -1.0)
    ink = bpy.data.materials.new('Tinta')
    ink.diffuse_color = (.05, .05, .07, 1)
    label.data.materials.append(ink)
    # Suelo para ver la altura de las manos y del torso.
    bpy.ops.mesh.primitive_plane_add(size=6)
    floor = bpy.context.object
    paint = bpy.data.materials.new('Suelo')
    paint.diffuse_color = (.55, .56, .55, 1)
    floor.data.materials.append(paint)
    return scene, cam, label


def prepare_character(scene, path=CAST):
    body = load(path)
    arm = next(o for o in body if o.type == 'ARMATURE')
    for o in body:
        if o.name.startswith('ShoppingBag'):
            o.hide_render = True
    # La animación importada pisaría la pose: se congela el primer cuadro de reposo y se quita la animación.
    data = arm.animation_data
    if data:
        idle = next((t for t in data.nla_tracks if 'idle' in t.name.lower()), None)
        for t in data.nla_tracks:
            t.mute = t is not idle
        scene.frame_set(1)
    bpy.context.view_layer.update()
    frozen = {b.name: b.matrix.copy() for b in arm.pose.bones}
    arm.animation_data_clear()
    for b in arm.pose.bones:
        b.matrix = frozen[b.name]
        bpy.context.view_layer.update()
    rest = {b.name: b.matrix_basis.copy() for b in arm.pose.bones}
    return arm, rest


def lean_spine(arm, lean):
    # Igual que HeldItemView: el torso gira (y), se inclina adelante (x) y de costado (z) desde el abdomen.
    turn = unity_turn((0, 1, 0), lean.y) @ unity_turn((1, 0, 0), lean.x) @ unity_turn((0, 0, 1), -lean.z)
    mw = arm.matrix_world
    bone = arm.pose.bones['Abdomen']
    head = mw @ bone.head
    world = Matrix.Translation(head) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-head) @ (mw @ bone.matrix)
    bone.matrix = mw.inverted() @ world
    bpy.context.view_layer.update()


def feet_of(arm):
    # Dónde apoyan los pies en reposo: al agacharse quedan fijos en el suelo.
    mw = arm.matrix_world
    return {side: (mw @ arm.pose.bones['Foot.' + side].matrix).copy() for side in 'LR'}


# Cómo se reparte la inclinación del torso (clips): la cadera bisagra y la columna se curva de abajo hacia arriba,
# en vez de doblarse en un solo punto. El giro lo hace la columna y la cadera lo contrarresta un poco.
SPINE = (('Hips', .35, -.15), ('Abdomen', .3, .4), ('Torso', .2, .35), ('Chest', .15, .4))


def rotate_bone(arm, name, turn):
    mw = arm.matrix_world
    bone = arm.pose.bones[name]
    pivot = mw @ bone.head
    bone.matrix = mw.inverted() @ (Matrix.Translation(pivot) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ (mw @ bone.matrix))
    bpy.context.view_layer.update()


def lean_body(arm, lean, seconds):
    for name, bend, twist in SPINE:
        rotate_bone(arm, name, unity_turn((0, 1, 0), lean.y * twist) @ unity_turn((1, 0, 0), lean.x * bend)
                    @ unity_turn((0, 0, 1), -lean.z * bend))
    if seconds is not None:
        # Respiración: el pecho sube y baja apenas (una vez cada 3,5 s).
        rotate_bone(arm, 'Chest', unity_turn((1, 0, 0), -1.2 * math.sin(seconds * 2 * math.pi / 3.5)))


def place_body(arm, motion, feet, seconds):
    # Cadera: baja (crouch) y va atrás para que el peso quede sobre los pies; pies: paso adelante con el izquierdo (step)
    # y rodilla derecha al piso (kneel). Las piernas se doblan con IK hasta cada pie, con las rodillas sobre la punta.
    mw = arm.matrix_world
    crouch, kneel, step = motion['crouch'], motion['kneel'], motion['step']
    both = motion.get('both', False)  # las dos rodillas al piso (rehén)
    back = crouch * .5 + math.sin(math.radians(max(0.0, motion['lean'].x))) * .12
    sway = .008 * math.sin(seconds * 2 * math.pi / 2.3) if seconds is not None else 0.0  # el peso pasa de un pie al otro
    body = arm.pose.bones['Body']
    body.matrix = mw.inverted() @ (Matrix.Translation(Vector((sway, back - step * .35, -crouch))) @ (mw @ body.matrix))
    bpy.context.view_layer.update()
    for side, planted in feet.items():
        foot = arm.pose.bones['Foot.' + side]
        spot = planted.to_translation().copy()
        turn = Matrix.Identity(4)
        if side == 'L' and not both:
            spot += Vector((0, -(step + kneel * .24), 0))  # adelante es -Y
        else:
            # Atrás, un largo de canilla detrás de la cadera: la rodilla queda en el piso bajo la cadera, talón arriba.
            spot += Vector((0, kneel * (back + .38), kneel * .07))
            turn = Matrix.Rotation(math.radians(55 * kneel), 4, 'X')
        foot.matrix = mw.inverted() @ (Matrix.Translation(spot) @ turn @ planted.to_3x3().to_4x4())
        bpy.context.view_layer.update()
        outward = Vector((1 if side == 'L' else -1, 0, 0))  # la izquierda del personaje es +X
        down = side == 'R' or both
        hint = Vector((0, -1, 0)) + outward * .6 + (Vector((0, 0, -1.5)) * kneel if down else Vector())  # rodilla hacia la punta del pie
        solve(arm, 'UpperLeg.' + side, 'LowerLeg.' + side, 0.0, mw @ foot.head, hint)


def shrug(arm, side, target, share=.25):
    # El hombro acompaña al brazo hacia donde va la mano (adelante, arriba o cruzado), como en una persona.
    mw = arm.matrix_world
    pivot = mw @ arm.pose.bones['Shoulder.' + side].head
    joint = mw @ arm.pose.bones['UpperArm.' + side].head
    full = (joint - pivot).normalized().rotation_difference((target - pivot).normalized())
    rotate_bone(arm, 'Shoulder.' + side, Quaternion().slerp(full, share))


def crouch_body(arm, crouch, feet):
    # Versión simple (sin clip): baja la cadera y dobla las rodillas para que los pies sigan en el suelo.
    place_body(arm, dict(crouch=crouch, kneel=0.0, step=0.0, lean=Vector()), feet, None)


def turn_head(arm, head):
    # Mira hacia donde trabaja: x hacia abajo, y a la derecha (grados, ejes de Unity).
    turn = unity_turn((0, 1, 0), head.y) @ unity_turn((1, 0, 0), head.x)
    mw = arm.matrix_world
    bone = arm.pose.bones['Head']
    pivot = mw @ bone.head
    bone.matrix = mw.inverted() @ (Matrix.Translation(pivot) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ (mw @ bone.matrix))
    bpy.context.view_layer.update()


def pose_frame(arm, rest, item, pose, spec, action, t, feet=None, body_from_clip=False):
    # body_from_clip: el cuerpo ya viene del clip (inclinación, agachada y cabeza), como en Unity; si no, se arma aquí.
    root, grip_r, grip_l, base = item
    motion = action_pose(action, t)
    lean = motion['lean']
    # Al hornear un clip el cuerpo es completo: columna repartida, cadera, pies, hombros y respiración. Sin clip (armas)
    # se imita a Unity: solo el abdomen se inclina.
    whole = bool(action.get('clip')) and not body_from_clip
    seconds = t * action['duration'] if whole and not action['repeat'] else None  # los clips que se repiten no respiran
    if not body_from_clip:
        for b in arm.pose.bones:
            b.matrix_basis = rest[b.name]
        bpy.context.view_layer.update()
        if whole:
            lean_body(arm, lean, seconds)
            if feet:
                place_body(arm, motion, feet, seconds)
        else:
            if lean.length > .01:
                lean_spine(arm, lean)
            if feet and motion['crouch'] > .001:
                crouch_body(arm, motion['crouch'], feet)
        if motion['head'].length > .01:
            turn_head(arm, motion['head'])
    mw = arm.matrix_world
    chest = mw @ arm.pose.bones['Chest'].head
    body = unity_turn((0, 1, 0), lean.y)
    frame = body @ unity_euler((lean.x * .5, 0, 0))
    target = chest + frame @ to_blender(pose['offset'] + spec['offset'] + motion['offset'])
    orientation = body @ unity_euler(pose['euler']) @ unity_euler(spec['euler']) @ unity_euler(motion['euler'])
    root.rotation_mode = 'QUATERNION'
    root.rotation_quaternion = orientation @ base
    bpy.context.view_layer.update()
    root.location += target - grip_r.matrix_world.translation
    bpy.context.view_layer.update()
    firearm = spec['style'] in ('Pistol', 'Long')
    right = body @ Vector((-1, 0, 0))
    if whole:
        shrug(arm, 'R', target)
    _, error_r = solve(arm, 'UpperArm.R', 'LowerArm.R', .06, target, right * .45 + Vector((0, 0, -1)))
    point_fingers(arm, 'Wrist.R', 'LowerArm.R', root, (0, 0, 1) if firearm else tuple(pose['rightFingers'].normalized()))
    root.location += palm_of(arm, 'Wrist.R', 'LowerArm.R') - grip_r.matrix_world.translation  # el objeto sigue a la palma
    bpy.context.view_layer.update()
    weight = max(1.0 if spec['style'] in TWO_HANDED else 0.0, motion['left'])
    error_l = 0.0
    # Mano izquierda libre (granadas: apunta adelante y equilibra el lanzamiento); con agarre, va hacia Grip_L.
    free = chest + frame @ to_blender(motion['free']) if motion['has_free'] and not body_from_clip else None
    if free is not None and (grip_l is None or weight < .99):
        goal = grip_l.matrix_world.translation if grip_l is not None else free
        if whole:
            shrug(arm, 'L', free.lerp(goal, weight))
        solve(arm, 'UpperArm.L', 'LowerArm.L', .06, free.lerp(goal, weight), -right * .45 + Vector((0, 0, -1)))
    elif grip_l is not None and weight > .01:
        start = palm_of(arm, 'Wrist.L', 'LowerArm.L')
        goal = grip_l.matrix_world.translation
        if whole:
            shrug(arm, 'L', goal, .25 * weight)
        _, error_l = solve(arm, 'UpperArm.L', 'LowerArm.L', .06, start.lerp(goal, weight), -right * .45 + Vector((0, 0, -1)))
    if grip_l is not None and weight > .01:
            point_fingers(arm, 'Wrist.L', 'LowerArm.L', root, (0, 0, 1) if firearm else tuple(pose['leftFingers'].normalized()))
    hidden = action['type'] == 'throw' and t >= action['trigger']  # la granada ya salió de la mano
    for o in [root] + list(root.children_recursive):
        o.hide_render = hidden
    return round(error_r, 3), round(error_l, 3), weight


def prepare_partner(scene):
    arm, rest = prepare_character(scene, PARTNER)
    arm.location.y -= PARTNER_DISTANCE  # adelante del jugador, mirando hacia el mismo lado: le da la espalda
    bpy.context.view_layer.update()
    feet = feet_of(arm)
    for b in arm.pose.bones:
        b.matrix_basis = rest[b.name]
    bpy.context.view_layer.update()
    lean = Vector((6, 0, 0))
    lean_body(arm, lean, None)
    place_body(arm, dict(crouch=.47, kneel=1.0, step=0.0, lean=lean, both=True), feet, None)
    turn_head(arm, Vector((20, 0, 0)))
    # Manos juntas en la espalda, sobre la cintura, con los codos hacia afuera.
    mw = arm.matrix_world
    hips = mw @ arm.pose.bones['Hips'].head
    palms = []
    for side, x in (('L', .035), ('R', -.035)):
        solve(arm, 'UpperArm.' + side, 'LowerArm.' + side, .06, hips + Vector((x, .17, .12)), Vector((x * 20, .6, -.4)))
        palms.append(palm_of(arm, 'Wrist.' + side, 'LowerArm.' + side))
    objects = [arm] + list(arm.children_recursive)
    return objects, (palms[0] + palms[1]) / 2


def to_unity(v):
    return Vector((-v.x, v.z, -v.y))


def sheet(paths, columns, name):
    # Une los cuadros en una hoja: fila de arriba de tres cuartos, fila de abajo de costado.
    rows = (len(paths) + columns - 1) // columns
    canvas = np.ones((rows * FRAME_H, columns * FRAME_W, 4), dtype=np.float32)
    for i, path in enumerate(paths):
        image = bpy.data.images.load(str(path))
        pixels = np.array(image.pixels[:], dtype=np.float32).reshape(FRAME_H, FRAME_W, 4)
        row, col = divmod(i, columns)
        y = (rows - 1 - row) * FRAME_H  # en Blender la imagen empieza abajo
        canvas[y:y + FRAME_H, col * FRAME_W:(col + 1) * FRAME_W] = pixels
        bpy.data.images.remove(image)
        path.unlink()
    out = bpy.data.images.new(name, columns * FRAME_W, rows * FRAME_H, alpha=True)
    out.pixels = canvas.ravel()
    out.filepath_raw = str(OUT / f'{name}.png')
    out.file_format = 'PNG'
    out.save()
    bpy.data.images.remove(out)


def main():
    wanted = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else SHOW
    actions = {a['id']: a for a in json.loads((ITEMS / 'item_actions.json').read_text(encoding='utf-8'))['actions']}
    poses, specs = hold_poses(), item_specs()
    scene, cam, label = setup_scene()
    arm, rest = prepare_character(scene)
    feet = feet_of(arm)
    clips, source, rest_error = load_clips(scene, arm)
    partner, wrists = prepare_partner(scene) if any(actions[i].get('partner') for i in wanted) else ([], None)
    OUT.mkdir(parents=True, exist_ok=True)
    chest0 = arm.matrix_world @ arm.pose.bones['Chest'].head
    look = chest0 - Vector((0, 0, .45))  # más abajo: entran los pies al agacharse
    views = [look + Vector((-1.25, -1.75, .35)), look + Vector((-2.15, .05, .1))]  # tres cuartos y costado derecho
    report = {}
    for item_id in wanted:
        action, spec = actions[item_id], specs[item_id]
        pose = poses[spec['style']]
        loaded = load(ART / 'Weapons' / f"{spec['model']}.fbx")
        root = next(o for o in loaded if o.parent is None)
        grip_r = next(o for o in loaded if o.name.startswith('Grip_R'))
        grip_l = next((o for o in loaded if o.name.startswith('Grip_L')), None)
        bpy.context.view_layer.update()
        item = (root, grip_r, grip_l, root.matrix_world.to_quaternion())
        times = key_times(action)
        clip = clips.get(item_id) if action.get('clip') else None
        if clip:
            play(source, clip)
        for o in partner:
            o.hide_render = not action.get('partner')
        paths, frames = [[], []], []
        for k, t in enumerate(times):
            if clip:
                start, end = clip.frame_range
                frame = start + t * (end - start)
                scene.frame_set(int(frame), subframe=frame - int(frame))
                copy_pose(source, arm)
            error_r, error_l, weight = pose_frame(arm, rest, item, pose, spec, action, t, feet, body_from_clip=clip is not None)
            seconds = t * action['duration']
            effect = '  efecto' if abs(t - action['trigger']) < .02 else ''
            origin = 'clip' if clip else 'curvas'
            label.data.body = f'{item_id}  t={t:.2f} ({seconds:.2f} s) {origin}{effect}'
            frames.append(dict(t=t, mano_derecha_falta=error_r, mano_izquierda_falta=error_l, peso_izquierda=round(weight, 2)))
            if action.get('partner') and wrists is not None:
                # Qué tan lejos quedan las manos de las muñecas del rehén, y dónde están esas muñecas respecto del pecho
                # (ejes de Unity del cuerpo inclinado), para ajustar las curvas.
                lean_now = action_pose(action, t)['lean']
                chest = arm.matrix_world @ arm.pose.bones['Chest'].head
                frame = unity_turn((0, 1, 0), lean_now.y) @ unity_euler((lean_now.x * .5, 0, 0))
                frames[-1].update(rehen_izquierda=round((palm_of(arm, 'Wrist.L', 'LowerArm.L') - wrists).length, 3),
                                  rehen_derecha=round((palm_of(arm, 'Wrist.R', 'LowerArm.R') - wrists).length, 3),
                                  munecas_desde_pecho=[round(v, 3) for v in to_unity(frame.inverted() @ (wrists - chest))])
            # Con otra persona delante, la primera vista es desde atrás del jugador para que no la tape.
            shots = [look + Vector((-1.25, 1.75, .45)), views[1]] if action.get('partner') else views
            for v, eye in enumerate(shots):
                cam.location = eye
                cam.rotation_euler = (look - eye).to_track_quat('-Z', 'Y').to_euler()
                path = OUT / f'_{item_id}_{v}_{k}.png'
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                paths[v].append(path)
        sheet(paths[0] + paths[1], len(times), item_id)
        report[item_id] = frames
        if clip:
            source.animation_data.action = None
        for o in loaded:
            bpy.data.objects.remove(o, do_unlink=True)
    report['_esqueleto_clips_vs_elenco_m'] = rest_error
    (OUT / 'informe.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
    worst = {k: max(max(f['mano_derecha_falta'], f['mano_izquierda_falta']) for f in v) for k, v in report.items() if not k.startswith('_')}
    print('ACCIONES', worst, 'clips', sorted(clips), 'diferencia de esqueleto', rest_error)


def load_clips(scene, arm):
    # Clips exportados por build_action_clips.py (lo mismo que recibe Unity), evaluados sobre su propio esqueleto y
    # copiados al personaje cuadro a cuadro. Comprueba que el clip «Reposo» da la misma pose que el reposo del elenco:
    # si no coincidiera, los clips se verían torcidos en el juego.
    path = CLIPS / 'Alarma_ItemActions_Men.fbx'
    if not path.exists():
        return {}, None, None
    before = set(bpy.data.actions)
    loaded = load(path)
    source = next(o for o in loaded if o.type == 'ARMATURE')
    clips = {a.name.split('|')[-1]: a for a in bpy.data.actions if a not in before}
    play(source, clips['Reposo'])
    scene.frame_set(int(clips['Reposo'].frame_range[0]))
    bpy.context.view_layer.update()
    error = 0.0
    for b in arm.pose.bones:
        mine, theirs = arm.matrix_world @ b.matrix, source.matrix_world @ source.pose.bones[b.name].matrix
        error = max(error, (mine.to_translation() - theirs.to_translation()).length,
                    mine.to_quaternion().rotation_difference(theirs.to_quaternion()).angle * .1)  # 0,1 = 1 cm por cada 0,1 rad
    source.animation_data.action = None
    source.hide_render = True
    return clips, source, round(error, 4)


def copy_pose(source, arm):
    # Misma pose en el mundo, hueso por hueso, de padre a hijo.
    inverse = arm.matrix_world.inverted()
    for b in sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive)):
        b.matrix = inverse @ (source.matrix_world @ source.pose.bones[b.name].matrix)
        bpy.context.view_layer.update()


def play(arm, clip):
    data = arm.animation_data_create()
    data.action = clip
    if hasattr(data, 'action_slot') and clip.slots:
        data.action_slot = clip.slots[0]


if __name__ == '__main__':
    main()
