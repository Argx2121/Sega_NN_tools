import bpy
from bpy.props import BoolProperty, StringProperty
from ..modules.blender.model_assets.nodes import classes
from ..modules.blender.model_assets.node_groups import MakeGroups
from dataclasses import dataclass


def main(operator, context, settings):
    tree = context.space_data.node_tree
    MakeGroups().execute()

    gno_shader = tree.nodes.new('ShaderNodeNNShader')
    gno_shader.location = (30, 300)
    colour_init = tree.nodes.new('ShaderNodeNNShaderInit')
    colour_init.inputs["Emission"].hide = True
    colour_init.location = (-1060, 330)
    last_node = colour_init

    tree.links.new(gno_shader.inputs["Unshaded"], colour_init.outputs["Unshaded"])
    node = tree.nodes.get("Material Output")
    if node:
        tree.links.new(node.inputs[0], gno_shader.outputs[0])
    else:
        node = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(node.inputs[0], gno_shader.outputs[0])
    node.location = (300, 300)

    if settings.hide_override:
        gno_shader.inputs["Override Flags"].hide = True
        gno_shader.inputs["Mat Flags"].hide = True
        gno_shader.inputs["Override Data"].hide = True
        gno_shader.inputs["Mat Data 1"].hide = True
        gno_shader.inputs["Mat Data 2"].hide = True
        gno_shader.inputs["Mat Data 3"].hide = True
        gno_shader.inputs["Mat Data 4"].hide = True
        gno_shader.inputs["Mat Data 5"].hide = True
        gno_shader.inputs["Mat Data 6"].hide = True
        gno_shader.inputs["Mat Data 7"].hide = True
        gno_shader.inputs["Mat Data 8"].hide = True
        gno_shader.inputs["Mat Data 9"].hide = True
        gno_shader.inputs["Mat Data 10"].hide = True

    if settings.vertex_color:
        vertex_color = tree.nodes.new(type="ShaderNodeVertexColor")
        vertex_color.location = (-1260, 200)
        tree.links.new(colour_init.inputs["Vertex Color"], vertex_color.outputs[0])
        tree.links.new(colour_init.inputs["Vertex Alpha"], vertex_color.outputs[1])

    if settings.diffuse:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-1090, 0)
        mix_node = tree.nodes.new('ShaderNodeNNMixRGB')
        mix_node.location = (-730, 330)
        mix_node.blend_type = "_NN_RGB_MULTI"

        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])

        last_node = mix_node
        if settings.specular:
            spec_rgb = tree.nodes.new('ShaderNodeRGB')
            spec_rgb.location = (-500, 60)
            spec_rgb.outputs[0].default_value = (0.882353, 0.882353, 0.882353, 1)
            spec_alpha = tree.nodes.new(type="ShaderNodeValue")
            spec_alpha.location = (-500, -130)
            spec_alpha.outputs[0].default_value = 1
            image = tree.nodes.new(type="ShaderNodeTexImage")
            image.location = (-660, -260)
            mix_node = tree.nodes.new('ShaderNodeNNMixRGB')
            mix_node.location = (-260, 0)
            mix_node.blend_type = "_NN_RGB_MULTI"

            tree.links.new(mix_node.inputs["Color 1"], spec_rgb.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 1"], spec_alpha.outputs[0])
            tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
            tree.links.new(gno_shader.inputs["Specular"], mix_node.outputs[0])

    if settings.reflection:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-1060, -230)
        node = tree.nodes.new('ShaderNodeNNReflection')
        node.location = (-1300, -330)
        mix_node = tree.nodes.new('ShaderNodeNNMixRGB')
        mix_node.location = (-260, 290)
        mix_node.blend_type = "_NN_RGB_MULTI"

        tree.links.new(image.inputs[0], node.outputs[0])
        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        last_node = mix_node

    tree.links.new(gno_shader.inputs["Color"], last_node.outputs[0])
    tree.links.new(gno_shader.inputs["Alpha"], last_node.outputs[1])


class NodeGnoSetup(bpy.types.Operator):
    """Spawn in a Gno node set up"""
    bl_idname = "node.gno_operator"
    bl_label = "Gno Node Operator"

    diffuse: BoolProperty(
        name="Diffuse texture",
        description="Has a diffuse texture",
        default=True,
    )

    specular: BoolProperty(
        name="Specular texture",
        description="Has a specular texture",
    )

    reflection: BoolProperty(
        name="Reflection texture",
        description="Has a reflection texture",
    )

    vertex_color: BoolProperty(
        name="Vertex colors",
        description="Use vertex colors",
    )

    hide_override: BoolProperty(
        name="Hide Overridable",
        description="Hide overridable flags",
        default=True,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Gno Node Setup")
        box = layout.box()
        box.label(text="Texture settings:", icon="KEYFRAME_HLT")
        box.prop(self, "diffuse")
        if self.diffuse:
            box.prop(self, "specular")
        box.prop(self, "reflection")
        box.prop(self, "vertex_color")
        box.label(text="Advanced settings:", icon="KEYFRAME_HLT")
        box.prop(self, "hide_override")

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        settings = SetGno(self.diffuse, self.specular, self.reflection, self.vertex_color, self.hide_override)
        main(self, context, settings)
        return {'FINISHED'}


@dataclass
class SetGno:
    diffuse: bool
    specular: bool
    reflection: bool
    vertex_color: bool
    hide_override: bool


class NNNodeAdd(bpy.types.Operator):
    """Spawn in an NN node"""
    bl_idname = "node.add_node_nn"
    bl_label = "Node Add NN Operator"

    use_transform: BoolProperty(
    )

    type: StringProperty(
    )

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        MakeGroups().execute()
        bpy.ops.node.add_node(use_transform=self.use_transform, type=self.type)
        return {'FINISHED'}


class NN_MT_Node_Add(bpy.types.Menu):
    bl_label = "NN"

    def draw(self, context):
        layout = self.layout
        for cla in classes:
            var = layout.operator("node.add_node_nn", text=cla.bl_label)
            var.type = cla.bl_idname
            var.use_transform = True
        # imagine if the world was made of pudding


class NN_MT_Node_Setup(bpy.types.Menu):
    bl_label = "NN Setup"

    def draw(self, context):
        layout = self.layout
        layout.operator("node.gno_operator", text="GNO")


def nn_node_menu(self, context):
    if context.area.ui_type == 'ShaderNodeTree':
        layout = self.layout
        layout.separator()
        layout.menu("NN_MT_Node_Add")
        layout.menu("NN_MT_Node_Setup")

