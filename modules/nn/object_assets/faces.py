from dataclasses import dataclass

from ...util import *


class Read:
    __slots__ = [
        "f", "start", "format_type", "debug",
        "face_set_count", "face_info", "face_strip_list", "face_list"
    ]

    def __init__(self, var, face_set_count: int):
        self.f, self.start, self.format_type, self.debug = var
        self.face_set_count = face_set_count
        self.face_info = []
        self.face_strip_list = []
        self.face_list = []

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

    def le_1(self):
        info_offset = self._le_offsets()
        self._le_info_1(info_offset)
        self._le_strip_1()
        self._le_indices_1()
        return self.face_list

    def be_1(self):
        info_offset = self._be_offsets()
        self._be_info_1(info_offset)
        self._be_strip_1()
        self._be_indices_1()
        return self.face_list

    def le_2(self):
        info_offset = self._le_offsets()
        self._le_info_2(info_offset)
        self._le_indices_2()
        return self.face_list

    def be_2(self):
        info_offset = self._be_offsets()
        self._be_info_2(info_offset)
        self._be_indices_2()
        return self.face_list
