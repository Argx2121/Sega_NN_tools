from ..util import *


class Read:
    def __init__(self, f: BinaryIO):
        """Reads a NFN0 block.

        Usage : Optional

        Function : Storing a file's name

        Parameters
        ----------
        f : BinaryIO
            The file read.

        Returns
        -------
        str :
            The NN file's name.
        """
        self.f = f

    def generic(self) -> str:
        f = self.f
        start_nfn0 = f.tell() - 4
        block_len = read_int(f)
        f.seek(8, 1)
        file_name = read_str_nulls(f, block_len)[0]
        f.seek(start_nfn0 + block_len + 8)
        return file_name
