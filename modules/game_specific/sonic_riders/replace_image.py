from . import *


class ReplaceImage:  # main
    def __init__(self, f, file_path, file_count, sub_file_offsets, naming_style):
        self.f = f
        self.file_path = file_path
        self.file_count = file_count
        self.sub_file_offsets = sub_file_offsets
        self.image_naming = naming_style
        self.texture_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.texture_names = []
        self.texture_start = None
        self.image_count = None

    def execute(self):
        f = self.f
        file_offsets = list(self.sub_file_offsets)
        for i in range(len(file_offsets) - 1):
            offset_cur = file_offsets[i]
            f.seek(offset_cur + 4)
            if BlockTypeCheck(f, self.file_path, 0).check_image():
                offset_old = file_offsets[i + 1]
                f.seek(offset_old)
                post_data = f.read()
                f.seek(offset_cur)
                self.textures(i)
                offset_diff = f.tell() - offset_old
                f.write(post_data)
                f.truncate(f.tell())
                for a in range(len(file_offsets) - i - 1):
                    if file_offsets[a + i + 1]:
                        file_offsets[a + i + 1] += offset_diff
        f.seek(file_offsets[-1])
        if BlockTypeCheck(f, self.file_path, 0).check_image():
            self.textures(len(file_offsets))

        f.seek(self.file_count + 4)
        read_aligned(f, 4)
        f.seek(self.file_count * 4, 1)  # unidentified shorts here
        for offset in file_offsets:
            write_integer(f, offset)

    def textures(self, sub_index):
        f = self.f

        def read_image(ft: BinaryIO):
            ft.seek(12)
            ft_y, ft_x = read_multi_ints(ft, 2)
            ft.seek(28)
            mip_map_count = read_int(ft)
            ft.seek(44)
            ft_type = read_int(ft)  # if the image was extracted from the game the formats here
            ft.seek(68)
            ft_type_conf = read_str(ft, 4)
            if ft_type_conf == 'PRTF':  # if its one of our textures read texture data and return
                ft.seek(128)
                ft_stream = ft.read()
                return ft_y, ft_x, ft_stream, ft_type
            ft.seek(84)
            tex_source = read_str(ft, 4)
            if tex_source == 'DX10':  # made by nvidia tools - DXT format is stored elsewhere
                ft.seek(128)
                ft_type = read_int(ft)
                if ft_type == 71 and mip_map_count > 1:
                    ft_type = 29701
                else:
                    determine_dxt = {71: 29445, 74: 29956, 77: 31494}  # dxt1, dxt3, dxt5
                    ft_type = determine_dxt[ft_type]  # from DXT to bitflags
                ft.seek(148)
                ft_stream = ft.read()
            else:  # typical dxt place
                if tex_source == 'DXT1' and mip_map_count > 1:
                    ft_type = 29701
                else:
                    determine_dxt = {'DXT1': 29445, 'DXT3': 29956, 'DXT5': 31494}  # dxt1, dxt3, dxt5
                    ft_type = determine_dxt[tex_source]  # from DXT to bitflags
                ft.seek(128)
                ft_stream = ft.read()
            return ft_y, ft_x, ft_stream, ft_type

        def write_image(ft_y, ft_x, ft_stream, ft_type):
            write_string(f, b'GBIX')
            write_integer(f, 8, 0, 0)
            write_string(f, b'PVRT')
            write_integer(f, len(ft_stream) + 40, ft_type)
            write_short(f, ft_y, ft_x)
            write_integer(f, 0, 0, 0, 0, 0, 1, 0, 0)
            f.write(ft_stream)
            write_aligned(f, 16)

        def replace():
            # get users textures, fix and add
            image_offset = []
            write_aligned(f, 16)
            for tex_index in range(self.image_count):
                image_offset.append(f.tell() - self.texture_start)
                tex_name_base = self.texture_path + self.texture_names[tex_index]
                if self.image_naming == "complex":
                    ft = open(tex_name_base + "." + bpy.path.basename(self.file_path) + "." +
                              str(sub_index) + "." + str(tex_index) + ".dds", "rb")
                else:
                    ft = open(tex_name_base + ".dds", "rb")
                ft_y, ft_x, ft_stream, ft_type = read_image(ft)
                ft.close()
                write_image(ft_x, ft_y, ft_stream, ft_type)
            tex_end = f.tell()
            f.seek(self.texture_start + 4)
            for var in range(self.image_count):
                write_integer(f, image_offset[var])
            self.texture_names = []
            f.seek(tex_end)

        self.texture_start, self.image_count, _, _, self.texture_names = \
            read_texture_block_info(self.f)
        replace()
        f.flush()
