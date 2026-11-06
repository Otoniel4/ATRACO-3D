"""Armas, herramientas y consumibles del jugador (y la porra de los guardias) a escala real, para la mano.

Convención para Unity: metros, frente -Y (cañón o punta), arriba +Z, origen en el centro de la empuñadura.
Con el frente en -Y, la derecha de quien lo sostiene es -X: Grip_R va del lado -X y Grip_L del lado +X.
Puntos vacíos que lee el juego:
  Grip_R  palma de la mano derecha (la que sostiene).
  Grip_L  palma de la mano izquierda: siempre en los objetos de dos manos (escopeta, rifle, pistola en guardia,
          tablet, termita) y, en los de una mano, solo durante su acción (palanca más arriba en la barra, llave de
          tensión de la ganzúa, empuñadura del taladro, ventosa del cortavidrios, colas de las bridas, cuerda del
          gancho y anilla de las granadas). Los datos de cada acción están en make_item_actions.py.
  MuzzlePoint  boca del cañón (disparos, Task 18).
Medidas de referencia: pistola 19 cm, táser 17 cm, escopeta 1,05 m, rifle 0,95 m, taladro 24 cm, granadas 12 cm.
Uso: blender -b --factory-startup -P build_weapons.py
Salida: Art/Weapons/<pieza>.fbx, Art/Weapons/weapon_materials.json y Previews~/armas_*.png.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'City25~'))
import alarmart as a  # noqa: E402
from kit_parts import Kit  # noqa: E402

OUT = a.ART / 'Weapons'
COLORS = dict(Polymer='23272C', Slide='56606A', SteelDark='2B3036', Metal='8A9499', Rubber='1C1F22', Wood='8B5A3C',
              WoodLight='A8744E', Taser='F2C230', TaserBlue='3A7BD5', Sight='EDEDED', RedDot=('E8483C', 1.5, 1),
              Tan='9C8A6A', Black='15171A', Crowbar='C9684F', Teal='397C78', Apricot='EF9B59', Navy='293C55',
              Mustard='E6BB55', Sage='87A885', Berry='A15A78', Ivory='F2EBD6', Screen=('4FB3FF', 1.0, 1), Status='A8E6A3',
              Rope='B08A5A', Copper='B87333')
kit = Kit(OUT, 'Alarma_Weapon_', COLORS)
B, C = kit.B, kit.C
PIECES = []
X90 = (math.pi / 2, 0, 0)  # cilindro a lo largo de Y (cañones)


def start(name):
    PIECES.append(name)
    a.begin(name, 'Weapons')
    a.ROOT['GameplayState'] = 'Modelo para la mano: sin disparos ni efectos'


def grips(right, left=None, muzzle=None):
    a.empty('Grip_R', right)
    if left:
        a.empty('Grip_L', left)
    if muzzle:
        a.empty('MuzzlePoint', muzzle)


def handgun(body, grip_color, length=.19, taser=False):
    # Pistola compacta: corredera con estrías y miras, armazón, empuñadura inclinada 18°, guardamonte y gatillo.
    top = .085
    B('Slide', (0, -length / 2 + .03, top), (.028, length, .032), body, .004)
    for i in range(5):
        B('Serration', (0, .022 - i * .006, top), (.0295, .0025, .024), 'Black', 0)  # estrías al final de la corredera
    B('FrontSight', (0, -length + .038, top + .019), (.005, .006, .007), 'Sight', 0)
    B('RearSight', (0, .024, top + .019), (.018, .006, .007), 'Black', 0)
    B('Frame', (0, -length / 2 + .035, .058), (.026, length - .02, .022), grip_color, .003)
    B('Grip', (0, .008, 0), (.03, .052, .112), grip_color, .006, rot=(math.radians(18), 0, 0))
    for i in range(4):
        B('GripTexture', (.0152, .004 + i * .004, .02 - i * .025), (.001, .03, .012), 'Black', 0, rot=(math.radians(18), 0, 0))
    B('Magazine', (0, .026, -.057), (.032, .05, .012), 'Black', .003, rot=(math.radians(18), 0, 0))
    B('GuardBottom', (0, -.04, .036), (.012, .05, .006), grip_color, .002)
    B('GuardFront', (0, -.065, .046), (.012, .006, .026), grip_color, .002)
    B('Trigger', (0, -.034, .046), (.006, .008, .02), 'Black', .001, rot=(math.radians(-10), 0, 0))
    if taser:
        B('Cartridge', (0, -length + .015, .07), (.034, .04, .05), 'Black', .004)
        for x in (-.009, .009):
            C('Electrode', (x, -length - .006, .078), .004, .006, 'TaserBlue', 8, rot=X90)
        B('Laser', (0, -length + .04, .043), (.012, .03, .01), 'TaserBlue', .002)
    else:
        C('Bore', (0, -length + .029, top), .005, .004, 'Black', 8, rot=X90)
        B('Port', (.0142, -.035, top + .004), (.001, .03, .012), 'Black', 0)
    grips((-.02, .006, .0), (.024, .012, -.012), (0, -length + .028, top))


def weapon_pistol():
    start('Weapon_Pistol')
    handgun('Slide', 'Polymer')
    a.export_asset('Weapon_Pistol')


def weapon_taser():
    start('Weapon_Taser')
    handgun('Taser', 'Black', .17, taser=True)
    a.export_asset('Weapon_Taser')


def long_gun(name, rifle):
    start(name)
    if rifle:
        # Rifle tipo carabina: culata regulable, tubo, empuñadura, cargador curvo, riel con mira de punto rojo y guardamanos.
        B('Stock', (0, .33, .02), (.04, .16, .075), 'Polymer', .008)
        B('ButtPad', (0, .415, .015), (.042, .012, .085), 'Rubber', .003)
        C('BufferTube', (0, .2, .045), .014, .14, 'SteelDark', 10, rot=X90)
        B('Lower', (0, .03, .03), (.034, .18, .045), 'SteelDark', .004)
        B('Upper', (0, .0, .07), (.036, .26, .04), 'SteelDark', .004)
        B('Rail', (0, .0, .094), (.022, .24, .008), 'Black', .001)
        for i in range(10):
            B('RailSlot', (0, -.11 + i * .024, .099), (.023, .008, .004), 'Black', 0)
        B('Grip', (0, .1, -.035), (.028, .04, .09), 'Polymer', .005, rot=(math.radians(18), 0, 0))
        B('Magazine', (0, -.03, -.06), (.024, .06, .13), 'Black', .004, rot=(math.radians(-10), 0, 0))
        B('Trigger', (0, .055, .0), (.006, .008, .02), 'Black', 0)
        B('Guard', (0, .05, -.012), (.012, .05, .005), 'SteelDark', 0)
        B('Handguard', (0, -.25, .055), (.048, .26, .055), 'Tan', .008)
        for i in range(6):
            B('Vent', (.0245, -.16 - i * .035, .055), (.001, .016, .028), 'Black', 0)
            B('Vent', (-.0245, -.16 - i * .035, .055), (.001, .016, .028), 'Black', 0)
        C('Barrel', (0, -.44, .06), .009, .14, 'SteelDark', 10, rot=X90)
        C('FlashHider', (0, -.525, .06), .012, .04, 'Black', 8, rot=X90)
        B('FrontSight', (0, -.37, .1), (.006, .01, .035), 'Black', 0)
        B('OpticBase', (0, .02, .105), (.026, .05, .012), 'Black', .002)
        C('Optic', (0, .02, .13), .018, .07, 'Black', 12, rot=X90)
        C('OpticLens', (0, -.016, .13), .014, .002, 'RedDot', 12, rot=X90)
        C('Charging', (0, .12, .088), .005, .02, 'Black', 6, rot=(0, math.pi / 2, 0))
        grips((-.02, .1, -.03), (.026, -.26, .025), (0, -.545, .06))
    else:
        # Escopeta de corredera: culata de madera, cajón de mecanismos, cañón con tubo de cartuchos y corredera estriada.
        B('Stock', (0, .38, -.005), (.042, .3, .09), 'Wood', .012, rot=(math.radians(-6), 0, 0))
        B('ButtPad', (0, .535, -.02), (.044, .014, .1), 'Rubber', .004)
        B('Wrist', (0, .17, .01), (.036, .14, .05), 'Wood', .01, rot=(math.radians(-12), 0, 0))
        B('Receiver', (0, .02, .04), (.044, .18, .07), 'SteelDark', .006)
        B('Port', (.0225, .03, .052), (.001, .06, .022), 'Black', 0)
        B('Trigger', (0, .085, -.004), (.006, .008, .02), 'Black', 0)
        B('Guard', (0, .08, -.018), (.012, .05, .005), 'SteelDark', 0)
        C('Barrel', (0, -.31, .058), .011, .5, 'SteelDark', 12, rot=X90)
        C('Tube', (0, -.27, .028), .011, .42, 'SteelDark', 12, rot=X90)
        C('Cap', (0, -.485, .028), .012, .02, 'Black', 10, rot=X90)
        B('Pump', (0, -.25, .03), (.05, .2, .045), 'WoodLight', .01)
        for i in range(6):
            B('PumpGroove', (.0255, -.32 + i * .028, .03), (.001, .01, .032), 'Wood', 0)
            B('PumpGroove', (-.0255, -.32 + i * .028, .03), (.001, .01, .032), 'Wood', 0)
        C('Bead', (0, -.55, .072), .003, .004, 'Sight', 8)
        grips((-.02, .14, -.005), (.028, -.24, .015), (0, -.56, .058))
    a.export_asset(name)


def baton():
    # Porra de los guardias (no es del jugador): tolete negro con mango de goma.
    start('Weapon_Baton')
    C('Shaft', (0, 0, .25), .016, .5, 'Black', 10)
    C('Handle', (0, 0, .02), .019, .17, 'Rubber', 10)
    for i in range(5):
        C('GripRing', (0, 0, -.04 + i * .028), .02, .006, 'Polymer', 10)
    C('Collar', (0, 0, .115), .022, .02, 'SteelDark', 10)
    grips((.0, 0, .0))
    a.export_asset('Weapon_Baton')


def crowbar():
    # Palanca de 60 cm: barra hexagonal con uña curva arriba y punta plana abajo; se toma por el tercio inferior.
    start('Tool_Crowbar')
    C('Shaft', (0, 0, .12), .011, .46, 'Crowbar', 6)
    a.beam('Neck', (0, 0, .35), (0, -.05, .42), .011, 'Metal', 6)
    kit.use(bpy.context.object, 'Crowbar')
    B('Claw', (0, -.075, .425), (.03, .06, .01), 'Metal', .002, rot=(math.radians(-15), 0, 0))
    B('Notch', (0, -.098, .427), (.008, .02, .012), 'Black', 0)
    B('Tip', (0, .012, -.115), (.024, .03, .008), 'Metal', .002, rot=(math.radians(20), 0, 0))
    grips((.0, 0, .0), (.0, 0, .16))
    a.export_asset('Tool_Crowbar')


def lockpick():
    start('Tool_Lockpick')
    B('Handle', (0, .03, 0), (.012, .07, .018), 'Teal', .004)
    a.beam('Pick', (0, -.005, .0), (0, -.075, .0), .0015, 'Metal', 6)
    kit.use(bpy.context.object, 'Metal')
    a.beam('PickTip', (0, -.075, 0), (0, -.083, .007), .0015, 'Metal', 6)
    kit.use(bpy.context.object, 'Metal')
    B('Tension', (.006, -.02, -.006), (.002, .06, .003), 'Metal', 0)
    B('TensionBend', (.006, .012, -.012), (.002, .004, .012), 'Metal', 0)
    grips((.0, .03, 0), (.02, .02, -.02))
    a.export_asset('Tool_Lockpick')


def zip_ties():
    start('Tool_ZipTies')
    for i in range(3):
        a.torus('Loop', (i * .012 - .012, 0, .03), .028, .003, 'Ivory', rotation=(0, math.pi / 2, 0), scale=(1, 1, .7))
        kit.use(bpy.context.object, 'Ivory')
        B('Tail', (i * .012 - .012, .045, .01), (.004, .07, .003), 'Ivory', 0)
        B('Head', (i * .012 - .012, .0, .001), (.008, .008, .006), 'Ivory', 0)
    grips((.0, .02, .01), (.012, .075, .01))
    a.export_asset('Tool_ZipTies')


def drill():
    # Taladro inalámbrico de 24 cm: carcasa del motor, empuñadura de goma con gatillo, batería y mandril con broca.
    start('Tool_Drill')
    B('Motor', (0, -.04, .09), (.056, .16, .07), 'Apricot', .012)
    B('MotorBack', (0, .045, .09), (.05, .03, .06), 'Black', .01)
    for i in range(3):
        B('Vent', (.0285, .025 - i * .012, .095), (.001, .006, .035), 'Black', 0)
    B('Grip', (0, .01, .0), (.036, .045, .12), 'Rubber', .008, rot=(math.radians(12), 0, 0))
    B('Trigger', (0, -.018, .035), (.012, .012, .03), 'Black', .002)
    B('Battery', (0, .02, -.075), (.07, .1, .05), 'Navy', .008)
    C('Chuck', (0, -.14, .09), .019, .045, 'Metal', 12, rot=X90)
    C('Bit', (0, -.205, .09), .004, .09, 'SteelDark', 6, rot=X90)
    grips((-.02, .01, .0), (.03, -.06, .13))
    a.export_asset('Tool_Drill')


def glass_cutter():
    start('Tool_GlassCutter')
    C('Handle', (0, 0, 0), .009, .12, 'Mustard', 10)
    B('Neck', (0, 0, .07), (.006, .008, .025), 'Metal', .001)
    C('Wheel', (0, 0, .087), .008, .003, 'Metal', 12, rot=(0, math.pi / 2, 0))
    C('Suction', (0, 0, -.068), .022, .012, 'Teal', 14)
    B('SuctionTab', (.026, 0, -.068), (.012, .01, .006), 'Teal', .001)
    grips((.0, 0, .0), (.03, 0, -.072))
    a.export_asset('Tool_GlassCutter')


def hacking_tablet():
    # Tablet de 24 × 17 cm con antena y cable: se sostiene con las dos manos por los costados.
    start('Tool_HackingTablet')
    B('Tablet', (0, 0, 0), (.24, .17, .014), 'Navy', .006)
    B('Screen', (0, -.004, .0075), (.21, .14, .002), 'Screen', .001)
    for i in range(4):
        B('Code', (-.04 + (i % 2) * .02, -.045 + i * .025, .009), (.09 - i * .012, .006, .001), 'Status', 0)
    C('Antenna', (.1, .07, .06), .003, .11, 'Metal', 6)
    B('Port', (-.08, .086, 0), (.03, .004, .008), 'Black', 0)
    grips((-.12, 0, -.01), (.12, 0, -.01))
    a.export_asset('Tool_HackingTablet')


def thermite():
    start('Tool_ThermiteCharge')
    C('Canister', (0, 0, 0), .045, .2, 'Crowbar', 14)
    for z in (-.075, .075):
        C('Band', (0, 0, z), .048, .02, 'Navy', 14)
    B('Timer', (0, -.044, .02), (.04, .012, .03), 'Black', .002)
    B('TimerLed', (0, -.0505, .025), (.025, .002, .01), 'RedDot', 0)
    B('Handle', (0, 0, .115), (.07, .016, .025), 'Metal', .004)
    grips((-.045, 0, .0), (.045, 0, .0))
    a.export_asset('Tool_ThermiteCharge')


def grappling_hook():
    start('Tool_GrapplingHook')
    C('Handle', (0, 0, 0), .016, .2, 'Metal', 10)
    for i in range(3):
        angle = i * 2 * math.pi / 3
        x, y = math.cos(angle), math.sin(angle)
        a.beam('Arm', (0, 0, .09), (x * .07, y * .07, .16), .007, 'Metal', 6)
        kit.use(bpy.context.object, 'Metal')
        a.beam('Tip', (x * .07, y * .07, .16), (x * .085, y * .085, .12), .006, 'Metal', 6)
        kit.use(bpy.context.object, 'Metal')
    a.torus('Rope', (0, 0, -.11), .05, .012, 'Wood')
    kit.use(bpy.context.object, 'Rope')
    grips((.0, 0, -.03), (.05, 0, -.11))
    a.export_asset('Tool_GrapplingHook')


def grenade(name, color, emp=False):
    start(name)
    C('Body', (0, 0, 0), .032, .1, color, 14)
    C('Top', (0, 0, .056), .022, .014, 'SteelDark', 12)
    B('Lever', (.026, 0, .03), (.008, .016, .07), 'Metal', .002)
    a.torus('Ring', (-.018, 0, .066), .011, .002, 'Metal', rotation=X90)
    kit.use(bpy.context.object, 'Metal')
    for z in (-.035, .035):
        C('Stripe', (0, 0, z), .0325, .006, 'Black', 14)
    if emp:
        C('Indicator', (0, -.032, 0), .007, .004, 'TaserBlue', 8, rot=X90)
    grips((.0, 0, .0), (-.018, 0, .08))
    a.export_asset(name)


def review():
    # Hoja de revisión: todas las piezas en fila junto a una figura de 1,75 m para ver la escala.
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    world = bpy.data.worlds.new('Cielo')
    world.color = (.62, .7, .78)
    scene.world = world
    scene.view_settings.view_transform = 'Standard'
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x, scene.render.resolution_y = 2000, 900
    x = 0
    for name in PIECES:
        root = bpy.data.objects[name]
        meshes = [o for o in a.descendants(root) if o.type == 'MESH']
        bpy.context.view_layer.update()
        width = max(max((o.matrix_world @ Vector(c)).y for o in meshes for c in o.bound_box) - min((o.matrix_world @ Vector(c)).y for o in meshes for c in o.bound_box), .12)
        root.location = (x + width / 2, 0, 1.0)
        root.rotation_euler = (0, 0, math.radians(90))  # el cañón apunta a la derecha de la cámara
        x += width + .12
    kit.colors['Figura'] = 'C9C3B8'
    a.begin('Figura', 'Previews')
    B('Cuerpo', (-.4, 0, .875), (.4, .25, 1.75), 'Figura', .05)
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = x + 1.0
    cam.location = (x / 2 - .4, -6, 1.0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    scene.render.filepath = str(a.ART / 'Previews~' / 'armas_escala.png')
    bpy.ops.render.render(write_still=True)
    # Primeros planos en perspectiva de tres cuartos para revisar el diseño.
    cam.data.type = 'PERSP'
    cam.data.lens = 60
    scene.render.resolution_x, scene.render.resolution_y = 1400, 900
    for name in ('Weapon_Pistol', 'Weapon_Taser', 'Weapon_Shotgun', 'Weapon_Rifle', 'Tool_Drill', 'Tool_HackingTablet'):
        root = bpy.data.objects[name]
        meshes = [o for o in a.descendants(root) if o.type == 'MESH']
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        center = sum(pts, Vector()) / len(pts)
        size = max((max(p[i] for p in pts) - min(p[i] for p in pts)) for i in range(3))
        eye = center + Vector((-.35, -1.0, .45)).normalized() * size * 2.6
        cam.location = eye
        cam.rotation_euler = (center - eye).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(a.ART / 'Previews~' / f'armas_{name}.png')
        bpy.ops.render.render(write_still=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
weapon_pistol()
weapon_taser()
long_gun('Weapon_Shotgun', rifle=False)
long_gun('Weapon_Rifle', rifle=True)
baton()
crowbar()
lockpick()
zip_ties()
drill()
glass_cutter()
hacking_tablet()
thermite()
grappling_hook()
grenade('Consumable_Smoke', 'Sage')
grenade('Consumable_Stun', 'Mustard')
grenade('Consumable_EMP', 'Berry', emp=True)
kit.write_materials(OUT / 'weapon_materials.json')
review()
print('ARMAS', len(PIECES))
