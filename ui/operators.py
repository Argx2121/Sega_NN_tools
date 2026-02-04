import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty
from ..modules.blender.model_assets.node_groups import MakeGroups
from ..io.nn_import_data import no_export_list
from ..modules.util import get_bpy_meshes
from dataclasses import dataclass


def convert_materials(operator, context, checkma):
    tree = context.space_data.node_tree
    MakeGroups().execute()
    settings = operator
    if checkma:
        model_end = checkma[0]
        checkma = checkma[1]
    else:
        model_end = settings.nn_format
    spec_mix = False  # as specular is mixed in a node, we need to make sure that node gets spawned in
    # if it isnt spawned in during the image node loop we will add it at the end

    existing_diffuse = None
    # using a separate toggle for when its called elsewhere because running modal can mess up, that means other texture
    #  data may be missed, shrug

    if checkma:
        node = tree.nodes.get("Image Texture")  # blender wants node name w/e
        if node and node.image:
            existing_diffuse = node.image
        else:
            for node in tree.nodes:
                if node.bl_idname == "ShaderNodeTexImage" and node.image:
                    existing_diffuse = node.image

    for node in tree.nodes:
        tree.nodes.remove(node)

    end_node = tree.nodes.new("ShaderNodeOutputMaterial")
    shader = tree.nodes.new('ShaderNodeGNOShader')
    colour_init = tree.nodes.new('ShaderNodeGNOShaderInit')
    x_loc = -400
    y_loc = 300
    colour_init.location = (x_loc, y_loc)

    if not checkma:
        shader.nn_blend_method = settings.blend_mode
        colour_init.unshaded = settings.unshaded
        colour_init.use_specular = settings.use_specular
        shader.use_backface_culling = settings.backface

        if settings.vertex_color:
            node = tree.nodes.new(type="ShaderNodeVertexColor")
            tree.links.new(colour_init.inputs["Vertex Color"], node.outputs[0])
            tree.links.new(colour_init.inputs["Vertex Alpha"], node.outputs[1])
            node.location = (x_loc - 200, y_loc)

    tree.links.new(end_node.inputs[0], shader.outputs[0])
    last_node = colour_init

    if checkma:
        if existing_diffuse:
            vector_node = tree.nodes.new(type="ShaderNode" + model_end + "NOVector")
            image_node = tree.nodes.new(type="ShaderNodeTexImage")
            image_node.image = existing_diffuse
            tree.links.new(image_node.inputs["Vector"], vector_node.outputs["Image Vector"])

            node = tree.nodes.new(type="ShaderNodeUVMap")
            node.location = (x_loc - 500, y_loc - 1100)
            tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])

            image_node.location = (x_loc, y_loc - 450)
            vector_node.location = (x_loc - 300, y_loc - 800)
            mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOMixRGB')
            x_loc += 400
            mix_node.location = (x_loc, y_loc)

            tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
            tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
            last_node = mix_node

        # forced to add to make specular be mixed in
        mix_type = '.GNO_SPEC'
        mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
        mix_node.blend_type = mix_type
        x_loc += 400
        mix_node.location = (x_loc, y_loc)

        tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        last_node = mix_node

        tree.links.new(shader.inputs["Color"], last_node.outputs[0])
        tree.links.new(shader.inputs["Alpha"], last_node.outputs[1])
        x_loc += 400
        shader.location = (x_loc, y_loc)
        x_loc += 400
        end_node.location = (x_loc, y_loc)
        return

    for tex in context.window_manager.nn_texture_setups:
        vector_node = tree.nodes.new(type="ShaderNode" + model_end + "NOVector")
        image_node = tree.nodes.new(type="ShaderNodeTexImage")
        image_node.image = tex.texture
        tree.links.new(image_node.inputs["Vector"], vector_node.outputs["Image Vector"])

        image_node.location = (x_loc, y_loc - 450)
        vector_node.location = (x_loc - 300, y_loc - 800)

        vector_node.transform_mode = tex.vector
        vector_node.u_type = tex.u_wrap
        vector_node.v_type = tex.v_wrap
        if model_end == 'G':
            mix_type = tex.mix_g
        elif model_end == 'X':
            mix_type = tex.mix_x

        if tex.vector == "0":
            node = tree.nodes.new(type="ShaderNodeUVMap")
            node.location = (x_loc - 500, y_loc - 1100)
            tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])

        if 'SPEC' in mix_type:
            spec_mix = True
            mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
            mix_node.blend_type = mix_type
            x_loc += 400
            mix_node.location = (x_loc, y_loc)

            tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
            tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
            tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
            last_node = mix_node
        else:
            mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOMixRGB')
            mix_node.blend_type = mix_type
            x_loc += 400
            mix_node.location = (x_loc, y_loc)

            tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
            tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
            last_node = mix_node

        if tex.multi_shading:
            mix_node.multi_shading = True

    if not spec_mix:
        # forced to add to make specular be mixed in
        mix_type = '.GNO_SPEC'
        mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
        mix_node.blend_type = mix_type
        x_loc += 400
        mix_node.location = (x_loc, y_loc)

        tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        last_node = mix_node

    tree.links.new(shader.inputs["Color"], last_node.outputs[0])
    tree.links.new(shader.inputs["Alpha"], last_node.outputs[1])
    x_loc += 400
    shader.location = (x_loc, y_loc)
    x_loc += 400
    end_node.location = (x_loc, y_loc)


def tx2_update(self, context):  # i want to blow the devs up. be for real.
    # and then we made operator capable of literally NOTHING. ehe ^-^
    while self.texture_count2 > len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.add()
    while self.texture_count2 < len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.remove(len(context.window_manager.nn_texture_setups)-1)


def tx4_update(self, context):
    while self.texture_count4 > len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.add()
    while self.texture_count4 < len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.remove(len(context.window_manager.nn_texture_setups)-1)


def tx8_update(self, context):
    while self.texture_count8 > len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.add()
    while self.texture_count8 < len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.remove(len(context.window_manager.nn_texture_setups)-1)


def tx16_update(self, context):
    while self.texture_count16 > len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.add()
    while self.texture_count16 < len(context.window_manager.nn_texture_setups):
        context.window_manager.nn_texture_setups.remove(len(context.window_manager.nn_texture_setups)-1)


class NodeNNSetup(bpy.types.Operator):
    """Spawn in a NN node set up"""
    bl_idname = "node.nn_operator"
    bl_label = "NN Node Setup"

    nn_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_export_list,
        default=no_export_list[0][0],
    )

    checkma: BoolProperty(
        name="checkma",
        description="i dont think people will be able to see this",
        default=False,
    )

    texture_count2: IntProperty(
        name="Texture Count",
        description="Amount of textures to use",
        default=0,
        min=0,
        max=2,
        update=tx2_update
    )

    texture_count4: IntProperty(
        name="Texture Count",
        description="Amount of textures to use",
        default=0,
        min=0,
        max=4,
        update=tx4_update
    )

    texture_count8: IntProperty(
        name="Texture Count",
        description="Amount of textures to use",
        default=0,
        min=0,
        max=8,
        update=tx8_update
    )

    texture_count16: IntProperty(
        name="Texture Count",
        description="Amount of textures to use",
        default=0,
        min=0,
        max=16,
        update=tx16_update
    )
    unshaded: bpy.props.BoolProperty("Unshaded", default=False)
    use_specular: bpy.props.BoolProperty("Use Specular", default=True)
    vertex_color: bpy.props.BoolProperty("Vertex colors", default=False)
    backface: bpy.props.BoolProperty("Backface Culling", default=True)
    blend_mode: EnumProperty(
        name="Blend Mode", items=(('OPAQUE', "Opaque", ""), ('BLEND', "Alpha Blend", ""), ('CLIP', "Alpha Clip", "")))

    def invoke(self, context, event):
        tree = context.space_data.node_tree
        textures = []
        for node in tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage" and node.image:
                textures.append(node.image)

        self.texture_count2 = len(textures)
        self.texture_count4 = len(textures)
        self.texture_count8 = len(textures)
        self.texture_count16 = len(textures)
        for i, image in enumerate(textures):
            context.window_manager.nn_texture_setups[i].texture = image
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "nn_format")

        layout.label(text="Material settings:", icon="KEYFRAME_HLT")
        box = layout.box()
        box.prop(self, "unshaded", text="Unshaded")
        box.prop(self, "use_specular", text="Use Specular")
        box.prop(self, "vertex_color", text="Vertex Color")
        box.prop(self, "backface", text="Backface Culling")
        box.prop(self, "blend_mode", text="")

        row = layout.row()
        row.label(text="Texture settings:", icon="KEYFRAME_HLT")
        if self.nn_format in {"G", "X"}:
            row.prop(self, "texture_count4", expand=False, text="Count")
        elif self.nn_format in {"Z", "E"}:  # i think eno goes here
            row.prop(self, "texture_count16")

        for i in range(len(context.window_manager.nn_texture_setups)):
            this_image = context.window_manager.nn_texture_setups[i]
            box = layout.box()
            row = box.row(align=True)
            row.prop(this_image, "texture", text="")
            row = box.row()
            mix_prop = 'mix_' + self.nn_format.lower()
            row.prop(this_image, mix_prop, text="")
            row.prop(this_image, "multi_shading", text="Mix-in Shading")
            row = box.row()
            row.prop(this_image, "vector", text="")
            row.prop(this_image, "u_wrap", text="")
            row.prop(this_image, "v_wrap", text="")

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        convert_materials(self, context, False)
        return {'FINISHED'}


class SetFCurves(bpy.types.Operator):
    """Set the FCurves for NN"""
    bl_idname = "fcurve.nn_fcurve"
    bl_label = "Set FCurve Data"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    interpolation: bpy.props.EnumProperty(name="Interpolation", items=(
        ("none", "Don't Adjust", "Don't adjust"),
        ("spline", "Spline", "Set interpolation to spline"),
        ("linear", "Linear", "Set interpolation to Linear"),
        ("constant", "Constant", "Set interpolation to Constant"),
        ("bezier", "Bezier", "Set interpolation to Bezier (Will reset existing curves!)")), default="none")

    repeat: bpy.props.EnumProperty(name="Repeat", items=(
        ("none", "Don't Adjust", "Don't adjust"),
        ("no_repeat", "No Repeat", "Make the fcurve not repeat"),
        ("cons_repeat", "Hold Values", "Hold the Start and End frame"),
        ("repeat", "Repeat", "Repeat fcurve"),
        ("mirror", "Mirror", "Mirror animation")), default="none")

    trigger: bpy.props.BoolProperty(name="Trigger")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN Fcurve Settings")
        box = layout.box()
        if not self.trigger:
            box.label(text="Interpolation Settings:")
            box.prop(self, "interpolation", text="")
            box.label(text="Repeat Settings:")
            box.prop(self, "repeat", text="")
        box.prop(self, "trigger")

    def execute(self, context):
        for curve in context.selected_editable_fcurves:
            if self.trigger:
                for mod in curve.modifiers:
                    curve.modifiers.remove(mod)
                modifier = curve.modifiers.new('LIMITS')
                modifier.use_min_x = False
                modifier.use_max_x = False
                modifier.use_min_y = False
                modifier.use_max_y = False
                curve.update()
                continue

            if self.repeat == "none":
                pass
            elif self.repeat == "no_repeat":
                for mod in curve.modifiers:
                    curve.modifiers.remove(mod)
                modifier = curve.modifiers.new(type='LIMITS')
                modifier.use_min_x = False
                modifier.use_max_x = False
                modifier.use_min_y = True
                modifier.use_max_y = True
                modifier.use_restricted_range = True
                modifier.frame_start = curve.keyframe_points[-1].co[0]
                modifier.frame_end = 100000  # seems reasonable
            else:
                before = "NONE"
                after = "NONE"
                if self.repeat == "cons_repeat":
                    before = "NONE"
                    after = "NONE"
                elif self.repeat == "repeat":
                    before = "REPEAT"
                    after = "REPEAT"
                elif self.repeat == "mirror":
                    before = "MIRROR"
                    after = "MIRROR"
                for mod in curve.modifiers:
                    curve.modifiers.remove(mod)
                modifier = curve.modifiers.new(type='CYCLES')
                modifier.mode_after = before
                modifier.mode_before = after
            if self.interpolation == "none":
                pass
            elif self.interpolation == "spline":
                for kf in curve.keyframe_points:
                    kf.interpolation = 'CUBIC'
            elif self.interpolation == "linear":
                for kf in curve.keyframe_points:
                    kf.interpolation = 'LINEAR'
            elif self.interpolation == "constant":
                for kf in curve.keyframe_points:
                    kf.interpolation = 'CONSTANT'
            elif self.interpolation == "bezier":
                for kf in curve.keyframe_points:
                    kf.interpolation = 'BEZIER'
                    kf.handle_left_type = "FREE"
                    kf.handle_right_type = "FREE"
            curve.update()

        return {"FINISHED"}


class NNObjectSpawner(bpy.types.Operator):
    """Spawn in a NN Object"""
    bl_idname = "object.nn_spawner"
    bl_label = "NN Object Spawner"

    camera: EnumProperty(
        name="Camera Type",
        items=(
            ('target', "Target", "Camera has an object that defines its rotation and roll"),
            ('rotate', "Rotate", "Uses cameras rotation"),
            ('up', "Up Vector", "Camera has an object that defines rotation and another object defines up")),
        default='target'
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN Object Setup")
        box = layout.box()
        box.label(text="Camera settings:", icon="KEYFRAME_HLT")
        box.prop(self, "camera", text="")

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'VIEW_3D'

    def execute(self, context):
        if self.camera == 'rotate':
            cam = bpy.data.cameras.new('NewCamera')
            obj = bpy.data.objects.new(cam.name, cam)
            context.collection.objects.link(obj)
        elif self.camera == 'target':
            cam = bpy.data.cameras.new('NewCamera')
            obj = bpy.data.objects.new(cam.name, cam)
            context.collection.objects.link(obj)
            target = bpy.data.objects.new(cam.name + "_Target", None)
            context.collection.objects.link(target)
            const = obj.constraints.new(type='TRACK_TO')
            const.target = target
            const.track_axis = 'TRACK_NEGATIVE_Z'
            const.up_axis = 'UP_Y'
            const.owner_space = 'LOCAL'
            const.use_target_z = True
            copyrot = obj.constraints.new(type='COPY_ROTATION')
            copyrot.target = target
            copyrot.use_x = False
            copyrot.use_y = False
            copyrot.use_z = True
            copyrot.mix_mode = 'AFTER'
            copyrot.owner_space = 'LOCAL'
        elif self.camera == 'up':
            cam = bpy.data.cameras.new('NewCamera')
            obj = bpy.data.objects.new(cam.name, cam)
            context.collection.objects.link(obj)
            target = bpy.data.objects.new(cam.name + "_Target", None)
            context.collection.objects.link(target)
            const = obj.constraints.new(type='TRACK_TO')
            const.target = target
            const.track_axis = 'TRACK_NEGATIVE_Z'
            const.up_axis = 'UP_Y'
            const.owner_space = 'LOCAL'
            const.use_target_z = True
            up_vector = bpy.data.objects.new(cam.name + "_Up_Vector", None)
            context.collection.objects.link(up_vector)
            const = target.constraints.new(type='TRACK_TO')
            const.target = up_vector
            const.track_axis = 'TRACK_Z'
            const.up_axis = 'UP_X'
        return {'FINISHED'}


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


class GetNNMaterials(bpy.types.Operator):
    """Get Materials from this Armature and sets them in the Material list"""
    bl_idname = "operator.nn_get_materials"
    bl_label = "Get Materials"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE':
            return {'FINISHED'}
        materials = set()
        for child in get_bpy_meshes(context, obj, no_poly_test=True):
            for m_slot in child.material_slots:
                materials.add(m_slot.material)
        materials = list(materials)
        mat_end = []
        for i, mat in enumerate(materials):
            if mat.blend_method == "BLEND" or mat.blend_method == "CLIP":
                mat_end.append(i)
        for i in reversed(mat_end):
            materials.append(materials.pop(i))
        obj.data.nn_material_count = len(materials)
        for i in range(len(materials)):
            obj.data.nn_materials[i].material = materials[i]
        return {'FINISHED'}


class GetNNTextures(bpy.types.Operator):
    """Get Textures from this Armature and sets them in the Textures list, allocates new index"""
    bl_idname = "operator.nn_get_textures"
    bl_label = "Get Textures"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE':
            return {'FINISHED'}
        materials = set()
        for child in get_bpy_meshes(context, obj, no_poly_test=True):
            for m_slot in child.material_slots:
                materials.add(m_slot.material)
        materials = list(materials)
        textures = set()

        for material in materials:
            if material.node_tree:
                for node in material.node_tree.nodes:
                    node_n = node.bl_idname
                    if node_n.startswith('ShaderNode') and (
                            node_n.endswith('NOMixRGB') or node_n.endswith('NOSpecular')):
                        node.texture_2 = int(node.texture_2)
                        for node_l in node.inputs['Color 2'].links:
                            if node_l.from_node.bl_idname == 'ShaderNodeTexImage':
                                texture = node_l.from_node.image
                                interp = node_l.from_node.interpolation
                                textures.add((texture, interp))

        textures = list(textures)
        obj.data.nn_texture_count = len(textures)
        for i in range(len(textures)):
            obj.data.nn_textures[i].texture = textures[i][0]
            obj.data.nn_textures[i].interp_mag = textures[i][1]
        return allocate_indices(context)


class AssignNNTexturesIndices(bpy.types.Operator):
    """Assign this Armature's Textures Indices in the Materials"""
    bl_idname = "operator.nn_assign_indices_textures"
    bl_label = "Assign Texture Indices"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        return allocate_indices(context)


def allocate_indices(context):  # separate because i KNOW what blender will do
    obj = context.object
    if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE':
        return {'FINISHED'}
    materials = set()
    list_of_tex = []
    for i in range(obj.data.nn_texture_count):
        if not obj.data.nn_textures[i].texture:
            return {'FINISHED'}
        list_of_tex.append((obj.data.nn_textures[i].texture, obj.data.nn_textures[i].interp_mag))
    for child in get_bpy_meshes(context, obj, no_poly_test=True):
        for m_slot in child.material_slots:
            materials.add(m_slot.material)
    for material in list(materials):
        if material.node_tree:
            for node in material.node_tree.nodes:
                node_n = node.bl_idname
                if node_n.startswith('ShaderNode') and (node_n.endswith('NOMixRGB') or node_n.endswith('NOSpecular')):
                    for node_l in node.inputs['Color 2'].links:
                        if node_l.from_node.bl_idname == 'ShaderNodeTexImage':
                            texture = node_l.from_node.image
                            interp = node_l.from_node.interpolation
                            this_image = (texture, interp)
                            node.texture_2 = list_of_tex.index(this_image)
    return {'FINISHED'}


def armature_list(scene, context):
    items = [("nn_no_armature", "No Armature", "")]
    armatures = [(a.name, a.name, "") for a in bpy.data.armatures]
    items += armatures
    return items


class CopyNNTextures(bpy.types.Operator):
    """Get Textures from another Armature and set them to this ones Texture list"""
    bl_idname = "operator.nn_copy_textures"
    bl_label = "Copy Textures"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    arma_list: EnumProperty(
        name="Armature",
        items=armature_list,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN Object Setup")
        box = layout.box()
        box.label(text="Armature to copy:", icon="KEYFRAME_HLT")
        box.prop(self, "arma_list", text="")

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'VIEW_3D'

    def execute(self, context):
        obj = context.object
        if self.arma_list == "nn_no_armature":
            return {'FINISHED'}
        copy_arma = bpy.data.armatures[self.arma_list]

        while copy_arma.nn_texture_count > obj.data.nn_texture_count:
            obj.data.nn_texture_count += 1
            context.object.data.nn_textures.add()
        while copy_arma.nn_texture_count < obj.data.nn_texture_count:
            obj.data.nn_texture_count -= 1
            context.object.data.nn_textures.remove(len(context.object.data.nn_textures)-1)

        for tex_old, tex_new in zip(obj.data.nn_textures, copy_arma.nn_textures):
            tex_old.texture = tex_new.texture

        obj.data.nn_texture_count = copy_arma.nn_texture_count
        return {'FINISHED'}


class SyncNNTextures(bpy.types.Operator):
    """Update Material Textures with the textures in Texture list"""
    bl_idname = "operator.nn_sync_textures"
    bl_label = "Sync Textures"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE':
            return {'FINISHED'}
        materials = set()
        for i in range(obj.data.nn_texture_count):
            if not obj.data.nn_textures[i].texture:
                return {'FINISHED'}
        for child in get_bpy_meshes(context, obj, no_poly_test=True):
            for m_slot in child.material_slots:
                materials.add(m_slot.material)
        for material in list(materials):
            if material.node_tree:
                for node in material.node_tree.nodes:
                    node_n = node.bl_idname
                    if node_n.startswith('ShaderNode') and (node_n.endswith('NOMixRGB') or node_n.endswith('NOSpecular')):
                        node.texture_2 = int(node.texture_2)
                        for node_l in node.inputs['Color 2'].links:
                            if node_l.from_node.bl_idname == 'ShaderNodeTexImage' and obj.data.nn_textures[node.texture_2].interp_mag in {'Linear', 'Closest'}:
                                node_l.from_node.interpolation = obj.data.nn_textures[node.texture_2].interp_mag

        return {'FINISHED'}


class SetNNBones(bpy.types.Operator):
    """Assign Selected Meshes to this bones Mesh Visibility list"""
    bl_idname = "operator.nn_set_bones"
    bl_label = "Set Bone Visibility"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE' and obj.mode != "POSE" and not context.active_pose_bone:
            return {'FINISHED'}
        meshes = [a for a in bpy.context.selected_objects if a.data.id_type == "MESH"]
        for bone in obj.pose.bones:
            bone_meshes = [bone.nn_meshes[i].mesh for i in range(bone.nn_mesh_count) if bone.nn_meshes[i].mesh not in meshes]
            if bone.nn_mesh_count != len(bone_meshes):
                bone.nn_mesh_count = len(bone_meshes)
                for i in range(len(bone_meshes)):
                    bone.nn_meshes[i].mesh = bone_meshes[i]
        context.active_pose_bone.nn_mesh_count = len(meshes)
        for i in range(len(meshes)):
            context.active_pose_bone.nn_meshes[i].mesh = meshes[i]
        return {'FINISHED'}


class GuessNNBones(bpy.types.Operator):
    """Guess what meshes you want assigned to bones"""
    bl_idname = "operator.nn_guess_bones"
    bl_label = "Assign Meshes to Bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE' and obj.mode != "OBJECT":
            return {'FINISHED'}
        meshes = get_bpy_meshes(context, obj, no_poly_test=True)

        for bone in obj.pose.bones:
            if bone.nn_mesh_count != 0:
                bone.nn_mesh_count = 0

        for ind, child in enumerate(meshes):
            vert_names = [a.name for a in child.vertex_groups]
            if len(vert_names) == 1:
                obj.pose.bones[vert_names[0]].nn_mesh_count += 1
                obj.pose.bones[vert_names[0]].nn_meshes[obj.pose.bones[vert_names[0]].nn_mesh_count-1].mesh = child
            elif len(vert_names) == 0:
                pass  # uhm..?
            else:
                obj.pose.bones[-1].nn_mesh_count += 1
                obj.pose.bones[-1].nn_meshes[obj.pose.bones[-1].nn_mesh_count-1].mesh = child
        return {'FINISHED'}


class ShowNNBones(bpy.types.Operator):
    """Unhide any meshes hidden by bones"""
    bl_idname = "operator.nn_unhide_bones"
    bl_label = "Unhide Meshes from Bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE' and obj.mode != "OBJECT":
            return {'FINISHED'}

        for bone in obj.pose.bones:
            if bone.nn_mesh_count and bone.nn_hide:
                bone.nn_hide = False
        return {'FINISHED'}


class ReorderNNItem(bpy.types.Operator):
    """Move this element"""
    bl_idname = "operator.nn_change_index"
    bl_label = "Move NN element"
    bl_options = {'REGISTER', 'INTERNAL'}

    index: IntProperty(
        name="index",
        description="",
        default=-1,
    )

    up: BoolProperty(
        name="up",
        description="",
        default=False,
    )

    material: BoolProperty(
        name="material",
        description="",
        default=False,
    )

    def execute(self, context):
        obj = context.active_object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE' and obj.mode != "OBJECT":
            return {'FINISHED'}

        if self.material:
            data_path = obj.data.nn_materials
            count = obj.data.nn_material_count
        else:
            data_path = obj.data.nn_textures
            count = obj.data.nn_texture_count

        index = self.index
        current_item = data_path[index]
        if 2 > count:
            return {'FINISHED'}
        if index == 0 and self.up:
            return {'FINISHED'}
        if (index+1 == count) and not self.up:
            return {'FINISHED'}

        ignore_props = {'rna_type', 'name'}

        current_item_props = []
        for the_prop, prop_set in current_item.bl_rna.properties.items():
            if the_prop not in ignore_props:
                current_item_props.append((the_prop, getattr(current_item, the_prop)))

        if self.up:
            item_before = data_path[index-1]
            item_before_props = []
            for the_prop, prop_set in item_before.bl_rna.properties.items():
                if the_prop not in ignore_props:
                    item_before_props.append((the_prop, getattr(item_before, the_prop)))

            for the_prop, prop_set in current_item_props:
                setattr(item_before, the_prop, prop_set)
            for the_prop, prop_set in item_before_props:
                setattr(current_item, the_prop, prop_set)
        else:
            item_after = data_path[index+1]
            item_after_props = []
            for the_prop, prop_set in item_after.bl_rna.properties.items():
                if the_prop not in ignore_props:
                    item_after_props.append((the_prop, getattr(item_after, the_prop)))

            for the_prop, prop_set in item_after_props:
                setattr(current_item, the_prop, prop_set)
            for the_prop, prop_set in current_item_props:
                setattr(item_after, the_prop, prop_set)
        return {'FINISHED'}
