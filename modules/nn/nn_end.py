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


class Write:
    __slots__ = ["f", "align"]

    def __init__(self, f: BinaryIO, align: int):
        """Writes a NEND block.

        Usage : Required

        Function : Indicating end of file

        Parameters
        ----------
        f : BinaryIO
            The file written to.
        align : int
            Alignment length/
        """
        self.f = f
        self.align = align

    def generic(self):
        f = self.f
        start = f.tell()
        write_string(f, b"NEND")
        write_aligned(f, self.align)
        end = f.tell()
        f.seek(start + 4)
        write_integer(f, "<", end - start - 8)
        f.seek(end)
