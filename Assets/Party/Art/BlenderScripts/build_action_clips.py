"""Clips de cuerpo completo para usar cada objeto, para la capa «Acciones» del Animator de Unity.

Se hacen con bpy sobre el mismo esqueleto del pack Quaternius (CC0) del que sale el elenco (Men y Women), porque
reimportar el FBX del elenco cambia la orientación de los huesos y los clips se verían torcidos.
Cada cuadro arma la pose con los datos del juego (Data/Items/item_actions.json y HoldPoses.asset): torso inclinado
desde el abdomen, cadera que baja con rodillas dobladas y pies fijos (IK), cabeza que mira el trabajo, objeto en la
mano con IK de los dos brazos y mano izquierda libre cuando no está en el agarre. Es la misma cuenta que usa Unity,
así que el clip y el objeto en la mano coinciden.
Uso: blender -b --factory-startup -P build_action_clips.py
Salida: Art/Characters/Animations/Alarma_ItemActions_Men.fbx, _Women.fbx (solo esqueleto y clips) e
item_action_clips.json (qué archivo usa cada personaje). Revisión: preview_item_actions.py dibuja los clips exportados.
"""
import json
import re
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import preview_item_actions as preview  # noqa: E402

ART = HERE.parent
PACKS = ART / 'ThirdParty~' / 'Quaternius_Modular'
MASTER = {'Men': PACKS / 'Men' / 'Ultimate Modular Men- Feb 2022' / 'All together' / 'Blends' / 'Humans_Master.blend',
          'Women': PACKS / 'Women' / 'Ultimate Modular Women - April 2022' / 'All together' / 'Blends' / 'All together.blend'}
OUT = ART / 'Characters' / 'Animations'
RIG = 'Acciones_Rig'  # Unity cambia este nombre por el del esqueleto de cada personaje (<id>_Rig)
FPS = 30
MOVED = ('Body', 'Foot.L', 'Foot.R')  # huesos que además de girar se desplazan (Unity copia solo estas posiciones)


def load_pack(key):
    # Solo el esqueleto y la animación de reposo del .blend maestro, sin modificar el archivo.
    with bpy.data.libraries.load(str(MASTER[key]), link=False) as (src, dst):
        dst.objects = ['CharacterArmature']
        dst.actions = [name for name in src.actions if name.split('|')[-1] == 'Idle_Neutral']
    arm = dst.objects[0]
    bpy.context.scene.collection.objects.link(arm)
    return arm, dst.actions[0]


def freeze_idle(scene, arm, idle):
    # Base de todos los clips: el primer cuadro del reposo, el mismo con que empieza la locomoción del elenco.
    data = arm.animation_data_create()
    data.action = idle
    if hasattr(data, 'action_slot') and idle.slots:
        data.action_slot = idle.slots[0]
    scene.frame_set(int(idle.frame_range[0]))
    bpy.context.view_layer.update()
    frozen = {b.name: b.matrix.copy() for b in arm.pose.bones}
    data.action = None
    for b in sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive)):
        b.rotation_mode = 'QUATERNION'
        b.matrix = frozen[b.name]
        bpy.context.view_layer.update()
    return {b.name: b.matrix_basis.copy() for b in arm.pose.bones}


def load_item(spec):
    loaded = preview.load(ART / 'Weapons' / f"{spec['model']}.fbx")
    root = next(o for o in loaded if o.parent is None)
    grip_r = next(o for o in loaded if o.name.startswith('Grip_R'))
    grip_l = next((o for o in loaded if o.name.startswith('Grip_L')), None)
    bpy.context.view_layer.update()
    return loaded, (root, grip_r, grip_l, root.matrix_world.to_quaternion())


def bake(scene, arm, rest, feet, action, spec, pose):
    loaded, item = load_item(spec)
    frames = max(2, round(action['duration'] * FPS))
    clip = bpy.data.actions.new(action['id'])
    data = arm.animation_data
    data.action = clip
    previous = {}
    for f in range(frames + 1):
        preview.pose_frame(arm, rest, item, pose, spec, action, f / frames, feet)
        for b in arm.pose.bones:
            q = b.rotation_quaternion.copy()
            if b.name in previous and previous[b.name].dot(q) < 0:
                q.negate()  # mismo giro con el signo continuo: evita vueltas raras entre cuadros
                b.rotation_quaternion = q
            previous[b.name] = q
            b.keyframe_insert('rotation_quaternion', frame=f + 1, group=b.name)
        for name in MOVED:  # la cadera baja y los pies dan el paso o apoyan la rodilla
            arm.pose.bones[name].keyframe_insert('location', frame=f + 1, group=name)
    data.action = None
    track = data.nla_tracks.new()
    track.name = action['id']
    strip = track.strips.new(action['id'], 1, clip)
    if hasattr(strip, 'action_slot') and clip.slots:
        strip.action_slot = clip.slots[0]
    track.mute = True
    for o in loaded:
        bpy.data.objects.remove(o, do_unlink=True)
    return frames


def bake_rest(arm, rest):
    # Clip de referencia «Reposo» (el primer cuadro del reposo): preview_item_actions.py lo compara con el Idle del
    # elenco para comprobar que los clips se leen igual que los del personaje. Unity no lo usa.
    data = arm.animation_data
    clip = bpy.data.actions.new('Reposo')
    data.action = clip
    for f in (1, 2):
        for b in arm.pose.bones:
            b.matrix_basis = rest[b.name]
            b.keyframe_insert('rotation_quaternion', frame=f, group=b.name)
        for name in MOVED:
            arm.pose.bones[name].keyframe_insert('location', frame=f, group=name)
    data.action = None
    track = data.nla_tracks.new()
    track.name = 'Reposo'
    strip = track.strips.new('Reposo', 1, clip)
    if hasattr(strip, 'action_slot') and clip.slots:
        strip.action_slot = clip.slots[0]
    track.mute = True


def export(arm, path):
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        o.select_set(o == arm)
    bpy.context.view_layer.objects.active = arm
    for t in arm.animation_data.nla_tracks:
        t.mute = False
    # Mismos ajustes que el elenco (ModularCast~/build_cast.py) para que los huesos coincidan en Unity.
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'ARMATURE'}, global_scale=1,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=False, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
                             bake_anim_use_nla_strips=True, bake_anim_simplify_factor=1, bake_anim_step=1)


def role_packs():
    source = (HERE / 'ModularCast~' / 'build_cast.py').read_text(encoding='utf-8')
    return dict(re.findall(r"dict\(id='(\w+)', playtest='\w+', pack='(\w+)'", source))


def main():
    actions = [a for a in json.loads((preview.ITEMS / 'item_actions.json').read_text(encoding='utf-8'))['actions'] if a.get('clip')]
    poses, specs = preview.hold_poses(), preview.item_specs()
    OUT.mkdir(parents=True, exist_ok=True)
    files, clips = [], []
    for key in MASTER:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        scene.render.fps = FPS
        arm, idle = load_pack(key)
        rest = freeze_idle(scene, arm, idle)
        feet = preview.feet_of(arm)
        arm.name = RIG
        clips = []
        bake_rest(arm, rest)
        for action in actions:
            spec = specs[action['id']]
            frames = bake(scene, arm, rest, feet, action, spec, poses[spec['style']])
            clips.append(dict(id=action['id'], animationId=action['animationId'], fullBody=action.get('fullBody', False),
                              loop=action['repeat'], frames=frames))
        path = OUT / f'Alarma_ItemActions_{key}.fbx'
        export(arm, path)
        files.append(dict(pack=key, file=path.name))
    roles = [dict(id=role, pack=pack) for role, pack in role_packs().items()]
    manifest = dict(rig=RIG, fps=FPS, files=files, roles=roles, clips=clips)
    (OUT / 'item_action_clips.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding='utf-8')
    print('CLIPS', len(clips), files)


# Sus funciones también las usa build_npc_reaction_clips.py.
if __name__ == '__main__':
    main()
