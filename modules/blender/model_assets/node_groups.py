import bpy


class MakeGroups:
    def __init__(self):
        pass

    def execute(self):
        if '.NN_VECTOR_UV' in bpy.data.node_groups:
            return
        # GENERAL
        self._nn_uv()
        self._nn_pos()
        self._nn_normal()
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
    def _nn_uv():
        tree = bpy.data.node_groups.new('.NN_VECTOR_UV', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='UV Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Offset', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Rotation', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Scale', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (1.0, 1.0, 1.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='U', in_out='INPUT', socket_type='NodeSocketInt')
        var.max_value = 2
        var.default_value = 0
        var.hide_value = False
        var.min_value = 0

        var = tree.interface.new_socket(name='V', in_out='INPUT', socket_type='NodeSocketInt')
        var.max_value = 2
        var.default_value = 0
        var.hide_value = False
        var.min_value = 0

        var = tree.interface.new_socket(name='Normal Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (5.0, 5.0, 5.0)
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        # Group outputs
        var = tree.interface.new_socket(name='Image Vector', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-151.57119750976562, 22.959325790405273)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-3336.397705078125, -375.6051025390625)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.0, 0.0, 0.0)
        var.outputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[4].default_value = 0
        var.outputs[5].default_value = 0
        var.outputs[6].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp'
        var.location = (-1500.8118896484375, -231.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-1500.8118896484375, -660.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'PINGPONG'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ'
        var.location = (-1856.559326171875, -446.2098693847656)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ'
        var.location = (-401.0297546386719, 20.49124526977539)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-1650.0, 0.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-1225.8118896484375, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-1650.0, -431.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-1225.8118896484375, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-1375.0, -410.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (-950.8118896484375, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.location = (-950.8118896484375, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.location = (-675.8116455078125, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp.001'
        var.location = (-1753.1373291015625, -1039.0703125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.009'
        var.location = (-1731.9381103515625, -1227.345458984375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'PINGPONG'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.010'
        var.location = (-1475.6424560546875, -1053.4573974609375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.011'
        var.location = (-1123.3695068359375, -1058.9755859375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.012'
        var.location = (-1475.99267578125, -1245.1146240234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.013'
        var.location = (-1125.521728515625, -1264.8226318359375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.014'
        var.location = (-1483.2957763671875, -1442.364990234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.015'
        var.location = (-1117.843505859375, -1449.6419677734375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.016'
        var.location = (-909.7049560546875, -1073.7642822265625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.017'
        var.location = (-914.1976318359375, -1293.130615234375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMapping')
        var.name = 'Mapping'
        var.location = (-2629.74560546875, -144.9802703857422)
        var.inputs[0].default_value = (0.0, -15.59999942779541, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.vector_type = 'TEXTURE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math'
        var.location = (-2864.761962890625, -140.9693603515625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.001'
        var.location = (-2403.07080078125, -356.68243408203125)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ.001'
        var.location = (-3048.33203125, 56.45307540893555)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ.001'
        var.location = (-2599.334716796875, 116.958740234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.018'
        var.location = (-2803.10107421875, 18.493255615234375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'SUBTRACT'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.019'
        var.location = (-591.6944580078125, -189.5094757080078)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'SUBTRACT'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Clamp"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Clamp"].outputs[0], tree.nodes["Math.002"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.005"].inputs[0])
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
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.010"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.012"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.014"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mapping"].inputs[2])
        tree.links.new(tree.nodes["Vector Math.001"].outputs[0], tree.nodes["Separate XYZ"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Vector Math"].inputs[1])
        tree.links.new(tree.nodes["Vector Math"].outputs[0], tree.nodes["Mapping"].inputs[0])
        tree.links.new(tree.nodes["Mapping"].outputs[0], tree.nodes["Vector Math.001"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Vector Math.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Separate XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[1], tree.nodes["Math.018"].inputs[1])
        tree.links.new(tree.nodes["Math.018"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[1])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ.001"].outputs[0], tree.nodes["Vector Math"].inputs[0])
        tree.links.new(tree.nodes["Math.017"].outputs[0], tree.nodes["Math.019"].inputs[1])
        tree.links.new(tree.nodes["Math.019"].outputs[0], tree.nodes["Combine XYZ"].inputs[1])

    @staticmethod
    def _nn_pos():
        tree = bpy.data.node_groups.new('.NN_VECTOR_POSITION', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='UV Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Offset', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Rotation', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='UV Scale', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (1.0, 1.0, 1.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='U', in_out='INPUT', socket_type='NodeSocketInt')
        var.max_value = 2
        var.default_value = 0
        var.hide_value = False
        var.min_value = 0

        var = tree.interface.new_socket(name='V', in_out='INPUT', socket_type='NodeSocketInt')
        var.max_value = 2
        var.default_value = 0
        var.hide_value = False
        var.min_value = 0

        var = tree.interface.new_socket(name='Normal Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (5.0, 5.0, 5.0)
        var.hide_value = True
        var.min_value = -3.4028234663852886e+38

        # Group outputs
        var = tree.interface.new_socket(name='Image Vector', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)
        var.hide_value = False
        var.min_value = -3.4028234663852886e+38

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (-151.57119750976562, 22.959325790405273)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-3035.48583984375, -391.02630615234375)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.0, 0.0, 0.0)
        var.outputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[4].default_value = 0
        var.outputs[5].default_value = 0
        var.outputs[6].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp'
        var.location = (-1500.8118896484375, -231.0)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-1500.8118896484375, -660.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'PINGPONG'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ'
        var.location = (-1856.559326171875, -446.2098693847656)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ'
        var.location = (-401.0297546386719, 20.49124526977539)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-1650.0, 0.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-1225.8118896484375, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-1650.0, -431.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-1225.8118896484375, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-1375.0, -410.0)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (-950.8118896484375, -206.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.location = (-950.8118896484375, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.location = (-675.8116455078125, 0.0)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp.001'
        var.location = (-1753.1373291015625, -1039.0703125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.009'
        var.location = (-1731.9381103515625, -1227.345458984375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'PINGPONG'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.010'
        var.location = (-1475.6424560546875, -1053.4573974609375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.011'
        var.location = (-1123.3695068359375, -1058.9755859375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.012'
        var.location = (-1475.99267578125, -1245.1146240234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.013'
        var.location = (-1125.521728515625, -1264.8226318359375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.014'
        var.location = (-1483.2957763671875, -1442.364990234375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.015'
        var.location = (-1117.843505859375, -1449.6419677734375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.016'
        var.location = (-909.7049560546875, -1073.7642822265625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.017'
        var.location = (-914.1976318359375, -1293.130615234375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'ADD'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMapping')
        var.name = 'Mapping'
        var.location = (-2629.74560546875, -144.9802703857422)
        var.inputs[0].default_value = (0.0, -15.59999942779541, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.vector_type = 'TEXTURE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math'
        var.location = (-2864.761962890625, -140.9693603515625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.001'
        var.location = (-2403.07080078125, -356.68243408203125)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeNewGeometry')
        var.name = 'Geometry'
        var.location = (-4143.07666015625, -339.3970031738281)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.0, 0.0, 0.0)
        var.outputs[3].default_value = (0.0, 0.0, 0.0)
        var.outputs[4].default_value = (0.0, 0.0, 0.0)
        var.outputs[5].default_value = (0.0, 0.0, 0.0)
        var.outputs[6].default_value = 0.0
        var.outputs[7].default_value = 0.0
        var.outputs[8].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeObjectInfo')
        var.name = 'Object Info'
        var.location = (-3953.921142578125, -461.4044494628906)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.outputs[2].default_value = 0.0
        var.outputs[3].default_value = 0.0
        var.outputs[4].default_value = 0.0
        var.outputs[5].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.002'
        var.location = (-3730.725830078125, -342.44647216796875)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'SUBTRACT'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.018'
        var.location = (-691.346435546875, -205.9686279296875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'SUBTRACT'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ.001'
        var.location = (-3559.875, -164.35301208496094)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ.001'
        var.location = (-3110.87744140625, -103.84733581542969)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.019'
        var.location = (-3314.643798828125, -202.31283569335938)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.operation = 'SUBTRACT'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Clamp"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Clamp"].outputs[0], tree.nodes["Math.002"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math.005"].inputs[0])
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
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.010"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.012"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Math.014"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mapping"].inputs[2])
        tree.links.new(tree.nodes["Vector Math.001"].outputs[0], tree.nodes["Separate XYZ"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Vector Math"].inputs[1])
        tree.links.new(tree.nodes["Vector Math"].outputs[0], tree.nodes["Mapping"].inputs[0])
        tree.links.new(tree.nodes["Mapping"].outputs[0], tree.nodes["Vector Math.001"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Vector Math.001"].inputs[1])
        tree.links.new(tree.nodes["Object Info"].outputs[0], tree.nodes["Vector Math.002"].inputs[1])
        tree.links.new(tree.nodes["Geometry"].outputs[0], tree.nodes["Vector Math.002"].inputs[0])
        tree.links.new(tree.nodes["Math.017"].outputs[0], tree.nodes["Math.018"].inputs[1])
        tree.links.new(tree.nodes["Math.018"].outputs[0], tree.nodes["Combine XYZ"].inputs[1])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[1], tree.nodes["Math.019"].inputs[1])
        tree.links.new(tree.nodes["Math.019"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[1])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.002"].outputs[0], tree.nodes["Separate XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ.001"].outputs[0], tree.nodes["Vector Math"].inputs[0])

    @staticmethod
    def _nn_normal():
        # thanks to firegodjr for the vector node set up
        tree = bpy.data.node_groups.new('.NN_VECTOR_NORMAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='UV Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        var = tree.interface.new_socket(name='UV Offset', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        var = tree.interface.new_socket(name='UV Rotation', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        var = tree.interface.new_socket(name='UV Scale', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = (1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='U', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = 0
        var.hide_value = False
        var.max_value = 2
        var.default_value = 0

        var = tree.interface.new_socket(name='V', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = 0
        var.hide_value = False
        var.max_value = 2
        var.default_value = 0

        var = tree.interface.new_socket(name='Normal Map', in_out='INPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = (5.0, 5.0, 5.0)

        # Group outputs
        var = tree.interface.new_socket(name='Image Vector', in_out='OUTPUT', socket_type='NodeSocketVector')
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False
        var.max_value = 3.4028234663852886e+38
        var.default_value = (0.0, 0.0, 0.0)

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeNewGeometry')
        var.name = 'Geometry.001'
        var.location = (-3957.56591796875, -282.6197814941406)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.0, 0.0, 0.0)
        var.outputs[3].default_value = (0.0, 0.0, 0.0)
        var.outputs[4].default_value = (0.0, 0.0, 0.0)
        var.outputs[5].default_value = (0.0, 0.0, 0.0)
        var.outputs[6].default_value = 0.0
        var.outputs[7].default_value = 0.0
        var.outputs[8].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCameraData')
        var.name = 'Camera Data'
        var.location = (-2800.01611328125, -493.9341735839844)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ'
        var.location = (-1975.016357421875, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ'
        var.location = (-1425.016357421875, -195.9341278076172)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeVectorTransform')
        var.name = 'Vector Transform'
        var.location = (-2525.01611328125, -195.9341278076172)
        var.inputs[0].default_value = (0.5, 0.5, 0.5)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.convert_from = 'WORLD'
        var.convert_to = 'CAMERA'
        var.vector_type = 'NORMAL'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-1700.016357421875, -195.9341278076172)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = -1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeValue')
        var.name = 'Value'
        var.location = (-875.01611328125, -370.93414306640625)
        var.outputs[0].default_value = 0.4950000047683716

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math'
        var.location = (-2525.01611328125, -401.93414306640625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'NORMALIZE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.001'
        var.location = (-2250.01611328125, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'CROSS_PRODUCT'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.003'
        var.location = (-1150.01611328125, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'LENGTH'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.004'
        var.location = (-1150.01611328125, -341.93414306640625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'NORMALIZE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.005'
        var.location = (-875.01611328125, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.006'
        var.location = (-600.01611328125, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.007'
        var.location = (-325.0162048339844, -195.9341278076172)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.5, 0.5, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'ADD'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output.001'
        var.location = (1905.703369140625, 55.996681213378906)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input.001'
        var.location = (-4176.6435546875, -730.2864990234375)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.0, 0.0, 0.0)
        var.outputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[4].default_value = 0
        var.outputs[5].default_value = 0
        var.outputs[6].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp'
        var.location = (556.462646484375, -197.962646484375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (556.462646484375, -626.9625244140625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'PINGPONG'

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ.001'
        var.location = (200.7153778076172, -413.1724548339844)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeCombineXYZ')
        var.name = 'Combine XYZ.001'
        var.location = (1656.244873046875, 53.528564453125)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (407.2745666503906, 33.037353515625)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (831.4627075195312, 33.037353515625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (407.2745666503906, -397.9624938964844)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (831.4627075195312, -172.962646484375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (682.2745361328125, -376.9624938964844)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.location = (1106.462646484375, -172.962646484375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.location = (1106.462646484375, 33.037353515625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.009'
        var.location = (1381.462890625, 33.037353515625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeClamp')
        var.name = 'Clamp.001'
        var.location = (304.13726806640625, -1006.0328369140625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 1.0
        var.outputs[0].default_value = 0.0
        var.clamp_type = 'MINMAX'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.010'
        var.location = (325.33648681640625, -1194.30810546875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'PINGPONG'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.011'
        var.location = (581.6322021484375, -1020.419921875)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.012'
        var.location = (933.9050903320312, -1025.938232421875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.013'
        var.location = (581.2818603515625, -1212.077392578125)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 2.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.014'
        var.location = (931.7529296875, -1231.7852783203125)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.015'
        var.location = (573.9788818359375, -1409.327880859375)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.016'
        var.location = (939.4310302734375, -1416.604736328125)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.017'
        var.location = (1147.5697021484375, -1040.7269287109375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.018'
        var.location = (1143.076904296875, -1260.09326171875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMapping')
        var.name = 'Mapping'
        var.location = (-3050.29150390625, -84.5123519897461)
        var.inputs[0].default_value = (0.0, -15.59999942779541, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = (1.0, 1.0, 1.0)
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.vector_type = 'TEXTURE'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.002'
        var.location = (-3285.307861328125, -80.50141906738281)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeVectorMath')
        var.name = 'Vector Math.008'
        var.location = (-2823.616455078125, -296.214599609375)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.inputs[1].default_value = (0.0, 0.0, 0.0)
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 1.0
        var.outputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[1].default_value = 0.0
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeSeparateXYZ')
        var.name = 'Separate XYZ.002'
        var.location = (-4113.5185546875, -166.445556640625)
        var.inputs[0].default_value = (0.0, 0.0, 0.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = 0.0
        var.outputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.019'
        var.location = (-3868.518798828125, -18.335582733154297)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 4.0
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = True
        var.operation = 'GREATER_THAN'

        var = tree.nodes.new(type='ShaderNodeMix')
        var.name = 'Mix'
        var.location = (-3645.818359375, 52.8546257019043)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5)
        var.inputs[2].default_value = 0.0
        var.inputs[3].default_value = 0.0
        var.inputs[4].default_value = (0.0, 0.0, 0.0)
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = 0.0
        var.outputs[1].default_value = (0.0, 0.0, 0.0)
        var.outputs[2].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.factor_mode = 'UNIFORM'
        var.data_type = 'VECTOR'
        var.clamp_factor = True
        var.blend_type = 'MIX'
        var.clamp_result = False

        # Group Node links
        tree.links.new(tree.nodes["Vector Transform"].outputs[0], tree.nodes["Vector Math.001"].inputs[0])
        tree.links.new(tree.nodes["Camera Data"].outputs[0], tree.nodes["Vector Math"].inputs[0])
        tree.links.new(tree.nodes["Vector Math"].outputs[0], tree.nodes["Vector Math.001"].inputs[1])
        tree.links.new(tree.nodes["Vector Math.001"].outputs[0], tree.nodes["Separate XYZ"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.001"].outputs[0], tree.nodes["Vector Math.003"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ"].outputs[0], tree.nodes["Combine XYZ"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Combine XYZ"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ"].outputs[0], tree.nodes["Vector Math.004"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.003"].outputs[1], tree.nodes["Vector Math.005"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.004"].outputs[0], tree.nodes["Vector Math.005"].inputs[1])
        tree.links.new(tree.nodes["Vector Math.005"].outputs[0], tree.nodes["Vector Math.006"].inputs[0])
        tree.links.new(tree.nodes["Value"].outputs[0], tree.nodes["Vector Math.006"].inputs[1])
        tree.links.new(tree.nodes["Vector Math.006"].outputs[0], tree.nodes["Vector Math.007"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[0], tree.nodes["Clamp"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[4], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Clamp"].outputs[0], tree.nodes["Math.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input.001"].outputs[4], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Math.005"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input.001"].outputs[4], tree.nodes["Math.006"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[0], tree.nodes["Math.007"].inputs[1])
        tree.links.new(tree.nodes["Math.006"].outputs[0], tree.nodes["Math.007"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.008"].inputs[0])
        tree.links.new(tree.nodes["Math.005"].outputs[0], tree.nodes["Math.008"].inputs[1])
        tree.links.new(tree.nodes["Math.008"].outputs[0], tree.nodes["Math.009"].inputs[0])
        tree.links.new(tree.nodes["Math.007"].outputs[0], tree.nodes["Math.009"].inputs[1])
        tree.links.new(tree.nodes["Math.009"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Math.011"].outputs[0], tree.nodes["Math.012"].inputs[0])
        tree.links.new(tree.nodes["Clamp.001"].outputs[0], tree.nodes["Math.012"].inputs[1])
        tree.links.new(tree.nodes["Math.013"].outputs[0], tree.nodes["Math.014"].inputs[0])
        tree.links.new(tree.nodes["Math.010"].outputs[0], tree.nodes["Math.014"].inputs[1])
        tree.links.new(tree.nodes["Math.015"].outputs[0], tree.nodes["Math.016"].inputs[0])
        tree.links.new(tree.nodes["Math.012"].outputs[0], tree.nodes["Math.017"].inputs[0])
        tree.links.new(tree.nodes["Math.014"].outputs[0], tree.nodes["Math.017"].inputs[1])
        tree.links.new(tree.nodes["Math.017"].outputs[0], tree.nodes["Math.018"].inputs[0])
        tree.links.new(tree.nodes["Math.016"].outputs[0], tree.nodes["Math.018"].inputs[1])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[1], tree.nodes["Math.010"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[1], tree.nodes["Clamp.001"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.001"].outputs[1], tree.nodes["Math.016"].inputs[1])
        tree.links.new(tree.nodes["Group Input.001"].outputs[5], tree.nodes["Math.011"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[5], tree.nodes["Math.013"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[5], tree.nodes["Math.015"].inputs[0])
        tree.links.new(tree.nodes["Combine XYZ.001"].outputs[0], tree.nodes["Group Output.001"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[2], tree.nodes["Mapping"].inputs[2])
        tree.links.new(tree.nodes["Group Input.001"].outputs[3], tree.nodes["Vector Math.002"].inputs[1])
        tree.links.new(tree.nodes["Vector Math.002"].outputs[0], tree.nodes["Mapping"].inputs[0])
        tree.links.new(tree.nodes["Mapping"].outputs[0], tree.nodes["Vector Math.008"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[0], tree.nodes["Vector Math.008"].inputs[1])
        tree.links.new(tree.nodes["Vector Math.008"].outputs[0], tree.nodes["Vector Transform"].inputs[0])
        tree.links.new(tree.nodes["Vector Math.007"].outputs[0], tree.nodes["Separate XYZ.001"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[6], tree.nodes["Separate XYZ.002"].inputs[0])
        tree.links.new(tree.nodes["Separate XYZ.002"].outputs[0], tree.nodes["Math.019"].inputs[0])
        tree.links.new(tree.nodes["Math.019"].outputs[0], tree.nodes["Mix"].inputs[0])
        tree.links.new(tree.nodes["Group Input.001"].outputs[6], tree.nodes["Mix"].inputs[4])
        tree.links.new(tree.nodes["Geometry.001"].outputs[1], tree.nodes["Mix"].inputs[5])
        tree.links.new(tree.nodes["Mix"].outputs[1], tree.nodes["Vector Math.002"].inputs[0])
        tree.links.new(tree.nodes["Math.018"].outputs[0], tree.nodes["Combine XYZ.001"].inputs[1])

    @staticmethod
    def _gno_shader():
        tree = bpy.data.node_groups.new('.GNO_SHADER', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Disable Fog', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Callback', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Hide', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='User', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = -2147483648
        var.hide_value = False
        var.max_value = 2147483647
        var.default_value = 0

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
        var.outputs[0].default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[5].default_value = 0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-2031.972412109375, 173.82437133789062)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = True
        var.operation = 'SUBTRACT'

        # Group Node links
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix Shader"].inputs[0])

    @staticmethod
    def _xno_shader():
        tree = bpy.data.node_groups.new('.XNO_SHADER', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.interface.new_socket(name='Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Disable Fog', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Callback', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='Hide', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        var = tree.interface.new_socket(name='User', in_out='INPUT', socket_type='NodeSocketInt')
        var.min_value = -2147483648
        var.hide_value = False
        var.max_value = 2147483647
        var.default_value = 0

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
        var.outputs[0].default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[5].default_value = 0

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-2031.972412109375, 173.82437133789062)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.outputs[0].default_value = 0.0
        var.use_clamp = True
        var.operation = 'SUBTRACT'

        # Group Node links
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Math"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Mix Shader"].inputs[0])

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
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False
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
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.default_value = 0.0

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (92.06084442138672, -6.5836615562438965)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-669.0877685546875, -169.91989135742188)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-459.156982421875, 284.64276123046875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-709.8973388671875, 273.84515380859375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-146.5705108642578, 122.07246398925781)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-152.9092254638672, -72.77555084228516)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[0])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])

    @staticmethod
    def _gno_decal():
        tree = bpy.data.node_groups.new('.GNO_DECAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False
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
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.default_value = 0.0

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-663.119384765625, 280.70654296875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (29.5909366607666, 19.750957489013672)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-960.0, 0.0)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-467.38934326171875, 284.739013671875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-202.46466064453125, 148.04615783691406)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.003"].inputs[1])

    @staticmethod
    def _gno_add():
        tree = bpy.data.node_groups.new('.GNO_ADD', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38
        var.hide_value = True
        var.default_value = 1.0

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.min_value = 0.0
        var.max_value = 1.0
        var.hide_value = False
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
        var.max_value = 3.4028234663852886e+38
        var.hide_value = False
        var.default_value = 0.0

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-658.7831420898438, -172.1836700439453)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-671.2577514648438, 332.76019287109375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-965.0628662109375, 13.172920227050781)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (168.19419860839844, 105.3892593383789)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-97.21885681152344, 206.30654907226562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-424.9624938964844, 335.003173828125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-102.6130599975586, 4.491642951965332)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.003"].inputs[0])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.005"].inputs[0])

    @staticmethod
    def _gno_sub():
        tree = bpy.data.node_groups.new('.GNO_SUB', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 1.0
        var.min_value = 0.0
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
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-439.9923400878906, 270.1305236816406)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'SUBTRACT'
        var.use_alpha = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (279.53411865234375, -9.754495620727539)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.location = (-674.7991333007812, -103.10804748535156)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-986.8014526367188, 30.104755401611328)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-202.0596466064453, 256.00189208984375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (68.16622924804688, 143.22174072265625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MIX'
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.005"].inputs[0])

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
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 1.0
        var.min_value = 0.0
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
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
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
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-652.1366577148438, 165.6847686767578)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-493.03009033203125, -49.43866729736328)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MIX'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-291.39459228515625, 183.46327209472656)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MIX'
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.006"].inputs[0])

    @staticmethod
    def _gno_blend():
        tree = bpy.data.node_groups.new('.GNO_BLEND', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Color 1', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 1', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Color 2', in_out='INPUT', socket_type='NodeSocketColor')
        var.default_value = (1.0, 1.0, 1.0, 1.0)
        var.hide_value = True

        var = tree.interface.new_socket(name='Alpha 2', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = True

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
        var.default_value = 1.0
        var.max_value = 1.0
        var.min_value = 0.0
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
        var.max_value = 3.4028234663852886e+38
        var.min_value = -3.4028234663852886e+38
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (509.00518798828125, 164.19528198242188)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-999.7333984375, 20.390748977661133)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-127.5120849609375, 323.42413330078125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-435.01300048828125, -56.5857048034668)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-746.3284912109375, 344.4493713378906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'SUBTRACT'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-524.989990234375, 349.2527160644531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-324.7580871582031, 344.9975280761719)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'ADD'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (198.2682342529297, 54.795021057128906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.011'
        var.location = (201.30722045898438, 236.0465850830078)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.011"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.010"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.010"].inputs[0])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.011"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.011"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.011"].inputs[1])

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

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
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

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
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
        var = tree.interface.new_socket(name='Color 1', description='', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 1', description='', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Color 2', description='', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Alpha 2', description='', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 3.4028234663852886e+38
        var.default_value = 1.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Factor', description='', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = False
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Shader Init', description='', in_out='INPUT',
                                        socket_type='NodeSocketColor')
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
        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.location = (-560.859375, 334.3659362792969)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (275.31573486328125, 71.31949615478516)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-968.7755737304688, 52.83684158325195)
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = 1.0
        var.outputs[5].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-343.2276916503906, 324.3567199707031)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-608.76171875, -142.90650939941406)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (7.028472900390625, -6.452939033508301)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (6.399991989135742, 183.3028564453125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.blend_type = 'MIX'
        var.use_clamp = False

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.007"].inputs[0])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.008"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.005"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])

    @staticmethod
    def _gno_specular():
        tree = bpy.data.node_groups.new('.GNO_SPEC', 'ShaderNodeTree')
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
        var.default_value = 0.0
        var.min_value = -3.4028234663852886e+38

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
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
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 0.0
        var.outputs[4].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[5].default_value = 1.0
        var.outputs[6].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (93.70707702636719, 178.97238159179688)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-890.2716064453125, 521.1539306640625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-776.3517456054688, -31.350902557373047)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-694.0357666015625, 459.63275146484375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-150.968505859375, 277.09112548828125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-462.99090576171875, 449.8458557128906)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (-153.2354278564453, 95.23942565917969)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[0])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.010"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.010"].inputs[1])

    @staticmethod
    def _gno_specular2():
        tree = bpy.data.node_groups.new('.GNO_SPEC2', 'ShaderNodeTree')
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

        var = tree.interface.new_socket(name='Factor', in_out='INPUT', socket_type='NodeSocketFloat')
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
        var.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[1].default_value = 1.0
        var.outputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[3].default_value = 1.0
        var.outputs[4].default_value = (1.0, 1.0, 1.0, 1.0)
        var.outputs[5].default_value = 1.0
        var.outputs[6].default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (188.0198974609375, 181.97006225585938)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = 0.0
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.004'
        var.location = (-918.98095703125, 463.43316650390625)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-647.645263671875, -36.772850036621094)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.location = (-682.1365356445312, 464.17901611328125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.location = (-116.65190124511719, 342.59490966796875)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.009'
        var.location = (-473.3382873535156, 448.3706970214844)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (-122.7059326171875, 162.6301727294922)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.outputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.use_alpha = False
        var.use_clamp = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.004"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Group Output"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.009"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.009"].inputs[1])
        tree.links.new(tree.nodes["Mix.004"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.004"].inputs[1])
        tree.links.new(tree.nodes["Mix.009"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.008"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.010"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.010"].inputs[0])
