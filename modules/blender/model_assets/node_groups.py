import bpy


class MakeGroups:
    def __init__(self):
        pass

    def execute(self):
        if '.NN_REFLECTION' in bpy.data.node_groups:
            return
        # GENERAL
        self._nn_reflection()
        # self._reflection_normal()
        self._nn_vector()
        # self._nn_tangent()  # AND YEP THESE ARE NEEDED BC THEY CAN ANIMATE THE TEXTURE INDEX
        # self._nn_world()
        # SHADERS
        self._gno_shader_init_flat()
        self._gno_shader_init_no_spec()
        self._gno_shader_init_all()
        self._gno_shader()
        self._xno_shader()
        # MIX NODES
        self._gno_multi()
        self._gno_decal()
        self._gno_add()
        self._gno_sub()
        self._gno_specular2()
        self._gno_specular()
        self._gno_decal_2()
        self._gno_alpha_tex()
        self._gno_pass_color()
        self._gno_blend()
        self._gno_replace()

    @staticmethod
    def _nn_reflection():
        tree = bpy.data.node_groups.new('.NN_REFLECTION', 'ShaderNodeTree')
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
        tree = bpy.data.node_groups.new('.NN_REFLECTION_NORMAL', 'ShaderNodeTree')
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
    def _nn_tangent():
        tree = bpy.data.node_groups.new('.NN_TANGENT', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Normal', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-135.77098083496094, 129.41961669921875)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-673.4436645507812, 57.681312561035156)

        var = tree.nodes.new(type='ShaderNodeNormalMap')
        var.name = 'Normal Map'
        var.width = 150.0
        var.location = (-391.22308349609375, 144.7174835205078)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 1.0, 1.0)
        var.space = 'TANGENT'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-1214.9486083984375, 90.8031234741211)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Normal Map"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Normal Map"].inputs[1])

    @staticmethod
    def _nn_world():
        tree = bpy.data.node_groups.new('_NN_WORLD', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Normal', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-135.77098083496094, 129.41961669921875)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-673.4436645507812, 57.681312561035156)

        var = tree.nodes.new(type='ShaderNodeNormalMap')
        var.name = 'Normal Map'
        var.width = 150.0
        var.location = (-391.22308349609375, 144.7174835205078)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 1.0, 1.0)
        var.space = 'WORLD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-1214.9486083984375, 90.8031234741211)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Normal Map"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Normal Map"].inputs[1])

    @staticmethod
    def _nn_vector():
        tree = bpy.data.node_groups.new('.NN_VECTOR', 'ShaderNodeTree')
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
        var.node_tree = bpy.data.node_groups['.NN_REFLECTION']
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
        tree = bpy.data.node_groups.new('.GNO_SHADER', 'ShaderNodeTree')
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

        var = tree.interface.new_socket(name='Disable Fog', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Callback', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

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
    def _xno_shader():
        tree = bpy.data.node_groups.new('.XNO_SHADER', 'ShaderNodeTree')
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

        var = tree.interface.new_socket(name='Disable Fog', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Callback', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

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
    def _gno_shader_init_flat():  # ''gno'' ehe
        tree = bpy.data.node_groups.new('.GNO_SHADER_INIT_FLAT', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Specular Level', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.5

        var = tree.interface.new_socket(name='Specular Gloss', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.5

        var = tree.interface.new_socket(name='Vertex Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Vertex Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Normal', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.default_value = (0.0, 0.0, 0.0)

        # Group outputs
        var = tree.interface.new_socket(name='Diffuse Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Diffuse Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.0

        var = tree.interface.new_socket(name='Specular', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Shading', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-706.4210205078125, -519.6902465820312)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1313.3961181640625, -366.0379333496094)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.location = (-925.4171752929688, -234.64437866210938)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-80.7808609008789, -354.7804260253906)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-583.1181640625, -184.18759155273438)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = True

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[3])
        tree.links.new(tree.nodes["Mix"].outputs[0], tree.nodes["Mix.009"].inputs[1])

    @staticmethod
    def _gno_shader_init_no_spec():
        tree = bpy.data.node_groups.new('.GNO_SHADER_INIT_NO_SPEC', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Specular Level', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.5

        var = tree.interface.new_socket(name='Specular Gloss', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.5

        var = tree.interface.new_socket(name='Vertex Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Vertex Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Normal', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.default_value = (0.0, 0.0, 0.0)

        # Group outputs
        var = tree.interface.new_socket(name='Diffuse Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Diffuse Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.default_value = 0.0

        var = tree.interface.new_socket(name='Specular', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Shading', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-186.0754852294922, -371.3934020996094)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1328.613037109375, -523.9097900390625)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.location = (-436.0078125, -212.32485961914062)
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
        var.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-548.5967407226562, 16.612335205078125)

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-802.3429565429688, -91.7573471069336)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.location = (-259.1224365234375, 62.40679168701172)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (11.950872421264648, -57.335548400878906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (227.91891479492188, -101.7522964477539)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = True

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Mix"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[3])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[9], tree.nodes["Diffuse BSDF"].inputs[2])

    @staticmethod
    def _gno_shader_init_all():
        tree = bpy.data.node_groups.new('.GNO_SHADER_INIT_ALL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (0.5, 0.5, 0.5, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular Level', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.default_value = 0.5
        var.min_value = 0.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular Gloss', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.default_value = 0.5
        var.min_value = 0.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Vertex Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Vertex Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Normal', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Diffuse Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Diffuse Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.default_value = 0.0
        var.min_value = 0.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Specular', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Shading', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-186.0754852294922, -371.3934020996094)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1328.613037109375, -523.9097900390625)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix'
        var.location = (-436.0078125, -212.32485961914062)
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
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-548.5967407226562, 16.612335205078125)

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-802.3429565429688, -91.7573471069336)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.location = (-259.1224365234375, 62.40679168701172)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-208.0057373046875, -692.171142578125)

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-528.9509887695312, -793.4546508789062)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 1.0)
        var.inputs[2].default_value = 0.8999999761581421
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (11.950872421264648, -57.335548400878906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (227.91891479492188, -101.7522964477539)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (12.0, -677.3638916015625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (231.99998474121094, -605.88916015625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.75, 0.75, 0.75, 1.0)
        var.blend_type = 'DIVIDE'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[8], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Mix"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[3])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[9], tree.nodes["Specular BSDF"].inputs[5])
        tree.links.new(tree.nodes["Group Input"].outputs[9], tree.nodes["Diffuse BSDF"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Specular BSDF"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Specular BSDF"].inputs[2])

    @staticmethod
    def _gno_multi():
        tree = bpy.data.node_groups.new('.GNO_MULTI', 'ShaderNodeTree')
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
    def _gno_decal():
        tree = bpy.data.node_groups.new('.GNO_DECAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.min_value = 0.0
        var.hide_value = False
        var.max_value = 1.0

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
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-455.98284912109375, 187.4381561279297)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MIX'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-691.9195556640625, 198.87911987304688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

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
        var.location = (-210.9345703125, 178.30331420898438)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[1])

    @staticmethod
    def _gno_add():
        tree = bpy.data.node_groups.new('.GNO_ADD', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38
        var.default_value = 0.0

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-647.8196411132812, -176.92996215820312)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-306.98028564453125, -65.74803161621094)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-454.2577209472656, 202.18447875976562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_alpha = False
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
        var.location = (-746.0270385742188, 207.4038543701172)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-224.40200805664062, 185.77381896972656)
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
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _gno_sub():
        tree = bpy.data.node_groups.new('.GNO_SUB', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38
        var.default_value = 0.0

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-705.3594970703125, -116.40499114990234)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-222.24124145507812, 254.7414093017578)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'SUBTRACT'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (169.93411254882812, -9.754495620727539)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-482.66583251953125, 35.39385986328125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-986.8014526367188, 30.104755401611328)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-29.1396427154541, 200.8575897216797)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _gno_replace():
        tree = bpy.data.node_groups.new('.GNO_REPLACE', 'ShaderNodeTree')
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
    def _gno_blend():
        tree = bpy.data.node_groups.new('.GNO_BLEND', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.max_value = 1.0
        var.default_value = 1.0
        var.hide_value = False

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.default_value = 0.0
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-650.4283447265625, -141.6611785888672)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (447.39453125, 152.33287048339844)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (116.5609130859375, 370.8738098144531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-340.85052490234375, -13.607205390930176)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-758.1766357421875, 224.6389617919922)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'SUBTRACT'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-447.9766540527344, 377.72247314453125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-173.10104370117188, 416.1719665527344)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_clamp = False
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _gno_pass_color():
        tree = bpy.data.node_groups.new('.GNO_PASSCOLOR', 'ShaderNodeTree')
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
    def _gno_alpha_tex():
        tree = bpy.data.node_groups.new('.GNO_ALPHATEX', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.default_value = 1.0
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
        var.min_value = -3.4028234663852886e+38
        var.default_value = 0.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-579.4807739257812, -51.96924591064453)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'MULTIPLY'

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
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Group Output"].inputs[0])

    @staticmethod
    def _gno_decal_2():
        tree = bpy.data.node_groups.new('.GNO_DECAL2', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 1.0
        var.hide_value = False
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.default_value = (0.0, 0.0, 0.0, 1.0)
        var.hide_value = False

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.default_value = 0.0
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-379.69573974609375, 269.97735595703125)
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
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (66.75685119628906, 72.56986236572266)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-968.7755737304688, 52.83684158325195)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-149.38858032226562, 229.08718872070312)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-355.97467041015625, 32.785377502441406)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix.006"].inputs[0])

    @staticmethod
    def _gno_specular():
        tree = bpy.data.node_groups.new('.GNO_SPEC', 'ShaderNodeTree')
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
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
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
        var.location = (-730.0899047851562, 390.75653076171875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-390.5513000488281, 91.96931457519531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.blend_type = 'MIX'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-478.46417236328125, 380.19525146484375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.blend_type = 'ADD'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-978.73779296875, 404.60247802734375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-123.7258071899414, 298.9774475097656)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.007"].inputs[2])

    @staticmethod
    def _gno_specular2():
        tree = bpy.data.node_groups.new('.GNO_SPEC2', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Color 2 Multiplier', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Shader Init', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = 0.0

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
        var.location = (-668.1262817382812, 424.3163146972656)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-120.39617919921875, 15.422167778015137)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-247.5244598388672, 315.9359130859375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'ADD'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-863.2249145507812, 436.87457275390625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-3.0931153297424316, 284.1499938964844)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.007"].inputs[2])
