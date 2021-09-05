from Sega_NN_tools.modules.game_specific.srzg.extract_image import ExtractImage
from Sega_NN_tools.modules.nn.nn import ReadNn
from Sega_NN_tools.modules.util import *


class ExtractSRZG:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.set_batch = set_batch
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.f = None

    def pack_extract(self):
        f = self.f
        f.seek(4)
        # 1464420608 = "WII", 16930633 = 0x0102 "WII"
        type_list = {115: "collision", 1464420608: "pathfinding", 16930633: "splines"}
        file_count = read_short_tuple(f, 2, ">")[0]
        sub_count = read_byte_tuple(f, file_count, ">")
        offset_count = sum(sub_count)
        f.seek(file_count, 1)
        read_aligned(f, 4)
        net_count = read_short_tuple(f, file_count, ">")
        sub_type = read_short_tuple(f, file_count, ">")

        read_aligned(f, 4)
        offset_list = [a for a in read_int_tuple(f, offset_count + 1, ">")]
        # file includes file len at the end

        for sub, net, s_type in zip(sub_count, net_count, sub_type):
            offsets = [x for x in offset_list[net:net + sub + 1] if x != 0]
            sub_path = bpy.path.native_pathsep(
                self.file.split(".")[0] + "_Extracted" + "/" + str(s_type) + "_" + str(net) + "/")
            for i, j in zip(offsets, offsets[1:]):
                f.seek(i)
                block_type = read_str(f, 4)
                f.seek(i)
                if block_type == "NGIF":
                    write_texture_names = False

                    # check to see if materials are used
                    f.seek(read_int_tuple(f, 2)[1], 1)
                    n_start = f.tell()
                    if read_str(f, 4) == "NGOB":  # means there is no material block
                        f.seek(read_int_tuple(f, 2, ">")[1] + 4, 1)  # sends us after model bounds
                        mats, mat_off, _, _, _, _, bones, _, b_off, b_used, m_sets, off = read_int_tuple(f, 12, ">")

                        if b_off > n_start + 16:  # make sure pointers are fine
                            n_start = n_start + 16 - b_off

                        f.seek(mat_off + n_start)
                        t_count = read_int_tuple(f, mats * 2, ">")[0::2]

                        for texture in t_count:
                            var = format(texture >> 17, "b").count("1")
                            if var:  # if theres a texture count the file uses textures without a texture block
                                write_texture_names = True
                                break

                    f.seek(i + 4)
                    file_name, _ = ReadNn(f, self.file_path, "", False).find_file_name(i)

                    f.seek(i)

                    file_path = bpy.path.native_pathsep(sub_path + file_name)
                    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                    fn = open(file_path, "wb")
                    fn.write(f.read(j - i))
                    fn.close()

                    if write_texture_names:
                        file_path = bpy.path.native_pathsep(sub_path + file_name + ".texture_names")
                        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                        fn = open(file_path, "wb")
                        write_integer(fn, "<", texture_count)
                        fn.write(texture_file_stream)
                        fn.close()
                elif self.image_check():
                    texture_count, texture_file_stream = ExtractImage(
                        f, sub_path).execute()
                else:
                    block_type = read_int(f, ">")
                    # read as int
                    if block_type in type_list:
                        block_type = type_list[block_type]
                    else:
                        f.seek(56, 1)
                        sample = f.read(12)
                        f.seek(40, 1)
                        sample2 = f.read(12)
                        f.seek(40, 1)
                        sample3 = f.read(12)
                        if sample == sample2 == sample3 and block_type:
                            block_type = "objects"
                        else:
                            block_type = False

                    if block_type:
                        file_name = "Unnamed_File_" + str(i) + ".SonicRidersZeroGravity_G." + str(block_type)
                    else:
                        file_name = "Unnamed_File_" + str(i)

                    f.seek(i)

                    file_path = bpy.path.native_pathsep(sub_path + file_name)
                    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                    fn = open(file_path, "wb")
                    fn.write(f.read(j - i))
                    fn.close()
        f.close()

    def execute(self):
        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            self.pack_extract()
            self.f.close()

        else:
            files_pack = get_files(self.file, name_require=".pack")
            for self.file in files_pack:
                self.f = open(self.file, "rb")
                self.pack_extract()
                self.f.close()

        show_finished("Sonic Riders Zero Gravity Extractor")
        return {'FINISHED'}

    def image_check(self):
        f = self.f
        file_start = f.tell()
        if file_start + 8 > os.path.getsize(self.file):
            return False
        seek_value = file_start + read_int_tuple(f, 2, ">")[1]
        if os.path.getsize(self.file) > seek_value:
            f.seek(seek_value)
            block = read_str(f, 4)
            if block == "GCIX":
                f.seek(file_start)
                return True
        f.seek(file_start)
        return False


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class ExtractSrgzTools(Operator, ImportHelper):
    """Extract from a Sonic Riders Zero Gravity file archive"""
    bl_idname = "srzg.extract"
    bl_label = "Extract .pack files"
    filename_ext = ".pack"
    filter_glob: StringProperty(
        default="*.pack",
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
        box.label(text="Sonic Riders Zero Gravity Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        return ExtractSRZG(context, self.filepath, self.set_batch).execute()
