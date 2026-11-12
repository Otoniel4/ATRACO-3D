"""Postura de alcance al mostrador: compara el pliegue en un solo hueso (R40) con la bisagra de cadera repartida (R46).
Usa los FBX reales del elenco y el mismo criterio de PedestrianReach. Previsualización Blender; no ejecuta Unity."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Quaternion
H = Path(__file__).resolve().parent; ART = H.parents[1]
contacts = json.loads((H.parent / 'CounterContact40~' / 'contacts.json').read_text())
helper = ART / 'BlenderScripts/HideoutB1Fix~/DoorReview36~/verify_contacts.py'
scope = {'__file__': str(helper)}; exec(helper.read_text().split('for path in sorted', 1)[0], scope)
turn, frame = scope['turn'], scope['frame']; up = Vector((0, 0, 1))
# Reparto de la inclinación: cadera, abdomen y torso (suma 1) y cuánto la compensa el cuello para seguir mirando la tarea.
CHAIN = (('Hips', .45), ('Abdomen', .30), ('Torso', .25)); NECK = .45; STEP = 2; LIMIT = 48
# Cuánto acompaña el brazo libre a la inclinación (0 = cuelga vertical y se mete en el mueble; 1 = pegado al cuerpo).
FREE = float(__import__('os').environ.get('FREE', '.7'))

def rig_setup(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path))
    imported = set(bpy.data.objects) - before; rig = next(o for o in imported if o.type == 'ARMATURE')
    for obj in imported:
        if obj.name.startswith('ShoppingBag_'): obj.hide_render = True
        if obj.animation_data:
            for t in obj.animation_data.nla_tracks: t.mute = True
            action = next((a for a in bpy.data.actions if a.name.startswith(obj.name.split('.')[0] + '|Idle')), None)
            obj.animation_data.action = action
            if action and action.slots: obj.animation_data.action_slot = action.slots[0]
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update(); rig.animation_data_clear()
    return rig, imported

def shoulder_at(points, shoulder, axis, angle, chain):
    """Hombro después de girar cada hueso de la cadena su parte del ángulo, alrededor del mismo eje."""
    offset = shoulder - points[-1]
    for index in range(len(chain) - 1, -1, -1):
        offset = Quaternion(axis, math.radians(angle * chain[index][1])) @ offset
        if index: offset += points[index] - points[index - 1]
    return points[0] + offset

def solve(rig, target, forward, above, chain, neck, follow=0.):
    b = rig.pose.bones
    def p(n): return rig.matrix_world @ b[n].head
    def r(n): return (rig.matrix_world @ b[n].matrix).to_quaternion()
    fingers = p('Middle2.R') - p('Wrist.R'); normal = (p('Index2.R') - p('Pinky2.R')).cross(fingers).normalized()
    palm = p('Middle2.R') - fingers.normalized() * .025 + normal * .015
    offset = r('Wrist.R').inverted() @ (palm - p('Wrist.R')); local = r('Wrist.R').inverted() @ frame(fingers, normal)
    rotation = frame(forward, -up if above else up) @ local.inverted(); goal = target - rotation @ offset
    length = (p('UpperArm.R') - p('LowerArm.R')).length + (p('LowerArm.R') - p('Wrist.R')).length - .006
    axis = up.cross(forward.normalized())
    shoulder = p('UpperArm.R'); points = [p(name) for name, _ in chain]; angle = LIMIT
    for candidate in range(0, LIMIT + 1, STEP):
        if (goal - shoulder_at(points, shoulder, axis, candidate, chain)).length <= length: angle = candidate; break
    free = r('UpperArm.L'); head = r('Head')
    for name, share in chain:
        turn(rig, b[name], Quaternion(axis, math.radians(angle * share)) @ r(name))
    turn(rig, b['UpperArm.L'], free.slerp(r('UpperArm.L'), follow))
    if neck: turn(rig, b['Neck'], Quaternion(axis, math.radians(-angle * neck)) @ r('Neck'))
    shoulder = p('UpperArm.R'); elbow = p('LowerArm.R'); hand = p('Wrist.R')
    a = (elbow - shoulder).length; bb = (hand - elbow).length; reach = goal - shoulder; direction = reach.normalized()
    d = max(abs(a - bb) + .001, min(a + bb - .001, reach.length)); along = (a * a - bb * bb + d * d) / (2 * d)
    # R46: codo abajo, algo afuera y atrás (igual que PedestrianReach al sostener objetos); antes seguía la pose del clip.
    side = up.cross(forward.normalized()) * -1
    bend = (-up + side * .45 - forward.normalized() * .25) if neck else (elbow - shoulder); bend -= direction * bend.dot(direction)
    new_elbow = shoulder + direction * along + bend.normalized() * math.sqrt(max(0, a * a - along * along))
    turn(rig, b['UpperArm.R'], (elbow - shoulder).rotation_difference(new_elbow - shoulder) @ r('UpperArm.R'))
    turn(rig, b['LowerArm.R'], (p('Wrist.R') - p('LowerArm.R')).rotation_difference(goal - p('LowerArm.R')) @ r('LowerArm.R'))
    turn(rig, b['Wrist.R'], rotation)
    return (p('Wrist.R') + rotation @ offset - target).length, angle

def material(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1); return m

OLD = (('Abdomen', 1.),)
actors = sorted((ART / 'Characters/Cast').glob('NPC*.fbx'))
rows = []
# Medición: los diez personajes, seis mostradores, dinero (12 cm sobre el tablero) y producto tomado desde arriba.
heights = json.loads((H.parent / 'CounterContact40~' / 'product-heights.json').read_text())
for path in actors:
    for kind, data in contacts.items():
        for height, above in ((0., False), (.12, False), (heights[kind], True)):
            for label, chain, neck in (('antes', OLD, 0), ('ahora', CHAIN, NECK)):
                bpy.ops.wm.read_factory_settings(use_empty=True); rig, _ = rig_setup(path); b = rig.pose.bones
                def p(n): return rig.matrix_world @ b[n].head
                right = p('UpperArm.R') - p('UpperArm.L'); right.z = 0; right.normalize(); forward = up.cross(right)
                lateral = p('UpperArm.R').dot(right)
                target = right * lateral + forward * (data['width'] / 2 + .255) + up * (data['center'][1] - .1 + height)
                error, angle = solve(rig, target, forward, above, chain, neck, FREE if label == 'ahora' else 0.)
                edge = data['width'] / 2 + .255 - data['width'] / 2; top = data['center'][1] - .1
                tips = [p(n) for n in ('Wrist.L', 'Middle2.L')]
                inside = max((min(t.dot(forward) - edge, top - t.z) for t in tips))
                rows.append(dict(npc=path.stem, shop=kind, height=round(height, 3), above=above, mode=label, error=error, lean=angle, free_inside=inside,
                                 largest=max(angle * share for _, share in chain)))
(H / 'posture-results.json').write_text(json.dumps(rows, indent=1) + '\n')
for label in ('antes', 'ahora'):
    mine = [x for x in rows if x['mode'] == label]
    print('RESUMEN', label, 'error máx %.4f' % max(x['error'] for x in mine), 'inclinación total máx', max(x['lean'] for x in mine),
          'mayor giro de un solo hueso %.1f' % max(x['largest'] for x in mine),
          'mano libre dentro del mueble (m) %.3f' % max(x['free_inside'] for x in mine))

# Imágenes: el peor caso (supermercado, dinero) con dos personajes; a la izquierda antes, a la derecha ahora.
for shot, path in enumerate((actors[0], actors[1])):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    data = contacts['supermercado']; gray = material('Mostrador', (.25, .28, .32)); mark = material('Contacto', (1, .45, .1))
    for column, (chain, neck) in enumerate(((OLD, 0), (CHAIN, NECK))):
        rig, objects = rig_setup(path); b = rig.pose.bones
        def p(n): return rig.matrix_world @ b[n].head
        right = p('UpperArm.R') - p('UpperArm.L'); right.z = 0; right.normalize(); forward = up.cross(right)
        root = bpy.data.objects.new('Persona', None); bpy.context.scene.collection.objects.link(root)
        for obj in objects:
            if obj.parent is None: obj.parent = root
        root.location = forward * (column * 2.2); bpy.context.view_layer.update()
        lateral = (p('UpperArm.R') - root.location).dot(right)
        target = root.location + right * lateral + forward * (data['width'] / 2 + .255) + up * (data['center'][1] - .1 + .12)
        solve(rig, target, forward, False, chain, neck, FREE if column else 0.)
        top = data['center'][1] - .1
        bpy.ops.mesh.primitive_cube_add(size=1, location=root.location + forward * (data['width'] / 2 + .255) + up * (top / 2))
        box = bpy.context.object; box.scale = (1.6, data['width'], top); box.data.materials.append(gray)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.025, location=target); bpy.context.object.data.materials.append(mark)
    scene = bpy.context.scene
    camera = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara')); scene.collection.objects.link(camera); scene.camera = camera
    middle = forward * 1.4 + up * .95
    camera.location = middle + right * 6; camera.rotation_euler = (middle - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'; camera.data.ortho_scale = 4.2
    scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.light = 'STUDIO'; scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True; scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'; scene.world = bpy.data.worlds.new('Fondo'); scene.world.color = (.22, .24, .27)
    scene.render.resolution_x = 1300; scene.render.resolution_y = 650; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.filepath = str(H / ('postura_%d.png' % shot)); bpy.ops.render.render(write_still=True)
