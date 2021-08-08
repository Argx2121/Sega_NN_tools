from ..util import *


class Read:
    __slots__ = ["f"]

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
        f.seek(read_int(f), 1)
