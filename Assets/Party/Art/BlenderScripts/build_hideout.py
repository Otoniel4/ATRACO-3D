"""Escondite de la banda: casa enterable con interior de escondite y patio cerrado por un muro completo.

Planta baja abierta: mesa de planificación con el mapa de la ciudad, tablero del golpe con fotos e hilos, casilleros de
equipo, panel de herramientas, mesa del dinero con caja fuerte y bolsos, puesto del hacker con tres pantallas, sala con
sofá y televisor, cocina, perchero de disfraces con espejo y luces de techo. El piso de arriba es solo fachada.
Patio: muro alto con puntas por los cuatro lados, portón peatonal con bisagra y garaje cubierto con persiana enrollable, cámara,
timbre, número, entrada de auto y camino de piedras.

Mismas convenciones que build_shops.py: frente -Y, origen en el centro de la casa a ras del suelo, puertas con el origen
en la bisagra. Nombres que lee Unity: DoorLeaf_L/R (puerta de la casa), GateLeaf_L y Umbral_Porton (portón peatonal),
GarageDoor, GarageOpen y Umbral_Auto (persiana del garaje), Edificio (la casa sin el patio).
Uso: blender -b --factory-startup -P build_hideout.py
Salida: Art/City/Shops/Local_Escondite.fbx, Art/City/Shops/hideout_materials.json y Previews~/escondite_*.png.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'City25~'))
import alarmart as a  # noqa: E402
from kit_parts import Kit  # noqa: E402

OUT = a.ART / 'City' / 'Shops'
W, D, WALL, H1, H = 11.8, 16.0, .2, 3.0, 6.6   # casa: ancho, fondo, muro, alto de la planta baja y total
F, BK = -D / 2, D / 2                          # fachada (calle) y fondo
GARAGE_REAR, GARAGE_SPLIT = F + 1.60, 2.4
YARD = 3.65                                    # el muro del patio queda a 3,65 m de la fachada (borde de la vereda + 0,35)
SIDE, REAR, PATIO_H = W / 2 + 1.0, BK + .9, 2.2
FRONT_WALL = F - YARD + .125                   # eje del muro delantero (0,25 de espesor)
GATE_MIN, GATE_MAX, WALK_TOP = -3.3, -1.9, .143
COLORS = dict(Facade='D8CDB8', Trim='3A4148', Glass=('8FB8C2', 0, .4), Roof='5A6068', Floor='A0764E', Ceiling='F4F4F0',
              DarkConcrete='6B6C69', Concrete='B9B5AC', Bars='2E3338', Steel='8A9499', Lamp=('FFF4D6', 2.0, 1),
              DarkWood='6E4A2E', Wood='B07A4E', MapGreen='3D6E4A', MapLine='F4F4F0', River='5FA8D3', Pin='D2372E',
              Cork='C49A62', Locker='7A8890', Sofa='8C4A3A', Rug='7A2E35', Screen=('4FB3FF', 1.2, 1), Black='22262A',
              Cash='4E9A5A', Duffel='23324A', Safe='3A3F45', Gold='D6A93A', Fridge='E8E8E4', Counter='D0CCC4', Red='D2372E',
              Yellow='F2C230', Navy='22385A', Orange='EE7F2D', White='F4F4F0', Cream='F2E3C0', Mirror=('C9D6DC', 0, 1),
              Hedge='4F8A4A', HedgeLight='779F50', HedgeShade='356D48', Soil='675443',
              Stone='A8A39A', Rubber='23282C')
kit = Kit(OUT, 'Alarma_Hideout_', COLORS)
B, C, T = kit.B, kit.C, kit.T
rng = random.Random('escondite')


def merge(objs, name):
    # Une piezas repetidas (puntas, listones) en una sola malla: una sola colisión en Unity.
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def wall_x(name, y, x0, x1, z0, z1, m, thick=WALL, parent=None):
    return B(name, ((x0 + x1) / 2, y, (z0 + z1) / 2), (x1 - x0, thick, z1 - z0), m, 0, parent=parent)


def wall_y(name, x, y0, y1, z0, z1, m, thick=WALL, parent=None):
    return B(name, (x, (y0 + y1) / 2, (z0 + z1) / 2), (thick, y1 - y0, z1 - z0), m, 0, parent=parent)


def window_x(name, y, x0, x1, z0, z1, parent, out=-1):
    B(name + 'Glass', ((x0 + x1) / 2, y, (z0 + z1) / 2), (x1 - x0, .03, z1 - z0), 'Glass', 0, parent=parent)
    B(name + 'Sill', ((x0 + x1) / 2, y + out * .08, z0 - .03), (x1 - x0 + .2, .18, .06), 'Trim', 0, parent=parent)
    B(name + 'Mullion', ((x0 + x1) / 2, y, (z0 + z1) / 2), (.05, .05, z1 - z0), 'Trim', 0, parent=parent)


def house(root):
    shell = a.empty('Edificio', parent=root)
    B('Floor', ((GARAGE_SPLIT - W / 2) / 2, 0, .075), (GARAGE_SPLIT + W / 2, D, .15), 'Floor', 0, parent=shell)
    B('Floor', ((GARAGE_SPLIT + W / 2) / 2, (GARAGE_REAR + BK) / 2, .075),
      (W / 2 - GARAGE_SPLIT, BK - GARAGE_REAR, .15), 'Floor', 0, parent=shell)
    B('Step', (0, F - .4, .075), (2.6, .8, .15), 'Concrete', .01, parent=shell)
    y = F + WALL / 2
    # Fachada: puerta doble al centro y dos ventanas.
    for x0, x1 in ((-W / 2, -4.6), (-2.4, -1.0), (1.0, GARAGE_SPLIT)):
        wall_x('FrontWall', y, x0, x1, 0, H1, 'Facade', parent=shell)
    wall_y('GarageReturn', GARAGE_SPLIT, F, GARAGE_REAR + WALL, 0, H1, 'Facade', parent=shell)
    wall_x('FrontWall', GARAGE_REAR + WALL / 2, 4.6, W / 2, 0, H1, 'Facade', parent=shell)
    for x0, x1, depth in ((-4.6, -2.4, y), (GARAGE_SPLIT, 4.6, GARAGE_REAR + WALL / 2)):
        wall_x('FrontSill', depth, x0, x1, 0, 1.0, 'Facade', parent=shell)
        wall_x('FrontHead', depth, x0, x1, 2.4, H1, 'Facade', parent=shell)
        window_x('FrontWindow', depth, x0, x1, 1.0, 2.4, shell)
    wall_x('DoorHead', y, -1.0, 1.0, 2.4, H1, 'Facade', parent=shell)
    y = BK - WALL / 2
    for x0, x1 in ((-W / 2, -4.0), (-2.0, 2.0), (4.0, W / 2)):
        wall_x('BackWall', y, x0, x1, 0, H1, 'Facade', parent=shell)
    for x0, x1 in ((-4.0, -2.0), (2.0, 4.0)):
        wall_x('BackSill', y, x0, x1, 0, 1.2, 'Facade', parent=shell)
        wall_x('BackHead', y, x0, x1, 2.4, H1, 'Facade', parent=shell)
        window_x('BackWindow', y, x0, x1, 1.2, 2.4, shell, out=1)
    for sx in (-1, 1):
        x = sx * (W / 2 - WALL / 2)
        wall_y('SideWall', x, GARAGE_REAR if sx > 0 else F, 1.5, 0, H1, 'Facade', parent=shell)
        wall_y('SideWall', x, 3.5, BK, 0, H1, 'Facade', parent=shell)
        wall_y('SideSill', x, 1.5, 3.5, 0, 1.0, 'Facade', parent=shell)
        wall_y('SideHead', x, 1.5, 3.5, 2.4, H1, 'Facade', parent=shell)
        B('SideGlass', (x, 2.5, 1.7), (.03, 2.0, 1.4), 'Glass', 0, parent=shell)
    # Piso de arriba: solo por fuera (su base es el cielo raso de la planta baja), con balcón y ventanas.
    B('Upper', (0, .3, (H1 + H) / 2), (W, D - .6, H - H1), 'Facade', 0, parent=shell)
    B('CeilingPanel', (0, 0, H1 - .01), (W - 2 * WALL, D - 2 * WALL, .02), 'Ceiling', 0, parent=shell)
    for x in (-3.6, 0, 3.6):  # pegadas a las caras del piso de arriba (retirado 0,6 m al frente)
        B('UpperWindow', (x, F + .6 - .02, 4.8), (2.2, .03, 1.4), 'Glass', 0, parent=shell)
        B('UpperWindow', (x, BK + .02, 4.8), (2.2, .03, 1.4), 'Glass', 0, parent=shell)
    B('Balcony', (0, F - .3, H1 + .05), (W, 1.2, .12), 'Trim', 0, parent=shell)
    B('BalconyGlass', (0, F - .88, H1 + .6), (W, .04, 1.0), 'Glass', 0, parent=shell)
    B('BalconyRail', (0, F - .88, H1 + 1.12), (W, .06, .05), 'Trim', 0, parent=shell)
    B('Roof', (0, .3, H + .08), (W + .2, D - .4, .16), 'Roof', 0, parent=shell)
    B('Canopy', (0, F - .6, 2.75), (2.8, 1.2, .1), 'Trim', 0, parent=shell)
    B('Band', (0, F - .01, H1), (W + .04, .06, .18), 'Trim', 0, parent=shell)
    B('WallLamp', (1.3, F - .05, 2.3), (.18, .1, .3), 'Lamp', 0, parent=shell)
    for x0, x1, depth in ((-W / 2, -1, F), (1, GARAGE_SPLIT, F), (GARAGE_SPLIT, W / 2, GARAGE_REAR)):
        wall_x('Detail_Foundation', depth - .015, x0, x1, 0, .16, 'Trim', .055, shell)
    for sx in (-1, 1):
        wall_y('Detail_FoundationSide', sx * (W / 2 + .015), GARAGE_REAR if sx > 0 else F, BK, 0, .16, 'Trim', .055, shell)
        B('Detail_DoorJamb', (sx * 1.025, F - .02, 1.27), (.075, .085, 2.28), 'Trim', .008, parent=shell)
    B('Detail_DoorLintel', (0, F - .02, 2.44), (2.13, .085, .08), 'Trim', .008, parent=shell)
    # Puerta doble con el origen en la bisagra (la abre Unity con E, igual que los locales).
    for side, sx in (('L', 1), ('R', -1)):
        hinge = a.empty('DoorLeaf_' + side, (sx * .9, F + WALL / 2, .15), parent=root)
        B('DoorPanel_' + side, (-sx * .45, 0, 1.10), (.88, .06, 2.2), 'Trim', .005, parent=hinge)
        B('DoorWindow_' + side, (-sx * .45, -.035, 1.6), (.5, .01, .8), 'Glass', 0, parent=hinge)
        B('DoorHandle_' + side, (-sx * .8, -.07, 1.05), (.04, .04, .3), 'Steel', .005, parent=hinge)
        B('Detail_DoorPushPlate', (-sx * .72, .026, 1.05), (.16, .010, .25), 'Steel', .004, parent=hinge)
        B('Detail_DoorPushPlate', (-sx * .72, -.036, 1.05), (.16, .010, .25), 'Steel', .004, parent=hinge)
        a.empty('PushContact_' + side, (-sx * .72, 0, 1.05), parent=hinge)


def interior(root):
    room = a.empty('Interior', parent=root)
    z = .15  # piso interior
    # Punto libre en el recibidor, por debajo de la losa; Unity usa este marcador en vez del centro del mapa.
    spawn = a.empty('PlayerSpawn', (0, -6.0, z + .035), parent=root)
    spawn.rotation_euler.z = math.pi  # mira hacia el interior (+Y)
    # Mesa de planificación con el mapa de la ciudad, pines y sillas.
    B('FloorTiles_Rug', (0, -1.8, z + .005), (4.2, 3.2, .01), 'Rug', 0, parent=room)
    B('Table', (0, -1.8, z + .76), (3.2, 1.7, .08), 'DarkWood', .01, parent=room)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B('TableLeg', (sx * 1.5, -1.8 + sy * .75, z + .37), (.08, .08, .74), 'DarkWood', 0, parent=room)
    B('Map', (0, -1.8, z + .805), (2.9, 1.4, .01), 'MapGreen', 0, parent=room)
    for x in (-1.0, 0.0, 1.0):
        B('MapLine', (x, -1.8, z + .812), (.04, 1.4, .004), 'MapLine', 0, parent=room)
    for y in (-2.3, -1.3):
        B('MapLine', (0, y, z + .812), (2.9, .04, .004), 'MapLine', 0, parent=room)
    B('MapRiver', (-.5, -1.8, z + .813), (.12, 1.4, .004), 'River', 0, rot=(0, 0, math.radians(25)), parent=room)
    for x, y in ((-.6, -1.4), (.5, -2.1), (1.1, -1.5), (-1.2, -2.2)):
        C('Pin', (x, y, z + .86), .025, .1, 'Pin', 8, parent=room)
    B('Target', (.55, -1.55, z + .815), (.32, .22, .004), 'Gold', 0, parent=room)
    for x in (-1.0, 0.0, 1.0):
        for side in (-1, 1):
            y = -1.8 + side * 1.2
            B('ChairSeat', (x, y, z + .46), (.46, .46, .06), 'Trim', .01, parent=room)
            B('ChairBack', (x, y + side * .22, z + .75), (.46, .05, .55), 'Trim', .01, parent=room)
            for dx in (-.17, .17):
                for dy in (-.17, .17):
                    B('Detail_ChairLeg', (x + dx, y + dy, z + .215), (.04, .04, .43), 'Steel', .004, parent=room)
            B('Detail_ChairBrace', (x, y + side * .17, z + .2), (.38, .03, .03), 'Steel', 0, parent=room)
    # Tablero del golpe: fotos, notas e hilos rojos.
    bx = -W / 2 + WALL + .02
    B('Board', (bx, -1.8, 1.75), (.04, 3.0, 1.4), 'Cork', .01, parent=room)
    T('BoardTitle', 'EL GOLPE', (bx + .03, -1.8, 2.3), .14, 'Black', rot=(math.pi / 2, 0, math.pi / 2), parent=room)
    photos = [(-3.0, 1.95), (-2.3, 1.55), (-1.6, 2.0), (-1.0, 1.45), (-.6, 1.9), (-2.7, 1.25), (-1.3, 1.15)]
    for i, (y, zz) in enumerate(photos):
        B('Photo', (bx + .03, y, zz), (.01, .3, .22), ('White', 'Cream', 'Yellow')[i % 3], 0, parent=room)
    for (y0, z0), (y1, z1) in ((photos[0], photos[1]), (photos[1], photos[3]), (photos[2], photos[4]), (photos[1], photos[6])):
        length = math.hypot(y1 - y0, z1 - z0)
        B('String', (bx + .045, (y0 + y1) / 2, (z0 + z1) / 2), (.005, length, .012), 'Red', 0,
          rot=(math.atan2(z1 - z0, y1 - y0), 0, 0), parent=room)
    # Casilleros de equipo y panel de herramientas en la pared derecha.
    lx = W / 2 - WALL - .27
    for i in range(4):
        y = -4.6 + i * .65
        B('Locker', (lx, y, z + .98), (.5, .62, 1.95), 'Locker', .01, parent=room)
        B('LockerVent', (lx - .26, y, z + 1.65), (.01, .4, .14), 'Trim', 0, parent=room)
        B('Detail_LockerHandle', (lx - .29, y + .21, z + 1.0), (.04, .04, .18), 'Steel', .005, parent=room)
        T('LockerNum', str(i + 1), (lx - .27, y, z + 1.4), .1, 'White', rot=(math.pi / 2, 0, -math.pi / 2), parent=room)
    px = W / 2 - WALL - .02
    B('Pegboard', (px, -.3, 1.6), (.03, 2.2, 1.2), 'Trim', 0, parent=room)
    B('Drill', (px - .1, -1.0, 1.75), (.12, .32, .16), 'Yellow', .02, parent=room)
    C('DrillBit', (px - .1, -.78, 1.78), .015, .2, 'Steel', 6, rot=(math.pi / 2, 0, 0), parent=room)
    B('Crowbar', (px - .05, -.2, 1.6), (.03, .05, .9), 'Red', 0, rot=(math.radians(20), 0, 0), parent=room)
    for t in (-12, 12):
        B('Cutter', (px - .06, .4, 1.55), (.03, .04, .7), 'Bars', 0, rot=(math.radians(t), 0, 0), parent=room)
    B('Flashlight', (px - .06, .75, 1.95), (.06, .3, .06), 'Black', .01, parent=room)
    # Dinero: mesa con fajos, bolsos y caja fuerte.
    B('MoneyTable', (1.6, 4.0, z + .74), (2.0, 1.0, .06), 'Wood', .01, parent=room)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B('MoneyLeg', (1.6 + sx * .9, 4.0 + sy * .42, z + .36), (.06, .06, .72), 'Wood', 0, parent=room)
    for i in range(3):
        for j in range(2):
            for k in range(2):
                B('Cash', (1.0 + i * .3, 3.8 + j * .25, z + .81 + k * .08), (.16, .08, .08), 'Cash', 0, parent=room)
                B('Detail_CashBand', (1.0 + i * .3, 3.8 + j * .25, z + .851 + k * .08), (.045, .082, .003), 'Cream', 0, parent=room)
    B('Duffel', (2.9, 4.8, z + .2), (.8, .4, .38), 'Duffel', .12, parent=room)
    B('Duffel', (.4, 4.9, z + .2), (.75, .4, .36), 'Duffel', .12, rot=(0, 0, math.radians(30)), parent=room)
    for x, y in ((2.9, 4.8), (.4, 4.9)):
        for side in (-1, 1):
            B('Detail_BagHandleSide', (x + side * .13, y, z + .44), (.035, .035, .16), 'Black', .005, parent=room)
        B('Detail_BagHandleTop', (x, y, z + .51), (.29, .035, .035), 'Black', .005, parent=room)
        B('Detail_BagZip', (x, y, z + .395), (.5, .02, .012), 'Steel', 0, parent=room)
    B('Safe', (5.15, 6.4, z + .5), (.8, .7, 1.0), 'Safe', .02, parent=room)
    C('SafeDial', (4.70, 6.4, z + .65), .08, .03, 'Gold', 16, rot=(0, math.pi / 2, 0), parent=room)
    B('Detail_SafeDoor', (4.738, 6.4, z + .5), (.025, .61, .86), 'Trim', .01, parent=room)
    B('Detail_SafeHandle', (4.70, 6.57, z + .46), (.06, .04, .22), 'Steel', .006, parent=room)
    # Puesto del hacker contra el fondo.
    B('Desk', (3.6, 7.3, z + .74), (2.6, .8, .06), 'DarkWood', .01, parent=room)
    for x in (2.4, 4.8):
        B('DeskLeg', (x, 7.3, z + .36), (.06, .7, .72), 'DarkWood', 0, parent=room)
    for i, x in enumerate((2.85, 3.6, 4.35)):
        monitor = B('Monitor', (x, 7.5, z + 1.1), (.6, .05, .38), 'Black', .01, rot=(0, 0, math.radians((i - 1) * -12)), parent=room)
        B('ScreenGlow', (0, -.035, 0), (.54, .01, .32), 'Screen', 0, parent=monitor)
        B('Detail_MonitorFoot', (x, 7.47, z + .79), (.25, .2, .04), 'Black', .01, parent=room)
        B('Detail_MonitorStand', (x, 7.50, z + .875), (.045, .045, .17), 'Steel', .004, parent=room)
        for line in range(3):
            B('Detail_ScreenText', (-.09, -.045, .08 - line * .065), (.22, .006, .012), 'Cream', 0, parent=monitor)
    B('Keyboard', (3.6, 7.05, z + .78), (.5, .16, .02), 'Black', 0, parent=room)
    B('OfficeSeat', (3.6, 6.4, z + .48), (.5, .5, .08), 'Black', .02, parent=room)
    B('OfficeBack', (3.6, 6.15, z + .85), (.5, .06, .6), 'Black', .02, parent=room)
    C('OfficePost', (3.6, 6.4, z + .22), .04, .44, 'Steel', 6, parent=room)
    for i in range(5):
        angle = i * math.tau / 5
        dx, dy = math.cos(angle), math.sin(angle)
        B('Detail_OfficeFoot', (3.6 + dx * .16, 6.4 + dy * .16, z + .07), (.34, .045, .035), 'Black', .006,
          rot=(0, 0, angle), parent=room)
        C('Detail_Caster', (3.6 + dx * .29, 6.4 + dy * .29, z + .04), .04, .045, 'Black', 8,
          rot=(math.pi / 2, 0, angle), parent=room)
    B('Detail_ComputerTower', (4.7, 7.35, z + .32), (.22, .45, .64), 'Black', .015, parent=room)
    # Sala: sofá frente al televisor.
    B('SofaBase', (-3.4, 7.2, z + .22), (2.2, .9, .44), 'Sofa', .05, parent=room)
    B('SofaBack', (-3.4, 7.55, z + .62), (2.2, .22, .5), 'Sofa', .05, parent=room)
    for x in (-4.45, -2.35):
        B('SofaArm', (x, 7.2, z + .5), (.2, .9, .3), 'Sofa', .04, parent=room)
    for x in (-3.92, -2.88):
        B('Detail_SofaCushion', (x, 7.05, z + .47), (.98, .65, .13), 'Sofa', .045, parent=room)
    B('CoffeeTable', (-3.4, 6.0, z + .38), (1.2, .6, .06), 'Wood', .02, parent=room)
    for dx in (-.5, .5):
        for dy in (-.22, .22):
            B('Detail_CoffeeLeg', (-3.4 + dx, 6.0 + dy, z + .175), (.06, .06, .35), 'DarkWood', .006, parent=room)
    B('TvStand', (-3.4, 4.6, z + .25), (1.6, .4, .5), 'DarkWood', .01, parent=room)
    B('Tv', (-3.4, 4.6, z + .95), (1.4, .06, .8), 'Black', .01, parent=room)
    B('TvGlow', (-3.4, 4.64, z + .95), (1.3, .01, .7), 'Screen', 0, parent=room)
    B('Detail_TvStand', (-3.4, 4.6, z + .54), (.08, .06, .08), 'Black', .005, parent=room)
    for x in (-3.86, -2.94):
        B('Detail_TvCabinetDoor', (x, 4.807, z + .25), (.86, .015, .4), 'Wood', .01, parent=room)
        B('Detail_TvCabinetHandle', (x, 4.83, z + .34), (.15, .03, .025), 'Steel', .003, parent=room)
    # Cocina junto a la pared izquierda.
    cx = -W / 2 + WALL + .3
    B('Counter', (cx, 2.8, z + .45), (.6, 2.2, .9), 'Counter', .01, parent=room)
    B('CounterTop', (cx, 2.8, z + .92), (.64, 2.24, .04), 'DarkWood', 0, parent=room)
    B('Fridge', (cx + .05, 1.2, z + .93), (.7, .7, 1.85), 'Fridge', .03, parent=room)
    B('FridgeHandle', (cx + .42, 1.45, z + 1.1), (.03, .03, .5), 'Steel', 0, parent=room)
    B('CoffeeMaker', (cx, 3.5, z + 1.1), (.25, .3, .32), 'Black', .02, parent=room)
    B('Microwave', (cx, 2.4, z + 1.08), (.4, .5, .28), 'White', .02, parent=room)
    # Frentes orientados al pasillo (+X), con superficies separadas para evitar parpadeo.
    for y in (2.1, 2.8, 3.5):
        B('Detail_KitchenDoor', (cx + .306, y, z + .44), (.014, .67, .78), 'White', .008, parent=room)
        B('Detail_KitchenHandle', (cx + .335, y + .21, z + .67), (.04, .035, .18), 'Steel', .004, parent=room)
    B('Detail_MicrowaveWindow', (cx + .207, 2.34, z + 1.08), (.012, .32, .18), 'Black', .01, parent=room)
    B('Detail_MicrowaveHandle', (cx + .23, 2.52, z + 1.08), (.04, .025, .17), 'Steel', .004, parent=room)
    B('Detail_CoffeePot', (cx + .07, 3.5, z + 1.05), (.13, .18, .14), 'Glass', .012, parent=room)
    B('Detail_CoffeeHandle', (cx + .15, 3.5, z + 1.08), (.04, .12, .06), 'Black', .006, parent=room)
    B('Detail_SinkRim', (cx, 3.0, z + .948), (.5, .42, .018), 'Steel', .02, parent=room)
    B('Detail_SinkBowl', (cx, 3.0, z + .96), (.38, .3, .012), 'Trim', .025, parent=room)
    C('Detail_FaucetPost', (cx - .17, 3.0, z + 1.08), .018, .25, 'Steel', 8, parent=room)
    B('Detail_FaucetSpout', (cx - .09, 3.0, z + 1.20), (.18, .035, .035), 'Steel', .006, parent=room)
    # Disfraces: perchero con ropas de colores y espejo.
    for y in (-7.0, -5.8):
        C('RackPost', (-4.2, y, z + .8), .025, 1.6, 'Steel', 6, parent=room)
    C('RackRod', (-4.2, -6.4, z + 1.6), .02, 1.2, 'Steel', 6, rot=(math.pi / 2, 0, 0), parent=room)
    for i, color in enumerate(('Red', 'Yellow', 'Navy', 'Orange', 'White', 'Trim')):
        y = -6.9 + i * .2
        B('Outfit', (-4.2, y, z + 1.1), (.4, .06, .9), color, .01, parent=room)
        B('Detail_Hanger', (-4.2, y, z + 1.58), (.32, .025, .025), 'Steel', .003, parent=room)
        C('Detail_HangerHook', (-4.2, y, z + 1.62), .009, .10, 'Steel', 6, parent=room)
        for side in (-1, 1):
            B('Detail_Sleeve', (-4.2 + side * .25, y, z + 1.36), (.16, .06, .30), color, .01,
              rot=(0, side * math.radians(18), 0), parent=room)
    B('Mirror', (-W / 2 + WALL + .02, -5.0, 1.3), (.02, .8, 1.6), 'Mirror', 0, parent=room)
    B('ShoeBench', (4.6, GARAGE_REAR + .56, z + .22), (1.4, .4, .44), 'Wood', .02, parent=room)
    for i, color in enumerate(('Navy', 'Black', 'Orange')):
        B('Jacket', (4.1 + i * .5, GARAGE_REAR + .3, z + 1.4), (.35, .08, .7), color, .02, parent=room)
    for x in (-3.0, 0.0, 3.0):
        for y in (-3.5, 3.0):
            B('CeilingLight', (x, y, H1 - .035), (.8, .8, .03), 'Lamp', 0, parent=room)


def walkway(parent, points, width):
    # Cinta continua con encuentros biselados. La cara superior queda sobre la vereda sin caras coplanares.
    centers = [Vector(p) for p in points]
    tangents = [(b - a).normalized() for a, b in zip(centers, centers[1:])]
    normals = [Vector((-t.y, t.x)) for t in tangents]
    left, right = [], []
    for i, center in enumerate(centers):
        before, after = normals[max(0, i - 1)], normals[min(i, len(normals) - 1)]
        miter = (before + after).normalized()
        offset = miter * (width / (2 * miter.dot(after)))
        left.append(center + offset)
        right.append(center - offset)
    outline = right + left[::-1]
    n = len(outline)
    vertices = [(v.x, v.y, z) for z in (0, WALK_TOP) for v in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return kit.use(a.mesh('PatioWalkway', vertices, faces, parent=parent), 'Stone')


def patio_planter(parent, x, y):
    B('PlanterBase', (x, y, .07), (2.52, .63, .14), 'DarkConcrete', .02, parent=parent)
    for dy in (-.285, .285):
        B('PlanterWall', (x, y + dy, .30), (2.55, .09, .32), 'Concrete', .015, parent=parent)
        B('Detail_PlanterRim', (x, y + dy, .47), (2.59, .12, .06), 'Stone', .008, parent=parent)
    for dx in (-1.23, 1.23):
        B('PlanterWallEnd', (x + dx, y, .30), (.09, .48, .32), 'Concrete', .012, parent=parent)
    B('Detail_PlanterSoil', (x, y, .4), (2.36, .48, .05), 'Soil', .005, parent=parent)
    leaves = {c: ([], []) for c in ('Hedge', 'HedgeLight', 'HedgeShade')}
    branches = []
    for index in range(7):
        center = Vector((x - 1.02 + index * .34, y, .425))
        branches.append(C('Detail_ShrubStem', center + Vector((0, 0, .215)), .014, .43, 'DarkWood', 6, parent=parent))
        for i in range(7):
            angle = i * 2.39996 + index
            length = rng.uniform(.15, .26)
            base = center + Vector((0, 0, .08 + i * .048))
            tip = base + Vector((math.cos(angle) * length, math.sin(angle) * length, .085))
            branch = tip - base
            branches.append(C('Detail_Twig', (base + tip) / 2, .008, branch.length, 'DarkWood', 5,
                              rot=branch.to_track_quat('Z', 'Y').to_euler(), parent=parent))
            for j in range(6):
                start = base.lerp(tip, (j + 1) / 6)
                spread = angle + (-.87 if j % 2 else .87)
                along = Vector((math.cos(spread), math.sin(spread), rng.uniform(.14, .45))).normalized()
                side = along.cross(Vector((0, 0, 1))).normalized() * rng.uniform(.028, .050)
                reach = rng.uniform(.095, .16)
                verts, faces = leaves[rng.choice(tuple(leaves))]
                first = len(verts)
                verts.extend([start, start + along * reach * .48 + side, start + along * reach,
                              start + along * reach * .48 - side, start + along * reach * .52 + Vector((0, 0, .014))])
                faces.extend((first + k, first + (k + 1) % 4, first + 4) for k in range(4))
    merge(branches, 'Detail_ShrubBranches')
    for color, (verts, faces) in leaves.items():
        kit.use(a.mesh('Detail_ShrubLeaves_' + color, verts, faces, parent=parent), color)


def patio(root):
    yard = a.empty('Patio', parent=root)
    spikes = []

    def wall(x0, y0, x1, y1):
        horizontal = abs(y1 - y0) < 1e-6
        length = abs(x1 - x0) if horizontal else abs(y1 - y0)
        mid = ((x0 + x1) / 2, (y0 + y1) / 2)
        size = (length, .25) if horizontal else (.25, length)
        B('PatioWall', (*mid, PATIO_H / 2), (*size, PATIO_H), 'DarkConcrete', .01, parent=yard)
        front_end_margin = 0 if horizontal and abs(mid[1] - FRONT_WALL) < .001 else .05
        B('PatioCap', (*mid, PATIO_H + .04), (size[0] + front_end_margin, size[1] + .05, .08), 'Concrete', 0, parent=yard)
        for i in range(int(length / .25)):
            t = (i + .5) / int(length / .25)
            spikes.append(B('Spike', (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, PATIO_H + .16), (.02, .02, .16), 'Bars', 0, parent=yard))
    y = FRONT_WALL
    for x0, x1 in ((-SIDE, GATE_MIN - .02), (GATE_MAX + .02, 2.8), (6.4, SIDE)):
        wall(x0, y, x1, y)
    for sx in (-1, 1):
        wall(sx * (SIDE - .125), y - .105, sx * (SIDE - .125), REAR - .02)
    wall(-SIDE, REAR - .125, SIDE, REAR - .125)
    merge(spikes, 'Spikes')
    # Hueco de 1,40 m y marco anclado a ambos muros. La hoja queda 2 cm por encima del pavimento.
    center = (GATE_MIN + GATE_MAX) / 2
    for x in (GATE_MIN - .11, GATE_MAX + .11):
        B('GatePost', (x, y, 1.18), (.22, .32, 2.36), 'DarkConcrete', .012, parent=yard)
    B('GateHeader', (center, y, 2.40), (1.84, .31, .10), 'Trim', .012, parent=yard)
    gate = a.empty('GateLeaf_L', (GATE_MAX - .13, y, WALK_TOP), parent=root)
    B('GatePanel', (-.63, 0, .56), (1.24, .055, 1.08), 'Bars', .007, parent=gate)
    for x in (-1.20, -.055):
        B('GateStile', (x, 0, 1.07), (.075, .07, 2.10), 'Trim', .008, parent=gate)
    for zz in (.06, 1.08, 2.08):
        B('GateCrossbar', (-.63, 0, zz), (1.24, .07, .075), 'Trim', .006, parent=gate)
    for i in range(9):
        B('Detail_GatePicket', (-1.13 + i * .126, 0, 1.56), (.03, .04, .96), 'Bars', .004, parent=gate)
    contact_x = center - gate.location.x
    for face in (-1, 1):
        B('Detail_GatePushPlate', (contact_x, face * .031, 1.13), (.18, .010, .28), 'Steel', .004, parent=gate)
        B('Detail_GateHandle', (-1.17, face * .078, 1.07), (.04, .055, .20), 'Bars', .006, parent=gate)
    a.empty('PushContact_L', (contact_x, 0, 1.13), parent=gate)
    a.empty('Umbral_Porton', (center, y, WALK_TOP), parent=root)
    for height in (.26, 1.86):
        B('Detail_GateHingeBracket', (GATE_MAX - .06, y, WALK_TOP + height), (.17, .10, .12), 'Steel', .007, parent=yard)
        C('Detail_GateHinge', (0, 0, height), .047, .14, 'Bars', 8, parent=gate)
    # Portón corredizo del auto: por dentro del muro, se corre 3,8 m hacia la izquierda detrás del tramo central.
    garage_y, shutter_height = y + .09, 2.465
    shutter = a.empty('GarageDoor', (4.6, garage_y, WALK_TOP), parent=root)
    for i in range(17):
        B(f'GarageSlat_{i:02}', (0, 0, (i + .5) * .145), (3.52, .08, .144),
          'Bars' if i % 3 else 'Trim', .005, parent=shutter)
    a.empty('GarageOpen', (4.6, garage_y, WALK_TOP + shutter_height), parent=root)
    a.empty('Umbral_Auto', (4.6, garage_y, WALK_TOP), parent=root)
    for x in (2.71, 6.49):
        B('GaragePost', (x, garage_y, 1.40), (.23, .33, 2.80), 'DarkConcrete', .012, parent=yard)
        B('Detail_GarageGuide', (x, garage_y - .18, 1.39), (.09, .045, 2.48), 'Steel', .007, parent=yard)
    B('Detail_GarageDrum', (4.6, garage_y - .07, WALK_TOP + shutter_height + .115), (3.75, .35, .28), 'Trim', .014, parent=yard)
    B('GarageCanopy', (4.6, (garage_y + GARAGE_REAR) / 2, 2.83), (4.08, GARAGE_REAR - garage_y + .34, .15), 'DarkConcrete', .01, parent=yard)
    B('Detail_GarageFascia', (4.6, garage_y - .19, 2.82), (4.08, .10, .18), 'Bars', .008, parent=yard)
    B('Detail_GarageButton', (6.49, garage_y - .18, 1.17), (.12, .065, .19), 'Trim', .012, parent=yard)
    B('Detail_GarageLED', (6.49, garage_y - .215, 1.20), (.05, .01, .04), 'Lamp', .006, parent=yard)
    wall_y('GaragePartition', 2.64, garage_y + .16, GARAGE_REAR, 0, 2.76, 'DarkConcrete', .18, yard)
    # Detalles del frente: número, timbre, luz y cámara sobre el muro, por dentro de la línea.
    B('NumberPlate', (-3.6, y - .14, 1.6), (.32, .02, .2), 'Black', 0, parent=yard)
    T('Number', '13', (-3.6, y - .155, 1.6), .14, 'White', parent=yard)
    B('Intercom', (-1.75, y - .14, 1.35), (.14, .02, .22), 'Steel', 0, parent=yard)
    lamp_x = GATE_MIN - .11
    B('Detail_GateLampBase', (lamp_x, y - .17, 2.04), (.17, .07, .34), 'Trim', .015, parent=yard)
    B('Detail_GateLamp', (lamp_x, y - .213, 2.04), (.12, .025, .22), 'Lamp', .01, parent=yard)
    B('Detail_CameraMast', (SIDE - .5, y + .105, PATIO_H + .145), (.08, .08, .27), 'Bars', .008, parent=yard)
    B('CamArm', (6.49, y + .2, PATIO_H + .25), (.06, .2, .06), 'Bars', 0, parent=yard)
    B('Camera', (6.49, y + .02, PATIO_H + .24), (.14, .26, .14), 'White', .01, rot=(math.radians(-15), 0, 0), parent=yard)
    # Calzada y paso peatonal apoyados en el terreno, a la altura de la acera.
    drive_front = y - .65
    B('Drive', (4.6, (drive_front + GARAGE_REAR) / 2, WALK_TOP / 2), (3.6, GARAGE_REAR - drive_front, WALK_TOP), 'Concrete', 0, parent=yard)
    wall_x('GarageBack', GARAGE_REAR + .08, W / 2, SIDE - .10, 0, 2.75, 'DarkConcrete', .16, yard)
    walkway(yard, ((center, y - .65), (center, y + 1.10), (-.65, F - 1.02), (0, F - .18)), 1.30)
    patio_planter(yard, -5.2, y + .72)


def review(root):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sky = bpy.data.worlds.new('Cielo')
    sky.color = (.62, .74, .9)
    scene.world = sky
    scene.view_settings.view_transform = 'Standard'
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_shadows = scene.display.shading.show_cavity = True
    scene.render.resolution_x, scene.render.resolution_y = 1800, 1000
    ground = bpy.data.meshes.new('Suelo')
    ground.from_pydata([(-30, -20, -.01), (30, -20, -.01), (30, 20, -.01), (-30, 20, -.01)], [], [(0, 1, 2, 3)])
    g = bpy.data.objects.new('Suelo', ground)
    scene.collection.objects.link(g)
    kit.colors['Pasto'] = '6E9A5C'
    g.data.materials.append(kit.M('Pasto'))
    # Acera de referencia con las cotas del emplazamiento R046. Solo se guarda en la escena de revisión.
    sidewalk = bpy.data.meshes.new('Acera_Referencia')
    sidewalk.from_pydata([(-30, -15.55, .14), (30, -15.55, .14), (30, -12.05, .14), (-30, -12.05, .14)], [], [(0, 1, 2, 3)])
    preview = bpy.data.objects.new('Acera_Referencia', sidewalk)
    scene.collection.objects.link(preview)
    preview.data.materials.append(kit.M('Concrete'))
    road = bpy.data.meshes.new('Calle_Referencia')
    road.from_pydata([(-30, -27.55, .045), (30, -27.55, .045), (30, -15.55, .045), (-30, -15.55, .045)], [], [(0, 1, 2, 3)])
    road_preview = bpy.data.objects.new('Calle_Referencia', road)
    scene.collection.objects.link(road_preview)
    road_preview.data.materials.append(kit.M('Black'))
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    hidden = [o for o in a.descendants(root) if o.name.startswith(('Upper', 'Roof', 'CeilingPanel', 'Balcony', 'CeilingLight'))]
    shots = (('frente', (-9, -26, 6), (0, -8, 2), 30, False), ('patio', (1.8, -8.9, 2.2), (-2.65, -11.4, 1.1), 25, False),
             ('planta', (0, -1, 28), (0, 0, 0), 35, True), ('interior', (-4.5, -7.2, 2.4), (1.5, 2, .9), 22, True),
             ('golpe', (3.0, -4.5, 2.2), (-5, -1.6, 1.2), 26, True), ('dinero', (-1.5, 1.0, 2.4), (3.5, 6.5, .8), 24, True))
    for label, eye, target, lens, cut in shots:
        for o in hidden:
            o.hide_render = cut
        cam.location, cam.data.lens = eye, lens
        cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(a.ART / 'Previews~' / f'escondite_{label}.png')
        bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False


if bpy.app.background:
    bpy.ops.wm.read_factory_settings(use_empty=True)
else:
    # Reiniciar preferencias de fábrica corta el socket MCP; aislar la revisión conserva la conexión.
    scene = bpy.data.scenes.new('Alarma_Hideout_Revision')
    bpy.context.window.scene = scene
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
root = a.begin('Local_Escondite', 'City/Shops')
house(root)
interior(root)
patio(root)
meshes = [o for o in a.descendants(root) if o.type == 'MESH']
print('ESCONDITE', len(meshes), 'piezas', sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons), 'triángulos')
a.export_asset('Local_Escondite')
kit.write_materials(OUT / 'hideout_materials.json')
review(root)
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / 'BlenderSources~' / 'Alarma_Escondite.blend'))
