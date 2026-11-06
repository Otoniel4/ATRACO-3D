"""Revisión de cómo se sostienen las armas y herramientas, antes de probar en Unity.

Reproduce lo que hace HeldItemView: el objeto va frente al pecho del personaje con la pose de su forma de sostener
(mismos valores por defecto que HoldPoseLibrary.cs) y los brazos llegan a Grip_R y Grip_L con IK de dos huesos.
Si se cambian las poses en Unity, actualizar POSES aquí para volver a revisar.
Uso: blender -b --factory-startup -P preview_hold_poses.py
Salida: Previews~/sostener_*.png
"""
import math
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

ART = Path(__file__).resolve().parent.parent
CAST = ART / 'Characters' / 'Cast' / 'Player01_Thief.fbx'
# Unity: x derecha, y arriba, z adelante; giro en grados (x inclina la punta hacia abajo, y gira a la derecha).
POSES = {  # posición, giro, dedos derecha, dedos izquierda (ejes del objeto en Unity)
    'Pistol': ((.05, -.2, .34), (14, 0, 0), (-1, 0, .35), (1, -.2, .3)),
    'Long': ((.12, -.12, .14), (8, -25, 0), (-1, 0, .35), (.9, .4, .2)),
    'OneHandUpright': ((.2, -.36, .16), (100, 0, 0), (-1, 0, .3), (1, 0, .3)),
    'OneHandPointing': ((.2, -.36, .2), (25, 0, 0), (-1, 0, .3), (1, 0, .3)),
    'TwoHandTablet': ((.12, -.18, .3), (-55, 0, 0), (-1, -.3, 0), (1, -.3, 0)),
    'TwoHandCanister': ((.05, -.24, .28), (0, 0, 0), (-.3, 0, 1), (.3, 0, 1)),
    # Apuntando con clic derecho (aimOffset/aimEuler de HoldPoseLibrary).
    'PistolAim': ((.06, .06, .42), (0, 0, 0), (-1, 0, .35), (1, -.2, .3)),
    'LongAim': ((.11, .03, .09), (0, -8, 0), (-1, 0, .35), (.9, .4, .2)),
}
SHOTS = [('Weapon_Pistol', 'Pistol'), ('Weapon_Shotgun', 'Long'), ('Weapon_Rifle', 'Long'), ('Tool_Drill', 'Pistol'),
         ('Tool_Crowbar', 'OneHandUpright'), ('Tool_HackingTablet', 'TwoHandTablet'), ('Tool_ThermiteCharge', 'TwoHandCanister'),
         ('Tool_Lockpick', 'OneHandPointing'), ('Weapon_Pistol', 'PistolAim'), ('Weapon_Rifle', 'LongAim')]


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


def solve(arm, upper, lower, palm_offset, target, bend):
    # Mismo IK de dos huesos que TwoBoneIk.cs, sobre los huesos de pose de Blender.
    mw = arm.matrix_world
    pu, pl = arm.pose.bones[upper], arm.pose.bones[lower]
    shoulder, elbow0, wrist0 = mw @ pu.head, mw @ pl.head, mw @ pl.tail
    a, b = (elbow0 - shoulder).length, (wrist0 - elbow0).length + palm_offset
    reach = target - shoulder
    direction = reach.normalized()
    d = max(min(reach.length, a + b - .001), abs(a - b) + .001)
    along = (a * a - b * b + d * d) / (2 * d)
    side = bend - direction * bend.dot(direction)
    elbow = shoulder + direction * along + side.normalized() * math.sqrt(max(0, a * a - along * along))
    hand = elbow + (target - elbow).normalized() * (b - palm_offset)
    # Se escribe la pose en espacio de mundo hueso por hueso (brazo y luego antebrazo).
    for bone, head, tail in ((pu, shoulder, elbow), (pl, elbow, hand)):
        y = (tail - head).normalized()
        current = mw @ bone.matrix
        z = (current.to_3x3() @ Vector((0, 0, 1)))
        x = y.cross(z).normalized()
        z = x.cross(y).normalized()
        rot = Matrix((x, y, z)).transposed().to_4x4()
        world = Matrix.Translation(head) @ rot
        bone.matrix = mw.inverted() @ world
        bpy.context.view_layer.update()
    wrist, elbow_now = mw @ pl.tail, mw @ pl.head
    palm = wrist + (wrist - elbow_now).normalized() * palm_offset
    return palm, (palm - target).length


def palm_of(arm, wrist, lower):
    mw = arm.matrix_world
    w, e = mw @ arm.pose.bones[wrist].head, mw @ arm.pose.bones[lower].head
    t = mw @ arm.pose.bones[wrist].tail
    return w + (t - w).normalized() * .06


def point_fingers(arm, wrist, lower, item, fingers):
    # Igual que HeldItemView: gira la muñeca para que los dedos (muñeca → palma) apunten a «fingers» en ejes del objeto.
    mw = arm.matrix_world
    bone = arm.pose.bones[wrist]
    head, tail = mw @ bone.head, mw @ bone.tail
    x, y, z = fingers
    desired = (item.matrix_world.to_quaternion() @ Vector((-x, -z, y))).normalized()  # Unity → Blender
    turn = (tail - head).normalized().rotation_difference(desired)
    world = mw @ bone.matrix
    rotated = Matrix.Translation(head) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-head) @ world
    bone.matrix = mw.inverted() @ rotated
    bpy.context.view_layer.update()


def render(scene, cam, name):
    scene.render.filepath = str(ART / 'Previews~' / f'sostener_{name}.png')
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    world = bpy.data.worlds.new('Cielo')
    world.color = (.66, .74, .82)
    scene.world = world
    scene.view_settings.view_transform = 'Standard'
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x, scene.render.resolution_y = 900, 1000
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = 50
    report = []
    for model, style in SHOTS:
        for o in list(bpy.data.objects):
            if o is not cam:
                bpy.data.objects.remove(o, do_unlink=True)
        body = load(CAST)
        arm = next(o for o in body if o.type == 'ARMATURE')
        for o in body:
            if o.name.startswith('ShoppingBag'):
                o.hide_render = True
        # La animación importada pisaría la pose: se congela el primer cuadro de la pista de reposo y se quita la animación.
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
        mw = arm.matrix_world
        chest = mw @ arm.pose.bones['Chest'].head
        # El personaje mira a -Y en Blender: derecha = -X, adelante = -Y, arriba = +Z.
        right, forward, up = Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))
        (ox, oy, oz), (pitch, yaw, roll), fingers_r, fingers_l = POSES[style]
        target = chest + right * ox + up * oy + forward * oz
        item = load(ART / 'Weapons' / f'{model}.fbx')
        root = next(o for o in item if o.parent is None)
        grip_r = next(o for o in item if o.name.startswith('Grip_R'))
        grip_l = next((o for o in item if o.name.startswith('Grip_L')), None)
        root.rotation_mode = 'XYZ'
        base = root.matrix_world.to_quaternion()
        turn = Euler((math.radians(pitch), 0, math.radians(-yaw)), 'ZXY').to_quaternion()
        root.rotation_euler = (turn @ base).to_euler()
        bpy.context.view_layer.update()
        root.location += target - grip_r.matrix_world.translation
        bpy.context.view_layer.update()
        palm, error_r = solve(arm, 'UpperArm.R', 'LowerArm.R', .06, target, right * .7 - up)
        point_fingers(arm, 'Wrist.R', 'LowerArm.R', root, fingers_r)
        palm = palm_of(arm, 'Wrist.R', 'LowerArm.R')
        root.location += palm - grip_r.matrix_world.translation  # el objeto sigue a la palma real
        bpy.context.view_layer.update()
        error_l = solve(arm, 'UpperArm.L', 'LowerArm.L', .06, grip_l.matrix_world.translation, -right * .7 - up)[1] if grip_l else 0.0
        if grip_l:
            point_fingers(arm, 'Wrist.L', 'LowerArm.L', root, fingers_l)
        report.append((model, round(error_r, 3), round(error_l, 3)))
        eye = chest + Vector((-1.1, -1.6, .2))
        cam.location = eye
        cam.rotation_euler = (chest - Vector((0, 0, .25)) - eye).to_track_quat('-Z', 'Y').to_euler()
        render(scene, cam, model + ('_apuntando' if style.endswith('Aim') else ''))
    print('SOSTENER', report)


# Las funciones de arriba también las usa preview_item_actions.py.
if __name__ == '__main__':
    main()
