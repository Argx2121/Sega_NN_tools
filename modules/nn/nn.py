import os
from dataclasses import dataclass
from sys import stdout

from Sega_NN_tools.modules.nn import nn_unknown, nn_information_file, nn_texture_library, nn_effects, nn_node_names, \
    nn_object, nn_offset_file, nn_file_name, nn_end
from Sega_NN_tools.modules.util import read_str, console_out_pre, console_out_post, print_line

import Sega_NN_tools.io.nn_import_data as nn_data


class ReadNn:
    def __init__(self, f, filepath, format_type, debug):
        self.f = f
        self.filepath = filepath
        self.format_type = format_type
        self.debug = debug
        self.nn_file = self.NnFile()
        self.det_n = {
            # specific
            "NCIF": self.info_1, "NEIF": self.info_1, "NGIF": self.info_1,
            "NLIF": self.info_1, "NSIF": self.info_1, "NXIF": self.info_1, "NZIF": self.info_1,

            "NCTL": self.texl_2, "NETL": self.texl_2, "NGTL": self.texl_2,
            "NLTL": self.texl_1, "NSTL": self.texl_1, "NXTL": self.texl_1, "NZTL": self.texl_1,

            # Data isn't applicable
            "NCEF": self.efct_1, "NEEF": self.efct_1, "NGEF": self.efct_1,
            "NLEF": self.efct_1, "NSEF": self.efct_1, "NXEF": self.efct_1, "NZEF": self.efct_1,

            "NCNN": self.node_2, "NENN": self.node_2, "NGNN": self.node_2,
            "NLNN": self.node_1, "NSNN": self.node_1, "NXNN": self.node_1, "NZNN": self.node_1,

            "NCOB": self.obje_c, "NEOB": self.obje_e,
            "NLOB": self.obje_l, "NSOB": self.obje_s, "NXOB": self.obje_x, "NZOB": self.obje_z,

            # generic
            "NOF0": self.nof0, "NFN0": self.nfn0, "NEND": self.nend
        }  # supported blocks

    # all possible nn data
    @dataclass
    class NnFile:
        post_info: int = 0
        texture_names: list = False
        bone_names: list = False
        model_data: tuple = False
        file_name: str = "Unnamed_File"
        file_end: bool = False

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

    def read_block(self):
        self._read_block()
        return self.format_type, self.nn_file

    def read_file(self):
        while not self.nn_file.file_end:
            self._read_block()
        return self.format_type, self.nn_file

    def read_file_special(self):
        nn_file_list = []
        while self.f.tell() < os.path.getsize(self.filepath) - 4:  # just in case file len isn't divisible by 4
            block_name = read_str(self.f, 4)
            if block_name in self.det_n:
                start_time = console_out_pre("Reading %s..." % block_name)
                self.det_n[block_name]()
                if self.format_type[-1] == "_":
                    self.format_type = getattr(nn_data, block_name[1].lower() + "no_list")[0][0]
                console_out_post(start_time)
                if self.nn_file.file_end:
                    nn_file_list.append(self.nn_file)
                    print_line()
                    self.nn_file = self.NnFile()
        return self.format_type, nn_file_list

    # block definitions
    # specific
    def info_1(self):
        self.nn_file.post_info = nn_information_file.Read(self.f).type_1()
        if self.debug:
            message = "Post info file position: " + str(self.nn_file.post_info)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def texl_1(self):
        self.nn_file.texture_names = nn_texture_library.Read(self.f, self.filepath).type_1()
        if self.debug:
            message = "Texture names: " + str(self.nn_file.texture_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def texl_2(self):
        self.nn_file.texture_names = nn_texture_library.Read(self.f, self.filepath).type_2()
        if self.debug:
            message = "Texture names: " + str(self.nn_file.texture_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def efct_1(self):
        nn_effects.Read(self.f).type_1()

    def node_1(self):
        self.nn_file.bone_names = nn_node_names.Read(self.f, self.nn_file.post_info).type_1()
        if self.debug:
            message = "Bone names: " + str(self.nn_file.bone_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def node_2(self):
        self.nn_file.bone_names = nn_node_names.Read(self.f, self.nn_file.post_info).type_2()
        if self.debug:
            message = "Bone names: " + str(self.nn_file.bone_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def obje_x(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).xno()
        console_out_pre("")

    def obje_z(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).zno()
        console_out_pre("")

    def obje_l(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).lno()
        console_out_pre("")

    def obje_s(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).sno()
        console_out_pre("")

    def obje_e(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).eno()
        console_out_pre("")

    def obje_c(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type, self.debug).cno()
        console_out_pre("")

    # generic
    def nof0(self):
        nn_offset_file.Read(self.f).generic()

    def nfn0(self):
        self.nn_file.file_name = nn_file_name.Read(self.f).generic()
        if self.debug:
            message = "File name: " + str(self.nn_file.file_name)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def nend(self):
        nn_end.Read(self.f).generic()
        self.nn_file.file_end = True
