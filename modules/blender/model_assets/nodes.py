import bpy
import nodeitems_utils
from bpy.props import *
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


def _get_material(self):
    data_path = repr(self.id_data)
    if data_path.endswith('evaluated>'):  # you know i had to do it to em
        tree_name = self.id_data.get_output_node("ALL").outputs
        # bpy.data.materials['Material'].node_tree.nodes["Material Output"].outputs
        material_name = repr(tree_name).split("].node_tree")[0].split("bpy.data.materials[")[1][1:-1]
    else:
        material_name = repr(self.id_data)[20:-12]
    return bpy.data.materials[material_name]


def _update_texture(self, texture_var, image_input_str):
    if texture_var != -1:
        for link in self.id_data.links:
            if link.to_socket == self.inputs[image_input_str] and link.from_node.bl_idname == "ShaderNodeTexImage":
                material = _get_material(self)
                meshes = bpy.data.user_map(subset=[material]).values()
                for mesh in meshes:  # you test my patience
                    for m in mesh:
                        objs = bpy.data.user_map(subset=[m]).values()
                        for obj in objs:
                            for o in obj:
                                if o.parent and o.parent.data.id_type == "ARMATURE" and o.parent.data.nn_texture_count:
                                    # lord have mercy
                                    if o.parent.data.nn_texture_count <= texture_var:
                                        print("NN Material Node texture index greater than armatures nn textures!")
                                        return
                                    link.from_node.image = o.parent.data.nn_textures[texture_var].texture
                                    return


def _shader_ui_common(self, ignore, layout, pad_ind):
    if self.advanced:  # if show advanced settings
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="", icon='DOWNARROW_HLT')
        row.prop(self, 'advanced', emboss=False)
        index = 0
        for prop in self.bl_rna.properties:
            if prop.is_runtime and not prop.is_readonly and prop.name not in ignore:
                if prop.type == "ENUM":
                    text = ""
                else:
                    text = prop.name
                layout.prop(self, prop.identifier, text=text)
                if index in pad_ind:
                    layout.separator(factor=0.15)
                index += 1
    else:
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="", icon='RIGHTARROW')
        row.prop(self, 'advanced', emboss=False)
    layout.separator(factor=0.3)
    material = _get_material(self)
    layout.prop(material, 'use_backface_culling', text='Backface Culling')


class ShaderNodeGNOMixRGB(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "GNO MixRGB"
    bl_idname = "ShaderNodeGNOMixRGB"
    bl_width_default = 180

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('.GNO_MULTI', "Multiply", ""),
            ('.GNO_DECAL', "Decal", ""),
            ('.GNO_REPLACE', "Replace", ""),
            ('.GNO_BLEND', "Blend", ""),
            ('.GNO_PASSCOLOR', "Pass Color", ""),
            ('.GNO_ALPHATEX', "Alpha Texture", ""),
            ('.GNO_DECAL2', "Decal 2", ""),
            ('.GNO_SUB', "Subtract", "If you use Subtract as the first mixing type, you can only have 3 textures"),
            ('.GNO_ADD', "Add", ""),
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
                if node.bl_idname == "ShaderNodeGNOShaderInit":
                    self.id_data.links.new(node.outputs["Shading"], self.inputs["Shader Init"])
                    break
        else:
            for link in self.id_data.links:
                if link.to_socket == self.inputs["Shader Init"]:
                    self.id_data.links.remove(link)
                    break
        self.inputs["Shader Init"].hide = True

    def update_texture_2(self, context):
        _update_texture(self, self.texture_2, "Color 2")

    def get_texture_2(self):
        return self.get("texture_2", False)

    def set_texture_2(self, value):
        if self["texture_2"] != value:
            _update_texture(self, value, "Color 2")
            self["texture_2"] = value

    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types, options=set())
    multi_shading: BoolProperty(name="Apply Shading", update=update_shading, default=False, options=set())
    texture_2: IntProperty(name="Image Index", default=-1, min=-1, max=255,
                           get=get_texture_2, set=set_texture_2, update=update_texture_2)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_MULTI']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True
        self["texture_2"] = 0


class ShaderNodeXNOMixRGB(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "XNO MixRGB"
    bl_idname = "ShaderNodeXNOMixRGB"
    bl_width_default = 180

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('.GNO_MULTI', "Multiply", ""),
            ('.GNO_DECAL', "Decal", ""),
            ('.GNO_REPLACE', "Replace", ""),
            ('.GNO_BLEND', "Blend", ""),
            ('.GNO_DECAL2', "Decal 2", ""),
            ('.GNO_ADD', "Add", ""),
            ('.GNO_SUB', "Subtract", ""),
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
                if node.bl_idname == "ShaderNodeXNOShaderInit":
                    self.id_data.links.new(node.outputs["Shading"], self.inputs["Shader Init"])
                    break
        else:
            for link in self.id_data.links:
                if link.to_socket == self.inputs["Shader Init"]:
                    self.id_data.links.remove(link)
                    break
        self.inputs["Shader Init"].hide = True

    def update_texture_2(self, context):
        _update_texture(self, self.texture_2, "Color 2")

    def get_texture_2(self):
        return self.get("texture_2", False)

    def set_texture_2(self, value):
        if self["texture_2"] != value:
            _update_texture(self, value, "Color 2")
            self["texture_2"] = value

    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types, options=set())
    multi_shading: BoolProperty(name="Apply Shading", update=update_shading, default=False, options=set())
    texture_2: IntProperty(name="Image Index", default=-1, min=-1, max=255,
                           get=get_texture_2, set=set_texture_2, update=update_texture_2)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_MULTI']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True
        self["texture_2"] = 0


class ShaderNodeGNOShader(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "GNO Shader"
    bl_idname = "ShaderNodeGNOShader"
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

    def nn_blend_methods(self, context):
        nn_blend_methods = (
            ('OPAQUE', "Opaque", ""),
            ('BLEND', "Alpha Blend", ""),
            ('CLIP', "Alpha Clip", ""),
        )
        return nn_blend_methods

    def update_blend_type(self, context):
        if not self.blend_type:
            self.blend_type = self.blend_types(context)[1][0]

    def update_source_fact(self, context):
        if not self.source_fact:
            self.source_fact = self.source_facts(context)[4][0]

    def update_dest_fact(self, context):
        if not self.dest_fact:
            self.dest_fact = self.dest_facts(context)[5][0]

    def update_blend_op(self, context):
        if not self.blend_op:
            self.blend_op = self.blend_ops(context)[5][0]

    def update_z_mode(self, context):
        if not self.z_mode:
            self.z_mode = self.z_modes(context)[2][0]

    def update_alpha_comp0(self, context):
        if not self.alpha_comp0:
            self.alpha_comp0 = self.alpha_comp0s(context)[6][0]

    def update_alpha_comp1(self, context):
        if not self.alpha_comp1:
            self.alpha_comp1 = self.alpha_comp1s(context)[7][0]

    def update_alpha_op(self, context):
        if not self.alpha_op:
            self.alpha_op = self.alpha_ops(context)[0][0]

    def update_nn_blend(self, context):
        if not self.nn_blend_method:
            self.nn_blend_method = self.nn_blend_methods(context)[0][0]
        if self.nn_blend_method == "OPAQUE":
            _get_material(self).blend_method = "OPAQUE"
        elif self.nn_blend_method == "BLEND":
            _get_material(self).blend_method = "BLEND"
        elif self.nn_blend_method == "CLIP":
            _get_material(self).blend_method = "CLIP"

    def draw_buttons(self, context, layout):
        ignore = {'Advanced', "Blend Mode"}
        _shader_ui_common(self, ignore, layout, {5, 8})

        layout.prop(self, 'nn_blend_method', text='')

    blend_type: EnumProperty(name="Blend Mode", update=update_blend_type, items=blend_types, options=set())
    source_fact: EnumProperty(name="Source Factor", update=update_source_fact, items=source_facts, options=set())
    dest_fact: EnumProperty(name="Destination Factor", update=update_dest_fact, items=dest_facts, options=set())
    blend_op: EnumProperty(name="Blend Logic", update=update_blend_op, items=blend_ops, options=set())

    alpha_comp0: EnumProperty(name="Alpha Compare 0", update=update_alpha_comp0, items=alpha_comp0s, options=set())
    alpha_comp1: EnumProperty(name="Alpha Compare 1", update=update_alpha_comp1, items=alpha_comp1s, options=set())
    alpha_ref0: IntProperty(name='Alpha ref 0', default=0, min=0, max=255, options=set())
    alpha_ref1: IntProperty(name='Alpha ref 1', default=0, min=0, max=255, options=set())
    alpha_op: EnumProperty(name="Alpha Operation", update=update_alpha_op, items=alpha_ops, options=set())

    buff_comp: BoolProperty(name="Z Buff Compare", default=True, options=set())
    z_mode: EnumProperty(name="Z Mode", update=update_z_mode, items=z_modes, options=set())
    buff_update: BoolProperty(name="Z Buff Update", default=True, options=set())

    nn_blend_method: EnumProperty(name="Blend Mode", update=update_nn_blend, items=nn_blend_methods, options=set())
    # okay guys im sorry but im worried about calling it blend method ................

    advanced: BoolProperty(name="Advanced", default=False, options=set())

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_SHADER']
        self.blend_type = self.blend_types(context)[1][0]
        self.source_fact = self.source_facts(context)[4][0]
        self.dest_fact = self.dest_facts(context)[5][0]
        self.blend_op = self.blend_ops(context)[5][0]
        self.z_mode = self.z_modes(context)[2][0]
        self.alpha_comp0 = self.alpha_comp0s(context)[6][0]
        self.alpha_comp1 = self.alpha_comp1s(context)[7][0]
        self.alpha_op = self.alpha_ops(context)[0][0]


class ShaderNodeXNOShader(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "XNO Shader"
    bl_idname = "ShaderNodeXNOShader"
    bl_width_default = 180

    def blend_ops(self, context):
        blend_ops = (
            ('32774', 'Add', ''), ('32775', 'Min', ''), ('32776', 'Max', ''), ('32778', 'Subtract', ''),
            ('32779', 'Reverse Subtract', ''), ('61445', 'Reverse Subtract Signed', ''), ('61446', 'Add Signed', ''))
        return blend_ops

    def source_facts(self, context):
        source_facts = (
            ('0', 'Zero', ''), ('1', 'One', ''), ('768', 'Source Color', ''), ('769', '1 - Source Color', ''),
            ('770', 'Source Alpha', ''), ('771', '1 - Source Alpha', ''), ('772', 'Destination Alpha', ''),
            ('773', '1 - Destination Alpha', ''), ('774', 'Destination Color', ''), ('775', '1 - Destination Color', ''),
            ('776', 'Source Alpha SAT', ''), ('32769', 'Blend Color', ''), ('32770', '1 - Blend Color', ''),
            ('32771', 'Blend Alpha', ''), ('32772', '1 - Blend Alpha', ''))
        return source_facts

    def dest_facts(self, context):
        dest_facts = (
            ('0', 'Zero', ''), ('1', 'One', ''), ('768', 'Source Color', ''), ('769', '1 - Source Color', ''),
            ('770', 'Source Alpha', ''), ('771', '1 - Source Alpha', ''), ('772', 'Destination Alpha', ''),
            ('773', '1 - Destination Alpha', ''), ('774', 'Destination Color', ''), ('775', '1 - Destination Color', ''),
            ('776', 'Source Alpha SAT', ''), ('32769', 'Blend Color', ''), ('32770', '1 - Blend Color', ''),
            ('32771', 'Blend Alpha', ''), ('32772', '1 - Blend Alpha', ''))
        return dest_facts

    def blend_logics(self, context):
        blend_logics = (
            ('0', 'None', ''), ('5376', 'Clear', ''), ('5377', 'And', ''), ('5378', 'Reverse And', ''), ('5379', 'Copy', ''),
            ('5380', 'Inverse And', ''), ('5381', 'No Operation', ''), ('5382', 'Xor', ''), ('5383', 'Or', ''),
            ('5384', 'Nor', ''), ('5385', 'Equivalent', ''), ('5386', 'Inverse', ''), ('5387', 'Reverse Or', ''),
            ('5388', 'Inverse Copy', ''), ('5389', 'Inverse Or', ''), ('5390', 'Not And', ''), ('5391', 'Set', ''))
        return blend_logics

    def z_modes(self, context):
        z_modes = (
            ('512', 'Never', ''), ('513', 'Less', ''), ('514', 'Equal', ''), ('515', 'Less Equal', ''),
            ('516', 'Greater', ''), ('517', 'Not Equal', ''), ('518', 'Greater Equal', ''), ('519', 'Always', ''))
        return z_modes

    def test_modes(self, context):
        test_modes = (
            ('512', 'Never', ''), ('513', 'Less', ''), ('514', 'Equal', ''), ('515', 'Less Equal', ''),
            ('516', 'Greater', ''), ('517', 'Not Equal', ''), ('518', 'Greater Equal', ''), ('519', 'Always', ''))
        return test_modes

    def nn_blend_methods(self, context):
        nn_blend_methods = (
            ('OPAQUE', "Opaque", ""),
            ('BLEND', "Alpha Blend", ""),
            ('CLIP', "Alpha Clip", ""),
        )
        return nn_blend_methods

    def update_blend_logic(self, context):
        if not self.blend_logic:
            self.blend_logic = self.blend_logics(context)[0][0]

    def update_source_fact(self, context):
        if not self.source_fact:
            self.source_fact = self.source_facts(context)[4][0]

    def update_dest_fact(self, context):
        if not self.dest_fact:
            self.dest_fact = self.dest_facts(context)[5][0]

    def update_blend_op(self, context):
        if not self.blend_op:
            self.blend_op = self.blend_ops(context)[0][0]

    def update_z_mode(self, context):
        if not self.z_mode:
            self.z_mode = self.z_modes(context)[3][0]

    def update_test_mode(self, context):
        if not self.test_mode:
            self.test_mode = self.test_modes(context)[4][0]

    def update_nn_blend(self, context):
        if not self.nn_blend_method:
            self.nn_blend_method = self.nn_blend_methods(context)[0][0]
        if self.nn_blend_method == "OPAQUE":
            _get_material(self).blend_method = "OPAQUE"
        elif self.nn_blend_method == "BLEND":
            _get_material(self).blend_method = "BLEND"
        elif self.nn_blend_method == "CLIP":
            _get_material(self).blend_method = "CLIP"

    def draw_buttons(self, context, layout):
        ignore = {'Advanced', "Shader File", "Shader Name", "Blend Mode"}
        _shader_ui_common(self, ignore, layout, {5, 8})

        layout.prop(self, 'nn_blend_method', text='')
        row = layout.row(align=True)
        row.label(text='Shader Name:')
        row.prop(self, 'shader_name', text='')
        row = layout.row(align=True)
        row.label(text='Shader File:')
        row.prop(self, 'shader_file', text='')

    buffer_blend: BoolProperty(name="Buffer Blend", default=True, options=set())
    blend_op: EnumProperty(name="Blend Operation", update=update_blend_op, items=blend_ops, options=set())
    source_fact: EnumProperty(name="Source Factor", update=update_source_fact, items=source_facts, options=set())
    dest_fact: EnumProperty(name="Destination Factor", update=update_dest_fact, items=dest_facts, options=set())
    blend_logic: EnumProperty(name="Blend Type", update=update_blend_logic, items=blend_logics, options=set())
    blend_color: FloatVectorProperty(name='Blend Color', size=4, subtype='COLOR', min=0, max=1,
                                     default=(0.0, 0.0, 0.0, 0.0))

    alpha_test: BoolProperty(name="Alpha Test", default=True, options=set())
    test_mode: EnumProperty(name="Test Mode", update=update_test_mode, items=test_modes, options=set())
    alpha_ref: IntProperty(name='Alpha ref', default=0, min=0, max=255, options=set())

    buff_comp: BoolProperty(name="Z Buff Compare", default=True, options=set())
    z_mode: EnumProperty(name="Z Mode", update=update_z_mode, items=z_modes, options=set())
    buff_update: BoolProperty(name="Z Buff Update", default=True, options=set())

    shader_file: StringProperty(name="Shader File")
    shader_name: StringProperty(name="Shader Name")

    nn_blend_method: EnumProperty(name="Blend Mode", update=update_nn_blend, items=nn_blend_methods, options=set())

    advanced: BoolProperty(name="Advanced", default=False, options=set())

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.XNO_SHADER']
        self.blend_op = self.blend_ops(context)[0][0]
        self.source_fact = self.source_facts(context)[4][0]
        self.dest_fact = self.dest_facts(context)[5][0]
        self.blend_logic = self.blend_logics(context)[0][0]
        self.z_mode = self.z_modes(context)[3][0]
        self.test_mode = self.test_modes(context)[4][0]


class ShaderNodeGNOShaderInit(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "GNO Shader Init"
    bl_idname = "ShaderNodeGNOShaderInit"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def update_shading(self, context):
        if self.unshaded:
            if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_FLAT']:
                self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_FLAT']
        else:
            if self.use_specular:
                if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_ALL']:
                    self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_ALL']
            else:
                if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_NO_SPEC']:
                    self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_NO_SPEC']

    unshaded: BoolProperty(name="Unshaded", update=update_shading, default=False, options=set())
    use_specular: BoolProperty(name="Use Specular", update=update_shading, default=True, options=set())

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_ALL']
        self.inputs['Emission'].hide = True
        self.inputs['Normal'].hide = True


class ShaderNodeXNOShaderInit(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "XNO Shader Init"
    bl_idname = "ShaderNodeXNOShaderInit"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def update_shading(self, context):
        if self.unshaded:
            if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_FLAT']:
                self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_FLAT']
        else:
            if self.use_specular:
                if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_ALL']:
                    self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_ALL']
            else:
                if self.node_tree != bpy.data.node_groups['.GNO_SHADER_INIT_NO_SPEC']:
                    self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_NO_SPEC']

    unshaded: BoolProperty(name="Unshaded", update=update_shading, default=False, options=set())
    use_specular: BoolProperty(name="Use Specular", update=update_shading, default=True, options=set())

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_SHADER_INIT_ALL']
        self.inputs['Specular Gloss'].hide = True
        self.inputs['Normal'].hide = True


class ShaderNodeGNOSpecular(CustomNodetreeNodeBaseNNExpandLink, ShaderNodeCustomGroup):
    bl_label = "GNO Specular"
    bl_idname = "ShaderNodeGNOSpecular"
    bl_width_default = 180

    def update_init(self, context):
        for node in self.id_data.nodes:
            if node.bl_idname == "ShaderNodeGNOShaderInit":
                self.id_data.links.new(node.outputs["Specular"], self.inputs["Specular"])
                break

    find_init = (
        ('find_init', "Find Init", ""),
    )

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('.GNO_SPEC', "Specular", ""),
            ('.GNO_SPEC2', "Specular 2", ""),
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
                if node.bl_idname == "ShaderNodeGNOShaderInit":
                    self.id_data.links.new(node.outputs["Shading"], self.inputs["Shader Init"])
                    break
        else:
            for link in self.id_data.links:
                if link.to_socket == self.inputs["Shader Init"]:
                    self.id_data.links.remove(link)
                    break
        self.inputs["Shader Init"].hide = True

    def update_texture_2(self, context):
        _update_texture(self, self.texture_2, "Color 2")

    def get_texture_2(self):
        return self.get("texture_2", False)

    def set_texture_2(self, value):
        if self["texture_2"] != value:
            _update_texture(self, value, "Color 2")
            self["texture_2"] = value

    connect_init: EnumProperty(name="Find Init", update=update_init, items=find_init, options=set())
    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types, options=set())
    multi_shading: BoolProperty(name="Apply Shading", update=update_shading, default=False, options=set())
    texture_2: IntProperty(name="Image Index", default=-1, min=-1, max=255,
                           get=get_texture_2, set=set_texture_2, update=update_texture_2)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_SPEC']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True
        self["texture_2"] = 0


class ShaderNodeXNOSpecular(CustomNodetreeNodeBaseNNExpandLink, ShaderNodeCustomGroup):
    bl_label = "XNO Specular"
    bl_idname = "ShaderNodeXNOSpecular"
    bl_width_default = 180

    def update_init(self, context):
        for node in self.id_data.nodes:
            if node.bl_idname == "ShaderNodeXNOShaderInit":
                self.id_data.links.new(node.outputs["Specular"], self.inputs["Specular"])
                break

    find_init = (
        ('find_init', "Find Init", ""),
    )

    def blend_types(self, context):
        # Enum items list
        mix_types = (
            ('.GNO_SPEC', "Specular", ""),
            ('.GNO_SPEC2', "Specular 2", ""),
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
                if node.bl_idname == "ShaderNodeXNOShaderInit":
                    self.id_data.links.new(node.outputs["Shading"], self.inputs["Shader Init"])
                    break
        else:
            for link in self.id_data.links:
                if link.to_socket == self.inputs["Shader Init"]:
                    self.id_data.links.remove(link)
                    break
        self.inputs["Shader Init"].hide = True

    def update_texture_2(self, context):
        _update_texture(self, self.texture_2, "Color 2")

    def get_texture_2(self):
        return self.get("texture_2", False)

    def set_texture_2(self, value):
        if self["texture_2"] != value:
            _update_texture(self, value, "Color 2")
            self["texture_2"] = value

    connect_init: EnumProperty(name="Find Init", update=update_init, items=find_init, options=set())
    blend_type: EnumProperty(name="Blend", update=update_props, items=blend_types, options=set())
    multi_shading: BoolProperty(name="Apply Shading", update=update_shading, default=False, options=set())
    texture_2: IntProperty(name="Image Index", default=-1, min=-1, max=255,
                           get=get_texture_2, set=set_texture_2, update=update_texture_2)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.GNO_SPEC']
        self.blend_type = self.blend_types(context)[0][0]
        self.inputs["Shader Init"].hide = True
        self["texture_2"] = 0


class ShaderNodeXNONormal(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "XNO Normal"
    bl_idname = "ShaderNodeXNONormal"
    bl_width_default = 180

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass  # defining this so blender doesn't try to remove the group

    def update_texture_2(self, context):
        _update_texture(self, self.texture_2, "Color 2")

    def get_texture_2(self):
        return self.get("texture_2", False)

    def set_texture_2(self, value):
        if self["texture_2"] != value:
            _update_texture(self, value, "Color 2")
            self["texture_2"] = value

    texture_2: IntProperty(name="Image Index", default=-1, min=-1, max=255,
                           get=get_texture_2, set=set_texture_2, update=update_texture_2)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NN_TANGENT']
        self["texture_2"] = 0


class ShaderNodeGNOVector(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "GNO Vector"
    bl_idname = "ShaderNodeGNOVector"
    bl_width_default = 180

    def transform_modes(self, context):
        mix_types = (
            ('0', "UV", ""),
            ('1', "Normal", ""),
            ('2', "Position", ""),
        )
        return mix_types

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

    def update_mode(self, context):
        if not self.transform_mode:
            self.transform_mode = self.transform_modes(context)[0][0]
        mix_types = {
            "0": '.NN_VECTOR_UV',
            "1": '.NN_VECTOR_NORMAL',
            "2": '.NN_VECTOR_POSITION',
        }
        self.node_tree = bpy.data.node_groups[mix_types[self.transform_mode]]

        if self.transform_mode in {'2', '3'}:
            self.inputs["UV Map"].hide = True
        else:
            self.inputs["UV Map"].hide = False

    def update_u(self, context):
        if not self.u_type:
            self.u_type = self.u_types(context)[1][0]

        self.inputs["U"].default_value = int(self.u_type)

    def update_v(self, context):
        if not self.v_type:
            self.v_type = self.v_types(context)[1][0]

        self.inputs["V"].default_value = int(self.v_type)

    u_type: EnumProperty(name="U Wrapping", update=update_u, items=u_types, options=set())
    v_type: EnumProperty(name="V Wrapping", update=update_v, items=v_types, options=set())
    transform_mode: EnumProperty(name="Transform Mode", update=update_mode, items=transform_modes, options=set())

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NN_VECTOR_UV']
        self.transform_mode = self.transform_modes(context)[0][0]
        self.u_type = self.u_types(context)[1][0]
        self.v_type = self.v_types(context)[1][0]
        self.inputs["U"].hide = True
        self.inputs["V"].hide = True
        self.inputs["UV Rotation"].hide = True
        self.inputs["UV Scale"].hide = True


class ShaderNodeXNOVector(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "XNO Vector"
    bl_idname = "ShaderNodeXNOVector"
    bl_width_default = 180

    def transform_modes(self, context):
        mix_types = (
            ('0', "UV", ""),
            ('1', "Normal", ""),
            ('2', "Position", ""),
        )
        return mix_types

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

    def update_mode(self, context):
        if not self.transform_mode:
            self.transform_mode = self.transform_modes(context)[0][0]
        mix_types = {
            "0": '.NN_VECTOR_UV',
            "1": '.NN_VECTOR_NORMAL',
            "2": '.NN_VECTOR_POSITION',
        }
        self.node_tree = bpy.data.node_groups[mix_types[self.transform_mode]]

        if self.transform_mode in {'2', '3'}:
            self.inputs["UV Map"].hide = True
        else:
            self.inputs["UV Map"].hide = False

    def update_u(self, context):
        if not self.u_type:
            self.u_type = self.u_types(context)[1][0]

        self.inputs["U"].default_value = int(self.u_type)

    def update_v(self, context):
        if not self.v_type:
            self.v_type = self.v_types(context)[1][0]

        self.inputs["V"].default_value = int(self.v_type)

    u_type: EnumProperty(name="U Wrapping", update=update_u, items=u_types, options=set())
    v_type: EnumProperty(name="V Wrapping", update=update_v, items=v_types, options=set())
    transform_mode: EnumProperty(name="Transform Mode", update=update_mode, items=transform_modes, options=set())
    lod_bias: FloatProperty(name="LOD bias", min=-1, max=1, options=set())
    max_mip_map_level: IntProperty(name="Max MipMap Level", min=0, options=set())
    custom_filter: BoolProperty(name="Custom interpolation", description='Override texture interpolation',
                                default=False, options=set())
    interp_min: bpy.props.EnumProperty(
        name="Interpolation Min", description="Texture interpolation when far",
        items=(
            ('Closest', 'Closest', ""),
            ('Linear', 'Linear', ""),
            ('Closest MipMap Closest', 'Closest MipMap Closest', ""),
            ('Closest MipMap Linear', 'Closest MipMap Linear', ""),
            ('Linear MipMap Closest', 'Linear MipMap Closest', "CNO, ENO, INO, LNO, SNO, UNO, XNO, ZNO STANDARD"),
            ('Linear MipMap Linear', 'Linear MipMap Linear', "GNO STANDARD"),
            ('Anisotropic', 'Anisotropic', "Xbox only"),
            ('Anisotropic MipMap Closest', 'Anisotropic MipMap Closest', "Xbox only"),
            ('Anisotropic MipMap Linear', 'Anisotropic MipMap Linear', "Xbox only"),
            ('Anisotropic4', 'Anisotropic4', "Xbox only"),
            ('Anisotropic4 MipMap Closest', 'Anisotropic4 MipMap Closest', "Xbox only"),
            ('Anisotropic4 MipMap Linear', 'Anisotropic4 MipMap Linear', "Xbox only"),
            ('Anisotropic8', 'Anisotropic8', "Xbox only"),
            ('Anisotropic8 MipMap Closest', 'Anisotropic8 MipMap Closest', "Xbox only"),
            ('Anisotropic8 MipMap Linear', 'Anisotropic8 MipMap Linear', "Xbox only"),
        ), options=set())
    interp_mag: bpy.props.EnumProperty(
        name="Interpolation Mag", description="Texture interpolation when close",
        items=(('Closest', 'Closest', ""), ('Linear', 'Linear', ""), ('Anisotropic', 'Anisotropic', "XBOX")), options=set())

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NN_VECTOR_UV']
        self.transform_mode = self.transform_modes(context)[0][0]
        self.u_type = self.u_types(context)[1][0]
        self.v_type = self.v_types(context)[1][0]
        self.inputs["U"].hide = True
        self.inputs["V"].hide = True
        self.inputs["UV Rotation"].hide = True
        self.inputs["UV Scale"].hide = True
        self.inputs["Normal Map"].hide = True


classes = (
    ShaderNodeGNOMixRGB,
    ShaderNodeGNOShader,
    ShaderNodeGNOShaderInit,
    ShaderNodeGNOSpecular,
    ShaderNodeGNOVector,
    ShaderNodeXNOMixRGB,
    ShaderNodeXNOSpecular,
    ShaderNodeXNOShaderInit,
    ShaderNodeXNOShader,
    ShaderNodeXNOVector,
)
