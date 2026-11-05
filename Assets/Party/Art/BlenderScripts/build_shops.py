"""Locales con interior para la ciudad de 2 × 2 km: minimarket, supermercado, joyería, banco, comida y ropa.

Cada local se arma con el mismo estilo del kit: fachada con vidriera y puerta de dos hojas (piezas separadas para abrirlas),
letrero, toldo, techo con luces e interior lleno con los props propios de Art/Props (estanterías con productos,
refrigeradores, caja, máquina expendedora, cajero automático, cámaras).
También escribe shop_layouts.json con los puntos que usa Unity, ya en coordenadas locales de Unity del modelo
(frente +Z, derecha +X): suelo caminable, obstáculos, recorridos de entrada y salida, puestos para mirar productos,
productos, fila, mostrador, caja y cajero.
Uso: blender -b --factory-startup -P build_shops.py
Salida: Art/City/Shops/Local_<tipo>.fbx, Art/City/Shops/shop_layouts.json y Previews~/local_<tipo>_*.png.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import alarmart as a  # noqa: E402

OUT = a.ART / "City" / "Shops"
LIBRARY = {}


def material(name, hex_color, emission=0.0, alpha=1.0):
    m = bpy.data.materials.get("Alarma_" + name)
    if m:
        return m
    m = bpy.data.materials.new("Alarma_" + name)
    color = tuple(a.linear(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4))
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = .7
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    if alpha < 1:
        bsdf.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    REGISTRY["Alarma_" + name] = (hex_color, emission, alpha)
    return m


REGISTRY = {}


def use(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def library(name):
    # Cada prop se importa una vez y se une en una sola malla; las copias comparten esa malla.
    if name in LIBRARY:
        return LIBRARY[name]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(a.ART / "Props" / f"Prop_{name}.fbx"))
    new = [o for o in set(bpy.data.objects) - before]
    names = [o.name for o in new]  # al unir, Blender borra las piezas: se guardan los nombres antes
    meshes = [o for o in new if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for n in names:
        o = bpy.data.objects.get(n)
        if o is not None and o != joined:
            bpy.data.objects.remove(o, do_unlink=True)
    for slot in joined.material_slots:
        base = slot.material.name.split(".")[0] if slot.material else None
        if base and base != slot.material.name and bpy.data.materials.get(base):
            slot.material = bpy.data.materials[base]
        elif base and base != slot.material.name:
            slot.material.name = base
    for c in list(joined.users_collection):
        c.objects.unlink(joined)
    joined.name = "LIB_" + name
    LIBRARY[name] = joined
    return joined


def prop(name, x, y, yaw=0.0, z=0.0, label=None):
    source = library(name)
    obj = source.copy()
    obj.name = label or ("Prop_" + name)
    a.COLLECTION.objects.link(obj)
    obj.parent = a.ROOT
    obj.location = (x, y, z)
    obj.rotation_euler = (0, 0, math.radians(yaw))
    return obj


def unity(x, y):
    # Blender (frente -Y) → Unity local (frente +Z): x se invierte y y pasa a ser -z.
    return [round(-x, 3), round(-y, 3)]


def shell(W, D, H, wall, floor_mat, wall_mat, trim, glass, door_w=2.2, door_h=2.5):
    f, b = -D / 2, D / 2
    use(a.box("Floor", (0, 0, .05), (W, D, .1), "Navy", 0), floor_mat)
    use(a.box("Roof", (0, 0, H + .1), (W + .3, D + .3, .2), "Navy", .02), wall_mat)
    use(a.box("Ceiling", (0, 0, H - .02), (W - 2 * wall, D - 2 * wall, .04), "Navy", 0), material("ShopCeiling", "EEF0EC"))
    use(a.box("Parapet", (0, f - .05, H + .45), (W + .3, .2, .5), "Navy", .02), trim)
    use(a.box("WallBack", (0, b - wall / 2, H / 2), (W, wall, H), "Navy", 0), wall_mat)
    for sx in (1, -1):
        use(a.box("WallSide", (sx * (W / 2 - wall / 2), 0, H / 2), (wall, D, H), "Navy", 0), wall_mat)
    # Fachada: pilares, vidrieras a cada lado de la puerta y dintel.
    pane = (W - door_w) / 2 - 1.0
    for sx in (1, -1):
        use(a.box("Pillar", (sx * (W / 2 - .3), f + wall / 2, H / 2), (.6, wall, H), "Navy", .01), trim)
        use(a.box("PillarDoor", (sx * (door_w / 2 + .2), f + wall / 2, H / 2), (.4, wall, H), "Navy", .01), trim)
        center = sx * (door_w / 2 + .4 + pane / 2)
        use(a.box("Storefront", (center, f + wall / 2, 1.55), (pane, .04, 2.6), "Navy", 0), glass)
        use(a.box("StoreBase", (center, f + wall / 2, .12), (pane, wall, .24), "Navy", 0), trim)
        use(a.box("StoreTop", (center, f + wall / 2, (2.85 + H) / 2), (pane, wall, H - 2.85), "Navy", 0), wall_mat)
    use(a.box("DoorHeader", (0, f + wall / 2, (door_h + H) / 2), (door_w, wall, H - door_h), "Navy", 0), wall_mat)
    # Puerta de dos hojas con el origen en la bisagra: Unity las gira para abrir.
    leaves = []
    for side, sx in (("L", 1), ("R", -1)):
        hinge = a.empty("DoorLeaf_" + side, (sx * door_w / 2, f + wall / 2, .1))
        use(a.box("DoorGlass_" + side, (-sx * door_w / 4, 0, door_h / 2 - .05), (door_w / 2 - .08, .03, door_h - .2), "Navy", 0, parent=hinge), glass)
        use(a.box("DoorFrame_" + side, (-sx * door_w / 4, 0, door_h - .12), (door_w / 2, .06, .08), "Navy", .005, parent=hinge), trim)
        use(a.box("DoorFrameLow_" + side, (-sx * door_w / 4, 0, .06), (door_w / 2, .06, .12), "Navy", .005, parent=hinge), trim)
        use(a.box("DoorBar_" + side, (-sx * (door_w / 2 - .15), -.05, 1.05), (.04, .04, .5), "Navy", .005, parent=hinge), material("Chrome", "C9D2D6"))
        leaves.append(hinge)
    return leaves


def lights(W, D, H, rows, cols):
    lamp = material("ShopLight", "FFFBEA", 2.5)
    for i in range(cols):
        for j in range(rows):
            x = -W / 2 + W * (i + .5) / cols
            y = -D / 2 + D * (j + .5) / rows
            use(a.box("CeilingLight", (x, y, H - .06), (1.2, .3, .04), "Navy", 0), lamp)


W, D, H, WALL = 19.8, 22.2, 4.4, .25  # misma huella que las tiendas del kit: el local cabe donde estaba el edificio
F, B = -D / 2, D / 2


class Layout:
    """Puntos de la rutina de compra, ya en coordenadas locales de Unity."""

    def __init__(self):
        self.obstacles, self.stations, self.products, self.staff = [], [], [], []

    def post(self, role, pose, x, y, yaw, top, bottom, seat=0.0):
        # Puesto de un empleado. yaw 0 mira hacia la calle (-Y en Blender, +Z en Unity); en Unity el giro se invierte.
        ux, uz = unity(x, y)
        self.staff.append(dict(role=role, pose=pose, x=ux, z=uz, yaw=round(-yaw, 1), seat=seat, top=top, bottom=bottom,
                               blender=[x, y, yaw]))

    def block(self, x0, y0, x1, y1):
        a0, a1 = unity(x0, y0), unity(x1, y1)
        self.obstacles.append([min(a0[0], a1[0]), min(a0[1], a1[1]), max(a0[0], a1[0]), max(a0[1], a1[1])])

    def station(self, x, y, px, py, height):
        # Dónde se para el cliente a mirar y dónde está el producto que toma.
        self.stations.append(unity(x, y))
        self.products.append(unity(px, py) + [height])


def counter(lay, prop_name, yaw=90):
    # Caja junto a la entrada (a la izquierda al entrar): mostrador, cajero detrás y fila hacia el interior.
    prop(prop_name, -5.0, F + 3.2, yaw, label="Prop_Counter")
    lay.block(-6.0, F + 2.2, -4.0, F + 4.2)
    return dict(counter=unity(-3.6, F + 3.2), scan=unity(-5.0, F + 3.2) + [1.05], cashier=unity(-6.4, F + 3.2),
                receipt=unity(-4.7, F + 3.6) + [1.1], till=unity(-5.3, F + 3.0) + [1.0], queue=[unity(-3.6, F + 3.2 + k * .95) for k in range(1, 5)])


def shelves(lay, xs, rows, product_height=1.1):
    for x in xs:
        for k in range(rows):
            y = -3.6 + k * 1.82
            prop("RetailShelf", x - .3, y, 90)
            prop("RetailShelf", x + .3, y, -90)
        lay.block(x - .65, -4.6, x + .65, -3.6 + (rows - 1) * 1.82 + 1.0)
        for k in range(0, rows, 2):
            y = -3.6 + k * 1.82
            for side in (-1, 1):
                lay.station(x + side * 1.3, y, x + side * .45, y, product_height)


def fridges(lay, count, stations):
    for k in range(count):
        prop("Refrigerator", -W / 2 + 1.3 + k * 1.0, B - .7, 180)
    lay.block(-W / 2 + .5, B - 1.3, -W / 2 + 1.3 + count * 1.0, B - .2)
    for x in stations:
        lay.station(x, B - 2.0, x, B - .9, 1.2)


def cameras():
    for x, y, yaw in ((-W / 2 + .5, B - .5, 135), (W / 2 - .5, F + .5, -45), (W / 2 - .5, B - .5, -135)):
        prop("SecurityCamera", x, y, yaw, H - .45)


def showcase(name, x, y, length, depth, along_y, base, glass, trim, light, jewels):
    # Vitrina de joyería: zócalo oscuro, cristal encima con tira de luz y joyas a la vista.
    size = (depth, length, 1.0) if along_y else (length, depth, 1.0)
    use(a.box(name, (x, y, .5), size, "Navy", .02), base)
    use(a.box(name + "Trim", (x, y, 1.0), (size[0] + .04, size[1] + .04, .04), "Navy", .005), trim)
    use(a.box(name + "Glass", (x, y, 1.18), (size[0] - .04, size[1] - .04, .32), "Navy", 0), glass)
    # Tira de luz en el borde del lado del vendedor, no una losa que tape las joyas.
    strip = (.06, size[1] - .1) if along_y else (size[0] - .1, .06)
    back = (x + (.22 if x > 0 else -.22), y) if along_y else (x, y + .26)
    use(a.box(name + "Light", (*back, 1.33), (*strip, .02), "Navy", 0), light)
    for k in range(jewels):
        t = (k + .5) / jewels - .5
        prop("JewelrySet", x + (0 if along_y else t * length), y + (t * length if along_y else 0), 0, 1.02)


def checkout_lane(lay, x, number, belt, steel, accent, light):
    # Caja con cinta: el cajero queda a la izquierda (mirando +X) y el cliente pasa por la derecha hacia la salida.
    y = F + 3.2
    use(a.box("LaneCounter", (x, y, .45), (.75, 2.2, .9), "Navy", .02), steel)
    use(a.box("LaneBelt", (x, y + .35, .91), (.55, 1.4, .02), "Navy", 0), belt)
    use(a.box("LaneScanner", (x, y - .45, .93), (.45, .35, .04), "Navy", .005), material("Vidrio_Escaner", "6FB7C9", .6))
    use(a.box("LaneRegister", (x - .25, y - .75, 1.1), (.3, .3, .3), "Navy", .01), material("Grafito_Super", "2B2F36"))
    use(a.box("LaneBagging", (x, y - 1.45, .4), (.75, .7, .8), "Navy", .02), steel)
    a.beam("LanePole", (x - .3, y - .9, .9), (x - .3, y - .9, 2.4), .03, "Metal")
    use(a.box("LaneNumber", (x - .3, y - .9, 2.55), (.45, .06, .35), "Navy", .01), accent)
    for side in (-.035, .035):
        a.text("LaneNumberText", str(number), (x - .3, y - .9 + side, 2.55), .24, "Ivory", rotation=(math.pi / 2, 0, 0 if side < 0 else math.pi))
    use(a.cyl("LaneLight", (x - .3, y - .9, 2.76), .07, .06, "Navy", 12), light)
    lay.block(x - 1.1, F + 1.7, x + .4, F + 4.4)


def furnish_supermercado(lay):
    # Según las referencias: verdulería al entrar, circuito alrededor de los pasillos, lácteos y frescos al fondo,
    # bebidas frías a la derecha, carnicería y panadería con personal, ofertas en los extremos y cajas junto a la salida.
    orange, steel = material("Accent_supermercado", "E8742A"), material("Acero_Super", "B9C0C4")
    belt, wood = material("Cinta_Super", "23262B"), material("Madera_Super", "9A6B43")
    glass, light = material("VidrioVitrina", "CFE4EA", 0, .25), material("LuzVitrina", "FFF4D6", 2.4)
    top, bottom = material("Uniforme_Super_Polo", "E8742A").name, material("Uniforme_Super_Pantalon", "2B2F36").name
    white = material("Uniforme_Super_Delantal", "F4F1E8").name
    fruit = [material("Fruta_" + n, h) for n, h in (("Naranja", "F28C28"), ("Manzana", "D64545"), ("Lima", "7CB342"), ("Platano", "F2D04A"))]

    # Cajas: tres líneas frente a la salida, visibles desde todo el local.
    for number, x in enumerate((-3.4, -5.8, -8.2), 1):
        checkout_lane(lay, x, number, belt, steel, orange, light)
        lay.post("caja" if number == 1 else "cajero", "stand", x - .8, F + 3.2, 90, top, bottom)
    use(a.box("ExitRail", (-1.6, F + 1.6, .5), (.04, 1.6, 1.0), "Navy", 0), steel)
    lay.block(-1.7, F + .8, -1.5, F + 2.4)

    # Verdulería a la entrada: dos islas de mesas inclinadas con cajones de fruta y verdura, y una balanza.
    for x in (3.6, 6.6):
        use(a.box("ProduceTable", (x, F + 4.8, .35), (1.4, 3.2, .7), "Navy", .02), wood)
        for k in range(4):
            cy = F + 3.6 + k * .8
            for sx in (-1, 1):
                crate = use(a.box("ProduceCrate", (x + sx * .35, cy, .82), (.62, .74, .18), "Navy", .01), wood)
                crate.rotation_euler = (0, math.radians(-12 * sx), 0)
                for n in range(6):
                    use(a.sphere("Fruit", (x + sx * (.2 + (n % 3) * .14), cy - .2 + (n // 3) * .3, .97 - (n % 3) * .02),
                                 (.08, .08, .08), "Navy", 1), fruit[(k + n + (sx > 0)) % 4])
        lay.block(x - .75, F + 3.1, x + .75, F + 6.5)
        lay.station(x - 1.4, F + 4.4, x - .5, F + 4.4, .9)
        lay.station(x + 1.4, F + 6.0, x + .5, F + 6.0, .9)
    use(a.box("ScaleStand", (8.9, F + 5.0, .5), (.4, .5, 1.0), "Navy", .01), steel)
    use(a.box("Scale", (8.9, F + 5.0, 1.03), (.3, .35, .06), "Navy", .005), material("Grafito_Super", "2B2F36"))
    lay.block(8.6, F + 4.7, W / 2, F + 5.3)
    # Carros y canastos junto a la puerta.
    for k in range(3):
        cart = F + .7 + k * .28
        use(a.box("CartBasket", (2.9, cart, .62), (.55, .8, .42), "Navy", .01), steel)
        a.beam("CartHandle", (2.6, cart - .42, .95), (3.2, cart - .42, .95), .02, "Rubber")
        for wx in (2.7, 3.1):
            use(a.cyl("CartWheel", (wx, cart + .3, .08), .07, .04, "Navy", 8, rotation=(0, math.pi / 2, 0)), belt)
    for k in range(4):
        prop("ShoppingBasket", 4.0, F + .8 + k * .3, 0)
    lay.block(2.3, F + .3, 4.4, F + 2.0)

    # Pasillos centrales con ofertas en la punta trasera y un reponedor con su carro de cajas.
    shelves(lay, (-6.4, -3.0, .4, 3.8), 5)
    for x in (-6.4, -3.0, .4, 3.8):
        use(a.box("EndCap", (x, 5.6, .35), (1.3, .9, .7), "Navy", .02), orange)
        for row in range(3):
            for n in range(4 - row):
                prop("ProductCan", x - .45 + n * .3 + row * .15, 5.6, 0, .7 + row * .16)
        use(a.box("EndCapSign", (x, 5.13, 1.2), (.9, .03, .3), "Navy", .005), material("Folleto", "F4F1E8"))
        a.text("EndCapText", "OFERTA", (x, 5.1, 1.2), .14, "Navy").data.materials[0] = orange
        lay.block(x - .7, 5.1, x + .7, 6.1)
    use(a.box("RestockCart", (2.4, 2.9, .45), (.6, .9, .9), "Navy", .01), steel)
    for z in (.95, 1.2):
        prop("ProductBox", 2.4, 2.9, 0, z)
    lay.block(2.05, 2.4, 2.75, 3.4)
    lay.post("reponedor", "stand", 2.4, 1.9, 90, top, bottom)
    lay.block(2.15, 1.65, 2.65, 2.15)
    # Pared izquierda con estanterías de limpieza.
    for k in range(5):
        prop("RetailShelf", -W / 2 + .7, -3.6 + k * 1.82, 90)
    lay.block(-W / 2, -4.6, -W / 2 + 1.3, 4.7)
    lay.station(-W / 2 + 2.0, -1.8, -W / 2 + .7, -1.8, 1.1)

    # Fondo: lácteos refrigerados a la izquierda y mostrador de carnicería y panadería a la derecha.
    fridges(lay, 9, (-7.0, -4.0, -1.4))
    showcase("DeliCase", 5.2, B - 2.4, 7.0, .8, False, steel, glass, orange, light, 0)
    meat = (material("Carne_Roja", "B8483E"), material("Carne_Rosada", "E39A8C"), material("Pan_Dorado", "D9A35B"))
    for k in range(10):
        use(a.box("DeliItem", (2.2 + k * .65, B - 2.4, 1.07), (.38, .3, .1), "Navy", .02), meat[k % 3])
    for k in range(4):
        use(a.box("BreadShelf", (3.0 + k * 1.6, B - .55, 1.3), (1.4, .45, 2.0), "Navy", .01), wood)
        for z in (.75, 1.35, 1.95):
            for n in range(3):
                use(a.sphere("Bread", (2.6 + k * 1.6 + n * .4, B - .82, z), (.16, .1, .08), "Navy", 1), meat[2])
    use(a.box("DeliSign", (5.2, B - WALL - .03, 3.2), (4.4, .04, .55), "Navy", .01), orange)
    a.text("DeliSignText", "CARNICERÍA · PANADERÍA", (5.2, B - WALL - .06, 3.2), .22, "Ivory")
    lay.block(1.5, B - 2.9, W / 2, B)
    lay.post("carnicero", "stand", 3.4, B - 1.5, 0, white, bottom)
    lay.post("panadera", "stand", 7.0, B - 1.5, 0, white, bottom)
    for x in (3.4, 7.0):
        lay.station(x, B - 3.6, x, B - 2.4, 1.1)

    # Pared derecha: bebidas frías.
    for k in range(7):
        prop("Refrigerator", W / 2 - .7, -2.6 + k * 1.0, -90)
    lay.block(W / 2 - 1.3, -3.2, W / 2, 4.2)
    for y in (-2.0, .5, 3.0):
        lay.station(W / 2 - 2.0, y, W / 2 - .9, y, 1.2)
    prop("ATM", W / 2 - 1.0, F + 2.4, -90)
    lay.block(W / 2 - 1.6, F + 1.8, W / 2, F + 3.0)
    cameras()
    till = dict(counter=unity(-2.6, F + 3.2), scan=unity(-3.4, F + 2.75) + [.98], cashier=unity(-4.2, F + 3.2),
                receipt=unity(-3.6, F + 2.45) + [1.0], till=unity(-3.65, F + 2.45) + [1.2],
                queue=[unity(-2.6, F + 4.15 + k * .9) for k in range(3)])
    return till, dict(LIMPIEZA=(-6.4, .5), ABARROTES=(-3.0, .5), SNACKS=(.4, .5), CONSERVAS=(3.8, .5),
                      LACTEOS=(-4.0, B - 2.4), BEBIDAS=(W / 2 - 2.2, .5), VERDULERIA=(5.1, F + 4.8))


def furnish_joyeria(lay):
    # Circuito según las referencias: vitrinas perimetrales con el vendedor detrás, dos islas para rodear,
    # mostrador de atención con taburetes al fondo, luz general + de acento + de vitrina y zona de personal.
    gold, plum = material("Oro", "C9A227"), material("Accent_joyeria", "7B4FA3")
    base, wood = material("Grafito_Joyeria", "1E1B24"), material("Nogal_Joyeria", "4A3226")
    glass = material("VidrioVitrina", "CFE4EA", 0, .25)
    light = material("LuzVitrina", "FFF4D6", 2.4)
    velvet, mirror = material("Terciopelo_Joyeria", "5A2D6E"), material("Espejo", "D7E3EA")
    top, bottom = material("Uniforme_Joyeria_Saco", "2E2338").name, material("Uniforme_Joyeria_Pantalon", "17161B").name

    # Fondo: mostrador de atención con vitrina, taburetes para clientes y caja a la derecha; detrás, nichos iluminados.
    cb = B - 3.2
    showcase("ServiceCase", 0, cb, 10.0, .75, False, base, glass, gold, light, 6)
    for x in (-3.8, -2.2, -.6):
        use(a.cyl("StoolPole", (x, cb - .85, .35), .04, .7, "Metal", 8), gold)
        use(a.cyl("StoolSeat", (x, cb - .85, .72), .2, .07, "Navy", 16), velvet)
        lay.block(x - .22, cb - 1.07, x + .22, cb - .63)
    for k, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
        # Nicho abierto: fondo de terciopelo enmarcado por tablas de nogal.
        use(a.box("NicheBack", (x, B - WALL - .03, 1.9), (2.4, .03, 1.6), "Navy", 0), velvet)
        for dz in (-.79, .79):
            use(a.box("NicheBoard", (x, B - WALL - .2, 1.9 + dz), (2.4, .35, .04), "Navy", .005), wood)
        for dx in (-1.18, 1.18):
            use(a.box("NicheSide", (x + dx, B - WALL - .2, 1.9), (.04, .35, 1.6), "Navy", .005), wood)
        use(a.box("NicheLight", (x, B - WALL - .2, 2.68), (2.2, .3, .03), "Navy", 0), light)
        for z in (1.45, 2.05):
            use(a.box("NicheShelf", (x, B - WALL - .2, z), (2.2, .32, .03), "Navy", 0), glass)
        prop("JewelrySet", x, B - WALL - .2, 0, 1.47 if k % 2 else 2.07)
    use(a.box("LogoPanel", (0, B - WALL - .03, 3.55), (5.4, .04, .75), "Navy", .01), base)
    a.text("LogoText", "JOYERÍA AURA", (0, B - WALL - .06, 3.55), .34, "Navy").data.materials[0] = gold
    # Puerta de personal hacia la trastienda con las cajas fuertes y su panel de alarma.
    use(a.box("StaffDoor", (8.4, B - WALL - .03, 1.05), (1.0, .04, 2.1), "Navy", .01), wood)
    use(a.box("StaffSign", (8.4, B - WALL - .05, 2.35), (1.3, .03, .22), "Navy", .005), base)
    a.text("StaffSignText", "SOLO PERSONAL", (8.4, B - WALL - .07, 2.35), .11, "Ivory")
    prop("SecurityPanel", 7.5, B - WALL - .05, 180, 1.4)
    for x in (-8.6, -7.4):
        prop("Safe", x, B - .8, 180)
    lay.block(-W / 2, cb - .45, W / 2, B)
    lay.post("caja", "stand", 3.0, cb + .8, 0, top, bottom)
    lay.post("asesora", "stand", -2.2, cb + .8, 0, top, bottom)
    for x in (-3.0, -1.4):
        lay.station(x, cb - 1.0, x, cb, 1.05)

    # Lados: vitrinas separadas de la pared; el vendedor atiende desde el pasillo con espejos y estantes de luz detrás.
    for sx in (1, -1):
        for y in (-4.6, -1.2, 2.2):
            showcase("SideCase", sx * 8.25, y, 3.1, .6, True, base, glass, gold, light, 3)
            lay.station(sx * 7.25, y, sx * 8.25, y, 1.05)
        for y in (-4.6, 2.2):
            use(a.box("WallMirror", (sx * (W / 2 - WALL - .03), y, 1.8), (.03, 1.6, 1.8), "Navy", 0), mirror)
            use(a.box("WallMirrorFrame", (sx * (W / 2 - WALL - .02), y, 1.8), (.02, 1.75, 1.95), "Navy", 0), gold)
        use(a.box("WallLight", (sx * (W / 2 - WALL - .05), -1.2, 2.75), (.04, 9.6, .05), "Navy", 0), light)
        use(a.box("WallPanel", (sx * (W / 2 - WALL - .02), 0, .55), (.03, D - 2 * WALL, 1.1), "Navy", 0), wood)
        lay.block(sx * 7.9, -6.3, sx * W / 2, cb - .45)
        lay.post("vendedor", "stand", sx * 9.15, -1.2, -90 * sx, top, bottom)

    # Centro: dos islas hexagonales para rodear, con joyas bajo cúpula de cristal y lámpara de araña dorada.
    for sx in (1, -1):
        x, y = sx * 3.2, -1.0
        use(a.cyl("Island", (x, y, .5), .9, 1.0, "Navy", 6), base)
        use(a.cyl("IslandTrim", (x, y, 1.01), .93, .04, "Navy", 6), gold)
        use(a.cyl("IslandGlass", (x, y, 1.2), .85, .34, "Navy", 6), glass)
        for k in range(3):
            angle = k * 2 * math.pi / 3
            prop("JewelrySet", x + .45 * math.cos(angle), y + .45 * math.sin(angle), math.degrees(angle), 1.03)
        lay.block(x - .95, y - .95, x + .95, y + .95)
        lay.station(x, y - 1.5, x, y - .4, 1.05)
        lay.station(x, y + 1.5, x, y + .4, 1.05)
    for r, z in ((.9, 3.55), (.6, 3.35)):
        use(a.torus("Chandelier", (0, -1.0, z), r, .035, "Navy"), gold)
    for k in range(8):
        angle = k * math.pi / 4
        use(a.sphere("ChandelierBulb", (.9 * math.cos(angle), -1.0 + .9 * math.sin(angle), 3.45), (.07, .07, .09), "Navy", 1), light)
    a.beam("ChandelierRod", (0, -1.0, 3.55), (0, -1.0, H - .05), .015, "Navy")
    # Focos de acento sobre cada vitrina lateral.
    for sx in (1, -1):
        for y in (-4.6, -1.2, 2.2):
            use(a.cyl("Spot", (sx * 8.0, y, H - .12), .09, .14, "Navy", 12), gold)

    # Entrada: escaparates con bustos y anillos, rincón de espera con sillones y alfombra de terciopelo.
    for sx in (1, -1):
        for k, x in enumerate((3.4, 5.6, 7.8)):
            px = sx * x
            use(a.cyl("Pedestal", (px, F + .8, .45 + .15 * (k % 2)), .32, .9 + .3 * (k % 2), "Navy", 16), base)
            if k == 1:
                use(a.box("Bust", (px, F + .8, 1.38), (.26, .14, .42), "Navy", .03), velvet)
                use(a.torus("Necklace", (px, F + .72, 1.45), .1, .012, "Navy", rotation=(math.radians(70), 0, 0)), gold)
            else:
                prop("JewelrySet", px, F + .8, 0, .92 + .3 * (k % 2))
            use(a.cyl("WindowSpot", (px, F + .8, H - .12), .08, .14, "Navy", 12), gold)
        lay.block(sx * 3.0, F + .3, sx * 8.2, F + 1.3)
    for dx in (-.75, .75):
        use(a.box("ArmchairSeat", (-6.8 + dx, F + 3.6, .3), (.8, .75, .4), "Navy", .06), velvet)
        use(a.box("ArmchairBack", (-6.8 + dx, F + 3.95, .7), (.8, .15, .6), "Navy", .06), velvet)
    use(a.cyl("SideTable", (-6.8, F + 3.0, .25), .3, .5, "Navy", 16), gold)
    lay.block(-7.8, F + 2.6, -5.8, F + 4.1)
    plant(-8.9, F + 1.5, .9)
    lay.block(-9.3, F + 1.1, -8.5, F + 1.9)
    use(a.box("Runner", (0, F + 6.6, .13), (2.0, 12.8, .01), "Navy", 0), material("Alfombra_Joyeria", "5A2D6E"))
    use(a.box("StandingMirror", (5.6, F + 3.4, 1.0), (.6, .04, 1.6), "Navy", 0), mirror)
    use(a.box("StandingMirrorFrame", (5.6, F + 3.42, 1.0), (.68, .03, 1.68), "Navy", 0), gold)
    lay.block(5.2, F + 3.2, 6.0, F + 3.6)
    for x in (-1.5, 1.5):
        prop("LaserEmitter", x, cb - 1.6, 0, H - .35)
    cameras()
    till = dict(counter=unity(3.0, cb - 1.0), scan=unity(3.0, cb - .2) + [1.05], cashier=unity(3.0, cb + .8),
                receipt=unity(3.3, cb - .3) + [1.06], till=unity(3.7, cb + .2) + [1.04],
                queue=[unity(3.0, cb - 1.95 - k * .95) for k in range(4)])
    return till, {}


def pane(name, x0, y0, x1, y1, z0, z1, glass, frame):
    # Tabique de vidrio con perfil metálico arriba y abajo, de un punto del piso a otro.
    length, yaw = math.hypot(x1 - x0, y1 - y0), math.atan2(y1 - y0, x1 - x0)
    center = ((x0 + x1) / 2, (y0 + y1) / 2)
    use(a.box(name, (*center, (z0 + z1) / 2), (length, .03, z1 - z0), "Navy", 0, rotation=(0, 0, yaw)), glass)
    for label, z, h in (("Top", z1, .05), ("Base", z0 + .04, .08)):
        use(a.box(name + label, (*center, z), (length, .06, h), "Navy", 0, rotation=(0, 0, yaw)), frame)


def plant(x, y, scale=1.0):
    use(a.cyl("Planter", (x, y, .3 * scale), .28 * scale, .6 * scale, "Navy", 12), material("Maceta", "3B3F45"))
    # Tres matas de dos tonos en lugar de una sola esfera: se lee como planta desde cualquier ángulo.
    for dx, dy, z, r, tone in ((0, 0, 1.05, .34, "4E8F55"), (.16, .1, .8, .26, "3F7A48"), (-.14, -.12, .85, .25, "5FA066")):
        use(a.sphere("Plant", (x + dx * scale, y + dy * scale, z * scale), (r * scale, r * scale, r * 1.2 * scale), "Navy", 2),
            material("Planta" if tone == "4E8F55" else "Planta_" + tone, tone))


def furnish_banco(lay):
    # Sucursal según las referencias: ventanillas al fondo tras vidrio de seguridad (lejos de la puerta), bóveda en la
    # zona de personal, recepción y turnos al entrar, cajeros automáticos aparte, asesores, gerencia y sala de espera.
    green, wood = material("Accent_banco", "1F6E4A"), material("Madera_Banco", "6B4A32")
    stone, steel = material("Marmol_Banco", "E8E4DC"), material("Acero_Banco", "8E979C")
    glass, dark = material("VidrioSeguridad", "A9D3DC", 0, .3), material("Grafito_Banco", "2B2F36")
    led, paper = material("LedTurno", "7CFFB2", 2.0), material("Folleto", "F4F1E8")
    top, bottom = material("Uniforme_Banco_Saco", "1F6E4A").name, material("Uniforme_Banco_Pantalon", "2B2F36").name
    boss = material("Uniforme_Banco_Gerente", "1F2A44").name
    rope, chrome = material("Cordon", "B3262E"), material("Chrome", "C9D2D6")

    # Zona de personal: mostrador continuo con cuatro ventanillas, vidrio de seguridad y bandeja para pasar billetes.
    cy = B - 4.7
    use(a.box("TellerCounter", (0, cy, .52), (14.4, .8, 1.04), "Navy", .02), wood)
    use(a.box("TellerTop", (0, cy - .05, 1.07), (14.6, .95, .06), "Navy", .01), stone)
    use(a.box("TellerStripe", (0, cy - .41, .55), (14.4, .02, .14), "Navy", 0), green)
    windows = (-5.4, -1.8, 1.8, 5.4)
    for i, x in enumerate(windows):
        use(a.box("TellerGlass", (x, cy - .2, 1.78), (3.4, .03, 1.3), "Navy", 0), glass)
        use(a.box("TellerSlot", (x, cy - .32, 1.12), (.55, .3, .03), "Navy", .005), steel)
        prop("OfficeMonitor", x + .8, cy + .2, 180, 1.1)
        prop("CashStack", x - .7, cy + .25, 0, 1.1)
        use(a.box("WindowPlate", (x, cy - .29, 2.66), (.55, .04, .36), "Navy", .01), green)
        a.text("WindowNumber", str(i + 1), (x, cy - .32, 2.66), .28, "Ivory")
        use(a.cyl("PendantLamp", (x, cy - .9, 3.5), .22, .18, "Navy", 16), material("ShopLight", "FFFBEA", 2.5))
        a.beam("PendantWire", (x, cy - .9, 3.6), (x, cy - .9, H - .05), .008, "Rubber")
    for x in (-7.2, -3.6, 0, 3.6, 7.2):
        use(a.box("TellerPost", (x, cy - .2, 1.8), (.08, .08, 1.4), "Navy", .005), steel)
        if abs(x) < 7:
            use(a.box("BoothDivider", (x, cy + .85, .8), (.08, 1.1, 1.6), "Navy", .01), wood)
    use(a.box("TellerHeader", (0, cy - .2, 2.66), (14.6, .1, .4), "Navy", .01), dark)
    use(a.box("TurnScreen", (0, cy - .3, 2.66), (1.9, .05, .34), "Navy", .005), material("PantallaTurno", "15201C"))
    a.text("TurnText", "TURNO A-07", (0, cy - .34, 2.66), .17, "Ivory").data.materials[0] = led
    # Cierres laterales con puerta de personal.
    for sx in (1, -1):
        use(a.box("StaffWall", (sx * 8.43, cy, 1.3), (2.45, .2, 2.6), "Navy", .01), material("ShopWall_banco", "EDEBE4"))
        use(a.box("StaffDoor", (sx * 8.43, cy - .11, 1.05), (.95, .04, 2.1), "Navy", .01), wood)
        use(a.box("StaffSign", (sx * 8.43, cy - .14, 2.3), (1.3, .03, .22), "Navy", .005), dark)
        a.text("StaffSignText", "SOLO PERSONAL", (sx * 8.43, cy - .16, 2.3), .11, "Ivory")
    # Fondo: bóveda, cajas fuertes, archivadores y el logo visible por encima del vidrio.
    prop("VaultDoor", 0, B - .35, 180)
    a.text("VaultText", "BÓVEDA", (0, B - WALL - .04, 3.05), .22, "Navy")
    for x in (-3.2, 3.2):
        prop("Safe", x, B - .8, 180)
    for sx in (1, -1):
        for k in range(3):
            use(a.box("FileCabinet", (sx * (5.6 + k * .62), B - .55, .68), (.55, .6, 1.36), "Navy", .01), steel)
    use(a.box("BankLogo", (0, B - WALL - .03, 3.88), (5.2, .04, .7), "Navy", .02), green)
    a.text("BankLogoText", "BANCO CENTRAL", (0, B - WALL - .06, 3.88), .34, "Ivory")
    lay.block(-W / 2, cy - .45, W / 2, B)
    lay.post("caja", "stand", -1.8, cy + .85, 0, top, bottom)
    for x in (-5.4, 1.8, 5.4):
        lay.post("cajero", "stand", x, cy + .85, 0, top, bottom)

    # Fila en zigzag simple: postes con cordón a ambos lados del pasillo que lleva a las ventanillas.
    for sx in (1, -1):
        posts = [(sx * .75, 1.0 + k * 1.23) for k in range(4)]
        for x, y in posts:
            use(a.cyl("Stanchion", (x, y, .5), .04, 1.0, "Metal", 8), chrome)
        for (x0, y0), (x1, y1) in zip(posts, posts[1:]):
            use(a.beam("Rope", (x0, y0, .9), (x1, y1, .9), .02, "Navy", 6), rope)
        lay.block(sx * .65, .9, sx * .85, 4.8)

    # Asesores: dos cubículos con divisiones de vidrio, empleado sentado de espaldas a la pared y dos sillas de cliente.
    for y, slogan, detail in ((-5.6, "AHORRO", "Tu meta, paso a paso"), (-1.6, "CRÉDITOS", "Tasa preferente")):
        prop("OfficeDesk", -7.9, y, 90)
        prop("OfficeMonitor", -7.75, y + .25, -90, .79)
        prop("Chair", -8.95, y, 90)
        for dy in (-.45, .45):
            prop("Chair", -6.75, y + dy, -90)
        use(a.box("CubicleRug", (-7.9, y, .125), (3.2, 2.6, .01), "Navy", 0), material("Alfombra_Banco", "2C5E4A"))
        use(a.box("Poster", (-W / 2 + WALL + .03, y, 2.0), (.03, 1.4, .9), "Navy", .005), green)
        use(a.box("PosterInner", (-W / 2 + WALL + .05, y, 2.0), (.02, 1.2, .7), "Navy", 0), material("Folleto", "F4F1E8"))
        facing = (math.pi / 2, 0, math.pi / 2)  # texto legible desde la sala (+X)
        a.text("PosterTitle", slogan, (-W / 2 + WALL + .07, y, 2.12), .2, "Navy", rotation=facing).data.materials[0] = green
        a.text("PosterDetail", detail, (-W / 2 + WALL + .07, y, 1.86), .09, "Navy", rotation=facing)
        lay.block(-W / 2, y - 1.0, -6.3, y + 1.0)
        lay.post("asesor", "seat", -8.95, y, 90, top, bottom, .47)
    for y in (-7.6, -3.6, .4):
        pane("CubicleGlass", -W / 2 + WALL, y, -6.2, y, 0, 1.5, glass, steel)

    # Gerencia: oficina con paredes de vidrio, escritorio, biblioteca y planta.
    pane("OfficeGlassFront", 5.6, -.6, 6.0, -.6, 0, 2.6, glass, steel)
    pane("OfficeGlassFront", 7.0, -.6, W / 2 - WALL, -.6, 0, 2.6, glass, steel)
    pane("OfficeGlassSide", 5.6, -.6, 5.6, cy - .45, 0, 2.6, glass, steel)
    use(a.box("OfficeHeader", (7.6, -.6, 2.45), (4.1, .05, .3), "Navy", 0), dark)
    a.text("OfficeText", "GERENCIA", (7.6, -.64, 2.45), .16, "Ivory")
    prop("OfficeDesk", 8.0, 2.2, -90)
    prop("OfficeMonitor", 7.85, 1.95, 90, .79)
    prop("Chair", 9.05, 2.2, -90)
    for dy in (-.45, .45):
        prop("Chair", 6.85, 2.2 + dy, 90)
    use(a.box("Bookcase", (W / 2 - WALL - .22, 4.2, 1.0), (.4, 1.8, 2.0), "Navy", .01), wood)
    for k, hex_color in enumerate(("2C5E4A", "B3262E", "D9C27A", "1F2A44")):
        use(a.box("Books", (W / 2 - WALL - .25, 3.55 + k * .42, 1.35), (.3, .32, .32), "Navy", .005), material("Libro_" + str(k), hex_color))
    plant(6.1, 4.2)
    lay.block(5.5, -.7, W / 2, cy - .45)
    lay.post("gerente", "seat", 9.05, 2.2, -90, boss, boss, .47)

    # Sala de espera frente a las ventanillas: dos grupos de sillas sobre alfombra, mirando la pantalla de turnos.
    for sx in (1, -1):
        for y in (-1.6, -3.0):
            for k in range(4):
                prop("Chair", sx * (3.0 + k * .6), y, 180)
        use(a.box("LoungeRug", (sx * 3.9, -2.3, .125), (3.2, 3.0, .01), "Navy", 0), material("Alfombra_Banco", "2C5E4A"))
        lay.block(sx * 2.6, -3.5, sx * 5.2, -1.1)
    use(a.box("Runner", (0, F + 5.8, .13), (1.6, 11.2, .01), "Navy", 0), material("Alfombra_Banco", "2C5E4A"))

    # Mesa para llenar boletas de depósito, de pie, con folletos.
    use(a.box("SlipDesk", (3.2, 2.5, .52), (1.8, .6, 1.04), "Navy", .02), wood)
    use(a.box("SlipTop", (3.2, 2.5, 1.06), (1.9, .7, .05), "Navy", .01), stone)
    lay.block(2.3, 2.2, 4.1, 2.8)
    for x in (2.7, 3.7):
        use(a.box("Slips", (x, 2.5, 1.1), (.25, .32, .03), "Navy", 0), paper)
        lay.station(x, 1.7, x, 2.5, 1.1)

    # Entrada: recepción a la izquierda, máquina de turnos y folletos, cajeros automáticos en su vestíbulo a la derecha.
    use(a.box("Reception", (-3.6, F + 4.2, .52), (2.6, .7, 1.04), "Navy", .02), wood)
    use(a.box("ReceptionTop", (-3.6, F + 4.2, 1.06), (2.7, .8, .05), "Navy", .01), stone)
    use(a.box("ReceptionStripe", (-3.6, F + 3.84, .6), (2.6, .02, .14), "Navy", 0), green)
    a.text("ReceptionText", "INFORMACIÓN", (-3.6, F + 3.82, .82), .14, "Ivory")
    prop("OfficeMonitor", -3.2, F + 4.35, 180, 1.08)
    lay.block(-5.0, F + 3.7, -2.2, F + 5.3)
    lay.post("recepcion", "stand", -3.6, F + 4.95, 0, top, bottom)
    use(a.box("TicketKiosk", (2.2, F + 3.0, .7), (.6, .45, 1.4), "Navy", .02), dark)
    use(a.box("TicketScreen", (2.2, F + 2.76, 1.2), (.45, .02, .32), "Navy", 0), led)
    lay.block(1.8, F + 2.7, 2.6, F + 3.3)
    lay.station(2.2, F + 2.2, 2.2, F + 2.8, 1.2)
    use(a.box("BrochureStand", (-6.8, F + 2.0, .7), (.7, .35, 1.4), "Navy", .01), wood)
    for z in (.6, .95, 1.3):
        use(a.box("Brochures", (-6.8, F + 1.8, z), (.6, .05, .25), "Navy", 0), paper)
    lay.block(-7.2, F + 1.6, -6.4, F + 2.4)
    lay.station(-6.8, F + 1.2, -6.8, F + 1.8, 1.0)
    for k in range(3):
        prop("ATM", W / 2 - 1.0, F + 1.5 + k * 1.1, -90)
    pane("AtmGlass", W / 2 - 2.6, F + 4.6, W / 2 - WALL, F + 4.6, 0, 2.6, glass, steel)
    use(a.box("AtmSign", (W / 2 - 1.4, F + 4.57, 2.85), (2.2, .04, .3), "Navy", .005), green)
    a.text("AtmSignText", "CAJEROS 24 H", (W / 2 - 1.4, F + 4.54, 2.85), .15, "Ivory")
    lay.block(W / 2 - 2.0, F + .6, W / 2, F + 4.7)
    for x in (-2.6, 2.6):
        plant(x, F + .9)
        lay.block(x - .35, F + .55, x + .35, F + 1.25)
    plant(-1.6, -5.2, .8)
    lay.block(-1.9, -5.5, -1.3, -4.9)

    # Zócalo de madera y cuadros en las paredes de la sala.
    for sx in (1, -1):
        use(a.box("Wainscot", (sx * (W / 2 - WALL - .02), 0, .5), (.03, D - 2 * WALL, 1.0), "Navy", 0), wood)
    for y in (-5.0, -2.6):
        use(a.box("Frame", (W / 2 - WALL - .03, y, 2.0), (.03, 1.2, .8), "Navy", .005), wood)
        use(a.box("FrameArt", (W / 2 - WALL - .05, y, 2.0), (.02, 1.0, .6), "Navy", 0), material("Cuadro_" + str(int(-y * 10)), "D9C27A" if y < -3 else "4E8F55"))
    cameras()
    till = dict(counter=unity(-1.8, cy - 1.0), scan=unity(-1.8, cy - .3) + [1.12], cashier=unity(-1.8, cy + .85),
                receipt=unity(-1.5, cy - .35) + [1.13], till=unity(-2.5, cy + .25) + [1.1],
                queue=[unity(0, cy - 2.1 - k * .95) for k in range(4)])
    return till, {}


def cash_counter(lay, x, y, length, body, top, accent):
    # Mostrador de caja a lo largo de Y junto a la entrada: el cajero queda a la izquierda (-X) mirando +X,
    # el cliente a la derecha y la fila crece hacia el interior.
    use(a.box("CashCounter", (x, y, .5), (.8, length, 1.0), "Navy", .02), body)
    use(a.box("CashTop", (x, y, 1.02), (.95, length + .1, .05), "Navy", .01), top)
    use(a.box("CashStripe", (x + .41, y, .62), (.02, length, .14), "Navy", 0), accent)
    use(a.box("Register", (x - .15, y - .45, 1.18), (.35, .3, .28), "Navy", .01), material("Grafito_Caja", "2B2F36"))
    use(a.box("CardReader", (x + .25, y - .2, 1.1), (.12, .18, .1), "Navy", .005), material("Grafito_Caja", "2B2F36"))
    lay.block(x - 1.3, y - length / 2 - .1, x + .45, y + length / 2 + .1)
    return dict(counter=unity(x + 1.0, y), scan=unity(x + .1, y + .25) + [1.06], cashier=unity(x - .9, y),
                receipt=unity(x + .2, y - .3) + [1.07], till=unity(x - .15, y - .45) + [1.3],
                queue=[unity(x + 1.0, y + length / 2 + .4 + k * .9) for k in range(3)])


def wall_stock(name, x, y0, y1, depth, height, body, colors, rows=4):
    # Repisa de pared llena de productos de colores (cigarros, golosinas, prendas dobladas).
    use(a.box(name, (x, (y0 + y1) / 2, height / 2), (depth, y1 - y0, height), "Navy", .01), body)
    step = (y1 - y0) / max(1, int((y1 - y0) / .32))
    for r in range(rows):
        z = .9 + r * (height - 1.0) / rows
        k, y = 0, y0 + step / 2
        while y < y1:
            front = x + (depth / 2 + .04 if x < 0 else -(depth / 2 + .04))
            use(a.box(name + "Item", (front, y, z + .12), (.08, step * .8, .22), "Navy", .005), colors[(k + r) % len(colors)])
            k, y = k + 1, y + step


def furnish_minimarket(lay):
    # Tienda de conveniencia según las referencias: caja a la entrada con golosinas de impulso y repisa detrás,
    # café contra la pared lejos de la puerta, bebidas frías al fondo, comida caliente y pasillos cortos visibles.
    green = material("Accent_minimarket", "2E9E5B")
    wood, top = material("Madera_Mini", "8A5A3B"), material("Laminado_Mini", "EDE8DC")
    steel, dark = material("Acero_Super", "B9C0C4"), material("Grafito_Caja", "2B2F36")
    heat = material("LamparaCalor", "FF8A3D", 2.0)
    polo, pants = material("Uniforme_Mini_Polo", "2E9E5B").name, material("Uniforme_Super_Pantalon", "2B2F36").name
    snacks = [material("Golosina_" + n, h) for n, h in (("Roja", "D64545"), ("Amarilla", "F2C94C"), ("Azul", "3E7CB1"), ("Verde", "6BBF59"))]

    till = cash_counter(lay, -5.4, F + 3.4, 2.8, wood, top, green)
    lay.post("caja", "stand", -6.3, F + 3.4, 90, polo, pants)
    use(a.box("CandyRack", (-5.4, F + 1.75, .6), (.8, .4, 1.2), "Navy", .01), green)
    for k in range(8):
        use(a.box("Candy", (-5.7 + (k % 4) * .2, F + 1.53, .55 + (k // 4) * .4), (.15, .06, .2), "Navy", .005), snacks[k % 4])
    lay.block(-5.85, F + 1.5, -4.95, F + 2.0)
    wall_stock("BackShelf", -W / 2 + WALL + .25, F + 2.0, F + 5.0, .5, 2.2, wood, snacks)
    use(a.box("LotteryPanel", (-W / 2 + WALL + .03, F + 3.5, 2.75), (.03, 1.6, .5), "Navy", .01), green)
    a.text("LotteryText", "LOTERÍA", (-W / 2 + WALL + .06, F + 3.5, 2.75), .2, "Ivory", rotation=(math.pi / 2, 0, math.pi / 2))
    lay.block(-W / 2, F + 1.9, -W / 2 + .9, F + 5.1)

    shelves(lay, (-2.2, 1.2, 4.6), 4)
    for x in (-2.2, 1.2, 4.6):
        use(a.box("SnackBin", (x, -5.2, .4), (1.2, .7, .8), "Navy", .02), green)
        for k in range(6):
            use(a.box("SnackBag", (x - .45 + (k % 3) * .45, -5.2 + (k // 3) * .25 - .12, .92), (.3, .08, .25), "Navy", .02), snacks[k % 4])
        lay.block(x - .65, -5.6, x + .65, -4.8)

    fridges(lay, 14, (-6.0, -2.0, 2.0))
    use(a.box("ColdSign", (-2.0, B - WALL - .03, 3.15), (5.0, .04, .5), "Navy", .01), green)
    a.text("ColdSignText", "BEBIDAS FRÍAS", (-2.0, B - WALL - .06, 3.15), .24, "Ivory")
    use(a.box("RestockCrate", (.6, B - 2.2, .3), (.6, .5, .6), "Navy", .01), wood)
    lay.block(.25, B - 2.5, .95, B - 1.9)
    lay.post("reponedor", "stand", -.2, B - 2.2, 180, polo, pants)
    lay.block(-.45, B - 2.45, .05, B - 1.95)
    # Comida caliente en la esquina del fondo.
    use(a.box("HotCase", (7.6, B - 1.0, .5), (3.0, .8, 1.0), "Navy", .02), steel)
    use(a.box("HotGlass", (7.6, B - 1.0, 1.25), (2.9, .7, .5), "Navy", 0), material("VidrioVitrina", "CFE4EA", 0, .25))
    use(a.box("HotLamp", (7.6, B - 1.0, 1.48), (2.8, .5, .03), "Navy", 0), heat)
    for k in range(8):
        use(a.cyl("HotDog", (6.4 + k * .34, B - 1.0, 1.06), .04, .25, "Navy", 8, rotation=(math.pi / 2, 0, 0)), material("Carne_Rosada", "E39A8C"))
    lay.block(6.0, B - 1.6, W / 2, B)
    lay.station(7.6, B - 2.2, 7.6, B - 1.0, 1.1)
    # Estación de café contra la pared derecha.
    use(a.box("CoffeeCounter", (W / 2 - .6, -1.5, .45), (.8, 3.0, .9), "Navy", .02), wood)
    use(a.box("CoffeeTop", (W / 2 - .6, -1.5, .92), (.9, 3.1, .05), "Navy", .01), top)
    for k in range(3):
        y = -2.5 + k * 1.0
        use(a.box("CoffeeMachine", (W / 2 - .65, y, 1.25), (.45, .5, .6), "Navy", .02), dark)
        use(a.box("CoffeeLight", (W / 2 - .89, y, 1.4), (.02, .2, .08), "Navy", 0), heat)
        use(a.cyl("Cups", (W / 2 - .45, y + .38, 1.08), .05, .28, "Navy", 10), material("Folleto", "F4F1E8"))
    use(a.box("CoffeeSign", (W / 2 - WALL - .03, -1.5, 2.6), (.03, 2.4, .5), "Navy", .01), green)
    a.text("CoffeeText", "CAFÉ", (W / 2 - WALL - .06, -1.5, 2.6), .26, "Ivory", rotation=(math.pi / 2, 0, -math.pi / 2))
    lay.block(W / 2 - 1.1, -3.1, W / 2, .1)
    lay.station(W / 2 - 1.8, -2.0, W / 2 - .6, -2.0, 1.0)
    lay.station(W / 2 - 1.8, -.8, W / 2 - .6, -.8, 1.0)
    # Entrada derecha: máquina expendedora, cajero automático, hielo y canastos; espejo convexo en la esquina.
    prop("VendingMachine", W / 2 - 1.0, F + 1.6, -90)
    prop("ATM", W / 2 - 1.0, F + 2.8, -90)
    lay.block(W / 2 - 1.6, F + .9, W / 2, F + 3.4)
    use(a.box("IceChest", (5.6, F + 1.2, .45), (1.0, .7, .9), "Navy", .03), material("Hielo", "EAF4FA"))
    a.text("IceText", "HIELO", (5.6, F + .84, .6), .16, "Navy").data.materials[0] = material("Azul_Hielo", "3E7CB1")
    lay.block(5.05, F + .8, 6.15, F + 1.6)
    for k in range(4):
        prop("ShoppingBasket", 2.7, F + .9 + k * .3, 0)
    lay.block(2.35, F + .6, 3.05, F + 2.1)
    use(a.sphere("ConvexMirror", (W / 2 - .45, B - .45, 3.3), (.3, .3, .3), "Navy", 2), material("Chrome", "C9D2D6"))
    cameras()
    return till, dict(SNACKS=(-2.2, 0), ABARROTES=(1.2, 0), LIMPIEZA=(4.6, 0))


def booth(x, y, wood, seat, table):
    # Reservado contra la pared izquierda: mesa entre dos bancas tapizadas con respaldo alto.
    use(a.box("BoothTable", (x, y, .74), (1.5, .8, .05), "Navy", .01), table)
    a.beam("BoothLeg", (x, y, 0), (x, y, .72), .05, "Metal")
    for dy in (-.75, .75):
        use(a.box("BoothSeat", (x, y + dy, .23), (1.5, .5, .46), "Navy", .03), seat)
        use(a.box("BoothBack", (x, y + dy * 1.33, .75), (1.5, .14, .6), "Navy", .03), seat)
    use(a.box("BoothFrame", (x, y, .05), (1.6, 2.4, .1), "Navy", 0), wood)


def furnish_comida(lay):
    # Comida rápida según las referencias: pedido al fondo con cocina abierta, retiro separado de la fila,
    # bebidas a un lado y asientos variados (reservados, mesa comunitaria y mesas de dos).
    red, wood = material("Accent_comida", "D9534A"), material("Madera_Comida", "8A5A3B")
    steel, dark = material("Acero_Super", "B9C0C4"), material("Grafito_Caja", "2B2F36")
    table, seat = material("Mesa_Comida", "EDE8DC"), material("Tapiz_Comida", "B83B34")
    heat, light = material("LamparaCalor", "FF8A3D", 2.0), material("LuzVitrina", "FFF4D6", 2.4)
    shirt, pants = material("Uniforme_Comida_Polera", "D9534A").name, material("Uniforme_Super_Pantalon", "2B2F36").name
    cook = material("Uniforme_Super_Delantal", "F4F1E8").name

    # Mostrador de pedidos con caja y paso de cocina bajo lámparas de calor.
    cb = B - 4.2
    use(a.box("OrderCounter", (0, cb, .52), (9.0, .8, 1.04), "Navy", .02), wood)
    use(a.box("OrderTop", (0, cb - .05, 1.07), (9.2, .95, .06), "Navy", .01), table)
    use(a.box("OrderStripe", (0, cb - .41, .6), (9.0, .02, .2), "Navy", 0), red)
    use(a.box("Register", (2.0, cb + .1, 1.24), (.4, .35, .3), "Navy", .01), dark)
    for x in (-3.2, -2.2, -1.2):
        use(a.cyl("HeatLamp", (x, cb, 1.9), .14, .16, "Navy", 12), heat)
        a.beam("HeatLampWire", (x, cb, 1.98), (x, cb, H - .05), .008, "Rubber")
        use(a.box("Tray", (x, cb - .1, 1.11), (.45, .32, .02), "Navy", 0), red)
        prop("ProductBox", x, cb - .1, 0, 1.12)
    # Menú colgado sobre el mostrador.
    for x, title in ((-3.0, "HAMBURGUESAS"), (0, "COMBOS"), (3.0, "BEBIDAS")):
        use(a.box("MenuBoard", (x, cb + .3, 3.05), (2.7, .06, .9), "Navy", .01), dark)
        a.text("MenuTitle", title, (x, cb + .26, 3.32), .15 if len(title) > 8 else .17, "Ivory").data.materials[0] = heat
        for k in range(3):
            use(a.box("MenuLine", (x - .25, cb + .26, 3.08 - k * .2), (1.6, .01, .05), "Navy", 0), table)
            use(a.box("MenuPrice", (x + .95, cb + .26, 3.08 - k * .2), (.35, .01, .07), "Navy", 0), red)
        a.beam("MenuWire", (x, cb + .3, 3.5), (x, cb + .3, H - .05), .008, "Rubber")
    # Cocina abierta: plancha con campana, freidora, mesa de armado y refrigeradores.
    for x, w in ((-2.5, 2.2), (1.5, 1.6), (4.6, 2.0)):
        use(a.box("KitchenLine", (x, B - .75, .45), (w, .8, .9), "Navy", .02), steel)
    use(a.box("Griddle", (-2.5, B - .75, .93), (2.0, .7, .04), "Navy", 0), dark)
    use(a.box("Hood", (-1.0, B - .7, 3.3), (5.4, 1.0, .6), "Navy", .02), steel)
    for dx in (-.35, .35):
        use(a.box("FryerBasket", (1.5 + dx, B - .75, 1.0), (.45, .45, .2), "Navy", .01), material("Aceite", "D9A35B"))
    for k in range(6):
        use(a.cyl("Sauce", (4.0 + k * .22, B - .8, 1.05), .045, .22, "Navy", 8), red if k % 2 else material("Mostaza", "F2C94C"))
    for x in (-6.2, -7.2):
        prop("Refrigerator", x, B - .7, 180)
    lay.block(-W / 2, cb - .45, W / 2, B)
    lay.post("caja", "stand", 2.0, cb + .85, 0, shirt, pants)
    lay.post("cocinero", "stand", -2.5, B - 1.55, 180, cook, pants)
    lay.post("cocinera", "stand", 1.5, B - 1.55, 180, cook, pants)

    # A los lados del mostrador: bebidas de autoservicio y estante de retiro numerado.
    use(a.box("DrinkCabinet", (-6.8, cb, .45), (2.2, .7, .9), "Navy", .02), wood)
    use(a.box("SodaFountain", (-6.8, cb + .05, 1.25), (1.4, .55, .7), "Navy", .02), red)
    for k in range(4):
        a.beam("Nozzle", (-7.3 + k * .33, cb - .25, 1.1), (-7.3 + k * .33, cb - .25, 1.25), .02, "Metal")
    use(a.box("PickupShelf", (6.8, cb, 1.0), (2.2, .6, 2.0), "Navy", .01), steel)
    for k in range(6):
        cx, cz = 6.1 + (k % 3) * .7, .7 + (k // 3) * .7
        use(a.box("Cubby", (cx, cb - .28, cz), (.6, .04, .55), "Navy", 0), dark)
        a.text("CubbyNumber", str(k + 1), (cx, cb - .31, cz + .2), .1, "Ivory")
        if k % 2 == 0:
            prop("ProductBox", cx, cb, 0, cz - .2)
    use(a.box("PickupSign", (6.8, cb - .3, 2.25), (2.2, .04, .3), "Navy", .005), red)
    a.text("PickupText", "RETIRO", (6.8, cb - .33, 2.25), .16, "Ivory")
    for x in (-7.4, -6.2):
        lay.station(x, cb - 1.0, x, cb, 1.1)
    for x in (6.1, 7.5):
        lay.station(x, cb - 1.0, x, cb - .1, 1.0)
    # Condimentos y basurero con bandejas camino a la salida.
    use(a.box("CondimentStand", (-4.0, 3.2, .5), (1.2, .6, 1.0), "Navy", .02), wood)
    for k in range(4):
        use(a.cyl("Dispenser", (-4.4 + k * .27, 3.2, 1.12), .06, .25, "Navy", 8), red if k % 2 else material("Mostaza", "F2C94C"))
    lay.block(-4.65, 2.85, -3.35, 3.55)
    lay.station(-4.0, 2.4, -4.0, 3.2, 1.1)
    use(a.box("TrashStation", (3.2, F + 2.2, .55), (.8, .6, 1.1), "Navy", .02), wood)
    use(a.box("TrayTop", (3.2, F + 2.2, 1.12), (.7, .5, .03), "Navy", 0), red)
    lay.block(2.75, F + 1.85, 3.65, F + 2.55)

    # Comedor: reservados contra la pared izquierda, mesa comunitaria con taburetes y mesas de dos a la derecha.
    art = (material("Cuadro_Tomate", "D9534A"), material("Mostaza", "F2C94C"), material("Cuadro_Oliva", "6B7A3A"))
    for k, y in enumerate((-6.6, -3.6, -.6)):
        booth(-8.6, y, wood, seat, table)
        lay.block(-W / 2, y - 1.25, -7.75, y + 1.25)
        # Cuadro sobre cada reservado.
        use(a.box("BoothFrame", (-W / 2 + WALL + .03, y, 2.05), (.03, 1.1, .8), "Navy", .005), wood)
        use(a.box("BoothArt", (-W / 2 + WALL + .05, y, 2.05), (.02, .9, .6), "Navy", 0), art[k])
        use(a.cyl("BoothArtDot", (-W / 2 + WALL + .07, y, 2.05), .18, .02, "Navy", 16, rotation=(0, math.pi / 2, 0)), table)
        use(a.cyl("BoothLamp", (-8.6, y, 2.6), .18, .2, "Navy", 12), red)
        a.beam("BoothLampWire", (-8.6, y, 2.7), (-8.6, y, H - .05), .008, "Rubber")
    use(a.box("CommunalTable", (3.6, -3.0, .9), (1.0, 4.4, .06), "Navy", .01), wood)
    for dy in (-1.6, 1.6):
        a.beam("CommunalLeg", (3.6, -3.0 + dy, 0), (3.6, -3.0 + dy, .88), .06, "Metal")
    for k in range(6):
        for sx in (-1, 1):
            y = -4.9 + k * .75
            use(a.cyl("Stool", (3.6 + sx * .8, y, .62), .18, .06, "Navy", 12), seat)
            a.beam("StoolLeg", (3.6 + sx * .8, y, 0), (3.6 + sx * .8, y, .6), .03, "Metal")
    lay.block(2.55, -5.3, 4.65, -.7)
    for y in (-6.6, -3.6, -.6):
        prop("RestaurantTable", 7.8, y, 0)
        prop("Chair", 7.1, y, 90)
        prop("Chair", 8.5, y, -90)
        prop("ProductBox", 7.8, y, 0, .83)
        lay.block(6.8, y - .55, 8.8, y + .55)
    for y in (-4.4, -1.6):
        use(a.cyl("Pendant", (3.6, y, 3.1), .25, .25, "Navy", 16), red)
        use(a.cyl("PendantBulb", (3.6, y, 2.96), .12, .05, "Navy", 12), light)
        a.beam("PendantWire", (3.6, y, 3.2), (3.6, y, H - .05), .008, "Rubber")
    lay.post("mesero", "stand", 5.8, -2.0, -90, shirt, pants)
    lay.block(5.55, -2.25, 6.05, -1.75)
    use(a.box("WallGraphic", (W / 2 - WALL - .03, 3.0, 2.3), (.03, 4.0, 1.0), "Navy", .01), red)
    a.text("WallGraphicText", "SABOR DE BARRIO", (W / 2 - WALL - .06, 3.0, 2.3), .26, "Ivory", rotation=(math.pi / 2, 0, -math.pi / 2))
    for x in (-2.6, 2.6):
        plant(x, F + .9, .8)
        lay.block(x - .3, F + .6, x + .3, F + 1.2)
    cameras()
    till = dict(counter=unity(2.0, cb - 1.0), scan=unity(2.0, cb - .25) + [1.1], cashier=unity(2.0, cb + .85),
                receipt=unity(2.3, cb - .3) + [1.11], till=unity(2.0, cb + .1) + [1.4],
                queue=[unity(2.0, cb - 1.95 - k * .95) for k in range(3)])
    return till, {}


def round_rack(x, y, colors, chrome):
    # Perchero redondo: base, poste y aro con prendas colgadas alrededor.
    use(a.cyl("RackBase", (x, y, .03), .45, .06, "Navy", 16), chrome)
    a.beam("RackPole", (x, y, 0), (x, y, 1.35), .025, "Metal")
    use(a.torus("RackRing", (x, y, 1.35), .55, .02, "Navy"), chrome)
    for k in range(12):
        angle = k * math.pi / 6
        garment = use(a.box("Garment", (x + .55 * math.cos(angle), y + .55 * math.sin(angle), 1.0), (.42, .04, .62), "Navy", .01),
                      colors[k % len(colors)])
        garment.rotation_euler = (0, 0, angle + math.pi / 2)


def furnish_ropa(lay):
    # Tienda de ropa según las referencias: zona despejada al entrar con mesa de presentación, caja adelante a la
    # izquierda, lo más vendido en la pared derecha, percheros al centro y probadores con banca para acompañantes.
    pink, wood = material("Accent_ropa", "C2457A"), material("Madera_Ropa", "8A5A3B")
    top, chrome = material("Laminado_Ropa", "F6F0F2"), material("Chrome", "C9D2D6")
    light, mirror = material("LuzVitrina", "FFF4D6", 2.4), material("Espejo", "D7E3EA")
    tee, jeans = material("Uniforme_Ropa_Polera", "1E1E22").name, material("Uniforme_Ropa_Jean", "3A5A8C").name
    cloth = [material("Tela_" + n, h) for n, h in (("Rosa", "E58FB1"), ("Marino", "2F4A6D"), ("Mostaza", "D9A93B"),
                                                   ("Blanca", "F2EFE8"), ("Oliva", "6B7A3A"), ("Coral", "E8735A"))]

    till = cash_counter(lay, -5.4, F + 3.4, 2.8, wood, top, pink)
    lay.post("caja", "stand", -6.3, F + 3.4, 90, tee, jeans)
    wall_stock("BagWall", -W / 2 + WALL + .2, F + 2.0, F + 5.0, .4, 2.0, wood, [pink, top], rows=2)
    use(a.box("BrandPanel", (-W / 2 + WALL + .03, F + 3.5, 2.75), (.03, 2.4, .6), "Navy", .01), pink)
    a.text("BrandText", "MODA URBANA", (-W / 2 + WALL + .06, F + 3.5, 2.75), .2, "Ivory", rotation=(math.pi / 2, 0, math.pi / 2))
    lay.block(-W / 2, F + 1.9, -W / 2 + .7, F + 5.1)

    # Vidrieras: maniquíes sobre tarimas a ambos lados de la puerta.
    for sx in (1, -1):
        use(a.box("WindowStage", (sx * 6.2, F + .8, .1), (4.0, 1.0, .2), "Navy", .01), wood)
        for k, x in enumerate((4.8, 6.2, 7.6)):
            prop("Mannequin", sx * x, F + .8, 0, .2)
        lay.block(sx * 4.1, F + .25, sx * 8.3, F + 1.35)
    # Zona de descompresión: mesa de presentación con prendas dobladas y luz de acento.
    for dx, h in ((-.6, .75), (.6, .6)):
        use(a.box("FeatureTable", (dx, -5.0, h / 2), (1.1, .9, h), "Navy", .02), wood)
        for k in range(3):
            use(a.box("FoldedStack", (dx - .3 + k * .3, -5.0, h + .06), (.26, .32, .12), "Navy", .01), cloth[(k + int(h * 10)) % 6])
    use(a.cyl("FeatureSpot", (0, -5.0, H - .12), .1, .14, "Navy", 12), light)
    lay.block(-1.2, -5.5, 1.2, -4.5)
    lay.station(0, -6.1, -.3, -5.0, .85)
    lay.station(0, -3.9, .3, -5.0, .7)

    # Pared derecha (la más vista al entrar): rieles con prendas colgadas y cubículos de prendas dobladas encima.
    for k, y0 in enumerate((-6.0, -3.0, 0.0, 3.0)):
        a.beam("WallRail", (W / 2 - .55, y0 + .1, 1.6), (W / 2 - .55, y0 + 2.4, 1.6), .02, "Metal")
        for n in range(12):
            use(a.box("WallGarment", (W / 2 - .55, y0 + .2 + n * .19, 1.22), (.5, .05, .7), "Navy", .01), cloth[(n // 3 + k) % 6])
        use(a.box("Cubbies", (W / 2 - .45, y0 + 1.25, 2.35), (.5, 2.3, .6), "Navy", .01), wood)
        for n in range(4):
            use(a.box("Folded", (W / 2 - .7, y0 + .5 + n * .5, 2.3), (.06, .38, .3), "Navy", .005), cloth[(n + k + 2) % 6])
        lay.station(W / 2 - 1.8, y0 + 1.25, W / 2 - .55, y0 + 1.25, 1.2)
    lay.block(W / 2 - 1.1, -6.1, W / 2, 5.5)
    # Centro: percheros redondos y percheros rectos hacia la pared izquierda.
    for x in (-2.6, 2.6):
        for y in (-1.2, 2.4):
            round_rack(x, y, cloth[(int(x) + int(y)) % 3::2] + cloth[:1], chrome)
            lay.block(x - .7, y - .7, x + .7, y + .7)
            lay.station(x, y - 1.15, x, y - .55, 1.0)
    for y in (-2.0, .6, 3.2):
        prop("ClothingRack", -6.4, y, 90)
        lay.block(-6.8, y - .8, -6.0, y + .8)
        lay.station(-5.3, y, -6.4, y, 1.2)
    use(a.box("Rug", (0, .6, .125), (8.0, 7.0, .01), "Navy", 0), material("Alfombra_Ropa", "D8C9B0"))
    lay.post("vendedora", "stand", 0, .6, 0, tee, jeans)
    lay.block(-.25, .35, .25, .85)

    # Fondo: cuatro probadores numerados, espejo grande, banca para acompañantes y la encargada.
    curtain = material("Cortina", "8E5BB0")
    for k in range(4):
        x = -7.6 + k * 2.0
        use(a.box("FittingRoom", (x, B - 1.1, 1.2), (1.8, 1.8, 2.4), "Navy", .02), material("Probador", "E9E3EF"))
        use(a.box("Curtain", (x, B - 2.02, 1.15), (1.4, .04, 2.1), "Navy", 0), curtain)
        a.text("RoomNumber", str(k + 1), (x, B - 2.05, 2.3), .14, "Navy")
    use(a.box("FittingSign", (-4.6, B - 2.1, 2.75), (2.6, .04, .3), "Navy", .005), pink)
    a.text("FittingText", "PROBADORES", (-4.6, B - 2.13, 2.75), .16, "Ivory")
    lay.block(-W / 2, B - 2.2, -.5, B)
    use(a.box("BigMirror", (3.0, B - WALL - .03, 1.3), (1.6, .03, 2.2), "Navy", 0), mirror)
    use(a.box("BigMirrorFrame", (3.0, B - WALL - .02, 1.3), (1.75, .02, 2.35), "Navy", 0), wood)
    use(a.box("WaitingBench", (6.4, B - .7, .25), (2.4, .6, .5), "Navy", .04), material("Tapiz_Ropa", "B5875B"))
    plant(8.6, B - .7, .9)
    lay.block(5.1, B - 1.1, W / 2, B)
    lay.post("probadores", "stand", .6, B - 2.6, 0, tee, jeans)
    lay.block(.35, B - 2.85, .85, B - 2.35)
    for y in (-1.2, 2.4):
        use(a.cyl("RackSpot", (-2.6, y, H - .12), .09, .14, "Navy", 12), light)
        use(a.cyl("RackSpot", (2.6, y, H - .12), .09, .14, "Navy", 12), light)
    cameras()
    return till, dict(MUJER=(-2.6, .6), HOMBRE=(2.6, .6))


# tipo, letrero, color de acento, pared, piso, baldosa, producto que se lleva el cliente, precio en centavos
KINDS = {
    "minimarket": ("MINIMARKET", "2E9E5B", "F3EBDD", "E2DED3", "C4BFB2", "ProductBox", "Abarrotes", 1500, furnish_minimarket),
    "supermercado": ("SUPERMERCADO", "E8742A", "F5EFE6", "E6E1D6", "CFC8BA", "ProductCan", "Compras del super", 4500, furnish_supermercado),
    "joyeria": ("JOYERÍA", "7B4FA3", "E8DCCB", "3A3542", "2E2A33", "JewelrySet", "Joyas", 250000, furnish_joyeria),
    "banco": ("BANCO", "1F6E4A", "EDEBE4", "E4E0D8", "D6D0C4", "CashStack", "Depósito", 50000, furnish_banco),
    "comida": ("COMIDA", "D9534A", "FBEFE3", "E8DCCB", "D4C3AC", "ProductBox", "Comida", 2500, furnish_comida),
    "ropa": ("ROPA", "C2457A", "F6F0F2", "C79A6E", "B5875B", "ProductBox", "Ropa", 8000, furnish_ropa),
}

# Acabados propios por tipo; los demás locales conservan baldosa de 1 m y toldo a rayas.
STYLE = {"banco": dict(tile=2.0, awning=False, cladding="CFC8BA"), "supermercado": dict(tile=2.0, awning=False, cladding="E6E1D6"), "joyeria": dict(tile=2.0, awning=False, cladding="2E2A33"),
         "minimarket": dict(tile=2.0), "comida": dict(tile=2.0), "ropa": dict(tile=2.0, awning=False, cladding="D8C9B0")}


def build_local(kind):
    title, accent_hex, wall_hex, floor_hex, tile_hex, product, product_name, price, furnish = KINDS[kind]
    root = a.begin("Local_" + kind.capitalize(), "City/Shops")
    root["ReviewStatus"] = "Pendiente de aprobación visual"
    accent = material("Accent_" + kind, accent_hex)
    trim = material("ShopTrim", "2B3A4A")
    glass = material("ShopGlass", "8FC3D1", 0, .35)
    shell(W, D, H, WALL, material("ShopFloor_" + kind, floor_hex), material("ShopWall_" + kind, wall_hex), trim, glass)
    style = STYLE.get(kind, {})
    use(a.box("SignBoard", (0, F - .16, 3.55), (8.0, .12, .9), "Navy", .02), accent)
    a.text("SignText", title, (0, F - .23, 3.55), .62 if len(title) < 11 else .5, "Ivory")
    if style.get("awning", True):
        for k in range(10):
            stripe = material("Awning_" + kind, accent_hex) if k % 2 == 0 else material("AwningWhite", "F7F7F2")
            x = -W / 2 + .9 + (k + .5) * (W - 1.8) / 10
            use(a.box("Awning", (x, F - .7, 2.95), ((W - 1.8) / 10, 1.4, .06), "Navy", 0), stripe).rotation_euler = (math.radians(-14), 0, 0)
    else:
        # Fachada sobria: marquesina lisa del color del local y revestimiento de piedra en los pilares.
        use(a.box("Canopy", (0, F - .6, 2.95), (W - 1.2, 1.2, .14), "Navy", .02), accent)
        cladding = material("Revestimiento_" + kind, style.get("cladding", "CFC8BA"))
        # Junto a la puerta el revestimiento empieza a 15 cm de la bisagra para que la hoja gire hacia afuera.
        for x in (-W / 2 + .3, W / 2 - .3, -1.42, 1.42):
            use(a.box("Cladding", (x, F - .02, H / 2), (.7 if abs(x) > 5 else .3, .06, H), "Navy", .01), cladding)
    lights(W, D, H, 4, 3)
    tile = material("ShopTile_" + kind, tile_hex)
    size = style.get("tile", 1.0)
    if size == 1.0:
        tiles = [use(a.box("FloorTiles", (-W / 2 + 1 + i, -D / 2 + 1 + j, .115), (1.0, 1.0, .01), "Navy", 0), tile)
                 for i in range(int(W - 1)) for j in range(int(D - 1)) if (i + j) % 2 == 0]
    else:
        # Losas grandes centradas en la planta: alternan dos tonos suaves sin el efecto de tablero.
        nx, ny = int((W - 2 * WALL) / size), int((D - 2 * WALL) / size)
        tiles = [use(a.box("FloorTiles", ((i - (nx - 1) / 2) * size, (j - (ny - 1) / 2) * size, .115), (size - .03, size - .03, .01), "Navy", 0), tile)
                 for i in range(nx) for j in range(ny) if (i + j) % 2 == 0]
    with bpy.context.temp_override(active_object=tiles[0], selected_editable_objects=tiles, selected_objects=tiles):
        bpy.ops.object.join()  # una sola malla para todas las baldosas
    for sx in (1, -1):
        use(a.box("WallBand", (sx * (W / 2 - WALL - .025), 0, 2.7), (.03, D - 2 * WALL, .35), "Navy", 0), accent)
    use(a.box("WallBand", (0, B - WALL - .025, 2.7), (W - 2 * WALL, .03, .35), "Navy", 0), accent)
    lay = Layout()
    till, signs = furnish(lay)
    for label, (x, y) in signs.items():
        use(a.box("AisleSign", (x, y, 3.25), (1.9, .06, .45), "Navy", .02), accent)
        a.beam("AisleWire", (x, y, 3.47), (x, y, H - .05), .01, "Rubber")
        for side, rot in ((-.035, 0), (.035, math.pi)):
            a.text("AisleText_" + label, label, (x, y + side, 3.25), .2, "Ivory", rotation=(math.pi / 2, 0, rot))
    inner = unity(-W / 2 + WALL + .3, F + WALL + .3), unity(W / 2 - WALL - .3, B - WALL - .3)
    layout = dict(kind=kind, model=root.name, width=W, depth=D, door_width=2.2, product=product, product_name=product_name, price_cents=price,
                  walkable=[min(inner[0][0], inner[1][0]), min(inner[0][1], inner[1][1]), max(inner[0][0], inner[1][0]), max(inner[0][1], inner[1][1])],
                  obstacles=lay.obstacles, stations=lay.stations, products=lay.products,
                  sidewalk=[unity(-4.0, F - 2.4), unity(4.0, F - 2.4)],  # frente a la puerta, sin pasar por mesas ni bancas
                  entry=[unity(0, F - 1.6), unity(0, F + .2), unity(0, F + 1.4)], exit=[unity(1.2, F + 1.4), unity(1.0, F + .2), unity(1.4, F - 1.6)],
                  staff=lay.staff, **till)
    return root, layout


# Vistas extra de revisión por tipo: (nombre, ojo, objetivo) relativos al local.
VIEWS = {"banco": (("ventanillas", (2.5, .2, 1.75), (-1.5, 7.5, 1.4)), ("asesores", (-3.0, -4.6, 2.0), (-8.5, -2.6, .9)),
                   ("gerencia", (3.2, -2.4, 2.0), (8.5, 2.6, 1.0))),
         "joyeria": (("mostrador", (1.6, 3.4, 1.7), (-1.0, 9.0, 1.3)), ("vitrinas", (-4.6, -6.8, 1.8), (-9.0, 1.0, 1.1)),
                     ("islas", (5.5, -6.5, 2.2), (0, 1.5, .9))),
         "supermercado": (("cajas", (1.5, -4.0, 2.2), (-6.0, -8.0, 1.0)), ("verduleria", (-.5, -9.5, 1.8), (5.5, -5.0, .8)),
                          ("carniceria", (1.6, 6.9, 1.7), (6.0, 9.8, 1.3))),
         "minimarket": (("caja", (-1.5, -4.6, 1.8), (-6.5, -8.6, 1.0)), ("cafe", (6.9, -5.8, 1.8), (9.6, -1.5, 1.1)),
                        ("bebidas", (.5, 4.5, 1.8), (-4.0, 10.6, 1.2))),
         "comida": (("mostrador", (0, 1.5, 1.8), (0, 9.5, 1.6)), ("comedor", (2.0, -9.0, 2.2), (-6.0, -2.0, .8)),
                    ("cocina", (4.0, 4.6, 2.0), (-2.0, 10.6, 1.2))),
         "ropa": (("caja", (-1.5, -4.6, 1.8), (-6.5, -8.6, 1.0)), ("percheros", (6.0, -7.5, 2.0), (-1.0, 2.0, 1.0)),
                  ("probadores", (3.0, 3.0, 1.8), (-3.0, 10.6, 1.2)))}


def dress(obj, slots, uniform):
    # Cambia las prendas indicadas por el material del uniforme (los nombres importados pueden llevar sufijo .001).
    for slot in obj.material_slots:
        if slot.material and slot.material.name.split(".")[0] in slots:
            slot.material = uniform


def sit(armature, front, right, seat):
    # Misma regla que SeatedPose.cs: orienta abdomen, piernas y brazos por dirección y apoya la cadera en el asiento.
    up = Vector((0, 0, 1))
    bones = armature.pose.bones
    world = armature.matrix_world
    inverse = world.to_3x3().inverted()

    def local(v):  # vector del espacio del personaje en Unity (derecha, arriba, frente) a espacio de la armadura
        return (inverse @ (right * v[0] + up * v[1] + front * v[2])).normalized()

    def aim(name, target, direction):
        bpy.context.view_layer.update()
        bone = bones[name]
        head = bone.head.copy()
        rotation = (target - head).normalized().rotation_difference(direction).to_matrix().to_4x4()
        bone.matrix = Matrix.Translation(head) @ rotation @ Matrix.Translation(-head) @ bone.matrix
        bpy.context.view_layer.update()

    aim("Abdomen", bones["Torso"].head.copy(), local((0, 1, -.3)))
    for side, mirror in (("L", 1), ("R", -1)):
        s = lambda v: (v[0] * mirror, v[1], v[2])
        lower, foot = bones["LowerLeg." + side], bones["Foot." + side]
        ankle = lower.matrix.inverted() @ foot.head
        aim("UpperLeg." + side, lower.head.copy(), local(s((-.06, .15, 1))))
        aim("LowerLeg." + side, lower.matrix @ ankle, local(s((0, -1, .25))))
        moved = lower.matrix @ ankle
        foot.matrix = Matrix.Translation(moved - foot.head) @ foot.matrix
        aim("UpperArm." + side, bones["LowerArm." + side].head.copy(), local(s((.15, -.45, .8))))
        aim("LowerArm." + side, bones["Wrist." + side].head.copy(), local(s((.35, .2, .9))))
    bpy.context.view_layer.update()
    hips = world @ bones["Hips"].head
    return seat + up * .04 - front * .08 - hips


def preview_staff(layout, offset):
    # Solo para las capturas: viste a los civiles con el uniforme y los pone en sus puestos. No se exporta.
    slots = {m["model"]: m for m in json.loads((a.ART / "Characters" / "Cast" / "staff_uniform_slots.json").read_text())["models"]}
    models = sorted(slots)
    added = []
    for i, post in enumerate(layout["staff"]):
        model = models[(i * 3 + 1) % len(models)]
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(a.ART / "Characters" / "Cast" / (model + ".fbx")))
        new = list(set(bpy.data.objects) - before)
        added += new
        x, y, yaw = post["blender"]
        holder = bpy.data.objects.new("Personal_" + post["role"], None)
        bpy.context.scene.collection.objects.link(holder)
        added.append(holder)
        holder.location = (offset + x, y, 0)
        holder.rotation_euler = (0, 0, math.radians(yaw))
        for o in new:
            if o.parent is None:
                o.parent = holder
            if o.type == "MESH":
                o.hide_render = o.name.startswith("ShoppingBag_")
                dress(o, slots[model]["top"], bpy.data.materials[post["top"]])
                dress(o, slots[model]["bottom"], bpy.data.materials[post["bottom"]])
        bpy.context.view_layer.update()
        if post["pose"] == "seat":
            armature = next(o for o in new if o.type == "ARMATURE")
            turn = Matrix.Rotation(math.radians(yaw), 3, "Z")
            front, right = turn @ Vector((0, -1, 0)), turn @ Vector((-1, 0, 0))
            seat = Vector((offset + x, y, post["seat"]))
            holder.location += sit(armature, front, right, seat)
    return added


def review(root, name, offset):
    scene = bpy.context.scene
    cam = scene.camera
    hidden = [o for o in a.descendants(root) if o.name.startswith(("Roof", "Ceiling", "Parapet"))]
    ox = offset
    extra = tuple((label, (ox + e[0], e[1], e[2]), (ox + t[0], t[1], t[2]), False) for label, e, t in VIEWS.get(name, ()))
    for label, eye, target, hide in (("fachada", (ox - 9, -24, 5), (ox, -6, 2.5), False), ("interior", (ox, -7, 25), (ox, 0, 0), True),
                                     ("pasillo", (ox - 3.2, -9.5, 1.7), (ox + 3, 6, 1.2), False)) + extra:
        for o in hidden:
            o.hide_render = hide
        cam.location = eye
        cam.data.lens = 35 if label in ("fachada", "interior") else 28
        cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(a.ART / "Previews~" / f"local_{name}_{label}.png")
        bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False


def stage():
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    world = bpy.data.worlds.new("Cielo")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.5, .6, .7, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .6
    scene.world = world
    sun = bpy.data.objects.new("Sol", bpy.data.lights.new("Sol", "SUN"))
    sun.data.energy = 2.6
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.collection.objects.link(sun)
    ground = bpy.data.meshes.new("Suelo")
    ground.from_pydata([(-40, -40, 0), (240, -40, 0), (240, 40, 0), (-40, 40, 0)], [], [(0, 1, 2, 3)])
    g = bpy.data.objects.new("Suelo", ground)
    scene.collection.objects.link(g)
    g.data.materials.append(material("Acera", "9C9A94"))
    cam = bpy.data.objects.new("Camara", bpy.data.cameras.new("Camara"))
    scene.collection.objects.link(cam)
    scene.camera = cam


def flat(value):
    # JsonUtility de Unity no lee listas anidadas: los puntos se guardan como listas planas de números.
    return [round(v, 3) for item in value for v in (item if isinstance(item, (list, tuple)) else [item])]


# Uso parcial: blender -b --factory-startup -P build_shops.py -- --only banco
# Solo regenera esos locales; los demás conservan su FBX, su entrada del JSON y sus materiales.
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only = args[args.index("--only") + 1].split(",") if "--only" in args else list(KINDS)
unknown = [k for k in only if k not in KINDS]
if unknown:
    raise SystemExit("Tipos de local desconocidos: " + ", ".join(unknown))

bpy.ops.wm.read_factory_settings(use_empty=True)
a.new_scene("Shops")
OUT.mkdir(parents=True, exist_ok=True)
stage()
built = {}
for i, kind in enumerate(only):
    root, layout = build_local(kind)
    meshes = [o for o in a.descendants(root) if o.type == "MESH"]
    print("LOCAL", root.name, len(meshes), "piezas", sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons), "triángulos",
          len(layout["stations"]), "puestos", len(layout["staff"]), "empleados")
    a.export_asset(root.name)
    root.location = (i * 40, 0, 0)
    bpy.context.view_layer.update()
    staff = preview_staff(layout, i * 40) if layout["staff"] else []
    review(root, kind, i * 40)
    for o in staff:
        bpy.data.objects.remove(o, do_unlink=True)
    for post in layout["staff"]:
        post.pop("blender")
    built[kind] = {k: (flat(v) if k in ("obstacles", "stations", "products", "sidewalk", "entry", "exit", "queue") else v) for k, v in layout.items()}
previous = json.loads((OUT / "shop_layouts.json").read_text(encoding="utf-8"))["shops"] if len(only) < len(KINDS) else []
shops = [built.pop(s["kind"], s) for s in previous] + list(built.values())
(OUT / "shop_layouts.json").write_text(json.dumps(dict(shops=shops), indent=1, ensure_ascii=False), encoding="utf-8")
entries = {e["name"]: e for e in json.loads((OUT / "shop_materials.json").read_text())["materials"]} if len(only) < len(KINDS) else {}
for n, (h, e, al) in sorted(REGISTRY.items()):
    if n != "Alarma_Acera":
        entries[n] = dict(name=n, r=int(h[0:2], 16) / 255, g=int(h[2:4], 16) / 255, b=int(h[4:6], 16) / 255, a=al, metallic=0, roughness=.7, emission=round(e * .5, 2))
(OUT / "shop_materials.json").write_text(json.dumps(dict(materials=[entries[n] for n in sorted(entries)]), indent=1), encoding="utf-8")
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)  # sin restos de la vista previa
suffix = "" if len(only) == len(KINDS) else "_" + "_".join(only)
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / "BlenderSources~" / f"Alarma_Shops{suffix}.blend"), compress=True)
print("LOCALES", only)
