from ...util import *


# read + make textures
class ExtractImage:
    def __init__(self, f: BinaryIO, file):
        self.f = f
        self.filepath = file

    def execute(self):
        f = self.f
        start = f.tell()
        count, flags = read_short_tuple(f, 2, ">")
        offsets = read_int_tuple(f, count, ">")
        f.seek(flags * count, 1)
        tex_names_len = (offsets[0] - f.tell() + start)
        texture_start = f.tell()
        texture_files = read_str_nulls(f, tex_names_len)[:count]
        texture_files = [bpy.path.native_pathsep(t) for t in texture_files]

        f.seek(texture_start)  # names are needed like this to generate .texture_names files
        texture_file_stream = f.read(tex_names_len)

        tex_path = self.filepath
        texture_files = [tex_path + texture_files[texture_index] + ".gvr" for texture_index in list(range(count))]

        for texture_index in range(count):
            f.seek(start + offsets[texture_index] + 20)
            t_len = read_int(f) + 48 - 24

            f.seek(start + offsets[texture_index])

            pathlib.Path(texture_files[texture_index]).parent.mkdir(parents=True, exist_ok=True)

            ft = open(texture_files[texture_index], "wb")
            ft.write(f.read(t_len))
            ft.close()
        return count, texture_file_stream
