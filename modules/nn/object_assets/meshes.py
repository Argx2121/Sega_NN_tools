from dataclasses import dataclass

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "sets_count", "data_offset", "data_count"
    ]

    def __init__(self, var, sets_count: int, data_offset: list, data_count: list):
        self.f, self.start, self.format_type, self.debug = var
        self.sets_count = sets_count
        self.data_offset = data_offset
        self.data_count = data_count

    @dataclass
    class BuildMesh:
        __slots__ = ["bounds_position", "bounds_scale", "bone_visibility", "bone", "material", "vertex", "face"]
        bounds_position: tuple
        bounds_scale: float
        bone_visibility: int  # the animation set up means they can hide a bone (and the meshes with that bone listed)
        bone: int  # keep in mind FF FF bones arent included in the list - they're null !!
        material: int
        vertex: int
        face: int

    def le_9(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):  # usually about two of these
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 5)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_9_sno(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 5)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[3]))
        return build_mesh

    def be_9(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 5, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_10(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 6)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def be_10(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 6, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_12(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 8)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def be_12(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 8, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_14(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                f.seek(4, 1)
                scale = read_float(f)
                var = read_int_tuple(f, 9)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh
