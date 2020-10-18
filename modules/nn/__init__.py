import importlib
if "nn_information_file" in locals():
    importlib.reload(nn_texture_library)
    importlib.reload(nn_end)
    importlib.reload(nn_information_file)
    importlib.reload(nn_offset_file)
    importlib.reload(nn_file_name)
    importlib.reload(nn_object)
    importlib.reload(nn_unknown)
    importlib.reload(nn_node_names)
    importlib.reload(nn_effects)
else:
    from . import nn_texture_library
    from . import nn_end
    from . import nn_information_file
    from . import nn_offset_file
    from . import nn_file_name
    from . import nn_object
    from . import nn_unknown
    from . import nn_node_names
    from . import nn_effects

from ..util import *
from dataclasses import dataclass


class ReadNn:
    def __init__(self, f, filepath, format_type, debug=False):
        self.f = f
        self.filepath = filepath
        self.format_type = format_type
        self.debug = debug
        self.nn_file = self.NnFile()
        self.det_n = {
            # specific
            "NCIF": self.info_1, "NGIF": self.info_1, "NLIF": self.info_1, "NSIF": self.info_1, "NXIF": self.info_1,
            "NZIF": self.info_1,

            "NCTL": self.texl_2, "NGTL": self.texl_2, "NLTL": self.texl_1, "NSTL": self.texl_1, "NXTL": self.texl_1,
            "NZTL": self.texl_1,

            # all but NXEF are assumed to exist. (Data isn't applicable)
            "NCEF": self.efct_1, "NGEF": self.efct_1, "NLEF": self.efct_1, "NSEF": self.efct_1, "NXEF": self.efct_1,
            "NZEF": self.efct_1,

            # all but NXNN are assumed to exist
            "NCNN": self.node_2, "NGNN": self.node_2, "NLNN": self.node_1, "NSNN": self.node_1, "NXNN": self.node_1,
            "NZNN": self.node_1,

            "NXOB": self.nxob,
            # generic
            "NOF0": self.nof0, "NFN0": self.nfn0, "NEND": self.nend
        }  # all supported blocks

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
            start_time = console_out_pre("Reading %s..." % block_name)
            det_n[block_name]()
            console_out_post(start_time)
        else:
            nn_unknown.Read(f, block_name).generic()

    def read_block(self):
        self._read_block()
        return self.nn_file

    def read_file(self):
        while not self.nn_file.file_end:
            self._read_block()
        return self.nn_file

    # block definitions
    # specific
    def info_1(self):
        self.nn_file.post_info = nn_information_file.Read(self.f).type_1()

    def texl_1(self):
        self.nn_file.texture_names = nn_texture_library.Read(self.f, self.filepath).type_1()

    def texl_2(self):
        self.nn_file.texture_names = nn_texture_library.Read(self.f, self.filepath).type_2()

    def efct_1(self):
        nn_effects.Read(self.f).type_1()

    def node_1(self):
        self.nn_file.bone_names = nn_node_names.Read(self.f, self.nn_file.post_info).type_1()

    def node_2(self):
        self.nn_file.bone_names = nn_node_names.Read(self.f, self.nn_file.post_info).type_2()

    def nxob(self):
        self.nn_file.model_data = nn_object.Read(self.f, self.nn_file.post_info, self.format_type).x(self.debug)
        console_out_pre("")

    # generic
    def nof0(self):
        nn_offset_file.Read(self.f).generic()

    def nfn0(self):
        self.nn_file.file_name = nn_file_name.Read(self.f).generic()

    def nend(self):
        nn_end.Read(self.f).generic()
        self.nn_file.file_end = True
