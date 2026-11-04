"""Hoja de revisión con todos los trajes de los packs modulares, de frente y de espalda, para elegir piezas.
Uso: blender -b --factory-startup -P part_sheet.py
Salida: renders/piezas_<pack>_<vista>.png
"""
import bpy, math
from pathlib import Path
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
PACKS = HERE.parent.parent / 'ThirdParty~' / 'Quaternius_Modular'
MASTER = {'Men': PACKS / 'Men' / 'Ultimate Modular Men- Feb 2022' / 'All together' / 'Blends' / 'Humans_Master.blend',
          'Women': PACKS / 'Women' / 'Ultimate Modular Women - April 2022' / 'All together' / 'Blends' / 'All together.blend'}
SLOTS = ('Head', 'Body', 'Legs', 'Pants', 'Feet')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light, scene.display.shading.color_type = 'STUDIO', 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 2600, 900
scene.world = bpy.data.worlds.new('Fondo')
scene.world.color = (.78, .79, .81)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
scene.collection.objects.link(cam)
cam.data.type = 'ORTHO'
scene.camera = cam
for key, path in MASTER.items():
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = list(src.objects)
    collection = bpy.data.collections.new(key)
    scene.collection.children.link(collection)
    for o in dst.objects:
        if o:
            collection.objects.link(o)
    meshes = [o for o in dst.objects if o and o.type == 'MESH' and '_' in o.name and o.name.split('_')[-1].split('.')[0] in SLOTS]
    outfits = sorted({o.name.split('_')[0] for o in meshes})
    for o in dst.objects:
        if o and o.type == 'MESH':
            o.hide_render = o not in meshes
            o.hide_set(False)
            for m in o.modifiers:
                if m.type == 'ARMATURE':
                    m.show_render = m.show_viewport = False
    for i, outfit in enumerate(outfits):
        x = (i - (len(outfits) - 1) / 2) * .95
        for o in meshes:
            if o.name.split('_')[0] == outfit:
                o.matrix_world = Matrix.Translation((x, 0, 0)) @ o.matrix_world
        label = bpy.data.curves.new('L', 'FONT')
        label.body, label.size, label.align_x = outfit, .09, 'CENTER'
        text = bpy.data.objects.new('L_' + outfit, label)
        collection.objects.link(text)
        text.location = (x, -.3, 2.05)
        text.rotation_euler = (math.radians(90), 0, 0)
    for o in scene.collection.children:
        o.hide_render = o is not collection
    cam.data.ortho_scale = len(outfits) * .95 + .4
    for view, location, rotation in (('frente', (0, -10, 1.0), (90, 0, 0)), ('espalda', (0, 10, 1.0), (90, 0, 180))):
        cam.location, cam.rotation_euler = location, tuple(math.radians(a) for a in rotation)
        scene.render.filepath = str(HERE / 'renders' / f'piezas_{key}_{view}.png')
        bpy.ops.render.render(write_still=True)
