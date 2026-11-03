"""Viento por vértice en espacio mundial: raíces fijas, ramas coherentes y aleteo por hoja."""
import bpy,math
from mathutils import Vector
from flora import C
NAME='Plants_R4_NaturalWind'

def create_group():
    group=bpy.data.node_groups.new(NAME,'GeometryNodeTree');nodes=group.nodes;links=group.links
    def socket(name,kind,direction='INPUT',default=None):
        s=group.interface.new_socket(name=name,in_out=direction,socket_type=kind)
        if default is not None:s.default_value=default
        return s
    socket('Geometry','NodeSocketGeometry');socket('Geometry','NodeSocketGeometry','OUTPUT')
    socket('Strength','NodeSocketFloat',default=C['wind_strength']);socket('Speed','NodeSocketFloat',default=C['wind_speed'])
    socket('WorldOffset','NodeSocketVector',default=(0,0,0));socket('Scale','NodeSocketVector',default=(1,1,1));socket('Yaw','NodeSocketFloat',default=0)
    input_node=nodes.new('NodeGroupInput');output=nodes.new('NodeGroupOutput')
    def connect(value,target):
        if isinstance(value,bpy.types.NodeSocket):links.new(value,target)
        else:target.default_value=value
    def math_node(op,a,b=0):
        n=nodes.new('ShaderNodeMath');assert op in {i.identifier for i in n.bl_rna.properties['operation'].enum_items};n.operation=op
        connect(a,n.inputs[0]);connect(b,n.inputs[1]);return n.outputs[0]
    def vector_node(op,a,b):
        n=nodes.new('ShaderNodeVectorMath');assert op in {i.identifier for i in n.bl_rna.properties['operation'].enum_items};n.operation=op
        connect(a,n.inputs[0]);connect(b,n.inputs['Scale'] if op=='SCALE' else n.inputs[1]);return n.outputs['Vector']
    def rotate(vector,angle):
        n=nodes.new('ShaderNodeVectorRotate');n.rotation_type='AXIS_ANGLE';n.inputs['Axis'].default_value=(0,0,1)
        connect(vector,n.inputs['Vector']);connect(angle,n.inputs['Angle']);return n.outputs['Vector']
    position=nodes.new('GeometryNodeInputPosition').outputs['Position']
    world=vector_node('ADD',rotate(vector_node('MULTIPLY',position,input_node.outputs['Scale']),input_node.outputs['Yaw']),input_node.outputs['WorldOffset'])
    xyz=nodes.new('ShaderNodeSeparateXYZ');links.new(world,xyz.inputs['Vector']);x,y=xyz.outputs['X'],xyz.outputs['Y']
    attr=nodes.new('GeometryNodeInputNamedAttribute');attr.data_type='FLOAT_COLOR';attr.inputs['Name'].default_value='WindMask'
    separate=nodes.new('FunctionNodeSeparateColor');links.new(attr.outputs['Attribute'],separate.inputs['Color'])
    r,g,b,a=[separate.outputs[n] for n in ['Red','Green','Blue','Alpha']]
    seconds=nodes.new('GeometryNodeInputSceneTime').outputs['Seconds']
    time=math_node('MULTIPLY',math_node('MULTIPLY',seconds,input_node.outputs['Speed']),math.tau/C['loop_seconds'])
    spatial=math_node('ADD',math_node('MULTIPLY',x,.037),math_node('MULTIPLY',y,-.025))
    primary_phase=math_node('ADD',time,spatial)
    gust=math_node('ADD',.65,math_node('MULTIPLY',.35,math_node('SINE',math_node('ADD',math_node('MULTIPLY',time,2),math_node('ADD',math_node('MULTIPLY',spatial,.37),1.2)))))
    primary=math_node('MULTIPLY',math_node('MULTIPLY',r,C['primary_amplitude_m']),math_node('MULTIPLY',math_node('SINE',primary_phase),gust))
    branch_phase=math_node('ADD',math_node('MULTIPLY',time,3),math_node('ADD',math_node('MULTIPLY',x,.35),math_node('MULTIPLY',y,-.21)))
    branch=math_node('MULTIPLY',math_node('MULTIPLY',g,C['branch_amplitude_m']),math_node('SINE',branch_phase))
    phase=math_node('MULTIPLY',a,math.tau)
    leaf_phase=math_node('ADD',math_node('ADD',math_node('MULTIPLY',time,9),phase),math_node('ADD',math_node('MULTIPLY',x,.13),math_node('MULTIPLY',y,-.11)))
    flutter=math_node('MULTIPLY',math_node('MULTIPLY',b,C['leaf_amplitude_m']),math_node('SINE',leaf_phase))
    vertical=math_node('MULTIPLY',math_node('MULTIPLY',b,C['leaf_vertical_amplitude_m']),math_node('SINE',math_node('ADD',math_node('MULTIPLY',time,13),math_node('MULTIPLY',phase,1.7))))
    direction=Vector((C['wind_direction_unity_xz'][0],-C['wind_direction_unity_xz'][1],0)).normalized();perpendicular=Vector((-direction.y,direction.x,0))
    displacement=vector_node('ADD',vector_node('SCALE',tuple(direction),math_node('ADD',primary,branch)),vector_node('SCALE',tuple(perpendicular),flutter))
    displacement=vector_node('ADD',displacement,vector_node('SCALE',(0,0,1),vertical))
    displacement=vector_node('SCALE',displacement,input_node.outputs['Strength'])
    local=vector_node('DIVIDE',rotate(displacement,math_node('MULTIPLY',input_node.outputs['Yaw'],-1)),input_node.outputs['Scale'])
    set_position=nodes.new('GeometryNodeSetPosition');links.new(input_node.outputs['Geometry'],set_position.inputs['Geometry']);links.new(local,set_position.inputs['Offset'])
    links.new(set_position.outputs['Geometry'],output.inputs['Geometry'])
    for i,node in enumerate(nodes):node.location=((i%9)*210,-(i//9)*180)
    return group

def attach(obj,group,strength=None):
    modifier=obj.modifiers.new('NaturalWind_R3','NODES');modifier.node_group=group
    values={'Strength':C['wind_strength'] if strength is None else strength,'Speed':C['wind_speed'],
            'WorldOffset':tuple(obj.matrix_world.translation),'Scale':tuple(obj.matrix_world.to_scale()),'Yaw':obj.matrix_world.to_euler().z}
    for item in group.interface.items_tree:
        if item.item_type=='SOCKET' and item.in_out=='INPUT' and item.name in values:modifier[item.identifier]=values[item.name]
    return modifier
