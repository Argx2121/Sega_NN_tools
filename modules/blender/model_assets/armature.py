import math

import bpy
from dataclasses import dataclass

import mathutils
from bpy.types import Armature, Object
from math import *
from mathutils import *


def make_bones_accurate(self):
    bone_data = self.model.bones
    bone_names = self.bone_names
    armature: Armature = bpy.context.object.data
    tail_var = self.settings.format_bone_scale

    for i, b in enumerate(bone_data):
        bone = armature.edit_bones.new(bone_names[i])

        if b.parent != 65535:
            bone.parent = armature.edit_bones[b.parent]
        bone.tail = bone.head + mathutils.Vector((0, 1, 0))
        bone.matrix = b.matrix
        bone.length = tail_var


def make_bones_pretty(self):
    bone_data = self.model.bones
    bone_names = self.bone_names
    max_len = self.settings.max_bone_length
    armature: Armature = bpy.context.object.data
    tail_var = self.settings.format_bone_scale

    for i, b in enumerate(bone_data):
        bone = armature.edit_bones.new(bone_names[i])

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
    obj.rotation_euler[0] = 1.5707963267949  # rotate 90 deg to stand up
    self.armature = obj


def hide_null_bones():  # a subset of (if not all) unweighted bones
    arma: Armature = bpy.context.object.data
    if "Null_Bones" in arma.collections:
        arma.collections["Null_Bones"].is_visible = False


def make_bone_collections(self):
    bone_data = self.model.bones
    group_names = self.group_names
    arma: Armature = bpy.context.object.data

    if self.model_name_strip + "_Bone_Collection_" + "65535" in group_names:  # null
        arma.collections.new("Null_Bones")

    for i in range(self.model.info.bone_count):
        bone = arma.bones[i]
        if bone_data[i].group == 65535:
            arma.collections["Null_Bones"].assign(bone)
            bone.color.palette = "THEME08"  # makes it visibly different


def make_bone_constraints(self):
    for pose_b, nn_b in zip(bpy.context.object.pose.bones, self.model.bones):
        if nn_b.flags & 1835008:
            constraint = pose_b.constraints.new(type='LIMIT_ROTATION')
            if nn_b.flags & 256:
                constraint.use_limit_x = True
                constraint.use_limit_z = True
            elif nn_b.flags & 512:
                constraint.use_limit_y = True
                constraint.use_limit_z = True
            else:
                constraint.use_limit_x = True
                constraint.use_limit_y = True
            constraint.euler_order = 'XZY'
            constraint.owner_space = 'LOCAL'


@dataclass
class Bone:
    flags: list
    name: str
    matrix: mathutils.Matrix
    position: list
    rotation: list
    scale: list
    parent: int
    used: int
    child: int
    sibling: int
    center: tuple
    radius: float
    unknown: float
    length: tuple
    lock: bool


# noinspection PyArgumentList
def to_euler_angles_zyx(q: Quaternion):
    """Converts the values from Quaternion into Euler angles.

    Parameters
    ----------
    q : Quaternion
        The Quaternion to convert.
    """
    # Unit test from: http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/index.htm
    sqw = q.w * q.w
    sqx = q.x * q.x
    sqy = q.y * q.y
    sqz = q.z * q.z

    test = q.x * q.y + q.z * q.w
    # Unit vector to correct for non-normalised quaternions. Just in case.
    unit = sqx + sqy + sqz + sqw

    # Accounting for 'singularities', or rather, Gimbal Lock.
    # Honestly I'm unsure about why this has to be done, and why it only has to be done when all the signs are the same
    #  but that's nn for you
    if test > 0.4999999 * unit and (copysign(1, q.x) == copysign(1, q.y) == copysign(1, q.z) == copysign(1, q.w)):
        rotation = (q.inverted() @ Euler((0, -radians(180), 0)).to_quaternion()).inverted()
        rot = rotation.to_euler('XZY')
        return Vector((rot.x, rot.y, rot.z)), True
    if test < -0.4999999 * unit and (copysign(1, q.x) == copysign(1, q.y) == copysign(1, q.z) == copysign(1, q.w)):
        rotation = (q.inverted() @ Euler((0, -radians(180), 0)).to_quaternion()).inverted()
        rot = rotation.to_euler('XZY')
        return Vector((rot.x, rot.y, rot.z)), True

    rot = q.to_euler('XZY')

    return Vector((rot.x, rot.y, rot.z)), False


def get_bones(self):
    obj: Object = self.armature
    arma: Armature = obj.data
    original_position = self.armature.location[::]
    self.armature.location = 0, 0, 0
    bone_depth = 1

    bone_names = []
    for bone in arma.bones:
        bone_names.append(bone.name)
        if bone.parent and not bone.children:
            if bone_depth < len(bone.parent_recursive) + 1:
                bone_depth = len(bone.parent_recursive) + 1

    bone_used_2 = [[] for _ in arma.bones]  # the sequel: bones 2

    for child in self.mesh_list:
        vert_names = [a.name for a in child.vertex_groups]
        if len(vert_names) == 1:  # change this when you move to using bmesh
            bone_used_2[bone_names.index(vert_names[0])].append(child)
        else:  # :thumbs_up:
            bone_used_2[-1].append(child)

    used_bones = []
    if self.settings.riders_default:
        used_bones = [bone_names[2]]

    for obj_m in self.mesh_list:
        mesh = obj_m.data
        b_names = [a.name for a in obj_m.vertex_groups]

        for vert in mesh.vertices:
            for group in vert.groups[::]:
                if group.weight > 0:
                    used_bones.append(b_names[group.group])
        used_bones = list(set(used_bones))
    used_bones = [b for b in bone_names if b in used_bones]

    bpy.context.active_object.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    pose_data = []
    bpy.ops.object.mode_set(mode="POSE")
    for pose_b in self.armature.pose.bones:
        pose_var = False
        if "LIMIT_ROTATION" in [a.type for a in pose_b.constraints]:
            pose_var = True
        pose_data.append(pose_var)
    bpy.ops.object.mode_set(mode="OBJECT")

    bone_list = []

    for bone, mesh_bone, pose_b in zip(arma.bones, bone_used_2, pose_data):
        flags = [0, 0, 0, 0]

        center = (0, 0, 0)
        radius = 0
        unknown = 0
        length = (0, 0, 0)
        if mesh_bone:
            co_ords = []
            mesh_bone = list(set(mesh_bone))
            for mesh_used in mesh_bone:
                pos = [0, 0, 0] * len(mesh_used.data.vertices)
                mesh_used.data.vertices.foreach_get("co", pos)
                co_ords += pos

            co_x = [co_ords[i] for i in range(0, len(co_ords), 3)]
            co_y = [co_ords[i + 1] for i in range(0, len(co_ords), 3)]
            co_z = [co_ords[i + 2] for i in range(0, len(co_ords), 3)]

            max_x, min_x = max(co_x), min(co_x)
            max_y, min_y = max(co_y), min(co_y)
            max_z, min_z = max(co_z), min(co_z)

            bone_head = bone.head_local

            center_x = (max_x + min_x) / 2
            center_y = (max_y + min_y) / 2
            center_z = (max_z + min_z) / 2

            center_x1 = (max_x + min_x) / 2 - bone_head[0]
            center_y1 = (max_y + min_y) / 2 - bone_head[1]
            center_z1 = (max_z + min_z) / 2 - bone_head[2]

            center = center_x1, center_y1, center_z1

            pos = [tuple(co_ords[i:i + 3]) for i in range(0, len(co_ords), 3)]

            radius_list = [math.sqrt(((a[0] - center_x) ** 2 + (a[1] - center_y) ** 2 + (a[2] - center_z) ** 2)) for a
                           in pos]
            radius = max(radius_list)
            length = (max_x - center_x, max_y - center_y, max_z - center_z)

        used = -1
        if bone.name in used_bones:
            used = used_bones.index(bone.name)

        b_mat = mathutils.Matrix(bone.matrix_local).inverted()
        par = -1
        sib = -1
        chi = -1
        parent = Matrix().inverted()
        if bone.parent:
            parent = mathutils.Matrix(bone.parent.matrix_local).inverted()
            par = bone.parent.name
            par = bone_names.index(par)
            children_names = [ch.name for ch in bone.parent.children]
            next_index = children_names.index(bone.name) + 1
            if len(children_names) > next_index:
                sib = bone_names.index(children_names[next_index])

        if bone.children:
            chi = bone.children[0].name
            chi = bone_names.index(chi)

        # Special thanks to Sewer56 for this code

        # Remove Parent
        # Parent * Child = Result
        # AB = C
        # (A^-1)AB = A^-1(C)
        # IB = A^-1(C)
        # B = A^-1(C)

        # parent = mathutils.Matrix(bone.parent.matrix_local).inverted()
        child = parent @ mathutils.Matrix(bone.matrix_local) #.inverted()
        #child = child.inverted()

        # Apply properties
        translation, rotation, sca = Matrix(child).decompose()
        rotation, lock = to_euler_angles_zyx(rotation)

        print(bone.name, rotation, lock)

        if bone.parent:
            if bone_list[par].lock:
                translation, q, sca = Matrix(child).decompose()
                rotation = (q.inverted() @ Euler((-radians(180), 0, 0)).to_quaternion()).inverted()
                translation.rotate(Euler((-radians(180), 0, 0)))
                rotation, lock = to_euler_angles_zyx(rotation)

        # Shouldn't happen, but just in case.
        if math.isnan(rotation.x):
            rotation.x = 0

        if math.isnan(rotation.y):
            rotation.y = 0

        if math.isnan(rotation.z):
            rotation.z = 0

        # Convert to BAMS
        rotation.x = math.degrees(rotation.x)
        rotation.y = math.degrees(rotation.y)
        rotation.z = math.degrees(rotation.z)
        # noinspection PyTypeChecker
        rot = tuple(rotation)
        pos = tuple(translation)
        sca = tuple(sca)

        if radius:
            flags[1] = flags[1] | 32
        # seems like inherit some kinda scale
        # not sure what would use this but might need custom props if it wants to be preserved
        # or a custom tab that has a list of all of them
        for a in sca:
            if a != 1.0:
                flags[1] = flags[1] | 64
        if pose_b:  # Never seen them both set at once
            flags[1] = 28
        if self.format in {"SonicRiders_G", "SonicRiders_X"}:
            flags[2] = 1
        # guesses
        flags[3] = flags[3] | 4
        flags[3] = flags[3] | 128

        # noinspection PyTypeChecker
        bone_list.append(Bone(
            flags, bone.name, b_mat, pos, rot, sca, par, used, chi, sib, center, radius, unknown, length, lock))

    self.armature.location = original_position
    return bone_list, bone_depth, used_bones


def get_render_data(mesh_list):
    co_ords = []

    for child in mesh_list:
        child = child.data
        pos = [0, 0, 0] * len(child.vertices)
        child.vertices.foreach_get("co", pos)
        co_ords += pos

    co_x = co_ords[0::3]
    co_y = co_ords[1::3]
    co_z = co_ords[2::3]

    max_x, min_x = max(co_x), min(co_x)
    max_y, min_y = max(co_y), min(co_y)
    max_z, min_z = max(co_z), min(co_z)

    center_x = (max_x + min_x) / 2
    center_y = (max_y + min_y) / 2
    center_z = (max_z + min_z) / 2

    center = center_x, center_y, center_z

    pos = [tuple(co_ords[i:i + 3]) for i in range(0, len(co_ords), 3)]

    radius_list = [math.sqrt(((a[0] - center_x) ** 2 + (a[1] - center_y) ** 2 + (a[2] - center_z) ** 2)) for a
                   in pos]
    radius = max(radius_list)
    return center, radius


