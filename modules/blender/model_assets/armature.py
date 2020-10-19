import bpy
from mathutils import Matrix


class Armature:
    def make_bones_type_1(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        bone_names = self.bone_names
        max_len = self.settings.max_bone_length
        armature = bpy.context.object.data
        tail_var = self.settings.format_bone_scale
        for i in range(bone_count):
            b = bone_data[i]
            bone = armature.edit_bones.new(bone_names[i])

            if b.parent != 65535:
                bone.parent = armature.edit_bones[b.parent]
            matrix = Matrix(b.position).transposed().inverted_safe()  # there are unsafe matrices
            bone.tail = b.relative  # they store the position relative to parent bone
            bone.transform(matrix)  # this isn't the correct usage but it looks nice!
            if not 0.0001 < bone.length < tail_var * max_len:
                bone.length = tail_var  # len too small = bone isn't made, len too big = can't see anything in blender
            bone.roll = 0

        if self.settings.all_bones_one_length:
            for bone in armature.edit_bones:
                bone.length = tail_var

    def make_bones_type_2(self):  # this needs to be updated
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        bone_names = self.bone_names
        max_len = self.settings.max_bone_length
        armature = bpy.context.object.data
        tail_var = self.settings.format_bone_scale
        for i in range(bone_count):
            b = bone_data[i]
            bone = armature.edit_bones.new(bone_names[i])

            if b.parent != 65535:
                bone.parent = armature.edit_bones[b.parent]
            matrix = Matrix(b.position).transposed().inverted_safe()
            bone.tail = b.relative  # is this what they actually use that var for? no
            bone.transform(matrix)  # does it look cool? yes, so i'll be doing it
            if not 0.0001 < bone.length < tail_var * max_len:  # len too small = bone isnt made, len too big = cant see
                bone.length = tail_var
            bone.roll = 0

        if self.settings.all_bones_one_length:
            for bone in armature.edit_bones:
                bone.length = tail_var

    def make_armature(self):
        bpy.ops.object.add(type="ARMATURE", enter_editmode=True)  # first we make an armature
        obj = bpy.context.object
        obj.name = obj.data.name = self.model_name  # Object name, Armature name
        obj.rotation_euler[0] = 1.5708  # rotate to stand up

    @staticmethod
    def hide_null_bones():  # in riders these have no weights - 06 has unweighted but they don't have the group
        pose = bpy.context.object.pose
        pose.bone_groups.active = pose.bone_groups[0]  # group is always made and index 0
        bpy.ops.pose.group_select()
        bpy.ops.pose.hide(unselected=False)

    def scale_bones(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        pose = bpy.context.object.pose
        for i in range(bone_count):
            bpy.context.object.data.bones[i].inherit_scale = 'NONE'
            pose.bones[i].scale = bone_data[i].scale

    def make_bone_groups(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        group_names = self.group_names
        pose = bpy.context.object.pose
        if self.model_name_strip + "_Bone_Group_" + "65535" in group_names:
            no_weights = pose.bone_groups.new(name="Null_Bone_Group")
            no_weights.color_set = "THEME08"  # makes it clearer

        for i in range(bone_count):
            bone = pose.bones[i]
            if bone_data[i].group != 65535:  # bone has weights
                bone.bone_group = pose.bone_groups.new(name=group_names[i])
            else:  # bone doesn't have weights
                bone.bone_group = no_weights
