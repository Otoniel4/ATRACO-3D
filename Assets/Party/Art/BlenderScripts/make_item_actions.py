"""Genera Data/Items/item_actions.json: duración, efecto y animación de uso de cada objeto del inventario.

Es la fuente compartida: Unity crea o actualiza los assets Action_<id> con estos datos (ItemActionAssets) y
preview_item_actions.py dibuja los mismos cuadros en Blender para revisarlos.
Curvas: lista plana de pares (tiempo 0–1, valor). Desplazamiento en metros (side derecha, up arriba, forward adelante),
giros del objeto en grados (pitch positivo = punta abajo), torso en grados (leanForward adelante, leanTwist a la
derecha, leanSide de costado) y leftHand 0–1 (cuánto va la mano izquierda al agarre Grip_L).
Al cambiar los datos, subir VERSION: Unity vuelve a escribir los assets que tengan una versión anterior.
Uso: python make_item_actions.py
"""
import json
from pathlib import Path

VERSION = 6
OUT = Path(__file__).resolve().parents[2] / 'Data' / 'Items' / 'item_actions.json'
ACTIONS = []


def K(*points):
    return [round(v, 4) for p in points for v in p]


def add(id, type, duration, trigger, curves, repeat=False, shake=0.0, spin='', spinSpeed=0.0, blink='', clip=False,
        fullBody=False, noise=0.0, **data):
    # noise: hasta dónde se oye, en metros (lo escuchan los civiles por el canal Data/Events/Ruido.asset).
    entry = dict(id=id, type=type, duration=duration, trigger=trigger, repeat=repeat, shake=shake,
                 spin=spin, spinSpeed=spinSpeed, blink=blink, clip=clip, fullBody=fullBody, noise=noise, curves=curves)
    entry.update(data)
    ACTIONS.append(entry)


# Armas: retroceso hacia atrás, arriba y la punta sube; el torso cede un poco y todo vuelve a la guardia.
def recoil(back, lift, kick, settle, lean):
    peak = settle * .15
    return dict(forward=K((0, 0), (peak, -back), (settle, 0), (1, 0)), up=K((0, 0), (peak, lift), (settle, 0), (1, 0)),
                pitch=K((0, 0), (peak, -kick), (settle, 0), (1, 0)), leanForward=K((0, 0), (peak, -lean), (settle, 0), (1, 0)))


FLASH, TRAIL, BLUE = [1, .82, .4], [1, .9, .6], [.4, .75, 1]


def firearm(damage, reach, pellets, hip, aim, stun=False, pump='', flash=FLASH, tracer=TRAIL):
    return dict(damage=damage, range=reach, pellets=pellets, hipSpread=hip, aimSpread=aim, stun=stun, pump=pump,
                flash=flash, tracer=tracer)


def tool(reach, nothing, consume=False, rope=False, requireTarget=False):
    # requireTarget: solo empieza si hay un objetivo que la acepte al frente (la animación necesita a la otra persona).
    return dict(range=reach, consume=consume, rope=rope, nothing=nothing, requireTarget=requireTarget)


add('pistola', 'firearm', .25, 0, recoil(.05, .022, 16, .55, 2), noise=35, firearm=firearm(25, 60, 1, 4, .6))
add('taser', 'firearm', 1.2, 0, recoil(.025, .012, 6, .3, 1), noise=4, firearm=firearm(0, 9, 1, 3, .8, stun=True, flash=BLUE, tracer=BLUE))
add('escopeta', 'firearm', 1.0, 0, recoil(.1, .06, 26, .35, 4), noise=45, firearm=firearm(64, 35, 8, 7, 4.5, pump='Pump'))
add('rifle', 'firearm', .1, 0, recoil(.028, .01, 5, .9, .8), repeat=True, noise=40, firearm=firearm(18, 90, 1, 3, .4))

# Herramientas, granadas y termita usan clip de cuerpo (build_action_clips.py): clip=True. fullBody=True usa todo el
# cuerpo (rodillas y cadera) y deja al jugador quieto mientras dura; si no, solo el torso y se puede caminar.
# Curvas que solo usa el clip: crouch (metros que baja la cadera), kneel (0–1, rodilla derecha al piso), step (metros que
# avanza el pie izquierdo), headPitch/headTurn (cabeza abajo y a la derecha, grados) y leftSide/leftUp/leftForward
# (mano izquierda libre respecto del pecho, cuando no está en Grip_L).

# Palanca: la toma con las dos manos, la recoge junto al pecho, la clava al frente a la altura de la cerradura
# y tira dos veces del mango hacia un lado para hacer palanca, flexionando las rodillas con el esfuerzo.
add('palanca', 'tool', 1.3, .45, dict(
    side=K((0, 0), (.2, .03), (.42, -.04), (.5, -.03), (.62, .09), (.7, .05), (.78, .11), (.9, .03), (1, 0)),
    up=K((0, 0), (.2, .28), (.42, .24), (.5, .25), (.62, .22), (.7, .23), (.78, .21), (.9, .08), (1, 0)),
    forward=K((0, 0), (.2, -.1), (.42, .1), (.5, .07), (.62, .03), (.7, .05), (.78, .02), (.9, .02), (1, 0)),
    pitch=K((0, 0), (.2, -22), (.42, -10), (.5, -10), (.62, -6), (.78, -4), (.9, -4), (1, 0)),
    yaw=K((0, 0), (.5, 0), (.62, -24), (.7, -14), (.78, -32), (.9, -8), (1, 0)),
    leanForward=K((0, 0), (.2, -4), (.42, 16), (.5, 14), (.62, 10), (.78, 10), (.9, 4), (1, 0)),
    leanTwist=K((0, 0), (.2, 12), (.42, -4), (.5, -3), (.62, 10), (.7, 6), (.78, 14), (.9, 4), (1, 0)),
    crouch=K((0, 0), (.2, .02), (.42, .07), (.62, .06), (.78, .08), (.9, .02), (1, 0)),
    step=K((0, 0), (.2, 0), (.42, .22), (.9, .22), (1, 0)),
    headPitch=K((0, 0), (.42, 8), (.9, 6), (1, 0)),
    leftHand=K((0, 0), (.12, 1), (.9, 1), (1, 0))),
    clip=True, fullBody=True, tool=tool(1.8, 'Aquí no hay nada que forzar'))

# Ganzúa: apoya la rodilla derecha frente a la cerradura, la izquierda sostiene la llave de tensión, la derecha tantea
# y al final gira.
add('ganzua', 'tool', 2.0, .88, dict(
    side=K((0, 0), (.2, -.06), (.85, -.06), (1, 0)),
    up=K((0, 0), (.2, .3), (.85, .3), (1, 0)),
    forward=K((0, 0), (.2, .16), (.85, .16), (1, 0)),
    pitch=K((0, 0), (.2, -10), (.85, -10), (1, 0)),
    roll=K((0, 0), (.3, 0), (.38, 12), (.46, -10), (.54, 12), (.62, -8), (.7, 10), (.78, -6), (.86, 0), (.9, 35), (1, 0)),
    leanForward=K((0, 0), (.2, 10), (.88, 10), (1, 0)),
    crouch=K((0, 0), (.2, .4), (.88, .4), (1, 0)),
    kneel=K((0, 0), (.2, 1), (.88, 1), (1, 0)),
    headPitch=K((0, 0), (.2, 10), (.88, 10), (1, 0)),
    leftHand=K((0, 0), (.2, 1), (.88, 1), (1, 0))), shake=.002,
    clip=True, fullBody=True, tool=tool(1.4, 'No hay ninguna cerradura cerca'))

# Taladro: lo sujeta con las dos manos, se apoya con el cuerpo y empuja mientras vibra y gira la broca.
add('taladro', 'tool', .5, .9, dict(
    forward=K((0, .04), (1, .04)), up=K((0, .05), (1, .05)), pitch=K((0, -4), (1, -4)),
    leanForward=K((0, 10), (1, 10)), crouch=K((0, .06), (1, .06)), step=K((0, .15), (1, .15)), headPitch=K((0, 6), (1, 6)),
    leftHand=K((0, 1), (1, 1))),
    repeat=True, shake=.007, spin='Bit', spinSpeed=2000,
    clip=True, fullBody=True, tool=tool(1.6, 'No hay nada que perforar'))

# Cortavidrios: inclinado sobre la vitrina, la izquierda sujeta la ventosa y la derecha traza un círculo.
add('cortavidrios', 'tool', 2.0, .8, dict(
    side=K((0, 0), (.2, 0), (.3, 0), (.4, .07), (.5, 0), (.6, -.07), (.7, 0), (.9, 0), (1, 0)),
    up=K((0, 0), (.2, .1), (.9, .1), (1, 0)),
    forward=K((0, 0), (.2, .26), (.3, .33), (.4, .26), (.5, .19), (.6, .26), (.7, .33), (.8, .26), (.9, .26), (1, 0)),
    pitch=K((0, 0), (.2, 80), (.9, 80), (1, 0)),
    leanForward=K((0, 0), (.2, 20), (.9, 20), (1, 0)),
    crouch=K((0, 0), (.2, .03), (.9, .03), (1, 0)),
    step=K((0, 0), (.2, .12), (.9, .12), (1, 0)),
    headPitch=K((0, 0), (.2, 25), (.9, 25), (1, 0)),
    leftHand=K((0, 0), (.2, 1), (.9, 1), (1, 0))),
    clip=True, fullBody=True, tool=tool(1.5, 'No hay vidrio que cortar'))

# Tablet: la acerca a la cara, mira la pantalla, teclea (vibración fina) y las líneas de código parpadean. Se puede caminar.
add('hackeo', 'tool', 2.0, .85, dict(
    up=K((0, 0), (.25, .14), (.9, .14), (1, 0)), forward=K((0, 0), (.25, -.04), (.9, -.04), (1, 0)),
    pitch=K((0, 0), (.25, -18), (.9, -18), (1, 0)), leanForward=K((0, 0), (.25, 6), (.9, 6), (1, 0)),
    headPitch=K((0, 0), (.25, 22), (.9, 22), (1, 0))),
    shake=.0025, blink='Code', clip=True,
    tool=tool(8, 'No hay cámaras ni puertas electrónicas a la vista'))

# Bridas: amarre por detrás de una persona arrodillada con las manos en la espalda (la pose del rehén es de Task 13).
# Apoya la rodilla derecha detrás de ella, la izquierda le junta las muñecas, la derecha pasa el lazo alrededor, tira
# fuerte para cerrarlo (momento del efecto) y se levanta. Solo empieza si hay alguien a quien amarrar al frente.
add('bridas', 'tool', 2.2, .72, dict(
    side=K((0, 0), (.25, -.17), (.35, -.12), (.42, -.17), (.49, -.22), (.56, -.17), (.64, -.17), (.72, -.02), (.82, -.04), (1, 0)),
    up=K((0, 0), (.25, 0), (.35, .05), (.42, .1), (.49, .05), (.56, 0), (.64, 0), (.72, .14), (.82, .1), (1, 0)),
    forward=K((0, 0), (.25, .18), (.64, .18), (.72, .12), (.82, .1), (1, 0)),
    roll=K((0, 0), (.64, 0), (.72, -45), (.82, -30), (1, 0)),
    leanForward=K((0, 0), (.18, 26), (.86, 26), (1, 0)),
    crouch=K((0, 0), (.18, .4), (.86, .4), (1, 0)),
    kneel=K((0, 0), (.18, 1), (.86, 1), (1, 0)),
    step=K((0, 0), (.18, -.12), (.86, -.12), (1, 0)),  # el pie adelantado no pisa los pies del rehén
    headPitch=K((0, 0), (.18, 30), (.86, 30), (1, 0)),
    leftSide=K((0, -.2), (.2, -.03), (.82, -.03), (1, -.2)),
    leftUp=K((0, -.42), (.2, -.32), (.82, -.32), (1, -.42)),
    leftForward=K((0, .05), (.2, .4), (.82, .4), (1, .05))),
    clip=True, fullBody=True, partner='rehen',
    tool=tool(1.4, 'No hay nadie a quien amarrar', consume=True, requireTarget=True))

# Gancho: la izquierda lleva la cuerda, lo hace girar al costado, flexiona las rodillas y lo lanza mirando la azotea.
add('gancho', 'tool', 1.8, .72, dict(
    side=K((0, 0), (.15, .08), (.6, .08), (.8, 0), (1, 0)),
    up=K((0, 0), (.15, .45), (.26, .25), (.38, .05), (.49, .25), (.6, .45), (.66, .55), (.72, .6), (.85, .3), (1, 0)),
    forward=K((0, 0), (.15, 0), (.26, .2), (.38, 0), (.49, -.2), (.6, 0), (.66, .28), (.72, .36), (.85, .15), (1, 0)),
    pitch=K((0, 0), (.15, -60), (.6, -60), (.7, -110), (1, 0)),
    leanForward=K((0, 0), (.6, -8), (.72, 12), (1, 0)),
    leanTwist=K((0, 0), (.15, 15), (.6, 15), (.72, -15), (1, 0)),
    crouch=K((0, 0), (.5, .03), (.62, .09), (.72, 0), (1, 0)),
    step=K((0, 0), (.55, 0), (.72, .25), (.9, .25), (1, 0)),
    headPitch=K((0, 0), (.15, -10), (.6, -15), (.72, -30), (.85, -25), (1, 0)),
    leftHand=K((0, 0), (.1, 1), (.6, 1), (.68, 0), (1, 0))),
    clip=True, fullBody=True, tool=tool(18, 'No hay dónde enganchar el gancho', rope=True))


# Granadas: la izquierda saca la anilla y luego apunta al frente, el brazo va atrás con el torso girado y la lanza.
# Solo torso: se puede lanzar caminando.
def grenade(id, kind):
    add(id, 'throw', 1.1, .6, dict(
        side=K((0, 0), (.12, -.1), (.22, -.08), (.45, .12), (.55, .05), (.65, -.05), (1, 0)),
        up=K((0, 0), (.12, .25), (.22, .27), (.45, .45), (.55, .38), (.65, .15), (.8, 0), (1, 0)),
        forward=K((0, 0), (.12, .1), (.22, .12), (.45, -.3), (.55, .1), (.62, .32), (.75, .18), (1, 0)),
        pitch=K((0, 0), (.12, -10), (.22, -10), (.45, -80), (.55, -20), (.62, 40), (.75, 10), (1, 0)),
        leanTwist=K((0, 0), (.22, 0), (.45, 35), (.55, 10), (.65, -25), (.8, -10), (1, 0)),
        leanForward=K((0, 0), (.12, 4), (.22, 4), (.45, -10), (.55, 5), (.65, 18), (.8, 6), (1, 0)),
        headPitch=K((0, 0), (.12, 12), (.22, 10), (.45, -8), (.65, -4), (1, 0)),
        leftSide=K((0, -.15), (.32, -.12), (.55, -.1), (.65, -.22), (1, -.2)),
        leftUp=K((0, 0), (.32, .04), (.55, .06), (.65, -.3), (1, -.42)),
        leftForward=K((0, .2), (.32, .42), (.55, .45), (.65, .05), (1, .08)),
        leftHand=K((0, 0), (.1, 1), (.22, 1), (.32, 0), (1, 0))),
        clip=True, noise=30 if kind == 'Flash' else 0, thrown=dict(kind=kind, speed=13, fuse=1.6 if kind == 'Smoke' else 1.2, radius=8 if kind == 'Emp' else 6))


grenade('humo', 'Smoke')
grenade('aturdidora', 'Flash')
grenade('emp', 'Emp')

# Termita: apoya la rodilla derecha frente a la puerta, la aprieta contra ella con las dos manos y se levanta.
add('termita', 'charge', 1.6, .5, dict(
    up=K((0, 0), (.3, -.02), (.5, -.05), (.7, -.03), (1, 0)),
    forward=K((0, 0), (.3, .1), (.5, .16), (.7, .12), (1, 0)),
    leanForward=K((0, 0), (.3, 15), (.5, 22), (.7, 18), (.9, 6), (1, 0)),
    crouch=K((0, 0), (.3, .4), (.7, .4), (.9, .08), (1, 0)),
    kneel=K((0, 0), (.3, 1), (.7, 1), (.9, .15), (1, 0)),
    headPitch=K((0, 0), (.3, 20), (.62, 20), (1, 0))),
    clip=True, fullBody=True, charge=dict(reach=2, fuse=3, burn=6))

# Número de cada clip en el parámetro «Accion» del Animator (1, 2, 3… en el orden de este archivo; 0 = sin clip).
for number, entry in enumerate((e for e in ACTIONS if e['clip']), start=1):
    entry['animationId'] = number

if __name__ == '__main__':
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(version=VERSION, actions=ACTIONS), indent=1, ensure_ascii=False), encoding='utf-8')
    print('acciones', len(ACTIONS), '->', OUT)
