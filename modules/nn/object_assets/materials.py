from dataclasses import dataclass
from enum import Flag

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "material_count", "texture_count", "info_offset", "colour_offset",
        "texture_offset", "colour_list", "texture_list", "mat_set_list"
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
        self.mat_set_list = []

    @dataclass
    class MaterialSettings:
        __slots__ = ["type", "setting", "index"]
        type: str
        setting: list
        index: int

    @dataclass
    class Colour:  # todo get colour from all types
        __slots__ = ["diffuse", "ambient", "specular", "emission", "specular_value", "shininess"]
        diffuse: tuple
        ambient: tuple
        specular: tuple
        emission: tuple
        specular_value: float
        shininess: float

    @dataclass
    class Texture:
        __slots__ = ["type", "interpolation", "projection", "extension", "space", "index", "alpha", "scale", "uv", "texture_flags"]
        type: str
        interpolation: str
        projection: str
        extension: str
        space: str
        index: int
        alpha: float
        scale: tuple
        uv: int
        texture_flags: Flag

    @dataclass
    class GnoRender:
        blend: Flag
        source: Flag
        destination: Flag
        operation: Flag
        z_mode: Flag
        ref0: Flag
        ref1: Flag
        comp0: Flag
        comp1: Flag
        alpha: Flag

    @dataclass
    class Material:
        __slots__ = ["texture_count", "colour", "texture", "transparency", "mat_flags", "mat_data"]
        texture_count: int
        colour: Any
        texture: Any
        transparency: str
        mat_flags: int
        mat_data: list

    @dataclass
    class GnoMaterial:
        __slots__ = ["texture_count", "colour", "texture", "transparency", "mat_flags", "render", "user"]
        texture_count: int
        colour: Any
        texture: Any
        transparency: str
        mat_flags: int
        render: any
        user: tuple  # die

    def _le_offsets(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 2)[1::2]

    def _be_offsets(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 2, ">")[1::2]

    def _xno_offsets(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f) & 15)
            self.info_offset.append(read_int(f))

    def _sno_offsets(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_short(f, ">") // 4)
            f.seek(2, 1)
            self.texture_offset.append(read_int(f))

    def _uno_offsets(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            self.texture_count.append(read_int(f))
            self.texture_offset.append(read_int(f))

    def _le_offsets_3(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 3)[1::3]

    def _le_offsets_4(self):
        self.info_offset = read_int_tuple(self.f, self.material_count * 4)[2::4]

    def _gno_offsets(self):
        f = self.f
        material_count = self.material_count
        for _ in range(material_count):
            a = format(read_int(f, ">") >> 17, "b").count("1")
            self.texture_count.append(a)
            self.texture_offset.append(read_int(f, ">"))

    def _xno_info(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start + 8)
            var1, _, var2 = read_int_tuple(f, 3)
            self.colour_offset.append(var1)
            self.texture_offset.append(var2)

    def _lno_zno_info(self):
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

    def _ino_lno_info_2(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start)
            _, _, var1, _, _, _, var2, var3 = read_int_tuple(f, 8)
            self.colour_offset.append(var1)
            self.texture_count.append(var2)
            self.texture_offset.append(var3)

    def _ino_lno_info_2_ouya(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start)
            _, _, var1, _, _, _, var2, var3 = read_int_tuple(f, 8)
            self.colour_offset.append(var1)
            self.texture_offset.append(var2)
            self.texture_count.append(var3)

    def _cno_eno_info(self):
        f = self.f
        for offset in self.info_offset:
            f.seek(offset + self.start + 8)
            var = read_int_tuple(f, 5, ">")
            self.colour_offset.append(var[0])
            self.texture_count.append(var[-2])
            self.texture_offset.append(var[-1])

    def _xno_colour(self):
        f = self.f
        for offset in self.colour_offset:
            f.seek(offset + self.start)
            self.colour_list.append(self.Colour(
                read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4), read_float_tuple(f, 4),
                2, read_float(f) / 160)  # maybe just div by 100?
            )

    def _cno_eno_colour(self):
        f = self.f
        for offset in self.colour_offset:  # todo test these
            f.seek(offset + self.start + 4)
            # the material setting here isn't really needed
            #  if they don't use a colour property it is also nulled
            # 2 = all data types
            self.colour_list.append(self.Colour(
                read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"), read_float_tuple(f, 4, ">"),
                read_float_tuple(f, 4, ">"), read_float(f, ">") / 1280, read_float(f, ">")
            ))

    def _cno_texture(self):
        def house_of_the_dead_4_c():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.norm:
                t_type = "normal"
            elif TextureFlags.diff:
                t_type = "diffuse"
            elif TextureFlags.sp:
                t_type = "none"  # "spectacular"  # looks broken
            elif TextureFlags.ref:
                t_type = "none"  # "reflection"  # looks broken
                # t_proj = 'SPHERE'

            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "HouseOfTheDead4_C": house_of_the_dead_4_c,
            "SonicTheHedgehog4EpisodeI_C": house_of_the_dead_4_c, "SonicTheHedgehog4EpisodeII_C": house_of_the_dead_4_c,
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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f, ">")
                    f.seek(4, 1)
                    t_alpha = read_float(f, ">")
                    f.seek(8, 1)
                    t_scale = read_float_tuple(f, 2, ">")
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(32, 1)
            self.texture_list.append(texture_list)

    def _eno_texture(self):
        def sonic_free_riders_e():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.norm:
                t_type = "normal"
            elif TextureFlags.diff:
                t_type = "diffuse"
            elif TextureFlags.ref:
                t_type = "reflection"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_the_hedgehog_4_episode_i_prototype_e():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.norm:
                t_type = "normal"
            elif TextureFlags.diff:
                t_type = "diffuse"
            elif TextureFlags.ref:
                t_type = "reflection"

            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "SonicFreeRiders_E": sonic_free_riders_e,
            "SonicTheHedgehog4EpisodeIPrototype_E": sonic_the_hedgehog_4_episode_i_prototype_e,
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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f, ">")
                    f.seek(4, 1)
                    t_alpha = read_float(f, ">")
                    f.seek(8, 1)
                    t_scale = read_float_tuple(f, 2, ">")
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(32, 1)
            self.texture_list.append(texture_list)

    def _gno_texture(self):
        def super_monkey_ball_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_and_the_black_knight_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            mix_type = texture_flags & 255
            if texture_flags >> 8 & 255 == 2 and mix_type in {71, 2}:
                t_type = "emission"
            elif mix_type == 66:
                t_type = "specular_ref_alpha"
            elif mix_type == 71:
                t_type = "reflection"
            elif mix_type == 1:
                t_type = "diffuse"
            elif mix_type in {9, 73, 66}:
                t_type = "specular"
            if not texture_flags >> 30 & 1:
                pass

            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_and_the_secret_rings_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"
            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_riders_zero_gravity_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def bleach_shattered_blade_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def ghost_squad_g():  # needs material rework for proper support
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if texture_flags == 1074528513 or texture_flags == 1075314945:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_riders_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"
            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_unleashed_g():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.multiply:
                t_type = "diffuse"
            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "SuperMonkeyBallStepAndRoll_G": super_monkey_ball_g,
            "SonicAndTheBlackKnight_G": sonic_and_the_black_knight_g,
            "SonicAndTheSecretRings_G": sonic_and_the_secret_rings_g,
            "SonicRidersZeroGravity_G": sonic_riders_zero_gravity_g,
            "BleachShatteredBlade_G": bleach_shattered_blade_g,
            "SonicRiders_G": sonic_riders_g,
            "SonicUnleashed_G": sonic_unleashed_g,
            "SuperMonkeyBallBananaBlitz_G": super_monkey_ball_g,
            "GhostSquad_G": ghost_squad_g,
        }
        f = self.f

        for offset, count in zip(self.texture_offset, self.texture_count):
            texture_list = []
            f.seek(offset + self.start)
            # 0 = no specular 1 = all, 00 02 00 00 = boolean mesh
            mat_type = unpack(">i", f.read(4))[0]  # blender needs int.. not unit..

            diffuse = read_float_tuple(f, 4, ">")
            ambient = list(read_float_tuple(f, 3, ">"))
            ambient += [1.0]
            specular = list(read_float_tuple(f, 3, ">"))
            specular += [1.0]
            emission = (0, 0, 0, 1)
            specular_value = read_float(f, ">")
            shininess = read_float(f, ">")

            # speclevel and specgloss
            self.colour_list.append(self.Colour(
                diffuse, tuple(ambient), tuple(specular), emission, specular_value, shininess
            ))

            mat_data = self.GnoRender(
                *unpack(">5i", f.read(20)), *unpack(">4B", f.read(4))[:2], *unpack(">3i", f.read(12)))

            user = unpack(">i", f.read(4))[0]

            self.mat_set_list.append((mat_type, mat_data, user))

            for index in range(count):
                texture_flags = read_int(f, ">")

                class TextureFlags(Flag):
                    # ---- NEW DATA ----
                    # byte 1
                    ignore_uv_offset = texture_flags >> 30 & 1

                    # byte 2
                    # uv wrapping modes
                    clampu = texture_flags >> 16 & 1
                    clampv = texture_flags >> 17 & 1
                    repeatu = texture_flags >> 18 & 1
                    repeatv = texture_flags >> 19 & 1
                    mirroru = texture_flags >> 20 & 1
                    mirrorv = texture_flags >> 21 & 1

                    # byte 3
                    # vector type (reflection or uv map - multiple cannot be set)
                    reflection = texture_flags >> 13 & 1
                    uv4 = texture_flags >> 11 & 1
                    uv3 = texture_flags >> 10 & 1
                    uv2 = texture_flags >> 9 & 1
                    uv1 = texture_flags >> 8 & 1

                    # byte 4
                    # mixing
                    # the colour might be a bit different in blender because the colour space is different
                    multiply_shading = texture_flags >> 6 & 1
                    subtract_bit = texture_flags >> 3 & 1
                    add_bit = texture_flags >> 2 & 1
                    mix_bit = texture_flags >> 1 & 1
                    multiply_bit = texture_flags >> 0 & 1
                    # please note that specifying a specular texture starts a new node chain
                    multiply = multiply_bit and not mix_bit and not add_bit and not subtract_bit
                    decal = not multiply_bit and mix_bit and not add_bit and not subtract_bit
                    replace = multiply_bit and mix_bit and not add_bit and not subtract_bit
                    blend = not multiply_bit and not mix_bit and add_bit and not subtract_bit
                    pass_clear = multiply_bit and not mix_bit and add_bit and not subtract_bit
                    alpha_tex = not multiply_bit and mix_bit and add_bit and not subtract_bit  # next texture uses this ones alpha
                    decal_2 = multiply_bit and mix_bit and add_bit and not subtract_bit
                    subtract = not multiply_bit and not mix_bit and not add_bit and subtract_bit
                    specular = multiply_bit and not mix_bit and not add_bit and subtract_bit
                    specular2 = not multiply_bit and mix_bit and not add_bit and subtract_bit
                    add = multiply_bit and mix_bit and not add_bit and subtract_bit
                    subtract_2 = not multiply_bit and not mix_bit and add_bit and subtract_bit  # used if its not the first image

                    # unused:
                    # unknown = multiply_bit and not mix_bit and add_bit and subtract_bit  # 0xD
                    # unknown8 = not multiply_bit and mix_bit and add_bit and subtract_bit  # 0xE
                    # unknown0 = multiply_bit and mix_bit and add_bit and subtract_bit  # 0xF
                    # unknown15 = not multiply_bit and not mix_bit and not add_bit and not subtract_bit  # 0

                t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                t_index = read_int(f, ">")
                t_scale = read_float_tuple(f, 2, ">")
                t_alpha = read_float(f, ">")
                t_uv = len(format(texture_flags >> 8 & 255, "b"))

                texture_list.append(self.Texture(
                    t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))

            if self.format_type == "SonicAndTheBlackKnight_G":
                tex_formats = [a.type for a in texture_list]
                if tex_formats.count("diffuse") > 1:
                    mask_ind = tex_formats[tex_formats.index("diffuse") + 1::].index("diffuse")
                    tex_format = tex_formats[tex_formats.index("diffuse") + 1::][mask_ind - 1] + "_mask"
                    texture_list[mask_ind + len(tex_formats) -
                                 len(tex_formats[tex_formats.index("diffuse") + 1::])].type = tex_format
                if tex_formats.count("reflection") > 1:
                    texture_list[tex_formats.index("reflection")].type = "reflection_multi"
            self.texture_list.append(texture_list)

    def _ino_texture(self):
        def sonic_4_episode_1_i():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte2bit1:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "SonicTheHedgehog4EpisodeI_I": sonic_4_episode_1_i,
            "SonicTheHedgehog4EpisodeIPre2016_I": sonic_4_episode_1_i,
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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f)
                    # unfortunately I cannot test this so these are assumptions
                    f.seek(16, 1)
                    t_alpha = 1
                    t_scale = read_float_tuple(f, 2)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))
                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(20, 1)
            self.texture_list.append(texture_list)

    def _lno_texture(self):
        def house_of_the_dead_4_l():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit1:
                t_type = "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def loving_deads_house_of_the_dead_ex_l():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit1:
                t_type = "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_the_hedgehog4_episode_ii_l():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit1:
                t_type = "normal"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "SonicTheHedgehog4EpisodeII_L": sonic_the_hedgehog4_episode_ii_l,
            "SonicTheHedgehog4EpisodeIIOuya_L": sonic_the_hedgehog4_episode_ii_l,
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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f)
                    f.seek(4, 1)
                    t_alpha = read_float(f)
                    f.seek(8, 1)
                    t_scale = read_float_tuple(f, 2)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(32, 1)
            self.texture_list.append(texture_list)

    def _sno_texture(self):
        def sonic_riders_zero_gravity_s():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte2bit1:
                t_type = "diffuse"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sega_superstars_s():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte2bit1:
                t_type = "diffuse"
            if TextureFlags.byte2bit2:
                t_type = "wx"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"

            return t_type, t_interp, t_proj, t_ext, t_space

        def sega_ages_2500_series_vol_5_golden_axe_s():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte2bit1:
                t_type = "diffuse"
            elif TextureFlags.byte2bit3:
                t_type = "reflection"

            return t_type, t_interp, t_proj, t_ext, t_space

        format_dict = {
            "SonicRidersZeroGravity_S": sonic_riders_zero_gravity_s,
            "SegaSuperstars_S": sega_superstars_s,
            "SegaAges2500SeriesVol5GoldenAxe_S": sega_ages_2500_series_vol_5_golden_axe_s,
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
                        byte2bit2 = texture_flags >> 17 & 1
                        byte2bit1 = texture_flags >> 16 & 1

                        # byte 3

                        # byte 4

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    f.seek(2, 1)
                    t_index = read_short(f)
                    t_alpha = 1
                    t_scale = (1, 1)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))
                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(104, 1)
            self.texture_list.append(texture_list)

    def _uno_texture(self):
        def k_on_after_school_live_u():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            # Only seen diffuse
            if TextureFlags.byte1bit1 and TextureFlags.byte1bit2 and TextureFlags.byte1bit4:
                t_type = "diffuse"

            return t_type, t_interp, t_proj, t_ext, t_space

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
                        byte1bit1 = texture_flags >> 0 & 1  # 00000001
                        byte1bit2 = texture_flags >> 1 & 1  # 00000010
                        byte1bit3 = texture_flags >> 2 & 1  # 00000100
                        byte1bit4 = texture_flags >> 3 & 1  # 00001000

                        # byte 2

                        # byte 3

                        # byte 4

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f)
                    t_alpha = read_float(f)
                    t_scale = (1, 1)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(12, 1)
            self.texture_list.append(texture_list)

    def _xno_texture(self):
        def sonic_riders_x():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit1 and TextureFlags.diffuse_2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit3 and TextureFlags.reflection_2 and not TextureFlags.byte1bit2:
                t_type = "reflection"
            elif TextureFlags.byte1bit4:
                t_type = "none"

            if TextureFlags.clamp_y or TextureFlags.clamp_x:
                t_ext = "EXTEND"
            return t_type, t_interp, t_proj, t_ext, t_space

        def sonic_2006_x():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit4:
                t_type = "none"
            elif TextureFlags.byte1bit1 and TextureFlags.byte1bit2:
                t_type = "diffuse"
            elif TextureFlags.byte1bit1 and TextureFlags.byte1bit3:
                t_type = "spectacular"
            elif TextureFlags.byte1bit2 and TextureFlags.byte1bit3:  # 6
                t_type = "none"  # normal does 5 and 6 so if more than one image with 5 ignore the one that also has 6
            elif TextureFlags.byte1bit1 and not TextureFlags.byte1bit2 and not TextureFlags.byte1bit3:
                t_type = "diffuse"

            if TextureFlags.clamp_y or TextureFlags.clamp_x:
                t_ext = "EXTEND"
            return t_type, t_interp, t_proj, t_ext, t_space

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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f)
                    f.seek(8, 1)
                    t_alpha = read_float(f)
                    t_scale = (1, 1)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(28, 1)

                if self.format_type == "Sonic2006_X":
                    tex_formats = [a.type for a in texture_list]
                    if tex_formats.count("spectacular") > 1:
                        texture_list[tex_formats.index("spectacular") + 1].type = "normal"
                        texture_list[tex_formats.index("spectacular") + 1].space = "world"
                    while tex_formats.count("spectacular") > 0:
                        texture_list[tex_formats.index("spectacular")].type = "none"
                        tex_formats = [a.type for a in texture_list]
            self.texture_list.append(texture_list)

    def _zno_texture(self):
        def sonic_4_episode_1_z():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
            if TextureFlags.byte1bit3:
                t_type = "none"
            elif TextureFlags.byte1bit2:
                t_type = "diffuse"
            # unsure how to use shading
            return t_type, t_interp, t_proj, t_ext, t_space

        def transformers_human_alliance_z():
            # the normal maps are channel packed so they can't be added
            # todo yes they can
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
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
            return t_type, t_interp, t_proj, t_ext, t_space

        def sega_golden_gun_z():
            t_type, t_interp, t_proj, t_ext, t_space = "none", "Linear", "FLAT", "REPEAT", "TANGENT"
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
            return t_type, t_interp, t_proj, t_ext, t_space

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

                    t_type, t_interp, t_proj, t_ext, t_space = format_dict[self.format_type]()
                    t_index = read_int(f)
                    f.seek(4, 1)
                    t_alpha = read_float(f)
                    f.seek(8, 1)
                    t_scale = read_float_tuple(f, 2)
                    t_uv = len(format(texture_flags >> 8 & 255, "b"))

                    texture_list.append(self.Texture(
                        t_type, t_interp, t_proj, t_ext, t_space, t_index, t_alpha, t_scale, t_uv, TextureFlags))
                    f.seek(32, 1)
            self.texture_list.append(texture_list)

    def _return_data_1(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(
                self.texture_count[i], self.colour_list[i], self.texture_list[i], "OPAQUE", 0, []))
        return material_list

    def _return_data_2(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.Material(
                self.texture_count[i],
                self.Colour(
                    (0.75, 0.75, 0.75, 1), (0.75, 0.75, 0.75, 1), (0.9, 0.9, 0.9, 1), (0, 0, 0, 1), 0.2, 2),
                self.texture_list[i], "OPAQUE", 0, []))
        return material_list

    def _return_data_3(self):
        material_list = []
        for i in range(self.material_count):
            material_list.append(self.GnoMaterial(
                self.texture_count[i], self.colour_list[i], self.texture_list[i], "OPAQUE", *self.mat_set_list[i]))
        return material_list

    def cno(self):
        self._be_offsets()
        self._cno_eno_info()
        self._cno_eno_colour()
        self._cno_texture()
        return self._return_data_1()

    def eno(self):
        self._be_offsets()
        self._cno_eno_info()
        self._cno_eno_colour()
        self._eno_texture()
        return self._return_data_1()

    def gno(self):
        self._gno_offsets()
        self._gno_texture()
        return self._return_data_3()

    def ino(self):
        if self.format_type == "SonicTheHedgehog4EpisodeI_I":
            self._le_offsets_3()
            self._ino_lno_info_2()
        else:
            self._le_offsets()
            self._le_info_3()
        self._ino_texture()
        return self._return_data_2()

    def lno(self):
        self._le_offsets()
        self._lno_zno_info()
        self._lno_texture()
        return self._return_data_2()

    def lno_s4e2(self):
        self._le_offsets_4()
        self._ino_lno_info_2()
        self._lno_texture()
        return self._return_data_2()

    def lno_s4e2ouya(self):
        self._le_offsets()
        self._ino_lno_info_2_ouya()
        self._lno_texture()
        return self._return_data_2()

    def sno(self):
        self._sno_offsets()
        self._sno_texture()
        return self._return_data_2()

    def uno(self):
        self._uno_offsets()
        self._uno_texture()
        return self._return_data_2()

    def xno(self):
        self._xno_offsets()
        self._xno_info()
        self._xno_colour()
        self._xno_texture()
        return self._return_data_1()

    def zno(self):
        self._le_offsets()
        self._lno_zno_info()
        self._zno_texture()
        return self._return_data_2()


class Write:
    __slots__ = [
        "f", "format_type", "material_data", "nof0_offsets", "mat_offsets"
    ]

    def __init__(self, f, format_type, material_data, nof0_offsets):
        self.f = f
        self.format_type = format_type
        self.material_data = material_data
        self.nof0_offsets = nof0_offsets
        self.mat_offsets = []

    def _xno_colour(self):
        f = self.f
        for mat in self.material_data.material_list:
            self.mat_offsets.append((f.tell(), 0, 0))
            for a in mat.diffuse:
                write_float(f, "<", a)
            f.seek(-4, 1)
            write_float(f, "<", mat.alpha)
            write_float(f, "<", 0.7529413, 0.7529413, 0.7529413, 1, 0.9, 0.9, 0.9, 1, 0, 0, 0, 1, 32, 0, 0, 0)

    def _zno_colour(self):
        f = self.f
        for mat in self.material_data.material_list:
            self.mat_offsets.append((f.tell(), 0, 0))
            write_integer(f, "<", 2)  # unsure
            for a in mat.diffuse:
                write_float(f, "<", a)
            f.seek(-4, 1)
            write_float(f, "<", mat.alpha)
            write_float(f, "<", 0.7529413, 0.7529413, 0.7529413, 1, 0.0, 0.0, 0.0, 1, 1, 1, 1, 0, 8, 1)

    def _xno_unknown(self):
        f = self.f
        offset = f.tell()
        self.mat_offsets = [[a[0], offset, 0] for a in self.mat_offsets]
        write_integer(f, "<", 1, 770, 771, 0, 32774, 0, 1, 516, 0, 1, 515, 1, 0, 0, 0, 0)

    def _zno_unknown(self):
        f = self.f
        offset = f.tell()
        self.mat_offsets = [[a[0], offset, 0] for a in self.mat_offsets]
        write_integer(f, "<", 25, 393221, 393221, 0, 352649217, 262149, 0)

    def _gno_texture_simple(self):
        f = self.f
        textures = self.material_data.texture_list
        # evil cringe society

        for mat in self.material_data.material_list:
            self.mat_offsets.append(f.tell())
            mat_flags = 0
            if mat.boolean:
                mat_flags = mat_flags | 131072
            if mat.unlit:
                mat_flags = mat_flags | 256
            if mat.v_col:
                mat_flags = mat_flags | 1

            if not mat.unlit and not mat.boolean:
                mat_flags = mat_flags | 16777216

            write_integer(f, ">", mat_flags)
            for a in mat.diffuse:
                write_float(f, ">", a)
            f.seek(-4, 1)
            write_float(f, ">", mat.alpha)
            write_float(f, ">", 0.7529413, 0.7529413, 0.7529413, 0.9, 0.9, 0.9, 2, 0.3)

            write_integer(f, ">", 1, 4, 5, 5, 2, 0, 6, 7, 0, 0)
            tex_types = [a.type for a in mat.texture_list]
            if "DiffuseTexture" in tex_types and tex_types.index("DiffuseTexture"):
                # this means its not at index 0
                # which will mess up shading
                old_data = mat.texture_list.pop(tex_types.index("DiffuseTexture"))
                mat.texture_list.insert(0, old_data)

            for image in mat.texture_list:
                if image.type == "DiffuseTexture":
                    write_integer(f, ">", 1074528513)
                    # write index
                    write_integer(f, ">", textures.index(image.name.image.filepath))
                    write_integer(f, ">", 2147483648, 0)
                    write_float(f, ">", 1)
                elif image.type == "ReflectionTexture":
                    write_integer(f, ">", 1074536452)
                    # write index
                    write_integer(f, ">", textures.index(image.name.image.filepath))
                    write_integer(f, ">", 2147483648, 0)
                    write_float(f, ">", 1)
                elif image.type == "EmissionTexture":
                    if len(mat.texture_list) > 1:
                        write_integer(f, ">", 1074528516)
                    else:
                        write_integer(f, ">", 1074528514)
                    # write index
                    write_integer(f, ">", textures.index(image.name.image.filepath))
                    write_integer(f, ">", 2147483648, 0)
                    write_float(f, ">", 1)

    def _gno_texture_complex(self):
        f = self.f
        textures = self.material_data.texture_list

        for mat in self.material_data.material_list:
            self.mat_offsets.append(f.tell())
            if mat.override_mat:
                mat_flags = mat.mat_flags
            else:
                mat_flags = 0
                if mat.v_col == 0:
                    mat_flags |= 1
                if mat.backface_off:
                    mat_flags |= 32
                if mat.unlit:
                    mat_flags |= 256
                if mat.ignore_depth:
                    mat_flags |= 65536
                if mat.dont_write_depth:
                    mat_flags |= 131072
                if mat.blend_method == "Alpha Clip":  # cutout
                    mat_flags |= 262144
                if mat.has_spec:
                    mat_flags |= 16777216

            write_integer(f, ">", mat_flags)
            write_float(f, ">", *mat.diffuse[0:3], mat.alpha)
            write_float(f, ">", *mat.ambient[0:3])
            write_float(f, ">", *mat.specular[0:3], mat.specular_value, mat.shininess)

            write_integer(f, ">", mat.blend_type, mat.source_fact, mat.dest_fact, mat.blend_op, mat.z_mode)
            write_byte(f, ">", mat.ref0, mat.ref1, 0, 0)
            write_integer(f, ">", mat.comp0, mat.comp1, mat.alpha_op)
            f.write(pack(">i", mat.user))

            image_count = 0  # subtract moment

            for image in mat.texture_list:
                image_flags = 0
                if image.uv_offset[0] == image.uv_offset[1] == 0:
                    image_flags |= 1073741824

                if image.u_wrap == 0:
                    image_flags |= 65536
                elif image.u_wrap == 2:
                    image_flags |= 1048576
                else:  # elif image.u_wrap == 1:
                    image_flags |= 262144
                if image.v_wrap == 0:
                    image_flags |= 131072
                elif image.v_wrap == 2:
                    image_flags |= 2097152
                else:  # elif image.v_wrap == 1:
                    image_flags |= 524288

                if image.reflection:
                    image_flags |= 8192
                elif image.uv_map == 0:
                    image_flags |= 256
                elif image.uv_map == 1:
                    image_flags |= 512
                elif image.uv_map == 2:
                    image_flags |= 1024
                elif image.uv_map == 3:
                    image_flags |= 2048

                mix_types = {
                    '_NN_RGB_MULTI': 1, "_NN_RGB_DECAL": 2, '_NN_RGB_REPLACE': 3, "_NN_RGB_BLEND": 4,
                    '_NN_RGB_PASS': 5, "_NN_RGB_ALPHA": 6, '_NN_RGB_DECAL_2': 7,
                    '_NN_RGB_ADD': 11, "_NN_RGB_SPEC": 9, '_NN_RGB_SPEC_2': 10,
                }

                if image.mix_type != "_NN_RGB_SUB":
                    image_flags |= mix_types[image.mix_type]
                else:
                    if image_count == 0:
                        image_flags |= 8
                    else:
                        image_flags |= 12

                write_integer(f, ">", image_flags)
                write_integer(f, ">", textures.index(image.name.image.filepath))
                write_float(f, ">", *image.uv_offset[:2])
                write_float(f, ">", image.col_2_multi)
                image_count += 1

    def _xno_texture(self):
        f = self.f
        textures = self.material_data.texture_list
        # todo way to represent material as flat

        for i, mat in enumerate(self.material_data.material_list):
            self.mat_offsets[i][2] = f.tell()
            tex_types = [a.type for a in mat.texture_list]
            if "DiffuseTexture" in tex_types and tex_types.index("DiffuseTexture"):
                # this means its not at index 0
                # which will fuck up shading
                old_data = mat.texture_list.pop(tex_types.index("DiffuseTexture"))
                mat.texture_list.insert(0, old_data)

            for image in mat.texture_list:
                if image.type == "DiffuseTexture":
                    diff_flags = 1074528513
                    if "ReflectionTexture" in tex_types:
                        diff_flags = diff_flags | 3
                    write_integer(f, "<", diff_flags)
                    # write index
                    write_integer(f, "<", textures.index(image.name.image.filepath))
                    write_float(f, "<", 0, 0, 1, 0)
                    write_integer(f, "<", 65540, 0, 0, 0, 0, 0)
                elif image.type == "ReflectionTexture":
                    write_integer(f, "<", 1074536452)
                    # write index
                    write_integer(f, "<", textures.index(image.name.image.filepath))
                    write_float(f, "<", 0, 0, 1, 0)
                    write_integer(f, "<", 65540, 0, 0, 0, 0, 0)
                    # yes riders does suck
                    write_integer(f, "<", 1074536454)
                    # write index
                    write_integer(f, "<", textures.index(image.name.image.filepath))
                    write_float(f, "<", 0, 0, 1, 0)
                    write_integer(f, "<", 65540, 0, 0, 0, 0, 0)
            if "ReflectionTexture" in tex_types:
                mat.texture_list.append(mat.texture_list[tex_types.index("ReflectionTexture")])

    def _zno_texture(self):
        f = self.f
        textures = self.material_data.texture_list
        # todo way to represent material as flat

        for i, mat in enumerate(self.material_data.material_list):
            self.mat_offsets[i][2] = f.tell()
            tex_types = [a.type for a in mat.texture_list]
            if "DiffuseTexture" in tex_types and tex_types.index("DiffuseTexture"):
                # this means its not at index 0
                # which will fuck up shading
                old_data = mat.texture_list.pop(tex_types.index("DiffuseTexture"))
                mat.texture_list.insert(0, old_data)

            for image in mat.texture_list:
                if image.type == "DiffuseTexture":
                    diff_flags = 1610612738
                    if "ReflectionTexture" in tex_types:
                        diff_flags = diff_flags | 3
                    write_integer(f, "<", diff_flags)
                    # write index
                    write_integer(f, "<", textures.index(image.name.image.filepath))
                    write_float(f, "<", 0, 1, 0, 0, 1, 1)
                    write_integer(f, "<", 65537, 0, 0, 0, 0, 0, 0, 0)
                elif image.type == "ReflectionTexture":
                    continue
                    # write_integer(f, "<", 1074536452)
                    # # write index
                    # write_integer(f, "<", textures.index(image.name.image.filepath))
                    # write_float(f, "<", 0, 0, 1, 0)
                    # write_integer(f, "<", 65540, 0, 0, 0, 0, 0)
                    # # yes riders does suck
                    # write_integer(f, "<", 1074536454)
                    # # write index
                    # write_integer(f, "<", textures.index(image.name.image.filepath))
                    # write_float(f, "<", 0, 0, 1, 0)
                    # write_integer(f, "<", 65540, 0, 0, 0, 0, 0)
            if "ReflectionTexture" in tex_types:
                mat.texture_list.append(mat.texture_list[tex_types.index("ReflectionTexture")])

    def _xno_info(self):
        f = self.f
        new_off = []
        for offset, mat in zip(self.mat_offsets, self.material_data.material_list):
            new_off.append(f.tell())
            a = 16777248  # todo its the same concept :flushed:
            if mat.v_col:
                a = a | 16
            write_integer(f, "<", a, 0)
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[0])
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[1])
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[2])
            write_integer(f, "<", 0, 0, 0)
        self.mat_offsets = new_off

    def _zno_info(self):
        f = self.f
        new_off = []
        for offset, mat in zip(self.mat_offsets, self.material_data.material_list):
            new_off.append(f.tell())
            a = 16777248  # todo its the same concept :flushed:
            # todo all of these are temp hehe
            if mat.v_col:
                a = a | 16
            write_integer(f, "<", 0, 0)
            # 0, 0 (idk)
            # mat colour off, funny data off,
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[0])
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[1])
            # two flag type ints probably
            write_integer(f, "<", 2, 1)
            # texture offset, texture count
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", offset[2])
            write_integer(f, "<", len(mat.texture_list))
        self.mat_offsets = new_off

    def _gno_offsets(self):
        f = self.f
        for a, b in zip(self.material_data.material_list, self.mat_offsets):
            a = len(a.texture_list)
            a = 255 >> (7 - a)
            write_short(f, ">", a, 65535)
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", b)

    def _xno_offsets(self):
        f = self.f
        for a, b in zip(self.material_data.material_list, self.mat_offsets):
            a = len(a.texture_list)
            if a:
                a = 16 | a
            write_integer(f, "<", a)
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", b)

    def _zno_offsets(self):
        f = self.f
        for a in self.mat_offsets:
            write_integer(f, ">", 48)  # haha epic
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", a)

    def gno(self):
        if self.material_data.simple:
            self._gno_texture_simple()
        else:
            self._gno_texture_complex()
        material_offset = self.f.tell()
        self._gno_offsets()
        return material_offset, self.nof0_offsets

    def xno(self):
        self._xno_colour()
        self._xno_unknown()
        self._xno_texture()
        self._xno_info()
        material_offset = self.f.tell()
        self._xno_offsets()
        return material_offset, self.nof0_offsets

    def zno(self):
        self._zno_colour()
        self._zno_unknown()
        self._zno_texture()
        self._zno_info()
        material_offset = self.f.tell()
        self._zno_offsets()
        return material_offset, self.nof0_offsets
