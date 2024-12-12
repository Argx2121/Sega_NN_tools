import bpy
import nodeitems_utils
from bpy.props import EnumProperty, BoolProperty
from bpy.types import ShaderNodeCustomGroup
# blender crashing after reloading script is an issue with custom nodes
#  https://projects.blender.org/blender/blender/issues/72833


class CustomNodetreeNodeBaseNN:
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        pass

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
        pass

    def draw_buttons(self, context, layout):
        has_link = False
        for link in self.id_data.links:
            if link.to_socket == self.inputs["Specular"]:
                has_link = True
                break
        if not has_link:
            for prop in self.bl_rna.properties:
                if prop.is_runtime and not prop.is_readonly:
                    if prop.name == "Find Init":
                        layout.prop(self, prop.identifier, text=prop.name, expand=True)
                    elif prop.type == "ENUM":
                        layout.prop(self, prop.identifier, text="")
                    else:
                        layout.prop(self, prop.identifier, text=prop.name)

        else:
            for prop in self.bl_rna.properties:
                if prop.is_runtime and not prop.is_readonly:
                    if prop.name == "Find Init":
                        continue
                    elif prop.type == "ENUM":
                        layout.prop(self, prop.identifier, text="")
                    else:
                        layout.prop(self, prop.identifier, text=prop.name)


class ShaderNodeNNMixRGB(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN MixRGB"
    bl_idname = "ShaderNodeNNMixRGB"
    bl_width_default = 180

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('_NN_RGB_MULTI', "Multiply", ""),
            ('_NN_RGB_DECAL', "Decal", ""),
            ('_NN_RGB_REPLACE', "Replace", ""),
            ('_NN_RGB_BLEND', "Blend", ""),
            ('_NN_RGB_PASS', "Pass Clear", ""),
            ('_NN_RGB_ALPHA', "Alpha Texture", ""),
            ('_NN_RGB_DECAL_2', "Decal 2", ""),
            ('_NN_RGB_SUB', "Subtract", "If you use Subtract as the first mixing type, you can only have 3 textures"),
            ('_NN_RGB_ADD', "Add", ""),
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


class ShaderNodeNNShader(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN Shader"
    bl_idname = "ShaderNodeNNShader"
    bl_width_default = 180

    def blend_types(self, context):
        blend_types = (
            ('0', "None", ""),
            ('1', "Blend", ""),
            ('2', "Logic", ""),
            ('3', "Subtract", ""),
        )
        return blend_types

    def source_facts(self, context):
        source_facts = (
            ('0', "Zero", ""),
            ('1', "One", ""),
            ('2', "Destination Color", ""),
            ('3', "1 - Destination Color", ""),
            ('4', "Source Alpha", ""),
            ('5', "1 - Source Alpha", ""),
            ('6', "Destination Alpha", ""),
            ('7', "1 - Destination Alpha", ""),
        )
        return source_facts

    def dest_facts(self, context):
        dest_facts = (
            ('0', "Zero", ""),
            ('1', "One", ""),
            ('2', "Source Color", ""),
            ('3', "1 - Source Color", ""),
            ('4', "Source Alpha", ""),
            ('5', "1 - Source Alpha", ""),
            ('6', "Destination Alpha", ""),
            ('7', "1 - Destination Alpha", ""),
        )
        return dest_facts

    def blend_ops(self, context):
        blend_ops = (
            ('0', "Clear", ""),
            ('1', "And", ""),
            ('2', "Reverse And", ""),
            ('3', "Copy", ""),
            ('4', "Inverse And", ""),
            ('5', "No Operation", ""),
            ('6', "Xor", ""),
            ('7', "Or", ""),
            ('8', "Nor", ""),
            ('9', "Equivalent", ""),
            ('10', "Inverse", ""),
            ('11', "Reverse Or", ""),
            ('12', "Inverse Copy", ""),
            ('13', "Inverse Or", ""),
            ('14', "Not And", ""),
            ('15', "Set", ""),
        )
        return blend_ops

    def z_modes(self, context):
        z_modes = (
            ('0', "Never", ""),
            ('1', "Less", ""),
            ('2', "Less Equal", ""),
            ('3', "Equal", ""),
            ('4', "Not Equal", ""),
            ('5', "Greater Equal", ""),
            ('6', "Greater", ""),
            ('7', "Always", ""),
        )
        return z_modes

    def alpha_comp0s(self, context):
        alpha_comp0s = (
            ('0', "Never", ""),
            ('1', "Less", ""),
            ('2', "Less Equal", ""),
            ('3', "Equal", ""),
            ('4', "Not Equal", ""),
            ('5', "Greater Equal", ""),
            ('6', "Greater", ""),
            ('7', "Always", ""),
        )
        return alpha_comp0s

    def alpha_comp1s(self, context):
        alpha_comp1s = (
            ('0', "Never", ""),
            ('1', "Less", ""),
            ('2', "Less Equal", ""),
            ('3', "Equal", ""),
            ('4', "Not Equal", ""),
            ('5', "Greater Equal", ""),
            ('6', "Greater", ""),
            ('7', "Always", ""),
        )
        return alpha_comp1s

    def alpha_ops(self, context):
        alpha_ops = (
            ('0', "And", ""),
            ('1', "Or", ""),
            ('2', "Xor", ""),
            ('3', "Xnor", ""),
        )
        return alpha_ops

    def update_blend_type(self, context):
        if not self.blend_type:
            self.blend_type = self.blend_types(context)[1][0]

        self.inputs["Blend Type"].default_value = int(self.blend_type)

    def update_source_fact(self, context):
        if not self.source_fact:
            self.source_fact = self.source_facts(context)[4][0]

        self.inputs["Source Fact"].default_value = int(self.source_fact)

    def update_dest_fact(self, context):
        if not self.dest_fact:
            self.dest_fact = self.dest_facts(context)[5][0]

        self.inputs["Dest Fact"].default_value = int(self.dest_fact)

    def update_blend_op(self, context):
        if not self.blend_op:
            self.blend_op = self.blend_ops(context)[5][0]

        self.inputs["Blend Op"].default_value = int(self.blend_op)

    def update_z_mode(self, context):
        if not self.z_mode:
            self.z_mode = self.z_modes(context)[2][0]

        self.inputs["Z Mode"].default_value = int(self.z_mode)

    def update_alpha_comp0(self, context):
        if not self.alpha_comp0:
            self.alpha_comp0 = self.alpha_comp0s(context)[6][0]

        self.inputs["Alpha comp0"].default_value = int(self.alpha_comp0)

    def update_alpha_comp1(self, context):
        if not self.alpha_comp1:
            self.alpha_comp1 = self.alpha_comp1s(context)[7][0]

        self.inputs["Alpha comp1"].default_value = int(self.alpha_comp1)

    def update_alpha_op(self, context):
        if not self.alpha_op:
            self.alpha_op = self.alpha_ops(context)[0][0]

        self.inputs["Alpha Op"].default_value = int(self.alpha_op)

    blend_type: EnumProperty(name="Blend Type", update=update_blend_type, items=blend_types)
    source_fact: EnumProperty(name="Source Factor", update=update_source_fact, items=source_facts)
    dest_fact: EnumProperty(name="Destination Factor", update=update_dest_fact, items=dest_facts)
    blend_op: EnumProperty(name="Blend Operation", update=update_blend_op, items=blend_ops)
    z_mode: EnumProperty(name="Z Mode", update=update_z_mode, items=z_modes)
    alpha_comp0: EnumProperty(name="Alpha Compare 0", update=update_alpha_comp0, items=alpha_comp0s)
    alpha_comp1: EnumProperty(name="Alpha Compare 1", update=update_alpha_comp1, items=alpha_comp1s)
    alpha_op: EnumProperty(name="Alpha Operation", update=update_alpha_op, items=alpha_ops)

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_SHADER']
        self.blend_type = self.blend_types(context)[1][0]
        self.inputs["Blend Type"].hide = True
        self.source_fact = self.source_facts(context)[4][0]
        self.inputs["Source Fact"].hide = True
        self.dest_fact = self.dest_facts(context)[5][0]
        self.inputs["Dest Fact"].hide = True
        self.blend_op = self.blend_ops(context)[5][0]
        self.inputs["Blend Op"].hide = True
        self.z_mode = self.z_modes(context)[2][0]
        self.inputs["Z Mode"].hide = True
        self.alpha_comp0 = self.alpha_comp0s(context)[6][0]
        self.inputs["Alpha comp0"].hide = True
        self.alpha_comp1 = self.alpha_comp1s(context)[7][0]
        self.inputs["Alpha comp1"].hide = True
        self.alpha_op = self.alpha_ops(context)[0][0]
        self.inputs["Alpha Op"].hide = True


class ShaderNodeNNShaderInit(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN Shader Init"
    bl_idname = "ShaderNodeNNShaderInit"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_SHADER_INIT']


class ShaderNodeNNSpecular(CustomNodetreeNodeBaseNNExpandLink, ShaderNodeCustomGroup):
    bl_label = "NN Specular"
    bl_idname = "ShaderNodeNNSpecular"
    bl_width_default = 180

    def update_init(self, context):
        for node in self.id_data.nodes:
            if node.bl_idname == "ShaderNodeNNShaderInit":
                self.id_data.links.new(node.outputs["Specular"], self.inputs["Specular"])
                break

    find_init = (
        ('find_init', "Find Init", ""),
    )

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('_NN_RGB_SPEC', "Specular", ""),
            ('_NN_RGB_SPEC_2', "Specular 2", ""),
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

    connect_init: EnumProperty(name="Find Init", update=update_init, items=find_init)
    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types)
    multi_shading: BoolProperty(name="Use Shading Init", update=update_shading, default=False)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_RGB_SPEC']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True


class ShaderNodeNNVector(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NN Vector"
    bl_idname = "ShaderNodeNNVector"
    bl_width_default = 180

    def u_types(self, context):
        wrap_types = (
            ('0', "Clamp U", ""),
            ('1', "Repeat U", ""),
            ('2', "Mirror U", ""),
        )
        return wrap_types

    def v_types(self, context):
        wrap_types = (
            ('0', "Clamp V", ""),
            ('1', "Repeat V", ""),
            ('2', "Mirror V", ""),
        )
        return wrap_types

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass  # defining this so blender doesn't try to remove the group

    def update_u(self, context):
        if not self.u_type:
            self.u_type = self.u_types(context)[1][0]

        self.inputs["U"].default_value = int(self.u_type)

    def update_v(self, context):
        if not self.v_type:
            self.v_type = self.v_types(context)[1][0]

        self.inputs["V"].default_value = int(self.v_type)

    u_type: EnumProperty(name="U Wrapping", update=update_u, items=u_types)
    v_type: EnumProperty(name="V Wrapping", update=update_v, items=v_types)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['_NN_VECTOR']
        self.u_type = self.u_types(context)[1][0]
        self.v_type = self.v_types(context)[1][0]
        self.inputs["U"].hide = True
        self.inputs["V"].hide = True


classes = (
    ShaderNodeNNMixRGB,
    ShaderNodeNNShader,
    ShaderNodeNNShaderInit,
    ShaderNodeNNSpecular,
    ShaderNodeNNVector,
)
