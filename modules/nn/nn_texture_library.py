from ..util import *


class Read:
    __slots__ = ["f", "filepath"]

    def __init__(self, f: BinaryIO, filepath: str):
        """Reads a N*TL block.

        Usage : Optional

        Function : Storing texture names

        Parameters
        ----------
        f : BinaryIO
            The file read.

        filepath : str
            Folder location.

        Returns
        -------
        tuple :
            Texture names

        """
        self.f = f
        self.filepath = filepath.rstrip(bpy.path.basename(filepath))

    def le(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f) + start_block)
        texture_count = read_int_tuple(f, 2)[0]
        texture_names = read_str_nulls(f, end_of_block - f.tell())[:texture_count]
        f.seek(end_of_block)
        return [self.filepath + t for t in texture_names]

    def be(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, ">") + start_block)
        texture_count = read_int_tuple(f, 2, ">")[0]
        texture_names = read_str_nulls(f, end_of_block - f.tell())[:texture_count]
        f.seek(end_of_block)
        return [self.filepath + t for t in texture_names]
