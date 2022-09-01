from ..util import *
from dataclasses import dataclass

from .object_assets import model_data, materials, faces, vertices, bones, meshes
from .object_assets.obj_util import *


@dataclass
class ModelData:
    info: Any = None
    bones: Any = None
    materials: Any = None
    faces: Any = None
    uvs: Any = False
    wxs: Any = False
    norm: Any = False
    col: Any = False
    vertices: Any = None
    mesh_info: Any = None
    build_mesh: Any = None


# read model
class ReadModel:
    __slots__ = ["f", "start", "format_type", "debug"]

    def __init__(self, f, post_info, format_type, debug):
        self.f = f
        self.start = post_info
        self.format_type = format_type
        self.debug = debug

    def _run(self, seek, text_index: int, function):
        text_list = ["Parsing Model Info...", "Parsing Bones...", "Parsing Materials...", "Parsing Faces...",
                     "Parsing Vertices...", "Parsing Sub Mesh Data..."]
        self.f.seek(self.start + seek)
        return console_out(text_list[text_index], function)

    def _start(self):
        f = self.f
        start_block = f.tell() - 4
        len_block = read_int(f)
        stdout.write("| \n")
        return start_block, len_block

    def _info_gen(self):
        return self.f, self.start, self.format_type, self.debug

    def _debug_1(self, data):
        if self.debug:
            print(data)
            print("After info offset (memory rips / files with broken pointers will be negative):", self.start)

    def _debug_2(self, build_mesh):
        if self.debug:
            print(build_mesh)

    def cno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f, ">"), 0, model_data.Read(self._info_gen(), start_block).be_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).be_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).cno)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).cno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).cno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).be_12)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def eno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f

        m = ModelData()

        d, self.start = self._run(read_int(f, ">"), 0, model_data.Read(self._info_gen(), start_block).be_full)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).be_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).eno)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).eno)

        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).be_10)

        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).eno)

        self._debug_2(m.build_mesh)
        # f.seek(start_block + len_block + 8)  # seek end of block - sonic free riders has broken block len
        var = read_int(f)
        while var:
            var = read_int(f)
        f.seek(-4, 1)
        return m

    def gno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f, ">"), 0, model_data.Read(self._info_gen(), start_block).be_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).be_semi)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).gno)
        m.faces, m.uvs, m.norm, m.col = self._run(d.face_offset, 3, faces.Read(info, d.face_count).gno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).gno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).be_9)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def ino(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_ino)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).ino)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).ino)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).ino)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_12)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def lno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        if self.format_type == "SonicTheHedgehog4EpisodeII_L":
            d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_lno_s4e2)

            m.info = d
            self._debug_1(d)
            info = self._info_gen()

            m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full_s4e2)
            m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).lno_s4e2)
            m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).lno_s4e2)
            m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).lno_s4e2)
            m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_14)

            self._debug_2(m.build_mesh)
            f.seek(4, 1)
        else:
            d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_lno)

            m.info = d
            self._debug_1(d)
            info = self._info_gen()

            m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
            m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).lno)
            m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).lno)
            m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).lno)
            m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_12)

            self._debug_2(m.build_mesh)
            f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def sno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).sno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).sno)

        var = console_out_pre("Generating faces")
        m.faces, m.vertices = implicit_faces_fix_mesh_size(m.vertices)
        console_out_post(var)

        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_9_face)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def uno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).uno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).uno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_9_face)

        m.faces = implicit_faces(m.vertices)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def xno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_full)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).xno)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).xno_zno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).xno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_10)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def zno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_full)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).zno)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).xno_zno)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).zno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_10)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m


class WriteModel:
    __slots__ = ["f", "format_type", "debug", "nof0_offsets", "model_info", "settings"]

    def __init__(self, f, format_type, debug, nof0_offsets, model_info, settings):
        self.f = f
        self.format_type = format_type
        self.debug = debug
        self.nof0_offsets = nof0_offsets
        self.model_info = model_info
        self.settings = settings

    def _run(self, text_index: int, function):
        text_list = ["Writing Bones...", "Writing Materials...", "Writing Vertices...", "Writing Faces...",
                     "Writing Meshes...", "Writing Model Info..."]
        return console_out(text_list[text_index], function)

    def gno(self):
        f = self.f
        nof0_offsets = self.nof0_offsets
        model_info = self.model_info
        format_type = self.format_type
        bone_used = self.model_info.bone_used

        start_block = f.tell()
        block_name = "NGOB"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 0, 0, 0)

        bone_offset = self._run(0, bones.Write(f, model_info.bones).be_semi)

        material_offset, nof0_offsets = self._run(
            1, materials.Write(f, format_type, model_info.materials, nof0_offsets).gno)

        vert_offset, nof0_offsets = self._run(
            2, vertices.Write(
                f, format_type, model_info.geometry, nof0_offsets, model_info.bones, bone_used, self.settings).gno)

        face_offset, nof0_offsets = self._run(
            3, faces.Write(f, format_type, model_info.geometry, nof0_offsets).gno)

        mesh_offset, nof0_offsets = self._run(
            4, meshes.Write(
                f, format_type, model_info.meshes, nof0_offsets, len(model_info.bones), bone_used, model_info).be_9)

        offsets = (bone_offset, material_offset, vert_offset, face_offset, mesh_offset)

        info_offset, nof0_offsets = self._run(
            5, model_data.Write(f, format_type, model_info, nof0_offsets, offsets, bone_used).be)

        write_aligned(f, 16)

        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, ">", info_offset)
        f.seek(end_block)

        return nof0_offsets

    def xno(self):
        f = self.f
        nof0_offsets = self.nof0_offsets
        model_info = self.model_info
        format_type = self.format_type
        bone_used = self.model_info.bone_used

        start_block = f.tell()
        block_name = "NXOB"
        write_string(f, bytes(block_name, 'utf-8'))
        self.nof0_offsets.append(f.tell() + 16)
        write_integer(f, "<", 0, 0, 0, 0, 0, 0, 1)

        bone_offset = self._run(0, bones.Write(f, model_info.bones).le_full)

        material_offset, nof0_offsets = self._run(
            1, materials.Write(f, format_type, model_info.materials, nof0_offsets).xno)

        face_offset, nof0_offsets = self._run(
            3, faces.Write(f, format_type, model_info.geometry, nof0_offsets).xno)

        vert_start = f.tell()
        vert_offset, v_buff_end, nof0_offsets = self._run(
            2, vertices.Write(
                f, format_type, model_info.geometry, nof0_offsets, model_info.bones, bone_used, self.settings).xno)

        mesh_offset, nof0_offsets = self._run(
            4, meshes.Write(
                f, format_type, model_info.meshes, nof0_offsets, len(model_info.bones), bone_used, model_info).le_10)

        offsets = (bone_offset, material_offset, vert_offset, face_offset, mesh_offset)

        info_offset, nof0_offsets = self._run(
            5, model_data.Write(f, format_type, model_info, nof0_offsets, offsets, bone_used).le)

        write_aligned(f, 16)

        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, "<", info_offset, 0, v_buff_end - vert_start, vert_start)
        f.seek(end_block)

        return nof0_offsets

    def zno(self):
        f = self.f
        nof0_offsets = self.nof0_offsets
        model_info = self.model_info
        format_type = self.format_type
        bone_used = self.model_info.bone_used

        start_block = f.tell()
        block_name = "NZOB"
        write_string(f, bytes(block_name, 'utf-8'))
        self.nof0_offsets.append(f.tell() + 16)
        write_integer(f, "<", 0, 0, 3, 0, 0, 0, 0)

        bone_offset = self._run(0, bones.Write(f, model_info.bones).le_full)

        import codecs
        cred_bytes = codecs.encode(self.settings.credits, "utf-8")  # todo is this needed
        cred_bytes = codecs.decode(cred_bytes, "hex")
        f.write(cred_bytes)

        material_offset, nof0_offsets = self._run(
            1, materials.Write(f, format_type, model_info.materials, nof0_offsets).zno)

        face_offset, nof0_offsets = self._run(
            3, faces.Write(f, format_type, model_info.geometry, nof0_offsets).xno)

        vert_start = f.tell()
        vert_offset, v_buff_end, nof0_offsets = self._run(
            2, vertices.Write(
                f, format_type, model_info.geometry, nof0_offsets, model_info.bones, bone_used, self.settings).zno)

        mesh_offset, nof0_offsets = self._run(
            4, meshes.Write(
                f, format_type, model_info.meshes, nof0_offsets, len(model_info.bones), bone_used, model_info).le_10)

        offsets = (bone_offset, material_offset, vert_offset, face_offset, mesh_offset)

        info_offset, nof0_offsets = self._run(
            5, model_data.Write(f, format_type, model_info, nof0_offsets, offsets, bone_used).le)

        write_aligned(f, 16)

        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, "<", info_offset, 0, v_buff_end - vert_start, vert_start)
        f.seek(end_block)

        return nof0_offsets
