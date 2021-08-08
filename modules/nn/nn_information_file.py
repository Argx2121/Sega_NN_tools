from ..util import *


class Read:
    __slots__ = ["f"]

    def __init__(self, f: BinaryIO):
        """Reads a N*IF block.

        Usage : Required

        Function : Storing file information

        Parameters
        ----------
        f : BinaryIO
            The file read.

        Returns
        -------
        int :
            End position
        """
        self.f = f

    def type_1(self):  # we don't need most info, just the end of the block
        f = self.f
        f.seek(read_int(f), 1)
        return f.tell()
