from dataclasses import dataclass
from sys import stdout
from time import time
from typing import Any

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.nn_import_data import *


from Sega_NN_tools.io.nn_import_data import no_list, determine_bone
from Sega_NN_tools.modules.blender.model import Model
from Sega_NN_tools.modules.nn.nn import ReadNn
from Sega_NN_tools.modules.util import *


class ImportSegaNO(bpy.types.Operator, ImportHelper):
    """Import a Sega NN file (not necessarily an *.xno, *.zno etc file)"""
    bl_idname = "import.sega_no"
    bl_label = "Import *no Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.cno;*.eno;*.gno;*.ino;*.lno;*.sno;*.uno;*.xno;*.zno"
    filter_glob: StringProperty(
        default="*.cno;*.eno;*.gno;*.ino;*.lno;*.sno;*.uno;*.xno;*.zno",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    no_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_list,
        default=no_list[0][0],
    )

    C: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct cno variant)",
        items=cno_list,
    )
    E: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct eno variant)",
        items=eno_list,
    )
    G: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct gno variant)",
        items=gno_list,
    )
    I: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct ino variant)",
        items=ino_list,
    )
    L: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct lno variant)",
        items=lno_list,
    )
    S: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct sno variant)",
        items=sno_list,
    )
    U: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct uno variant)",
        items=uno_list,
    )
    X: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct xno variant)",
        items=xno_list,
    )
    Z: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct zno variant)",
        items=zno_list,
    )

    # other
    recursive_textures: BoolProperty(
        name="Recursive texture search",
        description="Looks for textures in sub folders too",
        default=False)
    batch: EnumProperty(
        name="Batch usage",
        description="If all files in a folder (non recursive) should be used",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files")),
        default='Single')
    simple_mat: BoolProperty(
        name="Simple materials (for export)",
        description="Keep materials simple for exporting to other formats, meaning not all material info is imported",
        default=True)

    # bones
    length: BoolProperty(
        name="Keep bones one size",
        description="Sets all bones as the same length",
        default=False)
    bone: BoolProperty(
        name="Hide Null bones",
        description="Hides Null Group bones from view",
        default=True)
    pose: BoolProperty(
        name="Ignore bone scale",
        description="Don't import bone scale - importing may make models appear distorted",
        default=True)

    # dev specific
    clean: BoolProperty(
        name="Clean mesh",
        description="Remove anything that will make blender crash - speeds up importing at the cost of edit mode",
        default=True)

    debug: BoolProperty(
        name="Debug mode",
        description="Print debug info",
        default=True)

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN importer settings:", icon="KEYFRAME_HLT")

        no_nn_format = self.no_format
        layout.row().prop(self, "no_format")
        if not no_nn_format.endswith("_"):
            layout.row().prop(self, no_nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)
        box.row().prop(self, "recursive_textures")
        box.row().prop(self, "simple_mat")
        box.row().prop(self, "bone")
        box.row().prop(self, "length")
        box.row().prop(self, "pose")
        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "debug")
            box.row().prop(self, "clean")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.clean = True
            self.debug = False
        settings = Settings(
            "", 0, self.debug, self.recursive_textures,
            self.batch, self.clean, self.simple_mat,
            self.length, preferences.max_len, self.pose, self.bone,
        )
        no_nn_format = self.no_format  # "Match__", "E" etc
        no_format = getattr(self, no_nn_format, no_nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match
        settings.format = no_format
        settings.format_bone_scale = determine_bone[no_format]

        # this gives us a game name
        if no_format != "Match__":
            pass  # user selected game name
        elif self.filepath.count(".") > 1 and self.filepath.split(".")[-2] in determine_bone:
            # dictionary has all game types
            settings.format = self.filepath.split(".")[-2]
            # if extracted by these tools game name is in file name
        else:
            settings.format = getattr(self, self.filepath[-3].upper())
            # gets *no type and uses name from * list of games
        settings.format_bone_scale = determine_bone[settings.format]

        return model_import(self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNO.bl_idname, text="Sega NN Model (.xno, .zno, etc.)")


@dataclass
class Settings:
    # generic
    format: str
    format_bone_scale: int
    debug: bool
    recursive_textures: bool
    batch_import: str
    clean_mesh: bool
    simple_materials: bool
    all_bones_one_length: bool
    max_bone_length: float
    ignore_bone_scale: bool
    hide_null_bones: bool


def model_import(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + settings.format[-1] + "IF"
        print_line()
        if block == expected_block:  # this catches files that get past name requirements (file.game.xno.texture_names)
            nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()[1]
            if nn.model:
                Model(nn, settings).execute()
        f.close()

    name_require = "." + settings.format[-1].lower() + "no"
    batch_handler(filepath, settings.batch_import, execute, name_require=name_require, case_sensitive=False)
    return {'FINISHED'}


def batch_handler(filepath: str, batch_import: str, func: Any, name_ignore: str = False, name_require: str = False,
                  case_sensitive: bool = True):
    start_time = time()
    if batch_import == "Single":
        func(filepath)
        stdout.flush()
    else:
        toggle_console()
        file_list = get_files(filepath, name_ignore, name_require, case_sensitive)
        for filepath in file_list:
            func(filepath)
            stdout.flush()
        toggle_console()
    print_line()

    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
