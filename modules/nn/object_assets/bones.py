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


class Write:
    __slots__ = ["f", "bones"]

    def __init__(self, f, bones):
        self.f = f
        self.bones = bones

    def be_semi(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            for var in b.flags:
                f.write(pack(">B", var))
            f.write(pack(">h", b.used))
            f.write(pack(">h", b.parent))
            f.write(pack(">h", b.child))
            f.write(pack(">h", b.sibling))
            for var in b.position:
                write_float(f, ">", var)
            for var in b.rotation:
                f.write(pack(">i", round(var / (180 / 32767))))
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
            write_float(f, ">", b.unknown)
            for var in b.length:
                write_float(f, ">", var)
        return start

    def le_semi(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            b.flags.reverse()
            for var in b.flags:
                f.write(pack("<B", var))
            f.write(pack("<h", b.used))
            f.write(pack("<h", b.parent))
            f.write(pack("<h", b.child))
            f.write(pack("<h", b.sibling))
            for var in b.position:
                write_float(f, "<", var)
            for var in b.rotation:
                f.write(pack("<i", round(var / (180 / 32767))))
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
            write_float(f, "<", b.unknown)
            for var in b.length:
                write_float(f, "<", var)
        return start

    def be_full(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            for var in b.flags:
                f.write(pack(">B", var))
            f.write(pack(">h", b.used))
            f.write(pack(">h", b.parent))
            f.write(pack(">h", b.child))
            f.write(pack(">h", b.sibling))
            for var in b.position:
                write_float(f, ">", var)
            for var in b.rotation:
                f.write(pack(">i", round(var / (180 / 32767))))
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
            write_float(f, ">", b.unknown)
            for var in b.length:
                write_float(f, ">", var)
        return start

    def le_full(self):
        f = self.f
        start = f.tell()
        for b in self.bones:
            # b.flags[2] = 0  # todo needed for zno
            b.flags.reverse()
            for var in b.flags:
                f.write(pack("<B", var))
            f.write(pack("<h", b.used))
            f.write(pack("<h", b.parent))
            f.write(pack("<h", b.child))
            f.write(pack("<h", b.sibling))
            for var in b.position:
                write_float(f, "<", var)
            for var in b.rotation:
                f.write(pack("<i", round(var / (180 / 32767))))
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
            write_float(f, "<", b.unknown)
            for var in b.length:
                write_float(f, "<", var)
        return start
