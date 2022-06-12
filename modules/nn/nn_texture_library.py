from ..util import *


class Read:
    __slots__ = ["f", "post_info", "filepath", "format_type"]

    def __init__(self, f: BinaryIO, post_info: int, filepath: str, format_type: str):
        """Reads a N*TL block.

        Usage : Optional

        Function : Storing texture names

        Parameters
        ----------
        f : BinaryIO
            The file read.

        post_info : int
            After the info block.

        filepath : str
            Folder location.

        format_type:
            Game format.

        Returns
        -------
        tuple :
            Texture names

        """
        self.f = f
        self.post_info = post_info
        self.filepath = filepath.rstrip(bpy.path.basename(filepath))
        self.format_type = format_type

    def le(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f) + start_block)
        texture_count = read_int(f)
        if self.format_type == "SonicTheHedgehog4EpisodeI_I":
            texture_start = read_int(f)
            f.seek(self.post_info + texture_start)
            texture_names = [read_int_tuple(f, 6)[1] for _ in range(texture_count)]
            for i in range(texture_count):
                f.seek(texture_names[i] + self.post_info)
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        elif self.format_type == "SonicTheHedgehog4EpisodeII_L":
            f.seek(4, 1)
            texture_start = read_int(f)
            f.seek(texture_start)
            texture_names = [read_int_tuple(f, 8)[2] for _ in range(texture_count)]
            for i in range(texture_count):
                f.seek(texture_names[i])
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        else:
            texture_start = read_int(f)
            f.seek(self.post_info + texture_start)
            texture_names = [read_int_tuple(f, 5)[1] for _ in range(texture_count)]
            for i in range(texture_count):
                f.seek(texture_names[i] + self.post_info)
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        return [self.filepath + t for t in texture_names]

    def be(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, ">") + start_block)
        texture_count = read_int(f, ">")
        texture_start = read_int(f, ">")
        f.seek(self.post_info + texture_start)
        texture_names = [read_int_tuple(f, 5, ">")[1] for _ in range(texture_count)]
        for i in range(texture_count):
            f.seek(texture_names[i] + self.post_info)
            texture_names[i] = read_str_terminated(f)
        f.seek(end_of_block)
        return [self.filepath + t for t in texture_names]
