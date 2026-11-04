"""Elenco low-poly sobre los packs CC0 Ultimate Modular Men y Women de Quaternius.

Cada personaje combina cabeza, torso, piernas y pies del pack, recoloreados con colores planos,
y suma nuestros accesorios (cinturón, radio, porra, funda, gorras, antifaz, gafas, bigote, saco y rótulos).
Elenco: seguridad y policía (hombres, láminas 11 y 13), diez civiles (láminas 01-10) y los cuatro protagonistas.
Todos comparten el esqueleto y las 24 animaciones del pack. Se exporta en el formato del elenco de la prueba:
clips por nombre (Idle, Walk, Run, Browse, Pay, CarryWalk y extras), agarre y bolsa en la mano derecha.
Uso: blender -b --factory-startup -P build_cast.py
Salida: Art/Characters/Cast/*.fbx, su copia con el id de la prueba en PlaytestR9~/export/Characters,
ModularCast.blend, renders/*.png y report.json en esta carpeta.
"""
import bpy, bmesh, json, math, shutil
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

HERE = Path(__file__).resolve().parent
ART = HERE.parent.parent
PACKS = ART / 'ThirdParty~' / 'Quaternius_Modular'
MASTER = {'Men': PACKS / 'Men' / 'Ultimate Modular Men- Feb 2022' / 'All together' / 'Blends' / 'Humans_Master.blend',
          'Women': PACKS / 'Women' / 'Ultimate Modular Women - April 2022' / 'All together' / 'Blends' / 'All together.blend'}
EXPORT = ART / 'Characters' / 'Cast'
PLAYTEST = HERE.parent / 'PlaytestR9~'
RENDERS = HERE / 'renders'
UP = Vector((0, 0, 1))
FORWARD = Vector((0, -1, 0))  # el pack mira a -Y
LEFT = Vector((1, 0, 0))      # y su izquierda es +X
BACK = -FORWARD
# Modos que pide el elenco de la prueba; Browse, Pay y CarryWalk no existen en el pack y reutilizan Interact y Walk.
# El Idle del pack gira el cuerpo 27°; Idle_Neutral mira al frente, como el resto de clips.
CLIPS = {'Idle': 'Idle_Neutral', 'Walk': 'Walk', 'Run': 'Run', 'Browse': 'Interact', 'Pay': 'Interact', 'CarryWalk': 'Walk'}
# Clips extra del pack según el papel; los civiles solo llevan los del elenco para que el FBX pese poco.
EXTRA_CLIPS = {'civil': [],
               'guard': ['Interact', 'Punch_Left', 'Punch_Right', 'HitRecieve', 'Death'],
               'police': ['Idle_Gun', 'Idle_Gun_Pointing', 'Gun_Shoot', 'Run_Shoot', 'HitRecieve', 'Death'],
               'player': ['Interact', 'Wave', 'Punch_Left', 'Punch_Right', 'Roll', 'HitRecieve', 'Death']}
BELT = .008

CAST = [
    dict(id='Security_Male', playtest='NPC11_SecurityMale', pack='Men', clips='guard',
         parts=['Casual2_Head', 'Worker_Body', 'Swat_Legs', 'Swat_Feet'],
         colors={'Skin': '8A5A3C', 'Skin_Darker': '6B4430', 'Hair': '1C1512', 'Eyebrows': '1C1512',
                 'LightBrown': '3B3C40', 'Worker_Vest': '25262A', 'Worker_Yellow': 'F2C200',
                 'Swat': '1F2023', 'Swat_Black': '121214'},
         belt='111113', props=['radio_belt', 'baton'],
         label=dict(text='SEGURIDAD', back_patch='F2C200', back_ink='111113', chest_patch='F2C200', chest_ink='111113')),
    dict(id='Police_Male', playtest='NPC13_PoliceMale', pack='Men', clips='police',
         parts=['Suit_Head', 'Casual2_Body', 'Suit_Legs', 'Suit_Feet'],
         colors={'Skin': 'A06A48', 'Hair': '17110E', 'Eyebrows': '17110E', 'LightBrown': '83B2E6',
                 'Suit': '1E2847', 'Black': '131315'},
         belt='111113', cap='1E2847', epaulets='1E2847', props=['radio_belt', 'holster'],
         label=dict(text='POLICIA', back_patch=None, back_ink=None, chest_patch='1E2847', chest_ink='F2F2F2')),
    # Civiles según las láminas 01-10 de References~/NPC_V2.
    dict(id='NPC01_Bomber', playtest='NPC01_Bomber', pack='Men', clips='civil',
         parts=['Beach_Head', 'Casual_Body', 'Adventurer_Legs', 'Casual_Feet'],
         colors={'Skin': '8A5A3C', 'Hair': '1C1512', 'Eyebrows': '1C1512', 'Earrings': '8A5A3C', 'Casual_Body:Purple': 'E07B2E',
                 'Brown': '5E6B3A', 'Brown2': '4C5730', 'Casual_Feet:Purple': 'F2F2F2', 'Casual_Feet:White': 'D9D9D9'}),
    dict(id='NPC02_Denim', playtest='NPC02_Denim', pack='Women', clips='civil',
         parts=['Formad_Head', 'Suit_Body', 'Suit_Legs', 'Casual_Feet'],
         colors={'Skin': '5C3A28', 'Red': '151210', 'Suit_Body:Black': '4C7DA7', 'White': 'E8796A',
                 'Suit_Legs:Black': 'D2C2A0', 'Grey': '1F5C6B'}),
    dict(id='NPC03_Tourist', playtest='NPC03_Tourist', pack='Men', clips='civil',
         parts=['Casual_Head', 'Adventurer_Body', 'Beach_Legs', 'Casual2_Feet'],
         colors={'Skin': 'E3B79A', 'Hair': '6B4A2E', 'Eyebrows': '6B4A2E', 'Green': '2BB3B1', 'LightGreen': 'F2F2F2',
                 'Beach_Legs:Red_Dark': 'D8C39A', 'Beach_Legs:White': 'E9DFC7', 'Casual2_Feet:Red_Dark': 'D4A62A', 'Casual2_Feet:White': 'F2F2F2'}),
    dict(id='NPC04_Lavender', playtest='NPC04_Lavender', pack='Women', clips='civil',
         parts=['Soldier_Head', 'Casual_Body', 'Casual_Legs', 'Casual_Feet'],
         colors={'Skin': 'B27A52', 'Hair_Brown': '1A1412', 'White': 'B7A3D8', 'Orange': '3A3B40', 'Grey': 'B7A3D8'}),
    dict(id='NPC05_Burgundy', playtest='NPC05_Burgundy', pack='Men', clips='civil',
         parts=['Suit_Head', 'Casual_Body', 'Suit_Legs', 'Farmer_Feet'],
         colors={'Skin': '5C3A28', 'Hair': '0F0D0C', 'Eyebrows': '0F0D0C', 'Purple': '7B2335', 'Suit': 'B8B8B4',
                 'Brown': '6B4A2E', 'Brown2': '4E3521'}),
    dict(id='NPC06_Mechanic', playtest='NPC06_Mechanic', pack='Women', clips='civil',
         parts=['Adventurer_Head', 'Worker_Body', 'Worker_Legs', 'Soldier_Feet'],
         colors={'Skin': 'E8C2A0', 'Hair_Brown': 'B5642F', 'Worker_Vest': '8FA77F', 'Worker_Yellow': '8FA77F', 'White': 'F2CF3B',
                 'Brown_02': '8FA77F', 'Brown2': '7A9070', 'Grey': 'D2C2A0', 'Black': '8C7A5B'}),
    dict(id='NPC07_PaddedVest', playtest='NPC07_PaddedVest', pack='Men', clips='civil',
         parts=['Suit_Head', 'Worker_Body', 'Casual2_Legs', 'Worker_Feet'],
         colors={'Skin': 'B07850', 'Hair': '141110', 'Eyebrows': '141110', 'Worker_Vest': '1E2847', 'Worker_Yellow': '1E2847',
                 'LightBrown': 'D4A62A', 'LightBlue': '4A6FA5', 'Grey': '7F8186', 'Black': '3A3B40'}),
    dict(id='NPC08_Sport', playtest='NPC08_Sport', pack='Women', clips='civil',
         parts=['Casual_Head', 'Suit_Body', 'Soldier_Legs', 'Suit_Feet'],
         colors={'Skin': 'A06A48', 'Hair_Brown': '151210', 'Hair_Blond': '151210', 'Suit_Body:Black': 'F2F2F2', 'White': '3E8E4A',
                 'Grey': '6E1F2F', 'Soldier_Legs:Black': '4A1520', 'Swat': '5A1A28', 'Suit_Feet:Black': '151517'}),
    dict(id='NPC09_Flannel', playtest='NPC09_Flannel', pack='Men', clips='civil',
         parts=['Casual2_Head', 'Adventurer_Body', 'Suit_Legs', 'Casual2_Feet'],
         colors={'Skin': 'A8805C', 'Skin_Darker': '8C6A4A', 'Hair': '141110', 'Eyebrows': '141110', 'Green': '8E2B2B', 'LightGreen': '1D1D22',
                 'Suit': 'CDB894', 'Red_Dark': '6B4A2E', 'White': 'E9DFC7'}),
    dict(id='NPC10_Cardigan', playtest='NPC10_Cardigan', pack='Women', clips='civil',
         parts=['Soldier_Head', 'Suit_Body', 'Formal_Legs', 'Adventurer_Feet'],
         colors={'Skin': 'F0CDB4', 'Hair_Brown': '6B4A2E', 'Black': '8EC5E8', 'White': 'F1E6CF', 'LimeGreen': '2F4F3A',
                 'Brown_02': 'A0622D', 'Brown2': '7A4A22'}),
    # Protagonistas: Don Sigilo, Primo WiFi, Abuelita Falsa y Toñito (docs/LowPolyCast.md).
    dict(id='Player01_Thief', playtest='Player01_Thief', pack='Men', clips='player',
         parts=['Suit_Head', 'Casual_Body', 'Casual2_Legs', 'Casual2_Feet'],
         colors={'Skin': 'D9A57E', 'Hair': '151210', 'Eyebrows': '151210', 'Purple': '1D1D22', 'LightBlue': '2A2D34',
                 'Red_Dark': '18181B', 'White': 'D9D9D9'},
         extras=[('beanie', '151518'), ('mask', '111113'), ('sack', 'C8B48A')]),
    dict(id='Player02_Hacker', playtest='Player02_Hacker', pack='Men', clips='player',
         parts=['Casual_Head', 'Casual_Body', 'Casual_Legs', 'Casual_Feet', 'Backpack'],
         colors={'Skin': 'C68B62', 'Hair': '2B1D14', 'Eyebrows': '2B1D14', 'Casual_Body:Purple': '3E8E4A', 'LightBlue': '5A5F6B',
                 'Casual_Feet:Purple': '2E7D32', 'Brown': '2C3E50', 'LightGreen': '7FB069', 'Gold': 'D4A62A', 'Green': '3E8E4A'},
         cap='2E7D32', extras=[('antennas', 'D4A62A'), ('glasses', '1B1B1F')]),
    dict(id='Player03_Distractor', playtest='Player03_Distractor', pack='Women', clips='player',
         parts=['Casual_Head', 'Formal_Body', 'Formal_Legs', 'Formal_Feet'],
         colors={'Skin': 'E8C2A0', 'Hair_Brown': 'C9C9C9', 'Hair_Blond': 'B5B5B5', 'LimeGreen': 'A779B0', 'Gold': 'E5C76B', 'Red': '5A3D2B'},
         extras=[('glasses', 'DDE8EE'), ('moustache', '3A2A20')]),
    dict(id='Player04_Muscle', playtest='Player04_Muscle', pack='Men', clips='player', bulk=1.4,
         parts=['Beach_Head', 'Beach_Body', 'Adventurer_Legs', 'Worker_Feet'],
         colors={'Skin': 'B8865E', 'Hair': '1C1512', 'Eyebrows': '1C1512', 'Earrings': 'B8865E', 'LightBrown': 'C0392B',
                 'Brown': '4C5730', 'Brown2': '3C4526', 'Grey': '6B6E73', 'Black': '2B2C30'},
         extras=[('tiny_cap', 'C0392B')]),
]


def linear(hexcolor):
    c = [int(hexcolor[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c) + (1.0,)


def material(role, hexcolor, base=None):
    # Un material por color: los personajes comparten los iguales y Unity los crea con ese color plano.
    name = f'QM_{role}_{hexcolor}'
    m = bpy.data.materials.get(name)
    if m is None:
        m = base.copy() if base else bpy.data.materials.new(name)
        m.name = name
    color = linear(hexcolor)
    m.diffuse_color = color
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    return m


def link(obj, collection=None):
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def mesh_object(name, bm, materials):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = link(bpy.data.objects.new(name, me))
    for m in materials:
        obj.data.materials.append(m)
    return obj


def world_bvh(obj):
    M = obj.matrix_world
    return BVHTree.FromPolygons([M @ v.co for v in obj.data.vertices], [list(p.vertices) for p in obj.data.polygons])


def frame(normal):
    # Ejes de una pieza pegada a la superficie: Z sale de la tela, Y hacia arriba.
    z = normal.normalized()
    y = UP - z * UP.dot(z)
    y = y.normalized() if y.length > 1e-4 else FORWARD.copy()
    return y.cross(z), y, z


def box(center, axes, size):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    basis = Matrix((axes[0] * size[0], axes[1] * size[1], axes[2] * size[2])).transposed()
    for v in bm.verts:
        v.co = center + basis @ v.co
    return bm


def play(arm, action):
    # Las acciones del pack tienen ranuras (Blender 4.4+): sin elegir la ranura, el esqueleto no se mueve.
    arm.animation_data_create().action = action
    if action is not None and hasattr(arm.animation_data, 'action_slot') and action.slots:
        arm.animation_data.action_slot = action.slots[0]


def cylinder(center, axis, radius, length, segments=8):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=length)
    rot = axis.normalized().to_track_quat('Z', 'Y').to_matrix()
    for v in bm.verts:
        v.co = center + rot @ v.co
    return bm


class Pack:
    """Esqueleto, piezas y animaciones de un pack, cargados del .blend maestro sin modificarlo."""

    def __init__(self, key):
        with bpy.data.libraries.load(str(MASTER[key]), link=False) as (src, dst):
            dst.objects = list(src.objects)
            dst.actions = list(src.actions)
        self.collection = bpy.data.collections.new('Pack_' + key)
        bpy.context.scene.collection.children.link(self.collection)
        self.objects = {o.name.split('.')[0]: o for o in dst.objects if o}
        for o in dst.objects:
            if o:
                link(o, self.collection)
        self.actions = {name: a for name, a in zip(src.actions, dst.actions)}
        self.armature = self.objects['CharacterArmature']
        self.armature.animation_data.action = None
        for pb in self.armature.pose.bones:
            pb.matrix_basis = Matrix()
        self.collection.hide_render = True

    def part(self, name, owner):
        # Copia la pieza con espejo y suavizado aplicados; la deformación la hará el esqueleto del personaje.
        src = self.objects[name]
        # Una pieza oculta en el visor no se evalúa y saldría sin espejo (media pieza): se muestra mientras se copia.
        state = [(m, m.show_viewport) for m in src.modifiers]
        for m in src.modifiers:
            m.show_viewport = m.type != 'ARMATURE'
        src.hide_viewport = False
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(src.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        for m, shown in state:
            m.show_viewport = shown
        obj = link(bpy.data.objects.new(f'{owner}_{name}', me))
        obj.matrix_world = src.matrix_world.copy()
        # Los nombres de los grupos viajan con la malla; solo se crean si no llegaron.
        if not obj.vertex_groups:
            for g in src.vertex_groups:
                obj.vertex_groups.new(name=g.name)
        return obj


class Member:
    def __init__(self, spec, pack):
        self.spec, self.pack = spec, pack
        self.arm = link(pack.armature.copy())
        self.arm.data = pack.armature.data.copy()
        self.arm.name = spec['id'] + '_Rig'
        self.arm.animation_data_clear()
        parts = [pack.part(name, spec['id']) for name in spec['parts']]
        for name, obj in zip(spec['parts'], parts):
            for i, m in enumerate(obj.data.materials):
                base = m.name.split('.')[0] if m else None
                color = spec['colors'].get(f'{name}:{base}', spec['colors'].get(base))
                if color:
                    obj.data.materials[i] = material(base, color, m)
        self.body = parts[0]
        self.join(parts)
        self.body.name = spec['id']
        self.bones = {b.name: (self.arm.matrix_world @ b.head_local, self.arm.matrix_world @ b.tail_local) for b in self.arm.data.bones}
        if spec.get('bulk'):
            self.bulk(spec['bulk'])
        self.snapshot()

    def bulk(self, factor):
        # Brazos y pecho más anchos sin tocar el esqueleto: las animaciones del pack siguen valiendo.
        me, M, Mi = self.body.data, self.body.matrix_world, self.body.matrix_world.inverted()
        names = {g.index: g.name for g in self.body.vertex_groups}
        gain = {b: factor - 1 for b in ('UpperArm.L', 'UpperArm.R', 'LowerArm.L', 'LowerArm.R', 'Shoulder.L', 'Shoulder.R')}
        gain.update({b: (factor - 1) * .45 for b in ('Chest', 'Torso')})
        for v in me.vertices:
            weights = {names[g.group]: g.weight for g in v.groups if g.weight > 0}
            k = 1 + sum(w * gain.get(b, 0) for b, w in weights.items())
            dominant = max(weights, key=weights.get) if weights else None
            if k <= 1.001 or dominant not in gain:
                continue
            head, tail = self.bones[dominant]
            p, d = M @ v.co, tail - head
            q = head + d * max(0, min(1, (p - head).dot(d) / d.length_squared))
            r = p - q
            if dominant in ('Chest', 'Torso'):
                r.z = 0
            v.co = Mi @ (q + r * k)

    def join(self, objs):
        with bpy.context.temp_override(active_object=self.body, object=self.body, selected_objects=objs, selected_editable_objects=objs):
            bpy.ops.object.join()

    def snapshot(self):
        # Posición y pesos de cada vértice del cuerpo vestido, para pegar accesorios y que sigan a la piel cercana.
        me, M = self.body.data, self.body.matrix_world
        groups = {g.index: g.name for g in self.body.vertex_groups}
        self.world = [M @ v.co for v in me.vertices]
        self.weights = [[(groups[g.group], g.weight) for g in v.groups if g.weight > 0] for v in me.vertices]
        self.kd = KDTree(len(self.world))
        for i, p in enumerate(self.world):
            self.kd.insert(p, i)
        self.kd.balance()
        self.bvh = world_bvh(self.body)
        self.waist = self.bones['UpperLeg.R'][0].z + .06

    # --- piezas añadidas ---
    def rigid(self, name, bm, mat, anchor):
        obj = mesh_object(name, bm, [mat])
        _, index, _ = self.kd.find(anchor)
        for group, weight in self.weights[index]:
            obj.vertex_groups.new(name=group).add(range(len(obj.data.vertices)), weight, 'REPLACE')
        self.pieces.append(obj)

    def skinned(self, name, bm, mat):
        obj = mesh_object(name, bm, [mat])
        for v in obj.data.vertices:
            _, index, _ = self.kd.find(obj.matrix_world @ v.co)
            for group, weight in self.weights[index]:
                (obj.vertex_groups.get(group) or obj.vertex_groups.new(name=group)).add([v.index], weight, 'REPLACE')
        self.pieces.append(obj)

    def surface(self, origin, direction):
        loc, normal, _, _ = self.bvh.ray_cast(origin, direction, 3.0)
        if loc is None:
            raise RuntimeError(f'{self.spec["id"]}: no se encontró la ropa desde {tuple(origin)}')
        return loc, normal if normal.dot(direction) < 0 else -normal

    def ring(self, z, offset, segments=36):
        center = Vector((0, self.bones['Hips'][0].y, z))
        points = []
        for k in range(segments):
            a = 2 * math.pi * k / segments
            d = Vector((math.cos(a), math.sin(a), 0))
            loc, _ = self.surface(center + d * .8, -d)
            points.append((loc + d * offset, d))
        return points

    def belt(self, color):
        rows = [self.ring(self.waist + dz, BELT) for dz in (-.02, .02)]
        bm = bmesh.new()
        layers = []
        for row in rows:
            layers.append([bm.verts.new(p) for p, _ in row])
            layers.append([bm.verts.new(p - d * .006) for p, d in row])
        n = len(rows[0])
        for a, b in ((0, 2), (3, 1), (2, 3), (1, 0)):
            for k in range(n):
                j = (k + 1) % n
                bm.faces.new((layers[a][k], layers[a][j], layers[b][j], layers[b][k]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        self.skinned('Belt', bm, material('Belt', color))
        front, normal = self.surface(Vector((0, -1, self.waist)), BACK)
        self.rigid('Buckle', box(front + normal * (BELT + .006), frame(normal), (.05, .04, .01)), material('Metal', '9C9EA3'), front)

    def hip_point(self, direction, z, out):
        d = direction.normalized()
        loc, normal = self.surface(Vector((0, self.bones['Hips'][0].y, z)) + d * .8, -d)
        return loc + normal * out, normal

    def radio_belt(self):
        center, normal = self.hip_point(LEFT * .82 + FORWARD * .57, self.waist - .03, BELT + .018)
        axes = frame(normal)
        dark = material('Gear', '18191C')
        self.rigid('Radio', box(center, axes, (.045, .09, .028)), dark, center)
        self.rigid('Antenna', cylinder(center + axes[1] * .075 - axes[0] * .012, axes[1], .005, .06, 6), dark, center)

    def baton(self):
        # Porra corta enfundada en el costado izquierdo; corta para no cruzar el muslo al caminar.
        center, normal = self.hip_point(LEFT * .94 + BACK * .34, self.waist - .1, BELT + .028)
        self.rigid('Baton', cylinder(center, UP, .015, .24, 8), material('Gear', '18191C'), center)
        self.rigid('BatonHolder', box(center + UP * .09, frame(normal), (.04, .035, .04)), material('Belt', '111113'), center)

    def holster(self):
        # Funda en el costado derecho con la empuñadura a la vista.
        center, normal = self.hip_point(-LEFT * .97 + BACK * .26, self.waist - .07, BELT + .025)
        axes = frame(normal)
        self.rigid('Holster', box(center, axes, (.04, .14, .045)), material('Gear', '18191C'), center)
        tilt = (axes[0], (axes[1] * math.cos(.3) - axes[2] * math.sin(.3)).normalized(), (axes[2] * math.cos(.3) + axes[1] * math.sin(.3)).normalized())
        self.rigid('PistolGrip', box(center + axes[1] * .1 - axes[2] * .004, tilt, (.028, .07, .03)), material('Metal', '2B2C30'), center)

    def epaulets(self, color):
        for bone in ('UpperArm.R', 'UpperArm.L'):
            head = self.bones[bone][0]
            loc, normal = self.surface(Vector((head.x * .78, head.y, head.z + .6)), -UP)
            x = Vector((1 if head.x > 0 else -1, 0, 0))
            y = normal.cross(x).normalized()
            self.rigid('Epaulet', box(loc + normal * .004, (x, y, normal), (.09, .04, .007)), material('Epaulet', color), loc)

    def text_mesh(self, text, size):
        cu = bpy.data.curves.new('Label', 'FONT')
        cu.body, cu.size, cu.align_x, cu.align_y, cu.extrude, cu.resolution_u = text, size, 'CENTER', 'CENTER', .0008, 2
        obj = link(bpy.data.objects.new('Label', cu))
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(obj)
        bpy.data.curves.remove(cu)
        return me

    def wrap(self, me, origin, axes, gap):
        # Pega la pieza plana sobre la ropa, vértice a vértice.
        bm = bmesh.new()
        bm.from_mesh(me)
        for v in bm.verts:
            base = origin + axes[0] * v.co.x + axes[1] * v.co.y
            loc, normal, _, _ = self.bvh.ray_cast(base + axes[2] * .25, -axes[2], .5)
            if loc is None:
                loc, normal, _, _ = self.bvh.find_nearest(base)
            if normal.dot(axes[2]) < 0:
                normal = -normal
            v.co = loc + normal * (gap + v.co.z)
        return bm

    def label(self, text, size, center, normal, patch, ink):
        axes = frame(normal)
        me = self.text_mesh(text, size)
        width = max(v.co.x for v in me.vertices) - min(v.co.x for v in me.vertices)
        if patch:
            plate = bmesh.new()
            bmesh.ops.create_grid(plate, x_segments=6, y_segments=2, size=.5)
            for v in plate.verts:
                v.co = Vector((v.co.x * (width + size * .9), v.co.y * size * 1.7, 0))
            pm = bpy.data.meshes.new('Patch')
            plate.to_mesh(pm)
            plate.free()
            self.rigid('Patch', self.wrap(pm, center, axes, .0025), material('Patch', patch), center)
        if ink:
            self.rigid('Text', self.wrap(me, center, axes, .0045), material('Ink', ink), center)

    def labels(self):
        lab = self.spec['label']
        chest = self.bones['Chest'][0].z
        if lab['back_ink']:
            loc, normal = self.surface(Vector((0, 1, chest + .02)), FORWARD)
            self.label(lab['text'], .04, loc, normal, lab['back_patch'], lab['back_ink'])
        loc, normal = self.surface(Vector((.075, -1, chest - .01)), BACK)
        self.label(lab['text'], .018, loc, normal, lab['chest_patch'], lab['chest_ink'])

    def eyes(self):
        # Centro de cada ojo (izquierda +X, derecha -X) a partir de las caras con material de ojo.
        # Las cabezas de mujer no tienen material Eye: ojos y cejas comparten Brown dentro de la cabeza.
        neck = self.bones['Head'][0].z
        pts = [p for p, _ in self.material_vertices('Eye')] or [p for p, _ in self.material_vertices('Brown') if p.z > neck and p.y < self.bones['Head'][0].y]
        if not pts:
            raise RuntimeError(self.spec['id'] + ': la cabeza no tiene material Eye')
        sides = [[p for p in pts if (p.x > self.bones['Head'][0].x) == left] for left in (True, False)]
        return [sum(side, Vector()) / len(side) for side in sides]

    def beanie(self, color):
        self.cap(color, visor=False)

    def cap(self, color, visor=True):
        eye = [p for p, _ in self.material_vertices('Eye')]
        brow = (sum(p.z for p in eye) / len(eye) if eye else self.bones['Head'][0].z + .12) + .035
        pts = [p for i, p in enumerate(self.world) if p.z > brow and any(g == 'Head' and w > .5 for g, w in self.weights[i])]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), brow))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, brow))
        # El pelo que quedaría por encima de la frente se recoge bajo la gorra.
        M, Mi = self.body.matrix_world, self.body.matrix_world.inverted()
        hair = {v for p, v in self.material_vertices('Hair') if p.z > brow + .01}
        for v in hair:
            w = M @ self.body.data.vertices[v].co
            self.body.data.vertices[v].co = Mi @ (center + (w - center) * .86)
        # Holgura suficiente para tapar mechones y flequillo del pack.
        r = Vector(((hi.x - lo.x) / 2 + .022, (hi.y - lo.y) / 2 + .022, hi.z - brow + .02))
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
        for v in bm.verts:
            v.co = center + Vector((v.co.x * r.x, v.co.y * r.y, v.co.z * r.z))
        self.cap_top = center + UP * r.z
        if not visor:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            obj = mesh_object('Beanie', bm, [material('Cap', color)])
            obj.vertex_groups.new(name='Head').add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
            self.pieces.append(obj)
            return
        # Visera hacia delante, algo inclinada.
        inner, outer = [], []
        for k in range(9):
            a = math.radians(25 + 130 * k / 8)
            side, ahead = math.cos(a), math.sin(a)
            p = center + LEFT * side * r.x + FORWARD * ahead * r.y
            inner.append(p)
            outer.append(p + (LEFT * side * .35 + FORWARD).normalized() * .07 * ahead - UP * .012 * ahead)
        rows = [[bm.verts.new(p - UP * dz) for p in row] for dz in (0, .006) for row in (inner, outer)]
        top_in, top_out, bot_in, bot_out = rows
        for k in range(8):
            bm.faces.new((top_in[k], top_in[k + 1], top_out[k + 1], top_out[k]))
            bm.faces.new((bot_in[k + 1], bot_in[k], bot_out[k], bot_out[k + 1]))
            bm.faces.new((top_out[k], top_out[k + 1], bot_out[k + 1], bot_out[k]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        obj = mesh_object('Cap', bm, [material('Cap', color)])
        obj.vertex_groups.new(name='Head').add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
        self.pieces.append(obj)

    def tiny_cap(self, color):
        # Gorrito diminuto de Toñito, posado en lo alto de la cabeza.
        head = [p for i, p in enumerate(self.world) if any(g == 'Head' and w > .5 for g, w in self.weights[i])]
        top = max(head, key=lambda p: p.z)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
        for v in bm.verts:
            v.co = top - UP * .012 + Vector((v.co.x * .055, v.co.y * .055, v.co.z * .04))
        visor = box(top - UP * .012 + FORWARD * .07, (LEFT, FORWARD, UP), (.08, .05, .006))
        visor.to_mesh(me := bpy.data.meshes.new('Visor'))
        visor.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        obj = mesh_object('TinyCap', bm, [material('Cap', color)])
        obj.vertex_groups.new(name='Head').add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
        self.pieces.append(obj)

    def antennas(self, color):
        # Dos antenas sobre la gorra del hacker, abiertas hacia los lados.
        for side in (1, -1):
            axis = (UP + LEFT * side * .35).normalized()
            base = self.cap_top + LEFT * side * .04
            self.rigid('Antenna', cylinder(base + axis * .06, axis, .004, .12, 6), material('Antenna', '2B2C30'), self.cap_top - UP * .05)
            self.rigid('AntennaTip', box(base + axis * .125, (LEFT, FORWARD, UP), (.022, .022, .022)), material('Antenna', color), self.cap_top - UP * .05)

    def glasses(self, color):
        eyes = self.eyes()
        frame_mat, lens_mat = material('Frame', '2B2C30'), material('Lens', color)
        for eye in eyes:
            loc, normal = self.surface(eye + FORWARD * .3, BACK)
            self.rigid('Lens', box(loc + normal * .012, frame(normal), (.042, .03, .004)), lens_mat, eye)
        mid = (eyes[0] + eyes[1]) / 2
        loc, normal = self.surface(mid + FORWARD * .3, BACK)
        self.rigid('Bridge', box(loc + normal * .013, frame(normal), ((eyes[0] - eyes[1]).length - .03, .006, .004)), frame_mat, mid)

    def moustache(self, color):
        eyes = self.eyes()
        mid = (eyes[0] + eyes[1]) / 2 - UP * .062
        loc, normal = self.surface(mid + FORWARD * .3, BACK)
        self.rigid('Moustache', box(loc + normal * .006, frame(normal), (.07, .018, .012)), material('Moustache', color), mid)

    def mask(self, color):
        # Antifaz: cinta alrededor de la cabeza a la altura de los ojos, con dos huecos para verlos.
        eyes = self.eyes()
        z = (eyes[0].z + eyes[1].z) / 2
        center = Vector((self.bones['Head'][0].x, self.bones['Head'][0].y, z))
        holes = [math.atan2((e - center).y, (e - center).x) for e in eyes]
        rows = []
        for dz in (-.03, .026):
            row = []
            for k in range(48):
                a = 2 * math.pi * k / 48
                d = Vector((math.cos(a), math.sin(a), 0))
                loc, _ = self.surface(center + UP * dz + d * .5, -d)
                open_ = any(abs((a - h + math.pi) % (2 * math.pi) - math.pi) < math.radians(7) for h in holes)
                row.append((loc + d * .007, open_))
            rows.append(row)
        bm = bmesh.new()
        lower = [bm.verts.new(p) for p, _ in rows[0]]
        upper = [bm.verts.new(p) for p, _ in rows[1]]
        for k in range(48):
            j = (k + 1) % 48
            if not (rows[0][k][1] or rows[0][j][1]):
                bm.faces.new((lower[k], lower[j], upper[j], upper[k]))
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        obj = mesh_object('Mask', bm, [material('Mask', color)])
        obj.vertex_groups.new(name='Head').add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
        self.pieces.append(obj)

    def sack(self, color):
        # Saco del botín a la espalda del ladrón.
        chest = self.bones['Chest'][0]
        loc, normal = self.surface(Vector((chest.x, 1, chest.z)), FORWARD)
        center = loc + normal * .16 - UP * .04
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=7, radius=1)
        for v in bm.verts:
            v.co = center + Vector((v.co.x * .2, v.co.y * .15, v.co.z * .25))
        self.rigid('Sack', bm, material('Sack', color), loc)
        self.rigid('SackKnot', box(center + UP * .26, (LEFT, FORWARD, UP), (.07, .07, .06)), material('Sack', color), loc)

    def material_vertices(self, role):
        # Vértices (posición en el mundo e índice) de las caras con un material del pack, recoloreado o no.
        me, M = self.body.data, self.body.matrix_world
        ids = {i for i, m in enumerate(me.materials) if m and (m.name.split('.')[0] == role or m.name.startswith(f'QM_{role}_'))}
        return [(M @ me.vertices[v].co, v) for p in me.polygons if p.material_index in ids for v in p.vertices]

    def build(self):
        s = self.spec
        self.pieces = []
        if s.get('belt'):
            self.belt(s['belt'])
        for prop in s.get('props', []):
            getattr(self, prop)()
        if s.get('epaulets'):
            self.epaulets(s['epaulets'])
        if s.get('label'):
            self.labels()
        if s.get('cap'):
            self.cap(s['cap'])
        for extra, color in s.get('extras', []):
            getattr(self, extra)(color)
        self.join([self.body] + self.pieces)
        self.body.parent = self.arm
        self.body.matrix_parent_inverse = self.arm.matrix_world.inverted()
        self.body.modifiers.new('Armature', 'ARMATURE').object = self.arm
        self.grip_and_bag()
        self.clips()

    def grip_and_bag(self):
        # El elenco de la prueba necesita un agarre en la mano derecha y una bolsa colgada de él (Unity la oculta al empezar).
        pid = self.spec['playtest']
        wrist, elbow = self.bones['Wrist.R'][0], self.bones['LowerArm.R'][0]
        palm = wrist + (wrist - elbow).normalized() * .06 - UP * .02
        self.grip = link(bpy.data.objects.new('Grip_R6_' + pid, None))
        self.grip.parent, self.grip.parent_type, self.grip.parent_bone = self.arm, 'BONE', 'Wrist.R'
        bpy.context.view_layer.update()
        self.grip.matrix_world = Matrix.Translation(palm)
        bm = box(Vector((0, 0, -.2)), (LEFT, FORWARD, UP), (.2, .09, .24))
        bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=.006, radius2=.006, depth=.11, matrix=Matrix.Translation((0, 0, -.04)))
        self.bag = mesh_object('ShoppingBag_' + pid, bm, [material('Bag', 'C49A6C')])
        self.bag.parent = self.grip
        bpy.context.view_layer.update()
        self.bag.matrix_world = Matrix.Translation(palm)

    def clips(self):
        # Una pista NLA por clip: el FBX exporta cada una con su nombre, como el resto del elenco.
        data = self.arm.animation_data_create()
        for name, source in list(CLIPS.items()) + [(n, n) for n in EXTRA_CLIPS[self.spec['clips']]]:
            action = self.pack.actions[source]
            track = data.nla_tracks.new()
            track.name = name
            strip = track.strips.new(name, int(action.frame_range[0]), action)
            if hasattr(strip, 'action_slot') and action.slots:
                strip.action_slot = action.slots[0]
            track.mute = True


def validate(member):
    me, arm = member.body.data, member.arm
    ws = [member.body.matrix_world @ v.co for v in me.vertices]
    return {
        'parts': member.spec['parts'],
        'triangles': sum(len(p.vertices) - 2 for p in me.polygons),
        'materials': len(me.materials),
        'bones': len(arm.data.bones),
        'unweighted_vertices': sum(1 for v in me.vertices if not any(g.weight > 0 for g in v.groups)),
        'groups_without_bone': sorted(g.name for g in member.body.vertex_groups if g.name not in arm.data.bones),
        'height_m': round(max(p.z for p in ws) - min(p.z for p in ws), 3),
    }


def export(member):
    EXPORT.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in (member.arm, member.body, member.grip, member.bag):
        o.select_set(True)
    bpy.context.view_layer.objects.active = member.arm
    tracks = member.arm.animation_data.nla_tracks
    for t in tracks:
        t.mute = False
    path = EXPORT / f'{member.spec["id"]}.fbx'
    # Normales tal cual (mesh_smooth_type OFF): conserva el facetado low-poly del pack.
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'ARMATURE', 'MESH', 'EMPTY'}, use_mesh_modifiers=False,
                             global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=False, add_leaf_bones=False, mesh_smooth_type='OFF', bake_anim=True,
                             bake_anim_use_all_actions=False, bake_anim_use_nla_strips=True, bake_anim_simplify_factor=1, bake_anim_step=1)
    for t in tracks:
        t.mute = True
    shutil.copyfile(path, PLAYTEST / 'export' / 'Characters' / f'{member.spec["playtest"]}.fbx')
    return path


def round_trip(path, member):
    # El FBX reimportado debe conservar esqueleto, malla y clips.
    before_actions = set(bpy.data.actions)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    objs = [o for o in bpy.data.objects if o not in before]
    clips = sorted({a.name.split('|')[-1] for a in bpy.data.actions if a not in before_actions})
    arm = next(o for o in objs if o.type == 'ARMATURE')
    mesh = next(o for o in objs if o.type == 'MESH' and o.name.startswith(member.spec['id']))
    worst = max((arm.matrix_world @ b.head_local - member.bones[b.name][0]).length for b in arm.data.bones)
    # Comprueba que el clip Walk del FBX mueve de verdad el pie (no solo que exista con ese nombre).
    walk = next(a for a in bpy.data.actions if a not in before_actions and a.name.endswith('|Walk') and arm.name.split('.')[0] in a.name)
    play(arm, walk)
    feet = []
    for frame in (int(walk.frame_range[0]), int(sum(walk.frame_range) / 2)):
        bpy.context.scene.frame_set(frame)
        feet.append(arm.matrix_world @ arm.pose.bones['Foot.L'].head)
    result = {'bone_offset_m': round(worst, 5), 'triangles': sum(len(p.vertices) - 2 for p in mesh.data.polygons),
              'size_mb': round(path.stat().st_size / 1048576, 2), 'clips': clips,
              'walk_foot_motion_m': round((feet[0] - feet[1]).length, 3),
              'empties': sorted(o.name.split('.')[0] for o in objs if o.type == 'EMPTY')}
    for o in objs:
        bpy.data.objects.remove(o)
    for a in [a for a in bpy.data.actions if a not in before_actions]:
        bpy.data.actions.remove(a)
    return result


def render(groups):
    RENDERS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light, shading.color_type, shading.show_cavity, shading.show_specular_highlight = 'STUDIO', 'MATERIAL', False, False
    scene.world = scene.world or bpy.data.worlds.new('Fondo')
    scene.world.color = (.78, .79, .81)
    cam = link(bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')))
    cam.data.type = 'ORTHO'
    scene.camera = cam
    everyone = [m for group in groups.values() for m in group]
    views = {'frente': ((0, -12, .95), (90, 0, 0), 'x'), 'espalda': ((0, 12, .95), (90, 0, 180), 'x'), 'perfil': ((-12, 0, .95), (90, 0, -90), 'y')}
    shots = [(g, v, 'Idle_Neutral', 10) for g in groups for v in ('frente', 'espalda')] + [('protagonistas', 'perfil', 'Walk', 10)]
    for group, view, clip, frame_number in shots:
        shown = groups[group]
        location, rotation, axis = views[view]
        for m in everyone:
            for o in [m.arm, m.body, m.grip, m.bag]:
                o.hide_render = m not in shown or o is m.bag
        for i, m in enumerate(shown):
            offset = (i - (len(shown) - 1) / 2) * 1.05
            m.arm.location = (offset, 0, 0) if axis == 'x' else (0, offset, 0)
            play(m.arm, m.pack.actions[clip])
        scene.frame_set(frame_number)
        width = max(3.0, len(shown) * 1.05 + .6)
        scene.render.resolution_x, scene.render.resolution_y = int(min(3600, 520 * width)), 1100
        cam.data.ortho_scale = max(width, 2.3 * scene.render.resolution_x / 1100)
        cam.location, cam.rotation_euler = location, tuple(math.radians(a) for a in rotation)
        scene.render.filepath = str(RENDERS / f'elenco_{group}_{view}.png')
        bpy.ops.render.render(write_still=True)
    for m in everyone:
        m.arm.location = (0, 0, 0)
        play(m.arm, None)
        for o in [m.arm, m.body, m.grip, m.bag]:
            o.hide_render = False


bpy.ops.wm.read_factory_settings(use_empty=True)
packs = {key: Pack(key) for key in sorted({s['pack'] for s in CAST})}
members = []
report = {'source': 'Quaternius Ultimate Modular Men/Women, CC0 1.0', 'characters': {}}
for spec in CAST:
    m = Member(spec, packs[spec['pack']])
    m.build()
    members.append(m)
    report['characters'][spec['id']] = validate(m)
for m in members:
    report['characters'][m.spec['id']]['fbx'] = round_trip(export(m), m)
render({'seguridad': members[:2], 'civiles': members[2:12], 'protagonistas': members[12:]})
# El .blend guarda solo el elenco: las piezas sin usar del pack se descartan.
for pack in packs.values():
    for o in list(pack.collection.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(pack.collection)
bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
(HERE / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'ModularCast.blend'), compress=True)
print('CAST_REPORT', json.dumps(report), flush=True)
