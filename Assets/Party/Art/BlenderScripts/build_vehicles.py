"""Autos de Alarma, versión 3: ocho modelos con silueta propia, conductor visible, luces que brillan y más detalle.

Convenciones para Unity (el juego cambia colores y luces en tiempo de ejecución por nombre de material):
- Alarma_Paint_*: pintura de carrocería; cada auto de la calle recibe un color distinto.
- Alarma_Headlight, Alarma_TailLight, Alarma_Indicator: faros, luces traseras (más fuertes al frenar) e intermitentes.
- Alarma_CarGlass: vidrio semitransparente para ver a quien conduce.
- Seat_Driver, Seat_Passenger y SteeringGrip: donde Unity sienta a un civil del elenco al volante y, a veces, a un acompañante.
Se mantienen: frente hacia -Y, metros, puertas separadas (Door_* con DoorPanel_*), ruedas separadas (Wheel_* con Tire_*),
asientos y punto de carga como vacíos.
Uso: blender -b --factory-startup -P build_vehicles.py [-- --export]
Sin --export solo renderiza la revisión: los FBX del juego se reemplazan cuando Alain aprueba el diseño.
Salida: Art/Vehicles/<auto>.fbx, BlenderSources~/Alarma_Vehicles.blend y Previews~/autos_v3_*.png.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import alarmart as a  # noqa: E402

# Colores propios de los autos (sRGB) e intensidad de brillo. La pintura de cada modelo es la de la revisión: en la calle varía.
OWN = {"Headlight": ("FFF6D8", 4.0), "TailLight": ("E8322B", 2.5), "Indicator": ("FFA21F", 2.5), "Chrome": ("C9D2D6", 0), "Trim": ("1E252C", 0)}
# nombre, tipo, pintura, largo, ancho, cintura, techo, radio de rueda, techo solar
CARS = [
    ("Car_Sedan", "sedan", "D9534A", 4.5, 1.80, .97, 1.44, .33, False),
    ("Car_Hatchback", "hatch", "2F9C8F", 3.9, 1.74, 1.0, 1.50, .32, True),
    ("Car_SUV", "suv", "4F5D6B", 4.75, 1.94, 1.12, 1.80, .38, True),
    ("Car_Pickup", "pickup", "A33B32", 5.25, 1.96, 1.10, 1.82, .38, False),
    ("Car_Van", "van", "ECECE6", 4.9, 1.92, 1.05, 2.05, .34, False),
    ("Car_Coupe", "coupe", "2D5FD0", 4.45, 1.86, .90, 1.28, .34, False),
    ("Car_Taxi", "taxi", "F2C230", 4.5, 1.80, .97, 1.44, .33, False),
    ("Car_Police", "police", "1F3352", 4.6, 1.82, .97, 1.46, .33, True),
]


REGISTRY = {}


def material(name, hex_color, emission=0.0, alpha=1.0):
    REGISTRY["Alarma_" + name] = (hex_color, emission, alpha)
    m = bpy.data.materials.get("Alarma_" + name)
    if m:
        return m
    m = bpy.data.materials.new("Alarma_" + name)
    color = tuple(a.linear(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4))
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = .35 if name.startswith("Paint") else .7
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    if alpha < 1:
        bsdf.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    return m


def use(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def solid(name, profile, x0, x1, mat, parent=None, top_width=None, split=None, open_bottom=False):
    # Extruye un perfil lateral (y, z) entre x0 y x1; con top_width estrecha la parte de arriba.
    # open_bottom deja sin la cara que cierra el último punto con el primero (la base de la cabina de vidrio).
    bm = bmesh.new()
    left = [bm.verts.new((x0, y, z)) for y, z in profile]
    right = [bm.verts.new((x1, y, z)) for y, z in profile]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    for i in range(len(profile) - (1 if open_bottom else 0)):
        j = (i + 1) % len(profile)
        bm.faces.new((left[i], left[j], right[j], right[i]))
    if top_width:
        for v in bm.verts:
            if v.co.z > split:
                v.co.x *= top_width / (x1 - x0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    data = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    a.COLLECTION.objects.link(obj)
    obj.parent = parent or a.ROOT
    data.materials.append(mat)
    return obj


def soften(obj, width=.05, segments=3, angle=30):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    m = obj.modifiers.new("Suavizado", "BEVEL")
    m.width, m.segments, m.limit_method, m.angle_limit = width, segments, "ANGLE", math.radians(angle)
    bpy.ops.object.modifier_apply(modifier=m.name)


def cut(body, location, size=None, radius=None, depth=None, rotation=None):
    cutter = a.cyl("Corte", location, radius, depth, vertices=20, rotation=rotation) if radius else a.box("Corte", location, size, bevel=0)
    bpy.context.view_layer.objects.active = body
    m = body.modifiers.new("Corte", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", cutter
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def arch_trim(name, x, y, radius, mat):
    # Moldura oscura en media luna sobre el arco de la rueda.
    bm = bmesh.new()
    inner, outer, ring = radius + .06, radius + .13, []
    for k in range(13):
        t = math.pi * k / 12
        ring.append(((y + math.cos(t) * inner, radius + math.sin(t) * inner), (y + math.cos(t) * outer, radius + math.sin(t) * outer)))
    sx = 1 if x > 0 else -1
    for (i0, o0), (i1, o1) in zip(ring, ring[1:]):
        quad = [bm.verts.new((x, *p)) for p in (i0, o0, o1, i1)]
        back = [bm.verts.new((x - sx * .05, *p)) for p in (i0, o0, o1, i1)]
        bm.faces.new(quad if sx > 0 else list(reversed(quad)))
        bm.faces.new((quad[1], back[1], back[2], quad[2]) if sx > 0 else (quad[2], back[2], back[1], quad[1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=.001)
    data = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    a.COLLECTION.objects.link(obj)
    obj.parent = a.ROOT
    data.materials.append(mat)
    return obj


def shape(kind, L, belt, roof):
    # Perfiles laterales con curvas suaves: carrocería baja hasta la cintura y cabina de vidrio encima.
    f, r = -L / 2, L / 2
    nose = [(f + .14, .30), (f + .02, .40), (f, .52), (f + .02, .64), (f + .1, .74), (f + .26, .81)]
    tail = [(r - .04, .84), (r, .66), (r - .02, .48), (r - .06, .38), (r - .16, .30)]
    if kind == "suv":
        lower = [(f + .16, .34), (f + .02, .46), (f, .66), (f + .04, .86), (f + .18, belt - .07), (f + 1.1, belt), (r - .12, belt), (r - .02, belt - .1), (r, .62), (r - .04, .44), (r - .16, .34)]
        glass = [(f + 1.1, belt), (f + 1.78, roof), (r - .28, roof), (r - .12, belt)]
    elif kind == "van":
        lower = [(f + .16, .32), (f + .02, .44), (f, .66), (f + .06, .86), (f + .3, belt - .02), (f + .86, belt), (r - .06, belt), (r, belt - .1), (r, .5), (r - .1, .32)]
        glass = [(f + .86, belt), (f + 1.42, roof), (r - .1, roof), (r - .06, belt)]
    elif kind == "pickup":
        lower = [(f + .16, .36), (f + .02, .48), (f, .70), (f + .06, .92), (f + .3, belt), (r - .02, belt), (r, belt - .08), (r, .52), (r - .12, .36)]
        glass = [(f + 1.12, belt), (f + 1.7, roof), (f + 2.62, roof), (f + 2.75, belt)]
    elif kind == "hatch":
        lower = nose + [(f + .46, .87), (f + 1.08, belt), (r - .24, belt), (r - .04, belt - .08)] + tail[1:]
        glass = [(f + 1.08, belt), (f + 1.8, roof), (r - .5, roof), (r - .24, belt)]
    elif kind == "coupe":
        lower = nose + [(f + .5, .82), (f + 1.4, belt), (r - .95, belt), (r - .25, belt - .02)] + tail
        glass = [(f + 1.4, belt), (f + 2.25, roof), (r - 1.55, roof), (r - .95, belt)]
    else:
        lower = nose + [(f + .5, .86), (f + 1.25, belt), (r - 1.05, belt), (r - .3, belt - .03)] + tail
        glass = [(f + 1.25, belt), (f + 2.05, roof), (r - 1.65, roof), (r - 1.05, belt)]
    return lower, glass


def build(name, kind, paint_hex, L, W, belt, roof, radius, passenger):
    root = a.begin(name, "Vehicles")
    root["RigStatus"] = "Modelo estático; puertas, ruedas, conductor y luces listos para dinámica"
    root["Design"] = "v3"
    tag = name.replace("Car_", "")
    paint = material("Paint_" + tag, paint_hex)
    head, tail, amber = (material(k, *OWN[k]) for k in ("Headlight", "TailLight", "Indicator"))
    glass_mat = material("CarGlass", "5E8A96", 0, .3)
    seat_mat, cabin_mat = material("Seat", "3A4250"), material("Cabin", "2E3238")
    chrome, trim = material("Chrome", *OWN["Chrome"]), material("Trim", *OWN["Trim"])
    plate = material("Plate", "F2F2EC")
    f, r = -L / 2, L / 2
    front_axle = f + {"hatch": .82, "van": .78, "coupe": 1.02}.get(kind, .95)
    rear_axle = r - {"hatch": .74, "pickup": 1.1, "van": .85}.get(kind, 1.0)
    lower, glass = shape(kind, L, belt, roof)
    body = solid("Body", lower, -W / 2, W / 2, paint)
    soften(body)
    for y in (front_axle, rear_axle):
        cut(body, (0, y, radius), radius=radius + .07, depth=W + .4, rotation=(0, math.pi / 2, 0))
    if kind == "pickup":
        # Caja de carga abierta detrás de la cabina.
        bed_front = f + 2.95
        cut(body, (0, (bed_front + r - .08) / 2, belt + .18), size=(W - .16, r - .08 - bed_front, .5))
        a.box("BedFloor", (0, (bed_front + r - .08) / 2, belt - .25), (W - .16, r - .1 - bed_front, .04), "Asphalt", 0)
        use(a.box("TailgateHandle", (0, r + .005, belt - .12), (.3, .02, .05), "Navy", .005), chrome)
        a.box("CargoBox", (0, bed_front + .4, belt - .02), (W - .3, .5, .42), "Wood", .02)
    # Cabina abierta por dentro: se ven asientos, tablero y quien conduce.
    cabin_end = glass[-1][0] - .05 if kind != "pickup" else f + 2.78
    cut(body, (0, (glass[0][0] + .12 + cabin_end) / 2, belt - .18), size=(W - .14, cabin_end - glass[0][0] - .12, .9))
    floor_z = belt - .62
    use(a.box("CabinFloor", (0, (glass[0][0] + cabin_end) / 2 + .06, floor_z), (W - .14, cabin_end - glass[0][0] - .12, .04), "Navy", 0), cabin_mat)
    for sx in (1, -1):
        use(a.box("DoorTrim", (sx * (W / 2 - .085), (glass[0][0] + cabin_end) / 2 + .06, belt - .2), (.03, cabin_end - glass[0][0] - .2, .36), "Navy", .01), cabin_mat)
        use(a.box("Armrest", (sx * (W / 2 - .12), (glass[0][0] + cabin_end) / 2 - .1, belt - .14), (.06, .45, .05), "Navy", .01), seat_mat)
    solid("WindowCabin", glass, -W * .44, W * .44, glass_mat, top_width=W * .8, split=belt + .05, open_bottom=True)
    roof_front, roof_back = glass[1][0], glass[2][0]
    use(a.box("Roof", (0, (roof_front + roof_back) / 2, roof + .025), (W * .82, roof_back - roof_front + .12, .06), "Navy", .025), paint)
    # Molduras finas a cada lado de las ventanas (una placa entera taparía la cabina vista desde arriba).
    for sx in (1, -1):
        use(a.box("BeltTrim", (sx * W * .445, (glass[0][0] + glass[-1][0]) / 2, belt + .012), (.035, glass[-1][0] - glass[0][0], .025), "Navy", .005), chrome)
    if kind in ("sedan", "hatch") and passenger:
        use(a.box("Sunroof", (0, (roof_front + roof_back) / 2 - .1, roof + .058), (W * .4, .55, .01), "Navy", 0), trim)
    front_end = (glass[0][0] + glass[-1][0]) / 2 + (.25 if kind == "coupe" else -.05)
    doors = [("F", glass[0][0] - .02, front_end)]
    if kind != "coupe":
        doors.append(("R", front_end, glass[-1][0] if kind == "pickup" else rear_axle - radius - .12))
    for side, sx in (("L", 1), ("R", -1)):  # frente -Y: la izquierda del auto es +X
        use(a.beam("PillarA_" + side, (sx * W * .43, glass[0][0] + .06, belt), (sx * W * .39, roof_front + .04, roof), .045, "Navy"), paint)
        use(a.beam("PillarC_" + side, (sx * W * .39, roof_back - .04, roof), (sx * W * .43, glass[-1][0] - .05, belt), .06, "Navy"), paint)
        use(a.beam("PillarB_" + side, (sx * W * .44, front_end, belt + .02), (sx * W * .40, front_end, roof - .02), .035, "Navy"), trim)
        use(a.box("SideLine_" + side, (sx * (W / 2 + .004), (front_axle + rear_axle) / 2, belt - .2), (.012, rear_axle - front_axle + .4, .03), "Navy", 0), paint)
        for label, y0, y1 in doors:
            hinge = a.empty("Door_" + label + side, (sx * (W / 2 + .012), y0, belt))
            panel = a.box("DoorPanel_" + label + side, (0, (y1 - y0) / 2, -(belt - .40) / 2), (.03, y1 - y0 - .03, belt - .40), "Navy", .012, parent=hinge)
            use(panel, material("Paint_PoliceDoor", "F7F7F2") if kind == "police" else paint)
            for edge in (.01, y1 - y0 - .01):
                use(a.box("DoorSeam_" + label + side, (sx * .017, edge, -(belt - .40) / 2), (.006, .012, belt - .42), "Navy", 0, parent=hinge), trim)
            use(a.box("DoorHandle_" + label + side, (sx * .022, y1 - y0 - .22, -.12), (.03, .16, .035), "Navy", .006, parent=hinge), chrome)
            if kind == "taxi":
                for k in range(int((y1 - y0) / .16)):
                    use(a.box("Checker_" + label + side + str(k), (sx * .02, .1 + k * .16, -.2 - (k % 2) * .06), (.01, .08, .06), "Navy", 0, parent=hinge), trim)
            if kind == "police" and label == "F":
                a.text("PoliceDoor_" + side, "POLICÍA", (sx * .025, (y1 - y0) / 2 + .05, -.2), .16, "Navy", rotation=(math.pi / 2, 0, sx * math.pi / 2), parent=hinge)
        if kind == "van":
            use(a.box("SlidingRail_" + side, (sx * (W / 2 + .006), front_end + .6, belt + .03), (.02, 1.3, .03), "Navy", 0), trim)
        use(a.box("Mirror_" + side, (sx * (W / 2 + .1), glass[0][0] + .18, belt + .08), (.1, .17, .11), "Navy", .025), paint)
        use(a.beam("MirrorArm_" + side, (sx * W / 2, glass[0][0] + .2, belt + .04), (sx * (W / 2 + .08), glass[0][0] + .18, belt + .07), .018, "Navy"), trim)
        use(a.box("SideSkirt_" + side, (sx * (W / 2 - .01), (front_axle + rear_axle) / 2, .33), (.05, rear_axle - front_axle - 2 * radius - .22, .09), "Navy", .01), trim)
        for y, label in ((front_axle, "F"), (rear_axle, "R")):
            arch_trim("ArchTrim_" + side + label, sx * (W / 2 + .01), y, radius, trim)
        # Luces: faro con luz de día, intermitentes delantero y lateral, piloto trasero envolvente.
        use(a.box("Headlight_" + side, (sx * W * .32, f + .02, .7), (.38, .06, .11), "Navy", .025), head)
        use(a.box("DayLight_" + side, (sx * W * .32, f + .015, .63), (.3, .05, .025), "Navy", 0), head)
        use(a.box("Indicator_" + side, (sx * W * .45, f + .04, .7), (.09, .05, .09), "Navy", .01), amber)
        use(a.box("SideIndicator_" + side, (sx * (W / 2 + .005), front_axle + radius + .2, .66), (.01, .08, .04), "Navy", 0), amber)
        rear_z = {"suv": .92, "van": .95, "pickup": .9}.get(kind, .76)
        use(a.box("TailLight_" + side, (sx * W * .36, r - .01, rear_z), (.38, .06, .13), "Navy", .025), tail)
        use(a.box("TailWrap_" + side, (sx * (W / 2 - .02), r - .12, rear_z), (.05, .22, .11), "Navy", .01), tail)
        use(a.box("RearIndicator_" + side, (sx * W * .2, r - .005, rear_z), (.1, .04, .08), "Navy", .01), amber)
    tall = kind in ("van", "suv")
    use(a.box("ThirdBrakeLight", (0, r - .08 if tall else glass[-1][0] - .02, roof - .1 if tall else (belt + roof) / 2 + .2), (.4, .03, .04), "Navy", 0), tail)
    # Parachoques, parrilla, patentes y escape.
    use(a.box("FrontBumper", (0, f - .015, .41), (W + .05, .17, .21), "Navy", .05), trim)
    use(a.box("RearBumper", (0, r + .015, .41), (W + .05, .17, .21), "Navy", .05), trim)
    use(a.box("FrontGrille", (0, f - .004, .58), (W * .46, .05, .15), "Navy", .02), trim)
    for z in (.55, .61):
        use(a.box("GrilleBar", (0, f - .03, z), (W * .44, .02, .018), "Navy", 0), chrome)
    use(a.box("PlateFront", (0, f - .105, .41), (.5, .02, .12), "Navy", .005), plate)
    use(a.box("PlateRear", (0, r + .105, .44), (.5, .02, .12), "Navy", .005), plate)
    use(a.cyl("Exhaust", (W * .3, r + .06, .3), .04, .2, "Metal", 8, (math.pi / 2, 0, 0)), chrome)
    # Ruedas separadas: neumático redondeado, llanta de rayos y tapacubos.
    spokes = 6 if kind == "coupe" else 5
    for side, sx in (("L", 1), ("R", -1)):  # frente -Y: la izquierda del auto es +X
        for label, y in (("F", front_axle), ("R", rear_axle)):
            wheel = a.empty("Wheel_" + label + side, (sx * W * .46, y, radius))
            tire = a.cyl("Tire_" + label + side, (0, 0, 0), radius, .25 if kind in ("pickup", "suv", "coupe") else .23, "Rubber", 18, (0, math.pi / 2, 0), parent=wheel)
            soften(tire, .035, 2)
            use(a.cyl("Rim_" + label + side, (sx * .1, 0, 0), radius * .64, .04, "Metal", 16, (0, math.pi / 2, 0), parent=wheel), chrome)
            for k in range(spokes):
                angle = k * math.tau / spokes
                a.box("Spoke_" + label + side + str(k), (sx * .125, math.cos(angle) * radius * .3, math.sin(angle) * radius * .3),
                      (.02, .05, radius * .55), "Asphalt", 0, parent=wheel, rotation=(angle - math.pi / 2, 0, 0))
            a.cyl("Hub_" + label + side, (sx * .13, 0, 0), .06, .03, "Ivory", 8, (0, math.pi / 2, 0), parent=wheel)
    # Interior, conductor y acompañante (el juego decide si va acompañado).
    seat_z = belt - .52  # cojín a la altura real de un asiento: la persona sentada cabe bajo el techo
    seat_y = front_end - (.45 if kind == "coupe" else .2)
    for x in (.42, -.42):
        use(a.box("FrontSeat", (x, seat_y, seat_z - .06), (.5, .52, .14), "Navy", .04), seat_mat)
        use(a.box("SeatBack", (x, seat_y + .3, seat_z + .27), (.48, .12, .58), "Navy", .04), seat_mat)
        use(a.box("Headrest", (x, seat_y + .32, seat_z + .66), (.26, .1, .16), "Navy", .03), seat_mat)
    if kind not in ("coupe", "pickup"):
        use(a.box("RearSeat", (0, seat_y + .95, seat_z - .06), (W * .78, .5, .14), "Navy", .04), seat_mat)
        use(a.box("RearSeatBack", (0, seat_y + 1.22, seat_z + .25), (W * .78, .12, .52), "Navy", .04), seat_mat)
    use(a.box("CenterConsole", (0, seat_y - .1, seat_z), (.2, .7, .22), "Navy", .02), trim)
    use(a.cyl("GearLever", (0, seat_y - .3, seat_z + .2), .012, .16, "Metal", 6), chrome)
    use(a.sphere("GearKnob", (0, seat_y - .3, seat_z + .28), (.03, .03, .03), "Navy", 1), trim)
    use(a.box("Dashboard", (0, glass[0][0] + .28, belt + .02), (W * .84, .32, .16), "Navy", .03), trim)
    use(a.box("InstrumentHood", (.42, glass[0][0] + .38, belt + .1), (.42, .14, .06), "Navy", .02), trim)
    for dx in (-.08, .08):
        use(a.cyl("Dial", (.42 + dx, glass[0][0] + .45, belt + .07), .05, .01, "Metal", 12, (math.radians(80), 0, 0)), material("DialFace", "DDEBF0", 1.0))
    use(a.box("CenterScreen", (0, glass[0][0] + .43, belt + .05), (.24, .02, .12), "Navy", .005), material("Screen", "4FB3FF", 1.5))
    use(a.box("RearViewMirror", (0, glass[0][0] + .62, roof - .1), (.22, .03, .07), "Navy", .01), trim)
    for x in (.42, -.42):
        use(a.box("SunVisor", (x, roof_front + .12, roof - .04), (.38, .16, .02), "Navy", .005), cabin_mat)
    wheel_y = seat_y - .42
    use(a.cyl("SteeringColumn", (.42, wheel_y - .12, seat_z + .36), .03, .3, "Metal", 8, (math.radians(-60), 0, 0)), trim)
    a.torus("SteeringWheel", (.42, wheel_y, seat_z + .46), .17, .025, "Rubber", rotation=(math.radians(65), 0, 0))
    a.empty("Seat_Driver", (.42, seat_y, seat_z))  # a la izquierda: se circula por la derecha
    a.empty("Seat_Passenger", (-.42, seat_y, seat_z))
    a.empty("SteeringGrip", (.42, wheel_y, seat_z + .46))
    a.empty("Trunk_LoadPoint", (0, r - .5, belt - .1))
    if tall:
        for x in (-W * .34, W * .34):
            use(a.box("RoofRail", (x, (roof_front + roof_back) / 2, roof + .09), (.05, roof_back - roof_front, .05), "Navy", .01), chrome)
    if kind == "coupe":
        use(a.box("Spoiler", (0, r - .2, belt + .16), (W * .8, .22, .04), "Navy", .01), paint)
        for x in (-W * .3, W * .3):
            use(a.box("SpoilerLeg", (x, r - .2, belt + .07), (.05, .1, .14), "Navy", .005), trim)
        use(a.box("HoodScoop", (0, f + .95, .9), (.5, .4, .05), "Navy", .02), trim)
    if kind == "pickup":
        use(a.box("BullBar", (0, f - .18, .6), (W * .7, .08, .45), "Navy", .02), trim)
    if kind == "taxi":
        use(a.box("TaxiRoofSign", (0, (roof_front + roof_back) / 2, roof + .16), (.7, .3, .22), "Navy", .04), material("TaxiSign", "FFF7DF", 1.2))
        for y, rot in ((-.152, 0), (.152, math.pi)):
            a.text("TaxiLabel" + ("F" if y < 0 else "B"), "TAXI", (0, (roof_front + roof_back) / 2 + y, roof + .16), .15, "Navy", rotation=(math.pi / 2, 0, rot))
    if kind == "police":
        y = (roof_front + roof_back) / 2
        use(a.box("LightBarBase", (0, y, roof + .08), (1.15, .3, .07), "Navy", .02), trim)
        use(a.box("LightBarRed", (-.31, y, roof + .16), (.5, .3, .12), "Navy", .03), material("SirenRed", "FF3B30", 3))
        use(a.box("LightBarBlue", (.31, y, roof + .16), (.5, .3, .12), "Navy", .03), material("SirenBlue", "2F7BFF", 3))
        use(a.box("PushBar", (0, f - .14, .5), (W * .62, .06, .32), "Navy", .02), trim)
        a.cyl("Antenna", (W * .25, roof_back - .1, roof + .3), .01, .5, "Rubber", 6)
    return root


# Pose sentada por direcciones de hueso (espacio del personaje: frente -Y, arriba +Z, izquierda +X). Unity usa la misma regla.
POSE_DRIVE = {"Abdomen": (0, .3, 1), "UpperLeg": (.06, -1, .15), "LowerLeg": (0, -.25, -1), "UpperArm": (-.15, -.8, -.45), "LowerArm": (-.35, -.9, .2)}
POSE_RIDE = dict(POSE_DRIVE, UpperArm=(-.1, -.35, -1), LowerArm=(-.1, -1, -.15))


def seat_character(path, seat, driving):
    from mathutils import Matrix
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    new = set(bpy.data.objects) - before
    arm = next(o for o in new if o.type == "ARMATURE")
    for o in new:
        if o.animation_data:
            o.animation_data_clear()
        if o.name.startswith(("ShoppingBag_", "Grip_")):
            o.hide_render = True
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    pb = arm.pose.bones
    rule = POSE_DRIVE if driving else POSE_RIDE

    def aim(bone, point, desired):
        rot = (point() - pb[bone].head).rotation_difference(Vector(desired))
        h = pb[bone].head.copy()
        pb[bone].matrix = Matrix.Translation(h) @ rot.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb[bone].matrix
        bpy.context.view_layer.update()

    aim("Abdomen", lambda: pb["Torso"].head, rule["Abdomen"])
    for side, sx in (("L", 1), ("R", -1)):
        ankle = pb["LowerLeg." + side].matrix.inverted() @ pb["Foot." + side].head
        mirror = lambda v: (v[0] * sx, v[1], v[2])
        aim("UpperLeg." + side, lambda: pb["LowerLeg." + side].head, mirror(rule["UpperLeg"]))
        aim("LowerLeg." + side, lambda: pb["LowerLeg." + side].matrix @ ankle, rule["LowerLeg"])
        foot = pb["Foot." + side]
        foot.matrix = Matrix.Translation(pb["LowerLeg." + side].matrix @ ankle - foot.head) @ foot.matrix
        bpy.context.view_layer.update()
        aim("UpperArm." + side, lambda: pb["LowerArm." + side].head, mirror(rule["UpperArm"]))
        aim("LowerArm." + side, lambda: pb["Wrist." + side].head, mirror(rule["LowerArm"]))
    bpy.ops.object.mode_set(mode="OBJECT")
    hips = arm.matrix_world @ pb["Hips"].head
    target = seat.matrix_world.translation + Vector((0, .08, .04))  # cadera sobre el cojín: la cabeza queda bajo el techo
    arm.location += target - hips


def review(names):
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1800, 900
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 32
    world = bpy.data.worlds.new("Estudio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.55, .64, .74, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .7
    scene.world = world
    sun = bpy.data.objects.new("Sol", bpy.data.lights.new("Sol", "SUN"))
    sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(55), 0, math.radians(35))
    scene.collection.objects.link(sun)
    floor = bpy.data.meshes.new("Suelo")
    floor.from_pydata([(-20, -25, 0), (60, -25, 0), (60, 25, 0), (-20, 25, 0)], [], [(0, 1, 2, 3)])
    ground = bpy.data.objects.new("Suelo", floor)
    scene.collection.objects.link(ground)
    ground.data.materials.append(material("Asfalto", "3B434A"))
    # Un civil del elenco al volante de cada auto y acompañante en algunos, como los sentará Unity.
    bpy.context.view_layer.update()
    cast = sorted((a.ART / "Characters" / "Cast").glob("NPC0*.fbx")) + [a.ART / "Characters" / "Cast" / "NPC10_Cardigan.fbx"]
    for i, name in enumerate(names):
        parts = a.descendants(a.CATALOG[name]["root"])
        seat_character(cast[i % len(cast)], next(o for o in parts if o.name.startswith("Seat_Driver")), True)
        if i % 2:
            seat_character(cast[(i + 5) % len(cast)], next(o for o in parts if o.name.startswith("Seat_Passenger")), False)
    cam = bpy.data.objects.new("Camara", bpy.data.cameras.new("Camara"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    out = a.ART / "Previews~"
    out.mkdir(exist_ok=True)
    mid = (len(names) - 1) * 2.4
    shots = (("frente", (-6, -24, 9), (mid, 0, .7), 50), ("atras", (mid * 2 + 6, 22, 9), (mid, 0, .7), 50),
             ("conductor", (2.4, -4.4, 1.6), (.3, -.3, .9), 40), ("detalle", (5.9, -6.2, 1.6), (4.8, 0, .8), 45),
             ("arriba", (28.8 + 1.5, -4.5, 5.2), (28.8, 0, .6), 40))
    for label, eye, target, lens in shots:
        cam.location = eye
        cam.data.lens = lens
        cam.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out / f"autos_v3_{label}.png")
        bpy.ops.render.render(write_still=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
a.new_scene("Vehicles")
names = []
for car in CARS:
    build(*car)
    names.append(car[0])
    meshes = [o for o in a.descendants(a.CATALOG[car[0]]["root"]) if o.type == "MESH"]
    triangles = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    path = a.export_asset(car[0]) if "--export" in sys.argv else "sin exportar"
    print("AUTO", car[0], len(meshes), "piezas", triangles, "triángulos", path)
if "--export" in sys.argv:
    # Colores propios para Unity (sRGB); el brillo se reduce porque Unity no usa el mismo motor de luz.
    entries = [dict(name=n, r=int(h[0:2], 16) / 255, g=int(h[2:4], 16) / 255, b=int(h[4:6], 16) / 255, a=al, metallic=0,
                    roughness=.4 if "Paint" in n else .75, emission=round(e * .5, 2)) for n, (h, e, al) in sorted(REGISTRY.items()) if n != "Alarma_Asfalto"]
    (a.ART / "Vehicles" / "vehicle_materials.json").write_text(__import__("json").dumps(dict(materials=entries), indent=1), encoding="utf-8")
    print("COLORES", len(entries))
a.arrange(names, len(names), (2.4 * 2, 0))
bpy.ops.wm.save_as_mainfile(filepath=str(a.ART / "BlenderSources~" / "Alarma_Vehicles.blend"))
review(names)
print("AUTOS_V3", names)
