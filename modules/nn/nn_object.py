from .object_assets import *
from ..util import *


# read model
class Read:
    def __init__(self, f, post_info, format_type):
        self.f = f
        self.post_info = post_info
        self.format_type = format_type  # psu, scrp, s06

    def _execute(self, seek, text, function):
        self.f.seek(seek)
        return console_out(text, function)

    def _type_1(self, debug):
        f = self.f
        post_info = self.post_info
        start_nxob = f.tell() - 4
        len_nxob = read_int(f)
        stdout.write("| \n")

        data, self.post_info = self._execute(
            read_int(f) + post_info, "Parsing Model Info...", model_data.Read(f, post_info, start_nxob).xbox)
        post_info = self.post_info
        if debug:
            print(data)
            print("After info (decimal, memory rips / files with broken pointers will be negative):", post_info)

        bone_data = self._execute(post_info + data.bone_offset, "Parsing Bones...", bones.Read(f, data.bone_count).xbox)

        material_list = self._execute(
            post_info + data.material_offset, "Parsing Materials...",
            materials.Read(f, post_info, data.material_count).xbox)

        face_list = self._execute(
            post_info + data.face_set_offset, "Parsing Faces...", faces.Read(f, post_info, data.face_set_count).xbox)

        vertex_data, mesh_info = self._execute(
            post_info + data.vertex_buffer_offset, "Parsing Vertices...",
            vertices.Read(f, post_info, self.format_type, data.vertex_buffer_count).xbox)

        build_mesh = console_out("Parsing Sub Mesh Data...", meshes.Read(
            f, post_info, data.mesh_sets_count, data.mesh_data_offset, data.mesh_data_count).xbox)  # seeks in method
        if debug:
            print(build_mesh)

        f.seek(start_nxob + len_nxob + 8)  # seek past this n block so we can read the next block

        return_data = (
            bone_data, data.bone_count, data.material_count,
            material_list, build_mesh, face_list, mesh_info, vertex_data
        )
        return return_data

    def x(self, debug) -> tuple:
        return self._type_1(debug)
