from dataclasses import dataclass
from enum import Flag

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

    def _le_offsets(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2)[1::2]

    def _be_offsets(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2, ">")[1::2]

    def _le_info_1(self):
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

    def _be_info_1(self):
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

    def _le_info_2(self):
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

    def _le_info_3(self):
        for offset in self.vert_info_offset:
            self.f.seek(offset + self.start)
            self.vertex_mesh_offset.append(read_int_tuple(self.f, 5))

    def _le_info_4(self):
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

    def _le_info_5(self):
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

    def _be_info_2(self):
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

            format_dict = {
                "HouseOfTheDead4_C": house_of_the_dead_4_c,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):
                # 00000000 000?00XU 0000IW0? 0?0??0/P house of the dead 4
                # 00000000 00010010 00001101 01011011
                # either have U or X on - you shouldn't have both
                # order:
                # Pos Weights boneIndices ? Uvs wX ?

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

                    v_normals.append([v0 / div_by, v1 / div_by, v2 / div_by])
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

            format_dict = {
                "SonicFreeRiders_E": sonic_free_riders_e,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
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
                "Sonic4Episode1_I": sonic_4_episode_1_i,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
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

    def _lno_vertices(self):
        def pos():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_pos_list.append(data[v * 3: v * 3 + 3])

        def norm():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_norms_list.append(data[v * 3: v * 3 + 3])

        def uv():
            data = read_float_tuple(f, 2 * vertex_count)
            for v in range(vertex_count):
                v_uvs_list.append((data[v * 2], - data[v * 2 + 1] + 1))

        def wx():
            data = read_float_tuple(f, 2 * vertex_count)
            for v in range(vertex_count):
                v_wxs_list.append((data[v * 2], - data[v * 2 + 1] + 1))

        def wei():
            for _ in range(vertex_count):
                var = [a / 255 for a in read_byte_tuple(f, block_size)]
                if len(var) > 1:
                    var.append(1 - sum(var))
                else:
                    var = (var[0], 1 - var[0])
                # noinspection PyTypeChecker
                v_b_wei_list.append(var)

        def bone():
            for _ in range(vertex_count):
                v_b_index_list.append(read_byte_tuple(f, block_size))

        def unknown():
            pass

        f = self.f
        vertex_data = []

        for info in self.mesh_info:  # for all sub meshes
            vertex_count = info.vertex_count
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []

            for i in range(len(info.vertex_offset)):
                f.seek(info.vertex_offset[i] + self.start)
                block_type = info.vertex_block_type[i]
                block_size = info.vertex_block_size[i]
                block_type_func = {
                    "pos": pos, "norm": norm, "unknown": unknown, "uv": uv, "weight": wei, "bone": bone,
                    "wx": wx,
                }
                block_type_func[block_type]()

            if v_b_index_list and not v_b_wei_list:
                v_b_wei_list = [[1, ] for _ in list(range(vertex_count))]

            vertex_data.append(
                VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                ))
        return vertex_data, self.mesh_info

    def _sno_vertices(self):
        def pos():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_pos_list.append(data[v * 3: v * 3 + 3])

        def norm():
            data = read_float_tuple(f, 3 * vertex_count)
            for v in range(vertex_count):
                v_norms_list.append(data[v * 3: v * 3 + 3])

        def uv():
            data = read_float_tuple(f, 2 * vertex_count)
            for v in range(vertex_count):
                v_uvs_list.append(data[v * 2: v * 2 + 2])

        def unk1():
            f.seek(vertex_count * 6, 1)

        def unk2():
            f.seek(vertex_count * 4, 1)

        f = self.f
        post_info = self.start
        det_v_type = {
            (2, 120): pos, (3, 120): norm, (4, 116): uv,
            (3, 121): unk1, (4, 117): unk2,
        }
        vertex_data = []
        mesh_info = []

        for info in self.vertex_mesh_offset:
            _, v_len, pos, bone_count_complex, b_off = info
            f.seek(b_off + post_info)
            bone_list_complex = read_int_tuple(f, bone_count_complex)
            pos = pos + post_info
            f.seek(pos)
            final_pos = v_len * 16 + pos - 32
            v_data = []
            while final_pos > f.tell():
                v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
                v_b_index_list, v_norms2_list, v_norms3_list = [], [], []

                var = read_int(f)
                while var != 16778244:
                    var = read_int(f)
                f.seek(4, 1)

                vertex_count = read_int(f)
                if vertex_count == 0:
                    break

                f.seek(28, 1)
                var = read_byte_tuple(f, 4)
                for _ in range(var[0]):
                    v_type = read_byte_tuple(f, 4)
                    if (v_type[0], v_type[1]) == (0, 0):
                        f.seek(-4, 1)
                        read_aligned(f, 4)
                        v_type = read_byte_tuple(f, 4)
                    det_v_type[(v_type[0], v_type[-1])]()

                v_data.append(
                    VertexData(
                        v_pos_list, v_b_wei_list, v_b_index_list,
                        v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    ))
            mesh_info.append(
                MeshData(None, None, 0, None, bone_count_complex, bone_list_complex))
            vertex_data.append(v_data)
        return vertex_data, mesh_info

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

            def get_weights_short(off):
                div_by = 65535
                for i in range(vertex_count):
                    i = (i * block_len + off) // 2
                    v = data_short[i:i + 4]
                    v_weights.append([v[0] / div_by, v[1] / div_by, v[2] / div_by, v[3] / div_by])
                return off + 8

            def k_on_after_school_live_u():
                off = 0

                off = get_weights_short(off)
                off = get_uvs(off)
                off = get_positions(off)

            format_dict = {
                "KOnAfterSchoolLive_U": k_on_after_school_live_u,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
            f.seek(self.vertex_mesh_offset[var] + self.start)
            vertex_count = self.mesh_info[var].vertex_count
            block_len = self.mesh_info[var].vertex_block_size
            block_type = self.mesh_info[var].vertex_block_type
            vertex_buffer_len = vertex_count * block_len

            class BitFlags(Flag):  # not enough samples for this

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

            data_short = unpack(str(vertex_buffer_len // 2) + "H", vertex_buffer)

            del vertex_buffer

            vert_block()
            vertex_data.append(
                VertexData(
                    v_positions, v_weights, v_bones, v_normals, v_uvs, v_wxs, v_colours
                ))
        return vertex_data, self.mesh_info

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
                    v_colours.append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 8

            def get_colours_byte(off):  # colours stored as b g r a
                div_by = 255
                for i in range(vertex_count):
                    i = i * block_len + off
                    v = data_byte[i:i + 4]
                    v_colours.append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 4

            def sonic_riders_x():
                off = 0
                if BitFlags.position:
                    off = get_positions(off)
                if BitFlags.wx:  # unknown float
                    off += 4
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

                if BitFlags.colour_short:
                    off = get_colours_short(off)
                elif BitFlags.colour_byte:
                    off = get_colours_byte(off)

                if BitFlags.wx:
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
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
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
                    v_colours.append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
                return off + 8

            def get_colours_byte(off):  # colours stored as b g r a
                div_by = 255
                for i in range(vertex_count):
                    i = i * block_len + off
                    v = data_byte[i:i + 4]
                    v_colours.append([v[2] / div_by, v[1] / div_by, v[0] / div_by, v[3] / div_by])
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
            v_positions, v_normals, v_uvs, v_wxs, v_weights, v_colours, v_bones = [], [], [], [], [], [], []
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
        self._be_info_2()
        return self._cno_vertices()

    def eno(self):
        self._be_offsets()
        self._be_info_1()
        return self._eno_vertices()

    def ino(self):
        self._le_offsets()
        self._le_info_5()
        return self._ino_vertices()

    def lno(self):
        self._le_offsets()
        self._le_info_2()
        return self._lno_vertices()

    def sno(self):
        self._le_offsets()
        self._le_info_3()
        return self._sno_vertices()

    def uno(self):
        self._le_offsets()
        self._le_info_4()
        return self._uno_vertices()

    def xno(self):
        self._le_offsets()
        self._le_info_1()
        return self._xno_vertices()

    def zno(self):
        self._le_offsets()
        self._le_info_1()
        return self._zno_vertices()
