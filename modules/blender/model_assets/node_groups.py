import bpy


class MakeGroups:
    def __init__(self):
        pass

    def execute(self):
        if '_NN_REFLECTION' in bpy.data.node_groups:
            return
        self._nn_reflection()
        # self._reflection_normal()
        self._gno_vector()
        self._gno_shader_init()
        self._gno_shader()
        self._nn_rgb_multi()
        self._nn_rgb_decal()
        self._nn_rgb_add()
        self._nn_rgb_sub()
        self._nn_rgb_specular2()
        self._nn_rgb_specular()
        self._nn_rgb_decal_2()
        self._nn_rgb_alpha_tex()
        self._nn_rgb_pass_clear()
        self._nn_rgb_blend()
        self._nn_rgb_replace()

    @staticmethod
    def _nn_reflection():
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
    def _gno_vector():
        tree = bpy.data.node_groups.new('_GNO_VECTOR', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Reflection Vector', in_out='INPUT', socket_type='NodeSocketBool')
        var.default_value = False
        var.hide_value = False

        var = tree.interface.new_socket(name='UV Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Offset', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38

        var = tree.interface.new_socket(name='U', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = 0
        var.default_value = 0
        var.hide_value = False
        var.max_value = 2

        var = tree.interface.new_socket(name='V', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = 0
        var.default_value = 0
        var.hide_value = False
        var.max_value = 2

        # Group outputs
        var = tree.interface.new_socket(name='Image Vector', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-67.90414428710938, 6.7112226486206055)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-2499.635986328125, -439.47772216796875)

        var = tree.nodes.new(type='ShaderNodeMix')
        var.name = 'Mix'
        var.location = (-249.5856475830078, 3.8023345470428467)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5)
        var.inputs[2].default_value = 0.0
        var.inputs[3].default_value = 0.0
        var.inputs[4].default_value = (0.0, 0.0, 0.0)
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MIX'
        var.data_type = 'VECTOR'
        var.clamp_factor = False
        var.factor_mode = 'UNIFORM'
        var.clamp_result = False

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp'
        var.location = (-1650.0, -231.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-1650.0, -660.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'PINGPONG'

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ'
        var.location = (-2005.7474365234375, -446.2098693847656)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ'
        var.location = (-550.2181396484375, 20.49124526977539)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeGroup')
        var.node_tree = bpy.data.node_groups['_NN_REFLECTION']
        var.name = 'Group'
        var.location = (-550.0, -167.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-1650.0, 0.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-1375.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-1650.0, -431.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-1375.0, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-1375.0, -410.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (-1100.0, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.location = (-1100.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.location = (-825.0, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp.001'
        var.location = (-1902.325439453125, -1039.0703125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.009'
        var.location = (-1881.126220703125, -1227.345458984375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'PINGPONG'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.010'
        var.location = (-1671.4371337890625, -1053.4573974609375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.011'
        var.location = (-1468.352294921875, -1058.9755859375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.012'
        var.location = (-1671.787353515625, -1245.1146240234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.013'
        var.location = (-1470.50439453125, -1264.8226318359375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.014'
        var.location = (-1679.0904541015625, -1442.364990234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.015'
        var.location = (-1462.826171875, -1449.6419677734375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.016'
        var.location = (-1254.687744140625, -1073.7642822265625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.017'
        var.location = (-1259.180419921875, -1293.130615234375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.001'
        var.location = (-2239.809326171875, -457.97613525390625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.operation = 'ADD'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[0])
        tree.links.new(tree.nodes["Mix"].outputs[1], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group"].outputs[0], tree.nodes["Mix"].inputs[5])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Clamp"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Clamp"].outputs[0], tree.nodes["Math.002"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math.005"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Math.006"].inputs[1])
        tree.links.new(tree.nodes["Math.005"].outputs[0], tree.nodes["Math.006"].inputs[0])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Math.007"].inputs[0])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Math.007"].inputs[1])
        tree.links.new(tree.nodes["Math.007"].outputs[0], tree.nodes["Math.008"].inputs[0])
        tree.links.new(tree.nodes["Math.006"].outputs[0], tree.nodes["Math.008"].inputs[1])
        tree.links.new(tree.nodes["Math.008"].outputs[0], tree.nodes["Combine XYZ"].inputs[0])
        tree.links.new(tree.nodes["Math.010"].outputs[0], tree.nodes["Math.011"].inputs[0])
        tree.links.new(tree.nodes["Clamp.001"].outputs[0], tree.nodes["Math.011"].inputs[1])
        tree.links.new(tree.nodes["Math.012"].outputs[0], tree.nodes["Math.013"].inputs[0])
        tree.links.new(tree.nodes["Math.009"].outputs[0], tree.nodes["Math.013"].inputs[1])
        tree.links.new(tree.nodes["Math.014"].outputs[0], tree.nodes["Math.015"].inputs[0])
        tree.links.new(tree.nodes["Math.011"].outputs[0], tree.nodes["Math.016"].inputs[0])
        tree.links.new(tree.nodes["Math.013"].outputs[0], tree.nodes["Math.016"].inputs[1])
        tree.links.new(tree.nodes["Math.016"].outputs[0], tree.nodes["Math.017"].inputs[0])
        tree.links.new(tree.nodes["Math.015"].outputs[0], tree.nodes["Math.017"].inputs[1])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[1], tree.nodes["Math.009"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[1], tree.nodes["Clamp.001"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[1], tree.nodes["Math.015"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.010"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.012"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.014"].inputs[0])
        tree.links.new(tree.nodes["Math.017"].outputs[0], tree.nodes["Combine XYZ"].inputs[1])
        tree.links.new(tree.nodes["Combine XYZ"].outputs[0], tree.nodes["Mix"].inputs[4])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Vector Math.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Vector Math.001"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.001"].outputs[0], tree.nodes["Separate XYZ"].inputs[0])

    @staticmethod
    def _gno_shader():
        tree = bpy.data.node_groups.new('_GNO_SHADER', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name="Don't Write Depth", in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 1
        var.default_value = 0
        var.min_value = 0

        var = tree.interface.new_socket(name='Ignore Depth', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 1
        var.default_value = 0
        var.min_value = 0

        var = tree.interface.new_socket(name='Override Flags', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Mat Flags', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 2147483647
        var.default_value = 0
        var.min_value = -2147483648

        var = tree.interface.new_socket(name='Alpha ref0', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 255
        var.default_value = 0
        var.min_value = 0

        var = tree.interface.new_socket(name='Alpha ref1', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 255
        var.default_value = 0
        var.min_value = 0

        var = tree.interface.new_socket(name='User', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 2147483647
        var.default_value = 0
        var.min_value = -2147483648

        # Group outputs
        var = tree.interface.new_socket(name='BSDF', in_out='OUTPUT', socket_type='NodeSocketShader')
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-1341.2568359375, 137.26876831054688)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixShader')
        var.name = 'Mix Shader'
        var.location = (-1616.2568359375, 137.26876831054688)
        var.inputs[0].default_value = 0.5

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.location = (-1943.4683837890625, -177.23348999023438)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeBsdfTransparent')
        var.name = 'Transparent BSDF'
        var.location = (-1943.4683837890625, -52.034461975097656)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 0.0

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.width = 177.6005859375
        var.location = (-2370.643310546875, -15.456640243530273)

        # Group Node links
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix Shader"].inputs[0])

    @staticmethod
    def _gno_shader_init():
        tree = bpy.data.node_groups.new('_GNO_SHADER_INIT', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Vertex Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Vertex Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Unshaded', in_out='INPUT', socket_type='NodeSocketInt')
        var.default_value = 0
        var.max_value = 1
        var.hide_value = False
        var.min_value = 0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (0.5, 0.5, 0.5, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular Level', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 2.0
        var.max_value = 4.0
        var.hide_value = False
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Specular Gloss', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.30000001192092896
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Use Specular', in_out='INPUT', socket_type='NodeSocketBool')
        var.default_value = True
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.hide_value = False

        # Group outputs
        var = tree.interface.new_socket(name='Diffuse Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Diffuse Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Specular', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-245.5607452392578, -212.1346893310547)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1328.613037109375, -523.9097900390625)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.location = (-785.5872802734375, -100.33970642089844)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (521.9993286132812, -262.09124755859375)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-1072.9659423828125, 42.85885238647461)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-821.0558471679688, 117.86932373046875)
        var.inputs[0].default_value = 0.25
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.operation = 'ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.label = 'amb'
        var.location = (-513.0729370117188, -112.3735580444336)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-1342.4432373046875, 39.475257873535156)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert.001'
        var.location = (-980.5103759765625, -444.16424560546875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.location = (-267.8619079589844, 13.413289070129395)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-208.0057373046875, -692.171142578125)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (-683.3147583007812, -447.78179931640625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-528.9509887695312, -793.4546508789062)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 1.0)
        var.inputs[2].default_value = 1.0
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-938.1666259765625, -843.8958740234375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 1.0
        var.operation = 'MULTIPLY_ADD'
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-911.6716918945312, -622.3729858398438)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0048721288330852985, 0.0048721288330852985, 0.0048721288330852985, 1.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-477.3672790527344, -498.4479064941406)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-47.477638244628906, 226.12686157226562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-9.247937202453613, -499.01812744140625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (279.42901611328125, -424.8663635253906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Invert.001"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Invert.001"].inputs[1])
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[9], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[2])
        tree.links.new(tree.nodes["Mix"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Invert.001"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Specular BSDF"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _nn_rgb_multi():
        tree = bpy.data.node_groups.new('_NN_RGB_MULTI', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
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
        var.location = (-316.18792724609375, -262.09112548828125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-531.4783325195312, -302.2730407714844)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-155.5754852294922, 330.7283630371094)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-468.78564453125, 91.69722747802734)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[2])

    @staticmethod
    def _nn_rgb_decal():
        tree = bpy.data.node_groups.new('_NN_RGB_DECAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-322.3995666503906, 215.954833984375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-691.9195556640625, 198.87911987304688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-583.2155151367188, -15.829150199890137)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])

    @staticmethod
    def _nn_rgb_add():
        tree = bpy.data.node_groups.new('_NN_RGB_ADD', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-588.3457641601562, -240.6518096923828)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-272.4024658203125, -90.68266296386719)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-259.23895263671875, 113.49003601074219)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-965.0628662109375, 13.172920227050781)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (7.088038444519043, 118.55655670166016)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-474.9371032714844, 193.54104614257812)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-709.8742065429688, 225.96676635742188)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
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
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-649.4619140625, -120.79322814941406)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-426.35040283203125, 426.61883544921875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'SUBTRACT'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-335.60516357421875, 155.9690399169922)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-652.1366577148438, 165.6847686767578)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.003"].inputs[2])

    @staticmethod
    def _nn_rgb_replace():
        tree = bpy.data.node_groups.new('_NN_RGB_REPLACE', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-672.8994140625, -43.72883987426758)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-652.1366577148438, 165.6847686767578)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])

    @staticmethod
    def _nn_rgb_blend():
        tree = bpy.data.node_groups.new('_NN_RGB_BLEND', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-695.3115234375, -157.01626586914062)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-274.3228454589844, 129.5900115966797)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-566.4703369140625, 158.44015502929688)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-354.65216064453125, -51.24089431762695)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.007"].inputs[0])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[0])

    @staticmethod
    def _nn_rgb_pass_clear():
        tree = bpy.data.node_groups.new('_NN_RGB_PASS', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-690.7468872070312, 157.2327117919922)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _nn_rgb_alpha_tex():
        tree = bpy.data.node_groups.new('_NN_RGB_ALPHA', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-579.4807739257812, -51.96924591064453)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (0.0, 0.0)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])


    @staticmethod
    def _nn_rgb_decal_2():
        tree = bpy.data.node_groups.new('_NN_RGB_DECAL_2', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-331.1751403808594, 268.79168701171875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-700.6951293945312, 251.71595764160156)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-8.775586128234863, 52.83684158325195)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-968.7755737304688, 52.83684158325195)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-591.9910888671875, 37.0076904296875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-313.9629211425781, 33.58995056152344)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'ADD'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.006"].inputs[2])

    @staticmethod
    def _nn_rgb_specular():
        tree = bpy.data.node_groups.new('_NN_RGB_SPEC', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1208.107177734375, 147.01263427734375)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (188.0198974609375, 181.97006225585938)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-467.794921875, 480.228271484375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-265.9745178222656, 450.68017578125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-343.2137756347656, 114.48762512207031)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-52.666481018066406, 346.6326904296875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-695.73486328125, 467.5712890625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-917.7125854492188, 450.2210998535156)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])

    @staticmethod
    def _nn_rgb_specular2():
        tree = bpy.data.node_groups.new('_NN_RGB_SPEC_2', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1208.107177734375, 147.01263427734375)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (188.0198974609375, 181.97006225585938)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-467.794921875, 480.228271484375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-265.9745178222656, 450.68017578125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-120.39617919921875, 15.422167778015137)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-52.666481018066406, 346.6326904296875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-695.73486328125, 467.5712890625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-917.7125854492188, 450.2210998535156)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
