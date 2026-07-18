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


class Write:
    __slots__ = ["f", "format_type", "effects", "nof0_offsets"]

    def __init__(self, f: BinaryIO, format_type: str, effects: list, nof0_offsets: list):
        """Writes a N*EF block.

        Usage : Optional

        Function : Storing a files material shaders


        Parameters
        ----------
        f : BinaryIO
            The file written to.

        format_type:
            Game format.

        effects : list
            List of effects.

        nof0_offsets : list
            List of NOF0 offsets.

        Returns
        -------
        list :
            List of NOF0 offsets.
        """
        self.f = f
        self.format_type = format_type
        self.effects = effects
        self.nof0_offsets = nof0_offsets

    def le(self):
        return self.write("<")

    def be(self):
        return self.write(">")

    def write(self, endian):
        f = self.f
        shader_files = self.effects[0]
        shader_names = self.effects[1]
        meshes = self.effects[2]
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "EF"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, endian, 0, 0, 0)

        to_file_name = f.tell()
        f.seek(2 * 4 * len(shader_files), 1)  # pad for shader file
        to_name_name = f.tell()
        f.seek(3 * 4 * len(shader_names), 1)  # pad for shader name
        to_meshes = f.tell()
        f.seek(2 * len(meshes), 1)  # pad for meshes
        write_aligned(f, 4)
        to_info = f.tell()
        write_integer(f, endian, 0)  # idk
        write_integer(f, endian, len(shader_files), to_file_name)
        write_integer(f, endian, len(shader_names), to_name_name)
        write_integer(f, endian, len(meshes), to_meshes)

        file_offsets = []
        for thing in shader_files:  # write names
            file_offsets.append(f.tell())
            write_string(f, bytes(thing, 'utf-8'))
            write_byte(f, endian, 0)
        name_offsets = []
        for thing in shader_names:  # write names
            name_offsets.append(f.tell())
            write_string(f, bytes(thing, 'utf-8'))
            write_byte(f, endian, 0)
        write_aligned(f, 16)
        end_block = f.tell()

        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, endian, to_info, 0)

        f.seek(to_file_name)
        for i in file_offsets:
            write_integer(f, endian, 0)
            nof0_offsets.append(f.tell())
            write_integer(f, endian, i)
        f.seek(to_name_name)
        for i, offset in enumerate(name_offsets):
            write_integer(f, endian, 0, i)
            nof0_offsets.append(f.tell())
            write_integer(f, endian, offset)

        nof0_offsets.append(to_info+8)
        nof0_offsets.append(to_info+16)
        nof0_offsets.append(to_info+24)

        f.seek(end_block)
        return nof0_offsets
