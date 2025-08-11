from ..util import *


class Read:
    __slots__ = ["f", "block_name"]

    def __init__(self, f: BinaryIO, block_name: str):
        """Skip an unknown block.

        Usage : Unknown

        Function : Unknown

        Parameters
        ----------
        f : BinaryIO
            The file read.

        block_name : str
            Name of the block read.
        """
        self.f = f
        self.block_name = block_name

    def _skip(self):
        f = self.f
        f.seek(read_int(f), 1)

    def generic(self):
        console_out("Skipping N Block %s..." % self.block_name, self._skip)
