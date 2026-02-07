from dataclasses import dataclass

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from ...io.import_util import batch_handler
from ...io.nn_import_data import *
from ...io import nn_import_data as nn_data
from ...modules.blender.morph import *
from ...modules.nn.nn import ReadNn
from ...modules.util import *
from ...modules.blender.model_assets.model_util import clean_mesh

selected_file = ""

# Please tell me if theres a better way to do this
nn_morph_path = ""


class ImportSegaNG(bpy.types.Operator, ImportHelper):
    """Import a Sega NN Morph"""
    bl_idname = "import_nn.sega_ng"
    bl_label = "Import *ng Morph"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.cng;*.eng;*.gng;*.ing;*.lng;*.sng;*.ung;*.xng;*.zng"
    filter_glob: StringProperty(
        default="*.cng;*.eng;*.gng;*.ing;*.lng;*.sng;*.ung;*.xng;*.zng",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*ng variant",
        items=ng_list,
        default=ng_list[0][0],
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
    remove_loose: BoolProperty(
        name="Remove Loose",
        description="Remove loose vertices after you've imported all morphs",
        default=False)


    # dev specific
    debug: BoolProperty(
        name="Debug mode",
        description="Print debug info",
        default=True)

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN importer settings:", icon="KEYFRAME_HLT")
        global selected_file
        if selected_file != bpy.context.space_data.params.filename:
            selected_file = bpy.context.space_data.params.filename
            if len(selected_file) > 2 and selected_file[-3:].upper():
                self.nn_format = selected_file[-3].upper()

        nn_format = self.nn_format
        layout.row().prop(self, "nn_format")
        if not nn_format.endswith("_"):
            layout.row().prop(self, nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)
        box.row().prop(self, "remove_loose", expand=True)
        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "debug")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.debug = False
        settings = Settings(
            "", self.debug, self.batch, self.remove_loose,
        )

        if not context.object.type == "ARMATURE":
            return {'FINISHED'}

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
        return morph_import(self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNG.bl_idname, text="Sega NN Morph (.xng, .zng, etc.)")


@dataclass
class Settings:
    format: str
    debug: bool
    batch_import: str
    remove_loose: bool


def remove_loose(settings):
    if settings.remove_loose:
        arma = bpy.context.object
        meshes = []
        for mesh in arma.children:
            if mesh.type == "MESH":
                meshes.append(mesh)
        for mesh in meshes:
            clean_mesh(mesh)


def morph_import(filepath, settings):
    def execute_set(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + settings.format[-1] + "IF"
        print_line()
        if block == expected_block:
            nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()[1]
            if nn.morphs:
                print("Making Morphs-------------------------------------")
                message = "Making" + " " + nn.name
                start_time = console_out_pre(message)
                Morph(nn, settings).morph()
                console_out_post(start_time)
        else:
            show_not_read("NN Morph Importer")
        f.close()

    def execute_match(file_path):
        if not file_path.lower().endswith("ng"):
            return
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + block[1] + "IF"
        print_line()
        if block == expected_block:
            settings.format = getattr(nn_data, block[1].lower() + "n_list")[0][0]
            nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()[1]
            if nn.morphs:
                print("Making Morphs-------------------------------------")
                message = "Making" + " " + nn.name
                start_time = console_out_pre(message)
                Morph(nn, settings).morph()
                console_out_post(start_time)
            settings.format = "Match__"
        else:
            show_not_read("NN Morph Importer")
        f.close()

    if settings.format != "Match__":
        name_require = "." + settings.format[-1].lower() + "ng"
        batch_handler(filepath, settings.batch_import, execute_set, name_require=name_require, case_sensitive=False)
        remove_loose(settings)
    else:
        name_require = "ng"
        batch_handler(filepath, settings.batch_import, execute_match, name_require=name_require, case_sensitive=False)
        remove_loose(settings)
    return {'FINISHED'}
