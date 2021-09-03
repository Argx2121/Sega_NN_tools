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
        __slots__ = ["group", "parent", "relative", "scale", "position"]
        group: int
        parent: int
        relative: tuple
        scale: tuple
        position: Matrix

    def le_full(self):
        f = self.f
        bone_data = []
        f.seek(4, 1)
        if self.format_type == "SonicTheHedgehog4EpisodeII_L":
            for _ in range(self.bone_count):
                group, parent, _, _ = read_short_tuple(f, 4)
                f.seek(4, 1)
                rel = read_float_tuple(f, 3)
                f.seek(20, 1)
                scale = read_float_tuple(f, 3)
                f.seek(4, 1)
                pos = (read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                       read_float_tuple(f, 4))
                f.seek(52, 1)
                bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).transposed().inverted_safe()))
        else:
            for _ in range(self.bone_count):
                group, parent, _, _ = read_short_tuple(f, 4)
                rel = read_float_tuple(f, 3)
                f.seek(12, 1)
                scale = read_float_tuple(f, 3)
                pos = (read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                       read_float_tuple(f, 4))
                f.seek(36, 1)
                bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).transposed().inverted_safe()))
        return bone_data

    def be_full(self):
        f = self.f
        bone_data = []
        f.seek(4, 1)
        for _ in range(self.bone_count):
            group, parent, _, _ = read_short_tuple(f, 4, ">")
            rel = read_float_tuple(f, 3, ">")
            f.seek(12, 1)
            scale = read_float_tuple(f, 3, ">")
            pos = (read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                   read_float_tuple(f, 4, ">"))
            f.seek(36, 1)
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).transposed().inverted_safe()))
        return bone_data

    def le_semi(self):
        f = self.f
        bone_data = []
        f.seek(4, 1)
        for _ in range(self.bone_count):
            group, parent, _, _ = read_short_tuple(f, 4, ">")
            rel = read_float_tuple(f, 3)
            f.seek(12, 1)
            scale = read_float_tuple(f, 3)
            pos = read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4), (0, 0, 0, 1)
            f.seek(36, 1)
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).inverted_safe()))
        return bone_data

    def be_semi(self):
        f = self.f
        bone_data = []
        f.seek(4, 1)
        for _ in range(self.bone_count):
            group, parent, _, _ = read_short_tuple(f, 4, ">")
            rel = read_float_tuple(f, 3, ">")
            f.seek(12, 1)
            scale = read_float_tuple(f, 3, ">")
            pos = read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), (0, 0, 0, 1)
            f.seek(36, 1)
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).inverted_safe()))
        return bone_data
