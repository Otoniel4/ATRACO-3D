"""Mide el alcance de la palma en los FBX reales sin guardar escenas ni alterar modelos."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

ART = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ACTORS = sorted((ART / 'Characters/Cast').glob('Player0*.fbx'))
EXPECTED = 4
assert len(ACTORS) == EXPECTED, ACTORS
PARAMETERS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
GATE_OFFSET = float(PARAMETERS[0]) if PARAMETERS else .06
GATE_HEIGHT = float(PARAMETERS[1]) if len(PARAMETERS) > 1 else 1.12


def load_idle(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    action = next(a for a in bpy.data.actions if a.name.endswith('|Idle') or a.name == 'Idle')
    rig.animation_data_create()
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    rig.animation_data.action = action
    if getattr(action, 'slots', None):
        rig.animation_data.action_slot = action.slots[0]
    bpy.context.scene.frame_set(round(action.frame_range[0]))
    bpy.context.view_layer.update()
    return rig


def measure(path):
    rig = load_idle(path)
    shoulder = rig.matrix_world @ rig.pose.bones['UpperArm.R'].head
    other_shoulder = rig.matrix_world @ rig.pose.bones['UpperArm.L'].head
    elbow = rig.matrix_world @ rig.pose.bones['LowerArm.R'].head
    spine = rig.matrix_world @ rig.pose.bones['Abdomen'].head
    palm = next(o for o in bpy.data.objects if o.name.startswith('Grip_R6_')).matrix_world.translation
    length = (elbow - shoulder).length + (palm - elbow).length
    right = shoulder - other_shoulder
    right.z = 0
    right.normalize()
    up = Vector((0, 0, 1))
    forward = up.cross(right).normalized()
    radius = .31 if 'Muscle' in path.name else .24
    stand = max(.4, radius + .13)
    cases = []
    # Centro de hoja única y dos caras. En la cara contraria el contacto lateral cambia de signo.
    for width, offset, height in ((1.4, GATE_OFFSET, GATE_HEIGHT), (1.8, .15, 1.05)):
        usable = width * .5 - radius - .08
        for sign in (-1, 1):
            target = sign * offset
            lateral = max(-usable, min(usable, target + .22))
            point = right * (lateral - target) + forward * (stand - .03) + up * height
            direction = point - shoulder
            direction.z = 0
            axis = up.cross(direction.normalized())
            leaned = spine + Quaternion(axis, math.radians(7)) @ (shoulder - spine)
            gap = max(0, (point - leaned).length - length)
            cases.append(dict(width=width, side=sign, hand_gap=gap))
    return dict(role=path.stem, arm_length=length, shoulder=list(shoulder), elbow=list(elbow), cases=cases)


results = [measure(path) for path in ACTORS]
maximum = max(case['hand_gap'] for rig in results for case in rig['cases'])
assert maximum <= .035, (maximum, results)
report = dict(roles=results, cases=EXPECTED * 4, gate_lateral_offset=GATE_OFFSET,
              gate_height_above_feet=GATE_HEIGHT, max_estimated_gap=maximum, unity_play_tested=False)
(HERE / 'rig-reach-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('RIG_REACH_GEOMETRY', json.dumps(report))
