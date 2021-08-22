from ..util import *


class Read:
    __slots__ = ["f"]

    def __init__(self, f: BinaryIO):
        """Reads a N*CA block.

        Usage : Optional

        Function : Storing camera data (not applicable to blender)


        Parameters
        ----------
        f : BinaryIO
            The file read.
        """
        self.f = f

    def type_1(self):
        f = self.f
        f.seek(read_int(f), 1)
