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
            def pos(is_var):
                if is_var:
                    v_pos_list.append(read_float_tuple(f, 3))

            def norm(is_var):
                if is_var:
                    v_norms_list.append(read_float_tuple(f, 3))

            def uv(is_var):
                if is_var:
                    v_uvs_list.append([read_float(f), - read_float(f) + 1])

            def col_s():
                div_by = 65535
                cols = read_multi_shorts(f, 4)  # stored as b g r a
                return cols[2] / div_by, cols[1] / div_by, cols[0] / div_by, cols[3] / div_by

            def col_b():
                div_by = 255
                cols = read_multi_bytes(f, 4)
                return cols[2] / div_by, cols[1] / div_by, cols[0] / div_by, cols[3] / div_by

            # "000KC0NP 0WWW0000 000000QU 00000000  KC0NW0P0 000000QU 00000000 00000000" SR PC
            #  K = colours as shorts, not bytes
            #  block order: POS Q WEIGH NORM COL UV SR PC
            # "0M00C0NP 0WWW0I02 0000000U 00000000  0C0NW0P0 000W000U 00000000 00000000" 06
            #  M = 2 extra normal sets, I = bone indices

            if self.format_type == "srpc":
                for _ in range(vertex_count_pop):
                    pos(BitFlags.position)
                    if BitFlags.srpc_unknown:
                        f.seek(4, 1)
                    if BitFlags.weights:
                        w1, w2, w3 = read_float_tuple(f, 3)
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                    norm(BitFlags.normal)
                    if BitFlags.colour_short:
                        v_cols_list.append(col_s())
                    elif BitFlags.colour_byte:
                        v_cols_list.append(col_b())
                    uv(BitFlags.uv)

            elif self.format_type == "psu":
                for _ in range(vertex_count_pop):
                    pos(BitFlags.position)
                    if BitFlags.weights:
                        w1, w2, w3 = read_float_tuple(f, 3)
                        v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                    norm(BitFlags.normal)
                    if BitFlags.colour_short:
                        v_cols_list.append(col_s())
                    elif BitFlags.colour_byte:
                        v_cols_list.append(col_b())
                    if BitFlags.wx:
                        v_uvs_list.append([read_float(f), - read_float(f) + 1])
                        v_wxs_list.append([read_float(f), - read_float(f) + 1])
                    uv(BitFlags.uv)

            elif self.format_type == "s06":
                for _ in range(vertex_count_pop):
                    pos(BitFlags.position)
                    if v_b >> 27 & 1:
                        if v_b >> 50 & 1:
                            w1, w2, w3 = read_float_tuple(f, 3)
                            b1, b2, b3, b4 = read_multi_bytes(f, 4)
                            v_b_index_list.append((b1, b2, b3, b4))
                            if b4:
                                v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                            elif b3:
                                v_b_wei_list.append((w1, w2, 1 - w1 - w2, 0))
                            elif b2:
                                v_b_wei_list.append((w1, 1 - w1, 0, 0))
                            else:
                                v_b_wei_list.append((1, 0, 0, 0))
                        else:
                            w1, w2, w3 = read_float_tuple(f, 3)
                            v_b_wei_list.append((w1, w2, w3, 1 - w1 - w2 - w3))
                    norm(BitFlags.normal)
                    if BitFlags.colour_short:  # colours assumed to exist
                        v_cols_list.append(col_s())
                    elif BitFlags.colour_byte:  # strange colours
                        v_cols_list.append(col_b())
                    uv(BitFlags.uv)
                    if v_b >> 48 & 1:
                        v_norms2_list.append(read_float_tuple(f, 3))
                        v_norms3_list.append(read_float_tuple(f, 3))

        for var in range(self.vertex_buffer_count):  # for all sub meshes
            v_pos_list, v_norms_list, v_uvs_list, v_wxs_list, v_b_wei_list, v_cols_list = [], [], [], [], [], []
            v_b_index_list, v_norms2_list, v_norms3_list = [], [], []
            # parse vertices
            f.seek(self.vertex_mesh_offset[var] + self.post_nxif)
            # go through each sub meshes block size
            vertex_count_pop = self.mesh_info[var].vertex_count
            v_b = self.mesh_info[var].vertex_block_type
            from enum import Flag

            class BitFlags(Flag):
                # generic
                uv = v_b >> 16 & 1
                position = v_b >> 25 & 1
                normal = v_b >> 28 & 1
                colour_short = v_b >> 31 & 1
                colour_byte = v_b >> 30 & 1
                weights = v_b >> 27 & 1
                wx = v_b >> 17 & 1
                # specific
                srpc_unknown = v_b >> 17 & 1

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
