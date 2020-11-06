from .sfr.header import *
from .sfr.textures import *
from ..blender.model import Model
from ..nn.nn import ReadNn


class ReadSFR:
    def __init__(self, f, file_path, settings):
        self.f = f
        self.file_path = file_path
        self.settings = settings

    def execute(self):
        f = self.f
        b_type = read_str(f, 4)
        if b_type == "paST":
            header = read_archive(f)
            nn_list = []
            for offset in header.offsets:
                f.seek(offset)
                b_type = read_str(f, 4)
                f.seek(-4, 1)
                if b_type == "NEIF":
                    nn_list.append(ReadNn(f, self.file_path, self.settings.format, self.settings.debug).read_file()[1])
                else:
                    ExtractImage(f, self.file_path).execute()
            for nn in nn_list:
                if nn.model_data:
                    Model(nn, self.settings).execute()
