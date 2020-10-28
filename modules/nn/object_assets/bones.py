from dataclasses import dataclass
from mathutils import Matrix

from ...util import *


class Read:
    def __init__(self, f: BinaryIO, bone_count: int):
        self.f = f
        self.bone_count = bone_count

    @dataclass
    class Bone:
        group: int
        parent: int
        relative: tuple
        scale: tuple
        position: Matrix

    def le_full(self):
        f = self.f
        bone_data = []
        for _ in range(self.bone_count):
            f.seek(4, 1)  # skip flags
            group, parent = read_multi_shorts(f, 2)
            f.seek(4, 1)  # skip child and sibling (4)
            rel = read_float_tuple(f, 3)
            f.seek(12, 1)  # some shorts (2*6)
            scale = read_float_tuple(f, 3)
            pos = read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4)
            f.seek(32, 1)  # skip some more
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).transposed().inverted_safe()))
        return bone_data

    def be_full(self):
        f = self.f
        bone_data = []
        for _ in range(self.bone_count):
            f.seek(4, 1)  # skip flags
            group, parent = read_multi_shorts(f, 2, ">")
            f.seek(4, 1)  # skip child and sibling (4)
            rel = read_float_tuple(f, 3, ">")
            f.seek(12, 1)  # some shorts (2*6)
            scale = read_float_tuple(f, 3, ">")
            pos = (read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                   read_float_tuple(f, 4, ">"))
            f.seek(32, 1)  # skip some more
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).transposed().inverted_safe()))
        return bone_data

    def be_semi(self):
        f = self.f
        bone_data = []
        for _ in range(self.bone_count):
            f.seek(4, 1)  # skip flags
            group, parent = read_multi_shorts(f, 2, ">")
            f.seek(4, 1)  # skip child and sibling (4)
            rel = read_float_tuple(f, 3, ">")
            f.seek(12, 1)  # some shorts (2*6)
            scale = read_float_tuple(f, 3, ">")
            pos = read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), (0, 0, 0, 1)
            f.seek(32, 1)  # skip some more
            bone_data.append(self.Bone(group, parent, rel, scale, Matrix(pos).inverted_safe()))
        return bone_data
