import pathlib

from Sega_NN_tools.modules.util import *


class ExtractTHA:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.f = None

    def izca_block(self):
        f = self.f
        if read_str(f, 4) != "IZCA":
            return

        f.seek(8)
        to_data = read_int(f)
        f.seek(8 + to_data)

        to_offsets = read_int(f)
        count = read_int(f)
        f.seek(to_offsets)
        offsets = read_int_tuple(f, count)

        index = 0
        for off in offsets:
            f.seek(off)
            block_name = read_str(f, 4)
            block_len = read_int(f)
            info_len = read_int(f)
            f.seek(off + info_len)
            data = f.read(block_len)

            file_path = bpy.path.native_pathsep(self.file[:-4] + "_" + str(index) + "." + block_name)
            pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            fn = open(file_path, "wb")
            fn.write(data)
            index += 1

    def htex_block(self):
        def execute():
            block = read_str(f, 4)
            if block != "DDM ":
                return

            f.seek(8 + read_int(f))
            block = read_str(f, 4)
            if block != "DSFN":
                return

            block_len = read_int(f)
            img_count = read_short_tuple(f, 4)[1]
            img_names = read_str_nulls(f, block_len - 8)
            block = read_str(f, 4)
            for i in range(img_count):
                while block != "DSCK":
                    block = read_str(f, 4)

                block_len = read_int_tuple(f, 3)[1]
                data = f.read(block_len)
                block = read_str(f, 4)

                tex_name = img_names[i]
                file_path = bpy.path.native_pathsep(self.file_path + tex_name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                fn = open(file_path, "wb")
                fn.write(data)
                fn.close()

        file_list = get_files(self.file, name_require=".HTEX")
        for file in file_list:
            f = open(file, "rb")
            execute()
            f.close()

    def execute(self):
        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.izca_block()
            self.f.close()
            self.htex_block()
        else:
            file_list = get_files(self.file, name_require=".bnk")
            for file in file_list:
                self.f = open(file, "rb")
                self.file = file
                self.izca_block()
                self.f.close()
            self.htex_block()
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


# all texture things are defined here
class ExtractThaTools(Operator, ImportHelper):
    """Extract from an bnk archive"""
    bl_idname = "tha.extract"
    bl_label = "Extract BNK files"
    filename_ext = ".bnk"
    filter_glob: StringProperty(
        default="*.bnk",
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
        box.label(text="Transformers: Human Alliance Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractTHA(context, self.filepath, self.set_batch).execute()
