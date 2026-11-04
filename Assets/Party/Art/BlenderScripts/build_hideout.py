"""Escondite de la banda: casa enterable con interior de escondite y patio cerrado por un muro completo.

Planta baja abierta: mesa de planificación con el mapa de la ciudad, tablero del golpe con fotos e hilos, casilleros de
equipo, panel de herramientas, mesa del dinero con caja fuerte y bolsos, puesto del hacker con tres pantallas, sala con
sofá y televisor, cocina, perchero de disfraces con espejo y luces de techo. El piso de arriba es solo fachada.
Patio: muro alto con puntas por los cuatro lados, portón peatonal con bisagra y portón corredizo para el auto, cámara,
timbre, número, entrada de auto y camino de piedras.

Mismas convenciones que build_shops.py: frente -Y, origen en el centro de la casa a ras del suelo, puertas con el origen
en la bisagra. Nombres que lee Unity: DoorLeaf_L/R (puerta de la casa), GateLeaf_L y Umbral_Porton (portón peatonal),
SlideGate, SlideGate_Abierto y Umbral_Auto (portón corredizo), Edificio (la casa sin el patio).
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
YARD = 3.65                                    # el muro del patio queda a 3,65 m de la fachada (borde de la vereda + 0,35)
SIDE, REAR, PATIO_H = W / 2 + 1.0, BK + .9, 2.2
FRONT_WALL = F - YARD + .125                   # eje del muro delantero (0,25 de espesor)
COLORS = dict(Facade='D8CDB8', Trim='3A4148', Glass=('8FB8C2', 0, .4), Roof='5A6068', Floor='A0764E', Ceiling='F4F4F0',
              DarkConcrete='6B6C69', Concrete='B9B5AC', Bars='2E3338', Steel='8A9499', Lamp=('FFF4D6', 2.0, 1),
              DarkWood='6E4A2E', Wood='B07A4E', MapGreen='3D6E4A', MapLine='F4F4F0', River='5FA8D3', Pin='D2372E',
              Cork='C49A62', Locker='7A8890', Sofa='8C4A3A', Rug='7A2E35', Screen=('4FB3FF', 1.2, 1), Black='22262A',
              Cash='4E9A5A', Duffel='23324A', Safe='3A3F45', Gold='D6A93A', Fridge='E8E8E4', Counter='D0CCC4', Red='D2372E',
              Yellow='F2C230', Navy='22385A', Orange='EE7F2D', White='F4F4F0', Cream='F2E3C0', Mirror=('C9D6DC', 0, 1),
              Hedge='4F8A4A', Stone='A8A39A', Rubber='23282C')
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
    B('Floor', (0, 0, .075), (W, D, .15), 'Floor', 0, parent=shell)
    B('Step', (0, F - .4, .075), (2.6, .8, .15), 'Concrete', .01, parent=shell)
    y = F + WALL / 2
    # Fachada: puerta doble al centro y dos ventanas.
    for x0, x1 in ((-W / 2, -4.6), (-2.4, -1.0), (1.0, 2.4), (4.6, W / 2)):
        wall_x('FrontWall', y, x0, x1, 0, H1, 'Facade', parent=shell)
    for x0, x1 in ((-4.6, -2.4), (2.4, 4.6)):
        wall_x('FrontSill', y, x0, x1, 0, 1.0, 'Facade', parent=shell)
        wall_x('FrontHead', y, x0, x1, 2.4, H1, 'Facade', parent=shell)
        window_x('FrontWindow', y, x0, x1, 1.0, 2.4, shell)
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
        wall_y('SideWall', x, F, 1.5, 0, H1, 'Facade', parent=shell)
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
    # Puerta doble con el origen en la bisagra (la abre Unity con E, igual que los locales).
    for side, sx in (('L', 1), ('R', -1)):
        hinge = a.empty('DoorLeaf_' + side, (sx * .9, F + WALL / 2, .15), parent=root)
        B('DoorPanel_' + side, (-sx * .45, 0, 1.15), (.88, .06, 2.3), 'Trim', .005, parent=hinge)
        B('DoorWindow_' + side, (-sx * .45, -.035, 1.6), (.5, .01, .8), 'Glass', 0, parent=hinge)
        B('DoorHandle_' + side, (-sx * .8, -.07, 1.05), (.04, .04, .3), 'Steel', .005, parent=hinge)


def interior(root):
    room = a.empty('Interior', parent=root)
    z = .15  # piso interior
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
            C('ChairPost', (x, y, z + .22), .03, .44, 'Steel', 6, parent=room)
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
    B('Duffel', (2.9, 4.8, z + .2), (.8, .4, .38), 'Duffel', .12, parent=room)
    B('Duffel', (.4, 4.9, z + .2), (.75, .4, .36), 'Duffel', .12, rot=(0, 0, math.radians(30)), parent=room)
    B('Safe', (5.15, 6.4, z + .5), (.8, .7, 1.0), 'Safe', .02, parent=room)
    C('SafeDial', (4.74, 6.4, z + .65), .08, .03, 'Gold', 16, rot=(0, math.pi / 2, 0), parent=room)
    # Puesto del hacker contra el fondo.
    B('Desk', (3.6, 7.3, z + .74), (2.6, .8, .06), 'DarkWood', .01, parent=room)
    for x in (2.4, 4.8):
        B('DeskLeg', (x, 7.3, z + .36), (.06, .7, .72), 'DarkWood', 0, parent=room)
    for i, x in enumerate((2.85, 3.6, 4.35)):
        B('Monitor', (x, 7.5, z + 1.1), (.6, .05, .38), 'Black', .01, rot=(0, 0, math.radians((i - 1) * -12)), parent=room)
        B('ScreenGlow', (x, 7.47, z + 1.1), (.54, .01, .32), 'Screen', 0, rot=(0, 0, math.radians((i - 1) * -12)), parent=room)
    B('Keyboard', (3.6, 7.05, z + .78), (.5, .16, .02), 'Black', 0, parent=room)
    B('OfficeSeat', (3.6, 6.4, z + .48), (.5, .5, .08), 'Black', .02, parent=room)
    B('OfficeBack', (3.6, 6.15, z + .85), (.5, .06, .6), 'Black', .02, parent=room)
    C('OfficePost', (3.6, 6.4, z + .22), .04, .44, 'Steel', 6, parent=room)
    # Sala: sofá frente al televisor.
    B('SofaBase', (-3.4, 7.2, z + .22), (2.2, .9, .44), 'Sofa', .05, parent=room)
    B('SofaBack', (-3.4, 7.55, z + .62), (2.2, .22, .5), 'Sofa', .05, parent=room)
    for x in (-4.45, -2.35):
        B('SofaArm', (x, 7.2, z + .5), (.2, .9, .3), 'Sofa', .04, parent=room)
    B('CoffeeTable', (-3.4, 6.0, z + .2), (1.2, .6, .4), 'Wood', .02, parent=room)
    B('TvStand', (-3.4, 4.6, z + .25), (1.6, .4, .5), 'DarkWood', .01, parent=room)
    B('Tv', (-3.4, 4.6, z + .95), (1.4, .06, .8), 'Black', .01, parent=room)
    B('TvGlow', (-3.4, 4.64, z + .95), (1.3, .01, .7), 'Screen', 0, parent=room)
    # Cocina junto a la pared izquierda.
    cx = -W / 2 + WALL + .3
    B('Counter', (cx, 2.8, z + .45), (.6, 2.2, .9), 'Counter', .01, parent=room)
    B('CounterTop', (cx, 2.8, z + .92), (.64, 2.24, .04), 'DarkWood', 0, parent=room)
    B('Fridge', (cx + .05, 1.2, z + .93), (.7, .7, 1.85), 'Fridge', .03, parent=room)
    B('FridgeHandle', (cx + .42, 1.45, z + 1.1), (.03, .03, .5), 'Steel', 0, parent=room)
    B('CoffeeMaker', (cx, 3.5, z + 1.1), (.25, .3, .32), 'Black', .02, parent=room)
    B('Microwave', (cx, 2.4, z + 1.08), (.4, .5, .28), 'White', .02, parent=room)
    # Disfraces: perchero con ropas de colores y espejo.
    for y in (-7.0, -5.8):
        C('RackPost', (-4.2, y, z + .8), .025, 1.6, 'Steel', 6, parent=room)
    C('RackRod', (-4.2, -6.4, z + 1.6), .02, 1.2, 'Steel', 6, rot=(math.pi / 2, 0, 0), parent=room)
    for i, color in enumerate(('Red', 'Yellow', 'Navy', 'Orange', 'White', 'Trim')):
        B('Outfit', (-4.2, -6.9 + i * .2, z + 1.1), (.4, .06, .9), color, .01, parent=room)
    B('Mirror', (-W / 2 + WALL + .02, -5.0, 1.3), (.02, .8, 1.6), 'Mirror', 0, parent=room)
    B('ShoeBench', (4.6, -7.4, z + .22), (1.4, .4, .44), 'Wood', .02, parent=room)
    for i, color in enumerate(('Navy', 'Black', 'Orange')):
        B('Jacket', (4.1 + i * .5, -7.7, z + 1.4), (.35, .08, .7), color, .02, parent=room)
    for x in (-3.0, 0.0, 3.0):
        for y in (-3.5, 3.0):
            B('CeilingLight', (x, y, H1 - .035), (.8, .8, .03), 'Lamp', 0, parent=room)


def patio(root):
    yard = a.empty('Patio', parent=root)
    spikes = []

    def wall(x0, y0, x1, y1):
        horizontal = abs(y1 - y0) < 1e-6
        length = abs(x1 - x0) if horizontal else abs(y1 - y0)
        mid = ((x0 + x1) / 2, (y0 + y1) / 2)
        size = (length, .25) if horizontal else (.25, length)
        B('PatioWall', (*mid, PATIO_H / 2), (*size, PATIO_H), 'DarkConcrete', .01, parent=yard)
        B('PatioCap', (*mid, PATIO_H + .04), (size[0] + (.05 if horizontal else .05), size[1] + .05, .08), 'Concrete', 0, parent=yard)
        for i in range(int(length / .25)):
            t = (i + .5) / int(length / .25)
            spikes.append(B('Spike', (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, PATIO_H + .16), (.02, .02, .16), 'Bars', 0, parent=yard))
    y = FRONT_WALL
    for x0, x1 in ((-SIDE, -3.2), (-2.0, 2.8), (6.4, SIDE)):
        wall(x0, y, x1, y)
    for sx in (-1, 1):
        wall(sx * (SIDE - .125), y - .125, sx * (SIDE - .125), REAR)
    wall(-SIDE, REAR - .125, SIDE, REAR - .125)
    merge(spikes, 'Spikes')
    # Portón peatonal con bisagra en su lado derecho (como la hoja izquierda de los locales): se abre hacia el patio.
    gate = a.empty('GateLeaf_L', (-2.0, y, 0), parent=root)
    B('GatePanel', (-.6, 0, 1.0), (1.18, .06, 1.95), 'Bars', .005, parent=gate)
    for zz in (.5, 1.0, 1.5):
        B('GateSlat', (-.6, -.035, zz), (1.1, .01, .08), 'DarkConcrete', 0, parent=gate)
    B('GateHandle', (-1.05, -.07, 1.05), (.04, .04, .25), 'Steel', 0, parent=gate)
    a.empty('Umbral_Porton', (-2.6, y, 0), parent=root)
    # Portón corredizo del auto: por dentro del muro, se corre 3,8 m hacia la izquierda detrás del tramo central.
    slide = a.empty('SlideGate', (4.6, y + .3, 0), parent=root)
    B('SlidePanel', (0, 0, 1.05), (3.7, .06, 2.0), 'Bars', .005, parent=slide)
    for zz in (.45, .85, 1.25, 1.65):
        B('SlideSlat', (0, -.035, zz), (3.6, .01, .08), 'DarkConcrete', 0, parent=slide)
    for x in (-1.5, 1.5):
        C('SlideWheel', (x, 0, .07), .07, .05, 'Rubber', 10, rot=(math.pi / 2, 0, 0), parent=slide)
    a.empty('SlideGate_Abierto', (4.6 - 3.8, y + .3, 0), parent=root)
    a.empty('Umbral_Auto', (4.6, y, 0), parent=root)
    B('Rail', (2.7, y + .3, .02), (7.6, .12, .04), 'Steel', 0, parent=yard)
    # Detalles del frente: número, timbre, luz y cámara sobre el muro, por dentro de la línea.
    B('NumberPlate', (-3.6, y - .14, 1.6), (.32, .02, .2), 'Black', 0, parent=yard)
    T('Number', '13', (-3.6, y - .155, 1.6), .14, 'White', parent=yard)
    B('Intercom', (-1.75, y - .14, 1.35), (.14, .02, .22), 'Steel', 0, parent=yard)
    B('GateLamp', (-2.6, y - .14, 2.05), (.3, .04, .12), 'Lamp', 0, parent=yard)
    B('CamArm', (SIDE - .5, y + .2, PATIO_H + .25), (.06, .2, .06), 'Bars', 0, parent=yard)
    B('Camera', (SIDE - .5, y + .02, PATIO_H + .24), (.14, .26, .14), 'White', .01, rot=(math.radians(-15), 0, 0), parent=yard)
    # Suelo del patio: entrada de auto y camino de piedras del portón a la puerta; canteros junto al muro.
    B('Drive', (4.6, (y + F) / 2, .02), (3.6, abs(F - y) - .2, .04), 'Concrete', 0, parent=yard)
    for i in range(6):
        t = (i + .5) / 6
        B('PathStone', (-2.6 + 2.6 * t, y + .5 + (F - .9 - y - .5) * t, .02), (.8, .4, .04), 'Stone', 0,
          rot=(0, 0, math.radians(-35)), parent=yard)
    B('Planter', (-5.2, y + .6, .3), (2.6, .6, .6), 'Concrete', .01, parent=yard)
    B('PlanterHedge', (-5.2, y + .6, .8), (2.4, .5, .5), 'Hedge', .06, parent=yard)


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
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    hidden = [o for o in a.descendants(root) if o.name.startswith(('Upper', 'Roof', 'CeilingPanel', 'Balcony', 'CeilingLight'))]
    shots = (('frente', (-9, -26, 6), (0, -8, 2), 30, False), ('patio', (-6, -10.6, 1.7), (2, -7.5, 1.4), 24, False),
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


bpy.ops.wm.read_factory_settings(use_empty=True)
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
