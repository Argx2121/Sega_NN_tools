from ..util import *


class Read:
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

    def _make_bpy(self, texture_names):
        for tex in texture_names:  # see if textures already exist in the folder
            if not os.path.exists(self.filepath + tex[:-4] + ".dds"):
                return texture_names
        return [bpy.data.images.load(self.filepath + tex[:-4] + ".dds") for tex in texture_names]

    def type_1(self):
        f = self.f
        start_block = f.tell() - 4
        block_len, to_texture_count = read_multi_ints(f, 2)
        f.seek(to_texture_count + start_block)
        texture_count = read_int(f)
        f.seek(4, 1)
        texture_names = read_str_nulls(f, start_block + block_len + 8 - f.tell())[:texture_count]
        f.seek(start_block + block_len + 8)
        return self._make_bpy(texture_names)

    def type_2(self):
        f = self.f
        start_block = f.tell() - 4
        block_len = read_int(f)
        to_texture_count = read_int(f, ">")
        f.seek(to_texture_count + start_block)
        texture_count = read_int(f, ">")
        f.seek(4, 1)
        texture_names = read_str_nulls(f, start_block + block_len + 8 - f.tell())[:texture_count]
        f.seek(start_block + block_len + 8)
        return self._make_bpy(texture_names)
