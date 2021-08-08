from Sega_NN_tools.modules.util import *


class ExtractS4E1:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
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
        f.seek(16, 1)
        count = read_int(f)
        str_len = read_int(f)
        f.seek(4, 1)
        names_offset = read_int(f)
        data = read_int_tuple(f, count * 4)
        offsets = data[::4]
        offset_sizes = data[1::4]
        self.file_count = count

        for off, size in zip(offsets, offset_sizes):
            self.f.seek(off + start_offset)
            self.file_data.append(self.f.read(size))

        self.f.seek(names_offset)
        for i, off in enumerate(offsets):
            var = read_str_nulls(self.f, str_len)[0]
            if off == 0:
                self.file_names.append(var)
                continue
            self.file_names.append(var)

        if "#AMB " in self.file_names:
            if self.file_names[0] == "#AMB ":
                self.file_names = [self.file_name + "_" + str(a) + ".AMB" for a in list(range(count))]
            else:
                start = self.file_names.index("#AMB ")
                self.file_names = self.file_names[:start]
                a = 0
                while len(self.file_names) != count:
                    self.file_names.append(self.file_name + "_" + str(a) + ".AMB")
                    a += 1
        self.index += 1

        self.file_names = [
            file[:-4] + ".Sonic4Episode1_Z" + file[-4:] if ".zn" in file.lower() else file for file in self.file_names]

    def execute(self):
        def run_file():
            block = read_str_nulls(self.f, 4)[0]
            self.f.seek(0)
            self.file_data = []
            self.file_names = []
            self.index = 0
            if block == "#AMB":
                self.amb_block()
                for name, data in zip(self.file_names, self.file_data):
                    if not name:
                        continue
                    file_path = bpy.path.native_pathsep(self.file.split(".")[0] + "_Extracted" + "/" + name)
                    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    fn = open(file_path, "wb")
                    fn.write(data)

        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.file_name = bpy.path.basename(self.file)[:-4]
            run_file()
            self.f.close()
        else:
            file_list = get_files(self.file, name_require=".AMB")
            for self.file in file_list:
                self.f = open(self.file, "rb")
                self.file_name = bpy.path.basename(self.file)[:-4]
                run_file()
                self.f.close()
        show_finished("Sonic 4 Episode 1 Extractor")
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
        box = layout.box()
        box.label(text="Sonic 4 Episode 1 Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractS4E1(context, self.filepath, self.set_batch).execute()
