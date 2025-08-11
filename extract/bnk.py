from ..modules.nn.nn import ReadNn
from ..modules.util import *


class ExtractBnk:
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
        f.seek(8 + read_int(f))

        to_offsets = read_int(f)
        count = read_int(f)
        f.seek(to_offsets)
        offsets = read_int_tuple(f, count)

        # i think i made this after making like, 50 other file extractors
        # sorry that the previous version was so ass i was just so over it man
        block_func = {
            "HTEX": self.htex_block,
            # "HTTB": self.skip, "ABDA": self.skip, "ABDT": self.skip, "ABRS": self.skip,
            # "HCCL": self.skip,
            "HMDL": self.nn_block, "HMOT": self.nn_block, "HCAM": self.nn_block, "HLIT": self.nn_block,
            "HMAT": self.nn_block, "HMMT": self.nn_block, "HMRT": self.nn_block}

        index = 0
        for e, off in enumerate(offsets):
            f.seek(off)
            block_name = read_str(f, 4)
            block_len = read_int(f)
            info_len = read_int(f)
            f.seek(off + info_len)

            info = (block_len, index)
            # noinspection PyArgumentList
            if block_name in block_func:
                index = block_func[block_name](info)
            else:
                self.skip(info, e, block_name)

    def nn_block(self, info):
        block_len, index = info
        f = self.f
        start = f.tell()
        f.seek(4, 1)
        name, index = ReadNn(f, self.file_path).find_file_name(index)

        f.seek(start)
        data = f.read(block_len)

        if ":" in name:
            name = pathlib.Path(name)
            name = str(pathlib.PurePath(name.parent.relative_to(name.parents[1]), name.name))

        file_path = bpy.path.native_pathsep(self.file[:-4] + "_Extracted" + "/" + name)
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()
        return index

    def skip(self, info, e, block_name):
        block_len, index = info
        f = self.f
        name = "Unknown_file_" + str(e) + "." + block_name
        data = f.read(block_len)

        if ":" in name:
            name = pathlib.Path(name)
            name = str(pathlib.PurePath(name.parent.relative_to(name.parents[1]), name.name))

        file_path = bpy.path.native_pathsep(self.file[:-4] + "_Extracted" + "/" + name)
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        fn = open(file_path, "wb")
        fn.write(data)
        fn.close()
        return index

    def htex_block(self, info):
        _, index = info
        f = self.f
        block = read_str(f, 4)
        if block != "DDM ":
            return

        f.seek(read_int(f), 1)
        block = read_str(f, 4)
        if block != "DSFN":
            return
        block_start = f.tell() - 4

        block_len = read_int(f)
        img_count = read_short_tuple(f, 4)[1]
        img_names = read_str_nulls(f, block_len - 8)

        f.seek(block_start + block_len + 8)
        for i in range(img_count):
            block_start = f.tell()
            _, block_len, tex_len, _ = read_int_tuple(f, 4)
            data = f.read(tex_len)

            tex_name = img_names[i]
            if ":" in tex_name:
                name = pathlib.Path(tex_name)
                tex_name = str(pathlib.PurePath(name.parent.relative_to(name.parents[1]), name.name))

            file_path = bpy.path.native_pathsep(self.file[:-4] + "_Extracted" + "/" + tex_name)
            pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            fn = open(file_path, "wb")
            fn.write(data)
            fn.close()
            f.seek(block_start + block_len + 8)
        return index

    def execute(self):
        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.izca_block()
            self.f.close()
        else:
            file_list = get_files(self.file, self.set_batch, name_require=".bnk")
            for file in file_list:
                self.f = open(file, "rb")
                self.file = file
                self.izca_block()
                self.f.close()
        show_finished("Bnk File Extractor")
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class ExtractBnkTools(Operator, ImportHelper):
    """Extract from an bnk archive"""
    bl_idname = "bnk.extract"
    bl_label = "Extract BNK files"
    filename_ext = ".bnk"
    filter_glob: StringProperty(
        default="*.bnk",
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
        box.label(text="Bnk File Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        # noinspection PyUnresolvedReferences
        return ExtractBnk(context, self.filepath, self.set_batch).execute()
