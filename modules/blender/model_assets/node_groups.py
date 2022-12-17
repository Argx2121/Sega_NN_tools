import bpy
from bpy.types import NodeSocket


class MakeGroups:
    def __init__(self):
        self.group = None

    def execute(self):
        if "NN Reflection Normal Map" in bpy.data.node_groups:
            return
        self._reflection()
        self._reflection_normal()
        self._colour_shader()
        self._nn_shader()
        #bpy.data.node_groups["NN Image Mixer"].use_fake_user = True

    def _reflection(self):
        tree = bpy.data.node_groups.new('NN Reflection', 'ShaderNodeTree')
        self.group = tree
        # thanks to firegodjr for the node set up
        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketVector', 'Reflection Vector')

        geometry = tree.nodes.new(type="ShaderNodeNewGeometry")
        camera = tree.nodes.new(type="ShaderNodeCameraData")
        separate = tree.nodes.new(type="ShaderNodeSeparateXYZ")
        combine = tree.nodes.new(type="ShaderNodeCombineXYZ")

        transform = tree.nodes.new(type="ShaderNodeVectorTransform")
        transform.vector_type = 'NORMAL'
        transform.convert_from = 'WORLD'
        transform.convert_to = 'CAMERA'

        math1 = tree.nodes.new(type="ShaderNodeMath")
        math1.operation = 'MULTIPLY'
        math1.inputs[1].default_value = -1

        value1 = tree.nodes.new(type="ShaderNodeValue")
        value1.outputs[0].default_value = 0.495

        normalize1 = tree.nodes.new(type="ShaderNodeVectorMath")
        normalize1.operation = 'NORMALIZE'

        cross_product = tree.nodes.new(type="ShaderNodeVectorMath")
        cross_product.operation = 'CROSS_PRODUCT'

        length_node = tree.nodes.new(type="ShaderNodeVectorMath")
        length_node.operation = 'LENGTH'

        normalize2 = tree.nodes.new(type="ShaderNodeVectorMath")
        normalize2.operation = 'NORMALIZE'

        vector_multi1 = tree.nodes.new(type="ShaderNodeVectorMath")
        vector_multi1.operation = 'MULTIPLY'

        vector_multi2 = tree.nodes.new(type="ShaderNodeVectorMath")
        vector_multi2.operation = 'MULTIPLY'

        vector_add = tree.nodes.new(type="ShaderNodeVectorMath")
        vector_add.operation = 'ADD'
        vector_add.inputs[1].default_value = [0.5, 0.5, 0]

        tree.links.new(geometry.outputs[1], transform.inputs[0])
        tree.links.new(transform.outputs[0], cross_product.inputs[0])
        tree.links.new(camera.outputs[0], normalize1.inputs[0])
        tree.links.new(normalize1.outputs[0], cross_product.inputs[1])
        tree.links.new(cross_product.outputs[0], separate.inputs[0])
        tree.links.new(cross_product.outputs[0], length_node.inputs[0])
        tree.links.new(separate.outputs[1], math1.inputs[0])
        tree.links.new(separate.outputs[0], combine.inputs[1])
        tree.links.new(math1.outputs[0], combine.inputs[0])
        tree.links.new(combine.outputs[0], normalize2.inputs[0])
        tree.links.new(length_node.outputs[1], vector_multi1.inputs[0])
        # this node only has one output and yet it is at index 1, curious!
        tree.links.new(normalize2.outputs[0], vector_multi1.inputs[1])
        tree.links.new(vector_multi1.outputs[0], vector_multi2.inputs[0])
        tree.links.new(value1.outputs[0], vector_multi2.inputs[1])
        tree.links.new(vector_multi2.outputs[0], vector_add.inputs[0])
        tree.links.new(vector_add.outputs[0], group_outputs.inputs['Reflection Vector'])

    def _reflection_normal(self):
        tree = bpy.data.node_groups.new('NN Reflection Normal Map', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.inputs.new('NodeSocketVector', 'Normal Map Vector')

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketVector', 'Reflection Vector')

        camera = tree.nodes.new(type="ShaderNodeCameraData")
        separate = tree.nodes.new(type="ShaderNodeSeparateXYZ")
        combine = tree.nodes.new(type="ShaderNodeCombineXYZ")

        transform = tree.nodes.new(type="ShaderNodeVectorTransform")
        transform.vector_type = 'NORMAL'
        transform.convert_from = 'WORLD'
        transform.convert_to = 'CAMERA'

        math1 = tree.nodes.new(type="ShaderNodeMath")
        math1.operation = 'MULTIPLY'
        math1.inputs[1].default_value = -1

        value1 = tree.nodes.new(type="ShaderNodeValue")
        value1.outputs[0].default_value = 0.495

        normalize1 = tree.nodes.new(type="ShaderNodeVectorMath")
        normalize1.operation = 'NORMALIZE'

        cross_product = tree.nodes.new(type="ShaderNodeVectorMath")
        cross_product.operation = 'CROSS_PRODUCT'

        length_node = tree.nodes.new(type="ShaderNodeVectorMath")
        length_node.operation = 'LENGTH'

        normalize2 = tree.nodes.new(type="ShaderNodeVectorMath")
        normalize2.operation = 'NORMALIZE'

        vector_multi1 = tree.nodes.new(type="ShaderNodeVectorMath")
        vector_multi1.operation = 'MULTIPLY'

        vector_multi2 = tree.nodes.new(type="ShaderNodeVectorMath")
        vector_multi2.operation = 'MULTIPLY'

        tree.links.new(group_inputs.outputs['Normal Map Vector'], transform.inputs[0])
        tree.links.new(transform.outputs[0], cross_product.inputs[0])
        tree.links.new(camera.outputs[0], normalize1.inputs[0])
        tree.links.new(normalize1.outputs[0], cross_product.inputs[1])
        tree.links.new(cross_product.outputs[0], separate.inputs[0])
        tree.links.new(cross_product.outputs[0], length_node.inputs[0])
        tree.links.new(separate.outputs[1], math1.inputs[0])
        tree.links.new(separate.outputs[0], combine.inputs[1])
        tree.links.new(math1.outputs[0], combine.inputs[0])
        tree.links.new(combine.outputs[0], normalize2.inputs[0])
        tree.links.new(length_node.outputs[1], vector_multi1.inputs[0])
        # this node only has one output and yet it is at index 1, curious!
        tree.links.new(normalize2.outputs[0], vector_multi1.inputs[1])
        tree.links.new(vector_multi1.outputs[0], vector_multi2.inputs[0])
        tree.links.new(value1.outputs[0], vector_multi2.inputs[1])
        tree.links.new(vector_multi2.outputs[0], group_outputs.inputs['Reflection Vector'])

    def _nn_diffuse(self):
        tree = bpy.data.node_groups.new('NN Diffuse Color', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.inputs.new('NodeSocketColor', 'Diffuse Colour')
        tree.inputs.new('NodeSocketFloat', 'Diffuse Alpha')
        tree.inputs.new('NodeSocketColor', 'Ambient Colour')
        tree.inputs.new('NodeSocketFloat', 'Ambient Alpha')
        tree.inputs.new('NodeSocketColor', 'Emission Colour')
        tree.inputs.new('NodeSocketFloat', 'Emission Alpha')
        tree.inputs.new('NodeSocketColor', 'Vertex Colour')
        tree.inputs.new('NodeSocketFloat', 'Vertex Alpha')

        tree.inputs['Material Colour'].default_value = (1, 1, 1, 1)
        tree.inputs['Material Alpha'].default_value = 1
        tree.inputs['Vertex Colour'].default_value = (1, 1, 1, 1)
        tree.inputs['Vertex Alpha'].default_value = 1

        tree.inputs['Vertex Colour'].hide_value = True
        tree.inputs['Vertex Alpha'].hide_value = True

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketColor', 'Diffuse Colour')
        tree.outputs.new('NodeSocketFloat', 'Diffuse Alpha')

        multi_alpha = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha.operation = 'MULTIPLY'
        multi_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_colour.blend_type = 'MULTIPLY'
        multi_colour.inputs[0].default_value = 1

        tree.links.new(group_inputs.outputs['Diffuse Colour'], multi_colour.inputs[1])
        tree.links.new(group_inputs.outputs['Vertex Colour'], multi_colour.inputs[2])
        tree.links.new(multi_colour.outputs[0], group_outputs.inputs['Diffuse Colour'])

        tree.links.new(group_inputs.outputs['Diffuse Alpha'], multi_alpha.inputs[0])
        tree.links.new(group_inputs.outputs['Vertex Alpha'], multi_alpha.inputs[1])
        tree.links.new(multi_alpha.outputs[0], group_outputs.inputs['Diffuse Alpha'])

        # todo make node spawn wider
        # todo node group that does nothing but it says yes bloom lol

    def _nn_shader(self):
        tree = bpy.data.node_groups.new('NN Shader', 'ShaderNodeTree')

        # Group inputs
        var = tree.inputs.new('NodeSocketColor', 'Colour')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketColor'
        var.default_attribute_name = ''
        var.description = ''
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.inputs.new('NodeSocketFloatFactor', 'Alpha')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketFloatFactor'
        var.min_value = 0.0
        var.max_value = 1.0
        var.default_value = 1.0
        var.default_attribute_name = ''
        var.description = ''

        var = tree.inputs.new('NodeSocketColor', 'Ambient')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketColor'
        var.default_attribute_name = ''
        var.description = ''
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.inputs.new('NodeSocketColor', 'Specular')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketColor'
        var.default_attribute_name = ''
        var.description = ''
        var.default_value = (0.8999999761581421, 0.8999999761581421, 0.8999999761581421, 1.0)

        var = tree.inputs.new('NodeSocketColor', 'Emission')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketColor'
        var.default_attribute_name = ''
        var.description = ''
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.inputs.new('NodeSocketFloatFactor', 'Specular Gloss')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketFloatFactor'
        var.min_value = 0.0
        var.max_value = 1.0
        var.default_value = 0.30000001192092896
        var.default_attribute_name = ''
        var.description = ''

        var = tree.inputs.new('NodeSocketFloatFactor', 'Specular Level')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketFloatFactor'
        var.min_value = 0.0
        var.max_value = 2.0
        var.default_value = 2.0
        var.default_attribute_name = ''
        var.description = ''

        var = tree.inputs.new('NodeSocketInt', 'Unshaded')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketInt'
        var.min_value = 0
        var.max_value = 1
        var.default_value = 0
        var.default_attribute_name = ''
        var.description = ''

        var = tree.inputs.new('NodeSocketInt', 'Black is alpha')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketInt'
        var.min_value = 0
        var.max_value = 1
        var.default_value = 0
        var.default_attribute_name = ''
        var.description = ''

        var = tree.inputs.new('NodeSocketVector', 'Normal')
        var.hide_value = True
        var.hide_value = True
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketVector'
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_attribute_name = ''
        var.description = ''
        var.default_value = (0.0, 0.0, 0.0)

        # Group outputs
        var = tree.outputs.new('NodeSocketShader', 'BSDF')
        var.hide_value = False
        var.hide_value = False
        var.attribute_domain = 'POINT'
        var.bl_socket_idname = 'NodeSocketShader'
        var.default_attribute_name = ''
        var.description = ''

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2020.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.label = ''
        var.height = 100.0
        var.width = 150.0
        var.location = (-2270.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0
        # Properties

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1780.0, -365.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 1.0
        # Properties
        var.operation = 'MULTIPLY_ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-960.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.20000000298023224
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-720.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 5.0
        var.inputs[2].default_value = 0.0
        # Properties

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1300.0, -191.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.002'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-480.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-480.0, -117.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        # Properties

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1300.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'SOFT_LIGHT'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1780.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        # Properties
        var.operation = 'ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.label = 'emis'
        var.height = 100.0
        var.width = 140.0
        var.location = (-1540.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2020.0, -117.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        # Properties

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1540.0, -191.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = True
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeSeparateColor')
        var.name = 'Separate Color'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1540.0, -677.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        # Properties
        var.mode = 'HSV'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-960.0, -385.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        # Properties
        var.operation = 'MULTIPLY'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-720.0, -119.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-960.0, -191.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 19.0
        var.inputs[2].default_value = 1.0
        # Properties
        var.operation = 'MULTIPLY_ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeRGBCurve')
        var.name = 'RGB Curves'
        var.label = ''
        var.height = 100.0
        var.width = 240.0
        var.location = (-1300.0, -308.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        # Properties
        curve = var.mapping.curves[0].points.new(0.0, 0.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[0].points.new(1.0, 1.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[1].points.new(0.0, 0.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[1].points.new(1.0, 1.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[2].points.new(0.0, 0.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[2].points.new(1.0, 1.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[3].points.new(0.0, 0.0)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[3].points.new(0.25, 0.75)
        curve.handle_type = 'AUTO'
        curve = var.mapping.curves[3].points.new(0.5, 1.0)
        curve.handle_type = 'AUTO'

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-240.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[2].default_value = 1.0
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0
        # Properties

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1780.0, -174.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        # Properties
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (0.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1540.0, -382.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (0.1718466877937317, 0.1718466877937317, 0.1718466877937317, 1.0)
        var.inputs[2].default_value = 1.0
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0
        # Properties

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1780.0, -559.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (-1.0, -1.0, -1.0)
        var.inputs[2].default_value = (1.0, 1.0, 1.0)
        var.inputs[3].default_value = 1.0
        # Properties
        var.operation = 'NORMALIZE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.001'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2270.0, -141.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (-1.0, -1.0, -1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        # Properties
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.002'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2020.0, -234.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (-1.0, -1.0, -1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        # Properties
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeNewGeometry')
        var.name = 'Geometry'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2510.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2510.0, -246.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 0.5
        # Properties
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2270.0, -352.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 0.5
        # Properties
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2750.0, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        # Properties
        var.operation = 'LESS_THAN'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.label = ''
        var.height = 100.0
        var.width = 177.6005859375
        var.location = (-3027.6005859375, 0.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        # Properties

        # Group Node links
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[4],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.003"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Specular BSDF"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Shader to RGB"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Shader to RGB"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.001"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Diffuse BSDF"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Shader to RGB.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix.003"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.001"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.003"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[5],
                       bpy.data.node_groups['NN Shader'].nodes["Math.003"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Emission"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Shader to RGB.002"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Emission"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Emission"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Shader to RGB.002"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF.001"].inputs[3])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Specular BSDF.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Group Output"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Invert"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF.001"].inputs[4])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Invert.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.002"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[3],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.002"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix.002"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Invert.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.004"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[2],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.004"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix.004"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Separate Color"].outputs[2],
                       bpy.data.node_groups['NN Shader'].nodes["RGB Curves"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[1],
                       bpy.data.node_groups['NN Shader'].nodes["Math.002"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["RGB Curves"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math.002"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Mix.006"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Invert"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Separate Color"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[1],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.006"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.002"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.006"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.003"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.003"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Geometry"].outputs[1],
                       bpy.data.node_groups['NN Shader'].nodes["Vector Math.001"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Vector Math"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF"].inputs[5])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Vector Math.002"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Vector Math"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Vector Math.001"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Vector Math.002"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.005"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math.007"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.007"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math.008"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.008"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Vector Math.002"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[8],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.006"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[8],
                       bpy.data.node_groups['NN Shader'].nodes["Math.001"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[7],
                       bpy.data.node_groups['NN Shader'].nodes["Math.005"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[7],
                       bpy.data.node_groups['NN Shader'].nodes["Math.008"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[7],
                       bpy.data.node_groups['NN Shader'].nodes["Invert.001"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[7],
                       bpy.data.node_groups['NN Shader'].nodes["Math"].inputs[1])

    def _colour_shader(self):
        tree = bpy.data.node_groups.new('NN Colour Init', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.inputs.new('NodeSocketColor', 'Material Colour')
        tree.inputs.new('NodeSocketFloat', 'Material Alpha')
        tree.inputs.new('NodeSocketColor', 'Vertex Colour')
        tree.inputs.new('NodeSocketFloat', 'Vertex Alpha')

        tree.inputs['Material Colour'].default_value = (1, 1, 1, 1)
        tree.inputs['Material Alpha'].default_value = 1
        tree.inputs['Vertex Colour'].default_value = (1, 1, 1, 1)
        tree.inputs['Vertex Alpha'].default_value = 1

        tree.inputs['Vertex Colour'].hide_value = True
        tree.inputs['Vertex Alpha'].hide_value = True

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketColor', 'Diffuse Colour')
        tree.outputs.new('NodeSocketFloat', 'Diffuse Alpha')

        multi_alpha = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha.operation = 'MULTIPLY'
        multi_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_colour.blend_type = 'MULTIPLY'
        multi_colour.inputs[0].default_value = 1

        tree.links.new(group_inputs.outputs['Material Colour'], multi_colour.inputs[1])
        tree.links.new(group_inputs.outputs['Vertex Colour'], multi_colour.inputs[2])
        tree.links.new(multi_colour.outputs[0], group_outputs.inputs['Diffuse Colour'])

        tree.links.new(group_inputs.outputs['Material Alpha'], multi_alpha.inputs[0])
        tree.links.new(group_inputs.outputs['Vertex Alpha'], multi_alpha.inputs[1])
        tree.links.new(multi_alpha.outputs[0], group_outputs.inputs['Diffuse Alpha'])
