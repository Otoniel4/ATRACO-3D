"""Kit de barrios y lugares de la ciudad 3.0 (fase B1).

Barrios: antejardines de casas con cerca (madera, reja o seto), portón, canteros con flores y camino de piedras;
cerca de malla para galpones; contenedores marítimos, pallets, tambores, grúa horquilla y neumáticos para los patios
industriales; pizarras de vereda para los comercios.
Lugares: gasolinera completa (techo, islas con surtidores, tienda 24 h, tótem de precios), estacionamiento (caseta,
barreras, topes, muros con seto, letrero P), letreros del reducidor y de los talleres (el escondite tiene su propio modelo: build_hideout.py).

Las cercas y los lugares conservan su origen de diseño (línea de la cerca o centro del lote); el resto se centra.
Uso: blender -b --factory-startup -P build_district_kit.py
Salida: Art/City/Kit25/District/<pieza>.fbx, Art/City/Kit25/district_kit.json, district_materials.json
        y renders/district_kit_*.png para revisión.
"""
import math
import random
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import alarmart as a  # noqa: E402
from kit_parts import FACE, Kit, review_stage  # noqa: E402

KIT_DIR = a.ART / 'City' / 'Kit25'
COLORS = dict(Steel='8A9499', DarkSteel='454D53', Concrete='B9B5AC', DarkConcrete='6B6C69', White='F4F4F0', Picket='F1EEE4',
              Bars='2E3338', Brick='B5654A', Hedge='4F8A4A', HedgeDark='3D6E3A', Soil='6B4A32', Stone='A8A39A', Leaf='5C9A4E',
              FlowerRed='D9443A', FlowerYellow='F2C230', FlowerPink='E07AA8', FlowerPurple='8E5BB0', Glass=('A9D3DB', 0, .35),
              Chain=('9AA3A8', 0, .5), Canopy='F4F4F0', Brand='C8322B', Navy='22385A', Yellow='F2C230', Orange='EE7F2D',
              Black='22262A', Rubber='23282C', Digit=('FFB23A', 1.5, 1), Lamp=('FFF4D6', 2.0, 1), ContainerRed='B5452F',
              ContainerBlue='2F5E9E', ContainerGreen='3E7D4A', Pallet='C49A62', Cardboard='C8A16E', Forklift='F2B230',
              Barrel='2F6EA8', BarrelRed='C0392B', Wood='B07A4E', SignBlue='2C5BB8', Chalk='2B2F2C', Cream='F2E3C0', Red='D2372E',
              Sofa='8C6A4E')
FLOWERS = ['FlowerRed', 'FlowerYellow', 'FlowerPink', 'FlowerPurple']
kit = Kit(KIT_DIR / 'District', 'Alarma_District_', COLORS)
B, C, S, T, begin, finish = kit.B, kit.C, kit.S, kit.T, kit.begin, kit.finish
HOUSE_WIDTHS = (11.87, 12.87, 13.87)  # anchos de las casas del kit: una cerca por ancho
WAREHOUSE_WIDTH = 32.3


def spans(length, gaps):
    # Tramos de cerca entre -length/2 y length/2 dejando libres los huecos (x0, x1).
    out, x = [], -length / 2
    for g0, g1 in sorted(gaps):
        if g0 > x:
            out.append((x, g0))
        x = max(x, g1)
    if x < length / 2:
        out.append((x, length / 2))
    return out


def garden(length, rng):
    # Canteros con flores a los lados del camino y camino de piedras del portón a la casa.
    for side in (-1, 1):
        x = side * (length / 2 - 1.7)
        B('Bed', (x, 1.25, .08), (2.2, .7, .16), 'Soil', .02)
        for i in range(8):
            fx, fy = x - .9 + (i % 4) * .6 + rng.uniform(-.08, .08), 1.08 + (i // 4) * .34
            S('Leaves', (fx, fy, .2), (.16, .16, .1), 'Leaf', 1)
            S('Flower', (fx, fy, .29), (.09, .09, .08), rng.choice(FLOWERS), 1)
    for i in range(5):  # el camino termina antes de la casa más cercana a la vereda (retiro de 4 m)
        B('Stone', (rng.uniform(-.05, .05), .45 + i * .55, .02), (.85, .4, .04), 'Stone', 0)


def open_leaf(hinge_x, width, height, z, m, angle=35, thick=.04):
    # Hoja de portón abierta hacia adentro (+Y) girando sobre su bisagra.
    t = math.radians(angle)
    B('Gate', (hinge_x + math.cos(t) * width / 2, .05 + math.sin(t) * width / 2, z), (width, thick, height), m, 0, rot=(0, 0, t))


def picket_gate(hinge_x, width, angle=35):
    # Portón de listones abierto hacia adentro, con los mismos listones y travesaños que la cerca.
    t = math.radians(angle)
    dx, dy = math.cos(t), math.sin(t)
    for z in (.3, .8):
        B('GateRail', (hinge_x + dx * width / 2, .05 + dy * width / 2, z), (width, .04, .06), 'Picket', 0, rot=(0, 0, t))
    for i in range(7):
        along = .1 + i * (width - .2) / 6
        B('GatePicket', (hinge_x + dx * along, .03 + dy * along, .5), (.07, .025, .95), 'Picket', 0, rot=(0, 0, t))


def yard(style, width):
    piece = f'Yard_{style}_{round(width)}'
    begin(piece)
    rng = random.Random(piece)
    length = width + 2.0  # la cerca sobresale 1 m a cada lado de la casa
    parts = spans(length, [(-.7, .7)])
    if style == 'Picket':
        for x0, x1 in parts:
            for x in [x0 + .05] + [x0 + k * 2 for k in range(1, int((x1 - x0) / 2) + 1) if x0 + k * 2 < x1 - .3] + [x1 - .05]:
                B('Post', (x, .05, .55), (.1, .1, 1.1), 'Picket', .01)
            for z in (.3, .8):
                B('Rail', ((x0 + x1) / 2, .08, z), (x1 - x0, .04, .06), 'Picket', 0)
            x = x0 + .14
            while x < x1 - .08:
                B('Picket', (x, .03, .5), (.07, .025, .95), 'Picket', 0)
                x += .17
        picket_gate(-.7, 1.35)
    elif style == 'Bars':
        for x0, x1 in parts:
            B('Wall', ((x0 + x1) / 2, .1, .25), (x1 - x0, .2, .5), 'Brick', .01)
            B('Cap', ((x0 + x1) / 2, .1, .52), (x1 - x0, .24, .05), 'Concrete', 0)
            B('TopRail', ((x0 + x1) / 2, .1, 1.38), (x1 - x0, .04, .04), 'Bars', 0)
            x = x0 + .2
            while x < x1 - .1:
                B('Bar', (x, .1, .96), (.025, .025, .84), 'Bars', 0)
                x += .14
            for x in (x0 + .16, x1 - .16):
                B('Pillar', (x, .1, .72), (.32, .32, 1.44), 'Brick', .01)
                B('PillarCap', (x, .1, 1.47), (.38, .38, .06), 'Concrete', 0)
        open_leaf(-.55, 1.1, 1.2, .7, 'Bars', angle=30, thick=.03)
    else:  # Hedge
        for x0, x1 in parts:
            n = max(1, round(x1 - x0))
            for i in range(n):
                h = rng.uniform(.95, 1.15)
                B('Hedge', (x0 + (i + .5) * (x1 - x0) / n, .35, h / 2), ((x1 - x0) / n + .02, .7, h), 'Hedge' if i % 2 else 'HedgeDark', .06)
        for x in (-.85, .85):
            B('GatePost', (x, .35, .6), (.3, .3, 1.2), 'Stone', .01)
        open_leaf(-.7, 1.35, .9, .5, 'Bars', angle=40, thick=.03)
    garden(length, rng)
    return finish(piece, 'yard', recenter=False)


def chain_fence():
    # Cerca de malla del galpón: libres los dos portones (x -10,5 a 8) y la puerta lateral (10,5 a 12).
    piece = f'Yard_Chain_{round(WAREHOUSE_WIDTH)}'
    begin(piece)
    length = WAREHOUSE_WIDTH + 4.0
    for x0, x1 in spans(length, [(-10.5, 8.0), (10.5, 12.0)]):
        n = max(1, math.ceil((x1 - x0) / 3))
        for i in range(n + 1):
            C('Post', (x0 + i * (x1 - x0) / n, .05, 1.05), .04, 2.1, 'Steel', 8)
        B('Mesh', ((x0 + x1) / 2, .05, 1.05), (x1 - x0, .01, 1.9), 'Chain', 0)
        B('TopRail', ((x0 + x1) / 2, .05, 2.08), (x1 - x0, .04, .04), 'Steel', 0)
    B('Slide', (-length / 2 + 4.2, .4, 1.0), (7.0, .03, 1.8), 'Chain', 0)
    B('SlideFrame', (-length / 2 + 4.2, .4, 1.92), (7.0, .05, .06), 'Steel', 0)
    for x in (-10.4, 7.9):
        C('Bollard', (x, .35, .45), .1, .9, 'Yellow', 10)
    B('Sign', (-12.5, -.02, 1.4), (.7, .02, .35), 'Red', 0)
    T('SignText', 'PRIVADO', (-12.5, -.04, 1.4), .11, 'White')
    return finish(piece, 'yard', recenter=False)


def container(piece, color):
    begin(piece)
    B('Body', (0, 0, 1.3), (6.0, 2.38, 2.5), color, 0)
    for z in (.06, 2.53):
        B('Frame', (0, 0, z), (6.06, 2.44, .12), 'DarkSteel', 0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B('Corner', (sx * 2.955, sy * 1.145, 1.3), (.15, .15, 2.6), 'DarkSteel', 0)
    x = -2.7
    while x < 2.8:
        for sy in (-1, 1):
            B('Rib', (x, sy * 1.205, 1.3), (.12, .03, 2.3), color, 0)
        x += .3
    for y in (-.6, -.2, .2, .6):
        C('Lock', (3.02, y, 1.3), .022, 2.3, 'Steel', 6)
    B('DoorSeam', (3.01, 0, 1.3), (.02, .03, 2.35), 'DarkSteel', 0)
    T('Name', 'VILLA LINES', (0, -1.23, 1.6), .38, 'White')
    return finish(piece, 'container')


def pallets():
    begin('PalletStack')

    def pallet(x, z):
        for y in (-.42, 0, .42):
            B('Runner', (x, y, z + .05), (1.2, .1, .1), 'Pallet', 0)
        for i in range(5):
            B('Board', (x - .5 + i * .25, 0, z + .115), (.14, 1.0, .03), 'Pallet', 0)
    pallet(0, 0)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                B('Box', (-.29 + i * .58, -.24 + j * .48, .33 + k * .41), (.55, .45, .4), 'Cardboard', .01)
                B('Tape', (-.29 + i * .58, -.24 + j * .48, .535 + k * .41), (.08, .46, .005), 'Cream', 0)
    for k in range(4):
        pallet(1.45, k * .14)
    return finish('PalletStack', 'pallets')


def barrels():
    begin('Barrels')
    for i, (x, y) in enumerate(((0, 0), (.62, .1), (.3, .58), (-.32, .55))):
        m = 'Barrel' if i % 2 == 0 else 'BarrelRed'
        C('Drum', (x, y, .44), .29, .88, m, 16)
        for z in (.3, .6):
            C('Ring', (x, y, z), .3, .03, 'DarkSteel', 16)
        C('Lid', (x, y, .885), .27, .01, 'DarkSteel', 16)
        C('Bung', (x + .14, y, .9), .04, .03, 'Steel', 8)
    return finish('Barrels', 'barrels')


def forklift():
    begin('Forklift')
    B('Body', (0, .25, .65), (1.1, 1.6, .7), 'Forklift', .04)
    B('Counterweight', (0, 1.0, .75), (1.12, .45, .9), 'Forklift', .05)
    B('Seat', (0, .45, 1.08), (.45, .45, .1), 'Black', .02)
    B('Backrest', (0, .68, 1.32), (.45, .08, .45), 'Black', .02)
    for sx in (-1, 1):
        for y in (-.35, .85):
            B('Guard', (sx * .48, y, 1.6), (.06, .06, 1.0), 'DarkSteel', 0)
        B('Rail', (sx * .35, -.75, 1.25), (.08, .12, 2.3), 'DarkSteel', 0)
        B('Fork', (sx * .25, -1.3, .08), (.1, 1.05, .05), 'DarkSteel', 0)
        B('ForkUp', (sx * .25, -.82, .35), (.1, .05, .55), 'DarkSteel', 0)
        C('Front', (sx * .5, -.45, .3), .3, .25, 'Rubber', 14, rot=(0, math.pi / 2, 0))
        C('Rear', (sx * .45, .95, .25), .25, .22, 'Rubber', 14, rot=(0, math.pi / 2, 0))
    B('Roof', (0, .25, 2.12), (1.04, 1.3, .05), 'DarkSteel', 0)
    B('Carriage', (0, -.86, .5), (.8, .05, .45), 'DarkSteel', 0)
    C('Wheel', (0, -.1, 1.35), .16, .03, 'Black', 12, rot=(math.radians(55), 0, 0))
    B('Headlight', (0, -.42, 2.05), (.3, .06, .1), 'Lamp', 0)
    return finish('Forklift', 'forklift')


def tires():
    begin('TireStack')
    for x in (0, .78):
        for k in range(4):
            C('Tire', (x, 0, .11 + k * .22), .33, .21, 'Rubber', 16)
        C('Hub', (x, 0, .89), .2, .02, 'DarkSteel', 12)
    return finish('TireStack', 'tires')


def sidewalk_sign():
    begin('SidewalkSign')
    for side in (-1, 1):
        t = math.radians(12) * side
        y = -side * .105
        B('Frame', (0, y, .5), (.66, .025, 1.0), 'Wood', 0, rot=(-t, 0, 0))
        B('Board', (0, y - side * .014, .52), (.56, .01, .82), 'Chalk', 0, rot=(-t, 0, 0))
    tilt = math.radians(12)
    T('Text', 'OFERTA\nDEL DIA', (0, -.125, .62), .085, 'White', rot=(math.pi / 2 - tilt, 0, 0))
    B('Star', (0, -.13, .34), (.12, .01, .12), 'Yellow', 0, rot=(-tilt, 0, math.radians(45)))
    return finish('SidewalkSign', 'asign')


def yard_sign(piece, background, band, title, subtitle, title_color, subtitle_color):
    # Letrero sobre dos postes, detrás de la cerca, mirando a la calle.
    begin(piece)
    for sx in (-1, 1):
        B('Post', (sx * 2.6, .1, 1.8), (.2, .2, 3.6), 'Steel', .01)
    B('Frame', (0, .1, 3.3), (6.4, .15, 1.8), 'DarkSteel', .01)
    B('Board', (0, .015, 3.3), (6.2, .02, 1.6), background, 0)
    B('Band', (0, .003, 2.65), (6.2, .01, .3), band, 0)
    T('Title', title, (0, -.005, 3.55), .5, title_color)
    T('Subtitle', subtitle, (0, -.005, 3.05), .22, subtitle_color)
    return finish(piece, 'yardsign')


def junk():
    begin('JunkPile')
    B('Fridge', (-1.3, .2, .85), (.7, .65, 1.7), 'White', .03, rot=(0, 0, math.radians(8)))
    B('FridgeLine', (-1.33, -.14, 1.15), (.66, .02, .02), 'DarkSteel', 0, rot=(0, 0, math.radians(8)))
    B('Washer', (-.4, -.3, .42), (.6, .6, .85), 'White', .03)
    C('WasherDoor', (-.4, -.61, .5), .2, .02, 'Black', 16, rot=FACE)
    for i, (x, y, z) in enumerate(((.5, -.2, .25), (.95, .25, .25), (.7, .05, .75))):
        B('Crate', (x, y, z), (.5, .5, .5), 'Wood', .02, rot=(0, 0, math.radians(i * 17)))
    for x in (1.5, 1.6):
        C('Tire', (x, .6, .11 + (x - 1.5) * 2.2), .33, .21, 'Rubber', 14)
    B('Tv', (.6, -.55, .22), (.6, .45, .45), 'DarkSteel', .02)
    B('Screen', (.6, -.78, .23), (.48, .01, .34), 'Black', 0)
    B('SofaBase', (-.2, .9, .22), (1.8, .8, .44), 'Sofa', .05)
    B('SofaBack', (-.2, 1.25, .62), (1.8, .2, .5), 'Sofa', .05)
    for x in (-1.05, .65):
        B('SofaArm', (x, .9, .52), (.2, .8, .3), 'Sofa', .04)
    return finish('JunkPile', 'junk')


def gas_station():
    # Lote de 34 × 24 m con el origen en su centro; la calle queda en -Y.
    begin('Lugar_Gasolinera')
    B('Roof', (0, -1, 4.85), (20, 12, .5), 'Canopy', .02)
    for y in (-7.03, 5.03):
        B('Fascia', (0, y, 4.85), (20.1, .05, .52), 'Brand', 0)
    for x in (-10.03, 10.03):
        B('FasciaSide', (x, -1, 4.85), (.05, 12.1, .52), 'Brand', 0)
    T('Brand', 'PETRO VILLA', (0, -7.07, 4.85), .36, 'White')
    for x in (-5, 0, 5):
        for y in (-4, 2):
            B('Light', (x, y, 4.585), (1.2, .4, .03), 'Lamp', 0)
    for sx in (-1, 1):
        x = sx * 4
        B('Island', (x, -1, .1), (1.4, 8.0, .2), 'Concrete', .03)
        for y in (-5.15, 3.15):
            C('Bumper', (x, y, .5), .15, 1.0, 'Yellow', 10)
        for y in (-4.4, 2.4):
            B('Column', (x, y, 2.4), (.45, .45, 4.4), 'White', .01)
            B('ColumnBand', (x, y, .6), (.47, .47, .4), 'Brand', 0)
        for y in (-2.2, .2):
            B('Pump', (x, y, 1.15), (.55, .9, 1.9), 'White', .03)
            B('PumpTop', (x, y, 2.22), (.57, .92, .3), 'Brand', .01)
            for side in (-1, 1):
                B('Screen', (x + side * .28, y, 1.62), (.01, .4, .25), 'Digit', 0)
                B('Holster', (x + side * .29, y + .25, 1.2), (.04, .14, .3), 'Black', 0)
                C('Hose', (x + side * .36, y + .25, .95), .025, .7, 'Black', 6)
    # Tienda 24 h al fondo a la derecha, con vidriera hacia la playa.
    B('ShopBack', (9.5, 11.4, 1.9), (13, .2, 3.8), 'White', .01)
    for x in (3.1, 15.9):
        B('ShopSide', (x, 8.5, 1.9), (.2, 6.0, 3.8), 'White', .01)
    B('ShopGlass', (9.5, 5.6, 1.4), (12.6, .05, 2.6), 'Glass', 0)
    B('ShopLintel', (9.5, 5.6, 3.25), (13, .2, 1.1), 'White', 0)
    for x in (3.5, 6.0, 8.5, 11.0, 13.5, 15.5):
        B('Mullion', (x, 5.58, 1.4), (.08, .08, 2.6), 'DarkSteel', 0)
    B('ShopRoof', (9.5, 8.5, 3.95), (13.4, 6.4, .3), 'White', .01)
    B('ShopFascia', (9.5, 5.28, 3.55), (13.4, .05, .6), 'Brand', 0)
    T('ShopText', 'TIENDA 24 H', (9.5, 5.24, 3.55), .38, 'White')
    for i, x in enumerate((5.5, 9.5, 13.5)):
        B('Shelf', (x, 9.6, .85), (3.0, .5, 1.7), 'DarkSteel', .01)
        for row in range(3):
            B('Goods', (x, 9.33, .45 + row * .5), (2.8, .05, .3), ('Brand', 'Yellow', 'SignBlue')[(i + row) % 3], 0)
    B('Counter', (5.0, 7.0, .5), (2.5, .7, 1.0), 'Wood', .02)
    B('AirCon', (12, 9.5, 4.4), (1.2, .8, .6), 'Steel', .02)
    B('IceChest', (4.4, 4.9, .45), (1.4, .7, .9), 'White', .03)
    T('Ice', 'HIELO', (4.4, 4.53, .55), .2, 'SignBlue')
    B('GasCage', (15.0, 4.9, .65), (1.2, .6, 1.3), 'Steel', 0)
    for x in (14.65, 15.0, 15.35):
        C('Cylinder', (x, 4.9, .45), .15, .8, 'Red', 10)
    # Tótem de precios en la esquina de la calle.
    B('TotemBase', (-14.5, -10, .3), (1.6, .6, .6), 'Concrete', .02)
    B('Totem', (-14.5, -10, 3.4), (1.4, .4, 5.6), 'Navy', .02)
    B('TotemBrand', (-14.5, -10, 5.6), (1.42, .42, 1.1), 'Brand', .01)
    T('TotemName', 'PETRO\nVILLA', (-14.5, -10.22, 5.6), .26, 'White')
    B('PriceBoard', (-14.5, -10.205, 3.4), (1.2, .01, 2.6), 'Black', 0)
    for i, line in enumerate(('93    1.249', '95    1.299', 'DIESEL 1.099')):
        T('Price', line, (-14.5, -10.215, 4.2 - i * .75), .17, 'Digit')
    B('AirPost', (-14, 7, .65), (.4, .3, 1.3), 'SignBlue', .02)
    T('Air', 'AIRE', (-14, 6.84, 1.0), .1, 'White')
    B('BackHedge', (-9, 11.4, .45), (14, .8, .9), 'Hedge', .08)
    for x in (-15.5, 15.5):
        B('LightPole', (x, -2, 3.0), (.18, .18, 6.0), 'Steel', 0)
        B('LightHead', (x, -2.5, 6.0), (.3, 1.0, .15), 'DarkSteel', 0)
        B('LightGlow', (x, -2.6, 5.92), (.25, .6, .02), 'Lamp', 0)
    # Lugares de carga para autos: (x, y, giro respecto del frente) a cada lado de las islas.
    slots = [[-6.2, -1.0, 0], [-1.6, -1.0, 180], [1.6, -1.0, 0], [6.2, -1.0, 180]]
    return finish('Lugar_Gasolinera', 'gasstation', recenter=False, slots=slots)


def parking():
    # Lote de 30 × 26 m con el origen en su centro; los puestos (líneas del suelo) están en la mitad de atrás (+Y).
    begin('Lugar_Estacionamiento')
    for x in (12.0, 7.4, 2.8, -1.8, -6.4, -11.0):
        B('WheelStop', (x, 12.0, .07), (1.8, .25, .14), 'Concrete', .02)
        B('StopPaint', (x, 11.87, .1), (1.8, .01, .08), 'Yellow', 0)
    B('Booth', (-12, -9, 1.2), (2.4, 2.0, 2.4), 'White', .02)
    B('BoothGlass', (-12, -10.02, 1.5), (2.0, .04, 1.0), 'Glass', 0)
    B('BoothGlassSide', (-10.78, -9, 1.5), (.04, 1.6, 1.0), 'Glass', 0)
    B('BoothRoof', (-12, -9, 2.5), (2.9, 2.5, .15), 'Navy', .01)
    B('BoothSign', (-12, -9.4, 2.85), (2.2, .1, .5), 'SignBlue', .01)
    T('BoothText', 'PARKING', (-12, -9.47, 2.85), .3, 'White')
    for housing, arm0, arm1 in ((-9.3, -9.1, -5.3), (9.3, 9.1, 5.3)):
        B('Barrier', (housing, -10, .5), (.35, .35, 1.0), 'Yellow', .02)
        for i in range(5):
            x0 = arm0 + (arm1 - arm0) * i / 5
            B('Arm', (x0 + (arm1 - arm0) / 10, -10, .95), (abs(arm1 - arm0) / 5, .08, .08), 'Red' if i % 2 == 0 else 'White', 0)
    C('PPole', (14, -12, 1.6), .05, 3.2, 'Steel', 8)
    B('PSign', (14, -12.06, 3.2), (1.0, .06, 1.0), 'SignBlue', .01)
    T('PText', 'P', (14, -12.1, 3.2), .8, 'White')
    B('PName', (14, -12.06, 2.45), (1.3, .06, .35), 'White', 0)
    T('PNameText', 'ESTACIONAMIENTO', (14, -12.1, 2.45), .1, 'Navy')
    B('PayMachine', (-12, -6.5, .8), (.7, .5, 1.6), 'Navy', .02)
    B('PayScreen', (-12, -6.76, 1.2), (.4, .01, .3), 'Digit', 0)
    B('BackWall', (0, 12.85, .3), (30, .3, .6), 'Concrete', .01)
    B('BackHedge', (0, 12.85, .9), (29.6, .5, .6), 'Hedge', .06)
    for x in (-14.85, 14.85):
        B('SideWall', (x, 3.5, .3), (.3, 19, .6), 'Concrete', .01)
        B('SideHedge', (x, 3.5, .9), (.5, 18.6, .6), 'HedgeDark', .06)
    for x in (-7, 7):
        B('LightPole', (x, 0, 3.5), (.18, .18, 7.0), 'Steel', 0)
        for side in (-1, 1):
            B('LightHead', (x + side * .6, 0, 7.0), (1.0, .3, .15), 'DarkSteel', 0)
            B('LightGlow', (x + side * .7, 0, 6.92), (.6, .25, .02), 'Lamp', 0)
    return finish('Lugar_Estacionamiento', 'parking', recenter=False)


bpy.ops.wm.read_factory_settings(use_empty=True)
for style in ('Picket', 'Bars', 'Hedge'):
    for width in HOUSE_WIDTHS:
        yard(style, width)
chain_fence()
container('Container_A', 'ContainerRed')
container('Container_B', 'ContainerBlue')
container('Container_C', 'ContainerGreen')
pallets()
barrels()
forklift()
tires()
sidewalk_sign()
yard_sign('Sign_DonTrueque', 'Yellow', 'Navy', 'DON TRUEQUE', 'COMPRA Y VENTA  -  PAGO AL CONTADO', 'Navy', 'Navy')
yard_sign('Sign_TallerPintura', 'White', 'Red', 'TALLER DE PINTURA', 'CAMBIO DE COLOR EN EL DIA', 'Red', 'Navy')
yard_sign('Sign_GarajeExpress', 'Navy', 'Orange', 'GARAJE EXPRESS', 'MECANICA RAPIDA', 'Orange', 'White')
junk()
gas_station()
parking()
kit.write(KIT_DIR / 'district_kit.json', KIT_DIR / 'district_materials.json', 'build_district_kit.py')

# --- revisión: una cuadra de muestra con casas reales del kit y sus antejardines, un galpón con patio,
# la gasolinera y el estacionamiento ---
slab, shoot, load = review_stage(kit)
slab('Pasto', -70, -20, 130, 70, -.01, 'Pasto')
slab('Calzada', -70, -20, 130, -9.5, .045, 'Asfalto')
slab('Vereda', -70, -9.5, 130, -6, .14, 'Acera')
buildings = a.ART / 'City' / 'Kit25' / 'Buildings'


def place(name, x, y, z=0.0, yaw=0.0):
    o = bpy.data.objects[name]
    o.location, o.rotation_euler = (x, y, z), (0, 0, math.radians(yaw))
    return o


# Casas a 4 m de la vereda con su cerca a 0,35 m del borde.
for i, (house, yard_id) in enumerate((('House_0', 'Yard_Picket_12'), ('House_1', 'Yard_Bars_13'), ('House_2', 'Yard_Hedge_14'))):
    x = -60 + i * 17
    h = load(buildings / f'{house}.fbx', house + '_Rev')
    h.location = (x, -6 + 4 + 8.05, 0)
    place(yard_id, x, -6 + .35)
w = load(buildings / 'Warehouse_0.fbx', 'Warehouse_Rev')
w.location = (25, -6 + 6 + 18.52, 0)
place('Yard_Chain_32', 25, -6 + .35)
place('Forklift', 28.8, 1.6, 0, 15)
place('PalletStack', 15.5, 3.5)
place('Barrels', 37.5, 3.0)
place('Container_A', 44.5, 12, 0, 90)
place('Container_B', 44.5, 20, 0, 90)
place('Sign_DonTrueque', 36.0, -4.2)
place('JunkPile', 12.5, 1.8)
place('TireStack', 31.0, 3.4)
place('Lugar_Gasolinera', 75, -6 + 12, .11)
place('Lugar_Estacionamiento', 112, -6 + 13, .11)
slab('LoteGas', 58, -6, 92, 18, .1, 'Lote')
slab('LoteParking', 97, -6, 127, 20, .1, 'Lote')
car = load(a.ART / 'Vehicles' / 'Car_Sedan.fbx', 'Car_Rev')
car.location, car.rotation_euler = (75 - 6.2, -6 + 12 - 1.0, .11), (0, 0, 0)
place('SidewalkSign', -8, -6.6, .14)
place('Container_C', -3, 60, 0, 0)
place('Sign_TallerPintura', 60, 40)
place('Sign_GarajeExpress', 70, 40)
renders = HERE / 'renders'
renders.mkdir(exist_ok=True)
for label, eye, target, lens in (('casas', (-48, -30, 10), (-40, 4, 2), 24), ('pizarra', (-10, -11, 1.6), (-8, -6.6, .6), 30),
                                 ('galpon', (25, -32, 12), (27, 6, 3), 24), ('gasolinera', (60, -30, 14), (76, 4, 2), 24),
                                 ('estacionamiento', (100, -26, 14), (112, 6, 1), 26), ('patio', (22, -10, 3), (32, 6, 1.5), 26),
                                 ('jardin', (-56, -11, 2.2), (-58, -3, .6), 30)):
    shoot(renders / f'district_kit_{label}.png', eye, target, lens)
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / 'BlenderSources~' / 'Alarma_DistrictKit.blend'))
