from ..nn_util import *


class Read:
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

    def type_1(self):
        f = self.f
        start_nxnn = f.tell() - 4
        block_len, to_count = read_multi_ints(f, 2)
        f.seek(self.post_info + to_count + 4)
        bone_count = read_int(f)
        f.seek(start_nxnn + bone_count * 8 + 16 + 12)
        name_len = start_nxnn + block_len + 8 - f.tell()
        bone_names = read_str_nulls(f, name_len)[:bone_count]
        f.seek(start_nxnn + block_len + 8)
        return bone_names

    def type_2(self):  # assumed to exist
        f = self.f
        start_nxnn = f.tell() - 4
        block_len = read_int(f)
        to_count = read_int(f, ">")
        f.seek(self.post_info + to_count + 4)
        bone_count = read_int(f, ">")
        f.seek(start_nxnn + bone_count * 8 + 16 + 12)
        name_len = start_nxnn + block_len + 8 - f.tell()
        bone_names = read_str_nulls(f, name_len)[:bone_count]
        f.seek(start_nxnn + block_len + 8)
        return bone_names
