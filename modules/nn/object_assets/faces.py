from dataclasses import dataclass
from enum import Flag

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "face_set_count", "face_info", "face_strip_list", "face_list", "uv_list", "norm_list", "col_list"
    ]

    def __init__(self, var, face_set_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.face_set_count = face_set_count
        self.face_info = []
        self.face_strip_list = []
        self.face_list = []
        self.uv_list = []
        self.norm_list = []
        self.col_list = []

    @dataclass
    class FaceInfo:
        __slots__ = ["face_short_count", "face_lens_count", "face_lens_offset", "face_offset"]
        face_short_count: Union[int, tuple]
        face_lens_count: int
        face_lens_offset: int
        face_offset: Union[int, tuple]

    def _le_offsets(self):  # 1, offset, 1, offset, ...
        return read_int_tuple(self.f, self.face_set_count * 2)[1::2]

    def _be_offsets(self):
        return read_int_tuple(self.f, self.face_set_count * 2, ">")[1::2]

    def _le_offsets_3(self):
        return read_int_tuple(self.f, self.face_set_count * 3)[1::3]

    def _le_offsets_4(self):
        return read_int_tuple(self.f, self.face_set_count * 4)[2::4]

    def _be_offsets_flags(self):
        var = read_int_tuple(self.f, self.face_set_count * 2, ">")
        return var[1::2], var[0::2]

    def _xno_zno_info(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            self.face_info.append(self.FaceInfo(read_int(f), read_int(f), read_int(f), read_int(f)))

    def _eno_info(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            self.face_info.append(self.FaceInfo(read_int(f, ">"), read_int(f, ">"), read_int(f, ">"), read_int(f, ">")))

    def _lno_info(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start)
            data = read_int_tuple(f, 8)
            self.face_info.append(self.FaceInfo(data[5], 0, 0, data[6]))

    def _lno_info_2(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start)
            data = read_int_tuple(f, 11)
            self.face_info.append(self.FaceInfo(data[9], 0, 0, data[10]))

    def _ino_info(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_len_off, _, face_off_off, face_off_count = read_int_tuple(f, 4)
            f.seek(face_len_off + self.start)
            face_len = read_int_tuple(f, face_off_count)
            f.seek(face_off_off + self.start)
            face_off = read_int_tuple(f, face_off_count)
            self.face_info.append(self.FaceInfo(face_len, 0, 0, face_off))

    def _ino_info_2(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_len_off, _, _, face_off_off, _, face_off_count = read_int_tuple(f, 6)
            f.seek(face_len_off + self.start)
            face_len = read_int_tuple(f, face_off_count)
            f.seek(face_off_off + self.start)
            face_off = read_int_tuple(f, face_off_count)
            self.face_info.append(self.FaceInfo(face_len, 0, 0, face_off))

    def _cno_info(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_len_off, _, face_off_off, face_off_count = read_int_tuple(f, 4, ">")
            f.seek(face_len_off + self.start)
            face_len = read_int_tuple(f, face_off_count, ">")
            f.seek(face_off_off + self.start)
            face_off = read_int_tuple(f, face_off_count, ">")
            self.face_info.append(self.FaceInfo(face_len, 0, 0, face_off))

    def _gno_info(self, info_offset, info_flag):
        f = self.f
        for t, offset in zip(info_flag, info_offset):
            f.seek(offset + self.start)
            flags = read_int(f, ">")
            if t == 4:
                face_off, face_len, face_off_2 = read_int_tuple(f, 3, ">")
                self.face_info.append(self.FaceInfo(face_len, flags, face_off_2, face_off))
            elif t == 0:
                face_off, face_len, face_off_2 = read_int_tuple(f, 3, ">")
                self.face_info.append(self.FaceInfo(face_len, flags, face_off_2, face_off))
            elif t == 65536:
                # not enough samples to verify what this 0x00 00 00 03 means
                # probably face index types (3 = three face sets, pos norm uv)
                # we will include it anyway
                # this seems like it's used in an older non-final version of the exporter
                self.face_info.append(self.FaceInfo(
                    read_int(f, ">"), read_int(f, ">"), read_int(f, ">"), read_int(f, ">")))

    def _xno_zno_strip(self):
        f = self.f
        for info in self.face_info:
            f.seek(info.face_lens_offset + self.start)
            self.face_strip_list.append(read_short_tuple(f, info.face_lens_count))

    def _eno_strip(self):
        f = self.f
        for info in self.face_info:
            f.seek(info.face_lens_offset + self.start)
            self.face_strip_list.append(read_short_tuple(f, info.face_lens_count, ">"))

    def _xno_zno_indices(self):
        f = self.f
        for index in range(len(self.face_info)):
            info = self.face_info[index]
            face_list_mesh = []
            f.seek(info.face_offset + self.start)
            for face_count in self.face_strip_list[index]:  # for all strips in that sub mesh
                face_list = read_short_tuple(f, face_count)
                face_count -= 2
                for loop in range(face_count // 2):
                    loop *= 2
                    face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                    face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
                if face_count % 2 != 0:
                    face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))
            self.face_list.append(face_list_mesh)

    def _eno_indices(self):
        f = self.f
        for index in range(len(self.face_info)):  # for all sub meshes
            info = self.face_info[index]
            face_list_mesh = []
            f.seek(info.face_offset + self.start)
            for i in range(info.face_lens_count):  # for all strips in that sub mesh
                face_count = self.face_strip_list[index][i]
                face_list = read_short_tuple(f, face_count, ">")
                face_count -= 2
                for loop in range(face_count // 2):
                    loop *= 2
                    face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                    face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
                if face_count % 2 != 0:
                    face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))
            self.face_list.append(face_list_mesh)

    def _lno_indices(self):
        f = self.f
        for info in self.face_info:
            face_list_mesh = []
            f.seek(info.face_offset + self.start)

            face_count = info.face_short_count // 2  # they store count in bytes, not count of faces
            face_list = read_short_tuple(f, face_count)
            face_count -= 2
            for loop in range(face_count // 2):
                loop *= 2
                face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
            if face_count % 2 != 0:
                face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))

            self.face_list.append(face_list_mesh)

    def _cno_indices(self):
        f = self.f
        for info in self.face_info:  # for all sub meshes
            face_list_mesh = []
            for i in range(len(info.face_short_count)):  # for each tri strip
                f.seek(info.face_offset[i] + self.start)
                face_count = info.face_short_count[i]
                face_list = unpack(">" + str(face_count) + "h", f.read(face_count * 2))
                if -1 in face_list:
                    # null terminated tri strips ?? in s4e2 cno ?? its more likely than you think
                    split_indices = [i + 1 for i, x in enumerate(face_list) if x == -1]
                    strips = [face_list[i:j] for i, j in zip([0] + split_indices, split_indices + [None])]
                    if strips[-1]:
                        strips[-1] = list(strips[-1]) + [-1]
                    strips = [s[:-1] for s in strips if s]
                    for face_strip in strips:
                        face_count = len(face_strip)
                        face_count -= 2
                        for loop in range(face_count // 2):
                            loop *= 2
                            face_list_mesh.append((face_strip[loop], face_strip[loop + 1], face_strip[loop + 2]))
                            face_list_mesh.append((face_strip[loop + 2], face_strip[loop + 1], face_strip[loop + 3]))
                        if face_count % 2 != 0:
                            face_list_mesh.append((face_strip[- 3], face_strip[- 2], face_strip[- 1]))
                else:
                    face_count -= 2
                    for loop in range(face_count // 2):
                        loop *= 2
                        face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                        face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
                    if face_count % 2 != 0:
                        face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))
            self.face_list.append(face_list_mesh)

    def _ino_indices(self):
        f = self.f
        for info in self.face_info:  # for all sub meshes
            face_list_mesh = []
            for i in range(len(info.face_short_count)):  # for each tri strip
                f.seek(info.face_offset[i] + self.start)
                face_count = info.face_short_count[i]
                face_list = read_short_tuple(f, face_count)
                face_count -= 2
                for loop in range(face_count // 2):
                    loop *= 2
                    face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                    face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
                if face_count % 2 != 0:
                    face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))
            self.face_list.append(face_list_mesh)

    def _gno_indices(self, info_flag):

        class ExtractFaces:
            def __init__(self, face_list, face_count, multi):
                self.face_list = face_list
                self.face_count = face_count
                self.multi = multi

            def extract(self, off):
                face_list = self.face_list
                multi = self.multi
                extracted = []
                for face in range(self.face_count - 2):
                    f1, f2, f3 = \
                        face_list[(face + 0) * multi + off], \
                        face_list[(face + 1) * multi + off], \
                        face_list[(face + 2) * multi + off]
                    if face & 1:
                        extracted.append((f1, f2, f3))
                    else:
                        extracted.append((f2, f1, f3))
                return extracted, off + 1

        # most use this setting
        def faces_type_4():
            f.seek(info.face_offset + self.start + 20)
            face_flags = read_byte(f, ">")
            face_start = read_byte(f, ">")

            class FaceFlags(Flag):
                # byte 1
                col = face_flags >> 0 & 1
                byte1bit2 = face_flags >> 1 & 1
                norm = face_flags >> 2 & 1
                byte1bit4 = face_flags >> 3 & 1
                uvs = face_flags >> 4 & 1
                wxs = face_flags >> 5 & 1
                byte1bit7 = face_flags >> 6 & 1
                byte1bit8 = face_flags >> 7 & 1

                # byte 2

            while face_start == 153:
                face_count = read_short(f, ">")
                multi = 1

                if FaceFlags.norm:
                    multi += 1
                if FaceFlags.uvs:
                    multi += 1
                if FaceFlags.wxs:
                    multi += 2
                if FaceFlags.col:
                    multi += 1

                count = face_count * multi
                face_list = read_short_tuple(f, count, ">")
                face_start = read_byte(f, ">")

                extract_faces = ExtractFaces(face_list, face_count, multi)
                nonlocal face_list_mesh, norm_list_mesh, col_list_mesh, uv_list_mesh, uv2_list_mesh, uv3_list_mesh
                a, off = extract_faces.extract(0)
                face_list_mesh += a

                if FaceFlags.norm:
                    a, off = extract_faces.extract(off)
                    norm_list_mesh += a

                if FaceFlags.col:
                    a, off = extract_faces.extract(off)
                    col_list_mesh += a

                if FaceFlags.uvs:
                    a, off = extract_faces.extract(off)
                    uv_list_mesh += a

                    if FaceFlags.wxs:
                        a, off = extract_faces.extract(off)
                        uv2_list_mesh += a

                        a, off = extract_faces.extract(off)
                        uv3_list_mesh += a
                elif FaceFlags.wxs:
                    a, off = extract_faces.extract(off)
                    uv_list_mesh += a

                    a, off = extract_faces.extract(off)
                    uv2_list_mesh += a

        # sonic unleashed uses this occasionally
        def faces_type_0():
            f.seek(info.face_short_count + self.start)  # they have the offset and count position swapped
            counts = read_short_tuple(f, info.face_offset, ">")
            f.seek(info.face_lens_offset + self.start)

            # yes I know the variable name is not face flags
            face_flags = info.face_lens_count
            has_colours = False
            has_uvs = False
            has_wxs = False
            has_normals = False
            if face_flags & 2097152 == 2097152:
                has_colours = True
            if face_flags & 4194304 == 4194304:
                has_uvs = True
            if face_flags & 134217728 == 134217728:
                has_wxs = True
            if face_flags & 17825792 == 17825792:
                has_uvs = True
            if face_flags & 268435456 == 268435456:  # complex mesh
                if face_flags & 262144 == 262144:  # has normals
                    has_normals = True
            else:
                if face_flags & 589824 == 589824:  # has normals
                    has_normals = True

            multi = 1

            if has_normals:
                multi += 1
            if has_uvs:
                multi += 1
            if has_wxs:
                multi += 2
            if has_colours:
                multi += 1

            for face_count in counts:
                count = face_count * multi
                face_list = read_short_tuple(f, count, ">")

                extract_faces = ExtractFaces(face_list, face_count, multi)
                nonlocal face_list_mesh, norm_list_mesh, col_list_mesh, uv_list_mesh, uv2_list_mesh, uv3_list_mesh
                a, off = extract_faces.extract(0)
                face_list_mesh += a

                if has_normals:
                    a, off = extract_faces.extract(off)
                    norm_list_mesh += a

                if has_colours:
                    a, off = extract_faces.extract(off)
                    col_list_mesh += a

                if has_uvs:
                    a, off = extract_faces.extract(off)
                    uv_list_mesh += a

                    if has_wxs:
                        a, off = extract_faces.extract(off)
                        uv2_list_mesh += a

                        a, off = extract_faces.extract(off)
                        uv3_list_mesh += a
                elif has_wxs:
                    a, off = extract_faces.extract(off)
                    uv_list_mesh += a

                    a, off = extract_faces.extract(off)
                    uv2_list_mesh += a

        # probably one of the oldest versions of gno face storage
        def faces_type_65536():
            f.seek(info.face_lens_offset + self.start)
            face_strips = read_short_tuple(f, info.face_lens_count, ">")

            f.seek(info.face_offset + self.start)
            for strip in face_strips:
                indices = read_short_tuple(f, info.face_short_count * strip, ">")
                multi = info.face_short_count
                face_list = indices
                face_count = strip

                extract_faces = ExtractFaces(face_list, face_count, multi)
                nonlocal face_list_mesh, norm_list_mesh, uv_list_mesh
                a, off = extract_faces.extract(0)
                face_list_mesh += a

                # not enough samples to know what the requirements are for any of these
                if multi == 3:
                    a, off = extract_faces.extract(off)
                    norm_list_mesh += a

                if multi == 3:
                    a, off = extract_faces.extract(off)
                    uv_list_mesh += a

        f = self.f
        for info, inf_flag in zip(self.face_info, info_flag):  # for all sub meshes
            face_list_mesh = []
            uv_list_mesh = []
            uv2_list_mesh = []
            uv3_list_mesh = []
            norm_list_mesh = []
            col_list_mesh = []
            if inf_flag == 4:
                faces_type_4()
            elif inf_flag == 0:
                faces_type_0()
            elif inf_flag == 65536:
                faces_type_65536()

            self.face_list.append(face_list_mesh)
            self.col_list.append(col_list_mesh)
            self.norm_list.append(norm_list_mesh)
            self.uv_list.append((uv_list_mesh, uv2_list_mesh, uv3_list_mesh))

    def xno_zno(self):
        info_offset = self._le_offsets()
        self._xno_zno_info(info_offset)
        self._xno_zno_strip()
        self._xno_zno_indices()
        return self.face_list

    def eno(self):
        info_offset = self._be_offsets()
        self._eno_info(info_offset)
        self._eno_strip()
        self._eno_indices()
        return self.face_list

    def lno(self):
        info_offset = self._le_offsets()
        self._lno_info(info_offset)
        self._lno_indices()
        return self.face_list

    def lno_s4e2(self):
        info_offset = self._le_offsets_4()
        self._lno_info_2(info_offset)
        self._lno_indices()
        return self.face_list

    def ino(self):
        if self.format_type == "SonicTheHedgehog4EpisodeI_I":
            info_offset = self._le_offsets_3()
            self._ino_info_2(info_offset)
            self._ino_indices()
        else:
            info_offset = self._le_offsets()
            self._ino_info(info_offset)
            self._ino_indices()
        return self.face_list

    def cno(self):
        info_offset = self._be_offsets()
        self._cno_info(info_offset)
        self._cno_indices()
        return self.face_list

    def gno(self):
        info_offset, info_flag = self._be_offsets_flags()
        self._gno_info(info_offset, info_flag)
        self._gno_indices(info_flag)
        return self.face_list, self.uv_list, self.norm_list, self.col_list


class Write:
    __slots__ = [
        "f", "format_type", "meshes", "nof0_offsets", "face_offsets"
    ]

    def __init__(self, f, format_type, meshes, nof0_offsets):
        self.f = f
        self.format_type = format_type
        self.meshes = meshes
        self.nof0_offsets = nof0_offsets
        self.face_offsets = []

    def _xno_indices(self):
        f = self.f
        for i, m in enumerate(self.meshes):
            if not m:
                continue
            face_list = m.faces
            for face_info in face_list:
                info = [len(face_info.faces), 1, f.tell()]
                write_short(f, "<", len(face_info.faces))
                info.append(f.tell())
                for face in face_info.faces:
                    write_short(f, "<", face)
                write_aligned(f, 4)
                self.face_offsets.append(info)

    def _xno_info(self):
        f = self.f
        new_offs = []
        for i in self.face_offsets:
            new_offs.append(f.tell())
            write_integer(f, "<", 18448, i[0], i[1])
            self.nof0_offsets.append(f.tell())
            self.nof0_offsets.append(f.tell() + 4)
            write_integer(f, "<", i[2], i[3], 0, 0, 0)
        self.face_offsets = new_offs

    def _gno_indices(self):
        f = self.f
        write_aligned(f, 32)
        for i, m in enumerate(self.meshes):
            if not m:
                continue
            face_list = m.faces
            for face_info in face_list:
                start = f.tell()
                write_integer(f, ">", 139460608)

                # this whole section is a guess
                face_fl = 0
                if face_info.normals_type:
                    face_fl = face_fl | 24
                if face_info.colours_type:
                    face_fl = face_fl | 96
                if face_info.uvs_type:
                    face_fl = face_fl | 6
                if not face_info.colours_type:
                    face_fl = face_fl | 6  # i really dont understand these flags
                write_short(f, "<", face_fl)
                write_short(f, ">", 2144)

                if face_info.has_wx:
                    write_integer(f, ">", 15)
                elif face_info.uvs_type:
                    write_integer(f, ">", 3)
                else:
                    write_integer(f, ">", 0)

                write_integer(f, ">", 268435472, 134217728)

                face_flags = 0
                face_type_count = 1

                if face_info.colours_type:
                    face_flags = face_flags | 1
                    face_type_count += 1
                if face_info.normals_type:
                    face_flags = face_flags | 4
                    face_type_count += 1
                if face_info.has_wx:
                    face_flags = face_flags | 32
                    face_type_count += 2
                elif face_info.uvs_type:
                    face_flags = face_flags | 16
                    face_type_count += 1

                write_byte(f, ">", face_flags, 153)
                write_short(f, ">", len(face_info.faces) // face_type_count)

                write_short(f, ">", *face_info.faces)

                write_aligned(f, 32)
                self.face_offsets.append((start, f.tell(), i, face_info))

    def _gno_info(self):
        f = self.f
        offsets = self.face_offsets
        self.face_offsets = []
        for offset in offsets:
            self.face_offsets.append(f.tell())
            a = 65536  # only position (does not include count bit)
            type_count = len([a for a in [
                True, offset[3].normals_type, offset[3].colours_type, offset[3].uvs_type, offset[3].has_wx
            ] if a])
            a = a | (43690 >> (16 - type_count*2))  # b10 = 1, b1010 = 2 etc.

            if offset[3].colours_type:
                a = a | 2097152
            if offset[3].uvs_type:
                a = a | 4194304
            if offset[3].has_wx:
                a = a | 134217728
            if offset[2] in {1, 3}:  # complex
                a = a | 268435456
                if offset[3].normals_type:
                    a = a | 262144
            else:  # simple mesh
                if offset[3].normals_type:
                    a = a | 589824
                if type_count > 2:
                    a = a | 4194304

            write_integer(f, ">", a)
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", offset[0], offset[1] - offset[0], 0)

    def _be_offsets_flags(self):
        f = self.f
        for a in self.face_offsets:
            write_integer(f, ">", 4)
            self.nof0_offsets.append(f.tell())
            write_integer(f, ">", a)

    def _le_offsets(self):
        f = self.f
        for a in self.face_offsets:
            write_integer(f, "<", 1)
            self.nof0_offsets.append(f.tell())
            write_integer(f, "<", a)

    def gno(self):
        self._gno_indices()
        self._gno_info()
        face_offset = self.f.tell()
        self._be_offsets_flags()
        return face_offset, self.nof0_offsets

    def xno(self):
        self._xno_indices()
        self._xno_info()
        face_offset = self.f.tell()
        self._le_offsets()
        return face_offset, self.nof0_offsets
