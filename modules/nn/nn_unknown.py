from ..util import *


class Read:
    def __init__(self, f: BinaryIO, block_name: str):
        """Skip an unknown block.

        Parameters
        ----------
        f : BinaryIO
            The file read.

        block_name : str
            Name of the block read.
        """
        self.f = f
        self.block_name = block_name

    def _type_1(self):
        f = self.f
        n_block_len = read_int(f)
        f.seek(n_block_len, 1)

    def generic(self):
        """Skips an unknown block.

        Platform : Unknown

        Usage : Unknown

        Function : Unknown
        """
        console_out("Skipping Unknown N Block %s..." % self.block_name, self._type_1)
