import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty
from ..modules.blender.model_assets.node_groups import MakeGroups
from ..io.nn_import_data import no_export_list
from ..modules.util import get_bpy_meshes
from dataclasses import dataclass


def convert_materials(operator, context, settings):
    tree = context.space_data.node_tree
    MakeGroups().execute()
    model_end = settings.nn_format
    existing_diffuse = None
    checkma = settings.checkma  # this means make sure there is an existing texture

    if settings.existing_diffuse:
        node = tree.nodes.get("Image Texture")  # blender wants node name w/e
        if node and node.image:
            existing_diffuse = node.image
        else:
            for node in tree.nodes:
                if node.bl_idname == "ShaderNodeTexImage" and node.image:
                    existing_diffuse = node.image

    if settings.remove_existing:
        for node in tree.nodes:
            tree.nodes.remove(node)

    shader = tree.nodes.new('ShaderNode' + model_end + 'NOShader')
    shader.location = (10, 310)
    colour_init = tree.nodes.new('ShaderNode' + model_end + 'NOShaderInit')
    colour_init.location = (-1970, 450)
    last_node = colour_init

    node = tree.nodes.get("Material Output")
    if node:
        tree.links.new(node.inputs[0], shader.outputs[0])
    else:
        node = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(node.inputs[0], shader.outputs[0])
    node.location = (300, 300)

    if settings.vertex_color:
        vertex_color = tree.nodes.new(type="ShaderNodeVertexColor")
        vertex_color.location = (-2260, 260)
        tree.links.new(colour_init.inputs["Vertex Color"], vertex_color.outputs[0])
        tree.links.new(colour_init.inputs["Vertex Alpha"], vertex_color.outputs[1])

    if settings.diffuse:
        if checkma and not existing_diffuse:
            pass
        else:
            image = tree.nodes.new(type="ShaderNodeTexImage")
            image.location = (-1640, 250)
            image.label = "Diffuse Texture"
            vector = tree.nodes.new(type='ShaderNode' + model_end + 'NOVector')
            vector.location = (-1940, 10)
            uv = tree.nodes.new(type="ShaderNodeUVMap")
            uv.location = (-2170, -120)
            mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOMixRGB')
            mix_node.location = (-1250, 500)
            mix_node.blend_type = '.GNO_MULTI'

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
        vector = tree.nodes.new(type='ShaderNode' + model_end + 'NOVector')
        vector.location = (-1440, -50)
        vector.inputs["Reflection Vector"].default_value = True
        mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOMixRGB')
        mix_node.location = (-770, 410)
        mix_node.blend_type = '.GNO_MULTI'

        tree.links.new(image.inputs["Vector"], vector.outputs["Image Vector"])
        tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        last_node = mix_node

    mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
    mix_node.location = (-320, 320)
    mix_node.blend_type = '.GNO_SPEC'

    tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
    tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
    tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
    last_node = mix_node

    if settings.specular:
        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-700, 70)
        image.label = "Specular Texture"
        vector = tree.nodes.new(type='ShaderNode' + model_end + 'NOVector')
        vector.location = (-940, -140)
        uv = tree.nodes.new(type="ShaderNodeUVMap")
        uv.location = (-1150, -260)

        tree.links.new(mix_node.inputs["Color 2"], image.outputs[0])
        tree.links.new(mix_node.inputs["Alpha 2"], image.outputs[1])
        tree.links.new(image.inputs["Vector"], vector.outputs["Image Vector"])
        tree.links.new(vector.inputs["UV Map"], uv.outputs[0])

    tree.links.new(shader.inputs["Color"], last_node.outputs[0])
    tree.links.new(shader.inputs["Alpha"], last_node.outputs[1])


class NodeNNSetup(bpy.types.Operator):
    """Spawn in a NN node set up"""
    bl_idname = "node.nn_operator"
    bl_label = "NN Node Operator"

    nn_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_export_list,
        default=no_export_list[0][0],
    )

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

    checkma: BoolProperty(
        name="checkma",
        description="i dont think people will be able to see this",
        default=False,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN Node Setup")
        box = layout.box()
        box.prop(self, "nn_format")
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
        settings = SetGno(self.nn_format, self.diffuse, self.specular, self.reflection, self.vertex_color,
                          self.existing_diffuse, self.remove_existing, self.checkma)
        convert_materials(self, context, settings)
        return {'FINISHED'}


@dataclass
class SetGno:
    nn_format: bool
    diffuse: bool
    specular: bool
    reflection: bool
    vertex_color: bool
    existing_diffuse: bool
    remove_existing: bool
    checkma: bool


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
                    if node_n.startswith('ShaderNodeG') and (node_n.endswith('NOMixRGB') or node_n.endswith('NOSpecular')):
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
                obj.pose.bones[-1].nn_meshes[obj.pose.bones[vert_names[0]].nn_mesh_count-1].mesh = child
        return {'FINISHED'}
