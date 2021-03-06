from dataclasses import dataclass

from ...util import *


class Read:
    def __init__(self, f: BinaryIO, post_nxif: int, sets_count: int, data_offset: list, data_count: list):
        self.f = f
        self.post_nxif = post_nxif
        self.sets_count = sets_count
        self.data_offset = data_offset
        self.data_count = data_count

    @dataclass
    class BuildMesh:
        bounds_position: tuple
        bounds_scale: float
        bone_visibility: int  # the animation set up means they can hide a bone (and the meshes with that bone listed)
        bone: int  # keep in mind FF FF bones arent included in the list - they're null !!
        material: int
        vertex: int
        face: int

    def le_10(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):  # usually about two of these
            f.seek(self.data_offset[var] + self.post_nxif)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 6)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_12(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.post_nxif)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 8)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def le_9(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.post_nxif)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 5)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def be_10(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):  # usually about two of these
            f.seek(self.data_offset[var] + self.post_nxif)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 6, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh

    def be_12(self):
        f = self.f
        build_mesh = []
        for var in range(self.sets_count):  # usually about two of these
            f.seek(self.data_offset[var] + self.post_nxif)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 8, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4]))
        return build_mesh
