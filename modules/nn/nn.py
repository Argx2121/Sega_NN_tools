from dataclasses import dataclass

from ..nn import nn_unknown, nn_information_file, nn_texture_library, nn_effects, nn_node_names, \
    nn_object, nn_offset_file, nn_file_name, nn_end, nn_camera
from ..nn.nn_object import ModelData
from ...io import nn_import_data as nn_data
from ..util import *


class ReadNn:
    __slots__ = ["f", "filepath", "file_len", "format_type", "debug", "nn", "big_endian", "det_n"]

    def __init__(self, f, filepath, format_type, debug):
        self.f = f
        self.filepath = filepath
        self.file_len = os.path.getsize(self.filepath)
        self.format_type = format_type
        self.debug = debug
        self.nn = self.NnFile()
        self.big_endian = {"C", "E", "G"}
        self.det_n = {
            # specific
            "NCIF": self._info_1, "NEIF": self._info_1, "NGIF": self._info_1,
            "NIIF": self._info_1, "NLIF": self._info_1, "NSIF": self._info_1, "NUIF": self._info_1,
            "NXIF": self._info_1, "NZIF": self._info_1,

            "NCTL": self._tex_2, "NETL": self._tex_2, "NGTL": self._tex_2,
            "NITL": self._tex_1, "NLTL": self._tex_1, "NSTL": self._tex_1, "NUTL": self._tex_1,
            "NXTL": self._tex_1, "NZTL": self._tex_1,

            "NCNN": self._node_2, "NENN": self._node_2, "NGNN": self._node_2,
            "NINN": self._node_1, "NLNN": self._node_1, "NSNN": self._node_1, "NUNN": self._node_1,
            "NXNN": self._node_1, "NZNN": self._node_1,

            "NCOB": self._obj_c, "NEOB": self._obj_e, "NGOB": self._obj_g,
            "NIOB": self._obj_i, "NLOB": self._obj_l, "NSOB": self._obj_s, "NUOB": self._obj_u,
            "NXOB": self._obj_x, "NZOB": self._obj_z,

            # Data isn't applicable
            "NCEF": self._eff_1, "NEEF": self._eff_1, "NGEF": self._eff_1,
            "NIEF": self._eff_1, "NLEF": self._eff_1, "NSEF": self._eff_1, "NUEF": self._eff_1,
            "NXEF": self._eff_1, "NZEF": self._eff_1,

            "NCCA": self._cam_1, "NECA": self._cam_1, "NGCA": self._cam_1,
            "NICA": self._cam_1, "NLCA": self._cam_1, "NSCA": self._cam_1, "NUCA": self._cam_1,
            "NXCA": self._cam_1, "NZCA": self._cam_1,


            # generic
            "NOF0": self._nof0, "NFN0": self._nfn0, "NEND": self._nend,
        }  # supported blocks

    @dataclass
    class NnFile:
        start: int = 0  # after n_if
        textures: Tuple[str, ...] = False  # texture names
        bones: Tuple[str, ...] = False  # bone names
        model: ModelData = False  # model data
        name: str = "Unnamed_File"  # file name
        end: bool = False  # if end of file reached

    # functions
    def _read_block(self):
        f = self.f
        det_n = self.det_n
        block_name = read_str(f, 4)
        if block_name in det_n:
            if self.format_type[-1] == "_":
                self.format_type = getattr(nn_data, block_name[1].lower() + "no_list")[0][0]
            start_time = console_out_pre("Reading %s..." % block_name)
            det_n[block_name]()
            console_out_post(start_time)
        elif block_name.startswith("N"):
            nn_unknown.Read(f, block_name).generic()

    def read_file(self):
        while not self.nn.end and self.file_len > self.f.tell():
            self._read_block()
        if self.nn.model:
            if not self.nn.textures:
                self.read_texture_names()
            if not self.nn.bones:
                self.read_bone_names()
        if self.nn.name == "Unnamed_File":
            self.nn.name = bpy.path.basename(self.filepath)
        return self.format_type, self.nn

    def read_texture_names(self):
        if self.debug:
            print("Trying external texture names")

        if os.path.exists(self.filepath + ".texture_names"):
            f = open(self.filepath + ".texture_names", "rb")
            texture_count = read_int(f)
            texture_names = read_str_nulls(f, os.path.getsize(self.filepath) - 4)[:texture_count]
            filepath = self.filepath.rstrip(bpy.path.basename(self.filepath))
            self.nn.textures = [filepath + t + ".png" for t in texture_names]

            if self.debug:
                print(self.nn.textures)
            f.close()

    def read_bone_names(self):
        if self.debug:
            print("Trying external bone names")

        final_letter = "a"
        if self.filepath[-3:].isupper():
            final_letter = "A"

        if os.path.exists(self.filepath[:-1] + final_letter):
            f = open(self.filepath[:-1] + final_letter, "rb")
            f.seek(4, 1)
            f.seek(read_int(f), 1)
            block_name = read_str(f, 4)

            if block_name[0] == block_name[2] == block_name[3]:  # N*NN
                if block_name[1] in self.big_endian:
                    self.nn.bones = nn_node_names.Read(f, f.tell() - 4).be()
                else:
                    self.nn.bones = nn_node_names.Read(f, f.tell() - 4).le()

            if self.debug:
                stdout.write("Bone names: " + str(self.nn.bones) + "\n")
            f.close()

    def find_file_name(self, index: int):
        """Reads NN file until NEND in search of file name.
        If no file name block is found,
        a generic name with the filetype based of the file contents + the file index is returned.
        Run this function after a N*IF string as been read."""
        f = self.f
        block_types = {
            "N_OB": "no", "N_TL": "no",
            "N_NN": "na",
            "N_MA": "nv", "N_MO": "nm", "N_MC": "nd", "N_MT": "ng", "N_MM": "nf",
            "N_CA": "nd", "N_LI": "ni",
        }

        start = f.tell() - 4

        self._info_1()
        block = read_str(f, 4)

        block_type = block[1]
        block = block[:1] + "_" + block[2:]
        block = block_types[block]

        if block_type in self.big_endian:
            endian = ">"
        else:
            endian = "<"

        f.seek(start + 20)
        f.seek(read_int(f, endian) + start)

        b_name = read_str(f, 4)
        while b_name != "NEND" and b_name != "NFN0":
            f.seek(read_int(f), 1)
            b_name = read_str(f, 4)

        if b_name == "NFN0":
            b_len = read_int(f)
            end_of_block = b_len + f.tell()
            f.seek(8, 1)
            file_name = read_str_nulls(f, b_len)[0]
            f.seek(end_of_block)
            b_name = read_str(f, 4)
            while b_name != "NEND":
                f.seek(read_int(f), 1)
                b_name = read_str(f, 4)
            f.seek(read_int(f), 1)
        else:
            f.seek(read_int(f), 1)
            file_name = "Unnamed_File_" + str(index) + "." + block_type.lower() + block
            index += 1
        return file_name, index

    # block definitions
    # specific
    def _info_1(self):
        self.nn.start = nn_information_file.Read(self.f).type_1()
        if self.debug:
            message = "Post info file position: " + str(self.nn.start)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _tex_1(self):
        self.nn.textures = nn_texture_library.Read(self.f, self.nn.start, self.filepath, self.format_type).le()
        if self.debug:
            message = "Texture names: " + str(self.nn.textures)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _tex_2(self):
        self.nn.textures = nn_texture_library.Read(self.f, self.nn.start, self.filepath, self.format_type).be()
        if self.debug:
            message = "Texture names: " + str(self.nn.textures)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _eff_1(self):
        nn_effects.Read(self.f).type_1()

    def _cam_1(self):
        nn_camera.Read(self.f).type_1()

    def _node_1(self):
        self.nn.bones = nn_node_names.Read(self.f, self.nn.start).le()
        if self.debug:
            message = "Bone names: " + str(self.nn.bones)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _node_2(self):
        self.nn.bones = nn_node_names.Read(self.f, self.nn.start).be()
        if self.debug:
            message = "Bone names: " + str(self.nn.bones)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _obj_c(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).cno()
        console_out_pre("")

    def _obj_e(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).eno()
        console_out_pre("")

    def _obj_g(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).gno()
        console_out_pre("")

    def _obj_i(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).ino()
        console_out_pre("")

    def _obj_l(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).lno()
        console_out_pre("")

    def _obj_s(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).sno()
        console_out_pre("")

    def _obj_u(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).uno()
        console_out_pre("")

    def _obj_x(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).xno()
        console_out_pre("")

    def _obj_z(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).zno()
        console_out_pre("")

    # generic
    def _nof0(self):
        nn_offset_file.Read(self.f).generic()

    def _nfn0(self):
        self.nn.name = nn_file_name.Read(self.f).generic()
        if self.debug:
            message = "File name: " + str(self.nn.name)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _nend(self):
        nn_end.Read(self.f).generic()
        self.nn.end = True
