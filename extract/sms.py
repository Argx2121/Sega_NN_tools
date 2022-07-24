from ..modules.nn.nn import ReadNn
from ..modules.util import *


class ExtractSms:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.f = None
        self.f_name = None
        self.file_list_names = []

    def ssl_block(self):
        f = self.f_name
        if read_str(f, 4) != "SMSL":
            return

        to_offsets = read_int(f)
        count = read_int(f)
        f.seek(to_offsets)
        offsets = list(read_int_tuple(f, count))

        for off in offsets:
            f.seek(off)
            name = read_str_terminated(f)
            self.file_list_names.append(name)

    def smst_block(self):
        f = self.f
        if read_str(f, 4) != "SMST":
            return

        to_offsets = read_int(f)
        count = read_int(f)
        f.seek(to_offsets)
        offsets = list(read_int_tuple(f, count))
        offsets.append(to_offsets)

        if self.file_list_names:
            for off, end, name in zip(offsets[:-1], offsets[1:], self.file_list_names):
                self.named(off, end, name)
        else:
            index = 0
            for i, off in enumerate(offsets[:-1]):
                f.seek(off)
                block_name = read_str(f, 4)
                f.seek(off)

                info = (off, offsets[i+1], index)
                if not offsets[i+1] - off:
                    continue

                if block_name == "NGIF":
                    index = self.nn_block(info)
                elif block_name == "SMST":
                    index = self.sms_block(info)
                else:
                    index = self.unknown(info, block_name)

    def nn_block(self, info):
        block_start, block_len, index = info
        f = self.f
        f.seek(4, 1)
        name, index = ReadNn(f, self.file_path, "", False).find_file_name(index)

        f.seek(block_start)
        data = f.read(block_len - block_start)

        file_path = bpy.path.native_pathsep(self.file[:-4] + "_Extracted" + "/" + name)
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()
        return index

    def named(self, start, next_f, name):
        f = self.f

        f.seek(start)
        data = f.read(next_f - start)

        file_path = bpy.path.native_pathsep(self.file[:-4] + "_Extracted" + "/" + name)
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()

    def unknown(self, info, block_name):
        block_start, block_len, index = info
        f = self.f

        f.seek(block_start)
        data = f.read(block_len - block_start)

        file_path = bpy.path.native_pathsep(
            self.file[:-4] + "_Extracted" + "/" + "Unknown_" + str(index) + "." + block_name)
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()
        return index + 1

    def sms_block(self, info):
        block_start, block_len, index = info
        f = self.f

        f.seek(block_start)
        data = f.read(block_len - block_start)

        file_path = bpy.path.native_pathsep(
            self.file[:-4] + "_Extracted" + "/" + bpy.path.basename(self.file)[:-4] + "_" + str(index) + ".sms")
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()
        return index + 1

    def execute(self):
        if self.set_batch == "Single":
            if os.path.isfile(self.file[:-3] + "ssl"):
                self.f_name = open(self.file[:-3] + "ssl", "rb")
                self.ssl_block()
                self.f_name.close()
                print(self.file_list_names)

            self.f = open(self.file, "rb")
            self.smst_block()
            self.f.close()
        else:
            file_list = get_files(self.file, self.set_batch, name_require=".sms")
            for file in file_list:
                self.file_list_names = []
                self.file = file
                if os.path.isfile(file[:-3] + "ssl"):
                    self.f_name = open(file[:-3] + "ssl", "rb")
                    self.ssl_block()
                    self.f_name.close()

                self.f = open(file, "rb")
                self.smst_block()
                self.f.close()
        show_finished("Sms File Extractor")
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class ExtractSmsTools(Operator, ImportHelper):
    """Extract from a sms archive"""
    bl_idname = "sms.extract"
    bl_label = "Extract SMS files"
    filename_ext = ".sms"
    filter_glob: StringProperty(
        default="*.sms",
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
        box.label(text="Sms File Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractSms(context, self.filepath, self.set_batch).execute()
