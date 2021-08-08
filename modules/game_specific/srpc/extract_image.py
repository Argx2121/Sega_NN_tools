from ...util import *


# read + make textures
class ExtractImage:
    def __init__(self, f: BinaryIO, filepath: str):
        self.f = f
        self.filepath = filepath
        self.texture_path = bpy.path.abspath(filepath).rstrip(bpy.path.basename(filepath))
        self.texture_files = []

    def texture_block_info(self):
        f = self.f
        tex_start = f.tell()
        img_count = read_short(f)
        _, image_pad = read_byte_tuple(f, 2)
        texture_offsets = read_int_tuple(f, img_count)
        tex_names_len = (texture_offsets[0] - (4 * img_count + 4 + img_count * image_pad))
        f.seek(tex_start + 4 + img_count * 4 + img_count * image_pad - 1)
        type_byte = read_byte(f)
        texture_bytes = f.read(tex_names_len)
        f.seek(tex_start + 4 + img_count * 4 + img_count * image_pad)
        texture_names = read_str_nulls(f, tex_names_len)[:img_count]
        texture_names = [bpy.path.native_pathsep(t) for t in texture_names]
        return tex_start, img_count, type_byte, texture_offsets, texture_names, texture_bytes

    def execute(self):
        texture_start, image_count, type_byte, texture_offsets, texture_names, texture_bytes = \
            self.texture_block_info()
        self.make_image(texture_start, image_count, texture_offsets, texture_names)
        return self.texture_files, self.texture_path, texture_names, type_byte, texture_bytes

    def make_image(self, texture_start, image_count, texture_offsets, texture_names):
        f = self.f
        tex_path = self.texture_path

        def dxt(dxt_type, tex_mip=1):
            ft = open(file_name, "wb")
            pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
            write_string(ft, b'DDS ')
            # block len, flags, x, y, pitch or linear size, depth, mip map count
            write_integer(ft, "<", 124, 659463, tex_y, tex_x, tex_y * tex_x // 2, 1, 1)  # stored mip count can be wrong
            # reserved block
            # noinspection SpellCheckingInspection
            write_string(ft, b'TEXTUREFLAGS')
            write_byte(ft, "<", tex_bin_1, tex_bin_2)
            ft.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            # noinspection SpellCheckingInspection
            write_string(ft, b'PRTF')  # pc riders texture file
            ft.write(b"\x00\x00\x00\x00")
            # pixel format block
            # block len, flags, string, bit count, bit masks (RGBA)
            write_integer(ft, "<", 32, 4)
            write_string(ft, dxt_type)
            ft.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            # caps (1 - 4), reserved 2
            write_integer(ft, "<", 4198408)
            ft.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

            ft.write(f.read(tex_len))
            ft.close()

        def dxt1():
            tex_mip = 1
            if tex_bin_1 == 5 and tex_bin_2 == 116:
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
            pixel_count = tex_y * tex_x
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
            # file_name: str = tex_path + texture_names[texture_index] + "." + str(texture_index) + ".tiff"
            self.texture_files.append(file_name)
            img = bpy.data.images.new(texture_names[texture_index], tex_x, tex_y, alpha=True)
            img.pixels = colour_list
            img.update()
            img.file_format = "TIFF"
            img.filepath_raw = file_name
            img.save()

        dxt_format = {
            115: dxt1, 116: dxt1,
            117: dxt3, 118: dxt3, 119: dxt3,
            121: dxt4,
            123: dxt5}

        pix_format = {"01110000": pixel, "01110001": pixel}  # pixels still swizzled

        # get the info we need and write image as dds
        # tex index included in case of name double ups
        for texture_index in range(image_count):
            texture_offset_current = texture_offsets[texture_index]
            f.seek(texture_start + texture_offset_current + 20)
            tex_len = read_int(f) - 40
            tex_bin_1, tex_bin_2 = read_byte_tuple(f, 2)
            _, tex_x, tex_y = read_short_tuple(f, 3)
            f.seek(32, 1)

            file_name = tex_path + texture_names[texture_index] + ".dds"
            pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
            self.texture_files.append(file_name)

            if tex_bin_2 >> 1 != 56:
                dxt_format[tex_bin_2]()
            else:
                dxt(b'DXT0')  # BREAKS TEXTURE + SAVES BLENDER FROM CRASH
