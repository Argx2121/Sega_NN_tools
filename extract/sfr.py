from Sega_NN_tools.modules.game_specific.sfr.extract_image import ExtractImage
from Sega_NN_tools.modules.nn import nn_file_name
from Sega_NN_tools.modules.nn.nn import ReadNn
from Sega_NN_tools.modules.util import *


class ExtractSFR:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.f = None

    def pack_extract(self):
        f = self.f
        f.seek(4)
        # 1479751216 = "X360", 16930867 = 0x0102 "X360"
        type_list = {16908291: "collision", 1479751216: "pathfinding", 16930867: "splines"}
        # here we read the count of files, then add the amount sub-files for each file and
        # treat them all as individual files (count of files, count of sub-files for each file becomes net file count)
        file_count = read_short_tuple(f, 2, ">")[0]
        count_sum = sum(read_short_tuple(f, file_count, ">"))
        read_aligned(f, 4)
        f.seek(file_count * 4, 1)  # seek past flags etc.
        offset_list = [a for a in read_int_tuple(f, count_sum + 1, ">") if a != 0]  # file includes file len at the end

        for i in range(len(offset_list) - 1):
            offset = offset_list[i]
            f.seek(offset)
            block_type = read_str(f, 4)
            f.seek(offset)
            if block_type == "NEIF":
                f.seek(4, 1)
                file_name, _ = ReadNn(f, self.file_path, "SonicFreeRiders_E", False).find_file_name(i)

                f.seek(offset)

                file_path = bpy.path.native_pathsep(self.file.split(".")[0] + "_Extracted" + "/" + file_name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                fn = open(file_path, "wb")
                fn.write(f.read(offset_list[i+1] - offset))
                fn.close()
            elif self.image_check():
                ExtractImage(f, self.file.split(".")[0] + "_Extracted" + "/").execute()
            else:
                block_type = read_int(f, ">")
                # read as int
                if block_type in type_list:
                    block_type = type_list[block_type]
                else:
                    f.seek(12, 1)
                    sample = f.read(8)
                    f.seek(48, 1)
                    sample2 = f.read(8)
                    f.seek(48, 1)
                    sample3 = f.read(8)
                    if sample == sample2 == sample3:
                        block_type = "objects"
                    else:
                        block_type = False

                if block_type:
                    file_name = "Unnamed_File_" + str(i) + ".SonicFreeRiders_E." + str(block_type)
                else:
                    file_name = "Unnamed_File_" + str(i)

                f.seek(offset)

                file_path = bpy.path.native_pathsep(self.file.split(".")[0] + "_Extracted" + "/" + file_name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                fn = open(file_path, "wb")
                fn.write(f.read(offset_list[i+1] - offset))
                fn.close()
        f.close()

    def past_extract(self):
        f = self.f
        f.seek(4)
        offset_count = read_int(f, ">")
        offset_list = read_int_tuple(f, offset_count, ">") + (os.path.getsize(self.file),)
        texture_count, texture_file_stream = 0, ""

        for i in range(offset_count):
            offset = offset_list[i]
            f.seek(offset)
            block_type = read_str(f, 4)
            if block_type == "NEIF":
                write_texture_names = False
                continue_extraction = f.tell()

                # check to see if materials are used
                f.seek(32 - 4, 1)
                if read_str(f, 4) == "NEOB":  # means there is no material block
                    f.seek(read_int_tuple(f, 2, ">")[1] + 4, 1)
                    material_count, material_offset = read_int_tuple(f, 2, ">")
                    f.seek(continue_extraction + 32 - 4 + material_offset)
                    material_offset = read_int_tuple(f, material_count * 2, ">")[1::2]

                    for material in material_offset:
                        f.seek(continue_extraction + 32 - 4 + material)
                        var = read_int_tuple(f, 5, ">")
                        if var[-2]:  # if theres a texture count the file uses textures without a texture block
                            write_texture_names = True
                            break

                f.seek(continue_extraction)
                f.seek(f.tell() + read_int_tuple(f, 5, ">")[-1])
                f.seek(read_int(f), 1)
                if read_str(f, 4) == "NFN0":
                    file_name = nn_file_name.Read(self.f).generic()
                else:
                    file_name = "Unnamed_NN_File_" + str(i) + ".eno"

                f.seek(offset)

                file_path = bpy.path.native_pathsep(self.file.split(".")[0] + "_Extracted" + "/" + file_name)
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                fn = open(file_path, "wb")
                fn.write(f.read(offset_list[i+1] - offset))
                fn.close()

                if write_texture_names:
                    file_path = bpy.path.native_pathsep(
                        self.file.split(".")[0] + "_Extracted" + "/" + file_name + ".texture_names")
                    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                    fn = open(file_path, "wb")
                    write_integer(fn, "<", texture_count)
                    fn.write(texture_file_stream)
                    fn.close()
            else:
                f.seek(offset)
                file_path = bpy.path.native_pathsep(self.file.split(".")[0] + "_Extracted" + "/")
                texture_count, texture_file_stream = ExtractImage(f, file_path).execute()
        f.close()

    def execute(self):
        if self.set_batch == "Single":
            self.f = open(self.file, "rb")

            if self.file.endswith("pac"):
                self.pack_extract()
            elif self.file.endswith("pas"):
                self.past_extract()

        else:
            files_pac = get_files(self.file, name_require=".pac")
            files_pas = get_files(self.file, name_require=".pas")

            for self.file in files_pac:
                self.f = open(self.file, "rb")
                self.pack_extract()
            for self.file in files_pas:
                self.f = open(self.file, "rb")
                self.past_extract()

        show_finished("Sonic Free Riders Extractor")
        return {'FINISHED'}

    def image_check(self):
        f = self.f
        file_start = f.tell()
        if file_start + 8 > os.path.getsize(self.file):
            return False
        seek_value = file_start + read_int_tuple(f, 2, ">")[1]
        if os.path.getsize(self.file) > seek_value:
            f.seek(seek_value)
            if read_str(f, 4) == "DDS ":
                f.seek(file_start)
                return True
        f.seek(file_start)
        return False


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


# all texture things are defined here
class ExtractSfrTools(Operator, ImportHelper):
    """Extract from a free riders file archive"""
    bl_idname = "sfr.extract"
    bl_label = "Extract .pac / .pas files"
    filename_ext = ".pac;.pas"
    filter_glob: StringProperty(
        default="*.pac;*.pas",
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
        box.label(text="Sonic Free Riders Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractSFR(context, self.filepath, self.set_batch).execute()
