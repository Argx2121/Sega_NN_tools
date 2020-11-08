from dataclasses import dataclass

from ...util import *


class Read:
    def __init__(self, f: BinaryIO, post_nxif: int, material_count: int):
        self.f = f
        self.post_nxif = post_nxif
        self.material_count = material_count
        self.texture_count = []
        self.info_offset = []
        self.colour_offset = []
        self.texture_offset = []
        self.colour_list = []
        self.texture_list = []

    @dataclass
    class Colour:  # there is other data available but we only ise main
        rgba_main: tuple = (0.75, 0.75, 0.75, 1)

    @dataclass
    class Texture:
        tex_type: str
        ex_type_int: int
        tex_setting: int
        tex_index: int

    @dataclass
    class Material:
        tex_count: int
        colour: Any
        texture: Any

    def _le_offsets_1(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f) & 15)  # stored: 00010001 (17), is: 0000001 (1) (texture count)
            self.info_offset.append(read_int(f))

    def _le_offsets_2(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f, ">") >> 4)
            self.info_offset.append(read_int(f))

    def _le_offsets_3(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            var = len(format(read_int(f) >> 1, "b"))
            self.texture_count.append(var)
            self.info_offset.append(read_int(f))

    def _be_offsets_1(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            f.seek(4, 1)
            self.info_offset.append(read_int(f, ">"))

    def _le_offsets_4(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            var = len(format(read_short(f, ">") >> 2, "b"))
            self.texture_count.append(var)
            f.seek(2, 1)
            self.texture_offset.append(read_int(f))

    def _le_info_1(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.post_nxif + 8)
            var1, _, var2 = read_int_tuple(f, 3)
            self.colour_offset.append(var1)
            self.texture_offset.append(var2)

    def _le_info_2(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.post_nxif)
            _, _, var1, _, _, var3, var2 = read_int_tuple(f, 7)
            self.colour_offset.append(var1 + 4)
            self.texture_count.append(var3)
            self.texture_offset.append(var2)

    def _be_info_1(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.post_nxif + 8)
            var = read_int_tuple(f, 5, ">")
            self.colour_offset.append(var[0])
            self.texture_count.append(var[-2])
            self.texture_offset.append(var[-1])

    def _le_colour_1(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.post_nxif)
            self.colour_list.append(self.Colour(read_float_tuple(f, 4)))

    def _be_colour_1(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.post_nxif + 16)
            var = read_float_tuple(f, 4, ">")
            self.colour_list.append(self.Colour((var[1], var[2], var[3], var[0])))

    def _le_texture_1(self):
        # 11 = normals? (sonic 06)
        texture_type = {
            1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse",
            9: "diffuse", 11: "normal"}
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.post_nxif)
                for _ in range(self.texture_count[texture_value]):
                    tex_type, _, tex_set, _ = read_byte_tuple(f, 4)
                    if tex_type in texture_type:
                        var = texture_type[tex_type]
                    else:
                        var = "diffuse"
                    texture_list.append(self.Texture(var, tex_type, tex_set, read_int(f)))
                    f.seek(40, 1)
            self.texture_list.append(texture_list)

    def _be_texture_1(self):
        texture_type = {
            1: "normal", 2: "diffuse", 32: "reflection"
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.post_nxif)
                for _ in range(self.texture_count[texture_value]):
                    tex_set, _, _, tex_type = read_byte_tuple(f, 4, ">")
                    if tex_type in texture_type:
                        var = texture_type[tex_type]
                    else:
                        var = "diffuse"
                    texture_list.append(self.Texture(var, tex_type, tex_set, read_int(f, ">")))
                    f.seek(56, 1)
            self.texture_list.append(texture_list)

    def _le_texture_2(self):
        texture_type = {
            1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse",
            9: "diffuse", 11: "normal"}
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.post_nxif)
                for _ in range(self.texture_count[texture_value]):
                    tex_type, _, tex_set, _ = read_byte_tuple(f, 4)
                    if tex_type in texture_type:
                        var = texture_type[tex_type]
                    else:
                        var = "diffuse"
                    texture_list.append(self.Texture(var, tex_type, tex_set, read_int(f)))
                    f.seek(56, 1)
            elif self.texture_count[texture_value]:
                for _ in range(self.texture_count[texture_value]):
                    texture_list.append(self.Texture("diffuse", 0, 0, 0))
            self.texture_list.append(texture_list)

    def _le_texture_3(self):
        texture_type = {
            1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse",
            9: "diffuse", 11: "normal"}
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.post_nxif + 80)
                for _ in range(self.texture_count[texture_value]):
                    var = read_byte_tuple(f, 6)
                    if var[1] in texture_type:
                        var1 = texture_type[var[1]]
                    else:
                        var1 = "diffuse"
                    texture_list.append(self.Texture(var1, var[1], 0, read_short(f)))
                    f.seek(104, 1)
            self.texture_list.append(texture_list)

    def _return_data_1(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(self.texture_count[i], self.colour_list[i], self.texture_list[i]))
        return material_list

    def _return_data_2(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(self.texture_count[i], self.Colour(), self.texture_list[i]))
        return material_list

    def _colour_texture_type_1(self):
        f = self.f
        texture_type = {1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse"}
        for offset in self.colour_offset:
            f.seek(offset + self.post_nxif + 4)
            self.colour_list.append(self.Colour(read_float_tuple(f, 4, ">")))
            f.seek(68, 1)
            texture_list = []
            for t_count in self.texture_count:
                for _ in range(t_count):
                    _, tex_set, _, tex_type = read_byte_tuple(f, 4)
                    tex_index = read_int(f, ">")
                    f.seek(12, 1)
                    texture_list.append(self.Texture(texture_type[tex_type], tex_type, tex_set, tex_index))
            self.texture_list.append(texture_list)

    def xno(self):
        self._le_offsets_1()
        self._le_info_1()
        self._le_colour_1()
        self._le_texture_1()
        return self._return_data_1()

    def zno(self):
        self._le_offsets_2()
        self._le_info_2()
        self._le_texture_2()
        return self._return_data_2()

    def lno(self):
        self._le_offsets_3()
        self._le_info_2()
        self._le_texture_2()
        return self._return_data_2()

    def sno(self):
        self._le_offsets_4()
        self._le_texture_3()
        return self._return_data_2()

    def eno(self):
        self._be_offsets_1()
        self._be_info_1()
        self._be_colour_1()
        self._be_texture_1()
        return self._return_data_1()
