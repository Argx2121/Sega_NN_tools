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
            "mesh_sets", "mesh_type", "mesh_count", "mesh_offset"
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
        mesh_type: list
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
            b_used, m_sets, [0], [0], [0])

        if b_off > n_start + 32:  # make sure pointers are fine
            start = n_start + 32 - b_off
            if not m_sets:
                start = n_start + 16 - b_off
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets)

        mi.mesh_type = var[0::5]
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
            b_used, m_sets, [0], [0], [0])

        if b_off > n_start + 32:  # make sure pointers are fine
            start = n_start + 32 - b_off
            if not m_sets:
                start = n_start + 16 - b_off
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets, ">")

        mi.mesh_type = var[0::5]
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
            b_used, m_sets, [0], [0], [0])

        if b_off > n_start + 16:  # make sure pointers are fine
            start = n_start + 16 - b_off
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets)

        mi.mesh_type = var[0::5]
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
            b_used, m_sets, [0], [0], [0])

        if b_off > n_start + 16:  # make sure pointers are fine
            start = n_start + 16 - b_off
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets, ">")

        mi.mesh_type = var[0::5]
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
                b_used, m_sets, [0], [0], [0])

            if b_off > n_start + 16:  # make sure pointers are fine
                start = n_start + 16 - b_off
                if not m_sets:
                    mi.vertex_count = mi.face_count = 0
                    mi.vertex_offset = mi.face_offset = - start
                    return mi, start

            f.seek(off + start)
            var = read_int_tuple(f, 6 * m_sets)

            mi.mesh_type = var[0::6]
            mi.mesh_count = var[1::6]
            mi.mesh_offset = var[2::6]
        else:
            mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

            mi = self.ModelInfo(
                bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
                b_used, m_sets, [0], [0], [0])

            if b_off > n_start + 16:  # make sure pointers are fine
                start = n_start + 16 - b_off
                if not m_sets:
                    mi.vertex_count = mi.face_count = 0
                    mi.vertex_offset = mi.face_offset = - start
                    return mi, start

            f.seek(off + start)
            var = read_int_tuple(f, 5 * m_sets)

            mi.mesh_type = var[0::5]
            mi.mesh_count = var[1::5]
            mi.mesh_offset = var[2::5]

        return mi, start

    def le_lno(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        bounds = read_float_tuple(f, 4)
        mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12)

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0], [0])

        if b_off > n_start + 16:  # make sure pointers are fine
            start = n_start + 16 - b_off
            if not m_sets:
                mi.vertex_count = mi.face_count = 0
                mi.vertex_offset = mi.face_offset = - start
                return mi, start

        f.seek(off + start)
        var = read_int_tuple(f, 5 * m_sets)

        mi.mesh_type = var[0::5]
        mi.mesh_count = var[1::5]
        mi.mesh_offset = var[2::5]

        return mi, start

    def le_lno_s4e2(self):
        f = self.f
        start = self.start
        n_start = self.n_start
        f.seek(4, 1)
        bounds = read_float_tuple(f, 4)
        (mats, mat_off, _,
         verts, _, v_off, _,
         faces, _, f_off, _,
         bones, _, b_off, _, b_used,
         m_sets, off) = read_int_tuple(f, 18)

        mi = self.ModelInfo(
            bounds[:3:], bounds[3], mats, mat_off, verts, v_off, faces, f_off, bones, b_off,
            b_used, m_sets, [0], [0], [0])

        # we can't check if pointers are fine
        if not m_sets:
            mi.vertex_count = mi.face_count = 0
            mi.vertex_offset = mi.face_offset = - start
            return mi, start

        f.seek(off)
        var = read_int_tuple(f, 8 * m_sets)

        mi.mesh_type = var[0::8]
        mi.mesh_count = var[1::8]
        mi.mesh_offset = var[2::8]
        start = 0

        return mi, start


class Write:
    __slots__ = [
        "f", "format_type", "model", "nof0_offsets", "offsets", "bone"
    ]

    def __init__(self, f, format_type, model, nof0_offsets, offsets, bone):
        self.f = f
        self.format_type = format_type
        self.model = model
        self.nof0_offsets = nof0_offsets
        self.offsets = offsets
        self.bone = bone

    def be(self):
        f = self.f
        model_data = self.model
        offsets = self.offsets
        info_offset = f.tell()

        mesh_set_count = len(model_data.meshes.simple_opaque) + len(model_data.meshes.complex_opaque) + \
                         len(model_data.meshes.simple_alpha) + len(model_data.meshes.complex_alpha) + \
                         len(model_data.meshes.simple_clip) + len(model_data.meshes.complex_clip)
        bone_used = self.bone
        vert_sets = 0

        for m in model_data.geometry:
            if not m:
                continue
            vert_sets += len(m.vertices)

        mesh_sets = 0
        if model_data.meshes.simple_opaque:
            mesh_sets += 1
        if model_data.meshes.complex_opaque:
            mesh_sets += 1
        if model_data.meshes.simple_alpha:
            mesh_sets += 1
        if model_data.meshes.complex_alpha:
            mesh_sets += 1
        if model_data.meshes.simple_clip:
            mesh_sets += 1
        if model_data.meshes.complex_clip:
            mesh_sets += 1

        write_float(f, ">", model_data.center[0], model_data.center[1], model_data.center[2], model_data.radius)
        write_integer(f, ">", len(model_data.materials.material_list), offsets[1])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(f, ">", vert_sets, offsets[2])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(f, ">", mesh_set_count, offsets[3])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(
            f, ">", len(model_data.bones), model_data.bone_depth, offsets[0], len(bone_used))
        self.nof0_offsets.append(f.tell() - 8)
        write_integer(f, ">", mesh_sets, offsets[4], len(model_data.materials.texture_list))
        self.nof0_offsets.append(f.tell() - 8)
        # mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12, ">")

        return info_offset, self.nof0_offsets

    def le(self):
        f = self.f
        model_data = self.model
        offsets = self.offsets
        info_offset = f.tell()

        mesh_set_count = len(model_data.meshes.simple_opaque) + len(model_data.meshes.complex_opaque) + \
                         len(model_data.meshes.simple_alpha) + len(model_data.meshes.complex_alpha)
        bone_used = self.bone
        vert_sets = 0

        for m in model_data.geometry:
            if not m:
                continue
            vert_sets += len(m.vertices)  # todo missing indent? nest

        mesh_sets = 0
        if model_data.meshes.simple_opaque:
            mesh_sets += 1
        if model_data.meshes.complex_opaque:
            mesh_sets += 1
        if model_data.meshes.simple_alpha:
            mesh_sets += 1
        if model_data.meshes.complex_alpha:
            mesh_sets += 1

        write_float(f, "<", model_data.center[0], model_data.center[1], model_data.center[2], model_data.radius)
        write_integer(f, "<", len(model_data.materials.material_list), offsets[1])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(f, "<", vert_sets, offsets[2])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(f, "<", mesh_set_count, offsets[3])
        self.nof0_offsets.append(f.tell() - 4)
        write_integer(
            f, "<", len(model_data.bones), model_data.bone_depth, offsets[0], len(bone_used))
        self.nof0_offsets.append(f.tell() - 8)
        write_integer(f, "<", mesh_sets, offsets[4], len(model_data.materials.texture_list))
        self.nof0_offsets.append(f.tell() - 8)
        # mats, mat_off, verts, v_off, faces, f_off, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12, ">")

        return info_offset, self.nof0_offsets