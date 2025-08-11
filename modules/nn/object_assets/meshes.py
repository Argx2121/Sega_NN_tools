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
        __slots__ = [
            "bounds_position", "bounds_scale", "bone_visibility", "bone", "material", "vertex", "face", "shader"
        ]
        bounds_position: tuple
        bounds_scale: float
        bone_visibility: int  # the animation set up means they can hide a bone (and the meshes with that bone listed)
        bone: int  # keep in mind FF FF bones aren't included in the list - they're null !!
        material: int
        vertex: int
        face: int
        shader: int
        # how i look at you after you make a shader system and then replace it with user and then
        # replace it with a shader file located elsewhere

    def le_9(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):  # usually about two of these
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 5)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], index))
                index += 1
        return build_mesh

    def le_9_face(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 5)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[3], index))
                index += 1
        return build_mesh

    def be_9(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 5, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], index))
                index += 1
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
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], var[5]))
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
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], var[5]))
        return build_mesh

    def le_12(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                scale = read_float(f)
                var = read_int_tuple(f, 8)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], index))
                index += 1
        return build_mesh

    def be_12(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3, ">")
                scale = read_float(f, ">")
                var = read_int_tuple(f, 8, ">")
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], index))
                index += 1
        return build_mesh

    def le_14(self):
        f = self.f
        index = 0
        build_mesh = []
        for var in range(self.sets_count):
            f.seek(self.data_offset[var] + self.start)
            for _ in range(self.data_count[var]):
                pos = read_float_tuple(f, 3)
                f.seek(4, 1)
                scale = read_float(f)
                var = read_int_tuple(f, 9)
                build_mesh.append(self.BuildMesh(pos, scale, var[0], var[1], var[2], var[3], var[4], index))
                index += 1
        return build_mesh


@dataclass
class TextureData:
    start: int
    end: int
    length: int


class Write:
    __slots__ = [
        "f", "format_type", "meshes", "nof0_offsets", "bone_count", "bone", "model"
    ]

    def __init__(self, f, format_type, meshes, nof0_offsets, bone_count, bone, model):
        self.f = f
        self.format_type = format_type
        self.meshes = meshes
        self.nof0_offsets = nof0_offsets
        self.bone_count = bone_count
        self.bone = bone
        self.model = model

    def _get_textures_be(self, mat_list):
        tex_list = []
        tex_ind = list(self.model.materials.texture_list.keys())
        for mat in mat_list:
            mat = self.model.materials.material_list[mat]
            for texture in mat.texture_list:
                tex_list.append(tex_ind.index(texture.name.image.filepath))
        for t in tex_list:
            write_integer(self.f, ">", t)
        return len(tex_list)

    def _get_textures_le(self, mat_list):
        tex_list = []
        tex_ind = list(self.model.materials.texture_list.keys())
        for mat in mat_list:
            mat = self.model.materials.material_list[mat]
            for texture in mat.texture_list:
                tex_list.append(tex_ind.index(texture.name.image.filepath))
        for t in tex_list:
            write_integer(self.f, "<", t)
        return len(tex_list)

    def be_9(self):
        f = self.f
        meshes = self.meshes
        model_data = self.model
        bone_names = [a.name for a in model_data.bones]

        bone_used = self.bone

        tex_simple_opaque = []   #  1 bone  no transparency  1 1
        tex_complex_opaque = []  # >1 bone  no transparency  1 2
        tex_simple_alpha = []    #  1 bone     transparency  2 1
        tex_complex_alpha = []   # >1 bone     transparency  2 2
        tex_simple_clip = []    #  1 bone      clip          4 1
        tex_complex_clip = []   # >1 bone      clip          4 2

        if meshes.simple_opaque:
            start = f.tell()
            mat_list = []
            for mesh in meshes.simple_opaque:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, ">", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_simple_opaque = TextureData(start, end, length)
        if meshes.complex_opaque:
            start = f.tell()
            mat_list = []
            for mesh in meshes.complex_opaque:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, ">", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_complex_opaque = TextureData(start, end, length)
        if meshes.simple_alpha:
            start = f.tell()
            mat_list = []
            for mesh in meshes.simple_alpha:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, ">", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_simple_alpha = TextureData(start, end, length)
        if meshes.complex_alpha:
            start = f.tell()
            mat_list = []
            for mesh in meshes.complex_alpha:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, ">", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_complex_alpha = TextureData(start, end, length)
        if meshes.simple_clip:
            start = f.tell()
            mat_list = []
            for mesh in meshes.simple_clip:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, ">", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_simple_clip = TextureData(start, end, length)
        if meshes.complex_clip:
            start = f.tell()
            mat_list = []
            for mesh in meshes.complex_clip:
                write_float(f, ">", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, ">", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_be(mat_list)
            tex_complex_clip = TextureData(start, end, length)

        mesh_offset = f.tell()
        if meshes.simple_opaque:
            write_integer(f, ">", 257, len(meshes.simple_opaque))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_simple_opaque.start, tex_simple_opaque.length)
            if tex_simple_opaque.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_simple_opaque.end)
            else:
                write_integer(f, ">", 0)
        if meshes.complex_opaque:
            write_integer(f, ">", 513, len(meshes.complex_opaque))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_complex_opaque.start, tex_complex_opaque.length)
            if tex_complex_opaque.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_complex_opaque.end)
            else:
                write_integer(f, ">", 0)
        if meshes.simple_alpha:
            write_integer(f, ">", 258, len(meshes.simple_alpha))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_simple_alpha.start, tex_simple_alpha.length)
            if tex_simple_alpha.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_simple_alpha.end)
            else:
                write_integer(f, ">", 0)
        if meshes.complex_alpha:
            write_integer(f, ">", 514, len(meshes.complex_alpha))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_complex_alpha.start, tex_complex_alpha.length)
            if tex_complex_alpha.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_complex_alpha.end)
            else:
                write_integer(f, ">", 0)
        if meshes.simple_clip:
            write_integer(f, ">", 260, len(meshes.simple_clip))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_simple_clip.start, tex_simple_clip.length)
            if tex_simple_clip.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_simple_clip.end)
            else:
                write_integer(f, ">", 0)
        if meshes.complex_clip:
            write_integer(f, ">", 516, len(meshes.complex_clip))
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", tex_complex_clip.start, tex_complex_clip.length)
            if tex_complex_clip.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", tex_complex_clip.end)
            else:
                write_integer(f, ">", 0)
        return mesh_offset, self.nof0_offsets

    def le_10(self):
        f = self.f
        meshes = self.meshes
        model_data = self.model
        bone_names = [a.name for a in model_data.bones]

        bone_used = self.bone

        tex_simple_opaque = []   #  1 bone  no transparency  1 1
        tex_complex_opaque = []  # >1 bone  no transparency  1 2
        tex_simple_alpha = []    #  1 bone     transparency  2 1
        tex_complex_alpha = []   # >1 bone     transparency  2 2
        tex_simple_clip = []    #  1 bone      clip          4 1
        tex_complex_clip = []   # >1 bone      clip          4 2

        if meshes.simple_opaque:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.simple_opaque):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, "<", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_simple_opaque = TextureData(start, end, length)
        if meshes.complex_opaque:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.complex_opaque):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, "<", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_complex_opaque = TextureData(start, end, length)
        if meshes.simple_alpha:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.simple_alpha):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, "<", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_simple_alpha = TextureData(start, end, length)
        if meshes.complex_alpha:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.complex_alpha):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, "<", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_complex_alpha = TextureData(start, end, length)
        if meshes.simple_clip:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.simple_clip):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                bone = bone_used.index(mesh.bone_names[0])
                write_integer(f, "<", mesh.vis_bone, bone, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_simple_clip = TextureData(start, end, length)
        if meshes.complex_clip:
            start = f.tell()
            mat_list = []
            for i, mesh in enumerate(meshes.complex_clip):
                write_float(f, "<", mesh.center[0], mesh.center[1], mesh.center[2], mesh.radius)
                write_integer(f, "<", mesh.vis_bone, 4294967295, mesh.material_name, mesh.vert, mesh.face, i)
                if mesh.material_name not in mat_list:
                    mat_list.append(mesh.material_name)
            end = f.tell()
            length = self._get_textures_le(mat_list)
            tex_complex_clip = TextureData(start, end, length)

        mesh_offset = f.tell()
        if meshes.simple_opaque:
            write_integer(f, "<", 257, len(meshes.simple_opaque))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_simple_opaque.start, tex_simple_opaque.length)
            if tex_simple_opaque.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_simple_opaque.end)
            else:
                write_integer(f, "<", 0)
        if meshes.complex_opaque:
            write_integer(f, "<", 513, len(meshes.complex_opaque))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_complex_opaque.start, tex_complex_opaque.length)
            if tex_complex_opaque.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_complex_opaque.end)
            else:
                write_integer(f, "<", 0)
        if meshes.simple_alpha:
            write_integer(f, "<", 258, len(meshes.simple_alpha))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_simple_alpha.start, tex_simple_alpha.length)
            if tex_simple_alpha.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_simple_alpha.end)
            else:
                write_integer(f, "<", 0)
        if meshes.complex_alpha:
            write_integer(f, "<", 514, len(meshes.complex_alpha))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_complex_alpha.start, tex_complex_alpha.length)
            if tex_complex_alpha.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_complex_alpha.end)
            else:
                write_integer(f, "<", 0)
        if meshes.simple_clip:
            write_integer(f, "<", 260, len(meshes.simple_clip))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_simple_clip.start, tex_simple_clip.length)
            if tex_simple_clip.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_simple_clip.end)
            else:
                write_integer(f, "<", 0)
        if meshes.complex_clip:
            write_integer(f, "<", 516, len(meshes.complex_clip))
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", tex_complex_clip.start, tex_complex_clip.length)
            if tex_complex_clip.length:
                self.nof0_offsets.append(f.tell())
                write_integer(f, "<", tex_complex_clip.end)
            else:
                write_integer(f, "<", 0)
        return mesh_offset, self.nof0_offsets
