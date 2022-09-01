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


class Write:
    __slots__ = ["f", "format_type", "block_count", "offset_file_start", "offset_file_end", "version"]

    def __init__(self, f: BinaryIO, format_type: str, block_count: int,
                 offset_file_start: int, offset_file_end: int, version: int):
        """Writes a N*IF block.

        Usage : Required

        Function : Storing file information

        Parameters
        ----------
        f : BinaryIO
            The file written to.

        format_type:
            Game format.

        block_count : int
            Count of chunks between N*IF and NOF0

        offset_file_start : int
            NOF0 Offset from the start of the block

        offset_file_end : int
            NOF0 Offset from the end of the block

        version : int
            NN Version
        """
        self.f = f
        self.format_type = format_type
        self.block_count = block_count
        self.offset_file_start = offset_file_start
        self.offset_file_end = offset_file_end
        self.version = version

    def le(self):
        f = self.f
        org_data = f.read()
        f.seek(0)

        offset_file_start = self.offset_file_start
        offset_file_end = self.offset_file_end
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "IF"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 24)
        write_integer(f, "<", self.block_count, 32)
        write_integer(f, "<", offset_file_start, offset_file_start + 32)
        write_integer(f, "<", offset_file_end - offset_file_start, self.version)

        f.write(org_data)

    def be(self):
        f = self.f
        org_data = f.read()
        f.seek(0)

        offset_file_start = self.offset_file_start
        offset_file_end = self.offset_file_end
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "IF"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 24)
        write_integer(f, ">", self.block_count, 32)
        write_integer(f, ">", offset_file_start, offset_file_start + 32)
        write_integer(f, ">", offset_file_end - offset_file_start, self.version)

        f.write(org_data)
