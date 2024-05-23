import bpy
import nodeitems_utils
from bpy.props import EnumProperty, BoolProperty
from bpy.types import ShaderNodeCustomGroup
from nodeitems_utils import NodeItem
# blender crashing after reloading script is an issue with custom nodes
#  https://projects.blender.org/blender/blender/issues/72833


class MyNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


class CustomNodetreeNodeBaseNN:
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        if not self.node_tree.users > 1:
            bpy.data.node_groups.remove(self.node_tree)

    def draw_buttons(self, context, layout):
        for prop in self.bl_rna.properties:
            if prop.is_runtime and not prop.is_readonly:
                if prop.type == "ENUM":
                    text = ""
                else:
                    text = prop.name
                layout.prop(self, prop.identifier, text=text)


class CustomNodetreeNodeBaseNNExpandLink:
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        if not self.node_tree.users > 1:
            bpy.data.node_groups.remove(self.node_tree)

    def draw_buttons(self, context, layout):
        for prop in self.bl_rna.properties:
            if prop.is_runtime and not prop.is_readonly:
                text = prop.name
                for link in self.id_data.links:
                    if link.to_socket == self.inputs["Unshaded"]:
                        return
                layout.prop(self, prop.identifier, text=text, expand=True)


class ShaderNodeNNMixRGB(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN MixRGB"
    bl_width_default = 180

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('_NN_RGB_MULTI', "Multiply", ""),
            ('_NN_RGB_MIX', "Mix", ""),
            ('_NN_RGB_ADD', "Add", ""),
            ('_NN_RGB_SUB', "Subtract", ""),
        )
        return mix_types

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass  # defining this so blender doesn't try to remove the group

    def update_props(self, context):
        if not self.blend_type:
            self.blend_type = self.blend_types(context)[0][0]

        self.node_tree = bpy.data.node_groups[self.blend_type]

    def update_shading(self, context):
        if self.multi_shading:
            for node in self.id_data.nodes:
                if node.bl_idname == "ShaderNodeNNShaderInit":
                    self.id_data.links.new(node.outputs["Diffuse Color"], self.inputs["Shader Init"])
                    break
        else:
            for link in self.id_data.links:
                if link.to_socket == self.inputs["Shader Init"]:
                    self.id_data.links.remove(link)
                    break
        self.inputs["Shader Init"].hide = True

    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types)
    multi_shading: BoolProperty(name="Use Shading Init", update=update_shading, default=False)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_RGB_MULTI']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True


class ShaderNodeNNShader(CustomNodetreeNodeBaseNNExpandLink, ShaderNodeCustomGroup):
    bl_label = "NN Shader"
    bl_width_default = 180

    def update_props(self, context):
        for node in self.id_data.nodes:
            if node.bl_idname == "ShaderNodeNNShaderInit":
                self.id_data.links.new(node.outputs["Unshaded"], self.inputs["Unshaded"])
                node_inputs = [node.to_socket for node in self.id_data.links]
                if self.inputs["Colour"] not in node_inputs:
                    self.id_data.links.new(node.outputs["Diffuse Color"], self.inputs["Colour"])
                if self.inputs["Alpha"] not in node_inputs:
                    self.id_data.links.new(node.outputs["Diffuse Alpha"], self.inputs["Alpha"])
                break

    find_init = (
        ('find_init', "Find Init", ""),
    )

    connect_init: EnumProperty(name="Find Init", update=update_props, items=find_init)

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_SHADER']


class ShaderNodeNNShaderInit(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN Shader Init"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_SHADER_INIT']


class ShaderNodeNNReflection(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN Reflection"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_REFLECTION']


node_categories = [
    MyNodeCategory('SH_NEW_NN', "Sega NN", items=[
        NodeItem("ShaderNodeNNMixRGB"),
        NodeItem("ShaderNodeNNShader"),
        NodeItem("ShaderNodeNNShaderInit"),
        NodeItem("ShaderNodeNNReflection"),
    ]),
]


classes = (
    ShaderNodeNNMixRGB,
    ShaderNodeNNShader,
    ShaderNodeNNShaderInit,
    ShaderNodeNNReflection,
)
