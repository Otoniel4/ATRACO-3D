"""Geometría y pesos de la cadena de pierna; coordenadas del armature en metros."""
import bpy
from mathutils import Vector

def axis_at(chain,z):
    hip,knee,ankle=chain
    a,b=(knee,ankle) if z<=knee.z else (hip,knee)
    return a.lerp(b,(z-a.z)/(b.z-a.z))

def map_height(z,old,new):
    if z>=old[0].z or z<=old[2].z:return z
    a,b=(1,2) if z<=old[1].z else (0,1)
    t=(z-old[a].z)/(old[b].z-old[a].z)
    return new[a].z+t*(new[b].z-new[a].z)

def move_point(p,old,new):
    z=map_height(p.z,old,new)
    delta=axis_at(new,z)-axis_at(old,p.z)
    seam=min(1,abs(p.x)/.035)
    return Vector((p.x+delta.x*seam,p.y+delta.y*seam,z))

def bind_region(obj,rig,indices,height):
    """Asigna solo los vértices de pierna; no altera pesos de mangas, cabeza o manos."""
    for group in obj.vertex_groups:group.remove(indices)
    names=['Hips']+[s+n for s in ['Left','Right'] for n in ['UpperLeg','LowerLeg','Foot']]
    groups={n:obj.vertex_groups.get(n) or obj.vertex_groups.new(name=n) for n in names}
    scale=height/1.88;knee_blend=.055*scale;hip_blend=.14*scale
    for i in indices:
        v=obj.data.vertices[i];side='Left' if v.co.x>=0 else 'Right'
        hip=rig.data.bones[side+'UpperLeg'].head_local.z
        knee=rig.data.bones[side+'LowerLeg'].head_local.z
        ankle=rig.data.bones[side+'Foot'].head_local.z
        if abs(v.co.x)<.012:weights={'Hips':1}
        elif v.co.z>hip-hip_blend:
            t=max(0,min(1,(v.co.z-hip+hip_blend)/hip_blend));weights={'Hips':t,side+'UpperLeg':1-t}
        elif v.co.z>knee+knee_blend:weights={side+'UpperLeg':1}
        elif v.co.z>knee-knee_blend:
            t=(v.co.z-knee+knee_blend)/(2*knee_blend);weights={side+'UpperLeg':t,side+'LowerLeg':1-t}
        elif v.co.z<ankle+.065*scale:
            t=max(0,min(1,(v.co.z-ankle+.015*scale)/(.08*scale)));weights={side+'LowerLeg':t,side+'Foot':1-t}
        else:weights={side+'LowerLeg':1}
        for n,w in weights.items():
            if w>1e-7:groups[n].add([i],w,'REPLACE')
    mod=next((m for m in obj.modifiers if m.type=='ARMATURE'),None)
    if mod is None:mod=obj.modifiers.new('Humanoid','ARMATURE')
    mod.object=rig;obj.parent=rig

def components(obj):
    remaining=set(range(len(obj.data.vertices)));neighbors={i:set() for i in remaining}
    for e in obj.data.edges:
        a,b=e.vertices;neighbors[a].add(b);neighbors[b].add(a)
    output=[]
    while remaining:
        start=remaining.pop();part={start};stack=[start]
        while stack:
            for v in neighbors[stack.pop()]:
                if v in remaining:remaining.remove(v);part.add(v);stack.append(v)
        output.append(part)
    return output

def section(obj,z,side,indices=None):
    points=[]
    for e in obj.data.edges:
        if indices is not None and not all(i in indices for i in e.vertices):continue
        a,b=[obj.data.vertices[i].co for i in e.vertices]
        if (a.z-z)*(b.z-z)<0:
            p=a.lerp(b,(z-a.z)/(b.z-a.z))
            if p.x*side>.001:points.append(p)
    if not points:return None
    return (min(v.x for v in points),max(v.x for v in points),min(v.y for v in points),max(v.y for v in points))
