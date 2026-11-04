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
from mathutils import Vector

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
        self.obstacles, self.stations, self.products = [], [], []

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


def furnish_minimarket(lay):
    shelves(lay, (-1.0, 2.6, 6.2), 5)
    fridges(lay, 14, (-5.5, -1.0, 3.5))
    till = counter(lay, "Checkout")
    for k in range(3):
        prop("ProductBox", -4.6, F + 2.6 + k * .2, 0, 1.0)
    prop("VendingMachine", W / 2 - 1.0, F + 1.6, -90)
    prop("ATM", W / 2 - 1.0, F + 3.0, -90)
    lay.block(W / 2 - 1.6, F + .9, W / 2 - .3, F + 3.6)
    for k in range(3):
        prop("StorageCrate", -W / 2 + 1.0, -2 + k * .9, 0)
    lay.block(-W / 2 + .4, -2.5, -W / 2 + 1.5, 0)
    for k in range(4):
        prop("ShoppingBasket", -2.4 + k * .3, F + 1.4, 0)
    cameras()
    return till, dict(SNACKS=(-1.0, 0), ABARROTES=(2.6, 0), LIMPIEZA=(6.2, 0), BEBIDAS=(0, B - 2.2))


def furnish_supermercado(lay):
    shelves(lay, (-1.6, 1.8, 5.2), 6)
    fridges(lay, 17, (-6.0, -2.0, 2.0, 6.0))
    till = counter(lay, "Checkout")
    # Verdulería: cajones con fruta y verdura de colores contra la pared izquierda.
    fruit = [material("Fruta_" + n, h) for n, h in (("Naranja", "F28C28"), ("Manzana", "D64545"), ("Lima", "7CB342"), ("Platano", "F2D04A"))]
    for k in range(5):
        y = -3.6 + k * 1.3
        prop("StorageCrate", -W / 2 + 1.0, y, 90)
        for n in range(6):
            use(a.sphere("Fruit", (-W / 2 + .8 + (n % 3) * .2, y - .15 + (n // 3) * .25, .85), (.09, .09, .09), "Navy", 1), fruit[(k + n) % 4])
        if k % 2 == 0:
            lay.station(-W / 2 + 2.3, y, -W / 2 + 1.0, y, .85)
    lay.block(-W / 2 + .4, -4.3, -W / 2 + 1.6, 2.2)
    for k in range(6):
        prop("ShoppingBasket", W / 2 - 1.2, F + 1.2 + k * .35, 0)
    prop("ATM", W / 2 - 1.0, F + 3.6, -90)
    lay.block(W / 2 - 1.6, F + .8, W / 2 - .3, F + 4.2)
    cameras()
    return till, dict(ABARROTES=(-1.6, 0), LACTEOS=(1.8, 0), LIMPIEZA=(5.2, 0), FRESCOS=(0, B - 2.2), VERDULERIA=(-W / 2 + 1.6, -1.0))


def furnish_joyeria(lay):
    gold = material("Oro", "C9A227")
    # Vitrinas contra las paredes y dos islas centrales, cada una con joyas a la vista.
    for sx in (1, -1):
        for k in range(5):
            y = -4.5 + k * 2.4
            prop("JewelryDisplay", sx * (W / 2 - .7), y, -90 * sx)
            prop("JewelrySet", sx * (W / 2 - .75), y, 0, 1.15)
            lay.station(sx * (W / 2 - 2.0), y, sx * (W / 2 - .75), y, 1.18)
        lay.block(sx * (W / 2 - .2), -5.4, sx * (W / 2 - 1.2), 5.9)
    for x in (-2.6, 2.6):
        for y in (-1.5, 2.5):
            prop("GlassCabinet", x, y, 0)
            prop("JewelrySet", x - .2, y, 0, 1.15)
            lay.station(x, y - 1.3, x - .2, y, 1.18)
            lay.block(x - .85, y - .45, x + .85, y + .4)
    prop("Safe", 0, B - .8, 180)
    prop("Safe", 1.2, B - .8, 180)
    lay.block(-.6, B - 1.4, 1.8, B - .2)
    for x in (-1.5, 1.5):
        prop("LaserEmitter", x, B - 2.5, 0, H - .35)
    use(a.box("VipCarpet", (0, 1.0, .135), (3.0, 9.0, .02), "Navy", 0), material("Alfombra_Joyeria", "5A2D6E"))
    use(a.box("Mirror", (0, B - WALL - .05, 2.2), (2.4, .03, 1.6), "Navy", 0), material("Espejo", "D7E3EA"))
    use(a.box("MirrorFrame", (0, B - WALL - .02, 2.2), (2.6, .02, 1.8), "Navy", 0), gold)  # detrás del espejo
    till = counter(lay, "GlassCabinet")
    cameras()
    return till, {}


def furnish_banco(lay):
    # Ventanillas al fondo, bóveda en la pared trasera, escritorios de atención y sillas de espera.
    prop("VaultDoor", 0, B - .35, 180)
    lay.block(-1.4, B - .7, 1.4, B - .2)
    for x in (-6.0, -3.6, 3.6, 6.0):
        prop("BankCounter", x, B - 3.2, 180)
        prop("OfficeMonitor", x + .4, B - 3.0, 180, 1.05)
        prop("CashStack", x - .3, B - 3.3, 0, 1.05)
        lay.station(x, B - 4.6, x - .3, B - 3.3, 1.08)
    lay.block(-7.2, B - 3.7, -2.4, B - 2.7)
    lay.block(2.4, B - 3.7, 7.2, B - 2.7)
    for sx in (1, -1):
        for y in (-2.5, .5):
            prop("OfficeDesk", sx * (W / 2 - 1.5), y, -90 * sx)
            prop("OfficeMonitor", sx * (W / 2 - 1.3), y, -90 * sx, .79)
            prop("Chair", sx * (W / 2 - 2.5), y, 90 * sx)
            lay.station(sx * (W / 2 - 3.9), y - .6, sx * (W / 2 - 1.5), y, .82)
        lay.block(sx * (W / 2 - .3), -3.2, sx * (W / 2 - 3.0), 1.2)
    # Fila con postes y cordón frente a las ventanillas, logo sobre la bóveda y plantas.
    rope = material("Cordon", "B3262E")
    posts = [(x, y) for y in (3.2, 1.8) for x in (-3.0, -1.0, 1.0, 3.0)]
    for x, y in posts:
        use(a.cyl("Stanchion", (x, y, .5), .04, 1.0, "Metal", 8), material("Chrome", "C9D2D6"))
    for (x0, y0), (x1, y1) in zip(posts[:3], posts[1:4]):
        use(a.beam("Rope", (x0, y0, .9), (x1, y1, .9), .02, "Navy", 6), rope)
    use(a.box("BankLogo", (0, B - WALL - .03, 3.3), (3.4, .04, .7), "Navy", .02), material("Accent_banco", "1F6E4A"))
    a.text("BankLogoText", "BANCO", (0, B - WALL - .06, 3.3), .4, "Ivory", rotation=(math.pi / 2, 0, math.pi))
    for x in (-3.5, 3.5):
        prop("StorageCrate", x, F + 1.2, 0)
        lay.block(x - .45, F + .8, x + .45, F + 1.6)
        use(a.sphere("Plant", (x, F + 1.2, 1.2), (.45, .45, .55), "Navy", 1), material("Planta", "4E8F55"))
    for x in (-2.0, -1.4, -.8, .8, 1.4, 2.0):
        prop("Chair", x, -1.5, 180)
    lay.block(-2.4, -2.0, 2.4, -1.0)
    for k in range(2):
        prop("ATM", W / 2 - 1.0, F + 1.4 + k * 1.1, -90)
    lay.block(W / 2 - 1.6, F + .8, W / 2 - .3, F + 3.0)
    for x in (-W / 2 + 1.0, W / 2 - 1.0):
        prop("StorageCrate", x, B - 1.2, 0)
        use(a.sphere("Plant", (x, B - 1.2, 1.2), (.45, .45, .5), "Navy", 1), material("Planta", "4E8F55"))
    use(a.box("BankStripe", (0, 0, .135), (2.2, D - 3, .02), "Navy", 0), material("Alfombra_Banco", "2C5E4A"))
    till = counter(lay, "BankCounter")
    cameras()
    return till, {}


def furnish_comida(lay):
    # Cocina al fondo, mostrador de pedidos, mesas con sillas y pizarra de menú.
    for x in (-5.0, -2.8, -.6, 1.6):
        prop("FoodCounter", x, B - .8, 180)
    prop("Refrigerator", 3.6, B - .7, 180)
    prop("Refrigerator", 4.6, B - .7, 180)
    lay.block(-6.2, B - 1.4, 5.2, B - .2)
    use(a.box("MenuBoard", (-5.0, F + WALL + .03, 3.1), (3.0, .04, 1.0), "Navy", .01), material("Pizarra", "1E252C"))
    a.text("MenuText", "MENÚ", (-5.0, F + WALL + .07, 3.35), .3, "Ivory", rotation=(math.pi / 2, 0, math.pi))
    for i, x in enumerate((-1.5, 2.0, 5.5)):
        for j, y in enumerate((-4.0, -.5, 3.0)):
            prop("RestaurantTable", x, y, 0)
            prop("Chair", x - .7, y, 90)   # el frente de la silla (-Y) gira hacia la mesa
            prop("Chair", x + .7, y, -90)
            prop("ProductBox", x, y, 0, .83)
            lay.block(x - 1.0, y - .55, x + 1.0, y + .55)
            if (i + j) % 2 == 0:
                lay.station(x, y - 1.1, x, y, .86)
    till = counter(lay, "FoodCounter")
    cameras()
    return till, {}


def furnish_ropa(lay):
    # Percheros en filas, maniquíes en la vidriera y probadores al fondo.
    for x in (-1.5, 2.0, 5.5):
        for k in range(4):
            y = -4.0 + k * 2.2
            prop("ClothingRack", x, y, 90)
            if k % 2 == 0:
                lay.station(x + 1.0, y, x, y, 1.2)
        lay.block(x - .35, -4.8, x + .35, 3.4)
    for x in (-7.5, 4.0, 6.5):
        prop("Mannequin", x, F + 1.0, 0)
    lay.block(3.5, F + .5, 7.0, F + 1.5)
    curtain = material("Cortina", "8E5BB0")
    for k in range(3):
        x = -6.0 + k * 2.0
        use(a.box("FittingRoom", (x, B - 1.1, 1.2), (1.8, 1.8, 2.4), "Navy", .02), material("Probador", "E9E3EF"))
        use(a.box("Curtain", (x, B - 2.02, 1.2), (1.4, .04, 2.2), "Navy", 0), curtain)
    lay.block(-7.0, B - 2.1, -3.0, B - .2)
    use(a.box("Rug", (2.0, 0, .135), (10.0, 9.0, .02), "Navy", 0), material("Alfombra_Ropa", "D8C9B0"))
    till = counter(lay, "Checkout")
    cameras()
    return till, {}


# tipo, letrero, color de acento, pared, piso, baldosa, producto que se lleva el cliente, precio en centavos
KINDS = {
    "minimarket": ("MINIMARKET", "2E9E5B", "F3EBDD", "E2DED3", "C4BFB2", "ProductBox", "Abarrotes", 1500, furnish_minimarket),
    "supermercado": ("SUPERMERCADO", "E8742A", "F5EFE6", "E6E1D6", "CFC8BA", "ProductCan", "Compras del super", 4500, furnish_supermercado),
    "joyeria": ("JOYERÍA", "7B4FA3", "F2EEF5", "3A3542", "2E2A33", "JewelrySet", "Joyas", 250000, furnish_joyeria),
    "banco": ("BANCO", "1F6E4A", "F0F2EE", "E9E6E0", "D2CEC6", "CashStack", "Depósito", 50000, furnish_banco),
    "comida": ("COMIDA", "D9534A", "FBEFE3", "E8DCCB", "D4C3AC", "ProductBox", "Comida", 2500, furnish_comida),
    "ropa": ("ROPA", "C2457A", "F6F0F2", "C79A6E", "B5875B", "ProductBox", "Ropa", 8000, furnish_ropa),
}


def build_local(kind):
    title, accent_hex, wall_hex, floor_hex, tile_hex, product, product_name, price, furnish = KINDS[kind]
    root = a.begin("Local_" + kind.capitalize(), "City/Shops")
    root["ReviewStatus"] = "Pendiente de aprobación visual"
    accent = material("Accent_" + kind, accent_hex)
    trim = material("ShopTrim", "2B3A4A")
    glass = material("ShopGlass", "8FC3D1", 0, .35)
    shell(W, D, H, WALL, material("ShopFloor_" + kind, floor_hex), material("ShopWall_" + kind, wall_hex), trim, glass)
    use(a.box("SignBoard", (0, F - .16, 3.55), (8.0, .12, .9), "Navy", .02), accent)
    a.text("SignText", title, (0, F - .23, 3.55), .62 if len(title) < 11 else .5, "Ivory")
    for k in range(10):
        stripe = material("Awning_" + kind, accent_hex) if k % 2 == 0 else material("AwningWhite", "F7F7F2")
        x = -W / 2 + .9 + (k + .5) * (W - 1.8) / 10
        use(a.box("Awning", (x, F - .7, 2.95), ((W - 1.8) / 10, 1.4, .06), "Navy", 0), stripe).rotation_euler = (math.radians(-14), 0, 0)
    lights(W, D, H, 4, 3)
    tile = material("ShopTile_" + kind, tile_hex)
    tiles = [use(a.box("FloorTiles", (-W / 2 + 1 + i, -D / 2 + 1 + j, .115), (1.0, 1.0, .01), "Navy", 0), tile)
             for i in range(int(W - 1)) for j in range(int(D - 1)) if (i + j) % 2 == 0]
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
                  entry=[unity(0, F - 1.6), unity(0, F + .2), unity(0, F + 1.4)], exit=[unity(1.2, F + 1.4), unity(1.0, F + .2), unity(1.4, F - 1.6)], **till)
    return root, layout


def review(root, name, offset):
    scene = bpy.context.scene
    cam = scene.camera
    hidden = [o for o in a.descendants(root) if o.name.startswith(("Roof", "Ceiling", "Parapet"))]
    ox = offset
    for label, eye, target, hide in (("fachada", (ox - 9, -24, 5), (ox, -6, 2.5), False), ("interior", (ox, -7, 25), (ox, 0, 0), True),
                                     ("pasillo", (ox - 3.2, -9.5, 1.7), (ox + 3, 6, 1.2), False)):
        for o in hidden:
            o.hide_render = hide
        cam.location = eye
        cam.data.lens = 28 if label == "pasillo" else 35
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


bpy.ops.wm.read_factory_settings(use_empty=True)
a.new_scene("Shops")
OUT.mkdir(parents=True, exist_ok=True)
stage()
shops = []
for i, kind in enumerate(KINDS):
    root, layout = build_local(kind)
    meshes = [o for o in a.descendants(root) if o.type == "MESH"]
    print("LOCAL", root.name, len(meshes), "piezas", sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons), "triángulos",
          len(layout["stations"]), "puestos")
    a.export_asset(root.name)
    root.location = (i * 40, 0, 0)
    bpy.context.view_layer.update()
    review(root, kind, i * 40)
    shops.append({k: (flat(v) if k in ("obstacles", "stations", "products", "sidewalk", "entry", "exit", "queue") else v) for k, v in layout.items()})
(OUT / "shop_layouts.json").write_text(json.dumps(dict(shops=shops), indent=1, ensure_ascii=False), encoding="utf-8")
entries = [dict(name=n, r=int(h[0:2], 16) / 255, g=int(h[2:4], 16) / 255, b=int(h[4:6], 16) / 255, a=al, metallic=0, roughness=.7, emission=round(e * .5, 2))
           for n, (h, e, al) in sorted(REGISTRY.items()) if n != "Alarma_Acera"]
(OUT / "shop_materials.json").write_text(json.dumps(dict(materials=entries), indent=1), encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / "BlenderSources~" / "Alarma_Shops.blend"))
print("LOCALES", list(KINDS))
