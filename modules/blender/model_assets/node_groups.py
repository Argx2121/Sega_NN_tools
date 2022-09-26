import bpy
from bpy.types import NodeSocket

do_once = True


class MixToList(NodeSocket):
    '''Image Mixing Type'''
    bl_idname = 'MixToList'
    # Label for nice name display
    bl_label = "Image Mix Type"

    # Enum items list
    mix_types = (
        ('0', "Multiply", "Multiply textures"),
        ('1', "Mix", "Mix textures"),
        ('2', "Add", "Add textures"),
        ('3', "Subtract", "Subtract textures"),
    )

    blend_type: bpy.props.EnumProperty(
        name="Texture mix mode",
        description="How to mix textures",
        items=mix_types,
        default='0',
    )

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text="Image Blending:")
        layout.prop(self, "blend_type", text="")
        colour1 = [1, 1, 1]
        colour2 = [1, 1, 1]
        if node.bl_idname == 'ShaderNodeGroup':
            int_blend_type = int(node.inputs['Blend'].blend_type)
            # you cant extract alpha from RGBA, so we will use two vectors instead
            # we can leave the other two slots open for potential other mixing types
            if 3 > int_blend_type:
                colour1[int_blend_type] = 0
            else:
                colour2[int_blend_type - 3] = 0
            if node.inputs['_blend_1'].default_value[:] != colour1:
                node.inputs['_blend_1'].default_value[:] = colour1
            if node.inputs['_blend_2'].default_value[:] != colour2:
                node.inputs['_blend_2'].default_value[:] = colour2

    # Socket color
    def draw_color(self, context, node):
        return (0, 0, 0, 0)


class MakeGroups:
    def __init__(self):
        self.group = None

    def execute(self):
        if "NN Reflection Normal Map" in bpy.data.node_groups:
            return
        self._reflection()
        self._reflection_normal()
        # todo unshaded and black = alpha
        #self._gno()
        #self._gno_alpha()
        #self._gno_unlit()
        #self._gno_unlit_alpha()
        #self._nn_diffuse()
        # self._image_vector()
        self._colour_shader()
        self._nn_shader()
        self._colour_mixer()
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
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.inputs.new('NodeSocketFloatFactor', 'Alpha')
        var.hide_value = False
        var.default_value = 1.0
        var.min_value = 0.0
        var.max_value = 1.0

        var = tree.inputs.new('NodeSocketColor', 'Ambient')
        var.hide_value = False
        var.default_value = (0.7529413104057312, 0.7529413104057312, 0.7529413104057312, 1.0)

        var = tree.inputs.new('NodeSocketColor', 'Specular')
        var.hide_value = False
        var.default_value = (0.8999999761581421, 0.8999999761581421, 0.8999999761581421, 1.0)

        var = tree.inputs.new('NodeSocketColor', 'Emission')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.inputs.new('NodeSocketFloatFactor', 'Specular Gloss')
        var.hide_value = False
        var.default_value = 0.30000001192092896
        var.min_value = 0.0
        var.max_value = 1.0

        var = tree.inputs.new('NodeSocketFloatFactor', 'Specular Level')
        var.hide_value = False
        var.default_value = 2.0
        var.min_value = 0.0
        var.max_value = 2.0

        var = tree.inputs.new('NodeSocketFloat', 'Unshaded')
        var.hide_value = False
        var.default_value = 0.0
        var.min_value = 0.0
        var.max_value = 1.0

        var = tree.inputs.new('NodeSocketFloat', 'Black is alpha')
        var.hide_value = False
        var.default_value = 0.0
        var.min_value = 0.0
        var.max_value = 1.0

        var = tree.inputs.new('NodeSocketVector', 'Normal')
        var.hide_value = True
        var.default_value = (0.0, 0.0, 0.0)
        var.min_value = -3.4028234663852886e+38
        var.max_value = 3.4028234663852886e+38

        # Group outputs
        var = tree.outputs.new('NodeSocketShader', 'BSDF')
        var.hide_value = False

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
        var.blend_type = 'ADD'
        var.use_alpha = False
        var.use_clamp = False

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
        var.blend_type = 'SOFT_LIGHT'
        var.use_alpha = False
        var.use_clamp = False

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
        var.blend_type = 'MIX'
        var.use_alpha = False
        var.use_clamp = False

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
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = True

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
        var.blend_type = 'MIX'
        var.use_alpha = False
        var.use_clamp = False

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

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-2270.0, -141.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        # Properties
        var.operation = 'COMPARE'
        var.use_clamp = False

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
        var.location = (-1300.0, -502.0)
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
        var.blend_type = 'MULTIPLY'
        var.use_alpha = False
        var.use_clamp = False

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.label = ''
        var.height = 100.0
        var.width = 140.0
        var.location = (-1300.0, -308.0)
        var.color = (0.6079999804496765, 0.6079999804496765, 0.6079999804496765)
        var.mute = False
        var.hide = False
        var.use_custom_color = False
        # Inputs
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0
        # Properties
        var.operation = 'COMPARE'
        var.use_clamp = False

        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.label = ''
        var.height = 100.0
        var.width = 177.6005859375
        var.location = (-2547.6005859375, 0.0)
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
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.004"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math"].inputs[1])
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
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[9],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF.001"].inputs[5])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.006"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Math.001"].inputs[0])
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
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[7],
                       bpy.data.node_groups['NN Shader'].nodes["Math.004"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[8],
                       bpy.data.node_groups['NN Shader'].nodes["Math.006"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.004"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Invert.001"].inputs[1])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.006"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.006"].inputs[0])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Group Input"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Mix.003"].inputs[2])
        tree.links.new(bpy.data.node_groups['NN Shader'].nodes["Math.003"].outputs[0],
                       bpy.data.node_groups['NN Shader'].nodes["Specular BSDF"].inputs[2])

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

    def _colour_mixer(self):
        tree = bpy.data.node_groups.new('NN Image Mixer', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.inputs.new('MixToList', 'Blend')
        tree.inputs.new('NodeSocketVector', '_blend_1')
        tree.inputs.new('NodeSocketVector', '_blend_2')
        tree.inputs.new('NodeSocketColor', 'Colour 1')
        tree.inputs.new('NodeSocketFloat', 'Alpha 1')
        tree.inputs.new('NodeSocketColor', 'Colour 2')
        tree.inputs.new('NodeSocketFloat', 'Alpha 2')
        tree.inputs.new('NodeSocketFloat', 'Colour 2 Multiplier')

        tree.inputs['Colour 1'].default_value = (1, 1, 1, 1)
        tree.inputs['Alpha 1'].default_value = 1
        tree.inputs['Colour 2'].default_value = (1, 1, 1, 1)
        tree.inputs['Alpha 2'].default_value = 1
        tree.inputs['Colour 2 Multiplier'].default_value = 1

        tree.inputs['Colour 1'].hide_value = True
        tree.inputs['Alpha 1'].hide_value = True
        tree.inputs['Colour 2'].hide_value = True
        tree.inputs['Alpha 2'].hide_value = True
        tree.inputs['_blend_1'].hide_value = True
        tree.inputs['_blend_2'].hide_value = True

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketColor', 'Colour')
        tree.outputs.new('NodeSocketFloat', 'Alpha')

        add_multi_mix = tree.nodes.new(type="ShaderNodeMixRGB")
        add_multi_mix.blend_type = 'ADD'
        add_multi_mix.inputs[0].default_value = 1
        add_add_subtract = tree.nodes.new(type="ShaderNodeMixRGB")
        add_add_subtract.blend_type = 'ADD'
        add_add_subtract.inputs[0].default_value = 1
        add_mm_as = tree.nodes.new(type="ShaderNodeMixRGB")
        add_mm_as.blend_type = 'ADD'
        add_mm_as.inputs[0].default_value = 1

        multi_col2_col_mult = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_col2_col_mult.blend_type = 'MULTIPLY'
        multi_col2_col_mult.inputs[0].default_value = 1

        alpha_mult = tree.nodes.new(type="ShaderNodeMath")
        alpha_mult.operation = 'MULTIPLY'

        col_col2_multi = tree.nodes.new(type="ShaderNodeMixRGB")
        col_col2_multi.blend_type = 'MULTIPLY'
        col_col2_multi.inputs[0].default_value = 1
        col_col2_mix = tree.nodes.new(type="ShaderNodeMixRGB")
        col_col2_mix.blend_type = 'MIX'
        col_col2_add = tree.nodes.new(type="ShaderNodeMixRGB")
        col_col2_add.blend_type = 'ADD'
        col_col2_add.inputs[0].default_value = 1
        col_col2_sub = tree.nodes.new(type="ShaderNodeMixRGB")
        col_col2_sub.blend_type = 'SUBTRACT'
        col_col2_sub.inputs[0].default_value = 1

        alpha_multi = tree.nodes.new(type="ShaderNodeMixRGB")
        alpha_multi.blend_type = 'MULTIPLY'

        multi_mult = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_mult.blend_type = 'MULTIPLY'
        multi_mult.inputs[2].default_value = (0, 0, 0, 1)
        mix_mult = tree.nodes.new(type="ShaderNodeMixRGB")
        mix_mult.blend_type = 'MULTIPLY'
        mix_mult.inputs[2].default_value = (0, 0, 0, 1)
        add_mult = tree.nodes.new(type="ShaderNodeMixRGB")
        add_mult.blend_type = 'MULTIPLY'
        add_mult.inputs[2].default_value = (0, 0, 0, 1)
        sub_mult = tree.nodes.new(type="ShaderNodeMixRGB")
        sub_mult.blend_type = 'MULTIPLY'
        sub_mult.inputs[2].default_value = (0, 0, 0, 1)
        
        separate_list1 = tree.nodes.new(type="ShaderNodeSeparateXYZ")
        separate_list2 = tree.nodes.new(type="ShaderNodeSeparateXYZ")

        tree.links.new(separate_list1.outputs[0], multi_mult.inputs[0])
        tree.links.new(col_col2_multi.outputs[0], multi_mult.inputs[1])
        tree.links.new(multi_mult.outputs[0], add_multi_mix.inputs[1])
        tree.links.new(separate_list1.outputs[1], mix_mult.inputs[0])
        tree.links.new(col_col2_mix.outputs[0], mix_mult.inputs[1])
        tree.links.new(mix_mult.outputs[0], add_multi_mix.inputs[2])

        tree.links.new(separate_list1.outputs[2], add_mult.inputs[0])
        tree.links.new(col_col2_add.outputs[0], add_mult.inputs[1])
        tree.links.new(add_mult.outputs[0], add_add_subtract.inputs[1])
        tree.links.new(separate_list2.outputs[0], sub_mult.inputs[0])
        tree.links.new(col_col2_sub.outputs[0], sub_mult.inputs[1])
        tree.links.new(sub_mult.outputs[0], add_add_subtract.inputs[2])

        tree.links.new(separate_list1.outputs[1], alpha_multi.inputs[0])
        tree.links.new(group_inputs.outputs['Alpha 1'], alpha_multi.inputs[1])
        tree.links.new(alpha_mult.outputs[0], alpha_multi.inputs[2])
        tree.links.new(alpha_multi.outputs[0], group_outputs.inputs['Alpha'])
        tree.links.new(group_inputs.outputs['Colour 1'], col_col2_multi.inputs[1])
        tree.links.new(multi_col2_col_mult.outputs[0], col_col2_multi.inputs[2])
        tree.links.new(group_inputs.outputs['Alpha 2'], alpha_mult.inputs[0])
        tree.links.new(group_inputs.outputs['Colour 2 Multiplier'], alpha_mult.inputs[1])
        tree.links.new(alpha_mult.outputs[0], col_col2_mix.inputs[0])
        tree.links.new(group_inputs.outputs['Colour 1'], col_col2_mix.inputs[1])
        tree.links.new(multi_col2_col_mult.outputs[0], col_col2_mix.inputs[2])
        tree.links.new(group_inputs.outputs['Colour 1'], col_col2_add.inputs[1])
        tree.links.new(multi_col2_col_mult.outputs[0], col_col2_add.inputs[2])
        tree.links.new(group_inputs.outputs['Colour 1'], col_col2_sub.inputs[1])
        tree.links.new(multi_col2_col_mult.outputs[0], col_col2_sub.inputs[2])
        tree.links.new(group_inputs.outputs['Colour 2'], multi_col2_col_mult.inputs[1])
        tree.links.new(group_inputs.outputs['Colour 2 Multiplier'], multi_col2_col_mult.inputs[2])
        tree.links.new(group_inputs.outputs['_blend_1'], separate_list1.inputs[0])
        tree.links.new(group_inputs.outputs['_blend_2'], separate_list2.inputs[0])
        tree.links.new(add_multi_mix.outputs[0], add_mm_as.inputs[1])
        tree.links.new(add_add_subtract.outputs[0], add_mm_as.inputs[2])
        tree.links.new(add_mm_as.outputs[0], group_outputs.inputs['Colour'])

        # todo group_inputs.inputs[''].hide = True
        #  this has to be done when the node is spawned in blender

    def _image_vector(self):
        tree = bpy.data.node_groups.new('NN Image Vector', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        tree.inputs.new('NodeSocketVector', 'UV / Reflection')
        tree.inputs.new('NodeSocketVector', 'UV Offset')

        tree.inputs['UV / Reflection'].hide_value = True

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketVector', 'Image Vector')

        add_vector = tree.nodes.new(type="ShaderNodeVectorMath")
        add_vector.operation = 'ADD'

        tree.links.new(group_inputs.outputs['UV / Reflection'], add_vector.inputs[0])
        tree.links.new(group_inputs.outputs['UV Offset'], add_vector.inputs[1])
        tree.links.new(add_vector.outputs[0], group_outputs.inputs['Image Vector'])

    def _gno(self):
        tree = bpy.data.node_groups.new('NN GNO Material', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        node_out, multi_alpha_diff_v_col, invert_alpha, _ = self._gno_base(group_inputs, tree)
        tree.links.new(multi_alpha_diff_v_col.outputs[0], invert_alpha.inputs[1])
        tree.links.new(invert_alpha.outputs[0], node_out.inputs[4])

    def _gno_unlit(self):
        tree = bpy.data.node_groups.new('NN GNO Material Unlit', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        node_out, multi_alpha_diff_v_col, invert_alpha, _ = self._gno_unshaded(group_inputs, tree)
        tree.links.new(multi_alpha_diff_v_col.outputs[0], invert_alpha.inputs[1])
        tree.links.new(invert_alpha.outputs[0], node_out.inputs[4])

    def _gno_alpha(self):
        tree = bpy.data.node_groups.new('NN GNO Material Black Alpha', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        node_out, multi_alpha_diff_v_col, invert_alpha, diff_out = self._gno_base(group_inputs, tree)

        sep_hsv = tree.nodes.new(type="ShaderNodeSeparateColor")
        sep_hsv.label = "get value"
        sep_hsv.mode = 'HSV'

        multi_all_alpha = tree.nodes.new(type="ShaderNodeMath")
        multi_all_alpha.label = "multiply all alphas"
        multi_all_alpha.operation = 'MULTIPLY'

        div_alpha = tree.nodes.new(type="ShaderNodeMath")
        div_alpha.label = "divide alpha"
        div_alpha.operation = 'DIVIDE'
        div_alpha.use_clamp = True
        div_alpha.inputs[1].default_value = 0.1

        tree.links.new(diff_out.outputs[0], sep_hsv.inputs[0])
        tree.links.new(sep_hsv.outputs[2], div_alpha.inputs[0])
        tree.links.new(div_alpha.outputs[0], multi_all_alpha.inputs[0])
        tree.links.new(multi_alpha_diff_v_col.outputs[0], multi_all_alpha.inputs[1])
        tree.links.new(multi_all_alpha.outputs[0], invert_alpha.inputs[1])
        tree.links.new(invert_alpha.outputs[0], node_out.inputs[4])

    def _gno_unlit_alpha(self):
        tree = bpy.data.node_groups.new('NN GNO Material Unlit Black Alpha', 'ShaderNodeTree')
        self.group = tree

        group_inputs = tree.nodes.new('NodeGroupInput')
        node_out, multi_alpha_diff_v_col, invert_alpha, diff_out = self._gno_unshaded(group_inputs, tree)

        sep_hsv = tree.nodes.new(type="ShaderNodeSeparateColor")
        sep_hsv.label = "get value"
        sep_hsv.mode = 'HSV'

        multi_all_alpha = tree.nodes.new(type="ShaderNodeMath")
        multi_all_alpha.label = "multiply all alphas"
        multi_all_alpha.operation = 'MULTIPLY'

        div_alpha = tree.nodes.new(type="ShaderNodeMath")
        div_alpha.label = "divide alpha"
        div_alpha.operation = 'DIVIDE'
        div_alpha.use_clamp = True
        div_alpha.inputs[1].default_value = 0.1

        tree.links.new(diff_out.outputs[0], sep_hsv.inputs[0])
        tree.links.new(sep_hsv.outputs[2], div_alpha.inputs[0])
        tree.links.new(div_alpha.outputs[0], multi_all_alpha.inputs[0])
        tree.links.new(multi_alpha_diff_v_col.outputs[0], multi_all_alpha.inputs[1])
        tree.links.new(multi_all_alpha.outputs[0], invert_alpha.inputs[1])
        tree.links.new(invert_alpha.outputs[0], node_out.inputs[4])

    @staticmethod
    def _gno_base(group_inputs, tree):
        tree.inputs.new('NodeSocketColor', 'Diffuse Colour')
        tree.inputs.new('NodeSocketFloat', 'Alpha Value')
        tree.inputs.new('NodeSocketColor', 'Ambient Colour')
        tree.inputs.new('NodeSocketColor', 'Specular Colour')
        tree.inputs.new('NodeSocketFloat', 'Specular Value')
        tree.inputs.new('NodeSocketFloat', 'Shininess Value')
        tree.inputs.new('NodeSocketColor', 'Vertex Colour')
        tree.inputs.new('NodeSocketColor', 'Diffuse Image')
        tree.inputs.new('NodeSocketFloat', 'Diffuse Image Alpha')
        tree.inputs.new('NodeSocketColor', 'Reflection Image')
        tree.inputs.new('NodeSocketColor', 'Emission Image')
        tree.inputs.new('NodeSocketFloat', 'Emission Image Alpha')
        tree.inputs.new('NodeSocketColor', 'Specular Image')
        tree.inputs.new('NodeSocketColor', 'Reflection Multi Image')
        tree.inputs.new('NodeSocketColor', 'Reflection Mask')
        tree.inputs.new('NodeSocketColor', 'Reflection Multi Mask')
        tree.inputs.new('NodeSocketFloat', 'Vertex Alpha')

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketShader', 'Shader Output')
        node_out = tree.nodes.new(type="ShaderNodeEeveeSpecular")
        tree.links.new(node_out.outputs[0], group_outputs.inputs['Shader Output'])

        multi_dif_tex_col = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_dif_tex_col.label = "multiply diffuse texture and colour"
        multi_dif_v_col = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_dif_v_col.label = "multiply diffuse and v colour"
        ao_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        ao_darken = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_spec_image_value = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_spec_image_value.use_clamp = True
        ref_add_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        ref_multi = tree.nodes.new(type="ShaderNodeMixRGB")
        ref_multi_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        ao_colour.label = "apply ambient colour"
        ao_darken.label = "darken ambient"
        multi_spec_image_value.label = "multiply specular image and value"
        ref_add_mask.label = "reflection mask"
        ref_multi.label = "reflection multiply"
        ref_multi_mask.label = "reflection multiply mask"
        multi_dif_tex_col.blend_type = 'MULTIPLY'
        multi_dif_v_col.blend_type = 'MULTIPLY'
        ao_colour.blend_type = 'MULTIPLY'
        ao_darken.blend_type = 'MULTIPLY'
        multi_spec_image_value.blend_type = 'MULTIPLY'
        ref_add_mask.blend_type = 'MULTIPLY'
        ref_multi.blend_type = 'MULTIPLY'
        ref_multi_mask.blend_type = 'MULTIPLY'
        multi_dif_tex_col.inputs[0].default_value = 1
        multi_dif_v_col.inputs[0].default_value = 1
        ao_darken.inputs[0].default_value = 0.8
        multi_spec_image_value.inputs[0].default_value = 1
        ref_add_mask.inputs[0].default_value = 1
        ref_multi.inputs[0].default_value = 1
        ref_multi_mask.inputs[0].default_value = 1
        multi_dif_tex_col.inputs[1].default_value = (1, 1, 1, 1)
        multi_dif_tex_col.inputs[2].default_value = (1, 1, 1, 1)
        multi_dif_v_col.inputs[1].default_value = (1, 1, 1, 1)
        multi_dif_v_col.inputs[2].default_value = (1, 1, 1, 1)
        ao_colour.inputs[2].default_value = (0, 0, 0, 1)
        ao_darken.inputs[2].default_value = (0, 0, 0, 1)
        diff_add_refl = tree.nodes.new(type="ShaderNodeMixRGB")
        diff_add_refl.label = "diffuse add reflection"
        diff_add_refl.blend_type = 'ADD'
        diff_add_refl.inputs[0].default_value = 1
        diff_add_refl.inputs[2].default_value = (0, 0, 0, 1)
        em_diff_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        em_diff_mask.label = "emission diffuse mask"
        em_diff_mask.blend_type = 'MULTIPLY'
        em_diff_mask.inputs[2].default_value = (0, 0, 0, 1)
        em_alpha_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        em_alpha_mask.label = "emission alpha mask"
        em_alpha_mask.blend_type = 'MULTIPLY'
        em_alpha_mask.inputs[0].default_value = 1
        add_diffuse_ambient = tree.nodes.new(type="ShaderNodeMixRGB")
        spec_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        add_diffuse_ambient.blend_type = 'ADD'
        spec_colour.blend_type = 'MULTIPLY'
        add_diffuse_ambient.label = "add diffuse and ambient"
        spec_colour.label = "apply specular colour"
        add_diffuse_ambient.inputs[0].default_value = 1
        add_diffuse_ambient.inputs[1].default_value = (0, 0, 0, 1)
        add_diffuse_ambient.inputs[2].default_value = (0, 0, 0, 1)
        spec_colour.inputs[1].default_value = (0, 0, 0, 1)
        spec_colour.inputs[2].default_value = (1, 1, 1, 1)
        invert_alpha = tree.nodes.new(type="ShaderNodeInvert")
        invert_alpha.label = "invert alpha"
        invert_roughness = tree.nodes.new(type="ShaderNodeInvert")
        invert_roughness.label = "invert roughness"
        ao_multi = tree.nodes.new(type="ShaderNodeMath")
        ao_multi.operation = 'MULTIPLY'
        ao_multi.label = "ambient multiplier"
        ao_multi.inputs[1].default_value = 2
        multi_alpha_tex_col = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha_tex_col.operation = 'MULTIPLY'
        multi_alpha_tex_col.label = "multiply texture alpha and colour alpha"
        multi_alpha_diff_v_col = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha_diff_v_col.operation = 'MULTIPLY'
        multi_alpha_diff_v_col.label = "multiply diffuse alpha and v colour alpha"
        ao = tree.nodes.new(type="ShaderNodeAmbientOcclusion")
        ao.label = "ambient"

        tree.links.new(group_inputs.outputs['Diffuse Image'], multi_dif_tex_col.inputs[2])
        tree.links.new(group_inputs.outputs['Diffuse Image Alpha'], multi_alpha_tex_col.inputs[0])
        tree.links.new(group_inputs.outputs['Diffuse Colour'], multi_dif_tex_col.inputs[1])
        tree.links.new(group_inputs.outputs['Vertex Colour'], multi_dif_v_col.inputs[2])
        tree.links.new(multi_dif_tex_col.outputs[0], multi_dif_v_col.inputs[1])
        tree.links.new(multi_dif_v_col.outputs[0], ao.inputs[0])
        tree.links.new(ao.outputs[0], add_diffuse_ambient.inputs[1])
        tree.links.new(ao.outputs[1], ao_multi.inputs[0])
        tree.links.new(ao_multi.outputs[0], ao_colour.inputs[0])
        tree.links.new(group_inputs.outputs['Ambient Colour'], ao_colour.inputs[1])
        tree.links.new(ao_colour.outputs[0], ao_darken.inputs[1])
        tree.links.new(ao_darken.outputs[0], add_diffuse_ambient.inputs[2])
        tree.links.new(group_inputs.outputs['Reflection Image'], ref_add_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Reflection Mask'], ref_add_mask.inputs[2])
        tree.links.new(group_inputs.outputs['Reflection Multi Image'], ref_multi_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Reflection Multi Mask'], ref_multi_mask.inputs[2])
        tree.links.new(ref_multi_mask.outputs[0], ref_multi.inputs[2])
        tree.links.new(diff_add_refl.outputs[0], ref_multi.inputs[1])
        tree.links.new(ref_add_mask.outputs[0], diff_add_refl.inputs[2])
        tree.links.new(add_diffuse_ambient.outputs[0], diff_add_refl.inputs[1])
        tree.links.new(ref_multi.outputs[0], em_diff_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Emission Image Alpha'], em_diff_mask.inputs[0])
        tree.links.new(em_diff_mask.outputs[0], node_out.inputs[0])
        tree.links.new(group_inputs.outputs['Specular Value'], multi_spec_image_value.inputs[1])
        tree.links.new(group_inputs.outputs['Specular Image'], multi_spec_image_value.inputs[2])
        tree.links.new(multi_spec_image_value.outputs[0], spec_colour.inputs[0])
        tree.links.new(group_inputs.outputs['Alpha Value'], multi_alpha_tex_col.inputs[1])
        tree.links.new(multi_alpha_tex_col.outputs[0], multi_alpha_diff_v_col.inputs[0])
        tree.links.new(group_inputs.outputs['Vertex Alpha'], multi_alpha_diff_v_col.inputs[1])
        tree.links.new(group_inputs.outputs['Specular Colour'], spec_colour.inputs[2])
        tree.links.new(spec_colour.outputs[0], node_out.inputs[1])
        tree.links.new(group_inputs.outputs['Shininess Value'], invert_roughness.inputs[1])
        tree.links.new(invert_roughness.outputs[0], node_out.inputs[2])
        tree.links.new(group_inputs.outputs['Emission Image'], em_alpha_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Emission Image Alpha'], em_alpha_mask.inputs[2])
        tree.links.new(em_alpha_mask.outputs[0], node_out.inputs[3])
        return node_out, multi_alpha_diff_v_col, invert_alpha, em_diff_mask

    @staticmethod
    def _gno_unshaded(group_inputs, tree):
        tree.inputs.new('NodeSocketColor', 'Diffuse Colour')
        tree.inputs.new('NodeSocketFloat', 'Alpha Value')
        tree.inputs.new('NodeSocketColor', 'Ambient Colour')
        tree.inputs.new('NodeSocketColor', 'Specular Colour')
        tree.inputs.new('NodeSocketFloat', 'Specular Value')
        tree.inputs.new('NodeSocketFloat', 'Shininess Value')
        tree.inputs.new('NodeSocketColor', 'Vertex Colour')
        tree.inputs.new('NodeSocketColor', 'Diffuse Image')
        tree.inputs.new('NodeSocketFloat', 'Diffuse Image Alpha')
        tree.inputs.new('NodeSocketColor', 'Reflection Image')
        tree.inputs.new('NodeSocketColor', 'Emission Image')
        tree.inputs.new('NodeSocketFloat', 'Emission Image Alpha')
        tree.inputs.new('NodeSocketColor', 'Specular Image')
        tree.inputs.new('NodeSocketColor', 'Reflection Multi Image')
        tree.inputs.new('NodeSocketColor', 'Reflection Mask')
        tree.inputs.new('NodeSocketColor', 'Reflection Multi Mask')
        tree.inputs.new('NodeSocketFloat', 'Vertex Alpha')

        group_outputs = tree.nodes.new('NodeGroupOutput')
        tree.outputs.new('NodeSocketShader', 'Shader Output')
        node_out = tree.nodes.new(type="ShaderNodeEeveeSpecular")
        tree.links.new(node_out.outputs[0], group_outputs.inputs['Shader Output'])
        node_out.inputs[0].default_value = (0, 0, 0, 1)

        multi_dif_tex_col = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_dif_tex_col.label = "multiply diffuse texture and colour"
        multi_dif_v_col = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_dif_v_col.label = "multiply diffuse and v colour"
        ao_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        ao_darken = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_spec_image_value = tree.nodes.new(type="ShaderNodeMixRGB")
        multi_spec_image_value.use_clamp = True
        ref_add_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        ref_multi = tree.nodes.new(type="ShaderNodeMixRGB")
        ref_multi_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        ao_colour.label = "apply ambient colour"
        ao_darken.label = "darken ambient"
        multi_spec_image_value.label = "multiply specular image and value"
        ref_add_mask.label = "reflection mask"
        ref_multi.label = "reflection multiply"
        ref_multi_mask.label = "reflection multiply mask"
        multi_dif_tex_col.blend_type = 'MULTIPLY'
        multi_dif_v_col.blend_type = 'MULTIPLY'
        ao_colour.blend_type = 'MULTIPLY'
        ao_darken.blend_type = 'MULTIPLY'
        multi_spec_image_value.blend_type = 'MULTIPLY'
        ref_add_mask.blend_type = 'MULTIPLY'
        ref_multi.blend_type = 'MULTIPLY'
        ref_multi_mask.blend_type = 'MULTIPLY'
        multi_dif_tex_col.inputs[0].default_value = 1
        multi_dif_v_col.inputs[0].default_value = 1
        ao_darken.inputs[0].default_value = 0.8
        multi_spec_image_value.inputs[0].default_value = 1
        ref_add_mask.inputs[0].default_value = 1
        ref_multi.inputs[0].default_value = 1
        ref_multi_mask.inputs[0].default_value = 1
        multi_dif_tex_col.inputs[1].default_value = (1, 1, 1, 1)
        multi_dif_tex_col.inputs[2].default_value = (1, 1, 1, 1)
        multi_dif_v_col.inputs[1].default_value = (1, 1, 1, 1)
        multi_dif_v_col.inputs[2].default_value = (1, 1, 1, 1)
        ao_colour.inputs[2].default_value = (0, 0, 0, 1)
        ao_darken.inputs[2].default_value = (0, 0, 0, 1)
        diff_add_refl = tree.nodes.new(type="ShaderNodeMixRGB")
        diff_add_refl.label = "diffuse add reflection"
        diff_add_refl.blend_type = 'ADD'
        diff_add_refl.inputs[0].default_value = 1
        diff_add_refl.inputs[2].default_value = (0, 0, 0, 1)
        em_diff_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        em_diff_mask.label = "emission diffuse mask"
        em_diff_mask.blend_type = 'MULTIPLY'
        em_diff_mask.inputs[2].default_value = (1, 1, 1, 1)
        em_alpha_mask = tree.nodes.new(type="ShaderNodeMixRGB")
        em_alpha_mask.label = "emission alpha mask"
        em_alpha_mask.blend_type = 'MULTIPLY'
        em_alpha_mask.inputs[0].default_value = 1
        add_diffuse_ambient = tree.nodes.new(type="ShaderNodeMixRGB")
        spec_colour = tree.nodes.new(type="ShaderNodeMixRGB")
        add_diffuse_ambient.blend_type = 'ADD'
        spec_colour.blend_type = 'MULTIPLY'
        add_diffuse_ambient.label = "add diffuse and ambient"
        spec_colour.label = "apply specular colour"
        add_diffuse_ambient.inputs[0].default_value = 1
        add_diffuse_ambient.inputs[1].default_value = (0, 0, 0, 1)
        add_diffuse_ambient.inputs[2].default_value = (0, 0, 0, 1)
        spec_colour.inputs[1].default_value = (0, 0, 0, 1)
        spec_colour.inputs[2].default_value = (1, 1, 1, 1)
        invert_alpha = tree.nodes.new(type="ShaderNodeInvert")
        invert_alpha.label = "invert alpha"
        invert_roughness = tree.nodes.new(type="ShaderNodeInvert")
        invert_roughness.label = "invert roughness"
        ao_multi = tree.nodes.new(type="ShaderNodeMath")
        ao_multi.operation = 'MULTIPLY'
        ao_multi.label = "ambient multiplier"
        ao_multi.inputs[1].default_value = 2
        multi_alpha_tex_col = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha_tex_col.operation = 'MULTIPLY'
        multi_alpha_tex_col.label = "multiply texture alpha and colour alpha"
        multi_alpha_diff_v_col = tree.nodes.new(type="ShaderNodeMath")
        multi_alpha_diff_v_col.operation = 'MULTIPLY'
        multi_alpha_diff_v_col.label = "multiply diffuse alpha and v colour alpha"
        ao = tree.nodes.new(type="ShaderNodeAmbientOcclusion")
        ao.label = "ambient"
        em_diff = tree.nodes.new(type="ShaderNodeMixRGB")
        em_diff.label = "emission diffuse mix"
        em_diff.blend_type = 'MULTIPLY'
        em_diff.inputs[0].default_value = 1

        tree.links.new(group_inputs.outputs['Diffuse Image'], multi_dif_tex_col.inputs[2])
        tree.links.new(group_inputs.outputs['Diffuse Image Alpha'], multi_alpha_tex_col.inputs[0])
        tree.links.new(group_inputs.outputs['Diffuse Colour'], multi_dif_tex_col.inputs[1])
        tree.links.new(group_inputs.outputs['Vertex Colour'], multi_dif_v_col.inputs[2])
        tree.links.new(multi_dif_tex_col.outputs[0], multi_dif_v_col.inputs[1])
        tree.links.new(multi_dif_v_col.outputs[0], ao.inputs[0])
        tree.links.new(ao.outputs[0], add_diffuse_ambient.inputs[1])
        tree.links.new(ao.outputs[1], ao_multi.inputs[0])
        tree.links.new(ao_multi.outputs[0], ao_colour.inputs[0])
        tree.links.new(group_inputs.outputs['Ambient Colour'], ao_colour.inputs[1])
        tree.links.new(ao_colour.outputs[0], ao_darken.inputs[1])
        tree.links.new(ao_darken.outputs[0], add_diffuse_ambient.inputs[2])
        tree.links.new(group_inputs.outputs['Reflection Image'], ref_add_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Reflection Mask'], ref_add_mask.inputs[2])
        tree.links.new(group_inputs.outputs['Reflection Multi Image'], ref_multi_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Reflection Multi Mask'], ref_multi_mask.inputs[2])
        tree.links.new(ref_multi_mask.outputs[0], ref_multi.inputs[2])
        tree.links.new(diff_add_refl.outputs[0], ref_multi.inputs[1])
        tree.links.new(ref_add_mask.outputs[0], diff_add_refl.inputs[2])
        tree.links.new(add_diffuse_ambient.outputs[0], diff_add_refl.inputs[1])
        tree.links.new(ref_multi.outputs[0], em_diff_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Emission Image Alpha'], em_diff_mask.inputs[0])
        tree.links.new(group_inputs.outputs['Specular Value'], multi_spec_image_value.inputs[1])
        tree.links.new(group_inputs.outputs['Specular Image'], multi_spec_image_value.inputs[2])
        tree.links.new(multi_spec_image_value.outputs[0], spec_colour.inputs[0])
        tree.links.new(group_inputs.outputs['Alpha Value'], multi_alpha_tex_col.inputs[1])
        tree.links.new(multi_alpha_tex_col.outputs[0], multi_alpha_diff_v_col.inputs[0])
        tree.links.new(group_inputs.outputs['Vertex Alpha'], multi_alpha_diff_v_col.inputs[1])
        tree.links.new(group_inputs.outputs['Specular Colour'], spec_colour.inputs[2])
        tree.links.new(spec_colour.outputs[0], node_out.inputs[1])
        tree.links.new(group_inputs.outputs['Shininess Value'], invert_roughness.inputs[1])
        tree.links.new(invert_roughness.outputs[0], node_out.inputs[2])
        tree.links.new(group_inputs.outputs['Emission Image'], em_alpha_mask.inputs[1])
        tree.links.new(group_inputs.outputs['Emission Image Alpha'], em_alpha_mask.inputs[2])
        tree.links.new(em_diff_mask.outputs[0], em_diff.inputs[1])
        tree.links.new(em_alpha_mask.outputs[0], em_diff.inputs[2])
        tree.links.new(em_diff.outputs[0], node_out.inputs[3])
        return node_out, multi_alpha_diff_v_col, invert_alpha, em_diff
