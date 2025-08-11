from ..util import *


class Read:
    __slots__ = ["f", "post_info"]

    def __init__(self, f: BinaryIO, post_info: int):
        """Reads a N*EF block.

        Usage : Optional

        Function : Storing a files material shaders (not applicable to blender)


        Parameters
        ----------
        f : BinaryIO
            The file read.

        post_info : int
            After the info block.
        """
        self.f = f
        self.post_info = post_info

    def le(self):
        return self.read("<")

    def be(self):
        return self.read(">")

    def read(self, endian):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, endian) + self.post_info)
        idk = read_int(f, endian)
        shader_f_count = read_int(f, endian)
        shader_f_start = read_int(f, endian)
        shader_t_count = read_int(f, endian)
        shader_t_start = read_int(f, endian)
        mesh_count = read_int(f, endian)
        mesh_start = read_int(f, endian)
        f.seek(self.post_info + shader_f_start)
        shader_files = [read_int_tuple(f, 2, endian)[1] for _ in range(shader_f_count)]
        f.seek(self.post_info + shader_t_start)
        shader_types = [read_int_tuple(f, 3, endian)[2] for _ in range(shader_t_count)]  # dont care
        f.seek(self.post_info + mesh_start)
        meshes = [read_short(f, endian) for _ in range(mesh_count)]
        for i in range(shader_f_count):
            f.seek(shader_files[i] + self.post_info)
            # noinspection PyTypeChecker
            shader_files[i] = read_str_terminated(f)
        for i in range(shader_t_count):
            f.seek(shader_types[i] + self.post_info)
            # noinspection PyTypeChecker
            shader_types[i] = read_str_terminated(f)
        meshes = [(shader_files[a], shader_types[a]) if a != 65535 else ('', '') for a in meshes]
        f.seek(end_of_block)
        return meshes
