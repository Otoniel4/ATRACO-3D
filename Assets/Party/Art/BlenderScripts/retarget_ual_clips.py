"""Pasa clips de la Universal Animation Library de Quaternius (CC0) al esqueleto del elenco.

La biblioteca viene sobre un esqueleto humanoide universal (pelvis, spine_01…); el elenco usa el de los packs Ultimate
Modular (Body, Abdomen…). Los dos descansan en T, así que cada hueso copia el giro del hueso equivalente respecto de
su reposo. La cadera se ubica según el largo de pierna de cada pack para que los pies lleguen al suelo, y cada pie va
pegado al final de su pierna (en el elenco los pies cuelgan de la raíz, no de la pierna). Los dedos quedan como en el
reposo del pack.
Uso: blender -b --factory-startup -P retarget_ual_clips.py
Entrada: Art/ThirdParty~/Quaternius_UAL/Universal Animation Library[Standard]/Unity/UAL1_Standard.fbx
Salida: Art/Characters/Animations/Alarma_Locomotion_Men.fbx, _Women.fbx (solo esqueleto y clips), locomotion_clips.json
y Previews~/acciones/ual_<clip>.png (revisión sobre el civil NPC01 con el FBX exportado).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_action_clips as clips_kit  # noqa: E402
import preview_item_actions as body  # noqa: E402

SOURCE = clips_kit.ART / 'ThirdParty~' / 'Quaternius_UAL' / 'Universal Animation Library[Standard]' / 'Unity' / 'UAL1_Standard.fbx'
OUT = clips_kit.OUT
FPS = clips_kit.FPS
REVIEW = body.CAST.parent / 'NPC01_Bomber.fbx'
# Clip de la biblioteca → nombre en el juego y si se repite en bucle.
CLIPS = {
    'Idle_Loop': ('Quieto', True),
    'Idle_Talking_Loop': ('Conversar', True),
    'Walk_Loop': ('Caminar', True),
    'Walk_Formal_Loop': ('CaminarFormal', True),
    'Jog_Fwd_Loop': ('Trotar', True),
    'Sprint_Loop': ('Correr', True),
    'Crouch_Idle_Loop': ('AgachadoQuieto', True),
    'Crouch_Fwd_Loop': ('AgachadoCaminar', True),
    'Sitting_Enter': ('Sentarse', False),
    'Sitting_Idle_Loop': ('Sentado', True),
    'Sitting_Talking_Loop': ('SentadoConversar', True),
    'Sitting_Exit': ('Pararse', False),
}
# Hueso del elenco ← hueso de la biblioteca, de padre a hijo.
SPINE = [('Body', 'pelvis'), ('Hips', 'pelvis'), ('Abdomen', 'spine_01'), ('Torso', 'spine_02'), ('Chest', 'spine_03'),
         ('Neck', 'neck_01'), ('Head', 'Head')]
LIMBS = [('Shoulder.{S}', 'clavicle_{s}'), ('UpperArm.{S}', 'upperarm_{s}'), ('LowerArm.{S}', 'lowerarm_{s}'),
         ('Wrist.{S}', 'hand_{s}'), ('UpperLeg.{S}', 'thigh_{s}'), ('LowerLeg.{S}', 'calf_{s}')]


def world(obj, turn, matrix):
    return turn @ obj.matrix_world @ matrix


class Retarget:
    def __init__(self, arm, src):
        self.arm, self.src = arm, src
        # La biblioteca mira hacia +Y y el elenco hacia -Y: se gira media vuelta para que coincidan frente y lados.
        toe = src.matrix_world @ src.data.bones['foot_l'].tail_local - src.matrix_world @ src.data.bones['foot_l'].head_local
        self.turn = Matrix.Rotation(math.pi, 4, 'Z') if toe.y > 0 else Matrix.Identity(4)
        left = (self.turn @ src.matrix_world @ src.data.bones['thigh_l'].head_local).x > 0
        sides = (('L', 'l'), ('R', 'r')) if left else (('L', 'r'), ('R', 'l'))
        self.pairs = list(SPINE)
        self.feet = []
        for big, small in sides:
            self.pairs += [(t.format(S=big), s.format(s=small)) for t, s in LIMBS]
            self.feet.append(('Foot.' + big, 'foot_' + small, 'LowerLeg.' + big))
        self.thighs = [('UpperLeg.' + big, 'thigh_' + small) for big, small in sides]
        rest_s = lambda name: world(src, self.turn, src.data.bones[name].matrix_local)
        rest_t = lambda name: arm.matrix_world @ arm.data.bones[name].matrix_local
        self.offset = {t: rest_s(s).to_quaternion().inverted() @ rest_t(t).to_quaternion()
                       for t, s in self.pairs + [(f, s) for f, s, _ in self.feet]}
        length = lambda a, upper, lower: (a.data.bones[upper].tail_local - a.data.bones[upper].head_local).length \
            + (a.data.bones[lower].tail_local - a.data.bones[lower].head_local).length
        self.scale = length(arm, 'UpperLeg.L', 'LowerLeg.L') / length(src, 'thigh_l', 'calf_l')
        ankles_s = [rest_s(s).to_translation() for _, s, _ in self.feet]
        ankles_t = [rest_t(f).to_translation() for f, _, _ in self.feet]
        self.stand_s = (ankles_s[0] + ankles_s[1]) / 2  # bajo el cuerpo, a la altura del tobillo
        self.stand_t = (ankles_t[0] + ankles_t[1]) / 2

    def turn_to(self, target, source):
        mw = self.arm.matrix_world
        bone = self.arm.pose.bones[target]
        spin = world(self.src, self.turn, self.src.pose.bones[source].matrix).to_quaternion() @ self.offset[target]
        bone.matrix = mw.inverted() @ (Matrix.Translation(mw @ bone.head) @ spin.to_matrix().to_4x4())
        bpy.context.view_layer.update()

    def pose(self, rest):
        arm, mw = self.arm, self.arm.matrix_world
        for bone in arm.pose.bones:
            bone.matrix_basis = rest[bone.name]
        bpy.context.view_layer.update()
        for target, source in self.pairs:
            self.turn_to(target, source)
            if target != 'Body':
                continue
            # Cadera: la de la biblioteca respecto de sus pies, a la escala de las piernas del elenco.
            hips_s = sum((world(self.src, self.turn, self.src.pose.bones[s].matrix).to_translation() for _, s in self.thighs), Vector()) / 2
            goal = self.stand_t + (hips_s - self.stand_s) * self.scale
            hips_t = sum((mw @ arm.pose.bones[t].head for t, _ in self.thighs), Vector()) / 2
            hips = arm.pose.bones['Body']
            hips.matrix = mw.inverted() @ (Matrix.Translation(goal - hips_t) @ (mw @ hips.matrix))
            bpy.context.view_layer.update()
        for foot, source, shin in self.feet:
            bone = arm.pose.bones[foot]
            spin = world(self.src, self.turn, self.src.pose.bones[source].matrix).to_quaternion() @ self.offset[foot]
            bone.matrix = mw.inverted() @ (Matrix.Translation(mw @ arm.pose.bones[shin].tail) @ spin.to_matrix().to_4x4())
            bpy.context.view_layer.update()


def bake(scene, arm, src, retarget, rest, action, name):
    body.play(src, action)
    start, end = (int(round(v)) for v in action.frame_range)
    clip = bpy.data.actions.new(name)
    data = arm.animation_data
    data.action = clip
    previous = {}
    for index, frame in enumerate(range(start, end + 1)):
        data.action = None  # la pose se arma a mano; el clip nuevo no debe pisarla al cambiar de cuadro
        scene.frame_set(frame)
        retarget.pose(rest)
        data.action = clip
        if hasattr(data, 'action_slot') and clip.slots:
            data.action_slot = clip.slots[0]
        for bone in arm.pose.bones:
            q = bone.rotation_quaternion.copy()
            if bone.name in previous and previous[bone.name].dot(q) < 0:
                q.negate()
                bone.rotation_quaternion = q
            previous[bone.name] = q
            bone.keyframe_insert('rotation_quaternion', frame=index + 1, group=bone.name)
        for moved in clips_kit.MOVED:
            arm.pose.bones[moved].keyframe_insert('location', frame=index + 1, group=moved)
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
        for bone in arm.pose.bones:  # las piernas copian giros: el IK del pack no debe recalcularlas
            for constraint in bone.constraints:
                constraint.mute = True
        arm.name = clips_kit.RIG
        arm.animation_data_create()
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(SOURCE))
        src = next(o for o in bpy.data.objects if o not in before and o.type == 'ARMATURE')
        actions = {a.name.split('|')[-1]: a for a in bpy.data.actions}
        retarget = Retarget(arm, src)
        for source, (name, _) in CLIPS.items():
            bake(scene, arm, src, retarget, rest, actions[source], name)
        for o in [o for o in bpy.data.objects if o not in before]:
            bpy.data.objects.remove(o, do_unlink=True)
        path = OUT / f'Alarma_Locomotion_{key}.fbx'
        clips_kit.export(arm, path)
        files.append(dict(pack=key, file=path.name))
    roles = [dict(id=role, pack=pack) for role, pack in clips_kit.role_packs().items()]
    manifest = dict(rig=clips_kit.RIG, fps=FPS, source='Quaternius Universal Animation Library (CC0)', files=files, roles=roles,
                    clips=[dict(id=name, source=source, loop=loop) for source, (name, loop) in CLIPS.items()])
    (OUT / 'locomotion_clips.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding='utf-8')
    print('LOCOMOCION', len(CLIPS), [f['file'] for f in files])


def review():
    # Lo mismo que verá Unity: el FBX exportado, evaluado en su esqueleto y copiado al civil, en seis cuadros por clip.
    scene, cam, label = body.setup_scene()
    arm, _ = body.prepare_character(scene, REVIEW)
    before = set(bpy.data.actions)
    loaded = body.load(OUT / 'Alarma_Locomotion_Men.fbx')
    source = next(o for o in loaded if o.type == 'ARMATURE')
    source.hide_render = True
    actions = {a.name.split('|')[-1]: a for a in bpy.data.actions if a not in before}
    chest = arm.matrix_world @ arm.pose.bones['Chest'].head
    look = chest - Vector((0, 0, .5))
    views = [look + Vector((-1.4, -1.9, .3)), look + Vector((-2.3, .05, 0))]
    for name, _ in CLIPS.values():
        clip = actions[name]
        body.play(source, clip)
        start, end = clip.frame_range
        times = [i / 5 for i in range(6)]
        paths = [[], []]
        for k, t in enumerate(times):
            frame = start + t * (end - start)
            scene.frame_set(int(frame), subframe=frame - int(frame))
            body.copy_pose(source, arm)
            label.data.body = f'{name}  t={t:.1f}'
            for v, eye in enumerate(views):
                cam.location = eye
                cam.rotation_euler = (look - eye).to_track_quat('-Z', 'Y').to_euler()
                path = body.OUT / f'_ual_{name}_{v}_{k}.png'
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                paths[v].append(path)
        body.sheet(paths[0] + paths[1], len(times), 'ual_' + name)
    print('REVISION', [name for name, _ in CLIPS.values()])


build()
review()
