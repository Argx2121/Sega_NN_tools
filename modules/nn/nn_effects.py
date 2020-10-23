from ..nn_util import *


class Read:
    def __init__(self, f: BinaryIO):
        """Reads a N*EF block.

        Usage : Optional

        Function : Storing a files material effects (not applicable to blender)


        Parameters
        ----------
        f : BinaryIO
            The file read.
        """
        self.f = f

    def type_1(self):
        f = self.f
        n_block_len = read_int(f)
        f.seek(n_block_len, 1)
