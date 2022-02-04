from Sega_NN_tools.modules.util import *


class ExtractAmb:
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
        block_len = read_int_tuple(f, 2)[1] // 8
        endian = "<"
        if block_len > 4194304:
            endian = ">"
            f.seek(start_offset + 4)
            block_len = read_int(f, endian) // 8
        f.seek(8, 1)
        count = read_int(f, endian)
        str_len = 32
        f.seek(8, 1)
        names_offset = [read_int(f, endian)]
        if block_len == 6:
            f.seek(8, 1)
        data = read_int_tuple(f, count * block_len, endian)
        if block_len == 4:
            offsets = data[0::4]
            offset_sizes = data[1::4]
        elif block_len == 5:
            names_offset = data[0::5]
            offsets = data[2::5]
            offset_sizes = data[4::5]
        elif block_len == 6:
            names_offset = data[0::6]
            offsets = data[2::6]
            offset_sizes = data[5::6]

        self.file_count = count

        for off, size in zip(offsets, offset_sizes):
            self.f.seek(off + start_offset)
            self.file_data.append(self.f.read(size))

        if len(names_offset) == 1:
            self.f.seek(names_offset[0])
            [self.file_names.append(read_str_nulls(self.f, str_len)[0]) for a in list(range(count))]
        elif len(names_offset) > 1:
            for off in names_offset:
                if off != 4294967295:
                    self.f.seek(off)
                self.file_names.append(read_str_nulls(self.f, str_len)[0])

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
                    fn.close()

        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.file_name = bpy.path.basename(self.file)[:-4]
            run_file()
            self.f.close()
        else:
            file_list = get_files(self.file, self.set_batch, name_require=".AMB", case_sensitive=False)
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
class Sonic4Tools(Operator, ImportHelper):
    """Extract from an AMB archive"""
    bl_idname = "amb.extract"
    bl_label = "Extract AMB files"
    filename_ext = ".AMB"
    filter_glob: StringProperty(
        default="*.AMB",
        options={'HIDDEN'},
        maxlen=255,
    )
    set_batch: EnumProperty(
        name="Batch usage",
        description="What files should be imported",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files (non recursive)"),
            ('Recursive', "Recursive", "Opens files recursively")),
        default='Single'
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Sonic 4 AMB Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractAmb(context, self.filepath, self.set_batch).execute()
