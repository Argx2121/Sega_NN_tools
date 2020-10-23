import os
import bpy

from Sega_NN_tools.modules.nn_util import read_int, read_multi_ints, read_str_nulls, get_files


class ExtractS4E1:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.file_name = None
        self.file_data = []
        self.file_names = []
        self.set_batch = set_batch
        self.file_count = 0
        self.index = 0
        self.f = None

    def amb_block(self):
        f = self.f
        start_offset = f.tell()
        f.seek(12 + 4, 1)
        count = read_int(f)
        f.seek(8, 1)
        names_offset = read_int(f)
        data = read_multi_ints(f, count * 4)
        offsets = data[::4]
        offset_sizes = data[1::4]

        lens = offset_sizes
        self.file_count = count
        for i in range(count):
            self.f.seek(offsets[i] + start_offset)
            self.file_data.append(self.f.read(lens[i]))
        self.f.seek(names_offset)
        for _ in range(count):
            self.file_names.append(read_str_nulls(self.f, 32)[0])
        if "#AMB " in self.file_names:
            if self.file_names[0] == "#AMB ":
                self.file_names = [self.file_name + "_" + str(a) + ".AMB"
                                   for a in list(range(count))]
            else:
                start = self.file_names.index("#AMB ")
                self.file_names = self.file_names[:start]
                a = 0
                while len(self.file_names) != count:
                    self.file_names.append(self.file_name + "_" + str(a) + ".AMB")
                    a += 1
        self.index += 1

    def execute(self):
        def run_file():
            block = read_str_nulls(self.f, 4)[0]
            self.f.seek(0)
            self.file_data = []
            self.file_names = []
            self.index = 0
            if block == "#AMB":
                self.amb_block()
                print(self.file_names)
                for i in range(self.file_count):
                    file_path = self.file_path + self.file_names[i]
                    if not os.path.exists(file_path.rsplit(sep="\\", maxsplit=1)[0]):
                        os.mkdir(file_path.rsplit(sep="\\", maxsplit=1)[0])
                    fn = open(file_path, "wb")
                    fn.write(self.file_data[i])

        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.file_name = bpy.path.basename(self.file)[:-4]
            run_file()
            self.f.close()
        else:
            file_list = get_files(self.file, name_require=".AMB")
            for file in file_list:
                self.f = open(file, "rb")
                self.file_name = bpy.path.basename(file)[:-4]
                run_file()
                self.f.close()
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


# all texture things are defined here
class Sonic4E1Tools(Operator, ImportHelper):
    """Extract from an AMB archive"""
    bl_idname = "s4e1.extract"
    bl_label = "Extract AMB files"
    filename_ext = ".AMB"
    filter_glob: StringProperty(
        default="*.AMB",
        options={'HIDDEN'},
        maxlen=255,
    )
    set_batch: EnumProperty(
        name="Batch usage",
        description="If all files in a folder (non recursive) should be used",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files"),
        ),
        default='Single',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Sonic 4 Episode 1 Extractor Settings:")
        layout.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractS4E1(context, self.filepath, self.set_batch).execute()
