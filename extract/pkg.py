from Sega_NN_tools.modules.util import *


class ExtractPkg:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.f_dir = None
        self.f_pkg = None
        self.f_data = []

    def read_dir(self):
        f = self.f_dir
        file_name = True
        while file_name:
            file_name = read_str_terminated(f)
            if not file_name:
                break
            offset = read_int(f)
            f_len = read_int(f)
            self.f_data.append((file_name, offset, f_len))

    def read_pkg(self):
        f = self.f_pkg
        for name, offset, f_len in self.f_data:
            f.seek(offset)
            file_path = bpy.path.native_pathsep(bpy.path.abspath(self.file[:-4]) + "_Extracted" + "/" + name)
            pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            fn = open(file_path, "wb")
            fn.write(f.read(f_len))
            fn.close()

    def execute(self):
        if self.set_batch == "Single":
            self.f_dir = open(self.file[:-3] + "DIR", "rb")
            self.read_dir()
            self.f_dir.close()

            self.f_pkg = open(self.file[:-3] + "PKG", "rb")
            self.read_pkg()
            self.f_pkg.close()
        else:
            file_list = get_files(self.file, name_require=".PKG")
            for self.file in file_list:
                self.f_dir = open(self.file[:-3] + "DIR", "rb")
                self.read_dir()
                self.f_dir.close()

                self.f_pkg = open(self.file[:-3] + "PKG", "rb")
                self.read_pkg()
                self.f_pkg.close()
        show_finished("Pkg File Extractor")
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class ExtractPkgTools(Operator, ImportHelper):
    """Extract from a pkg archive"""
    bl_idname = "pkg.extract"
    bl_label = "Extract PKG files"
    filename_ext = ".pkg;.dir"
    filter_glob: StringProperty(
        default="*.pkg;*.dir",
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
        box.label(text="Pkg File Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractPkg(context, self.filepath, self.set_batch).execute()
