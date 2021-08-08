from dataclasses import dataclass
from enum import Flag

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "material_count", "texture_count", "info_offset", "colour_offset",
        "texture_offset", "colour_list", "texture_list"
    ]

    def __init__(self, var, material_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.material_count = material_count
        self.texture_count = []
        self.info_offset = []
        self.colour_offset = []
        self.texture_offset = []
        self.colour_list = []
        self.texture_list = []

    @dataclass
    class MaterialSettings:
        __slots__ = ["type", "setting", "index"]
        type: str
        setting: list
        index: int

    @dataclass
    class Colour:  # there is other info available but we only use these
        __slots__ = ["colour", "alpha"]
        colour: tuple
        alpha: float

    @dataclass
    class Texture:
        __slots__ = ["type", "setting", "index"]
        type: str
        setting: list
        index: int

    @dataclass
    class Material:
        __slots__ = ["texture_count", "colour", "texture"]
        texture_count: int
        colour: Any
        texture: Any

    def _le_offsets_1(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 2)[1::2]

    def _be_offsets_1(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 2, ">")[1::2]

    def _le_offsets_2(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f) & 15)
            self.info_offset.append(read_int(f))

    def _le_offsets_3(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            var = len(format(read_short(f, ">") >> 2, "b"))
            self.texture_count.append(var)
            f.seek(2, 1)
            self.texture_offset.append(read_int(f))

    def _le_offsets_4(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f))
            self.texture_offset.append(read_int(f))

    def _le_info_1(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start + 8)
            var1, _, var2 = read_int_tuple(f, 3)
            self.colour_offset.append(var1)
            self.texture_offset.append(var2)

    def _le_info_2(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start)
            _, _, var1, _, _, var2, var3 = read_int_tuple(f, 7)
            self.colour_offset.append(var1 + 4)
            self.texture_count.append(var2)
            self.texture_offset.append(var3)

    def _le_info_3(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start)
            _, _, var1, _, var2, var3 = read_int_tuple(f, 6)
            self.colour_offset.append(var1)
            self.texture_count.append(var2)
            self.texture_offset.append(var3)

    def _be_info_1(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start + 8)
            var = read_int_tuple(f, 5, ">")
            self.colour_offset.append(var[0])
            self.texture_count.append(var[-2])
            self.texture_offset.append(var[-1])

    def _le_colour_1(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.start)
            self.colour_list.append(self.Colour(read_float_tuple(f, 3), read_float(f)))

    def _be_colour_1(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.start + 16)
            var_1 = read_float(f, ">")
            var = read_float_tuple(f, 3, ">")
            self.colour_list.append(self.Colour(var, var_1))

    def _cno_texture(self):
        def house_of_the_dead_4_c():
            t_type = "none"
            t_settings = []
            if TextureFlags.norm:
                t_type = "normal"
            elif TextureFlags.diff:
                t_type = "diffuse"
            elif TextureFlags.sp:
                t_type = "none"  # "spectacular"  # looks broken
            elif TextureFlags.ref:
                t_type = "none"  # "reflection"  # looks broken

            return t_type, t_settings

        format_dict = {
            "HouseOfTheDead4_C": house_of_the_dead_4_c,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1

                        # byte 2

                        # byte 3
                        duel_p = texture_flags >> 10 & 1  # don't know what to do with this
                        rem = texture_flags >> 11 & 1  # don't know what to do with this

                        # byte 4
                        norm = texture_flags >> 0 & 1
                        diff = texture_flags >> 1 & 1
                        sp = texture_flags >> 3 & 1
                        ref = texture_flags >> 5 & 1

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f, ">")))
                    f.seek(56, 1)
            self.texture_list.append(texture_list)

    def _eno_texture(self):
        def sonic_free_riders_e():
            t_type = "none"
            t_settings = []
            if TextureFlags.norm:
                t_type = "normal"
            elif TextureFlags.diff:
                t_type = "diffuse"
            elif TextureFlags.ref:
                t_type = "reflection"

            return t_type, t_settings

        format_dict = {
            "SonicFreeRiders_E": sonic_free_riders_e,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1

                        # byte 2

                        # byte 3

                        # byte 4
                        norm = texture_flags >> 0 & 1
                        diff = texture_flags >> 1 & 1
                        ref = texture_flags >> 5 & 1

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f, ">")))
                    f.seek(56, 1)
            self.texture_list.append(texture_list)

    def _ino_texture(self):
        def sonic_4_episode_1_i():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte2bit1:
                t_type = "diffuse"

            return t_type, t_settings

        format_dict = {
            "Sonic4Episode1_I": sonic_4_episode_1_i,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1

                        # byte 2
                        byte2bit1 = texture_flags >> 16 & 1

                        # byte 3

                        # byte 4

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f)))
                    f.seek(44, 1)
            self.texture_list.append(texture_list)

    def _lno_texture(self):
        def house_of_the_dead_4_l():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1:
                t_type = "normal"
                t_settings.append("world")
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"

            return t_type, t_settings

        def loving_deads_house_of_the_dead_ex_l():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1:
                t_type = "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"

            return t_type, t_settings

        format_dict = {
            "HouseOfTheDead4_L": house_of_the_dead_4_l,
            "LovingDeadsHouseOfTheDeadEX_L": loving_deads_house_of_the_dead_ex_l,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1
                        byte1bit4 = texture_flags >> 27 & 1  # 00001000
                        byte1bit3 = texture_flags >> 26 & 1  # 00000100
                        byte1bit2 = texture_flags >> 25 & 1  # 00000010
                        byte1bit1 = texture_flags >> 24 & 1  # 00000001

                        # byte 2
                        byte2bit4 = texture_flags >> 19 & 1
                        byte2bit3 = texture_flags >> 18 & 1

                        # byte 3

                        # byte 4

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f)))
                    f.seek(56, 1)
            self.texture_list.append(texture_list)

    def _sno_texture(self):
        def sonic_riders_zero_gravity_s():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte2bit1:
                t_type = "diffuse"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"

            return t_type, t_settings

        format_dict = {
            "SonicRidersZeroGravity_S": sonic_riders_zero_gravity_s,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start + 80)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1

                        # byte 2
                        byte2bit3 = texture_flags >> 18 & 1
                        byte2bit1 = texture_flags >> 16 & 1

                        # byte 3

                        # byte 4

                    var, tex_set = format_dict[self.format_type]()
                    f.seek(2, 1)
                    texture_list.append(self.Texture(var, tex_set, read_short(f)))
                    f.seek(104, 1)
            self.texture_list.append(texture_list)

    def _uno_texture(self):
        def k_on_after_school_live_u():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1:
                t_type = "diffuse"

            return t_type, t_settings

        format_dict = {
            "KOnAfterSchoolLive_U": k_on_after_school_live_u,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start + 184)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1
                        byte1bit4 = texture_flags >> 27 & 1  # 00001000
                        byte1bit3 = texture_flags >> 26 & 1  # 00000100
                        byte1bit2 = texture_flags >> 25 & 1  # 00000010
                        byte1bit1 = texture_flags >> 24 & 1  # 00000001

                        # byte 2

                        # byte 3

                        # byte 4

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f)))
                    f.seek(16, 1)
            self.texture_list.append(texture_list)

    def _xno_texture(self):
        def sonic_riders_x():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1 and TextureFlags.diffuse_2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit3 and TextureFlags.reflection_2 and not TextureFlags.byte1bit2:
                t_type = "reflection"
            elif TextureFlags.byte1bit4:
                t_type = "none"

            if TextureFlags.clamp_y or TextureFlags.clamp_x:
                t_settings.append("clamp")
            return t_type, t_settings

        def sonic_2006_x():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit4:
                t_type = "none"
            elif TextureFlags.byte1bit1 and TextureFlags.byte1bit2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit1 and TextureFlags.byte1bit3:
                t_type = "spectacular"
            elif TextureFlags.byte1bit2 and TextureFlags.byte1bit3:  # 6
                t_type = "none"  # normal does 5 and 6 so if more than one image with 5 ignore the one that also has 6
            elif TextureFlags.byte1bit1 and not TextureFlags.byte1bit2 and not TextureFlags.byte1bit3:
                t_type = "reflection"

            if TextureFlags.clamp_y or TextureFlags.clamp_x:
                t_settings.append("clamp")
            return t_type, t_settings

        format_dict = {
            "SonicRiders_X": sonic_riders_x, "PhantasyStarUniverse_X": sonic_riders_x,  # need more info for psu
            "Sonic2006_X": sonic_2006_x,
        }

        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1
                        byte1bit4 = texture_flags >> 27 & 1  # 00001000 : doesnt use texture
                        byte1bit3 = texture_flags >> 26 & 1  # 00000100 : no shadows, ignores environment colours
                        byte1bit2 = texture_flags >> 25 & 1  # 00000010 : don't use texture or texture settings
                        byte1bit1 = texture_flags >> 24 & 1  # 00000001 : default

                        # byte 2
                        reflection_2 = texture_flags >> 21 & 1  # 00100000 : image reflection
                        diffuse_2 = texture_flags >> 16 & 1  # 00000001 : default

                        # byte 3
                        clamp_x = texture_flags >> 9 & 1  # 00000010 : don't repeat texture x ways (--)
                        clamp_y = texture_flags >> 8 & 1  # 00000001 : don't repeat texture y ways (|)
                        # clamp can be implemented by
                        #  uv map -> separate xyz -> clamp -> combine xyz -> vector (image)
                        #  but not necessary

                        # byte 4
                        not_use_offset = texture_flags >> 6 & 1
                        # 01000000 : don't use texture offset floats right after texture index
                        #  first is x second is y as floats

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f)))
                    f.seek(40, 1)

                if self.format_type == "Sonic2006_X":
                    tex_formats = [a.type for a in texture_list]
                    if tex_formats.count("spectacular") > 1:
                        texture_list[tex_formats.index("spectacular") + 1].type = "normal"
                        texture_list[tex_formats.index("spectacular") + 1].setting.append("world")
            self.texture_list.append(texture_list)

    def _zno_texture(self):
        def sonic_4_episode_1_z():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit3:
                t_type = "none"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"
            # unsure how to use shading
            return t_type, t_settings

        def transformers_human_alliance_z():
            # the normal maps are channel packed so they can't be added
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1:
                t_type = "none"  # "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit4:
                t_type = "spectacular"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"
            elif TextureFlags.byte2bit4:
                t_type = "spectacular"
            return t_type, t_settings

        def sega_golden_gun_z():
            t_type = "none"
            t_settings = []
            if TextureFlags.byte1bit1:
                t_type = "none"  # "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit4:
                t_type = "spectacular"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"
            elif TextureFlags.byte2bit4:
                t_type = "spectacular"
            return t_type, t_settings

        format_dict = {
            "Sonic4Episode1_Z": sonic_4_episode_1_z,
            "TransformersHumanAlliance_Z": transformers_human_alliance_z,
            "SegaGoldenGun_Z": sega_golden_gun_z,
        }
        f = self.f
        material_count = self.material_count
        for texture_value in range(material_count):
            texture_list = []
            texture_offset = self.texture_offset[texture_value]
            if texture_offset:
                f.seek(texture_offset + self.start)
                for _ in range(self.texture_count[texture_value]):
                    texture_flags = read_int(f, ">")

                    class TextureFlags(Flag):
                        # byte 1
                        byte1bit4 = texture_flags >> 27 & 1  # 00001000
                        byte1bit3 = texture_flags >> 26 & 1  # 00000100
                        byte1bit2 = texture_flags >> 25 & 1  # 00000010
                        byte1bit1 = texture_flags >> 24 & 1  # 00000001

                        # byte 2
                        byte2bit4 = texture_flags >> 19 & 1
                        byte2bit3 = texture_flags >> 18 & 1

                        # byte 3

                        # byte 4

                    var, tex_set = format_dict[self.format_type]()

                    texture_list.append(self.Texture(var, tex_set, read_int(f)))
                    if self.format_type == "Sonic4Episode1_Z":
                        f.seek(40, 1)
                    else:
                        f.seek(56, 1)
            self.texture_list.append(texture_list)

    def _be_colour_texture_type_1(self):
        f = self.f
        texture_type = {1: "diffuse", 2: "diffuse", 3: "diffuse", 4: "reflection", 5: "diffuse", 6: "diffuse"}
        for offset in self.colour_offset:
            f.seek(offset + self.start + 4)
            self.colour_list.append(self.Colour(read_float_tuple(f, 3, ">"), read_float(f, ">")))
            f.seek(68, 1)
            texture_list = []
            for t_count in self.texture_count:
                for _ in range(t_count):
                    _, tex_set, _, tex_type = read_byte_tuple(f, 4)
                    tex_index = read_int(f, ">")
                    f.seek(12, 1)
                    texture_list.append(self.Texture(texture_type[tex_type], [], tex_index))
            self.texture_list.append(texture_list)

    def _return_data_1(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(self.texture_count[i], self.colour_list[i], self.texture_list[i]))
        return material_list

    def _return_data_2(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(
                self.texture_count[i], self.Colour((0.75, 0.75, 0.75), 1), self.texture_list[i]))
        return material_list

    def cno(self):
        self._be_offsets_1()
        self._be_info_1()
        self._be_colour_1()
        self._cno_texture()
        return self._return_data_1()

    def eno(self):
        self._be_offsets_1()
        self._be_info_1()
        self._be_colour_1()
        self._eno_texture()
        return self._return_data_1()

    def ino(self):
        self._le_offsets_1()
        self._le_info_3()
        self._ino_texture()
        return self._return_data_2()

    def lno(self):
        self._le_offsets_1()
        self._le_info_2()
        self._lno_texture()
        return self._return_data_2()

    def sno(self):
        self._le_offsets_3()
        self._sno_texture()
        return self._return_data_2()

    def uno(self):
        self._le_offsets_4()
        self._uno_texture()
        return self._return_data_2()

    def xno(self):
        self._le_offsets_2()
        self._le_info_1()
        self._le_colour_1()
        self._xno_texture()
        return self._return_data_1()

    def zno(self):
        self._le_offsets_1()
        self._le_info_2()
        self._zno_texture()
        return self._return_data_2()
