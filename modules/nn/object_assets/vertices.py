from dataclasses import dataclass

from ...util import *


class Read:
    def __init__(self, f: BinaryIO, post_nxif: int, format_type: str, vertex_buffer_count: int):
        self.f = f
        self.post_nxif = post_nxif
        self.format_type = format_type
        self.vertex_buffer_count = vertex_buffer_count
        self.vertex_mesh_offset = []
        self.mesh_info = []

    @dataclass
    class MeshData:
        vertex_block_type: Any
        vertex_block_size: Any
        vertex_count: int
        vertex_offset: Any
        bone_count_complex: int
        bone_list_complex: tuple

    @dataclass
    class VertexData:
        positions: list
        weights: list
        bone_list_indices: list
        normals: list
        uvs: list
        wxs: list
        colours: list
        normals2: list
        normals3: list

    def _le_offsets(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2)[1::2]

    def _be_offsets(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_int_tuple(self.f, self.vertex_buffer_count * 2, ">")[1::2]

    def _le_info_1(self):
        f = self.f
        post_nxif = self.post_nxif
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + post_nxif)
            block_type_list.append(unpack(">Q", f.read(8))[0])  # python gives back as big endian so countering
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5)
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)
        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + post_nxif
            if offset > 0:  # actually get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    self.MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_int_tuple(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    self.MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                                  self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _be_info_1(self):
        f = self.f
        post_nxif = self.post_nxif
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + post_nxif)
            block_type_list.append(unpack(">Q", f.read(8))[0])
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5, ">")
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)

        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + post_nxif
            if offset > 0:  # actually get bones for meshes with >1 bone
                f.seek(offset)
                self.mesh_info.append(
                    self.MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_int_tuple(f, bone_count_list[i], ">")))
            else:
                self.mesh_info.append(
                    self.MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                                  self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _be_info_2(self):
        f = self.f
        post_nxif = self.post_nxif
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for offset in self.vert_info_offset:
            f.seek(offset + post_nxif)
            block_type_list.append(read_int(f, ">"))
            size, count, offset, b_count, b_offset = read_int_tuple(f, 5, ">")
            block_size_list.append(size)
            vertex_count_list.append(count)
            self.vertex_mesh_offset.append(offset)
            bone_count_list.append(b_count)  # if > 1 bone its stored here
            bone_offset_complex.append(b_offset)

        for i in range(len(bone_offset_complex)):
            offset = bone_offset_complex[i] + post_nxif
            if offset > 0:  # get bones
                f.seek(offset)
                self.mesh_info.append(
                    self.MeshData(
                        block_type_list[i], block_size_list[i], vertex_count_list[i],
                        self.vertex_mesh_offset[i], bone_count_list[i], read_short_tuple(f, bone_count_list[i], ">")))
            else:
                self.mesh_info.append(
                    self.MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                                  self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _le_info_2(self):
        f = self.f
        post_nxif = self.post_nxif
        for offset in self.vert_info_offset:
            f.seek(offset + post_nxif + 4)
            vertex_count, info_count, info_offset = read_int_tuple(f, 3)
            f.seek(8, 1)
            v_bone_count, v_bone_off = read_int_tuple(f, 2)
            f.seek(v_bone_off + post_nxif)
            v_bone_list = read_short_tuple(f, v_bone_count)

            f.seek(info_offset + post_nxif)
            v_offset = []
            v_format = []
            v_format_size = []
            det_format = {
                1: "pos", 8: "norm", 64: "unknown", 128: "unknown", 256: "uv", 2: "weight", 4: "bone"
            }

            for _ in range(info_count):
                data = read_int_tuple(f, 5)
                v_offset.append(data[-1])
                v_format.append(det_format[data[0]])
                v_format_size.append(data[-2])

            self.mesh_info.append(self.MeshData(
                v_format, v_format_size, vertex_count, v_offset, v_bone_count, v_bone_list))

    def _le_info_3(self):
        for offset in self.vert_info_offset:
            self.f.seek(offset + self.post_nxif)
            self.vertex_mesh_offset.append(read_int_tuple(self.f, 5))

    def _le_vertices_1(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def pos(is_pos):
                if is_pos:
                    v_pos_list.append(read_float_tuple(f, 3))

            def norm(is_norm):
                if is_norm:
                    v_norms_list.append(read_float_tuple(f, 3))

            def extra_norms(is_extra_norms):
                if is_extra_norms:
                    v_norms2_list.append(read_float_tuple(f, 3))
                    v_norms3_list.append(read_float_tuple(f, 3))

            def uv_wx(is_wx, is_uv):
                if is_wx:
                    v_uvs_list.append([read_float(f), - read_float(f) + 1])
                    v_wxs_list.append([read_float(f), - read_float(f) + 1])
                elif is_uv:
                    v_uvs_list.append([read_float(f), - read_float(f) + 1])

            def wei(is_wei, is_index):
                if is_wei:
                    w1, w2, w3 = read_float_tuple(f, 3)
                    if is_index:
                        b1, b2, b3, b4 = read_byte_tuple(f, 4)
                        v_b_index_list.append((b1, b2, b3, b4))
                        if b4:
                            v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                        elif b3:
                            v_b_wei_list.append((w1, w2, 1 - w1 - w2))
                        elif b2:
                            v_b_wei_list.append((w1, 1 - w1))
                        else:
                            v_b_wei_list.append((1,))
                    else:
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))

            def col(is_short, is_byte):  # colours stored as b g r a
                if is_short:
                    div_by = 65535
                    cols = read_short_tuple(f, 4)
                elif is_byte:
                    div_by = 255
                    cols = read_byte_tuple(f, 4)
                else:
                    return
                v_cols_list.append([cols[2] / div_by, cols[1] / div_by, cols[0] / div_by, cols[3] / div_by])

            def sonic_riders_x():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    if block_type >> 17 & 1:  # unknown float
                        f.seek(4, 1)
                    wei(BitFlags.weights, BitFlags.weight_indices)
                    norm(BitFlags.normal)
                    col(BitFlags.colour_short, BitFlags.colour_byte)
                    uv_wx(False, BitFlags.uv)

            def phantasy_star_universe_x():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    wei(BitFlags.weights, BitFlags.weight_indices)
                    norm(BitFlags.normal)
                    col(BitFlags.colour_short, BitFlags.colour_byte)
                    uv_wx(BitFlags.wx, BitFlags.uv)

            def sonic_2006_x():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    wei(BitFlags.weights, BitFlags.weight_indices)
                    norm(BitFlags.normal)
                    if BitFlags.colour_byte:
                        f.seek(4, 1)
                    uv_wx(BitFlags.wx, BitFlags.uv)  # wx assumed to exist
                    extra_norms(BitFlags.extra_normals)

            def sonic_4_episode_1_z():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    wei(BitFlags.weights, BitFlags.weight_indices)
                    norm(BitFlags.normal)
                    col(BitFlags.colour_short, BitFlags.colour_byte)
                    uv_wx(None, BitFlags.uv)
                    if BitFlags.wx:
                        f.seek(16, 1)
                    extra_norms(BitFlags.extra_normals)

            format_dict = {
                "SonicRiders_X": sonic_riders_x, "PhantasyStarUniverse_X": phantasy_star_universe_x,
                "Sonic2006_X": sonic_2006_x,
                "Sonic4Episode1_Z": sonic_4_episode_1_z,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []
            f.seek(self.vertex_mesh_offset[var] + self.post_nxif)
            vertex_count = self.mesh_info[var].vertex_count
            block_type = self.mesh_info[var].vertex_block_type
            from enum import Flag

            class BitFlags(Flag):
                # 000KC0NP 0WWW0000 000000QU 00000000  KC0NW0P0 000000QU 00000000 00000000 SR PC
                #  K = colours as shorts, not bytes Q = unknown, in psu Q is wx but srpc has only one float
                #  block order: POS Q WEIGH NORM COL UV SR PC
                # 0M00C0NP 0WWW0I02 0000000U 00000000  0C0NW0P0 000W000U 00000000 00000000 06
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
                extra_normals = block_type >> 48 & 1

            vert_block()
            vertex_data.append(
                self.VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    v_norms2_list, v_norms3_list))
        return vertex_data, self.mesh_info

    def _be_vertices_1(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def pos(is_pos):
                if is_pos:
                    v_pos_list.append(read_float_tuple(f, 3, ">"))

            def uv(is_uv):
                if is_uv:
                    f.seek(4, 1)
                    v_uvs_list.append([read_half(f, ">"), - read_half(f, ">") + 1])

            def wei(is_wei, is_index):
                if is_wei:
                    w1, w2, w3 = read_float_tuple(f, 3, ">")
                    if is_index:
                        b4, b3, b2, b1 = read_byte_tuple(f, 4, ">")
                        v_b_index_list.append((b1, b2, b3, b4))
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                    else:
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))

            def sonic_free_riders_e():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    wei(BitFlags.weights, BitFlags.index)
                    uv(BitFlags.uv)
                    if BitFlags.unk1:
                        f.seek(8, 1)
                    if BitFlags.unk2:
                        f.seek(4, 1)

            format_dict = {
                "SonicFreeRiders_E": sonic_free_riders_e,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []
            f.seek(self.vertex_mesh_offset[var] + self.post_nxif)
            vertex_count = self.mesh_info[var].vertex_count
            block_type = self.mesh_info[var].vertex_block_type
            from enum import Flag

            class BitFlags(Flag):
                # 00000000 00PP000P 0WWW0X80 80000P0P 00000000 00000000 000X000P 000PW0P0 sonic free riders
                # 00000000 00110010 01110110 10000101 00000000 00000000 00010010 00011010 ?? size 48
                # I didn't have enough samples to check if P is P or UV but guessed for 1 based on similar structures
                # order Pos Wei indeX Uv 8 (no idea but skip 8)

                position = block_type >> 1 & 1
                weights = block_type >> 3 & 1
                index = block_type >> 12 & 1
                uv = block_type >> 4 & 1
                unk1 = block_type >> 39 & 1
                unk2 = block_type >> 9 & 1

            vert_block()
            vertex_data.append(
                self.VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    v_norms2_list, v_norms3_list))
        return vertex_data, self.mesh_info

    def _be_vertices_2(self):
        f = self.f
        vertex_data = []

        def vert_block():
            def pos(is_pos):
                if is_pos:
                    v_pos_list.append(read_float_tuple(f, 3, ">"))

            def uv_wx(is_wx, is_uv):
                if is_wx:
                    v_uvs_list.append([read_float(f, ">"), - read_float(f, ">") + 1])
                    v_wxs_list.append([read_float(f, ">"), - read_float(f, ">") + 1])
                elif is_uv:
                    v_uvs_list.append([read_float(f, ">"), - read_float(f, ">") + 1])

            def wei(is_wei, is_index):
                if is_wei:
                    w1, w2, w3 = read_float_tuple(f, 3, ">")
                    if is_index:
                        b1, b2, b3, b4 = read_byte_tuple(f, 4, ">")
                        v_b_index_list.append((b1, b2, b3, b4))
                        if b4:
                            v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                        elif b3:
                            v_b_wei_list.append((w1, w2, 1 - w1 - w2))
                        elif b2:
                            v_b_wei_list.append((w1, 1 - w1))
                        else:
                            v_b_wei_list.append((1,))
                    else:
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))

            def house_of_the_dead_4_c():
                for _ in range(vertex_count):
                    pos(BitFlags.position)
                    wei(BitFlags.weights, BitFlags.indices)
                    if BitFlags.unknown:
                        f.seek(20, 1)
                    uv_wx(BitFlags.wx, BitFlags.uv)
                    if BitFlags.unknown:
                        f.seek(12, 1)
                    if BitFlags.unknown2:
                        f.seek(12, 1)

            format_dict = {
                "HouseOfTheDead4_C": house_of_the_dead_4_c,
            }
            format_dict[self.format_type]()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []
            f.seek(self.vertex_mesh_offset[var] + self.post_nxif)
            vertex_count = self.mesh_info[var].vertex_count
            block_type = self.mesh_info[var].vertex_block_type
            from enum import Flag

            class BitFlags(Flag):
                # 00000000 000?00XU 0000IW0? 0?0??0N/P house of the dead 4
                # either have U or X on - you shouldn't have both
                # order:
                # Pos Weights boneIndices ? Uvs wX ?
                # I only had samples with both W and I, so it may be WI instead of IW
                # I only had samples with all unknowns active - all unknowns have been assigned to the first ?
                # / is an unknown as well but I could actually identify the section size

                position = block_type & 1
                unknown2 = block_type >> 1 & 1
                uv = block_type >> 16 & 1
                wx = block_type >> 17 & 1
                weights = block_type >> 10 & 1
                indices = block_type >> 11 & 1
                unknown = block_type >> 3 & 1

            vert_block()
            vertex_data.append(
                self.VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    v_norms2_list, v_norms3_list))
        return vertex_data, self.mesh_info

    def _le_vertices_2(self):
        def pos():
            for _ in range(vertex_count):
                v_pos_list.append(read_float_tuple(f, 3))

        def norm():
            for _ in range(vertex_count):
                v_norms_list.append(read_float_tuple(f, 3))

        def uv():
            for _ in range(vertex_count):
                v_uvs_list.append(read_float_tuple(f, 2))

        def wei():
            for _ in range(vertex_count):
                var = [a / 255 for a in read_byte_tuple(f, block_size)]
                if len(var) > 1:
                    var.append(1 - sum(var))
                else:
                    var = (var[0], 1 - var[0])
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
                f.seek(info.vertex_offset[i] + self.post_nxif)
                block_type = info.vertex_block_type[i]
                block_size = info.vertex_block_size[i]
                block_type_func = {
                    "pos": pos, "norm": norm, "unknown": unknown, "uv": uv, "weight": wei, "bone": bone
                }
                block_type_func[block_type]()

            vertex_data.append(
                self.VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    v_norms2_list, v_norms3_list))
        return vertex_data, self.mesh_info

    def _le_vertices_3(self):
        def pos():
            for _ in range(vertex_count):
                v_pos_list.append(read_float_tuple(f, 3))

        def norm():
            for _ in range(vertex_count):
                v_norms_list.append(read_float_tuple(f, 3))

        def uv():
            for _ in range(vertex_count):
                v_uvs_list.append(read_float_tuple(f, 2))

        def unk1():
            f.seek(vertex_count * 6, 1)

        def unk2():
            f.seek(vertex_count * 4, 1)

        f = self.f
        post_info = self.post_nxif
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
                    self.VertexData(
                        v_pos_list, v_b_wei_list, v_b_index_list,
                        v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                        v_norms2_list, v_norms3_list))
            mesh_info.append(
                self.MeshData(None, None, 0, None, bone_count_complex, bone_list_complex))
            vertex_data.append(v_data)
        return vertex_data, mesh_info

    def le_1(self):
        self._le_offsets()
        self._le_info_1()
        return self._le_vertices_1()

    def le_2(self):
        self._le_offsets()
        self._le_info_2()
        return self._le_vertices_2()

    def le_3(self):
        self._le_offsets()
        self._le_info_3()
        return self._le_vertices_3()

    def be_1(self):
        self._be_offsets()
        self._be_info_1()
        return self._be_vertices_1()

    def be_2(self):
        self._be_offsets()
        self._be_info_2()
        return self._be_vertices_2()
