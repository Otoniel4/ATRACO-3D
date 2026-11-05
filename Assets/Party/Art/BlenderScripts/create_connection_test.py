"""Task 03: cubo de un metro, captura y FBX sin contenido descargado."""
import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for directory in (ROOT / "BlenderSources~", ROOT / "Validation", ROOT / "BlenderScripts"):
    directory.mkdir(exist_ok=True)
scene = bpy.context.scene
if not scene.name.startswith("Alarma_"):
    raise RuntimeError("La conexión no apunta a la sesión de trabajo Alarma; no modificar otra escena")
for item in list(scene.objects):
    bpy.data.objects.remove(item, do_unlink=True)
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

def material(name, color):
    value = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1.0)
    value.use_nodes = True
    shader = next((node for node in value.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if shader is None:
        shader = value.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    output = next((node for node in value.node_tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
    if output is None:
        output = value.node_tree.nodes.new("ShaderNodeOutputMaterial")
    value.node_tree.links.new(shader.outputs[0], output.inputs[0])
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = 0.75
    return value

clay = material("Alarma_Apricot", (0.89, 0.36, 0.13))
cream = material("Alarma_Cream", (0.80, 0.72, 0.55))
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
cube = bpy.context.object
cube.name = "Alarma_ConnectionCube_1m"
cube.data.materials.append(clay)
bevel = cube.modifiers.new("Soft low-poly edges", "BEVEL")
bevel.width = 0.035
bevel.segments = 1
bpy.ops.object.modifier_apply(modifier=bevel.name)
bpy.context.view_layer.update()
assert all(abs(size - 1.0) < 0.001 for size in cube.dimensions)

bpy.ops.export_scene.fbx(filepath=str(ROOT / "Validation/ConnectionCube_1m.fbx"), use_selection=True, object_types={"MESH"}, global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", use_mesh_modifiers=True, axis_forward="-Z", axis_up="Y", bake_anim=False, add_leaf_bones=False)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.015))
floor = bpy.context.object
floor.name = "StudioFloor"
floor.data.materials.append(cream)
floor.hide_select = True
camera_data = bpy.data.cameras.new("StudioCamera")
camera = bpy.data.objects.new("StudioCamera", camera_data)
scene.collection.objects.link(camera)
camera.location = (3.2, -4.2, 3.0)
camera.rotation_euler = (Vector((0, 0, 0.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 3.0
scene.camera = camera
light_data = bpy.data.lights.new("StudioKey", "AREA")
light = bpy.data.objects.new("StudioKey", light_data)
scene.collection.objects.link(light)
light.location = (1, -3, 5)
light.rotation_euler = (Vector((0, 0, 0.3)) - light.location).to_track_quat("-Z", "Y").to_euler()
light_data.energy = 500
light_data.shape = "DISK"
light_data.size = 4
scene.world = scene.world or bpy.data.worlds.new("Alarma_StudioWorld")
scene.world.use_nodes = True
background = next((node for node in scene.world.node_tree.nodes if node.type == "BACKGROUND"), None)
if background is None:
    background = scene.world.node_tree.nodes.new("ShaderNodeBackground")
    world_output = scene.world.node_tree.nodes.new("ShaderNodeOutputWorld")
    scene.world.node_tree.links.new(background.outputs[0], world_output.inputs[0])
background.inputs["Color"].default_value = (0.55, 0.65, 0.8, 1)
background.inputs["Strength"].default_value = 0.5
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1000
scene.render.resolution_y = 750
scene.render.resolution_percentage = 100

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.shading.color_type = "MATERIAL"
            area.spaces.active.region_3d.view_perspective = "CAMERA"

bpy.ops.object.select_all(action="DESELECT")
cube.select_set(True)
bpy.context.view_layer.objects.active = cube
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "BlenderSources~/ConnectionTest.blend"))
print("CONNECTION_TEST_CREATED", cube.name, "dimensions_m", tuple(cube.dimensions), "fbx", str(ROOT / "Validation/ConnectionCube_1m.fbx"))
