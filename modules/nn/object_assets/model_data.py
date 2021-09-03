from dataclasses import dataclass

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "n_start"
    ]

    def __init__(self, var, n_start):
        self.f, self.start, self.format_type, self.debug = var
        self.n_start = n_start

    @dataclass
    class ModelInfo:
        __slots__ = [
            "bounds_position", "bounds_scale", "material_count", "material_offset", "vertex_count", "vertex_offset",
            "face_count", "face_offset", "bone_count", "bone_offset", "bone_used_count",
            "mesh_sets", "mesh_count", "mesh_offset"
        ]
        bounds_position: Tuple[float, ...]
        bounds_scale: float
        material_count: int
        material_offset: int
        vertex_count: int
        vertex_offset: int
        face_count: int
        face_offset: int
        bone_count: int
        bone_offset: int
        bone_used_count: int
        mesh_sets: int
        mesh_count: list
        mesh_offset: list

    def le_full(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4)
        mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0])

        if b_off > n_start + 32:  # make sure pointers are fine
            start = n_start + 32 - b_off
            if not m_sets:
                start = n_start + 16 - b_off
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets)

        mi.mesh_count = var[1::5]
        mi.mesh_offset = var[2::5]

        return mi, start

    def be_full(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4, ">")
        mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12, ">")

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0])

        if b_off > n_start + 32:  # make sure pointers are fine
            start = n_start + 32 - b_off
            if not m_sets:
                start = n_start + 16 - b_off
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets, ">")

        mi.mesh_count = var[1::5]
        mi.mesh_offset = var[2::5]

        return mi, start

    def le_semi(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4)
        mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0])

        if b_off > n_start + 16:  # make sure pointers are fine
            start = n_start + 16 - b_off
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets)

        mi.mesh_count = var[1::5]
        mi.mesh_offset = var[2::5]

        return mi, start

    def be_semi(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4, ">")
        mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12, ">")

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0])

        if b_off > n_start + 16:  # make sure pointers are fine
            start = n_start + 16 - b_off
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets, ">")

        mi.mesh_count = var[1::5]
        mi.mesh_offset = var[2::5]

        return mi, start

    def le_ino(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4)
        if self.format_type == "SonicTheHedgehog4EpisodeI_I":
            (mats, mat_off, _, verts, v_off, _,
             faces, f_off, _,
             bones, _, b_off, _, b_used,
             m_sets, off) = read_int_tuple(f, 16)

            mi = self.ModelInfo(
                bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
                b_used, m_sets, [0], [0])

            if b_off > n_start + 16:  # make sure pointers are fine
                start = n_start + 16 - b_off
                if not m_sets:
                    mi.vertex_count = mi.face_count = 0
                    mi.vertex_offset = mi.face_offset = - start
                    return mi, start

            f.seek(off + start)
            var = read_int_tuple(f, 6 * m_sets)

            mi.mesh_count = var[1::6]
            mi.mesh_offset = var[2::6]
        else:
            mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

            mi = self.ModelInfo(
                bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
                b_used, m_sets, [0], [0])

            if b_off > n_start + 16:  # make sure pointers are fine
                start = n_start + 16 - b_off
                if not m_sets:
                    mi.vertex_count = mi.face_count = 0
                    mi.vertex_offset = mi.face_offset = - start
                    return mi, start

            f.seek(off + start)
            var = read_int_tuple(f, 5 * m_sets)

            mi.mesh_count = var[1::5]
            mi.mesh_offset = var[2::5]

        return mi, start

    def le_lno(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        if self.format_type == "SonicTheHedgehog4EpisodeII_L":
            f.seek(4, 1)
            bounds = read_float_tuple(f, 4)
            (mats, mat_off, _,
             verts, _, v_off, _,
             faces, _, f_off, _,
             bones, _, b_off, _, b_used,
             m_sets, off) = read_int_tuple(f, 18)

            mi = self.ModelInfo(
                bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
                b_used, m_sets, [0], [0])

            # we can't check if pointers are fine
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

            f.seek(off)
            var = read_int_tuple(f, 8 * m_sets)

            mi.mesh_count = var[1::8]
            mi.mesh_offset = var[2::8]
            start = 0
        else:
            bounds = read_float_tuple(f, 4)
            mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

            mi = self.ModelInfo(
                bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
                b_used, m_sets, [0], [0])

            if b_off > n_start + 16:  # make sure pointers are fine
                start = n_start + 16 - b_off
                if not m_sets:
                    mi.vertex_count = mi.face_count = 0
                    mi.vertex_offset = mi.face_offset = - start
                    return mi, start

            f.seek(off + start)
            var = read_int_tuple(f, 5 * m_sets)

            mi.mesh_count = var[1::5]
            mi.mesh_offset = var[2::5]

        return mi, start
