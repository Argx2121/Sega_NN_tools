from dataclasses import dataclass

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from ...io.import_util import batch_handler
from ...io.nn_import_data import *
from ...io import nn_import_data as nn_data
from ...modules.blender.light import Light
from ...modules.nn.nn import ReadNn
from ...modules.util import *

ni_list_types = [a[1] for a in ni_list[1:]]
selected_file = ""


class ImportSegaNI(bpy.types.Operator, ImportHelper):
    """Import a Sega NN Light"""
    bl_idname = "import_nn.sega_ni"
    bl_label = "Import *ni, *nl Light"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.cni;*.eni;*.gni;*.ini;*.lni;*.sni;*.uni;*.xni;*.zni;*.cnl;*.enl;*.gnl;*.inl;*.lnl;*.snl;*.unl;*.xnl;*.znl"
    filter_glob: StringProperty(
        default="*.cni;*.eni;*.gni;*.ini;*.lni;*.sni;*.uni;*.xni;*.zni;*.cnl;*.enl;*.gnl;*.inl;*.lnl;*.snl;*.unl;*.xnl;*.znl",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*ni, *nl variant",
        items=ni_list,
        default=ni_list[0][0],
    )

    C: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=cn_list,
    )
    E: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=en_list,
    )
    G: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=gn_list,
    )
    I: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=in_list,
    )
    L: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=ln_list,
    )
    S: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=sn_list,
    )
    U: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=un_list,
    )
    X: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=xn_list,
    )
    Z: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=zn_list,
    )

    # other
    batch: EnumProperty(
        name="Batch usage",
        description="What files should be imported",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files (non recursive)"),
            ('Recursive', "Recursive", "Opens files recursively")),
        default='Single')
    fake_user: BoolProperty(
        name="Fake User",
        description="Store with fake user",
        default=True)

    # dev specific
    debug: BoolProperty(
        name="Debug mode",
        description="Print debug info",
        default=True)
    animations: BoolProperty(
        name="Import animation",
        description="Imports animation stored in the file",
        default=True)

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN importer settings:", icon="KEYFRAME_HLT")
        global selected_file
        if selected_file != bpy.context.space_data.params.filename:
            selected_file = bpy.context.space_data.params.filename
            if len(selected_file) > 2 and selected_file[-3:].upper() in ni_list_types:
                self.nn_format = selected_file[-3].upper()

        nn_format = self.nn_format
        layout.row().prop(self, "nn_format")
        #if not nn_format.endswith("_"):
        #    layout.row().prop(self, nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)
        box.row().prop(self, "fake_user")
        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "animations")
            box.row().prop(self, "debug")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.debug = False
        settings = Settings(
            "", self.debug, self.batch, self.animations, self.fake_user,
        )
        nn_format = self.nn_format  # "Match__", "E" etc
        nn_format = getattr(self, nn_format, nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match
        settings.format = nn_format

        # this gives us a game name
        if nn_format != "Match__":
            pass  # user selected game name
        elif self.filepath.count(".") > 1 and self.filepath.split(".")[-2] in determine_bone:
            # dictionary has all game types
            settings.format = self.filepath.split(".")[-2]
            # if extracted by these tools game name is in file name
        else:
            pass  # handled later
        return light_import(self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNI.bl_idname, text="Sega NN Light (.xni, .znl, etc.)")


@dataclass
class Settings:
    format: str
    debug: bool
    batch_import: str
    animations: bool
    fake_user: bool


def light_import(filepath, settings):
    def execute_set(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + settings.format[-1] + "IF"
        print_line()
        if block == expected_block:
            nn = ReadNn(f, file_path, settings.format, settings.animations, settings.debug).read_file()[1]
            if nn.light:
                Light(nn, settings).execute()
        else:
            show_not_read("NN Light Importer")
        f.close()

    def execute_match(file_path):
        if not (file_path.lower().endswith("ni") or file_path.lower().endswith("nl")):
            return
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + block[1] + "IF"
        print_line()
        if block == expected_block:
            settings.format = getattr(nn_data, block[1].lower() + "n_list")[0][0]
            nn = ReadNn(f, file_path, settings.format, settings.animations, settings.debug).read_file()[1]
            if nn.light:
                Light(nn, settings).execute()
            settings.format = "Match__"
        else:
            show_not_read("NN Light Importer")
        f.close()

    if settings.format != "Match__":
        if settings.batch_import == "Single":
            name_require = "." + settings.format[-1].lower() + "ni"
            batch_handler(filepath, settings.batch_import, execute_set, name_require=name_require, case_sensitive=False)
        else:
            name_require = "." + settings.format[-1].lower() + "ni"
            batch_handler(filepath, settings.batch_import, execute_set, name_require=name_require, case_sensitive=False)
            name_require = "." + settings.format[-1].lower() + "nl"
            batch_handler(filepath, settings.batch_import, execute_set, name_require=name_require, case_sensitive=False)
    else:
        if settings.batch_import == "Single":
            name_require = "ni"
            batch_handler(filepath, settings.batch_import, execute_match, name_require=name_require, case_sensitive=False)
        else:
            name_require = "ni"
            batch_handler(filepath, settings.batch_import, execute_match, name_require=name_require, case_sensitive=False)
            name_require = "nl"
            batch_handler(filepath, settings.batch_import, execute_match, name_require=name_require, case_sensitive=False)
    return {'FINISHED'}
