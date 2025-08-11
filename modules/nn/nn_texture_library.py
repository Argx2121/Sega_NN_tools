from ..util import *
from enum import Flag


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
            f.seek(self.post_info + texture_start)
            texture_interp = [read_short_tuple(f, 12)[4:6] for _ in range(texture_count)]
            texture_interp = [(interp_min(a[0]), interp_mag(a[1])) for a in texture_interp]
            for i in range(texture_count):
                f.seek(texture_names[i] + self.post_info)
                # noinspection PyTypeChecker
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        elif self.format_type == "SonicTheHedgehog4EpisodeII_L":
            f.seek(4, 1)
            texture_start = read_int(f)
            f.seek(texture_start)
            texture_names = [read_int_tuple(f, 8)[2] for _ in range(texture_count)]
            f.seek(texture_start)
            texture_interp = [read_short_tuple(f, 16)[6:8] for _ in range(texture_count)]
            texture_interp = [(interp_min(a[0]), interp_mag(a[1])) for a in texture_interp]
            for i in range(texture_count):
                f.seek(texture_names[i])
                # noinspection PyTypeChecker
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        else:
            texture_start = read_int(f)
            f.seek(self.post_info + texture_start)
            texture_names = [read_int_tuple(f, 5)[1] for _ in range(texture_count)]
            f.seek(self.post_info + texture_start)
            texture_interp = [read_short_tuple(f, 10)[4:6] for _ in range(texture_count)]
            texture_interp = [(interp_min(a[0]), interp_mag(a[1])) for a in texture_interp]
            for i in range(texture_count):
                f.seek(texture_names[i] + self.post_info)
                # noinspection PyTypeChecker
                texture_names[i] = read_str_terminated(f)
            f.seek(end_of_block)
        return [(texture_names[i], texture_interp[i]) for i in range(texture_count)]

    def be(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, ">") + start_block)
        texture_count = read_int(f, ">")
        texture_start = read_int(f, ">")
        f.seek(self.post_info + texture_start)
        texture_names = [read_int_tuple(f, 5, ">")[1] for _ in range(texture_count)]
        f.seek(self.post_info + texture_start)  # sorry guys cba
        texture_interp = [read_short_tuple(f, 10, ">")[4:6] for _ in range(texture_count)]
        texture_interp = [(interp_min(a[0]), interp_mag(a[1])) for a in texture_interp]
        for i in range(texture_count):
            f.seek(texture_names[i] + self.post_info)
            # noinspection PyTypeChecker
            texture_names[i] = read_str_terminated(f)
        f.seek(end_of_block)
        return [(texture_names[i], texture_interp[i]) for i in range(texture_count)]


class Write:
    __slots__ = ["f", "format_type", "textures", "nof0_offsets", "texture_interp"]

    def __init__(self, f: BinaryIO, format_type: str, textures: dict, nof0_offsets: list):
        """Writes a N*TL block.

        Usage : Optional

        Function : Storing texture names

        Parameters
        ----------
        f : BinaryIO
            The file written to.

        format_type:
            Game format.

        textures : dict
            Dict of texture data.

        nof0_offsets : list
            List of NOF0 offsets.

        Returns
        -------
        list :
            List of NOF0 offsets.

        """
        self.f = f
        self.format_type = format_type
        self.textures = [bpy.path.basename(a) for a in textures.keys()]
        self.texture_interp = list(textures.values())
        self.nof0_offsets = nof0_offsets

    def le(self):
        f = self.f
        textures = self.textures
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "TL"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 0, 0, 0)

        f.seek(5 * 4 * len(textures), 1)
        to_count = f.tell()
        write_integer(f, "<", 0, 0)

        texture_offsets = []
        for texture in textures:
            texture_offsets.append(f.tell())
            write_string(f, bytes(texture, 'utf-8'))
            write_byte(f, "<", 0)
        write_aligned(f, 16)
        end_block = f.tell()

        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, "<", to_count, 0, 0)

        for i, offset in enumerate(texture_offsets):
            nof0_offsets.append(f.tell())
            write_integer(f, "<", offset)
            write_short(f, "<", to_interp_min(self.texture_interp[i][0]), to_interp_mag(self.texture_interp[i][1]))
            write_integer(f, "<", 0, 0, 0)
        nof0_offsets.append(f.tell())

        f.seek(to_count)
        write_integer(f, "<", len(textures), 16)

        f.seek(end_block)
        return nof0_offsets

    def be(self):
        f = self.f
        textures = self.textures
        nof0_offsets = self.nof0_offsets
        start_block = f.tell()
        block_name = "N" + self.format_type[-1] + "TL"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, "<", 0, 0, 0)

        f.seek(5 * 4 * len(textures), 1)
        to_count = f.tell()
        write_integer(f, ">", 0, 0)

        texture_offsets = []
        for texture in textures:
            texture_offsets.append(f.tell())
            write_string(f, bytes(texture, 'utf-8'))
            write_byte(f, ">", 0)
        write_aligned(f, 16)
        end_block = f.tell()

        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, ">", to_count, 0, 0)

        for i, offset in enumerate(texture_offsets):
            nof0_offsets.append(f.tell())
            write_integer(f, ">", offset)
            write_short(f, ">", to_interp_min(self.texture_interp[i][0]), to_interp_mag(self.texture_interp[i][1]))
            write_integer(f, ">", 0, 0, 0)
        nof0_offsets.append(f.tell())

        f.seek(to_count)
        write_integer(f, ">", len(textures), 16)

        f.seek(end_block)
        return nof0_offsets
