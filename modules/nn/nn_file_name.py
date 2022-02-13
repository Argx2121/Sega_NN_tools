from ..util import *


class Read:
    __slots__ = ["f"]

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
        block_len = read_int(f)
        end_of_block = block_len + f.tell()
        f.seek(8, 1)
        file_name = read_str_nulls(f, block_len - 8)[0]
        f.seek(end_of_block)
        return file_name
