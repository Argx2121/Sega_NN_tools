from .object_assets import *
from ..util import *
from dataclasses import dataclass


# read model
class Read:
    def __init__(self, f, post_info, format_type):
        self.f = f
        self.post_info = post_info
        self.format_type = format_type  # psu, scrp, s06

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

    def _type_1(self, debug):
        f = self.f
        post_info = self.post_info
        start_nxob = f.tell() - 4
        len_nxob = read_int(f)
        stdout.write("| \n")
        model = self.ModelData()

        model.data, self.post_info = self._execute(
            read_int(f) + post_info, "Parsing Model Info...", model_data.Read(f, post_info, start_nxob).xbox)
        post_info = self.post_info
        if debug:
            print(model.data)
            print("After info (decimal, memory rips / files with broken pointers will be negative):", post_info)

        model.bones = self._execute(post_info + model.data.bone_offset, "Parsing Bones...",
                                    bones.Read(f, model.data.bone_count).xbox)
        model.materials = self._execute(post_info + model.data.material_offset, "Parsing Materials...",
                                        materials.Read(f, post_info, model.data.material_count).xbox)
        model.faces = self._execute(post_info + model.data.face_set_offset, "Parsing Faces...",
                                    faces.Read(f, post_info, model.data.face_set_count).xbox)
        model.vertices, model.mesh_info = self._execute(
            post_info + model.data.vertex_buffer_offset, "Parsing Vertices...",
            vertices.Read(f, post_info, self.format_type, model.data.vertex_buffer_count).xbox)

        model.build_mesh = \
            console_out("Parsing Sub Mesh Data...", meshes.Read(
                f, post_info, model.data.mesh_sets_count, model.data.mesh_data_offset, model.data.mesh_data_count).xbox)
        # seeks in method
        if debug:
            print(model.build_mesh)
        f.seek(start_nxob + len_nxob + 8)  # seek end of block

        return model

    def x(self, debug) -> ModelData:
        return self._type_1(debug)
