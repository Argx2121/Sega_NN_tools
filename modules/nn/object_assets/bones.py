from dataclasses import dataclass
from mathutils import Matrix

from ...util import *


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
            "position", "rotation", "scale", "matrix", "center", "radius", "unknown", "length"
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
        unknown: int
        length: tuple

    def le_full(self):
        f = self.f
        bone_data = [
            self.Bone(
                read_int(f), read_short(f), read_short(f), read_short(f), read_short(f),
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
            flags = read_int(f)
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
                read_int(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"),
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
                read_int(f), read_short(f), read_short(f), read_short(f), read_short(f),
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
                read_int(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"), read_short(f, ">"),
                read_float_tuple(f, 3, ">"), read_int_bam_tuple(f, 3, ">"), read_float_tuple(f, 3, ">"),
                Matrix((read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                        (0, 0, 0, 1))).inverted_safe(),
                read_float_tuple(f, 3, ">"), read_float(f, ">"), read_int(f, ">"), read_float_tuple(f, 3, ">"),
            )
            for _ in range(self.bone_count)]
        return bone_data
