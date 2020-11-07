from dataclasses import dataclass

from ...util import *


class Read:
    def __init__(self, f: BinaryIO, post_nxif: int, start_obj: int):
        self.f = f
        self.post_nxif = post_nxif
        self.start_obj = start_obj

    @dataclass
    class ModelInfo:
        material_count: int
        material_offset: int
        vertex_buffer_count: int
        vertex_buffer_offset: int
        face_set_count: int
        face_set_offset: int
        bone_count: int
        bone_offset: int
        bone_used_count: int
        mesh_sets_count: int
        mesh_data_count: list
        mesh_data_offset: list

    def le_full(self):
        f = self.f
        start_obj = self.start_obj
        read_float_tuple(f, 4)  # hit box
        mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset = read_int_tuple(f, 6)
        b_count, _, b_offset, b_used_count, m_sets_count = read_int_tuple(f, 5)
        m_data_count, m_data_offset = [], []
        # make sure pointers are fine
        if b_offset > self.post_nxif + 32:
            self.post_nxif = start_obj + 32 - b_offset
            if not m_sets_count:
                self.post_nxif = start_obj + 16 - b_offset
                return self.ModelInfo(mat_count, mat_offset, 0, - self.post_nxif, 0, - self.post_nxif, b_count,
                                      b_offset, b_used_count, m_sets_count, [0], [0]), self.post_nxif
        # get data just before hit box
        offset0101 = read_int(f)
        f.seek(offset0101 + self.post_nxif + 4)
        for _ in range(m_sets_count):
            m_data_count.append(read_int(f))
            m_data_offset.append(read_int(f))
            f.seek(12, 1)

        return self.ModelInfo(
            mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset, b_count, b_offset,
            b_used_count, m_sets_count, m_data_count, m_data_offset), self.post_nxif

    def le_semi(self):
        f = self.f
        start_obj = self.start_obj
        read_float_tuple(f, 4)  # hit box
        mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset = read_int_tuple(f, 6)
        b_count, _, b_offset, b_used_count, m_sets_count = read_int_tuple(f, 5)
        m_data_count, m_data_offset = [], []
        # make sure pointers are fine
        if b_offset > self.post_nxif + 16:
            self.post_nxif = start_obj + 16 - b_offset
            if not m_sets_count:
                return self.ModelInfo(mat_count, mat_offset, 0, - self.post_nxif, 0, - self.post_nxif, b_count,
                                      b_offset, b_used_count, m_sets_count, [0], [0]), self.post_nxif
        # get data just before hit box
        offset0101 = read_int(f)
        f.seek(offset0101 + self.post_nxif + 4)
        for _ in range(m_sets_count):
            m_data_count.append(read_int(f))
            m_data_offset.append(read_int(f))
            f.seek(12, 1)

        return self.ModelInfo(
            mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset, b_count, b_offset,
            b_used_count, m_sets_count, m_data_count, m_data_offset), self.post_nxif

    def be_full(self):
        f = self.f
        start_obj = self.start_obj
        read_float_tuple(f, 4, ">")  # hit box
        mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset = read_int_tuple(f, 6, ">")
        b_count, _, b_offset, b_used_count, m_sets_count = read_int_tuple(f, 5, ">")
        m_data_count, m_data_offset = [], []
        # make sure pointers are fine
        if b_offset > self.post_nxif + 32:
            self.post_nxif = start_obj + 32 - b_offset
            if not m_sets_count:
                self.post_nxif = start_obj + 16 - b_offset
                return self.ModelInfo(mat_count, mat_offset, 0, - self.post_nxif, 0, - self.post_nxif, b_count,
                                      b_offset, b_used_count, m_sets_count, [0], [0]), self.post_nxif
        # get data just before hit box
        offset0101 = read_int(f, ">")
        f.seek(offset0101 + self.post_nxif + 4)
        for _ in range(m_sets_count):
            m_data_count.append(read_int(f, ">"))
            m_data_offset.append(read_int(f, ">"))
            f.seek(12, 1)

        return self.ModelInfo(
            mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset, b_count, b_offset,
            b_used_count, m_sets_count, m_data_count, m_data_offset), self.post_nxif

    def be_semi(self):
        f = self.f
        start_obj = self.start_obj
        read_float_tuple(f, 4, ">")  # hit box
        mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset = read_int_tuple(f, 6, ">")
        b_count, _, b_offset, b_used_count, m_sets_count = read_int_tuple(f, 5, ">")
        m_data_count, m_data_offset = [], []
        # make sure pointers are fine
        if b_offset > self.post_nxif + 16:
            self.post_nxif = start_obj + 16 - b_offset
            if not m_sets_count:
                return self.ModelInfo(mat_count, mat_offset, 0, - self.post_nxif, 0, - self.post_nxif, b_count,
                                      b_offset, b_used_count, m_sets_count, [0], [0]), self.post_nxif
        # get data just before hit box
        offset0101 = read_int(f, ">")
        f.seek(offset0101 + self.post_nxif + 4)
        for _ in range(m_sets_count):
            m_data_count.append(read_int(f, ">"))
            m_data_offset.append(read_int(f, ">"))
            f.seek(12, 1)

        return self.ModelInfo(
            mat_count, mat_offset, m_01_count, m_01_offset, f_01_count, f_01_offset, b_count, b_offset,
            b_used_count, m_sets_count, m_data_count, m_data_offset), self.post_nxif
