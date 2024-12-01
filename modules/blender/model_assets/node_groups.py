import bpy


class MakeGroups:
    def __init__(self):
        pass

    def execute(self):
        if '_NN_REFLECTION' in bpy.data.node_groups:
            return
        self._reflection()
        # self._reflection_normal()
        self._nn_shader_init()
        self._nn_shader()
        self._nn_rgb_multi()
        self._nn_rgb_mix()
        self._nn_rgb_add()
        self._nn_rgb_sub()

    @staticmethod
    def _reflection():
        tree = bpy.data.node_groups.new('_NN_REFLECTION', 'ShaderNodeTree')
        tree.use_fake_user = True
        # thanks to firegodjr for the node set up
        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.interface.new_socket(name="Reflection Vector", in_out='OUTPUT', socket_type='NodeSocketVector')

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

        # todo .. yeah

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
        tree.links.new(normalize2.outputs[0], vector_multi1.inputs[1])
        tree.links.new(vector_multi1.outputs[0], vector_multi2.inputs[0])
        tree.links.new(value1.outputs[0], vector_multi2.inputs[1])
        tree.links.new(vector_multi2.outputs[0], vector_add.inputs[0])
        tree.links.new(vector_add.outputs[0], group_outputs.inputs['Reflection Vector'])

    @staticmethod
    def _reflection_normal():
        tree = bpy.data.node_groups.new('_NN_REFLECTION_NORMAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.interface.new_socket(name="Normal Map Vector", in_out='INPUT', socket_type='NodeSocketVector')

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.interface.new_socket(name="Reflection Vector", in_out='OUTPUT', socket_type='NodeSocketVector')

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
        tree.links.new(normalize2.outputs[0], vector_multi1.inputs[1])
        tree.links.new(vector_multi1.outputs[0], vector_multi2.inputs[0])
        tree.links.new(value1.outputs[0], vector_multi2.inputs[1])
        tree.links.new(vector_multi2.outputs[0], group_outputs.inputs['Reflection Vector'])

    @staticmethod
    def _nn_shader():
        tree = bpy.data.node_groups.new('_NN_SHADER', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.min_value = 0.0
        var.default_value = 1.0
        var.max_value = 1.0

        var = tree.interface.new_socket(name='Unshaded', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 1

        var = tree.interface.new_socket(name='Black is alpha', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 1

        var = tree.interface.new_socket(name='Dont Write Depth', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 1

        var = tree.interface.new_socket(name='Ignore Depth', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 1

        var = tree.interface.new_socket(name='Use Specular', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = True

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.8999999761581421, 0.8999999761581421, 0.8999999761581421, 1.0)

        var = tree.interface.new_socket(name='Specular Gloss', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.min_value = 0.0
        var.default_value = 0.30000001192092896
        var.max_value = 1.0

        var = tree.interface.new_socket(name='Specular Level', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.min_value = 0.0
        var.default_value = 2.0
        var.max_value = 2.0

        var = tree.interface.new_socket(name='Override Flags', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Mat Flags', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = -2147483648
        var.default_value = 0
        var.max_value = 2147483647

        var = tree.interface.new_socket(name='Override Data', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Blend Type', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0  # OFF
        var.default_value = 1  # ON
        var.max_value = 1

        var = tree.interface.new_socket(name='Source Fact', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 4
        var.max_value = 7

        var = tree.interface.new_socket(name='Dest Fact', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 5
        var.max_value = 7

        var = tree.interface.new_socket(name='Blend Op', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 5
        var.max_value = 15

        var = tree.interface.new_socket(name='Z Mode', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 2
        var.max_value = 7

        var = tree.interface.new_socket(name='Alpha ref0', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 255

        var = tree.interface.new_socket(name='Alpha ref1', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 255

        var = tree.interface.new_socket(name='Alpha comp0', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 6
        var.max_value = 7

        var = tree.interface.new_socket(name='Alpha comp1', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 7
        var.max_value = 7

        var = tree.interface.new_socket(name='Alpha Op', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = 0
        var.default_value = 0
        var.max_value = 3

        var = tree.interface.new_socket(name='User', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.min_value = -2147483648
        var.default_value = 0
        var.max_value = 2147483647

        # Group outputs
        var = tree.interface.new_socket(name='BSDF', in_out='OUTPUT', socket_type='NodeSocketShader')
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-1225.0, -408.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-825.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (-1775.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-1500.0, -198.0)
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

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert.001'
        var.location = (-2050.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixShader')
        var.name = 'Mix Shader'
        var.location = (-275.0, 0.0)
        var.inputs[0].default_value = 0.5

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-550.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MIX'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.location = (-825.0, -204.0)
        var.inputs[0].default_value = 0.20000000298023224
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeSeparateColor')
        var.name = 'Separate Color'
        var.location = (-1500.0, 0.0)
        var.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.mode = 'HSV'

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.location = (-550.0, -340.0)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 5.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-825.0, -429.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 24.0
        var.inputs[2].default_value = 1.0
        var.operation = 'MULTIPLY_ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeBsdfTransparent')
        var.name = 'Transparent BSDF'
        var.location = (-550.0, -225.0)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-2050.0, -365.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 1.0
        var.operation = 'MULTIPLY_ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeRGBCurve')
        var.name = 'RGB Curves'
        var.width = 240.0
        var.location = (-1225.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        point = var.mapping.curves[0].points.new(0.0, 0.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[0].points.new(1.0, 1.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[1].points.new(0.0, 0.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[1].points.new(1.0, 1.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[2].points.new(0.0, 0.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[2].points.new(1.0, 1.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[3].points.new(0.0, 0.02500000037252903)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[3].points.new(0.5, 1.0)
        point.handle_type = 'AUTO'
        point = var.mapping.curves[3].points.new(1.0, 1.0)
        point.handle_type = 'AUTO'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.width = 177.6005859375
        var.location = (-2372.000732421875, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-2050.0, -140.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0048721288330852985, 0.0048721288330852985, 0.0048721288330852985, 1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        var.blend_type = 'MIX'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-1775.0, -225.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 1.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Emission"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Specular BSDF"].inputs[1])
        tree.links.new(tree.nodes["Separate Color"].outputs[2], tree.nodes["RGB Curves"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math.002"].inputs[1])
        tree.links.new(tree.nodes["RGB Curves"].outputs[0], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Separate Color"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Specular BSDF"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Invert.001"].inputs[1])
        tree.links.new(tree.nodes["Invert.001"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix Shader"].inputs[0])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.003"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Math.004"].inputs[1])

    @staticmethod
    def _nn_shader_init():
        tree = bpy.data.node_groups.new('_NN_SHADER_INIT', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name="Material Color", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Material Alpha", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name="Vertex Color", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Vertex Alpha", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Unshaded", in_out='INPUT', socket_type='NodeSocketInt')
        var.default_value = 0
        var.hide_value = False
        var.max_value = 1
        var.min_value = 0

        var = tree.interface.new_socket(name="Emission", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Ambient", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name="Diffuse Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Diffuse Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.hide_value = False

        var = tree.interface.new_socket(name="Unshaded", in_out='OUTPUT', socket_type='NodeSocketInt')
        var.default_value = 0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-275.0, -231.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1100.0, -140.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.location = (-825.0, -210.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-1100.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-825.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.operation = 'ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.label = 'emis'
        var.location = (-550.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.label = 'amb'
        var.location = (-550.0, -231.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-1387.5, 0.0)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert.001'
        var.location = (-825.0, -441.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.location = (-275.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'SOFT_LIGHT'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Mix.001"].inputs[0])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Mix.003"].inputs[0])
        tree.links.new(tree.nodes["Invert.001"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Invert.001"].inputs[1])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Group Output"].inputs[2])

    @staticmethod
    def _nn_rgb_multi():
        tree = bpy.data.node_groups.new('_NN_RGB_MULTI', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name="Color 1", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 1", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 2", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2 Multiplier", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = False
        var.max_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name="Shader Init", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-240.0, -191.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-480.0, -191.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-240.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-480.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-720.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.003"].inputs[1])

    @staticmethod
    def _nn_rgb_mix():
        tree = bpy.data.node_groups.new('_NN_RGB_MIX', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name="Color 1", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 1", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 2", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2 Multiplier", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = False
        var.max_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name="Shader Init", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-240.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MIX'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-480.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-240.0, -191.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-480.0, -174.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-720.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[1])

    @staticmethod
    def _nn_rgb_add():
        tree = bpy.data.node_groups.new('_NN_RGB_ADD', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name="Color 1", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 1", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 2", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2 Multiplier", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = False
        var.max_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name="Shader Init", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-480.0, -191.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-240.0, -191.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-240.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-480.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-720.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[1])

    @staticmethod
    def _nn_rgb_sub():
        tree = bpy.data.node_groups.new('_NN_RGB_SUB', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name="Color 1", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 1", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name="Alpha 2", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name="Color 2 Multiplier", in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.hide_value = False
        var.max_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name="Shader Init", in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-480.0, -191.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-240.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'SUBTRACT'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-240.0, -191.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-480.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-720.0, 0.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[1])
