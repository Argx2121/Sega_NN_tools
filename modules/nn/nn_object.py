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
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).be_2)
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
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).be_1)

        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).be_10)

        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).eno)

        self._debug_2(m.build_mesh)
        # f.seek(start_block + len_block + 8)  # seek end of block - sonic free riders has broken block len
        var = read_int(f)
        while var:
            var = read_int(f)
        f.seek(-4, 1)
        return m

    def ino(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).ino)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).le_3)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).ino)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_12)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m

    def lno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        m = ModelData()

        d, self.start = self._run(read_int(f), 0, model_data.Read(self._info_gen(), start_block).le_semi)

        m.info = d
        self._debug_1(d)
        info = self._info_gen()

        m.bones = self._run(d.bone_offset, 1, bones.Read(info, d.bone_count).le_full)
        m.materials = self._run(d.material_offset, 2, materials.Read(info, d.material_count).lno)
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).le_2)
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

        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_9)

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
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_9)

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
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).le_1)
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
        m.faces = self._run(d.face_offset, 3, faces.Read(info, d.face_count).le_1)
        m.vertices, m.mesh_info = self._run(d.vertex_offset, 4, vertices.Read(info, d.vertex_count).zno)
        m.build_mesh = self._run(- self.start, 5, meshes.Read(info, d.mesh_sets, d.mesh_offset, d.mesh_count).le_10)

        self._debug_2(m.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return m
