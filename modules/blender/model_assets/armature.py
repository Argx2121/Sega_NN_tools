import bpy
import mathutils


def make_bones_accurate(self):
    bone_data = self.model.bones
    bone_names = self.bone_names
    armature = bpy.context.object.data
    tail_var = self.settings.format_bone_scale

    for b, name in zip(bone_data, bone_names):
        bone = armature.edit_bones.new(name)

        if b.parent != 65535:
            bone.parent = armature.edit_bones[b.parent]
        bone.tail = bone.head + mathutils.Vector((0, 1, 0))
        bone.matrix = b.matrix
        bone.length = tail_var


def make_bones_pretty(self):
    bone_data = self.model.bones
    bone_names = self.bone_names
    max_len = self.settings.max_bone_length
    armature = bpy.context.object.data
    tail_var = self.settings.format_bone_scale

    for b, name in zip(bone_data, bone_names):
        bone = armature.edit_bones.new(name)

        if b.parent != 65535:
            bone.parent = armature.edit_bones[b.parent]
        bone.tail = b.position  # they store the position relative to parent bone
        # it's not the correct usage but its aesthetically nice for most bones
        bone.transform(b.matrix)

        if not 0.0001 < bone.length < tail_var * max_len:  # blender rounds bone len
            bone.length = tail_var  # 0 = bone isn't made, too big = can't see anything in blender
        bone.roll = 0

    if self.settings.all_bones_one_length:
        for bone in armature.edit_bones:
            bone.length = tail_var


def make_armature(self):
    bpy.ops.object.add(type="ARMATURE", enter_editmode=True)
    obj = bpy.context.object
    obj.name = obj.data.name = self.model_name  # Object name, Armature name
    obj.rotation_euler[0] = 1.5708  # rotate 90 deg to stand up
    self.armature = obj


def hide_null_bones():  # a subset of (if not all) unweighted bones
    bone_groups = bpy.context.object.pose.bone_groups
    if "Null_Bone_Group" in bone_groups:
        bone_groups.active = bone_groups["Null_Bone_Group"]
        bpy.ops.pose.group_select()
        bpy.ops.pose.hide(unselected=False)


def make_bone_groups(self):
    bone_data = self.model.bones
    group_names = self.group_names
    pose = bpy.context.object.pose

    if self.model_name_strip + "_Bone_Group_" + "65535" in group_names:  # null
        null_group = pose.bone_groups.new(name="Null_Bone_Group")
        null_group.color_set = "THEME08"  # makes it visibly different

    for i in range(self.model.info.bone_count):
        bone = pose.bones[i]
        if bone_data[i].group != 65535:
            bone.bone_group = pose.bone_groups.new(name=group_names[i])
        else:
            # noinspection PyUnboundLocalVariable
            bone.bone_group = null_group
