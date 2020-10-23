from dataclasses import dataclass

from ...nn_util import *


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
        vertex_block_type: str
        vertex_block_size: int
        vertex_count: int
        vertex_offset: int
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

    def _info_offsets_type_1(self):  # 1, offset, 1, offset, ...
        self.vert_info_offset = read_multi_ints(self.f, self.vertex_buffer_count * 2)[1::2]

    def _info_type_1(self):
        f = self.f
        post_nxif = self.post_nxif
        block_type_list = []
        block_size_list = []
        vertex_count_list = []
        bone_count_list = []
        bone_offset_complex = []
        for var in range(self.vertex_buffer_count):
            f.seek(self.vert_info_offset[var] + post_nxif)
            block_type_list.append(unpack(">Q", f.read(8))[0])  # python gives back as big endian so countering
            size, count, offset, b_count, b_offset = read_multi_ints(f, 5)
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
                        self.vertex_mesh_offset[i], bone_count_list[i], read_multi_ints(f, bone_count_list[i])))
            else:
                self.mesh_info.append(
                    self.MeshData(block_type_list[i], block_size_list[i], vertex_count_list[i],
                                  self.vertex_mesh_offset[i], bone_count_list[i], ()))

    def _vertices_type_1(self):
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
                        b1, b2, b3, b4 = read_multi_bytes(f, 4)
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
                    cols = read_multi_shorts(f, 4)
                elif is_byte:
                    div_by = 255
                    cols = read_multi_bytes(f, 4)
                else:
                    return
                v_cols_list.append([cols[2] / div_by, cols[1] / div_by, cols[0] / div_by, cols[3] / div_by])

            # 000KC0NP 0WWW0000 000000QU 00000000  KC0NW0P0 000000QU 00000000 00000000 SR PC
            #  K = colours as shorts, not bytes Q = unknown, in psu Q is wx but srpc has only one float
            #  block order: POS Q WEIGH NORM COL UV SR PC
            # 0M00C0NP 0WWW0I02 0000000U 00000000  0C0NW0P0 000W000U 00000000 00000000 06
            #  M = 2 extra normal sets, I = bone indices
            # 00000001 00000000 00000011 00000000 00000010 00000011 00000000 00000000 s4e1
            # p, uw,

            # latest goes first and should be of the latest games format
            def latest_x():
                sonic_2006_x()

            def latest_z():
                sonic_4_episode_1_z()

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
                    col(BitFlags.colour_short, BitFlags.colour_byte)  # colours assumed to exist
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

            dict_x = {
                "SonicRiders_X": sonic_riders_x, "PhantasyStarUniverse_X": phantasy_star_universe_x,
                "Sonic2006_X": sonic_2006_x}
            dict_z = {
                "Sonic4Episode1_Z": sonic_4_episode_1_z}
            format_type = self.format_type
            if format_type[-1] == "X":
                if format_type in dict_x:
                    dict_x[format_type]()
                else:
                    latest_x()
            elif format_type[-1] == "Z":
                if format_type in dict_z:
                    dict_z[format_type]()
                else:
                    latest_z()

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []
            # parse vertices
            f.seek(self.vertex_mesh_offset[var] + self.post_nxif)
            # go through each sub meshes block size
            vertex_count = self.mesh_info[var].vertex_count
            block_type = self.mesh_info[var].vertex_block_type
            from enum import Flag

            class BitFlags(Flag):
                # generic
                uv = block_type >> 16 & 1
                position = block_type >> 25 & 1
                normal = block_type >> 28 & 1
                colour_short = block_type >> 31 & 1
                colour_byte = block_type >> 30 & 1
                weights = block_type >> 27 & 1
                weight_indices = block_type >> 50 & 1
                wx = block_type >> 17 & 1
                extra_normals = block_type >> 48 & 1
                # keep generic values here

            vert_block()
            vertex_data.append(
                self.VertexData(
                    v_pos_list, v_b_wei_list, v_b_index_list,
                    v_norms_list, v_uvs_list, v_wxs_list, v_cols_list,
                    v_norms2_list, v_norms3_list))
        return vertex_data, self.mesh_info

    def xbox(self):
        self._info_offsets_type_1()
        self._info_type_1()
        return self._vertices_type_1()
