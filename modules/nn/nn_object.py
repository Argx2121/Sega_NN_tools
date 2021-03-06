from .object_assets import model_data, materials, faces, vertices, bones, meshes
from .object_assets.obj_util import implicit_faces_fix_mesh_size
from ..util import *
from dataclasses import dataclass


# read model
class Read:
    def __init__(self, f, post_info, format_type, debug):
        self.f = f
        self.post_info = post_info
        self.format_type = format_type
        self.debug = debug

    def _execute(self, seek, text_index: int, function):
        text_list = ["Parsing Model Info...", "Parsing Bones...", "Parsing Materials...", "Parsing Faces...",
                     "Parsing Vertices..."]
        self.f.seek(self.post_info + seek)
        return console_out(text_list[text_index], function)

    def _start(self):
        f = self.f
        start_block = f.tell() - 4
        len_block = read_int(f)
        stdout.write("| \n")
        return start_block, len_block

    @dataclass
    class ModelData:
        data: Any = None
        bones: Any = None
        materials: Any = None
        faces: Any = None
        vertices: Any = None
        mesh_info: Any = None
        build_mesh: Any = None

    def xno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f), 0, model_data.Read(f, post, start_block).le_full)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).le_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).xno)

        model.faces = self._execute(data.face_set_offset, 3, faces.Read(f, post, data.face_set_count).le_1)

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).le_1)

        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).le_10)  # seeks in method

        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model

    def zno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f), 0, model_data.Read(f, post, start_block).le_full)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).le_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).zno)

        model.faces = self._execute(data.face_set_offset, 3, faces.Read(f, post, data.face_set_count).le_1)

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).le_1)

        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).le_10)  # seeks in method

        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model

    def lno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f), 0, model_data.Read(f, post, start_block).le_semi)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).le_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).lno)

        model.faces = self._execute(data.face_set_offset, 3, faces.Read(f, post, data.face_set_count).le_2)

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).le_2)

        print(data.mesh_data_offset)
        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).le_12)  # seeks in method

        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model

    def sno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f), 0, model_data.Read(f, post, start_block).le_semi)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).le_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).sno)

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).le_3)

        var = console_out_pre("Generating faces")
        model.faces, model.vertices = implicit_faces_fix_mesh_size(model.vertices)
        console_out_post(var)

        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).le_9)  # seeks in method

        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model

    def eno(self) -> ModelData:
        start_block, len_block = self._start()  # len block is wrong
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f, ">"), 0, model_data.Read(f, post, start_block).be_full)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).be_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).eno)

        model.faces = self._execute(data.face_set_offset, 3, faces.Read(f, post, data.face_set_count).be_1)

        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).be_10)  # seeks in method

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).be_1)

        if self.debug:
            print(model.build_mesh)
        return model

    def cno(self) -> ModelData:
        start_block, len_block = self._start()
        f = self.f
        model = self.ModelData()
        post = self.post_info

        data, self.post_info = self._execute(read_int(f, ">"), 0, model_data.Read(f, post, start_block).be_semi)
        model.data = data
        post = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post)

        model.bones = self._execute(data.bone_offset, 1, bones.Read(f, data.bone_count).be_full)

        model.materials = self._execute(data.material_offset, 2, materials.Read(f, post, data.material_count).eno)

        model.faces = self._execute(data.face_set_offset, 3, faces.Read(f, post, data.face_set_count).be_2)

        model.build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).be_12)  # seeks in method

        model.vertices, model.mesh_info = self._execute(
            data.vertex_buffer_offset, 4, vertices.Read(f, post, self.format_type, data.vertex_buffer_count).be_2)

        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model
