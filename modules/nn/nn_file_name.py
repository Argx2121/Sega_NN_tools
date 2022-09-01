from ..util import *


class Read:
    __slots__ = ["f"]

    def __init__(self, f: BinaryIO):
        """Reads a NFN0 block.

        Usage : Optional

        Function : Storing a file's name

        Parameters
        ----------
        f : BinaryIO
            The file read.

        Returns
        -------
        str :
            The NN file's name.
        """
        self.f = f

    def generic(self) -> str:
        f = self.f
        block_len = read_int(f)
        end_of_block = block_len + f.tell()
        f.seek(8, 1)
        file_name = read_str_nulls(f, block_len - 8)[0]
        f.seek(end_of_block)
        return file_name


class Write:
    __slots__ = ["f", "name"]

    def __init__(self, f: BinaryIO, name: str):
        """Writes a NFN0 block.

        Usage : Optional

        Function : Storing a file's name

        Parameters
        ----------
        f : BinaryIO
            The file written to.

        name : str
            The model name.
        """
        self.f = f
        self.name = name

    def generic(self):
        f = self.f
        start_offset = f.tell()
        write_string(f, b"NFN0")
        write_integer(f, "<", 0, 0, 0)
        write_string(f, bytes(self.name, 'utf-8'))
        write_aligned(f, 16)
        end_offset = f.tell()
        block_len = end_offset - start_offset - 8
        f.seek(start_offset + 4)
        write_integer(f, "<", block_len)
        f.seek(end_offset)
