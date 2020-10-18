from ..util import *


class Read:
    def __init__(self, f: BinaryIO):
        """Reads a NEND block.

        Usage : Required

        Function : Indicating end of file

        Parameters
        ----------
        f : BinaryIO
            The file read.
        """
        self.f = f

    def generic(self):
        f = self.f
        block_len = read_int(f)
        f.seek(block_len, 1)
