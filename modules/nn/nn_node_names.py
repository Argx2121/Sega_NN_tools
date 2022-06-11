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
