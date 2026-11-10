"""Clips de reacción de los civiles (Task 13) para el doble de reacción de Unity (NpcReactionAssets).

Mismo esqueleto del pack Quaternius que el elenco (Men y Women) y la misma mecánica de cuerpo que los clips de uso de
objetos: columna repartida, cadera que baja con los pies plantados y rodillas con IK, hombros que acompañan, cabeza.
Cada clip es una lista de poses clave; entre una y otra los valores pasan suave (sin pasarse de largo) y las manos van
de un punto al otro. Las manos se ubican respecto del pecho («chest», ejes de Unity del cuerpo) o del suelo bajo la
cadera («floor»).
  Suplicar            se agacha con las manos en alto pidiendo piedad.
  Rendido             lleva las manos a la espalda, se arrodilla con las dos rodillas y agacha la cabeza.
  Amarrado            de rodillas y con la cabeza gacha, junta las muñecas en la espalda (así lo amarran con bridas).
  LevantarseEspalda   sentado en el suelo (tras caer boca arriba) → apoya una rodilla → se pone de pie.
  LevantarseBoca      en cuatro patas (tras caer boca abajo) → se sienta en los talones → una rodilla → de pie.
  Grabar              levanta el celular con la mano derecha frente a la cara, de pie y con la pantalla hacia sus ojos
                      (testigo que graba).
  Llamar              desde esa postura lleva el celular a la oreja derecha (testigo que llama a la policía).
  Sorprendido         da un respingo: se echa atrás con las manos abiertas frente al pecho (ve el atraco).
  GrabarAgachado      agachado como en Suplicar, saca el celular junto al pecho y graba a escondidas.
  Esposar             (policía) apoya una rodilla, se inclina sobre el detenido en el suelo y le junta las manos.
En Grabar y Llamar la muñeca se orienta sola: el celular va apoyado en la palma (misma regla que
NpcReactionAssets.MakePhone: muñeca y nudillos del índice, medio y meñique), de pie, con la pantalla hacia la cabeza.
Los clips de levantarse empiezan sentado o en cuatro patas: NpcRagdoll mezcla desde el cuerpo caído a ese primer cuadro.
Uso: blender -b --factory-startup -P build_npc_reaction_clips.py   (con «-- --solo-revision» solo redibuja las hojas)
Salida: Art/Characters/Animations/Alarma_NpcReactions_Men.fbx, _Women.fbx, npc_reaction_clips.json y
Previews~/acciones/npc_<clip>.png (revisión sobre el civil NPC01 con el FBX exportado).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_action_clips as clips_kit  # noqa: E402
import preview_item_actions as body  # noqa: E402

OUT = clips_kit.OUT
FPS = clips_kit.FPS
REVIEW = body.CAST.parent / 'NPC01_Bomber.fbx'
BEHIND_BACK = (('hips', (.035, .12, -.17)), ('hips', (-.035, .12, -.17)))
WRISTS_TOGETHER = (('hips', (.015, .12, -.17)), ('hips', (-.015, .12, -.17)))
# Celular: (punto que mira la pantalla, desde la base de la cabeza; hacia dónde va su borde de arriba), ejes de Unity.
# Celular: (agarre, punto que mira la pantalla desde la base de la cabeza, hacia dónde va su borde de arriba), en ejes
# de Unity.
RECORD = ('film', (0, .085, .10), (0, 1, -.12))  # hacia los ojos, apenas echado atrás
CALL = ('call', (.02, .06, 0), (0, 1, -.4))      # contra la oreja, inclinado hacia la boca
PHONE = clips_kit.ART / 'Props' / 'Prop_NpcPhone.fbx'
RECORD_LOW = ('film', (0, .085, .10), (0, 1, -.35))  # agachado: bajo, junto al pecho, inclinado hacia los ojos
PHONE_CLIPS = ('Grabar', 'Llamar', 'GrabarAgachado')
# Dos agarres, como los de una persona (NpcReactionAssets.MakePhone usa los mismos números):
#   film  para grabar: la mano como al dar la mano (pulgar arriba), con los cuatro dedos doblados por detrás del celular
#         y el pulgar por delante; el celular queda de pie entre los dedos y el pulgar, con la pantalla hacia la muñeca.
#   call  para hablar: el celular va a lo largo de la mano, sobre la palma y los dedos apenas curvados.
# up y screen: ejes de la mano que siguen el borde de arriba y hacia dónde mira la pantalla (along: hacia los dedos,
# across: hacia el índice, palm: fuera de la palma; «-» invierte); along, out, side: centro del celular desde la muñeca (hacia los
# dedos, fuera de la palma y hacia el índice); curl: grados que se cierra cada falange; thumb: grados que el pulgar se
# cierra hacia la palma y hacia los dedos. Las manos del elenco son grandes: el celular se agranda (PHONE_SCALE).
GRIPS = {
    'film': dict(up='across', screen='-along', along=.128, out=.055, side=.045, curl=(78, 18, 10), thumb=(0, 32)),
    'call': dict(up='along', screen='palm', along=.13, out=.028, side=.03, curl=(12, 16, 10), thumb=(0, 0)),
}
PHONE_SCALE = 1.15
REGRIP = .28  # parte del clip Llamar en que el celular se acomoda de un agarre al otro (0,25 s; igual en WitnessPhone)
FINGERS = ('Index', 'Middle', 'Ring', 'Pinky')
PLEAD = (('chest', (.13, .1, .3)), ('chest', (-.13, .1, .3)))

CLIPS = {
    'Suplicar': (1.0, [
        (0, dict()),
        (.55, dict(crouch=.44, lean=(26, 0, 0), head=(12, 0), hands=PLEAD)),
        (1, dict(crouch=.45, lean=(28, 0, 0), head=(16, 0), hands=(('chest', (.12, .13, .3)), ('chest', (-.12, .13, .3))))),
    ]),
    'Rendido': (1.3, [
        (0, dict()),
        (.3, dict(lean=(2, 0, 0), head=(10, 0), hands=BEHIND_BACK)),
        (.75, dict(crouch=.47, kneel=1, both=True, lean=(8, 0, 0), head=(28, 0), hands=BEHIND_BACK)),
        (1, dict(crouch=.47, kneel=1, both=True, lean=(10, 0, 0), head=(36, 0), hands=BEHIND_BACK)),
    ]),
    'Amarrado': (.7, [
        (0, dict(crouch=.47, kneel=1, both=True, lean=(10, 0, 0), head=(36, 0), hands=BEHIND_BACK)),
        (1, dict(crouch=.47, kneel=1, both=True, lean=(10, 0, 0), head=(38, 0), hands=WRISTS_TOGETHER)),
    ]),
    'LevantarseEspalda': (2.2, [
        (0, dict(crouch=.72, tuck=.38, lean=(-18, 0, 0), head=(6, 0), hands=(('floor', (.24, 0, -.22)), ('floor', (-.24, 0, -.22))))),
        (.3, dict(crouch=.66, tuck=.2, lean=(28, 0, 0), head=(10, 0), hands=(('floor', (.3, 0, .15)), ('floor', (-.3, 0, .1))))),
        (.55, dict(crouch=.42, kneel=1, lean=(26, 0, 0), head=(8, 0), hands=(('chest', (.2, -.36, .3)), ('floor', (-.28, 0, .22))))),
        (.8, dict(crouch=.14, kneel=.15, lean=(12, 0, 0), head=(2, 0))),
        (1, dict()),
    ]),
    'LevantarseBoca': (2.0, [
        (0, dict(crouch=.5, kneel=1, both=True, lean=(72, 0, 0), head=(-25, 0), hands=(('floor', (.2, 0, .42)), ('floor', (-.2, 0, .42))))),
        (.3, dict(crouch=.55, kneel=1, both=True, lean=(30, 0, 0), head=(4, 0), hands=(('floor', (.22, 0, .25)), ('floor', (-.22, 0, .25))))),
        (.55, dict(crouch=.42, kneel=1, lean=(22, 0, 0), head=(6, 0), hands=(('chest', (.2, -.36, .3)), None))),
        (.8, dict(crouch=.14, kneel=.15, lean=(10, 0, 0), head=(2, 0))),
        (1, dict()),
    ]),
    'Grabar': (.7, [
        (0, dict()),
        (.6, dict(lean=(2, 0, 0), head=(-2, 0), hands=(('chest', (.10, .15, .27)), None), phone=RECORD, elbow=.6)),
        (1, dict(lean=(2, 0, 0), head=(-3, 0), hands=(('chest', (.10, .17, .28)), None), phone=RECORD, elbow=.6)),
    ]),
    'Llamar': (.9, [
        (0, dict(lean=(2, 0, 0), head=(-3, 0), hands=(('chest', (.10, .17, .28)), None), phone=RECORD, elbow=.6)),
        (.7, dict(head=(4, 0), hands=(('head', (.105, 0, .035)), None), phone=CALL)),
        (1, dict(head=(5, 0), hands=(('head', (.10, 0, .03)), None), phone=CALL)),
    ]),
    'Sorprendido': (.5, [
        (0, dict()),
        (.5, dict(lean=(-8, 0, 0), head=(-6, 0), hands=(('chest', (.2, .04, .2)), ('chest', (-.2, .04, .2))))),
        (1, dict(lean=(-5, 0, 0), head=(-4, 0), hands=(('chest', (.18, 0, .22)), ('chest', (-.18, 0, .22))))),
    ]),
    'GrabarAgachado': (.8, [
        (0, dict(crouch=.45, lean=(28, 0, 0), head=(16, 0), hands=(('chest', (.12, .13, .3)), ('chest', (-.12, .13, .3))))),
        (.7, dict(crouch=.46, lean=(30, 0, 0), head=(-6, 0), hands=(('chest', (.1, .0, .27)), ('chest', (-.16, -.3, .2))), phone=RECORD_LOW, elbow=.6)),
        (1, dict(crouch=.46, lean=(30, 0, 0), head=(-8, 0), hands=(('chest', (.1, .02, .28)), ('chest', (-.16, -.3, .2))), phone=RECORD_LOW, elbow=.6)),
    ]),
    'Esposar': (2.4, [
        (0, dict()),
        (.35, dict(crouch=.4, kneel=1, lean=(34, 0, 0), head=(24, 0), hands=(('floor', (.12, 0, .42)), ('floor', (-.12, 0, .42))))),
        (.8, dict(crouch=.42, kneel=1, lean=(38, 0, 0), head=(26, 0), hands=(('floor', (.04, 0, .4)), ('floor', (-.04, 0, .4))))),
        (1, dict(crouch=.42, kneel=1, lean=(36, 0, 0), head=(24, 0), hands=(('floor', (.05, 0, .38)), ('floor', (-.05, 0, .38))))),
    ]),
}
NUMBERS = ('crouch', 'kneel', 'step', 'tuck')


def ease(a, b, s):
    s = s * s * (3 - 2 * s)  # sale y llega suave, sin pasarse
    return a + (b - a) * s


def segment(keys, t):
    for i in range(len(keys) - 1):
        if keys[i][0] <= t <= keys[i + 1][0]:
            span = keys[i + 1][0] - keys[i][0]
            return keys[i][1], keys[i + 1][1], (t - keys[i][0]) / span if span > 0 else 1.0
    return keys[-1][1], keys[-1][1], 1.0


def hand_target(arm, spec, frame):
    mw = arm.matrix_world
    kind, (x, y, z) = spec
    if kind == 'chest':
        return mw @ arm.pose.bones['Chest'].head + frame @ body.to_blender(Vector((x, y, z)))
    if kind == 'head':
        return mw @ arm.pose.bones['Head'].head + frame @ body.to_blender(Vector((x, y, z)))
    hips = mw @ arm.pose.bones['Body'].head
    if kind == 'hips':
        return hips + frame @ body.to_blender(Vector((x, y, z)))
    return Vector((hips.x, hips.y, .05)) + frame @ body.to_blender(Vector((x, 0, z)))  # floor: sobre el suelo


def hand_frame(arm, side='R'):
    # Muñeca, dirección de los dedos y hacia dónde mira la palma (en reposo, hacia el cuerpo), a partir de los nudillos.
    mw = arm.matrix_world
    at = lambda name: mw @ arm.pose.bones[f'{name}.{side}'].head  # noqa: E731
    wrist = at('Wrist')
    along = (at('Middle2') - wrist).normalized()  # los huesos «2» nacen en los nudillos
    across = (at('Index2') - at('Pinky2')).normalized()
    palm = across.cross(along).normalized()
    return wrist, along, -palm if side == 'L' else palm, across


def hand_axis(name, along, palm, across):
    axis = dict(along=along, palm=palm, across=across)[name.lstrip('-')]
    return -axis if name.startswith('-') else axis


def phone_matrix(arm, grip):
    # Dónde queda el celular en la mano: columnas ancho, dorso y alto del modelo, y su centro.
    g = GRIPS[grip]
    wrist, along, palm, across = hand_frame(arm)
    up, screen = hand_axis(g['up'], along, palm, across), hand_axis(g['screen'], along, palm, across)
    held = Matrix((up.cross(screen), -screen, up)).transposed().to_4x4()
    held.translation = wrist + along * g['along'] + palm * g['out'] + across * g['side']
    return held


def phone_turn(arm, spec, frame):
    # Giro de la muñeca derecha para sostener el celular de pie con la pantalla hacia un punto de la cabeza.
    if not spec:
        return Quaternion()
    grip, look, up = spec
    wrist, along, palm, across = hand_frame(arm)
    axis = hand_axis(GRIPS[grip]['up'], along, palm, across)        # eje de la mano que sigue el borde de arriba
    facing = hand_axis(GRIPS[grip]['screen'], along, palm, across)  # y el que sigue la pantalla
    point = arm.matrix_world @ arm.pose.bones['Head'].head + frame @ body.to_blender(Vector(look))
    want_up = (frame @ body.to_blender(Vector(up))).normalized()
    want_palm = point - phone_matrix(arm, grip).translation
    want_palm = (want_palm - want_up * want_palm.dot(want_up)).normalized()
    now = Matrix((axis, facing, axis.cross(facing))).transposed()
    goal = Matrix((want_up, want_palm, want_up.cross(want_palm))).transposed()
    return (goal @ now.inverted()).to_quaternion()


def pose(arm, rest, feet, keys, t):
    a, b, s = segment(keys, t)
    for bone in arm.pose.bones:
        bone.matrix_basis = rest[bone.name]
    bpy.context.view_layer.update()
    value = {k: ease(a.get(k, 0.0), b.get(k, 0.0), s) for k in NUMBERS}
    lean = Vector([ease(p, q, s) for p, q in zip(a.get('lean', (0, 0, 0)), b.get('lean', (0, 0, 0)))])
    head = Vector([ease(p, q, s) for p, q in zip(a.get('head', (0, 0)), b.get('head', (0, 0)))] + [0])
    body.lean_body(arm, lean, None)
    both = (a if s < .5 else b).get('both', False)  # las dos rodillas al piso: cambia a mitad de camino
    body.place_body(arm, dict(value, lean=lean, both=both), feet, None)
    if head.length > .01:
        body.turn_head(arm, head)
    frame = body.unity_turn((0, 1, 0), lean.y) @ body.unity_euler((lean.x * .5, 0, 0))
    right = frame @ Vector((-1, 0, 0))
    sides = (('R', 0, right), ('L', 1, -right))
    for side, index, out in sides:
        start = (a.get('hands') or (None, None))[index]
        end = (b.get('hands') or (None, None))[index]
        if start is None and end is None:
            continue
        rest_palm = body.palm_of(arm, 'Wrist.' + side, 'LowerArm.' + side)
        p = hand_target(arm, start, frame) if start else rest_palm
        q = hand_target(arm, end, frame) if end else rest_palm
        goal = p.lerp(q, s * s * (3 - 2 * s))
        body.shrug(arm, side, goal, .2)
        elbow = ease(a.get('elbow', .45), b.get('elbow', .45), s)  # cuánto se abre el codo hacia afuera
        body.solve(arm, 'UpperArm.' + side, 'LowerArm.' + side, .06, goal, out * elbow + Vector((0, 0, -1)))
    if a.get('phone') or b.get('phone'):
        turn = phone_turn(arm, a.get('phone'), frame).slerp(phone_turn(arm, b.get('phone'), frame), s * s * (3 - 2 * s))
        body.rotate_bone(arm, 'Wrist.R', turn)
        # Dedos y pulgar: del agarre de una clave al de la otra (mano abierta si la clave no tiene celular).
        def held(key, name, count):
            return GRIPS[key['phone'][0]][name] if key.get('phone') else (0,) * count
        curl = [ease(p, q, s) for p, q in zip(held(a, 'curl', 3), held(b, 'curl', 3))]
        thumb = [ease(p, q, s) for p, q in zip(held(a, 'thumb', 2), held(b, 'thumb', 2))]
        _, along, palm, across = hand_frame(arm)
        for finger in FINGERS:
            for joint, degrees in enumerate(curl):
                body.rotate_bone(arm, f'{finger}{joint + 2}.R', Quaternion(along.cross(palm), math.radians(degrees)))
        body.rotate_bone(arm, 'Thumb1.R', Quaternion(along, math.radians(thumb[0])) @ Quaternion(palm, math.radians(thumb[1])))


def bake(arm, rest, feet, name, duration, keys):
    frames = max(2, round(duration * FPS))
    clip = bpy.data.actions.new(name)
    data = arm.animation_data
    data.action = clip
    previous = {}
    for f in range(frames + 1):
        pose(arm, rest, feet, keys, f / frames)
        for bone in arm.pose.bones:
            q = bone.rotation_quaternion.copy()
            if bone.name in previous and previous[bone.name].dot(q) < 0:
                q.negate()
                bone.rotation_quaternion = q
            previous[bone.name] = q
            bone.keyframe_insert('rotation_quaternion', frame=f + 1, group=bone.name)
        for moved in clips_kit.MOVED:
            arm.pose.bones[moved].keyframe_insert('location', frame=f + 1, group=moved)
    data.action = None
    track = data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 1, clip)
    if hasattr(strip, 'action_slot') and clip.slots:
        strip.action_slot = clip.slots[0]
    track.mute = True


def build():
    files = []
    for key in clips_kit.MASTER:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        scene.render.fps = FPS
        arm, idle = clips_kit.load_pack(key)
        rest = clips_kit.freeze_idle(scene, arm, idle)
        feet = body.feet_of(arm)
        arm.name = clips_kit.RIG
        arm.animation_data_create()
        for name, (duration, keys) in CLIPS.items():
            bake(arm, rest, feet, name, duration, keys)
        path = OUT / f'Alarma_NpcReactions_{key}.fbx'
        clips_kit.export(arm, path)
        files.append(dict(pack=key, file=path.name))
    roles = [dict(id=role, pack=pack) for role, pack in clips_kit.role_packs().items()]
    manifest = dict(rig=clips_kit.RIG, fps=FPS, files=files, roles=roles, clips=[dict(id=name, loop=False) for name in CLIPS])
    (OUT / 'npc_reaction_clips.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding='utf-8')
    print('REACCIONES', len(CLIPS), [f['file'] for f in files])


def review():
    # Lo mismo que verá Unity: el FBX exportado, evaluado en su esqueleto y copiado al civil, en seis cuadros por clip.
    scene, cam, label = body.setup_scene()
    arm, _ = body.prepare_character(scene, REVIEW)
    before = set(bpy.data.actions)
    loaded = body.load(OUT / 'Alarma_NpcReactions_Men.fbx')
    source = next(o for o in loaded if o.type == 'ARMATURE')
    source.hide_render = True
    actions = {a.name.split('|')[-1]: a for a in bpy.data.actions if a not in before}
    # El celular en la palma, como lo coloca Unity.
    phone = next(o for o in body.load(PHONE) if o.type == 'MESH')
    bpy.context.view_layer.update()
    phone_base = phone.matrix_world.copy()
    chest = arm.matrix_world @ arm.pose.bones['Chest'].head
    look = chest - Vector((0, 0, .5))
    views = [look + Vector((-1.4, -1.9, .3)), look + Vector((-2.3, .05, 0))]
    for name in CLIPS:
        clip = actions[name]
        body.play(source, clip)
        start, end = clip.frame_range
        times = [i / 5 for i in range(6)]
        paths = [[], []]
        for k, t in enumerate(times):
            frame = start + t * (end - start)
            scene.frame_set(int(frame), subframe=frame - int(frame))
            body.copy_pose(source, arm)
            phone.hide_render = name not in PHONE_CLIPS
            held = phone_matrix(arm, 'film')
            if name == 'Llamar':  # se acomoda al agarre de hablar al empezar el clip
                call, k_grip = phone_matrix(arm, 'call'), ease(0.0, 1.0, min(1.0, t / REGRIP))
                turn = held.to_quaternion().slerp(call.to_quaternion(), k_grip).to_matrix().to_4x4()
                turn.translation = held.translation.lerp(call.translation, k_grip)
                held = turn
            phone.matrix_world = held @ Matrix.Scale(PHONE_SCALE, 4) @ phone_base
            label.data.body = f'{name}  t={t:.1f}'
            for v, eye in enumerate(views):
                cam.location = eye
                cam.rotation_euler = (look - eye).to_track_quat('-Z', 'Y').to_euler()
                path = body.OUT / f'_npc_{name}_{v}_{k}.png'
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                paths[v].append(path)
        body.sheet(paths[0] + paths[1], len(times), 'npc_' + name)
        if name in PHONE_CLIPS:
            # De cerca, en la postura final: desde atrás del hombro (se ve la pantalla), de frente y de los dos costados.
            face = arm.matrix_world @ arm.pose.bones['Head'].head + Vector((-.06, -.1, .05))
            close = []
            for v, offset in enumerate(((.25, .75, .2), (-.3, -.85, .1), (-.9, -.05, .1), (.9, -.2, .1))):
                cam.location = face + Vector(offset)
                cam.rotation_euler = (face - cam.location).to_track_quat('-Z', 'Y').to_euler()
                label.data.body = f'{name}  celular {v + 1}'
                path = body.OUT / f'_npc_{name}_cerca_{v}.png'
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                close.append(path)
            body.sheet(close, len(close), 'npc_' + name + '_celular')
    print('REVISION', list(CLIPS))


if '--solo-revision' not in sys.argv:
    build()
review()
