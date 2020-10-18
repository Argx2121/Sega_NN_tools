from ..util import *


class Read:
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
        block_len = read_int(f)
        f.seek(block_len, 1)
        post_info = f.tell()
        return post_info
