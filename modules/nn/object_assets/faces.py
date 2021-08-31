from dataclasses import dataclass
from enum import Flag

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "face_set_count", "face_info", "face_strip_list", "face_list", "uv_list", "wx_list", "norm_list", "col_list"
    ]

    def __init__(self, var, face_set_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.face_set_count = face_set_count
        self.face_info = []
        self.face_strip_list = []
        self.face_list = []
        self.uv_list = []
        self.wx_list = []
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

    def _be_offsets_flags(self):
        var = read_int_tuple(self.f, self.face_set_count * 2, ">")
        return var[1::2], var[0::2]

    def _le_info_1(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            self.face_info.append(self.FaceInfo(read_int(f), read_int(f), read_int(f), read_int(f)))

    def _be_info_1(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            self.face_info.append(self.FaceInfo(read_int(f, ">"), read_int(f, ">"), read_int(f, ">"), read_int(f, ">")))

    def _le_info_2(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start)
            data = read_int_tuple(f, 8)
            self.face_info.append(self.FaceInfo(data[5], 0, 0, data[6]))

    def _le_info_3(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_len_off, _, face_off_off, face_off_count = read_int_tuple(f, 4)
            f.seek(face_len_off + self.start)
            face_len = read_int_tuple(f, face_off_count)
            f.seek(face_off_off + self.start)
            face_off = read_int_tuple(f, face_off_count)
            self.face_info.append(self.FaceInfo(face_len, 0, 0, face_off))

    def _be_info_2(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_len_off, _, face_off_off, face_off_count = read_int_tuple(f, 4, ">")
            f.seek(face_len_off + self.start)
            face_len = read_int_tuple(f, face_off_count, ">")
            f.seek(face_off_off + self.start)
            face_off = read_int_tuple(f, face_off_count, ">")
            self.face_info.append(self.FaceInfo(face_len, 0, 0, face_off))

    def _be_info_3(self, info_offset):
        f = self.f
        for offset in info_offset:
            f.seek(offset + self.start + 4)
            face_off, face_len, face_off_2 = read_int_tuple(f, 3, ">")
            self.face_info.append(self.FaceInfo(face_len, 0, face_off_2, face_off))

    def _le_strip_1(self):
        f = self.f
        for info in self.face_info:
            f.seek(info.face_lens_offset + self.start)
            self.face_strip_list.append(read_short_tuple(f, info.face_lens_count))

    def _be_strip_1(self):
        f = self.f
        for info in self.face_info:
            f.seek(info.face_lens_offset + self.start)
            self.face_strip_list.append(read_short_tuple(f, info.face_lens_count, ">"))

    def _le_indices_1(self):
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

    def _be_indices_1(self):
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

    def _le_indices_2(self):
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

    def _be_indices_2(self):
        f = self.f
        for info in self.face_info:  # for all sub meshes
            face_list_mesh = []
            for i in range(len(info.face_short_count)):  # for each tri strip
                f.seek(info.face_offset[i] + self.start)
                face_count = info.face_short_count[i]
                face_list = read_short_tuple(f, face_count, ">")
                face_count -= 2
                for loop in range(face_count // 2):
                    loop *= 2
                    face_list_mesh.append((face_list[loop], face_list[loop + 1], face_list[loop + 2]))
                    face_list_mesh.append((face_list[loop + 2], face_list[loop + 1], face_list[loop + 3]))
                if face_count % 2 != 0:
                    face_list_mesh.append((face_list[- 3], face_list[- 2], face_list[- 1]))
            self.face_list.append(face_list_mesh)

    def _le_indices_3(self):
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

    def _be_indices_3(self, info_flag):
        def faces_flag():
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
                off = 0

                for face in range(face_count - 2):
                    f1, f2, f3 = \
                        face_list[(face + 0) * multi], \
                        face_list[(face + 1) * multi], \
                        face_list[(face + 2) * multi]
                    if face & 1:
                        face_list_mesh.append((f1, f2, f3))
                    else:
                        face_list_mesh.append((f2, f1, f3))
                off += 1

                if FaceFlags.norm:
                    for face in range(face_count - 2):
                        f1, f2, f3 = \
                            face_list[(face + 0) * multi + off], \
                            face_list[(face + 1) * multi + off], \
                            face_list[(face + 2) * multi + off]
                        if face & 1:
                            norm_list_mesh.append((f1, f2, f3))
                        else:
                            norm_list_mesh.append((f2, f1, f3))
                    off += 1

                if FaceFlags.col:
                    for face in range(face_count - 2):
                        f1, f2, f3 = \
                            face_list[(face + 0) * multi + off], \
                            face_list[(face + 1) * multi + off], \
                            face_list[(face + 2) * multi + off]
                        if face & 1:
                            col_list_mesh.append((f1, f2, f3))
                        else:
                            col_list_mesh.append((f2, f1, f3))
                    off += 1

                if FaceFlags.uvs:
                    for face in range(face_count - 2):
                        f1, f2, f3 = \
                            face_list[(face + 0) * multi + off], \
                            face_list[(face + 1) * multi + off], \
                            face_list[(face + 2) * multi + off]
                        if face & 1:
                            uv_list_mesh.append((f1, f2, f3))
                        else:
                            uv_list_mesh.append((f2, f1, f3))
                    off += 1

                if FaceFlags.wxs:
                    for face in range(face_count - 2):
                        f1, f2, f3 = \
                            face_list[(face + 0) * multi + off], \
                            face_list[(face + 1) * multi + off], \
                            face_list[(face + 2) * multi + off]
                        if face & 1:
                            uv_list_mesh.append((f1, f2, f3))
                        else:
                            uv_list_mesh.append((f2, f1, f3))
                    off += 1

                    for face in range(face_count - 2):
                        f1, f2, f3 = \
                            face_list[(face + 0) * multi + off], \
                            face_list[(face + 1) * multi + off], \
                            face_list[(face + 2) * multi + off]
                        if face & 1:
                            wx_list_mesh.append((f1, f2, f3))
                        else:
                            wx_list_mesh.append((f2, f1, f3))
                    off += 1

        def faces():
            f.seek(info.face_short_count + self.start)  # they have the offset and count position swapped
            counts = read_short_tuple(f, info.face_offset, ">")
            f.seek(info.face_lens_offset + self.start)

            for face_count in counts:
                face_list = read_short_tuple(f, face_count * 3, ">")
                face_l = face_list[0::3]
                for face in range(face_count - 2):
                    f1, f2, f3 = \
                        face_l[(face + 0)], \
                        face_l[(face + 1)], \
                        face_l[(face + 2)]
                    if face & 1:
                        face_list_mesh.append((f1, f2, f3))
                    else:
                        face_list_mesh.append((f2, f1, f3))

                face_l = face_list[1::3]
                for face in range(face_count - 2):
                    f1, f2, f3 = \
                        face_l[(face + 0)], \
                        face_l[(face + 1)], \
                        face_l[(face + 2)]
                    if face & 1:
                        col_list_mesh.append((f1, f2, f3))
                    else:
                        col_list_mesh.append((f2, f1, f3))

                face_l = face_list[2::3]
                for face in range(face_count - 2):
                    f1, f2, f3 = \
                        face_l[(face + 0)], \
                        face_l[(face + 1)], \
                        face_l[(face + 2)]
                    if face & 1:
                        uv_list_mesh.append((f1, f2, f3))
                    else:
                        uv_list_mesh.append((f2, f1, f3))

        f = self.f
        for info, inf_flag in zip(self.face_info, info_flag):  # for all sub meshes
            face_list_mesh = []
            uv_list_mesh = []
            wx_list_mesh = []
            norm_list_mesh = []
            col_list_mesh = []
            if inf_flag:
                faces_flag()
            else:
                faces()

            self.face_list.append(face_list_mesh)
            self.col_list.append(col_list_mesh)
            self.norm_list.append(norm_list_mesh)
            self.uv_list.append(uv_list_mesh)
            self.wx_list.append(wx_list_mesh)

    def xno_zno(self):
        info_offset = self._le_offsets()
        self._le_info_1(info_offset)
        self._le_strip_1()
        self._le_indices_1()
        return self.face_list

    def eno(self):
        info_offset = self._be_offsets()
        self._be_info_1(info_offset)
        self._be_strip_1()
        self._be_indices_1()
        return self.face_list

    def lno(self):
        info_offset = self._le_offsets()
        self._le_info_2(info_offset)
        self._le_indices_2()
        return self.face_list

    def ino(self):
        info_offset = self._le_offsets()
        self._le_info_3(info_offset)
        self._le_indices_3()
        return self.face_list

    def cno(self):
        info_offset = self._be_offsets()
        self._be_info_2(info_offset)
        self._be_indices_2()
        return self.face_list

    def gno(self):
        info_offset, info_flag = self._be_offsets_flags()
        self._be_info_3(info_offset)
        self._be_indices_3(info_flag)
        return self.face_list, self.uv_list, self.wx_list, self.norm_list, self.col_list
