from ..modules.nn.nn import ReadNn
from ..modules.util import *


class ExtractGosGts:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.f = None
        self.folder_path = None
        self.file_offsets = []
        self.f_name = None
        self.file_list_names = []

    def header_block(self):
        f = self.f
        f.seek(4, 1)  # this * 4 = what file len would be if it was 32 byte aligned
        # why they didn't just align it I do not know
        block = read_str(f, 4)
        if block not in {"gos1", "gts1"}:
            return
        self.file_offsets = read_int_tuple(f, read_short_tuple(f, 2, ">")[0], ">")
        # padding with FF for 32 byte alignment is not read

    def gts_block(self):
        f = self.f
        file_len = read_int(f, ">")
        file_name = str(f.read(60)).split("\\x00", 1)[0][2:]
        # respect for having a set block length
        # not respect to python though is there no way to just... read a string and ignore the nulls

        file_path = bpy.path.native_pathsep(self.folder_path + "/" + file_name + ".gvr")
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(f.read(file_len))
        fn.close()

    def gos_block(self):
        f = self.f
        folder_name = str(f.read(40)).split("\\x00", 1)[0][2:]
        file_len = read_int(f, ">")  # this is the len for the first file, not for the sum
        f.seek(4, 1)  # unknown int
        additional_count = read_int(f, ">")
        read_aligned(f, 32)
        return folder_name, additional_count, file_len

    def gos_block_info(self, additional_count):
        f = self.f
        additional_file_offsets = read_int_tuple(f, additional_count, ">")
        # this is also padded
        return additional_file_offsets

    def gts(self):
        self.header_block()
        for file_off in self.file_offsets:
            self.f.seek(file_off)
            self.gts_block()

    def gos(self):
        f = self.f
        self.header_block()
        for file_off in self.file_offsets:
            f.seek(file_off)
            folder_name, additional_count, file_len = self.gos_block()
            first_file_start = f.tell()
            self.folder_path = self.file[:-4] + "_Extracted/" + folder_name
            if additional_count:
                f.seek(4, 1)
                name, _ = ReadNn(self.f, self.file, "", False).find_file_name(0)
                file_path = bpy.path.native_pathsep(self.folder_path + "/" + name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                f.seek(first_file_start)

                fn = open(file_path, "wb")
                fn.write(f.read(file_len))
                fn.close()
                # we are now at the info (file_len is actually the info offset, but it works that way too so...)
                additional_file_offsets = self.gos_block_info(additional_count)
                for off in additional_file_offsets:
                    f.seek(file_off + off + 4)  # we don't need the index (?)
                    read_aligned(f, 32)
                    file_start = f.tell()
                    f.seek(4, 1)
                    name, _ = ReadNn(self.f, self.file, "", False).find_file_name(0)
                    file_path = bpy.path.native_pathsep(self.folder_path + "/" + name)
                    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    file_len = f.tell() - file_start
                    f.seek(file_start)

                    fn = open(file_path, "wb")
                    fn.write(f.read(file_len))
                    fn.close()
            else:
                f.seek(4, 1)
                name, _ = ReadNn(self.f, self.file, "", False).find_file_name(0)
                file_path = bpy.path.native_pathsep(self.folder_path + "/" + name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                f.seek(first_file_start)

                fn = open(file_path, "wb")
                fn.write(f.read(file_len))
                fn.close()

    def execute(self):
        if self.set_batch == "Single":
            if self.file.endswith("gos"):
                self.f = open(self.file, "rb")
                self.gos()
            elif self.file.endswith("gts"):
                self.f = open(self.file, "rb")
                self.folder_path = self.file[:-4] + "_Extracted"
                self.gts()
        else:
            files_gos = get_files(self.file, self.set_batch, name_require=".gos")
            files_gts = get_files(self.file, self.set_batch, name_require=".gts")

            for self.file in files_gos:
                self.f = open(self.file, "rb")
                self.gos()
            for self.file in files_gts:
                self.f = open(self.file, "rb")
                self.folder_path = self.file[:-4] + "_Extracted"
                self.gts()
        show_finished("Gos / Gts File Extractor")
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class ExtractGosGtsTools(Operator, ImportHelper):
    """Extract from a Gos or Gts archive"""
    bl_idname = "gosgts.extract"
    bl_label = "Extract Gos / Gts files"
    filename_ext = ".gos;.gts"
    filter_glob: StringProperty(
        default="*.gos;*.gts",
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
        box.label(text="Gos / Gts File Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        # noinspection PyUnresolvedReferences
        return ExtractGosGts(context, self.filepath, self.set_batch).execute()
