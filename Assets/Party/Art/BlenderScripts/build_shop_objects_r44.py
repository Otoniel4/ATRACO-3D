"""Lote propio de revisión: 18 objetos, metros, FBX y anclas; no modifica escenas de Unity."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent/'ShopObjectsR44~'
OUT.mkdir(exist_ok=True)
scene=bpy.data.scenes.new('R44_Objetos');bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
materials={}
def mat(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new('R44_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
    materials[name]=m;return m
for n,c,m,r in [('cream',(.88,.82,.65),0,.7),('red',(.65,.06,.025),0,.5),('green',(.07,.27,.12),0,.5),('blue',(.035,.17,.32),0,.4),('gold',(.75,.43,.08),.8,.23),('steel',(.5,.57,.63),.8,.25),('dark',(.035,.045,.05),0,.55),('leather',(.2,.07,.028),0,.6),('white',(.9,.93,.9),0,.45),('bread',(.66,.31,.07),0,.7),('cheese',(.97,.57,.035),0,.55),('salad',(.15,.48,.06),0,.6),('meat',(.16,.035,.015),0,.8),('gem',(.05,.54,.62),.45,.14)]:mat(n,c,m,r)
root=None
def finish(o,name,color):
    o.name=name;o.data.materials.append(materials[color]);o.parent=root
    return o
def box(name,p,s,color,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Bordes','BEVEL');mod.width=bevel;mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,name,color)
def lathe(name,profile,color,segments=32):
    verts=[(r*math.cos(2*math.pi*i/segments),r*math.sin(2*math.pi*i/segments),z) for z,r in profile for i in range(segments)]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);return finish(o,name,color)
def cyl(name,p,r,h,color):
    o=lathe(name,[(0,r),(h,r)],color);o.location=p;return o
def ring(name,p,major,minor,color,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=p,rotation=rotation)
    return finish(bpy.context.object,name,color)
def line(name,points,r,color):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for v,p in zip(s.points,points):v.co=(*p,1)
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);finish(o,name,color)
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def text(label,p,size=.018,color='white',rotation=(math.pi/2,0,0)):
    c=bpy.data.curves.new('Etiqueta','FONT');c.body=label;c.align_x='CENTER';c.size=size;c.extrude=.00025
    o=bpy.data.objects.new('Texto_'+label,c);scene.collection.objects.link(o);o.location=p;o.rotation_euler=rotation;finish(o,o.name,color)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False)
def bottle():
    lathe('Botella_hombros',[(0,.028),(.012,.035),(.19,.035),(.225,.016),(.265,.016)],'green')
    cyl('Tapa',(0,0,.262),.018,.025,'gold')
    for z in [.267,.274,.281]:ring('Estrias_tapa',(0,0,z),.018,.001,'gold')
    box('Etiqueta',(0,-.034,.13),(.047,.002,.085),'cream',.001);text('RESERVA',(0,-.036,.15),.008,'dark');text('ALMA',(0,-.036,.12),.014,'red')
def milk():
    box('Carton',(0,0,.105),(.075,.075,.21),'white');roof=box('Techo_plegado',(0,0,.222),(.075,.054,.037),'blue');roof.rotation_euler.x=.2
    box('Costura_superior',(0,0,.247),(.075,.006,.01),'blue',.001)
    cyl('Tapon',(.018,0,.242),.013,.014,'white');box('Banda',(0,-.039,.11),(.068,.003,.105),'blue',.001);text('LECHE',(0,-.042,.13),.014);text('1 L',(0,-.042,.08),.018)
def package(label,color):
    box('Envase',(0,0,.115),(.105,.055,.23),color,.009)
    for z in [.01,.22]:box('Sellado',(0,0,z),(.11,.059,.008),'gold',.001)
    box('Etiqueta',(0,-.029,.12),(.088,.002,.12),'cream',.002);text(label,(0,-.032,.15),.014,'dark');text('ALMA',(0,-.032,.10),.018,'red')
    for i in range(11):box('Codigo_barras',(-.035+i*.006,-.032,.062),(.0015,.001,.017),'dark',0)
def can():
    lathe('Lata',[(0,.027),(.008,.032),(.11,.032),(.12,.027)],'red');cyl('Tapa',(0,0,.12),.028,.003,'steel')
    ring('Borde_superior',(0,0,.122),.028,.0015,'steel');ring('Anilla',(0,-.004,.125),.008,.002,'steel')
    text('COLA',(0,-.033,.066),.018);text('330',(0,-.033,.04),.008)
def oil():
    bottle()
    for o in root.children:
        if o.name.startswith('Texto_'):o.hide_render=True
    text('ACEITE',(0,-.038,.135),.011,'dark');text('OLIVA',(0,-.038,.11),.009,'green')
def jewel():
    ring('Aro',(0,0,.004),.009,.002,'gold')
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=(0,-.009,.012));finish(bpy.context.object,'Piedra_tallada','gem')
    for x in [-.004,.004]:cyl('Garra',(x,-.009,.006),.0007,.009,'gold')
def watch():
    box('Correa',(0,0,.004),(.022,.19,.008),'leather',.004)
    for y in [.05,.06,.07,.08]:cyl('Ojal',(0,y,.008),.0018,.001,'dark')
    cyl('Caja',(0,0,.008),.019,.009,'gold');cyl('Esfera',(0,0,.017),.016,.001,'dark')
    for i in range(12):
        a=2*math.pi*i/12;box('Indice',(math.sin(a)*.013,math.cos(a)*.013,.019),(.001,.002,.0006),'cream',0)
    box('Aguja_minutos',(0,.005,.02),(.0008,.012,.001),'white',0);h=box('Aguja_horas',(.004,0,.021),(.008,.001,.001),'gold',0)
    ring('Hebilla',(0,-.085,.01),.01,.002,'gold')
def necklace():
    for i in range(42):
        a=2*math.pi*i/42;ring('Eslabon',(.065*math.cos(a),.09*math.sin(a),.003),.004,.001,'gold',(0,(i%2)*.65,0))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.012,location=(0,-.097,.012));finish(bpy.context.object,'Colgante','gem')
def bullion():
    o=box('Lingote',(0,0,.018),(.105,.055,.036),'gold',.005)
    text('ALMA',(0,.005,.037),.015,'dark',(0,0,0));text('999.9',(0,-.012,.037),.008,'dark',(0,0,0))
def briefcase():
    box('Maletin',(0,0,.12),(.34,.1,.24),'dark',.015)
    box('Union_tapa',(0,-.051,.12),(.332,.003,.003),'steel',.001)
    for x in [-.105,.105]:box('Cierre',(x,-.054,.125),(.03,.009,.025),'steel')
    line('Asa',[(-.055,0,.24),(-.055,0,.28),(.055,0,.28),(.055,0,.24)],.008,'leather')
    for x in [-.15,.15]:
        for z in [.025,.215]:box('Esquina',(x,-.052,z),(.025,.008,.028),'steel')
def envelope():
    box('Sobre',(0,0,.004),(.22,.12,.008),'cream',.001)
    line('Solapa',[(-.108,.057,.009),(0,-.01,.009),(.108,.057,.009)],.0007,'leather')
    cyl('Sello',(0,-.01,.009),.012,.002,'red');text('CONFIDENCIAL',(0,-.045,.01),.012,'dark',(0,0,0))
def burger():
    lathe('Pan_base',[(0,.035),(.008,.047),(.023,.046)],'bread')
    cyl('Carne',(0,0,.024),.044,.014,'meat');box('Queso',(0,0,.04),(.078,.078,.004),'cheese',.002)
    for i in range(12):a=i*math.pi/6;leaf=box('Lechuga',(.025*math.cos(a),.025*math.sin(a),.045),(.04,.025,.004),'salad');leaf.rotation_euler.z=a
    lathe('Pan_superior',[(.049,.045),(.065,.043),(.078,.03),(.084,.008)],'bread')
    for i in range(16):a=i*2.4;r=.028*math.sqrt((i+1)/16);seed=box('Sesamo',(r*math.cos(a),r*math.sin(a),.079-r*.2),(.004,.0015,.001),'cream',.0005);seed.rotation_euler.z=a
def cup():
    lathe('Vaso',[(0,.027),(.12,.041)],'blue');cyl('Tapa',(0,0,.12),.043,.009,'white');ring('Borde_tapa',(0,0,.127),.041,.002,'white')
    line('Pajita',[(.008,0,.124),(.008,0,.18),(.025,0,.19)],.0025,'red');text('FRIO',(0,-.037,.07),.017)
def pizza():
    box('Caja_base',(0,0,.015),(.25,.25,.03),'cream',.002);box('Tapa',(0,0,.033),(.255,.255,.006),'red',.001)
    text('PIZZA',(0,0,.037),.04,'white',(0,0,0));text('ALMA',(0,-.06,.037),.018,'cream',(0,0,0))
    for x in [-.125,.125]:
        for y in [-.06,0,.06]:box('Ventilacion',(x,y,.016),(.002,.015,.003),'dark',0)
def handbag():
    box('Cuerpo_bolso',(0,0,.105),(.25,.085,.21),'leather',.025)
    for y in [-.028,.028]:line('Asa',[(-.065,y,.2),(-.06,y,.28),(-.035,y,.30),(.035,y,.30),(.06,y,.28),(.065,y,.2)],.006,'leather')
    for x in [-.09,.09]:line('Costura',[(x,-.044,.025),(x,-.044,.19)],.0007,'cream')
    box('Cremallera',(0,0,.214),(.19,.004,.003),'gold',.001);ring('Tirador',(.07,-.003,.22),.006,.0015,'gold',(math.pi/2,0,0));box('Placa',(0,-.045,.14),(.034,.003,.015),'gold')
def shoe():
    box('Suela',(0,0,.012),(.095,.255,.024),'white',.014);box('Empeine',(0,.015,.045),(.087,.215,.06),'blue',.025)
    box('Tobillo',(0,.08,.08),(.083,.07,.05),'blue',.016);box('Abertura',(0,.08,.106),(.055,.047,.002),'dark',.01)
    for y in [-.04,-.02,0,.02,.04]:line('Cordon',[(-.025,y,.078),(.025,y+.01,.078)],.0015,'white')
    for y in [-.1,-.07,-.04,-.01,.02,.05,.08,.11]:box('Dibujo_suela',(0,y,.002),(.075,.004,.003),'dark',.001)
def shirt():
    box('Camiseta_doblada',(0,0,.022),(.24,.29,.044),'green',.01)
    for x in [-.104,.104]:line('Costura',[(x,-.13,.045),(x,.13,.045)],.0007,'cream')
    ring('Cuello',(0,.095,.046),.035,.006,'green');box('Interior_cuello',(0,.095,.045),(.05,.045,.001),'dark',.008)
    text('ALMA',(0,-.02,.046),.027,'cream',(0,0,0));box('Etiqueta_talla',(0,.115,.051),(.015,.01,.002),'white',.001)

items=[('minimarket','BotellaReserva',bottle),('minimarket','Leche',milk),('minimarket','Cafe',lambda:package('CAFE','leather')),('supermercado','LataCola',can),('supermercado','Aceite',oil),('supermercado','Cereal',lambda:package('CEREAL','blue')),('joyeria','Anillo',jewel),('joyeria','Reloj',watch),('joyeria','Collar',necklace),('banco','Lingote',bullion),('banco','Maletin',briefcase),('banco','Sobre',envelope),('comida','Hamburguesa',burger),('comida','Vaso',cup),('comida','Pizza',pizza),('ropa','Bolso',handbag),('ropa','Zapatilla',shoe),('ropa','Camiseta',shirt)]
catalog=[]
for index,(shop,name,build) in enumerate(items):
    root=bpy.data.objects.new('R44_'+name,None);scene.collection.objects.link(root);build()
    meshes=[o for o in root.children_recursive if o.type=='MESH' and not o.hide_render]
    bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);size=hi-lo
    two=name in ['Maletin','Pizza','Camiseta'];gripz=(hi.z+lo.z)*.55
    anchors={'Support':(0,0,lo.z),'Grip_R':(hi.x,0,gripz),'Grip_L':(lo.x,0,gripz)}
    if name in ['Maletin','Bolso']:anchors['Grip_R']=(0,0,hi.z-.006)
    if name in ['Anillo','Reloj','Collar']:anchors['Grip_R']=(0,lo.y,hi.z*.5)
    for key,p in anchors.items():
        o=bpy.data.objects.new(key,None);scene.collection.objects.link(o);o.parent=root;o.location=p;o.empty_display_size=.012
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in root.children_recursive:o.select_set(not o.hide_render)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,add_leaf_bones=False,axis_forward='-Z',axis_up='Y',bake_anim=False)
    catalog.append(dict(id=name,shop=shop,dimensions_m=list(size),two_hands=two,grips_blender=anchors,grips_unity={k:[p[0],p[2],-p[1]] for k,p in anchors.items()},stealable_candidate=True,license='Original Alarma',validated_in_unity=False,fbx=name+'.fbx'))
    # Galería ampliada; FBX permanece a escala real y origen cero.
    scale=.43/max(size);root.scale=(scale,)*3;root.location=((index%3)*.64,(index//3)*.7,0)
    root=None;text(name,((index%3)*.64,(index//3)*.7-.30,.002),.038,'white',(0,0,0))
(OUT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8')
root=None
camera=bpy.data.objects.new('R44_Camera',bpy.data.cameras.new('R44_Camera'));scene.collection.objects.link(camera)
camera.location=(4,-5,7);camera.rotation_euler=(Vector((.64,1.75,.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.2;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=1500;scene.render.resolution_y=1800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Catalogo.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Objetos_Negocios_R44.blend'))
bpy.ops.render.render(write_still=True)
print('R44: 18 FBX y catálogo guardados en',OUT)
