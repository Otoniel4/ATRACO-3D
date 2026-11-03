"""Manos propias low poly, con cinco dedos y cadenas deformantes. Conserva el cuerpo R3 fuera de las muñecas."""
import bpy,bmesh,math
from mathutils import Vector,Matrix

def replace_hands(scene,rig,identifier):
    bpy.context.window.scene=scene;rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    body=next(o for o in scene.objects if o.type=='MESH' and '_Body' in o.name)
    skin=next((m for m in body.data.materials if m and any(x in m.name.lower() for x in ['skin','piel'])),body.data.materials[0])
    allverts=[];allfaces=[];allweights=[];bones=[];audit=[]
    for side,sign in [('Left',1),('Right',-1)]:
        hand=rig.data.bones[side+'Hand'];origin=hand.head_local.copy();d=(hand.tail_local-origin).normalized()
        u=Vector((sign*abs(d.z),0,abs(d.x))).normalized();n=Vector((0,-1,0));scale=hand.length/.078
        width=.070*scale;length=.075*scale;thickness=.026*scale
        def world(x,y,z):return origin+u*x+d*y+n*z
        # Retira exclusivamente el extremo antiguo de piel; no corta mangas ni antebrazos.
        bm=bmesh.new();bm.from_mesh(body.data);deform=bm.verts.layers.deform.verify();group=body.vertex_groups.get(side+'Hand')
        remove=[]
        for v in bm.verts:
            p=rig.matrix_world.inverted()@(body.matrix_world@v.co)
            if group and v[deform].get(group.index,0)>.35 and (p-origin).dot(d)>.007*scale:remove.append(v)
        bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(body.data);bm.free()
        v=[];f=[];w=[]
        def vertex(p,weight):v.append(tuple(p));w.append(weight);return len(v)-1
        # Palma cuadriculada; cuatro aberturas distales comparten sus vértices con los dedos.
        grid={}
        for j,(y,factor) in enumerate([(-.009*scale,.65),(.038*scale,1),(length,.94)]):
            for i in range(5):
                for k in range(2):grid[i,j,k]=vertex(world((i/4-.5)*width*factor,y,(-.5+k)*thickness),{side+'Hand':1})
        for j in range(2):
            for i in range(4):
                f.append([grid[i,j,1],grid[i+1,j,1],grid[i+1,j+1,1],grid[i,j+1,1]])
                f.append([grid[i,j,0],grid[i,j+1,0],grid[i+1,j+1,0],grid[i+1,j,0]])
            for i in [0,4]:
                if i==0 and j==1:continue # abertura del pulgar
                f.append([grid[i,j,0],grid[i,j,1],grid[i,j+1,1],grid[i,j+1,0]])
        f.append([grid[i,0,k] for k,indices in [(0,range(4,-1,-1)),(1,range(5))] for i in indices])
        def extrude(loop,centres,radii,names):
            previous=loop
            start=sum((Vector(v[i]) for i in loop),Vector())/4
            axis=(centres[-1]-start).normalized();across=u-axis*u.dot(axis);across.normalize();normal=axis.cross(across).normalized()
            for index,(centre,radius) in enumerate(zip(centres,radii)):
                ring=[vertex(centre+across*x*radius+normal*z*radius*.72,{names[min(index,2)]:1}) for x,z in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                # Alinea las esquinas por proximidad para evitar torsión entre anillos.
                if index==0:
                    options=[loop[i:]+loop[:i] for i in range(4)]+[list(reversed(loop))[i:]+list(reversed(loop))[:i] for i in range(4)]
                    previous=min(options,key=lambda q:sum((Vector(v[q[k]])-Vector(v[ring[k]])).length_squared for k in range(4)))
                for k in range(4):f.append([previous[k],previous[(k+1)%4],ring[(k+1)%4],ring[k]])
                previous=ring
            f.append(previous[:])
        for i,(name,fingerlength) in enumerate(zip(['Index','Middle','Ring','Little'],[.062,.071,.065,.050])):
            x=(i/4+.125-.5)*width*.94;start=world(x,length,0);end=world(x+(i-1.5)*.004*scale,length+fingerlength*scale,0)
            chain=[start,start.lerp(end,.42),start.lerp(end,.75),end];names=[side+name+s for s in ['Proximal','Intermediate','Distal']]
            for j in range(3):bones.append((names[j],chain[j],chain[j+1],side+'Hand' if j==0 else names[j-1],n))
            loop=[grid[i,2,0],grid[i+1,2,0],grid[i+1,2,1],grid[i,2,1]]
            extrude(loop,chain[1:],[.0082*scale,.0073*scale,.0058*scale],names)
        thumbstart=world(-width*.48,length*.70,0);thumbend=world(-width*.98,length*.95,.012*scale)
        chain=[thumbstart,thumbstart.lerp(thumbend,.38),thumbstart.lerp(thumbend,.72),thumbend];names=[side+'Thumb'+s for s in ['Proximal','Intermediate','Distal']]
        for j in range(3):bones.append((names[j],chain[j],chain[j+1],side+'Hand' if j==0 else names[j-1],n))
        extrude([grid[0,1,0],grid[0,1,1],grid[0,2,1],grid[0,2,0]],chain[1:],[.010*scale,.0088*scale,.0065*scale],names)
        offset=len(allverts);allverts+=v;allfaces += [[index+offset for index in face] for face in f];allweights+=w
        audit.append({'side':side,'fingers':5,'length_m':length+.071*scale,'removed_old_vertices':len(remove)})
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for name,head,tail,parent,normal in bones:
        bone=rig.data.edit_bones.new(name);bone.head=head;bone.tail=tail;bone.parent=rig.data.edit_bones[parent];bone.align_roll(normal)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh=bpy.data.meshes.new(identifier+'_Hands');mesh.from_pydata(allverts,[],allfaces);mesh.materials.append(skin);mesh.update()
    obj=bpy.data.objects.new(identifier+'_Hands',mesh);scene.collection.objects.link(obj);obj.parent=rig
    for index,weights in enumerate(allweights):
        for name,weight in weights.items():
            group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name);group.add([index],weight,'REPLACE')
    mod=obj.modifiers.new('DeformHands','ARMATURE');mod.object=rig
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    return obj,audit

def curl_fingers(rig,amount,only_side=None):
    # Cada hueso usa su eje Z orientado hacia la palma; la misma flexión sirve en ambas manos.
    from mathutils import Quaternion
    for side in ['Left','Right']:
        if only_side and side!=only_side:continue
        for digit in ['Thumb','Index','Middle','Ring','Little']:
            for i,suffix in enumerate(['Proximal','Intermediate','Distal']):
                name=side+digit+suffix
                if name not in rig.pose.bones:continue
                bone=rig.pose.bones[name];normal=Vector((0,-1,0));direction=bone.bone.tail_local-bone.bone.head_local
                axis=direction.cross(normal).normalized();local=bone.bone.matrix_local.to_quaternion().inverted()@axis
                bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion(local,amount*(.65 if digit=='Thumb' else 1)*(1 if i==0 else 1.2))
