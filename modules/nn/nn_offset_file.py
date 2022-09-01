from ..util import *


class Read:
    __slots__ = ["f"]

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
        f.seek(read_int(f), 1)


class Write:
    __slots__ = ["f", "nof0_offsets"]

    def __init__(self, f: BinaryIO, nof0_offsets: list):
        """Writes a NFN0 block.

        Usage : Required

        Function : Storing offsets

        Parameters
        ----------
        f : BinaryIO
            The file written to.

        nof0_offsets : list
            List of NOF0 offsets.
        """
        self.f = f
        self.nof0_offsets = nof0_offsets

    def le(self):
        f = self.f
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        write_string(f, bytes("NOF0", 'utf-8'))
        write_integer(f, "<", 0, len(nof0_offsets), 0)
        for offset in nof0_offsets:
            write_integer(f, "<", offset)
        write_aligned(f, 16)
        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        f.seek(end_block)

    def be(self):
        f = self.f
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        write_string(f, bytes("NOF0", 'utf-8'))
        write_integer(f, ">", 0, len(nof0_offsets), 0)
        for offset in nof0_offsets:
            write_integer(f, ">", offset)
        write_aligned(f, 16)
        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        f.seek(end_block)

