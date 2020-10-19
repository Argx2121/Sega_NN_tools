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
    class Colour:
        rgba_main: tuple = (0.75, 0.75, 0.75, 1)
        rgba_sub: tuple = (0.75, 0.75, 0.75, 1)
        rgba_highlight: tuple = (0.75, 0.75, 0.75, 1)
        rgba_shadow: tuple = (0.75, 0.75, 0.75, 1)
        shadow_intensity: float = 1

    @dataclass
    class Texture:
        tex_type: str
        ex_type_int: int
        tex_setting: int
        tex_index: int

    @dataclass
    class Material:
        tex_count: int
        colour: tuple
        texture: tuple

    def _info_offsets_type_1(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f) & 15)  # stored: 00010001 (17), is: 0000001 (1) (texture count)
            self.info_offset.append(read_int(f))

    def _info_type_1(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.post_nxif + 8)
            var1, _, var2 = read_multi_ints(f, 3)
            self.colour_offset.append(var1)
            self.texture_offset.append(var2)

    def _colour_type_1(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.post_nxif)
            self.colour_list.append(self.Colour(read_float_tuple(f, 4), read_float_tuple(f, 4),
                                                read_float_tuple(f, 4), read_float_tuple(f, 4), read_float(f)))

    def _texture_type_1(self):
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
                    tex_type, _, tex_set, _ = read_multi_bytes(f, 4)
                    texture_list.append(self.Texture(texture_type[tex_type], tex_type, tex_set, read_int(f)))
                    f.seek(40, 1)
            self.texture_list.append(texture_list)

    def _return_data_type_1(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(self.texture_count[i], self.colour_list[i], self.texture_list[i]))
        return material_list

    def _info_offsets_type_2(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(len(bin(read_short(f, ">"))) - 2)  # 0b1 = 1 tex, 0b11 = 2, 0b111 = 3 etc
            f.seek(2, 1)
            self.colour_offset.append(read_int(f, ">"))

    def _colour_texture_type_1(self):
        f = self.f  # TODO see texture types
        texture_type = {1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse"}
        for offset in self.colour_offset:
            f.seek(offset + self.post_nxif + 4)
            self.colour_list.append(self.Colour(
                read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">")))
            f.seek(36, 1)
            texture_list = []
            for t_count in self.texture_count:
                for _ in range(t_count):
                    _, tex_set, _, tex_type = read_multi_bytes(f, 4)
                    tex_index = read_int(f, ">")
                    f.seek(12, 1)
                    texture_list.append(self.Texture(texture_type[tex_type], tex_set, tex_index))
            self.texture_list.append(texture_list)

    def xbox(self):  # [two offsets] all colour blocks, all texture blocks
        self._info_offsets_type_1()
        self._info_type_1()
        self._colour_type_1()
        self._texture_type_1()
        return self._return_data_type_1()

    def gamecube(self):  # [one offset] colour block, texture block
        self._info_offsets_type_2()
        self._colour_texture_type_1()
        return self._return_data_type_1()
