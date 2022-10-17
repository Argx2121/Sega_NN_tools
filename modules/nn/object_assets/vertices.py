from dataclasses import dataclass
from enum import Flag
from mathutils import Vector

from ...util import *


@dataclass
class VertexData:
    __slots__ = ["positions", "weights", "bone_list_indices", "normals", "uvs", "wxs", "colours"]
    positions: list
    weights: list
    bone_list_indices: list
    normals: list
    uvs: list
    wxs: list
    colours: list


@dataclass
class MeshData:
    __slots__ = [
        "vertex_block_type", "vertex_block_size", "vertex_count", "vertex_offset",
        "bone_count_complex", "bone_list_complex"
    ]
    vertex_block_type: Any
    vertex_block_size: Any
    vertex_count: int
    vertex_offset: Any
    bone_count_complex: int
    bone_list_complex: tuple


@dataclass
class MeshDataGno:
    __slots__ = [
        "vertex_type", "vertex_count", "vertex_offset",
        "norm_type", "norm_count", "norm_offset",
        "col_type", "col_count", "col_offset",
        "uv_type", "uv_count", "uv_offset",
        "uv2_type", "uv2_count", "uv2_offset",
        "uv3_type", "uv3_count", "uv3_offset",
        "bone_type", "bone_count", "bone_offset",
        "data_bone_type", "data_bone_count", "data_bone_offset",
    ]
    vertex_type: int
    vertex_count: int
    vertex_offset: int
    norm_type: int
    norm_count: int
    norm_offset: int
    col_type: int
    col_count: int
    col_offset: int
    uv_type: int
    uv_count: int
    uv_offset: int
    uv2_type: int
    uv2_count: int
    uv2_offset: int
    uv3_type: int
    uv3_count: int
    uv3_offset: int
    bone_type: int
    bone_count: int
    bone_offset: int
    data_bone_type: int
    data_bone_count: int
    data_bone_offset: int


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "vertex_buffer_count", "vert_info_offset", "vertex_mesh_offset", "mesh_info"
    ]

    def __init__(self, var, vertex_buffer_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.vertex_buffer_count = vertex_buffer_count
        self.vert_info_offset = []
        self.vertex_mesh_offset = []
        self.mesh_info = []

    def _be_offsets(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2, ">")[1::2]

    def _be_offsets_flags(self):
        var = read_int_tuple(self.f, self.vertex_buffer_count * 2, ">")
        self.vert_info_offset = var[1::2]
        return var[0::2]

    def _le_offsets(self):
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2)[1::2]

    def _le_offsets_3(self):
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 3)[1::3]

    def _le_offsets_4(self):
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 4)[2::4]

    def _cno_info(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start)
            block_type_list.append(read_int(f, ">"))
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5, ">")
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)

        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_short_tuple(f, bone_count_list[i], ">")))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _cno_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_normals(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_normals.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_wxs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_wxs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_weights(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    w = data_float[i:i + 3]
                    v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                return off + 12

            def get_weights_with_indices(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4
                    w = data_float[b:b + 3]

                    a = i * block_len + off + 12
                    b1, b2, b3, b4 = data_byte[a:a + 4]
                    v_bones.append((b1, b2, b3, b4))

                    if b4:
                        v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                    elif b3:
                        v_weights.append((w[0], w[1], 1 - w[0] - w[1]))
                    elif b2:
                        v_weights.append((w[0], 1 - w[0]))
                    else:
                        v_weights.append((1,))
                return off + 16

            def house_of_the_dead_4_c():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normals:
                    off = get_normals(off)

                if BitFlags.colours:
                    off += 8

                if BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

            def sonic4():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normals:
                    off = get_normals(off)

                if BitFlags.colours:
                    off += 8

                if BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

            format_dict = {
                "HouseOfTheDead4_C": house_of_the_dead_4_c,
                "SonicTheHedgehog4EpisodeI_C": sonic4, "SonicTheHedgehog4EpisodeII_C": sonic4,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                # 00000000 000?00XU 0000IW0? 0?0??0NP house of the dead 4
                # 00000000 00010010 00001101 01011011
                # either have U or X on - you shouldn't have both
                # order:
                # Pos Weights boneIndices ? Uvs wX ?
                # 00000000 00010001 00000000 00000011 s4e2

                position = block_type & 1
                colours = block_type >> 3 & 1
                uv = block_type >> 16 & 1
                wx = block_type >> 17 & 1
                weights = block_type >> 10 & 1
                weight_indices = block_type >> 11 & 1
                normals = block_type >> 1 & 1

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(">" + str(vertex_buffer_len // 4) + "f", vertex_buffer)

            if BitFlags.weight_indices:
                data_byte = unpack(str(vertex_buffer_len) + "B", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def _eno_info(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start)
            block_type_list.append(unpack(">Q", f.read(8))[0])
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5, ">")
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)

        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_int_tuple(f, bone_count_list[i], ">")))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _eno_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v_uvs.append((data_half[i], - data_half[i + 1] + 1))
                return off + 4

            def get_uvs_float(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_normals(off):
                def to_signed(normals):
                    mask = 0b1000000000
                    return (normals ^ mask) - mask

                div_by = 511

                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v = data_int[i]
                    # 012, 120, 210, 021, 201 // 102
                    v0 = to_signed(v >> 0 & 0b1111111111)
                    v1 = to_signed(v >> 10 & 0b1111111111)
                    v2 = to_signed(v >> 20 & 0b1111111111)
                    v_normals.append(Vector([v0 / div_by, v1 / div_by, v2 / div_by]).normalized())
                return off + 4

            def get_normals_float(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_normals.append(data_float[i:i + 3])
                return off + 12

            def get_weights(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    w = data_float[i:i + 3]
                    v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                return off + 12

            def get_weights_with_indices(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4
                    w = data_float[b:b + 3]

                    a = i * block_len + off + 12
                    b4, b3, b2, b1 = data_byte[a:a + 4]
                    v_bones.append((b1, b2, b3, b4))

                    v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                return off + 16

            def get_weights_bit_index(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4

                    a = (i * block_len + off) + 4
                    b4, b3, b2, b1 = data_byte[a:a + 4]
                    v_bones.append((b1, b2, b3, b4))

                    v = data_int_un[b]
                    # 012, 120, 210, 021, 201 // 102
                    div_by = 511
                    v0 = (v >> 0 & 0b1111111111) / div_by
                    v1 = (v >> 10 & 0b1111111111) / div_by
                    v2 = (v >> 20 & 0b1111111111) / div_by

                    if b4:
                        v_weights.append((v0, v1, v2, 1 - v0 - v1 - v2))
                    elif b3:
                        v_weights.append((v0, v1, 1 - v0 - v1))
                    elif b2:
                        v_weights.append((v0, 1 - v0))
                    else:
                        v_weights.append((1,))
                return off + 8

            def get_weights_bit(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4
                    v = data_int_un[b]
                    # 012, 120, 210, 021, 201 // 102
                    div_by = 511
                    v0 = (v >> 0 & 0b1111111111) / div_by
                    v1 = (v >> 10 & 0b1111111111) / div_by
                    v2 = (v >> 20 & 0b1111111111) / div_by

                    v_weights.append((v0, v1, v2, 1 - v0 - v1 - v2))
                return off + 4

            def sonic_free_riders_e():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weights_bit_compressed and BitFlags.weight_indices:
                    off = get_weights_bit_index(off)
                elif BitFlags.weights_bit_compressed:
                    off = get_weights_bit(off)
                elif BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    if BitFlags.normal_float:
                        off = get_normals_float(off)
                    else:
                        off = get_normals(off)
                if BitFlags.unk3:
                    off += 4
                if BitFlags.unk4:
                    off += 4
                if BitFlags.uv:
                    if BitFlags.uv_half:
                        off = get_uvs(off)
                    else:
                        off = get_uvs_float(off)
                if BitFlags.unk1:
                    off += 8

            def sonic_the_hedgehog_4_episode_i_prototype_e():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weights_bit_compressed and BitFlags.weight_indices:
                    off = get_weights_bit_index(off)
                elif BitFlags.weights_bit_compressed:
                    off = get_weights_bit(off)
                elif BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    if BitFlags.normal_float:
                        off = get_normals_float(off)
                    else:
                        off = get_normals(off)
                if BitFlags.unk3:
                    off += 4
                if BitFlags.unk4:
                    off += 4
                if BitFlags.uv:
                    if BitFlags.uv_half:
                        off = get_uvs(off)
                    else:
                        off = get_uvs_float(off)
                if BitFlags.unk1:
                    off += 8

            format_dict = {
                "SonicFreeRiders_E": sonic_free_riders_e,
                "SonicTheHedgehog4EpisodeIPrototype_E": sonic_the_hedgehog_4_episode_i_prototype_e,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                # 00000000 00PP000U 0WWW0X80 8000?N0P 00000000 00000000 000X000U 0?0NW0P0 sonic free riders

                # order Pos Wei index (X) ? N(norms bit compressed)
                # U(uv half float) 8 (skip 4 and skip 8, ? also skips 4)

                position = block_type >> 1 & 1
                weights = block_type >> 3 & 1
                weight_indices = block_type >> 12 & 1
                weights_bit_compressed = block_type >> 43 & 1
                unk3 = block_type >> 6 & 1
                normal = block_type >> 4 & 1
                normal_float = block_type >> 33 & 1
                uv_half = block_type >> 53 & 1
                unk1 = block_type >> 39 & 1
                unk4 = block_type >> 7 & 1
                uv = block_type >> 8 & 1  # uv type 1?

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(">" + str(vertex_buffer_len // 4) + "f", vertex_buffer)
            if BitFlags.normal:
                data_int = unpack(">" + str(vertex_buffer_len // 4) + "i", vertex_buffer)

            if BitFlags.weights_bit_compressed:
                data_int_un = unpack(">" + str(vertex_buffer_len // 4) + "I", vertex_buffer)

            if BitFlags.uv:
                data_half = unpack(">" + str(vertex_buffer_len // 2) + "e", vertex_buffer)

            if BitFlags.weight_indices:
                data_byte = unpack(">" + str(vertex_buffer_len) + "B", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def _gno_info(self, vert_flags):
        f = self.f
        start = self.start
        for t, offset in zip(vert_flags, self.vert_info_offset):
            f.seek(offset + start)
            if t == 1:
                vert_type, vert_count = read_short_tuple(f, 2, ">")
                vert_offset = read_int(f, ">")
                norm_type, norm_total = read_short_tuple(f, 2, ">")
                norm_offset = read_int(f, ">")
                col_type, col_total = read_short_tuple(f, 2, ">")
                col_offset = read_int(f, ">")
                uv_type, uv_total = read_short_tuple(f, 2, ">")
                uv_offset = read_int(f, ">")
                f.seek(8, 1)
                bone_type, bone_total = read_short_tuple(f, 2, ">")
                bone_offset = read_int(f, ">")
                data_bone_type, data_bone_total = read_short_tuple(f, 2, ">")
                data_bone_offset = read_int(f, ">")

                self.mesh_info.append(
                    MeshDataGno(vert_type, vert_count, vert_offset, norm_type, norm_total, norm_offset,
                                col_type, col_total, col_offset,
                                uv_type, uv_total, uv_offset,
                                0, 0, 0,
                                0, 0, 0,
                                bone_type, bone_total, bone_offset, data_bone_type, data_bone_total, data_bone_offset))
            elif t == 16:
                vert_type, vert_count = read_short_tuple(f, 2, ">")
                vert_offset = read_int(f, ">")
                norm_type, norm_total = read_short_tuple(f, 2, ">")
                norm_offset = read_int(f, ">")
                col_type, col_total = read_short_tuple(f, 2, ">")
                col_offset = read_int(f, ">")
                uv_type, uv_total = read_short_tuple(f, 2, ">")
                uv_offset = read_int(f, ">")
                uv2_type, uv2_total = read_short_tuple(f, 2, ">")
                uv2_offset = read_int(f, ">")
                uv3_type, uv3_total = read_short_tuple(f, 2, ">")
                uv3_offset = read_int(f, ">")
                f.seek(8, 1)
                bone_type, bone_total = read_short_tuple(f, 2, ">")
                bone_offset = read_int(f, ">")
                data_bone_type, data_bone_total = read_short_tuple(f, 2, ">")
                data_bone_offset = read_int(f, ">")

                self.mesh_info.append(
                    MeshDataGno(vert_type, vert_count, vert_offset, norm_type, norm_total, norm_offset,
                                col_type, col_total, col_offset,
                                uv_type, uv_total, uv_offset,
                                uv2_type, uv2_total, uv2_offset,
                                uv3_type, uv3_total, uv3_offset,
                                bone_type, bone_total, bone_offset, data_bone_type, data_bone_total, data_bone_offset))
            elif t == 65536:
                vert_info = []
                for _ in range(4):  # looks to be set to 4
                    vert_type = read_int(f, ">")
                    vert_count = read_int(f, ">")
                    block_len = read_int(f, ">")
                    vert_offset = read_int(f, ">")

                    vert_info.append(MeshData(vert_type, block_len, vert_count, vert_offset, 0, ()))
                self.mesh_info.append(vert_info)

    def _gno_vertices(self, vert_flags):
        f = self.f
        vertex_data = []

        def get_verts(d_type, count):
            if d_type == 1:
                data = read_float_tuple(f, 3 * count, ">")
                for v in range(count):
                    v_positions.append(data[v * 3: v * 3 + 3])
            else:
                data = unpack(">" + str(3 * count) + "h", f.read(3 * count * 2))
                d_type -= 2
                mult_by = 4 ** d_type
                # 9 and 10 aren't on all formats
                for v in range(count):
                    v1 = data[v * 3] / mult_by
                    v2 = data[v * 3 + 1] / mult_by
                    v3 = data[v * 3 + 2] / mult_by
                    v_positions.append((v1, v2, v3))

        def get_norms(d_type, count):
            if d_type == 1:
                data = read_float_tuple(f, 3 * count, ">")
                for v in range(count):
                    v_normals.append(data[v * 3: v * 3 + 3])
            elif d_type == 2:
                data_byte = unpack(">" + str(count * 3) + "h", f.read(count * 6))
                for v in range(count):
                    v_normals.append(
                        Vector((data_byte[v * 3] / 16384, data_byte[v * 3 + 1] / 16384, data_byte[v * 3 + 2] / 16384)
                               ).normalized())
            elif d_type == 3:
                data_byte = unpack(">" + str(count * 3) + "b", f.read(count * 3))
                for v in range(count):
                    v_normals.append(
                        Vector((data_byte[v * 3] / 64, data_byte[v * 3 + 1] / 64, data_byte[v * 3 + 2] / 64)
                               ).normalized())

        def get_colours(d_type, count):
            if d_type == 1:
                data_byte = unpack(">" + str(count * 4) + "B", f.read(count * 4))
                div_by = 255
                for v in range(count):
                    v_colours[0].append((
                        data_byte[v * 4 + 0] / div_by, data_byte[v * 4 + 1] / div_by,
                        data_byte[v * 4 + 2] / div_by, data_byte[v * 4 + 3] / div_by))

        def get_uvs(d_type, count):
            uv_data = []
            if d_type == 1:
                data = read_float_tuple(f, 2 * count, ">")
                for v in range(count):
                    v = v * 2
                    uv_data.append((data[v], - data[v + 1] + 1))
            elif d_type == 2:
                data = unpack(">" + str(2 * count) + "h", f.read(2 * count * 2))
                for v in range(count):
                    v_u = data[v * 2] / 256
                    v_v = - data[v * 2 + 1] / 256 + 1
                    uv_data.append((v_u, v_v))
            elif d_type == 3:
                data = unpack(">" + str(2 * count) + "h", f.read(2 * count * 2))
                for v in range(count):
                    v_u = data[v * 2] / 1024
                    v_v = - data[v * 2 + 1] / 1024 + 1
                    uv_data.append((v_u, v_v))
            return uv_data

        def get_bones(d_type, count, data_bone_total, data_bone_offset):
            start = f.tell()
            if d_type == 1:
                data_byte = read_byte_tuple(f, 4 * count, ">")
                f.seek(start + 2)
                data_short = read_short_tuple(f, 2 * count, ">")
                for v in range(count):
                    v_bones.append((data_byte[v * 4], data_byte[v * 4 + 1]))
                    v_weights.append((data_short[v * 2] / 16384, 1 - data_short[v * 2] / 16384))
            if d_type == 8:
                data_short = read_short_tuple(f, 2 * count, ">")
                data_short = list(zip(data_short[0::2], data_short[1::2]))
                f.seek(self.start + data_bone_offset)
                data_bone_short = read_short_tuple(f, 2 * data_bone_total, ">")
                for bone_count, bone_offset in zip(data_bone_short[0::2], data_bone_short[1::2]):
                    bone_data = data_short[bone_offset:bone_offset + bone_count]
                    v_bones.append([a[0] for a in bone_data])
                    v_weights.append([a[1] / 16384 for a in bone_data])

        # for the oldest gno known to man
        def pos():
            data = read_float_tuple(f, 3 * vertex_count, ">")
            for v in range(vertex_count):
                v_positions.append(data[v * 3: v * 3 + 3])

        def norm():
            data = read_float_tuple(f, 3 * vertex_count, ">")
            for v in range(vertex_count):
                v_normals.append(data[v * 3: v * 3 + 3])

        def uv():
            data = read_float_tuple(f, 2 * vertex_count, ">")
            uv_data = []
            for v in range(vertex_count):
                uv_data.append((data[v * 2], - data[v * 2 + 1] + 1))
            return uv_data

        def pos_wei():
            start = f.tell()
            data_float = read_float_tuple(f, 6 * vertex_count, ">")
            f.seek(start)
            data_int = read_int_tuple(f, 6 * vertex_count, ">")
            for v in range(vertex_count):
                v_positions.append(data_float[v * 6: v * 6 + 3])
                v_bones.append(data_int[v * 6 + 3: v * 6 + 5])
                v_weights.append((data_float[v * 6 + 5], 1 - data_float[v * 6 + 5]))

        for t, m in zip(vert_flags, self.mesh_info):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            if t in {1, 16}:
                if m.vertex_offset:
                    f.seek(m.vertex_offset + self.start)
                    get_verts(m.vertex_type, m.vertex_count)
                if m.norm_offset:
                    f.seek(m.norm_offset + self.start)
                    get_norms(m.norm_type, m.norm_count)
                if m.col_offset:
                    f.seek(m.col_offset + self.start)
                    get_colours(m.col_type, m.col_count)
                if m.uv_offset:
                    f.seek(m.uv_offset + self.start)
                    v_uvs = [get_uvs(m.uv_type, m.uv_count), ]
                if m.uv2_offset:
                    f.seek(m.uv2_offset + self.start)
                    v_uvs.append(get_uvs(m.uv2_type, m.uv2_count))
                if m.uv3_offset:
                    f.seek(m.uv3_offset + self.start)
                    v_uvs.append(get_uvs(m.uv3_type, m.uv3_count))
                if m.bone_offset:
                    f.seek(m.bone_offset + self.start)
                    get_bones(m.bone_type, m.bone_count, m.data_bone_count, m.data_bone_offset)
            elif t == 65536:
                for info in m:
                    vertex_count = info.vertex_count
                    f.seek(info.vertex_offset + self.start)
                    if info.vertex_block_type == 1:
                        pos()
                    elif info.vertex_block_type == 1025:
                        pos_wei()
                    elif info.vertex_block_type == 2:
                        norm()
                    elif info.vertex_block_type == 32:
                        v_uvs = [uv(), ]

            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, [], v_colours
                ))
        return vertex_data, self.mesh_info

    def _ino_info(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start + 4)
            count = read_int(f)
            vert_info_count = read_int(f)
            to_vert_info = read_int(f)
            vert_info = []
            f.seek(4, 1)
            offset = read_int(f)
            b_count = read_int(f)
            b_offset = read_int(f)

            f.seek(to_vert_info + start + 12)
            block_size_list.append(read_int(f))

            f.seek(to_vert_info + start)
            for i in range(vert_info_count):
                vert_info.append(read_int_tuple(f, 2))
                f.seek(12, 1)

            block_type_list.append(vert_info)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)
        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_short_tuple(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _ino_info_2(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start + 4)
            count = read_int(f)
            vert_info_count = read_int(f)
            to_vert_info = read_int(f)
            vert_info = []
            f.seek(8, 1)
            offset = read_int(f)
            f.seek(4, 1)
            b_count = read_int(f)
            b_offset = read_int(f)

            f.seek(to_vert_info + start + 12)
            block_size_list.append(read_int(f))

            f.seek(to_vert_info + start)
            for i in range(vert_info_count):
                vert_info.append(read_int_tuple(f, 2))
                f.seek(16, 1)

            block_type_list.append(vert_info)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)
        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_short_tuple(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _ino_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_normals(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_normals.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_wxs(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_wxs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_weights(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    w_list = []
                    for b_i in range(b_count):
                        w_list.append(data_float[i + b_i])
                    v_weights.append(w_list)
                return off + b_count * 4

            def get_indices(b_var):
                off, b_count = b_var
                for i in range(vertex_count):
                    a = i * block_len + off
                    v_bones.append(data_byte[a:a + b_count])
                return off + 4

            def sonic_4_episode_1_i():
                b_func = {
                    1: get_positions, 2: get_weights, 4: get_indices, 8: get_normals,
                    256: get_uvs
                }
                off = 0
                for b_type, b_count in block_type:
                    b_var = off, b_count
                    off = b_func[b_type](b_var)

            format_dict = {
                "SonicTheHedgehog4EpisodeI_I": sonic_4_episode_1_i,
                "SonicTheHedgehog4EpisodeIPre2016_I": sonic_4_episode_1_i,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(str(vertex_buffer_len // 4) + "f", vertex_buffer)
            data_byte = unpack(str(vertex_buffer_len) + "B", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def _lno_info(self):
        f = self.f
        start = self.start
        for offset in self.vert_info_offset:
            f.seek(offset + start + 4)
            vertex_count, info_count, info_offset = read_int_tuple(f, 3)
            f.seek(8, 1)
            v_bone_count, v_bone_off = read_int_tuple(f, 2)
            f.seek(v_bone_off + start)
            v_bone_list = read_short_tuple(f, v_bone_count)

            f.seek(info_offset + start)
            v_offset = []
            v_format = []
            v_format_size = []
            det_format = {
                1: "pos", 8: "norm", 64: "unknown", 128: "unknown", 256: "uv", 2: "weight", 4: "bone",
                512: "wx",
            }

            for _ in range(info_count):
                data = read_int_tuple(f, 5)
                v_offset.append(data[-1])
                if data[0] in det_format:
                    v_format.append(det_format[data[0]])
                else:
                    v_format.append("unknown")
                v_format_size.append(data[-2])

            self.mesh_info.append(MeshData(
                v_format, v_format_size, vertex_count, v_offset, v_bone_count, v_bone_list))

    def _lno_info_2(self):
        f = self.f
        start = self.start
        for offset in self.vert_info_offset:
            f.seek(offset + start + 4)
            vertex_count, info_count = read_int_tuple(f, 2)
            f.seek(4, 1)
            info_offset = read_int(f)
            f.seek(20, 1)
            v_bone_count, _, v_bone_off = read_int_tuple(f, 3)
            f.seek(v_bone_off + start)
            v_bone_list = read_short_tuple(f, v_bone_count)

            f.seek(info_offset + start)
            v_offset = []
            v_format = []
            v_format_size = []
            det_format = {
                1: "pos", 8: "norm", 64: "unknown", 128: "unknown", 256: "uv", 2: "weight", 4: "bone",
                512: "wx",
            }

            for _ in range(info_count):
                data = read_int_tuple(f, 6)
                v_offset.append(data[-2])
                if data[0] in det_format:
                    v_format.append(det_format[data[0]])
                else:
                    v_format.append("unknown")
                v_format_size.append(data[-3])

            self.mesh_info.append(MeshData(
                v_format, v_format_size, vertex_count, v_offset, v_bone_count, v_bone_list))

    def _lno_vertices(self):
        def pos():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_positions.append(data[v * 3: v * 3 + 3])

        def norm():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_normals.append(data[v * 3: v * 3 + 3])

        def uv():
            data = read_float_tuple(f, 2 * vertex_count)
            for v in range(vertex_count):
                v_uvs.append((data[v * 2], - data[v * 2 + 1] + 1))

        def wx():
            data = read_float_tuple(f, 2 * vertex_count)
            for v in range(vertex_count):
                v_wxs.append((data[v * 2], - data[v * 2 + 1] + 1))

        def wei():
            for _ in range(vertex_count):
                var = [a / 255 for a in read_byte_tuple(f, block_size)]
                if len(var) > 1:
                    var.append(1 - sum(var))
                else:
                    var = (var[0], 1 - var[0])
                # noinspection PyTypeChecker
                v_weights.append(var)

        def bone():
            for _ in range(vertex_count):
                v_bones.append(read_byte_tuple(f, block_size))

        def unknown():
            pass

        f = self.f
        vertex_data = []

        for info in self.mesh_info:  # for all sub meshes
            vertex_count = info.vertex_count
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
            v_bones, v_norms2_list, v_norms3_list = [], [], []

            for i in range(len(info.vertex_offset)):
                f.seek(info.vertex_offset[i] + self.start)
                block_type = info.vertex_block_type[i]
                block_size = info.vertex_block_size[i]
                block_type_func = {
                    "pos": pos, "norm": norm, "unknown": unknown, "uv": uv, "weight": wei, "bone": bone,
                    "wx": wx,
                }
                block_type_func[block_type]()

            if v_bones and not v_weights:
                v_weights = [[1, ] for _ in list(range(vertex_count))]

            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                ))
        return vertex_data, self.mesh_info

    def _sno_info(self):
        for offset in self.vert_info_offset:
            self.f.seek(offset + self.start)
            self.vertex_mesh_offset.append(read_int_tuple(self.f, 5))

    def _sno_vertices(self):
        def type_common():
            def pos():
                data = read_float_tuple(f, 3 * vertex_count)
                for v in range(vertex_count):
                    v_positions.append(data[v * 3: v * 3 + 3])

            def norm():
                data = read_float_tuple(f, 3 * vertex_count)
                for v in range(vertex_count):
                    v_normals.append(data[v * 3: v * 3 + 3])

            def uv():
                data = read_float_tuple(f, 2 * vertex_count)
                for v in range(vertex_count):
                    v_uvs.append((data[v * 2], - data[v * 2 + 1] + 1))

            def uv_short():
                data = read_short_tuple(f, 2 * vertex_count)
                data = [a / 4095 for a in data]
                for v in range(vertex_count):
                    v_uvs.append((data[v * 2], - data[v * 2 + 1] + 1))

            def norm_short():
                count = vertex_count * 3
                data = unpack(str(count) + "h", f.read(count * 2))
                data = [a / 4096 for a in data]
                for v in range(vertex_count):
                    v_normals.append(Vector(data[v * 3: v * 3 + 3]).normalized())

            def unk4():  # not sure how to parse these normals
                f.seek(4 * vertex_count, 1)

            def uv_wx_short():
                data = read_short_tuple(f, 4 * vertex_count)
                data = [a / 4095 for a in data]
                for v in range(vertex_count):
                    v_uvs.append((data[v * 4], - data[v * 4 + 1] + 1))
                    v_wxs.append((data[v * 4 + 2], - data[v * 4 + 3] + 1))

            det_v_type = {
                (2, 120): pos,
                (3, 120): norm, (3, 121): norm_short, (3, 126): unk4,
                (4, 116): uv, (4, 117): uv_short, (4, 125): uv_wx_short,
            }

            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(4, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    f.seek(4, 1)
                    vertex_count = read_int(f)
                    if vertex_count == 0:
                        break
                    f.seek(36, 1)
                else:
                    f.seek(28, 1)

                var = read_byte_tuple(f, 4)
                for _ in range(var[0]):
                    v_type = read_byte_tuple(f, 4)
                    if v_type[0] == v_type[1] == v_type[2] == 0 and v_type[3] == 32:
                        f.seek(4, 1)
                        v_type = read_byte_tuple(f, 4)
                    if (v_type[0], v_type[1]) == (0, 0):
                        f.seek(-4, 1)
                        read_aligned(f, 4)
                        v_type = read_byte_tuple(f, 4)
                    det_v_type[(v_type[0], v_type[-1])]()

                read_int(f)  # should be 23

                read_aligned(f, 16)

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        def type_1():
            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(12, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    break
                f.seek(28, 1)
                for _ in range(vertex_count):
                    v_positions.append(read_float_tuple(f, 3))
                    f.seek(4, 1)
                    v_normals.append(read_float_tuple(f, 3))
                    f.seek(20, 1)

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        def type_2():
            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(12, 1)

                vertex_count = read_int(f)
                f.seek(28, 1)
                if vertex_count == 0:
                    break
                for _ in range(vertex_count):
                    v_positions.append(read_float_tuple(f, 3))
                    f.seek(20, 1)
                    v_uvs.append((read_float(f), - read_float(f) + 1))
                    f.seek(8, 1)

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        def type_17():
            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(12, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    break
                f.seek(28, 1)
                for _ in range(vertex_count):
                    v_positions.append(read_float_tuple(f, 3))
                    w1 = read_float(f)
                    v_normals.append(read_float_tuple(f, 3))
                    f.seek(4, 1)
                    v_uvs.append((read_float(f), - read_float(f) + 1))
                    b1 = read_int(f) // 4
                    b2 = read_int(f) // 4
                    w2 = 1 - w1
                    v_weights.append((w1, w2))
                    v_bones.append((b1, b2))

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        def type_33():
            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(12, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    break
                f.seek(28, 1)
                for _ in range(vertex_count):
                    v_positions.append(read_float_tuple(f, 3))
                    w1 = read_float(f)
                    v_normals.append(read_float_tuple(f, 3))
                    f.seek(4, 1)
                    v_uvs.append((read_float(f), - read_float(f) + 1))
                    b1 = read_int(f) // 4
                    b2 = read_int(f) // 4
                    w2, w3 = read_float_tuple(f, 2)
                    b3 = read_int(f) // 4
                    b4 = read_int(f) // 4
                    w4 = 1 - w1 - w2 - w3
                    v_weights.append((w1, w2, w3, w4))
                    v_bones.append((b1, b2, b3, b4))

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        def type_273():
            while final_pos > f.tell():
                v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours = [], [], [], [], [], [[], []]
                v_bones, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(12, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    break
                f.seek(28, 1)
                for _ in range(vertex_count):
                    v_positions.append(read_float_tuple(f, 3))
                    w1 = read_float(f)
                    v_normals.append(read_float_tuple(f, 3))
                    f.seek(4, 1)
                    v_uvs.append((read_float(f), - read_float(f) + 1))
                    b1 = read_int(f) // 4
                    b2 = read_int(f) // 4
                    w2 = 1 - w1
                    v_weights.append((w1, w2))
                    v_bones.append((b1, b2))
                    v_wxs.append((read_float(f), - read_float(f) + 1))
                    f.seek(8, 1)

                v_data.append(
                    VertexData(
                        v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours,
                    ))

        f = self.f
        post_info = self.start
        d_type_list = {1: type_1, 2: type_2, 17: type_17, 33: type_33, 273: type_273}
        vertex_data = []
        mesh_info = []

        for info in self.vertex_mesh_offset:
            d_type, v_len, fpos, bone_count_complex, b_off = info
            f.seek(b_off + post_info)
            bone_list_complex = read_int_tuple(f, bone_count_complex)
            fpos = fpos + post_info
            f.seek(fpos)
            final_pos = v_len * 16 + fpos - 32
            v_data = []
            if d_type in {5, 6, 9, 10, 265}:
                type_common()
            elif d_type in d_type_list:
                d_type_list[d_type]()

            mesh_info.append(
                MeshData(None, None, 0, None, bone_count_complex, bone_list_complex))
            vertex_data.append(v_data)
        return vertex_data, mesh_info

    def _uno_info(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start + 8)
            block_type_list.append(read_int(f, ">"))
            f.seek(1, 1)
            size = read_byte(f)
            f.seek(6, 1)
            offset, b_offset, b_count, count = read_int_tuple(f, 4)
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)
        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_int_tuple(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _uno_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_weights_4(off):
                div_by = 32767
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v = data_short[i:i + 4]
                    v_weights.append([v[0] / div_by, v[1] / div_by, v[2] / div_by, v[3] / div_by])
                return off + 8

            def get_weights_2(off):
                div_by = 32767
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v_weights.append([data_short[i] / div_by, data_short[i + 1] / div_by])
                return off + 4

            def k_on_after_school_live_u():
                off = 0

                if BitFlags.weights_2:
                    off = get_weights_2(off)

                if BitFlags.weights_4:
                    off = get_weights_4(off)

                if BitFlags.uv:
                    off = get_uvs(off)

                if BitFlags.unknown:
                    off += 4

                off = get_positions(off)

            format_dict = {
                "KOnAfterSchoolLive_U": k_on_after_school_live_u,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                unknown = block_type >> 10 & 1
                uv = block_type >> 19 & 1
                weights_2 = block_type >> 26 & 1
                weights_4 = block_type >> 27 & 1

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(str(vertex_buffer_len // 4) + "f", vertex_buffer)

            if BitFlags.weights_4 or BitFlags.weights_2:  # signed weights
                data_short = unpack(str(vertex_buffer_len // 2) + "h", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def _xno_zno_info(self):
        f = self.f
        start = self.start
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + start)
            block_type_list.append(unpack(">Q", f.read(8))[0])  # python gives back as big endian so countering
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5)
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)
        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + start
            if offset:  # get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_int_tuple(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                             self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _xno_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_weights(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    w = data_float[i:i + 3]
                    v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                return off + 12

            def get_weights_with_indices(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4
                    w = data_float[b:b + 3]

                    a = i * block_len + off + 12
                    b1, b2, b3, b4 = data_byte[a:a + 4]
                    v_bones.append((b1, b2, b3, b4))

                    if b4:
                        v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                    elif b3:
                        v_weights.append((w[0], w[1], 1 - w[0] - w[1]))
                    elif b2:
                        v_weights.append((w[0], 1 - w[0]))
                    else:
                        v_weights.append((1,))
                return off + 16

            def get_normals(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_normals.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_wxs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_wxs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_colours_short(off):  # colours stored as b g r a
                div_by = 65535
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v = data_short[i:i + 4]
                    v_colours[0].append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 8

            def get_colours_byte(off):  # colours stored as b g r a
                div_by = 255
                for i in range(vertex_count):
                    i = i * block_len + off
                    v = data_byte[i:i + 4]
                    v_colours[0].append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 4

            def get_colours_byte2(off):  # colours stored as b g r a
                div_by = 255
                for i in range(vertex_count):
                    i = i * block_len + off
                    v = data_byte[i:i + 4]
                    v_colours[1].append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 4

            def sonic_riders_x():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)
                if BitFlags.weights:
                    off = get_weights(off)
                if BitFlags.normal:
                    off = get_normals(off)

                if BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)
                if BitFlags.uv:
                    off = get_uvs(off)
                if BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)

            def phantasy_star_universe_x():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    off = get_normals(off)

                if BitFlags.colour_short and BitFlags.colour_byte:
                    off = get_colours_byte(off)
                    off = get_colours_byte2(off)
                elif BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)

                if BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

            def sonic_2006_x():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    off = get_normals(off)
                if BitFlags.colour_byte:
                    off += 4
                    # off = get_colours_byte(off)
                    # would like to support this better but need material refactor

                if BitFlags.wx and BitFlags.uv:
                    off = get_uvs(off)
                    off += 8
                    off = get_wxs(off)
                elif BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

                if BitFlags.unnamed:
                    off += 24

            format_dict = {
                "SonicRiders_X": sonic_riders_x, "PhantasyStarUniverse_X": phantasy_star_universe_x,
                "Sonic2006_X": sonic_2006_x,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                # 000KC0NP 0WWW0000 000000QU 00000000 KC0NW0P0 000000QU 00000000 00000000 SR PC
                #  K = colours as shorts, not bytes Q = uv2
                #  block order: POS Q WEIGH NORM COL UV SR PC
                # 0M00C0NP 0WWW0I02 000000XU 00000000 0C0NW0P0 000W00XU 00000000 00000000 06
                # X is wx - if both U and X are on its a different thing
                #  M = 2 extra normal sets, I = bone indices
                # 00000001 00000000 00000011 00000000 00000010 00000011 00000000 00000000 s4e1
                # p, uw,

                uv = block_type >> 16 & 1
                position = block_type >> 25 & 1
                normal = block_type >> 28 & 1
                colour_short = block_type >> 31 & 1
                colour_byte = block_type >> 30 & 1
                weights = block_type >> 27 & 1
                weight_indices = block_type >> 50 & 1
                wx = block_type >> 17 & 1
                unnamed = block_type >> 48 & 1

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(str(vertex_buffer_len // 4) + "f", vertex_buffer)

            if BitFlags.colour_short:
                data_short = unpack(str(vertex_buffer_len // 2) + "H", vertex_buffer)

            if BitFlags.weight_indices or BitFlags.colour_byte:
                data_byte = unpack(str(vertex_buffer_len) + "B", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def _zno_vertices(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def get_positions(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_positions.append(data_float[i:i + 3])
                return off + 12

            def get_weights(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    w = data_float[i:i + 3]
                    v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                return off + 12

            def get_weights_with_indices(off):
                for i in range(vertex_count):
                    b = (i * block_len + off) // 4
                    w = data_float[b:b + 3]

                    a = i * block_len + off + 12
                    b1, b2, b3, b4 = data_byte[a:a + 4]
                    v_bones.append((b1, b2, b3, b4))

                    if b4:
                        v_weights.append((w[0], w[1], w[2], 1 - w[0] - w[1] - w[2]))
                    elif b3:
                        v_weights.append((w[0], w[1], 1 - w[0] - w[1]))
                    elif b2:
                        v_weights.append((w[0], 1 - w[0]))
                    else:
                        v_weights.append((1,))
                return off + 16

            def get_normals(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_normals.append(data_float[i:i + 3])
                return off + 12

            def get_uvs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_uvs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_wxs(off):
                for i in range(vertex_count):
                    i = (i * block_len + off) // 4
                    v_wxs.append((data_float[i], - data_float[i + 1] + 1))
                return off + 8

            def get_colours_short(off):  # colours stored as b g r a
                div_by = 65535
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v = data_short[i:i + 4]
                    v_colours[0].append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 8

            def get_colours_byte(off):  # colours stored as b g r a
                div_by = 255
                for i in range(vertex_count):
                    i = i * block_len + off
                    v = data_byte[i:i + 4]
                    v_colours[0].append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 4

            def sonic_4_episode_1_z():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    off = get_normals(off)

                if BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)

                if BitFlags.wx and BitFlags.uv:
                    off = get_uvs(off)
                    off += 8
                    off = get_wxs(off)
                elif BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

                if BitFlags.unnamed:
                    off += 24

            def transformers_human_alliance_z():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    off = get_normals(off)

                if BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)

                if BitFlags.wx and BitFlags.uv:
                    off = get_uvs(off)
                    off += 8
                    off = get_wxs(off)
                elif BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

                if BitFlags.unnamed:
                    off += 24

            def sega_golden_gun_z():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)

                if BitFlags.weight_indices:
                    off = get_weights_with_indices(off)
                elif BitFlags.weights:
                    off = get_weights(off)

                if BitFlags.normal:
                    off = get_normals(off)

                if BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)

                if BitFlags.wx and BitFlags.uv:
                    off = get_uvs(off)
                    off += 8
                    off = get_wxs(off)
                elif BitFlags.wx:
                    off = get_uvs(off)
                    off = get_wxs(off)
                elif BitFlags.uv:
                    off = get_uvs(off)

                if BitFlags.unnamed:
                    off += 24

            format_dict = {
                "Sonic4Episode1_Z": sonic_4_episode_1_z,
                "TransformersHumanAlliance_Z": transformers_human_alliance_z,
                "SegaGoldenGun_Z": sega_golden_gun_z,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [[], []], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                # 000KC0NP 0WWW0000 000000QU 00000000 KC0NW0P0 000000QU 00000000 00000000 SR PC
                #  K = colours as shorts, not bytes Q = unknown, in psu Q is wx but srpc has only one float(?)
                #  block order: POS Q WEIGH NORM COL UV SR PC
                # 0M00C0NP 0WWW0I02 000000XU 00000000 0C0NW0P0 000W00XU 00000000 00000000 06
                # X is wx - if both U and X are on its a different thing
                #  M = 2 extra normal sets, I = bone indices
                # 00000001 00000000 00000011 00000000 00000010 00000011 00000000 00000000 s4e1
                # p, uw,

                uv = block_type >> 16 & 1
                position = block_type >> 25 & 1
                normal = block_type >> 28 & 1
                colour_short = block_type >> 31 & 1
                colour_byte = block_type >> 30 & 1
                weights = block_type >> 27 & 1
                weight_indices = block_type >> 50 & 1
                wx = block_type >> 17 & 1
                unnamed = block_type >> 48 & 1

            vertex_buffer = f.read(vertex_buffer_len)
            data_float = unpack(str(vertex_buffer_len // 4) + "f", vertex_buffer)

            if BitFlags.colour_short:
                data_short = unpack(str(vertex_buffer_len // 2) + "H", vertex_buffer)

            if BitFlags.weight_indices or BitFlags.colour_byte:
                data_byte = unpack(str(vertex_buffer_len) + "B", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

    def cno(self):
        self._be_offsets()
        self._cno_info()
        return self._cno_vertices()

    def eno(self):
        self._be_offsets()
        self._eno_info()
        return self._eno_vertices()

    def gno(self):
        vert_flags = self._be_offsets_flags()
        self._gno_info(vert_flags)
        return self._gno_vertices(vert_flags)

    def ino(self):
        if self.format_type == "SonicTheHedgehog4EpisodeI_I":
            self._le_offsets_3()
            self._ino_info_2()
            return self._ino_vertices()
        else:
            self._le_offsets()
            self._ino_info()
            return self._ino_vertices()

    def lno(self):
        self._le_offsets()
        self._lno_info()
        return self._lno_vertices()

    def lno_s4e2(self):
        self._le_offsets_4()
        self._lno_info_2()
        return self._lno_vertices()

    def sno(self):
        self._le_offsets()
        self._sno_info()
        return self._sno_vertices()

    def uno(self):
        self._le_offsets()
        self._uno_info()
        return self._uno_vertices()

    def xno(self):
        self._le_offsets()
        self._xno_zno_info()
        return self._xno_vertices()

    def zno(self):
        self._le_offsets()
        self._xno_zno_info()
        return self._zno_vertices()


@dataclass
class GnoVertOffset:
    pos_start: int
    pos_count: int
    pos_type: int
    norm_start: int
    norm_count: int
    norm_type: int
    col_start: int
    col_count: int
    col_type: int
    uv_start: int
    uv_count: int
    uv_type: int
    bone_start: int
    bone_count: int
    weight_type: int
    bone2_start: int
    bone2_count: int


class Write:
    __slots__ = [
        "f", "format_type", "meshes", "nof0_offsets", "bones", "vert_offsets", "bone_used", "settings"
    ]

    def __init__(self, f, format_type, meshes, nof0_offsets, bones, bone_used, settings):
        self.f = f
        self.format_type = format_type
        self.meshes = meshes
        self.nof0_offsets = nof0_offsets
        self.bones = bones
        self.bone_used = bone_used
        self.settings = settings
        self.vert_offsets = []

    @dataclass
    class VertData:
        offset: int
        norm: bool
        wei: bool
        col: bool
        uv: bool
        wx: bool
        block_size: int
        count: int
        bones: list

    def _xno_vertices(self):
        f = self.f

        for m in self.meshes:
            if not m:
                continue
            m = m.vertices
            for mesh, bone_names in m:
                vertex_start = f.tell()
                norm = bool(mesh[0].normals)
                wei = bool(mesh[0].weights)
                colours = bool(mesh[0].colours)
                uvs = bool(mesh[0].uvs)
                wxs = bool(mesh[0].wxs)
                if len(bone_names) > 4:
                    # indices, weights
                    for v in mesh:
                        current_weights = list(v.weights)

                        # get used groups
                        used = [a for a in current_weights if a[1]][:4]
                        used.sort()
                        needed = [(0, 0) for a in range(4 - len(used))]
                        used = used + needed
                        # we do not write the last float :)
                        v.weights = [[a[0] for a in used], [a[1] for a in used][:-1]]
                elif len(bone_names) > 1:
                    # the order of names in bone_names is the final order
                    # the length can be 2, 3 or 4 names but 4 weights will always be stored
                    for v in mesh:
                        current_weights = list(v.weights)

                        # get correct length
                        used = set([a[0] for a in current_weights])
                        possible = set(range(4))
                        needed = [(a, 0) for a in list(possible - used)]
                        new_weights = current_weights + needed
                        new_weights.sort()  # order correctly
                        v.weights = [a[1] for a in new_weights[:-1]]  # we do not write the last float :)
                else:
                    bone_names = []
                block_size = 3 * 4
                if norm:
                    block_size += 3 * 4
                if uvs:
                    block_size += 2 * 4
                if colours:
                    if self.settings.cols == "short":
                        block_size += 1 * 4
                    block_size += 1 * 4
                if bone_names:
                    block_size += 3 * 4
                if len(bone_names) > 4:
                    block_size += 4
                self.vert_offsets.append(self.VertData(
                    vertex_start, norm, wei, colours, uvs, wxs, block_size, len(mesh), bone_names))
                v_buff = b""
                for v in mesh:
                    v_buff += pack("<3f", *v.positions)
                    if v.weights:
                        if len(bone_names) > 4:
                            v_buff += pack("<3f", *v.weights[1])
                            v_buff += pack("<4B", *v.weights[0])
                        else:
                            v_buff += pack("<3f", *v.weights)
                    if v.normals:
                        v_buff += pack("<3f", *v.normals)
                    if v.colours:
                        if self.settings.cols == "short":
                            for col in [v.colours[2], v.colours[1], v.colours[0], v.colours[3]]:
                                v_buff += pack("<H", round(col * 65535))
                        else:
                            for col in [v.colours[2], v.colours[1], v.colours[0], v.colours[3]]:
                                v_buff += pack("<B", round(col * 255))
                    if v.uvs:
                        v_buff += pack("<2f", *v.uvs)
                    if v.wxs:
                        v_buff += pack("<2f", *v.wxs)
                f.write(v_buff)

    def _gno_vertices(self):
        f = self.f

        for m in self.meshes:
            if not m:
                continue
            m = m.vertices
            for mesh in m:
                pos_start = f.tell()
                if mesh.positions_type == 1:
                    for vert in mesh.positions:
                        write_float(f, ">", vert[0], vert[1], vert[2])
                else:
                    for vert in mesh.positions:
                        f.write(pack(">h", vert[0]))
                        f.write(pack(">h", vert[1]))
                        f.write(pack(">h", vert[2]))
                write_aligned(f, 4)

                norm_start = f.tell()
                if mesh.normals_type == 1:
                    for vert in mesh.normals:
                        write_float(f, ">", vert[0], vert[1], vert[2])
                elif mesh.normals_type == 2:
                    for vert in mesh.normals:
                        f.write(pack(">h", vert[0]))
                        f.write(pack(">h", vert[1]))
                        f.write(pack(">h", vert[2]))
                else:
                    for vert in mesh.normals:
                        f.write(pack(">b", vert[0]))
                        f.write(pack(">b", vert[1]))
                        f.write(pack(">b", vert[2]))
                write_aligned(f, 4)

                col_start = f.tell()
                if mesh.colours_type == 1:
                    for vert in mesh.colours:
                        f.write(pack(">B", vert[0]))
                        f.write(pack(">B", vert[1]))
                        f.write(pack(">B", vert[2]))
                        f.write(pack(">B", vert[3]))
                write_aligned(f, 4)

                uv_start = f.tell()
                if mesh.uvs_type == 1:
                    for vert in mesh.uvs:
                        write_float(f, ">", vert[0], vert[1])
                else:
                    for vert in mesh.uvs:
                        f.write(pack(">h", vert[0]))
                        f.write(pack(">h", vert[1]))
                write_aligned(f, 4)

                bone_start = f.tell()

                bone_used = self.bone_used
                weight_type = 0
                bone_count = 0
                bone2_start = 0
                bone2_count = 0

                if mesh.weights:
                    if max(len(i) for i in mesh.weights) > 2:
                        weight_type = 8
                        for vert in mesh.weights:
                            for v in vert:
                                write_short(f, ">", bone_used.index(v[0]), round(v[1] * 16384))
                        bone2_start = f.tell()
                        bone2_count = len(mesh.weights)
                        wei_list_len = [len(i) for i in mesh.weights]
                        wei_list_index = 0
                        for i in wei_list_len:
                            write_short(f, ">", i, wei_list_index)
                            wei_list_index += i
                        bone_count = wei_list_index
                    else:
                        weight_type = 1
                        wei_list = []
                        bone_count = len(mesh.weights)
                        for vert in mesh.weights:
                            w_bone = []
                            w_wei = []
                            for i, wei in vert:
                                bone = bone_used.index(i)
                                w_bone.append(bone)
                                w_wei.append(wei)
                            w_bone.append(0)
                            w_wei.append(0)
                            wei_list.append((w_bone, w_wei))
                        for wei in wei_list:
                            # byte byte short / index index weight
                            w_bone = wei[0]
                            w_wei = wei[1]
                            write_byte(f, ">", w_bone[0], w_bone[1])
                            write_short(f, ">", round(w_wei[0] * 16384))
                self.vert_offsets.append(GnoVertOffset(
                    pos_start, len(mesh.positions), mesh.positions_type,
                    norm_start, len(mesh.normals), mesh.normals_type,
                    col_start, len(mesh.colours), mesh.colours_type,
                    uv_start, len(mesh.uvs), mesh.uvs_type,
                    bone_start, bone_count, weight_type,
                    bone2_start, bone2_count
                ))
        write_aligned(f, 4)

    def _gno_info(self):
        f = self.f
        offsets = self.vert_offsets
        self.vert_offsets = []
        for vert_info in offsets:
            vert_info: GnoVertOffset
            self.vert_offsets.append(f.tell())
            write_short(f, ">", vert_info.pos_type, vert_info.pos_count)
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", vert_info.pos_start)

            if vert_info.norm_count:
                write_short(f, ">", vert_info.norm_type, vert_info.norm_count)
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", vert_info.norm_start)
            else:
                write_integer(f, ">", 0, 0)

            if vert_info.col_count:
                write_short(f, ">", vert_info.col_type, vert_info.col_count)
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", vert_info.col_start)
            else:
                write_integer(f, ">", 0, 0)

            if vert_info.uv_count:
                write_short(f, ">", vert_info.uv_type, vert_info.uv_count)
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", vert_info.uv_start)
            else:
                write_integer(f, ">", 0, 0)

            write_integer(f, ">", 0, 0)

            if vert_info.bone_count:
                write_short(f, ">", vert_info.weight_type, vert_info.bone_count)
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", vert_info.bone_start)
            else:
                write_integer(f, ">", 0, 0)

            if vert_info.bone2_count:
                write_short(f, ">", 1, vert_info.bone2_count)
                self.nof0_offsets.append(f.tell())
                write_integer(f, ">", vert_info.bone2_start)
            else:
                write_integer(f, ">", 0, 0)

    def _xno_info(self):
        f = self.f
        new_off = []
        for info in self.vert_offsets:
            info: Write.VertData
            start_bone = 0
            bone_count = 0
            if info.bones:
                start_bone = f.tell()
                bone_count = len(info.bones)
                for b in info.bones:
                    write_integer(f, "<", self.bone_used.index(b))
            new_off.append(f.tell())
            flag1 = 1  # position flags
            flag2 = 2
            if info.norm:
                flag1 = flag1 | 2
                flag2 = flag2 | 16
            if info.uv:
                flag1 = flag1 | 65536
                flag2 = flag2 | 256
            if info.col:
                if self.settings.cols == "short":
                    flag1 = flag1 | 16
                    flag2 = flag2 | 128
                else:
                    flag1 = flag1 | 8
                    flag2 = flag2 | 64
            if bone_count > 4:
                flag1 = flag1 | 1024
            if bone_count:
                flag1 = flag1 | 28672
                flag2 = flag2 | 8

            write_integer(f, "<", flag1, flag2)
            self.nof0_offsets.append(f.tell() + 8)
            write_integer(f, "<", info.block_size, info.count, info.offset, bone_count, start_bone)
            if start_bone:
                self.nof0_offsets.append(f.tell() - 4)
            write_integer(f, "<", 0, 0, 0, 0, 0)
        self.vert_offsets = new_off
        # 000KC0NP 0WWW0000 000000QU 00000000 KC0NW0P0 000000QU 00000000 00000000 SR PC
        #  K = colours as shorts, not bytes Q = unknown, in psu Q is wx but srpc has only one float(?)
        #  block order: POS Q WEIGH NORM COL UV SR PC
        # 0M00C0NP 0WWW0I02 000000XU 00000000 0C0NW0P0 000W00XU 00000000 00000000 06

    def _zno_info(self):
        f = self.f
        new_off = []
        for info in self.vert_offsets:
            info: Write.VertData
            start_bone = 0
            bone_count = 0
            if info.bones:
                start_bone = f.tell()
                bone_count = len(info.bones)
                for b in info.bones:
                    write_integer(f, "<", self.bone_used.index(b))
            new_off.append(f.tell())
            flag1 = 1  # position flags
            flag2 = 2

                # uv = block_type >> 16 & 1
                # position = block_type >> 25 & 1
                # normal = block_type >> 28 & 1
                # colour_short = block_type >> 31 & 1
                # colour_byte = block_type >> 30 & 1
                # weights = block_type >> 27 & 1
                # weight_indices = block_type >> 50 & 1
                # wx = block_type >> 17 & 1
                # unnamed = block_type >> 48 & 1

            if info.norm:
                flag1 = flag1 | 2
                flag2 = flag2 | 16
            if info.uv:
                flag1 = flag1 | 65536
                flag2 = flag2 | 256
            if info.col:
                if self.settings.cols == "short":
                    flag1 = flag1 | 16
                    flag2 = flag2 | 128
                else:
                    flag1 = flag1 | 8
                    flag2 = flag2 | 64
            if bone_count > 4:
                flag1 = flag1 | 1024
            if bone_count:
                flag1 = flag1 | 28672
                flag2 = flag2 | 8

            write_integer(f, "<", flag1, flag2)
            self.nof0_offsets.append(f.tell() + 8)
            write_integer(f, "<", info.block_size, info.count, info.offset, bone_count, start_bone)
            if start_bone:
                self.nof0_offsets.append(f.tell() - 4)
            write_integer(f, "<", 0, 0, 0, 0, 0)
        self.vert_offsets = new_off
        # 000KC0NP 0WWW0000 000000QU 00000000 KC0NW0P0 000000QU 00000000 00000000 SR PC
        #  K = colours as shorts, not bytes Q = unknown, in psu Q is wx but srpc has only one float(?)
        #  block order: POS Q WEIGH NORM COL UV SR PC
        # 0M00C0NP 0WWW0I02 000000XU 00000000 0C0NW0P0 000W00XU 00000000 00000000 06

    def _be_offsets(self):
        f = self.f
        for a in self.vert_offsets:
            write_integer(f, ">", 1)
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", a)

    def _le_offsets(self):
        f = self.f
        for a in self.vert_offsets:
            write_integer(f, "<", 1)
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", a)

    def gno(self):
        self._gno_vertices()
        self._gno_info()
        vert_offset = self.f.tell()
        self._be_offsets()
        return vert_offset, self.nof0_offsets

    def xno(self):
        self._xno_vertices()
        v_buff_end = self.f.tell()
        write_aligned(self.f, 4)
        self._xno_info()
        vert_offset = self.f.tell()
        self._le_offsets()
        return vert_offset, v_buff_end, self.nof0_offsets

    def zno(self):
        self._xno_vertices()
        v_buff_end = self.f.tell()
        write_aligned(self.f, 4)
        self._xno_info()
        vert_offset = self.f.tell()
        self._le_offsets()
        return vert_offset, v_buff_end, self.nof0_offsets
