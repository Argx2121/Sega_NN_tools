import bpy

from Sega_NN_tools.modules.game_specific import sonic_riders as riders
from Sega_NN_tools.modules.game_specific.sonic_riders import replace_image as re_img


def file_loc(file_path: str):  # is there a better way to do this?
    file_loc.file_path = file_path


file_loc("")  # define the var now to prevent a crash if called but not defined


class Tools:
    def __init__(self, file_path, image_setting):
        self.file_path = file_path
        self.tex_path = (bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path)))
        self.image_setting = image_setting

    def batch(self, archive_list, set_extract):
        riders.toggle_console()
        if set_extract:
            for file_name in archive_list:
                print(file_name)
                self.file_path = file_name
                f = open(file_name, 'rb')
                arc_data = riders.re_arc.read_archive(f)
                self.extract(arc_data.sub_file_offsets, f)
                f.close()
        else:
            for file_name in archive_list:
                print(file_name)
                f = open(self.tex_path + file_name, 'r+b')
                arc_data = riders.re_arc.read_archive(f)
                self.insert(arc_data.file_count, arc_data.sub_file_offsets, f)
                f.close()
        riders.ex_img.toggle_console()

    def extract(self, sub_file_offsets, f):
        for i in range(len(sub_file_offsets)):
            f.seek(sub_file_offsets[i] + 4)
            if riders.BlockTypeCheck(f, self.file_path, 0).check_image():
                riders.ex_img.ExtractImage(f, self.file_path, self.image_setting, i).execute()

    def insert(self, file_count, sub_file_offsets, f):
        re_img.ReplaceImage(f, self.file_path, file_count, sub_file_offsets, self.image_setting).execute()


def show_finished():
    def draw(self, context):
        self.layout.label(text="Finished!")
    bpy.context.window_manager.popup_menu(draw, "NN SRPC Texture Tools", "INFO")


def texture_tools(context, file_path, in_out, set_batch, image):
    file_loc(file_path)
    if set_batch == "Single":
        f = open(file_path, 'rb')
        if in_out == "Extract":
            print("Extracting a files textures")
            arc_data = riders.re_arc.read_archive(f)
            Tools(file_path, image).extract(arc_data.sub_file_offsets, f)
        else:
            print("Inserting a files textures")
            f = open(file_path, 'r+b')
            arc_data = riders.re_arc.read_archive(f)
            Tools(file_path, image).insert(arc_data.file_count, arc_data.sub_file_offsets, f)
        f.close()
    else:
        f = open(file_path, 'rb')
        if in_out == "Extract":
            print("Batch extracting a files textures")
            archive_list = riders.get_files(file_path, ".")
            Tools(file_path, image).batch(archive_list, True)
        else:
            print("Batch inserting a files textures")
            archive_list = riders.get_files(file_path, ".")
            Tools(file_path, image).batch(archive_list, False)
        f.close()
    print("Finished")
    show_finished()
    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator


class OpenTextureFolder(bpy.types.Operator):
    """Open Folder where textures were extracted"""
    bl_idname = "srpc_image_tools.open_texture_folder"
    bl_label = "Open Folder"

    def execute(self, context):
        print("Opening texture location")
        import subprocess
        filepath = file_loc.file_path
        folder_path: str = (bpy.path.abspath(filepath).rstrip(bpy.path.basename(filepath) + "\\"))
        subprocess.Popen('explorer ' + folder_path)
        return {'FINISHED'}


# all texture things are defined here
class SonicRPCTextureTools(Operator, ImportHelper):
    """Extract or insert textures for SRPC model archive(s)"""
    bl_idname = "srpc_image_tools.texture_tools"
    bl_label = "Extract or Insert Images"
    filename_ext = ""
    filter_glob: StringProperty(
        default="*",
        options={'HIDDEN'},
        maxlen=255,
    )
    in_out: EnumProperty(
        name="Extract / Insert",
        description="If textures should be extracted or inserted",
        items=(
            ('Extract', "Extract", "Extracts textures"),
            ('Insert', "Insert", "Inserts textures"),
        ),
        default='Extract',
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
    image: EnumProperty(
        name="Image naming conventions",
        description="How extracted texture names should be formatted",
        items=(
            ('simple', "Simple Names",
             "Allows textures with the same name to be replace eachother "
             "(syntax: Texture_name.dds)"),
            ('complex', "Specific Names",
             "Prevents a texture from being replaced by one with the same name "
             "(syntax: Name.file.subfile.index.dds)")),
        default='simple')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Sonic Riders PC Texture settings:")
        layout.row().prop(self, "in_out", expand=True)
        layout.row().prop(self, "set_batch", expand=True)
        layout.row().prop(self, "image", expand=True)

    def execute(self, context):
        return texture_tools(context, self.filepath, self.in_out, self.set_batch, self.image)
