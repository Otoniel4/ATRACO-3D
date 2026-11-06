"""Íconos de la barra rápida: un PNG transparente por arma, herramienta o consumible del jugador.

Importa cada FBX de Art/Weapons (los mismos modelos que se ven en la mano), lo encuadra en una vista de tres cuartos
ortográfica y lo renderiza con colores planos y contorno, igual que el resto del arte.
Uso: blender -b --factory-startup -P build_item_icons.py
Salida: Art/UI/Items/Icon_<modelo>.png y Previews~/iconos_inventario.png (hoja de revisión).
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ART = Path(__file__).resolve().parent.parent
SOURCE, OUT = ART / 'Weapons', ART / 'UI' / 'Items'
# La porra es solo de los guardias (NPC): no va al inventario del jugador.
MODELS = ['Weapon_Pistol', 'Weapon_Shotgun', 'Weapon_Taser', 'Weapon_Rifle', 'Tool_Crowbar', 'Tool_Lockpick', 'Tool_Drill',
          'Tool_GlassCutter', 'Tool_HackingTablet', 'Tool_ThermiteCharge', 'Tool_GrapplingHook', 'Tool_ZipTies',
          'Consumable_Smoke', 'Consumable_Stun', 'Consumable_EMP']
SIZE = 256


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
    scene.display.shading.show_object_outline = True
    scene.display.shading.object_outline_color = (.05, .06, .08)
    scene.display.shading.show_cavity = True
    scene.view_settings.view_transform = 'Standard'
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    scene.render.image_settings.file_format, scene.render.image_settings.color_mode = 'PNG', 'RGBA'
    cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
    scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    scene.camera = cam
    return scene, cam


def render(scene, cam, model):
    for o in list(bpy.data.objects):
        if o is not cam:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=str(SOURCE / f'{model}.fbx'))
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center, extent = (lo + hi) / 2, max((hi - lo).length, .05)
    # Tres cuartos desde la derecha y algo arriba: las armas (largas en Y) se ven de perfil.
    direction = Vector((1.0, -.35, .45)).normalized()
    cam.location = center + direction * extent * 3
    cam.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = extent * 1.08
    scene.render.filepath = str(OUT / f'Icon_{model}.png')
    bpy.ops.render.render(write_still=True)


def contact_sheet():
    # Hoja de revisión: todos los íconos en una cuadrícula sobre gris oscuro, como se verán en la barra.
    cols = 5
    rows = math.ceil(len(MODELS) / cols)
    sheet = bpy.data.images.new('Hoja', cols * SIZE, rows * SIZE, alpha=True)
    pixels = [.12, .14, .17, 1.0] * (cols * SIZE * rows * SIZE)
    for i, model in enumerate(MODELS):
        icon = bpy.data.images.load(str(OUT / f'Icon_{model}.png'))
        src = list(icon.pixels)
        ox, oy = (i % cols) * SIZE, (rows - 1 - i // cols) * SIZE
        for y in range(SIZE):
            for x in range(SIZE):
                s = (y * SIZE + x) * 4
                a = src[s + 3]
                if a <= 0:
                    continue
                d = ((oy + y) * cols * SIZE + ox + x) * 4
                for c in range(3):
                    pixels[d + c] = pixels[d + c] * (1 - a) + src[s + c] * a
    sheet.pixels = pixels
    sheet.filepath_raw = str(ART / 'Previews~' / 'iconos_inventario.png')
    sheet.file_format = 'PNG'
    sheet.save()


OUT.mkdir(parents=True, exist_ok=True)
scene, cam = setup()
for model in MODELS:
    render(scene, cam, model)
contact_sheet()
print('ICONOS', len(MODELS))
