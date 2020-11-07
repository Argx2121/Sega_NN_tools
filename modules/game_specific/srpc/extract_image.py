from ...util import *


# read + make textures
class ExtractImage:
    def __init__(self, f: BinaryIO, filepath: str, naming_style: str, file_index: int):
        self.f = f
        self.filepath = filepath
        self.image_naming = naming_style
        self.texture_start = None
        self.image_count = None
        self.texture_offsets = []
        self.texture_names = []
        self.texture_path = bpy.path.abspath(filepath).rstrip(bpy.path.basename(filepath))
        self.tex_y = None
        self.tex_x = None
        self.texture_data = None
        self.texture_files = []
        self.type_byte = None
        self.file_index = file_index

    def execute(self):
        self.texture_start, self.image_count, self.type_byte, self.texture_offsets, self.texture_names = \
            le_read_texture_block_info(self.f)
        self.make_image()
        self.texture_files = [bpy.data.images.load(tex) for tex in self.texture_files]
        return self.texture_files, self.texture_path, self.texture_names, self.type_byte

    def make_image(self):
        f = self.f
        tex_path = self.texture_path

        def dxt(dxt_type, tex_mip=1):
            tex_name_base = tex_path + self.texture_names[texture_index]
            if self.image_naming == "Complex":
                file_name = tex_name_base + "." + bpy.path.basename(self.filepath) + \
                            "." + str(self.file_index) + "." + str(texture_index) + ".dds"
            else:
                file_name: str = tex_name_base + ".dds"
            self.texture_files.append(file_name)
            ft = open(file_name, "wb")
            write_string(ft, b'DDS ')
            # block len, flags, x, y, pitch or linear size, depth, mip map count
            size = self.tex_y * self.tex_x // 2  # is this right
            write_integer(ft, 124, 659463, self.tex_y, self.tex_x, size, 1, tex_mip)
            # reserved block
            write_string(ft, b'TEXTUREFLAGS')
            write_byte(ft, texture_type[0], texture_type[1], 0, 0)
            for _ in range(5):
                write_integer(ft, 0)
            write_string(ft, b'PRTF')  # pc riders texture file lol
            write_integer(ft, 0)
            # pixel format block
            # block len, flags, string, bit count, bit masks (RGBA)
            write_integer(ft, 32, 4)
            write_string(ft, dxt_type)  # DX10 from nv tools
            for _ in range(5):
                write_integer(ft, 0)
            # caps (1 - 4), reserved 2
            write_integer(ft, 4198408)
            for _ in range(4):
                write_integer(ft, 0)

            ft.write(self.texture_data)
            ft.close()

        def dxt1():
            tex_mip = 1
            if tex_bin_1 == "00000101":
                if tex_bin_2 == "01110100":
                    tex_mip = 4
            dxt(b'DXT1', tex_mip)

        def dxt3():
            dxt(b'DXT3')

        def dxt4():
            dxt(b'DXT4')

        def dxt5():
            dxt(b'DXT5')

        def pixel():  # temp until dict implemented
            if tex_bin_2 == "01110001":  # a len = 0?
                if tex_bin_1 == "00000100":
                    write_pixel(read_pixel(8, 8, 8))
                elif tex_bin_1 == "00000101":
                    write_pixel(read_pixel(5, 6, 5))
                else:
                    write_pixel(read_pixel(5, 6, 5))  # jic
            else:
                if tex_bin_1 == "00000100":
                    write_pixel(read_pixel(4, 4, 4, 4))
                elif tex_bin_1 == "00000101":
                    write_pixel(read_pixel(4, 4, 4, 4))
                elif tex_bin_1 == "00000110":
                    write_pixel(read_pixel(8, 8, 8, 8))
                elif tex_bin_1 == "00010101":
                    write_pixel(read_pixel(8, 8, 8, 8))
                else:
                    write_pixel(read_pixel(4, 4, 4, 4))  # just in case

        def read_pixel(r_bits, g_bits, b_bits, a_bits=0):
            # get colours
            pixel_count = self.tex_y * self.tex_x
            colour_list = []
            bit_len = r_bits + g_bits + b_bits + a_bits
            byte_len = bit_len // 8  # 1 byte = 8 bits
            byte_list = []
            for _ in range(pixel_count):  # here's where de swizzling would be handled ig
                byte_list.append(unpack(str(byte_len) + "B", f.read(byte_len)))  # otherwise itd be if 1 or > 1

            if a_bits:
                for i in range(pixel_count):
                    bit_string = ""
                    for byte in byte_list[i]:
                        bit_string = bit_string + format(byte, "08b")
                    colour_list.append(int(bit_string[bit_len - a_bits:bit_len], 2) / (2 ** a_bits))
                    colour_list.append(int(bit_string[0:r_bits], 2) / (2 ** r_bits))
                    colour_list.append(int(bit_string[r_bits:r_bits + g_bits], 2) / (2 ** g_bits))
                    colour_list.append(int(bit_string[r_bits + g_bits:bit_len - a_bits], 2) / (2 ** b_bits))

            else:
                for i in range(pixel_count):
                    bit_string = ""
                    for byte in byte_list[i]:
                        bit_string = bit_string + format(byte, "08b")
                    colour_list.append(int(bit_string[0:r_bits], 2) / (2 ** r_bits))
                    colour_list.append(int(bit_string[r_bits:r_bits + g_bits], 2) / (2 ** g_bits))
                    colour_list.append(int(bit_string[r_bits + g_bits:bit_len - a_bits], 2) / (2 ** b_bits))
                    colour_list.append(1)

            return colour_list

        def write_pixel(colour_list):
            file_name: str = tex_path + self.texture_names[texture_index] + "." + str(texture_index) + ".tiff"
            self.texture_files.append(file_name)
            img = bpy.data.images.new(self.texture_names[texture_index], self.tex_x, self.tex_y, alpha=True)
            img.pixels = colour_list
            img.update()
            img.file_format = "TIFF"
            img.filepath_raw = file_name
            img.save()

        dxt_format = {
            "01110011": dxt1, "01110100": dxt1,
            "01110101": dxt3, "01110110": dxt3, "01110111": dxt3,
            "01111001": dxt4,
            "01111011": dxt5}

        pix_format = {"01110000": pixel, "01110001": pixel}  # pixels still swizzled

        # get the data we need and write image as dds
        # tex index included in case of name double ups
        for texture_index in range(self.image_count):
            texture_offset_current = self.texture_offsets[texture_index]
            f.seek(self.texture_start + texture_offset_current + 20)
            tex_len = read_int(f) - 40
            texture_type = read_byte_tuple(f, 2)
            tex_bin_1 = format(texture_type[0], "08b")
            tex_bin_2 = format(texture_type[1], "08b")
            _, self.tex_x, self.tex_y = read_short_tuple(f, 3)
            f.seek(32, 1)
            if tex_bin_2 not in {"01110000", "01110001"}:
                self.texture_data = (f.read(tex_len))
                dxt_format[tex_bin_2]()
            else:
                self.texture_data = (f.read(tex_len))
                dxt(b'DXT0')  # BREAKS TEXTURE + SAVES BLENDER FROM CRASH
