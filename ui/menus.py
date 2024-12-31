import bpy
from bpy.props import BoolProperty, StringProperty
from ..modules.blender.model_assets.nodes import classes
from ..modules.blender.model_assets.node_groups import MakeGroups
from dataclasses import dataclass


def main(operator, context, settings):
    tree = context.space_data.node_tree
    MakeGroups().execute()
    existing_diffuse = None

    if settings.existing_diffuse:
        node = tree.nodes.get("Image Texture")  # blender wants node name w/e
        if node and node.image:
            existing_diffuse = node.image

    if settings.remove_existing:
        for node in tree.nodes:
            tree.nodes.remove(node)

    gno_shader = tree.nodes.new('ShaderNodeGNOShader')
    gno_shader.location = (10, 310)
    colour_init = tree.nodes.new('ShaderNodeGNOShaderInit')
    colour_init.location = (-1970, 450)
    last_node = colour_init

    node = tree.nodes.get("Material Output")
    if node:
        tree.links.new(node.inputs[0], gno_shader.outputs[0])
    else:
        node = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(node.inputs[0], gno_shader.outputs[0])
    node.location = (300, 300)

    if settings.vertex_color:
        vertex_color = tree.nodes.new(type="ShaderNodeVertexColor")
        vertex_color.location = (-2260, 260)
        tree.links.new(colour_init.inputs["Vertex Color"], vertex_color.outputs[0])
        tree.links.new(colour_init.inputs["Vertex Alpha"], vertex_color.outputs[1])

    if settings.diffuse:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-1640, 250)
        image.label = "Diffuse Texture"
        vector = tree.nodes.new(type="ShaderNodeGNOVector")
        vector.location = (-1940, 10)
        uv = tree.nodes.new(type="ShaderNodeUVMap")
        uv.location = (-2170, -120)
        mix_node = tree.nodes.new('ShaderNodeGNOMixRGB')
        mix_node.location = (-1250, 500)
        mix_node.blend_type = "_NN_RGB_MULTI"

        if existing_diffuse:
            image.image = existing_diffuse

        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        tree.links.new(image.inputs["Vector"], vector.outputs["Image Vector"])
        tree.links.new(vector.inputs["UV Map"], uv.outputs[0])
        last_node = mix_node

    if settings.reflection:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-1160, 160)
        image.label = "Reflection Texture"
        vector = tree.nodes.new(type="ShaderNodeGNOVector")
        vector.location = (-1440, -50)
        vector.inputs["Reflection Vector"].default_value = True
        mix_node = tree.nodes.new('ShaderNodeGNOMixRGB')
        mix_node.location = (-770, 410)
        mix_node.blend_type = "_NN_RGB_MULTI"

        tree.links.new(image.inputs["Vector"], vector.outputs["Image Vector"])
        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        last_node = mix_node

    if settings.specular:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-700, 70)
        image.label = "Specular Texture"
        vector = tree.nodes.new(type="ShaderNodeGNOVector")
        vector.location = (-940, -140)
        uv = tree.nodes.new(type="ShaderNodeUVMap")
        uv.location = (-1150, -260)
        mix_node = tree.nodes.new('ShaderNodeGNOSpecular')
        mix_node.location = (-320, 320)
        mix_node.blend_type = "_NN_RGB_SPEC"

        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
        tree.links.new(image.inputs["Vector"], vector.outputs["Image Vector"])
        tree.links.new(vector.inputs["UV Map"], uv.outputs[0])
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

    existing_diffuse: BoolProperty(
        name="Use existing diffuse",
        description="Use the existing texture as the diffuse texture",
        default=True,
    )

    remove_existing: BoolProperty(
        name="Remove existing",
        description="Remove existing nodes from the tree",
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
        box.prop(self, "specular")
        box.prop(self, "reflection")
        box.prop(self, "vertex_color")
        box.label(text="Advanced settings:", icon="KEYFRAME_HLT")
        box.prop(self, "existing_diffuse")
        box.prop(self, "remove_existing")

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        settings = SetGno(self.diffuse, self.specular, self.reflection, self.vertex_color, self.existing_diffuse,
                          self.remove_existing)
        main(self, context, settings)
        return {'FINISHED'}


@dataclass
class SetGno:
    diffuse: bool
    specular: bool
    reflection: bool
    vertex_color: bool
    existing_diffuse: bool
    remove_existing: bool


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

