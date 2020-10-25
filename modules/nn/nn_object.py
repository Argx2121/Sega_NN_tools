from .object_assets import model_data, materials, faces, vertices, bones, meshes
from ..util import *
from dataclasses import dataclass


# read model
class Read:
    def __init__(self, f, post_info, format_type, debug):
        self.f = f
        self.post_info = post_info
        self.format_type = format_type
        self.debug = debug

    def _execute(self, seek, text, function):
        self.f.seek(seek)
        return console_out(text, function)

    @dataclass
    class ModelData:
        data: Any = None
        bones: Any = None
        materials: Any = None
        faces: Any = None
        vertices: Any = None
        mesh_info: Any = None
        build_mesh: Any = None

    def type_1(self) -> ModelData:
        f = self.f
        start_block = f.tell() - 4
        len_block = read_int(f)
        model = self.ModelData()
        stdout.write("| \n")

        data, self.post_info = self._execute(
            read_int(f) + self.post_info, "Parsing Model Info...", model_data.Read(f, self.post_info, start_block).xbox)
        model.data = data
        post_info = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post_info)

        model.bones = self._execute(
            post_info + data.bone_offset, "Parsing Bones...", bones.Read(f, data.bone_count).type_1)
        model.materials = self._execute(post_info + data.material_offset, "Parsing Materials...",
                                        materials.Read(f, post_info, data.material_count).type_1)
        model.faces = self._execute(
            post_info + data.face_set_offset, "Parsing Faces...", faces.Read(f, post_info, data.face_set_count).xbox)
        model.vertices, model.mesh_info = self._execute(
            post_info + data.vertex_buffer_offset, "Parsing Vertices...",
            vertices.Read(f, post_info, self.format_type, data.vertex_buffer_count).xbox)

        model.build_mesh = \
            console_out("Parsing Sub Mesh Data...", meshes.Read(
                f, post_info, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).xbox)
        # seeks in method
        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model

    def type_2(self) -> ModelData:
        f = self.f
        start_block = f.tell() - 4
        len_block = read_int(f)
        model = self.ModelData()
        stdout.write("| \n")

        data, self.post_info = self._execute(
            read_int(f) + self.post_info, "Parsing Model Info...", model_data.Read(f, self.post_info, start_block).xbox)
        model.data = data
        post_info = self.post_info
        if self.debug:
            print(data)
            print("After info offset (decimal, memory rips / files with broken pointers will be negative):", post_info)

        model.bones = self._execute(
            post_info + data.bone_offset, "Parsing Bones...", bones.Read(f, data.bone_count).type_1)
        model.materials = self._execute(post_info + data.material_offset, "Parsing Materials...",
                                        materials.Read(f, post_info, data.material_count).type_2)
        model.faces = self._execute(
            post_info + data.face_set_offset, "Parsing Faces...", faces.Read(f, post_info, data.face_set_count).xbox)
        model.vertices, model.mesh_info = self._execute(
            post_info + data.vertex_buffer_offset, "Parsing Vertices...",
            vertices.Read(f, post_info, self.format_type, data.vertex_buffer_count).xbox)

        model.build_mesh = \
            console_out("Parsing Sub Mesh Data...", meshes.Read(
                f, post_info, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).xbox)
        # seeks in method
        if self.debug:
            print(model.build_mesh)
        f.seek(start_block + len_block + 8)  # seek end of block
        return model
