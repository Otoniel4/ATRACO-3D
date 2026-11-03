"""Cabeza low poly sencilla sobre el cuerpo propio de Alarma. Blender 4.5/5.x.
Uso: blender -b --python-exit-code 1 -P build_lowpoly_head.py
En Blender conectado puede llamarse main(save=False), sin guardar el archivo abierto.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Euler

# 1. MEDIDAS EDITABLES, en metros. Frente -Y; altura total conservada.
HEIGHT=1.65
HEAD_CENTER=(0,-.015,1.445)
HEAD_SIZE=(.205,.165,.225)
HEAD_BEVEL=.040
HEAD_BEVEL_SEGMENTS=2
HEAD_BOTTOM_TAPER=.92
NECK_CUT_Z=1.310
NECK_TOP_Z=1.350
EYE_X=.044
EYE_Z=1.465
EYE_SIZE=(.011,.014)
FACE_Y=-.099
MOUTH_Z=1.405
INK_HEX='241C1A'
SCENE_NAME='Female_LowPoly'
BASE=Path(__file__).resolve().parent

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.context.view_layer.objects.active=obj

def flat(obj):
    for face in obj.data.polygons:face.use_smooth=False

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
    data.materials.append(mat);flat(obj);return obj

def material(name,color):
    values=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values)+(1,)
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=rgba
    node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value=rgba;node.inputs['Roughness'].default_value=.85
    return mat

def bevel_box(name,center,size,bevel,mat,segments=1):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    obj=bpy.context.object;obj.name=name;obj.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=obj.modifiers.new('Bevel low poly','BEVEL');mod.width=bevel;mod.segments=segments
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat);flat(obj);return obj

def ico(name,center,size,mat,level=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=level,radius=1,location=center)
    obj=bpy.context.object;obj.name=name;obj.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat);flat(obj);return obj

def join(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    obj=objects[0];obj.name=name
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    flat(obj);return obj

def rigid_head(obj,rig):
    # Las piezas gráficas siguen Head sin deformación blanda de la cara.
    for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
    obj.vertex_groups.new(name='Head').add(list(range(len(obj.data.vertices))),1,'REPLACE')
    obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted()
    mod=next((m for m in obj.modifiers if m.type=='ARMATURE'),None)
    if mod is None:mod=obj.modifiers.new('Humanoid Head','ARMATURE')
    mod.object=rig

def replace_old_head(body):
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>NECK_CUT_Z],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    edges=[e for e in bm.edges if e.is_boundary]
    boundary={v for e in edges for v in e.verts}
    if not boundary:raise RuntimeError('No se encontró la unión del cuello')
    for vertex in boundary:vertex.co.z=NECK_TOP_Z
    bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if any(not e.is_manifold for e in bm.edges):raise RuntimeError('El cuerpo debe seguir cerrado')
    bm.to_mesh(body.data);bm.free();body.data.update()

def make_head(skin,ink,cream,hair_mat,rig):
    head=bevel_box('LP_HeadCore',HEAD_CENTER,HEAD_SIZE,HEAD_BEVEL,skin,HEAD_BEVEL_SEGMENTS)
    for vertex in head.data.vertices:
        t=max(0,min(1,(vertex.co.z+HEAD_SIZE[2]/2)/(HEAD_SIZE[2]/2)))
        vertex.co.x*=HEAD_BOTTOM_TAPER+(1-HEAD_BOTTOM_TAPER)*t
    ears=[bevel_box('LP_Ear',(side*.108,0,1.438),(.025,.024,.043),.008,skin) for side in [-1,1]]
    head=join('LP_Head',[head]+ears);rigid_head(head,rig)
    face=[]
    for side in [-1,1]:
        x=side*EYE_X
        verts=[(x+EYE_SIZE[0]*math.cos(2*math.pi*i/8),FACE_Y-.001,EYE_Z+EYE_SIZE[1]*math.sin(2*math.pi*i/8)) for i in range(8)]
        face.append(mesh('LP_Eye',verts,[tuple(range(8))],ink))
        face.append(ico('LP_EyeGlint',(x-.003,FACE_Y-.0028,EYE_Z+.004),(.0028,.0018,.0028),cream))
        face.append(mesh('LP_Brow',[(x-.015,FACE_Y-.001,1.492),(x+.015,FACE_Y-.001,1.492),(x+.014,FACE_Y-.001,1.496),(x-.014,FACE_Y-.001,1.496)],[(0,1,2,3)],hair_mat))
    nose=[(-.009,FACE_Y,1.422),(.009,FACE_Y,1.422),(.009,FACE_Y,1.447),(-.009,FACE_Y,1.447),(0,FACE_Y-.016,1.428)]
    face.append(mesh('LP_Nose',nose,[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],skin))
    # Sonrisa gráfica de cuatro tramos, sin labios ni detalle anatómico.
    points=[(-.020,MOUTH_Z+.004),(-.010,MOUTH_Z),(0,MOUTH_Z-.001),(.010,MOUTH_Z),(.020,MOUTH_Z+.004)]
    verts=[]
    for x,z in points:verts.extend([(x,FACE_Y-.002,z-.0012),(x,FACE_Y-.002,z+.0012)])
    face.append(mesh('LP_Smile',verts,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(4)],ink))
    face=join('LP_Face',face);rigid_head(face,rig)
    # Pelo compuesto de masas facetadas, sin casco liso ni mechones finos.
    parts=[bevel_box('LP_HairCap',(0,.002,1.542),(.214,.180,.078),.035,hair_mat)]
    for i in range(10):
        a=2*math.pi*i/10
        parts.append(ico('LP_Curl',(math.cos(a)*.078,.005+math.sin(a)*.060,1.558+.006*math.cos(3*a)),(.034,.031,.032),hair_mat))
    bun=ico('LP_HighBun',(0,.030,1.610),(.057,.052,.041),hair_mat,2)
    high=max((bun.matrix_world@v.co).z for v in bun.data.vertices)
    bun.location.z+=HEIGHT-high;parts.append(bun)
    hair=join('LP_Hair',parts);rigid_head(hair,rig)
    return head,face,hair

def render_views(scene,camera):
    folder=BASE/'renders';folder.mkdir(exist_ok=True)
    for name,eye,center,scale,size in [
        ('head_front',(0,-6,0),(0,-.005,1.455),.43,(600,700)),
        ('head_side',(-6,0,0),(0,-.005,1.455),.43,(600,700)),
        ('head_three_quarter',(-4,-6,0),(0,-.005,1.455),.43,(600,700)),
        ('full_front',(0,-6,0),(0,0,.825),1.77,(600,950)),
        ('full_back',(0,6,0),(0,0,.825),1.77,(600,950))]:
        center=Vector(center);camera.location=center+Vector(eye)
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=size
        scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)

def frame_head(scene):
    # Dejar tanto la cámara del panel como el viewport mirando la cara.
    center=Vector((0,-.005,1.455));camera=scene.camera
    camera.location=center+Vector((-4,-6,0))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=.43;scene.render.resolution_x=600;scene.render.resolution_y=700
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.region_3d.view_location=center
                space.region_3d.view_distance=.47
                space.region_3d.view_rotation=(center-camera.location).to_track_quat('-Z','Y')
                allowed={i.identifier for i in space.region_3d.bl_rna.properties['view_perspective'].enum_items}
                if 'ORTHO' in allowed:space.region_3d.view_perspective='ORTHO'
                space.overlay.show_extras=False

def main(save=True):
    if bpy.data.scenes.get(SCENE_NAME):raise RuntimeError('Esta revisión ya existe; conservar la escena actual')
    with bpy.data.libraries.load(str(BASE/'baseline'/'character.blend'),link=False) as (src,dst):dst.scenes=['Character_Blockout_4x']
    scene=dst.scenes[0];scene.name=SCENE_NAME;bpy.context.window.scene=scene
    roles={o.name.split('.')[0]:o for o in scene.objects}
    body=roles['Body'];rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.name='LP_Armature'
    skin=body.data.materials[0];hair_mat=roles['Hair'].data.materials[0]
    cream=next(m for m in roles['Shoes'].data.materials if 'Cream' in m.name)
    ink=material('LP_Ink',INK_HEX)
    bpy.data.objects.remove(roles['Hair'],do_unlink=True)
    for role in ['Body','Jacket','Top','Pants','Shoes','Earrings']:roles[role].name='LP_'+role
    replace_old_head(body)
    head,face,hair=make_head(skin,ink,cream,hair_mat,rig)
    earrings=roles['Earrings']
    for v in earrings.data.vertices:v.co.x+=.014 if v.co.x>0 else -.014;v.co.z+=.041
    rigid_head(earrings,rig)
    parts=[roles[r] for r in ['Body','Jacket','Top','Pants','Shoes','Earrings']]+[head,face,hair]
    for obj in scene.objects:
        if obj.type=='EMPTY' or obj.name.startswith('SOURCE_'):
            obj.hide_set(True);obj.hide_render=True
    rig.hide_set(True)
    scene.render.film_transparent=False
    background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    background.inputs['Color'].default_value=(.16,.18,.20,1);background.inputs['Strength'].default_value=.5
    if save:
        render_views(scene,scene.camera)
        rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT')
        for obj in parts+[rig]:obj.select_set(True)
        bpy.context.view_layer.objects.active=rig
        export=BASE/'export';export.mkdir(exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=str(export/'character_lowpoly.fbx'),use_selection=True,
            object_types={'MESH','ARMATURE'},apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            bake_space_transform=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
        rig.hide_set(True);activate(head);frame_head(scene)
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'character_lowpoly.blend'),copy=True)
        report={'blender_version':bpy.app.version_string,'scene':SCENE_NAME,'height_m':HEIGHT,
            'objects':{o.name:{'vertices':len(o.data.vertices),'faces':len(o.data.polygons),
                'triangles':sum(len(f.vertices)-2 for f in o.data.polygons)} for o in parts},
            'bones':len(rig.data.bones),'head_rigid_weight_bone':'Head','unity_avatar_verified':False}
        (BASE/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('LOWPOLY_HEAD_READY',scene.name)
    return scene

if __name__=='__main__':main()
