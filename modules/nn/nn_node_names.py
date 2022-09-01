from ..util import *


class Read:
    __slots__ = ["f", "post_info"]

    def __init__(self, f: BinaryIO, post_info: int):
        """Reads a N*NN block.

        Usage : Optional

        Function : Storing node names

        Parameters
        ----------
        f : BinaryIO
            The file read.

        post_info : int
            After the info block.

        Returns
        -------
        tuple :
            Node names
        """
        self.f = f
        self.post_info = post_info

    def le(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(self.post_info + read_int(f) + 4)
        bone_count = read_int(f)
        name_start = read_int(f)
        f.seek(self.post_info + name_start)
        bone_names = [list(read_int_tuple(f, 2)) for _ in range(bone_count)]
        for i in range(bone_count):
            f.seek(bone_names[i][1] + self.post_info)
            bone_names[i][1] = read_str_terminated(f)
        f.seek(end_of_block)
        return dict(bone_names)

    def be(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(self.post_info + read_int(f, ">") + 4)
        bone_count = read_int(f, ">")
        name_start = read_int(f, ">")
        f.seek(self.post_info + name_start)
        bone_names = [list(read_int_tuple(f, 2, ">")) for _ in range(bone_count)]
        for i in range(bone_count):
            f.seek(bone_names[i][1] + self.post_info)
            bone_names[i][1] = read_str_terminated(f)
        f.seek(end_of_block)
        return dict(bone_names)


class Write:
    __slots__ = ["f", "format_type", "bones", "nof0_offsets"]

    def __init__(self, f: BinaryIO, format_type: str, bones: list, nof0_offsets: list):
        """Writes a N*TL block.

        Usage : Optional

        Function : Storing node names

        Parameters
        ----------
        f : BinaryIO
            The file written to.

        format_type:
            Game format.

        bones : list
            List of node names.

        nof0_offsets : list
            List of NOF0 offsets.

        Returns
        -------
        list :
            List of NOF0 offsets.

        """
        self.f = f
        self.format_type = format_type
        self.bones = bones
        self.nof0_offsets = nof0_offsets

    def le(self):
        f = self.f
        bones = self.bones
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "NN"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 0, 0, 0)

        f.seek(2 * 4 * len(bones), 1)  # pad for bone pointers
        to_count = f.tell()
        write_integer(f, "<", 0, 0, 0)  # pad for bone info

        bone_offsets = []
        for bone in bones:  # write names
            bone_offsets.append(f.tell())
            write_string(f, bytes(bone, 'utf-8'))
            write_byte(f, "<", 0)
        write_aligned(f, 16)
        end_block = f.tell()

        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, "<", to_count, 0)

        for i, offset in enumerate(bone_offsets):
            write_integer(f, "<", i)
            nof0_offsets.append(f.tell())
            write_integer(f, "<", offset)

        f.seek(to_count)
        write_integer(f, "<", 0, len(bones), start_block + 16)
        nof0_offsets.append(f.tell() - 4)

        f.seek(end_block)
        return nof0_offsets

    def be(self):
        f = self.f
        bones = self.bones
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "NN"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 0, 0, 0)

        f.seek(2 * 4 * len(bones), 1)  # pad for bone pointers
        to_count = f.tell()
        write_integer(f, ">", 0, 0, 0)  # pad for bone info

        bone_offsets = []
        for bone in bones:  # write names
            bone_offsets.append(f.tell())
            write_string(f, bytes(bone, 'utf-8'))
            write_byte(f, ">", 0)
        write_aligned(f, 16)
        end_block = f.tell()

        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, ">", to_count, 0)

        for i, offset in enumerate(bone_offsets):
            write_integer(f, ">", i)
            nof0_offsets.append(f.tell())
            write_integer(f, ">", offset)

        f.seek(to_count)
        write_integer(f, ">", 0, len(bones), start_block + 16)
        nof0_offsets.append(f.tell() - 4)

        f.seek(end_block)
        return nof0_offsets
