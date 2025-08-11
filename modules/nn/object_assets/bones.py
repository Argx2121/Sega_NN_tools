from dataclasses import dataclass
from mathutils import Matrix

from enum import Flag
from ...util import *


def bone_flags(bone_flag):
    class BoneFlags(Flag):
        init_unit_pos = bone_flag >> 0 & 1  # init matrix doesnt have a not unit position (aka pos = 0, 0, 0)
        init_unit_rot = bone_flag >> 1 & 1  # init matrix doesnt have a not unit rotation
        init_unit_scale = bone_flag >> 2 & 1  # init matrix doesnt have a not unit scale
        init_unit_matrix = bone_flag >> 3 & 1  # init matrix is all unit components
        # hide = bone_flag >> 4 & 1  # im not adding this bro no ones gonna use the hide bone flag itll be in anims
        # hide_recursive = bone_flag >> 5 & 1  # why?
        init_pos = bone_flag >> 6 & 1  # init matrix is all unit components but position
        init_ortho = bone_flag >> 7 & 1  # inits transposed form = inits inverted form

        xyz = (bone_flag >> 8 & 15) == 0
        xzy = (bone_flag >> 8 & 15) == 1
        zxy = (bone_flag >> 8 & 15) == 4

        inherit_pos_only = bone_flag >> 12 & 1

        ik_effector = bone_flag >> 13 & 1
        ik_1bone_joint1 = bone_flag >> 14 & 1
        ik_2bone_joint1 = bone_flag >> 15 & 1
        ik_2bone_joint2 = bone_flag >> 16 & 1
        ik_minus_z = bone_flag >> 17 & 1  # ???????

        reset_scale_x = bone_flag >> 18 & 1
        reset_scale_y = bone_flag >> 19 & 1
        reset_scale_z = bone_flag >> 20 & 1

        bounding_box = bone_flag >> 21 & 1
        bounding_box_sphere = bone_flag >> 22 & 1
        bounding_box_dom_x = bone_flag >> 23 & 3 == 1
        bounding_box_dom_y = bone_flag >> 23 & 3 == 2
        bounding_box_dom_z = bone_flag >> 23 & 3 == 3

        ik_1bone_root = bone_flag >> 25 & 1
        ik_2bone_root = bone_flag >> 26 & 1
        xsiik = bone_flag >> 27 & 1
    return BoneFlags


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "bone_count"
    ]

    def __init__(self, var, bone_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.bone_count = bone_count

    @dataclass
    class Bone:
        __slots__ = [
            "flags", "group", "parent", "child", "sibling",
            "position", "rotation", "scale", "matrix", "center", "radius", "user", "length"
        ]
        flags: int
        group: int
        parent: int
        child: int
        sibling: int
        position: tuple
        rotation: tuple
        scale: tuple
        matrix: Matrix
        center: tuple
        radius: float
        user: int
        length: tuple

    def le_full(self):
        f = self.f
        bone_data = [
            self.Bone(
                bone_flags(read_int(f)), read_short(f), read_short(f), read_short(f), read_short(f),
                read_float_tuple(f, 3), read_int_bam_tuple(f, 3), read_float_tuple(f, 3),
                Matrix((read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                        read_float_tuple(f, 4))).transposed().inverted_safe(),
                read_float_tuple(f, 3), read_float(f), read_int(f), read_float_tuple(f, 3),
            )
            for _ in range(self.bone_count)]
        return bone_data

    def le_full_s4e2(self):
        f = self.f
        bone_data = []
        for _ in range(self.bone_count):
            flags = bone_flags(read_int(f))
            group, parent, child, sibling = read_short_tuple(f, 4)
            f.seek(4, 1)
            pos = read_float_tuple(f, 3)
            f.seek(4, 1)
            rot = read_int_bam_tuple(f, 3)
            f.seek(4, 1)
            scale = read_float_tuple(f, 3)
            f.seek(4, 1)
            mat = (read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                   read_float_tuple(f, 4))
            cen = read_float_tuple(f, 3)
            f.seek(4, 1)
            rad = read_float(f)
            unk = read_int(f)
            f.seek(12, 1)
            dim = read_float_tuple(f, 3)
            bone_data.append(self.Bone(
                flags, group, parent, child, sibling, pos, rot, scale, Matrix(mat).transposed().inverted_safe(),
                cen, rad, unk, dim,
            ))
        return bone_data

    def be_full(self):
        f = self.f
        bone_data = [
            self.Bone(
                bone_flags(read_int(f, ">")), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"),
                read_float_tuple(f, 3, ">"), read_int_bam_tuple(f, 3, ">"), read_float_tuple(f, 3, ">"),
                Matrix((read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                        read_float_tuple(f, 4, ">"))).transposed().inverted_safe(),
                read_float_tuple(f, 3, ">"), read_float(f, ">"), read_int(f, ">"), read_float_tuple(f, 3, ">"),
            )
            for _ in range(self.bone_count)]
        return bone_data

    def le_semi(self):
        f = self.f
        bone_data = [
            self.Bone(
                bone_flags(read_int(f)), read_short(f), read_short(f), read_short(f), read_short(f),
                read_float_tuple(f, 3), read_int_bam_tuple(f, 3), read_float_tuple(f, 3),
                Matrix((read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                        (0, 0, 0, 1))).inverted_safe(),
                read_float_tuple(f, 3), read_float(f), read_int(f), read_float_tuple(f, 3),
            )
            for _ in range(self.bone_count)]
        return bone_data

    def be_semi(self):
        f = self.f
        bone_data = [
            self.Bone(
                bone_flags(read_int(f, ">")), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"),
                read_float_tuple(f, 3, ">"), read_int_bam_tuple(f, 3, ">"), read_float_tuple(f, 3, ">"),
                Matrix((read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                        (0, 0, 0, 1))).inverted_safe(),
                read_float_tuple(f, 3, ">"), read_float(f, ">"), read_int(f, ">"), read_float_tuple(f, 3, ">"),
            )
            for _ in range(self.bone_count)]
        return bone_data


class Write:
    __slots__ = ["f", "bones"]

    def __init__(self, f, bones):
        self.f = f
        self.bones = bones

    def be_semi(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            f.write(pack(">I", b.flags))
            f.write(pack(">h", b.used))
            f.write(pack(">h", b.parent))
            f.write(pack(">h", b.child))
            f.write(pack(">h", b.sibling))
            for var in b.position:
                write_float(f, ">", var)
            for var in b.rotation:
                f.write(pack(">i", round(var * 182.04444)))
            for var in b.scale:
                write_float(f, ">", var)
            bmat = b.matrix
            for var in bmat[0]:
                write_float(f, ">", var)
            for var in bmat[1]:
                write_float(f, ">", var)
            for var in bmat[2]:
                write_float(f, ">", var)

            for var in b.center:
                write_float(f, ">", var)
            write_float(f, ">", b.radius)
            f.write(pack(">i", b.user))
            for var in b.length:
                write_float(f, ">", var)
        return start

    def le_semi(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            b.flags.reverse()
            f.write(pack("<I", b.flags))
            f.write(pack("<h", b.used))
            f.write(pack("<h", b.parent))
            f.write(pack("<h", b.child))
            f.write(pack("<h", b.sibling))
            for var in b.position:
                write_float(f, "<", var)
            for var in b.rotation:
                f.write(pack("<i", round(var * 182.04444)))
            for var in b.scale:
                write_float(f, "<", var)
            bmat = b.matrix
            for var in bmat[0]:
                write_float(f, "<", var)
            for var in bmat[1]:
                write_float(f, "<", var)
            for var in bmat[2]:
                write_float(f, "<", var)

            for var in b.center:
                write_float(f, "<", var)
            write_float(f, "<", b.radius)
            f.write(pack("<i", b.user))
            for var in b.length:
                write_float(f, "<", var)
        return start

    def be_full(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            f.write(pack(">I", b.flags))
            f.write(pack(">h", b.used))
            f.write(pack(">h", b.parent))
            f.write(pack(">h", b.child))
            f.write(pack(">h", b.sibling))
            for var in b.position:
                write_float(f, ">", var)
            for var in b.rotation:
                f.write(pack(">i", round(var * 182.04444)))
            for var in b.scale:
                write_float(f, ">", var)
            bmat = b.matrix.transposed()
            for var in bmat[0]:
                write_float(f, ">", var)
            for var in bmat[1]:
                write_float(f, ">", var)
            for var in bmat[2]:
                write_float(f, ">", var)
            for var in bmat[3]:
                write_float(f, ">", var)

            for var in b.center:
                write_float(f, ">", var)
            write_float(f, ">", b.radius)
            f.write(pack(">i", b.user))
            for var in b.length:
                write_float(f, ">", var)
        return start

    def le_full(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            f.write(pack("<I", b.flags))
            f.write(pack("<h", b.used))
            f.write(pack("<h", b.parent))
            f.write(pack("<h", b.child))
            f.write(pack("<h", b.sibling))
            for var in b.position:
                write_float(f, "<", var)
            for var in b.rotation:
                f.write(pack("<i", round(var * 182.04444)))
            for var in b.scale:
                write_float(f, "<", var)
            bmat = b.matrix.transposed()
            for var in bmat[0]:
                write_float(f, "<", var)
            for var in bmat[1]:
                write_float(f, "<", var)
            for var in bmat[2]:
                write_float(f, "<", var)
            for var in bmat[3]:
                write_float(f, "<", var)

            for var in b.center:
                write_float(f, "<", var)
            write_float(f, "<", b.radius)
            f.write(pack("<i", b.user))
            for var in b.length:
                write_float(f, "<", var)
        return start
