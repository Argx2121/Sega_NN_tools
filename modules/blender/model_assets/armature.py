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

        if b.flags.inherit_pos_only:
            bone.use_inherit_rotation = False
            bone.inherit_scale = 'NONE'
        elif b.flags.reset_scale_x and b.flags.reset_scale_y and b.flags.reset_scale_z:
            bone.inherit_scale = 'NONE'
        bone.use_local_location = False

        if b.parent != 65535:
            bone.parent = armature.edit_bones[b.parent]

        bone.tail = bone.head + mathutils.Vector((0, 1, 0))
        bone.matrix = b.matrix
        bone.length = tail_var
        if b.flags.ik_1bone_joint1 or b.flags.ik_2bone_joint1 or b.flags.ik_2bone_joint2:
            bone.length = b.length[0]


def make_armature(self):
    bpy.ops.object.add(type="ARMATURE", enter_editmode=True)
    obj = bpy.context.object
    obj.name = obj.data.name = self.model_name  # Object name, Armature name
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


def make_bone_pose(self):
    scales = []  # BLENDER
    round_value = 0.1  # blender..............
    round_number = 1

    test_list = []
    for pose_b, nn_b in zip(bpy.context.object.pose.bones, self.model.bones):
        order = "XYZ"
        if nn_b.flags.zxy:
            order = "ZXY"
        elif nn_b.flags.xzy:
            order = "XZY"
        pose_b.rotation_mode = order
        pose_b.nn_euler_rotation = order
        pose_b.nn_user_int = nn_b.user
        rot = nn_b.rotation
        rot = [math.radians(r) for r in rot]
        pose_b.nn_euler_values = rot
        if [round(a, 0) for a in nn_b.scale] == [-1, -1, -1]:
            nn_b.scale = [1, 1, 1]
        pose_b.nn_scale_values = nn_b.scale
        pose_b.nn_position_values = nn_b.position

        if self.settings.pose:
            pos = mathutils.Vector(nn_b.position)
            rot = mathutils.Euler(rot, order)
            sca = mathutils.Vector(nn_b.scale)

            nnm = nn_b.matrix
            if pose_b.parent:
                nnm = self.model.bones[nn_b.parent].matrix.inverted() @ nnm

            np, nr, ns = nnm.decompose()
            sca_og = sca
            sca = Vector((sca.x / ns.x, sca.y / ns.y, sca.z / ns.z))
            new_v = Vector((sca_og.x / sca.x, sca_og.y / sca.y, sca_og.z / sca.z))
            scales.append(new_v)
            if pose_b.parent:
                pl, pr, ps = pose_b.parent.matrix.decompose()
                # are the blender devs insane why do they remove the scale from the edit bone matrix
                if nn_b.flags.reset_scale_x:
                    ps.x = 1
                if nn_b.flags.reset_scale_y:
                    ps.y = 1
                if nn_b.flags.reset_scale_z:
                    ps.z = 1
                if nn_b.flags.inherit_pos_only:
                    pr = None
                    ps = None
                pos = scales[nn_b.parent] * pos
                a = mathutils.Matrix.LocRotScale(pos, rot, sca)
                parent_mat = mathutils.Matrix.LocRotScale(pl, pr, ps)
                pose_b.matrix = parent_mat @ a
                testp1 = [0 if -round_value < a < round_value else round(a, round_number) for a in pose_b.nn_position_values]
                testp2 = [0 if -round_value < a < round_value else round(a, round_number) for a in np]
                testr1 = [0 if -round_value < a < round_value else round(a, round_number) for a in rot.to_quaternion().to_euler()]
                testr2 = [0 if -round_value < a < round_value else round(a, round_number) for a in nr.to_euler()]
                tests1 = [0 if -round_value < a < round_value else round(a, round_number) for a in pose_b.nn_scale_values]
                tests2 = [0 if -round_value < a < round_value else round(a, round_number) for a in ns]
                if (testp1 == testp2) and (testr1 == testr2) and (tests1 == tests2):
                    test_list.append(False)
                else:
                    test_list.append(True)

            else:
                a = mathutils.Matrix.LocRotScale(pos, rot, sca)
                pose_b.matrix = a
                test_list.append(False)  # you wouldnt pose a root node.............. right........

        if nn_b.flags.reset_scale_x:
            pose_b.nn_reset_scale_x = True
        if nn_b.flags.reset_scale_y:
            pose_b.nn_reset_scale_y = True
        if nn_b.flags.reset_scale_z:
            pose_b.nn_reset_scale_z = True
        if nn_b.flags.inherit_pos_only:
            pose_b.nn_inherit_pos_only = True

        if nn_b.flags.ik_effector:
            pose_b.nn_ik_effector = True
        if nn_b.flags.ik_minus_z:
            pose_b.nn_ik_minus_z = True
        if nn_b.flags.ik_1bone_joint1:
            pose_b.nn_ik_1bone_joint1 = True
        if nn_b.flags.ik_2bone_joint1:
            pose_b.nn_ik_2bone_joint1 = True
        if nn_b.flags.ik_2bone_joint2:
            pose_b.nn_ik_2bone_joint2 = True
        if nn_b.flags.ik_1bone_root:
            pose_b.nn_ik_1bone_root = True
        if nn_b.flags.ik_2bone_root:
            pose_b.nn_ik_2bone_root = True
        if nn_b.flags.xsiik:
            pose_b.nn_xsiik = True
    if set(test_list) == {False}:
        self.settings.pose = False


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
    user: int
    length: tuple


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
    mesh_vis_bone = [[] for _ in self.mesh_list]  # yeah

    if self.settings.over_bone:
        for ind, bone in enumerate(obj.pose.bones):
            if bone.nn_mesh_count:
                for i in range(bone.nn_mesh_count):
                    bone_used_2[ind].append(bone.nn_meshes[i].mesh)
                    mesh_vis_bone[self.mesh_list.index(bone.nn_meshes[i].mesh)] = ind
    else:
        for ind, child in enumerate(self.mesh_list):
            vert_names = [a.name for a in child.vertex_groups]
            if len(vert_names) == 1:  # change this when you move to using bmesh
                bone_used_2[bone_names.index(vert_names[0])].append(child)
                mesh_vis_bone[ind] = bone_names.index(vert_names[0])
            else:  # :thumbs_up:
                bone_used_2[-1].append(child)
                mesh_vis_bone[ind] = len(bone_used_2) - 1

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

    pose_data = []
    bpy.context.active_object.select_set(False)
    self.armature.hide_set(False)
    self.armature.select_set(True)
    bpy.context.view_layer.objects.active = self.armature
    bpy.ops.object.mode_set(mode="POSE")
    for pose_b in self.armature.pose.bones:
        if self.settings.over_scene:
            euler = pose_b.nn_euler_rotation
        else:
            euler = pose_b.rotation_mode
            if euler not in {'XYZ', 'XZY', 'ZXY'}:
                euler = 'XZY'
        flags = {"XYZ": 0, "XZY": 256, "ZXY": 1024}[euler]
        if pose_b.nn_inherit_pos_only:
            flags |= 1 << 12
        if pose_b.nn_reset_scale_x:
            flags |= 1 << 18
        if pose_b.nn_reset_scale_y:
            flags |= 1 << 19
        if pose_b.nn_reset_scale_z:
            flags |= 1 << 20
        if pose_b.nn_ik_effector:
            flags |= 1 << 13
        if pose_b.nn_ik_1bone_joint1:
            flags |= 1 << 14
        if pose_b.nn_ik_2bone_joint1:
            flags |= 1 << 15
        if pose_b.nn_ik_2bone_joint2:
            flags |= 1 << 16
        if pose_b.nn_ik_minus_z:
            flags |= 1 << 17
        if pose_b.nn_ik_1bone_root:
            flags |= 1 << 25
        if pose_b.nn_ik_2bone_root:
            flags |= 1 << 26
        if pose_b.nn_xsiik:
            flags |= 1 << 27
        pose_data.append((flags, pose_b.nn_user_int, euler))
    bpy.ops.object.mode_set(mode="OBJECT")

    bone_list = []
    round_value = 0.0000001

    for bone, mesh_bone, [flags, user, euler] in zip(arma.bones, bone_used_2, pose_data):
        center = (0, 0, 0)
        radius = 0
        length = (0, 0, 0)
        if bone.inherit_scale == 'NONE' and not bone.use_inherit_rotation:
            flags |= 1 << 12
        elif bone.inherit_scale == 'NONE':
            flags |= 1 << 18
            flags |= 1 << 19
            flags |= 1 << 20

        if mesh_bone:
            flags |= 1 << 21
            flags |= 1 << 22  # sorry all spheres
            co_ords = []
            mesh_bone = list(set(mesh_bone))
            for mesh_used in mesh_bone:
                pos = [0, 0, 0] * len(mesh_used.data.vertices)
                mesh_used.data.vertices.foreach_get("co", pos)
                co_ords += pos

            co_ords = [bone.matrix_local.inverted() @ mathutils.Vector(co_ords[i:i + 3]) for i in
                       range(0, len(co_ords), 3)]

            co_x = [i[0] for i in co_ords]
            co_y = [i[1] for i in co_ords]
            co_z = [i[2] for i in co_ords]

            max_x, min_x = max(co_x), min(co_x)
            max_y, min_y = max(co_y), min(co_y)
            max_z, min_z = max(co_z), min(co_z)

            center_x = (max_x + min_x) / 2
            center_y = (max_y + min_y) / 2
            center_z = (max_z + min_z) / 2
            center = center_x, center_y, center_z

            radius_list = [math.sqrt(((a[0] - center_x) ** 2 + (a[1] - center_y) ** 2 + (a[2] - center_z) ** 2)) for a
                           in co_ords]
            radius = max(radius_list)
            length = (mathutils.Vector((max_x, max_y, max_z)) - mathutils.Vector(
                (center_x, center_y, center_z))).to_tuple()

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

        child = parent @ mathutils.Matrix(bone.matrix_local)
        translation, rotation, scale = Matrix(child).decompose()
        rotation = rotation.to_euler(euler)

        # yeah we have to convert it to degrees so we can convert it to radians later lol
        rotation.x = math.degrees(rotation.x)
        rotation.y = math.degrees(rotation.y)
        rotation.z = math.degrees(rotation.z)
        # noinspection PyTypeChecker
        rot = tuple(rotation)
        pos = tuple(translation)
        sca = tuple(scale)
        if -round_value < translation.length < round_value:
            flags |= 1 << 0
        if -round_value < rot[0] < round_value and -round_value < rot[1] < round_value and -round_value < rot[
            2] < round_value:
            flags |= 1 << 1
        if -round_value < sca[0] - 1 < round_value and -round_value < sca[1] - 1 < round_value and -round_value < sca[
            2] - 1 < round_value:
            flags |= 1 << 2
        if flags >> 0 & 1 and flags >> 1 & 1 and flags >> 1 & 2:
            flags |= 1 << 3
        if not flags >> 0 & 1 and flags >> 1 & 1 and flags >> 1 & 2:
            flags |= 1 << 6
        if b_mat.to_3x3().is_orthogonal:
            flags |= 1 << 7

        # noinspection PyTypeChecker
        bone_list.append(Bone(
            flags, bone.name, b_mat, pos, rot, sca, par, used, chi, sib, center, radius, user, length))

    self.armature.location = original_position
    return bone_list, bone_depth, used_bones, mesh_vis_bone


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
