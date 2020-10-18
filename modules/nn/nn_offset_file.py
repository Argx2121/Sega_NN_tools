from ..util import *


class Read:
    def __init__(self, f: BinaryIO):
        """Reads a NFN0 block.

        Usage : Required

        Function : Storing offsets

        Parameters
        ----------
        f : BinaryIO
            The file read.
        """
        self.f = f

    def generic(self):
        f = self.f
        n_block_len = read_int(f)
        f.seek(n_block_len, 1)
