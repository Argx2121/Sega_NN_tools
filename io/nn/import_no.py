from dataclasses import dataclass

from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from ...io.import_util import batch_handler
from ...io.nn_import_data import *
from ...io import nn_import_data as nn_data
from ...modules.blender.model import Model
from ...modules.nn.nn import ReadNn
from ...modules.util import *

no_list_types = [a[1] for a in no_list[1:]]
selected_file = ""


class ImportSegaNO(bpy.types.Operator, ImportHelper):
    """Import a Sega NN Model"""
    bl_idname = "import.sega_no"
    bl_label = "Import *no Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.cno;*.eno;*.gno;*.ino;*.lno;*.sno;*.uno;*.xno;*.zno"
    filter_glob: StringProperty(
        default="*.cno;*.eno;*.gno;*.ino;*.lno;*.sno;*.uno;*.xno;*.zno",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_list,
        default=no_list[0][0],
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
    recursive_textures: BoolProperty(
        name="Recursive texture search",
        description="Looks for textures in sub folders too",
        default=False)
    batch: EnumProperty(
        name="Batch usage",
        description="What files should be imported",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files (non recursive)"),
            ('Recursive', "Recursive", "Opens files recursively")),
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
    accurate: BoolProperty(
        name="Accurate bones",
        description="Do not modify bones - only use stored values",
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
        global selected_file
        if selected_file != bpy.context.space_data.params.filename:
            selected_file = bpy.context.space_data.params.filename
            if len(selected_file) > 2 and selected_file[-3:].upper() in no_list_types:
                # the file name is a variable that the user can set
                #  the user could rename this variable to a filetype that isn't supported
                #  it could also be renamed to gno to pull gno settings without actually selecting a gno file
                self.nn_format = selected_file[-3].upper()

        nn_format = self.nn_format
        layout.row().prop(self, "nn_format")
        if not nn_format.endswith("_"):
            layout.row().prop(self, nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)
        box.row().prop(self, "recursive_textures")
        box.row().prop(self, "simple_mat")
        box.row().prop(self, "bone")
        box.row().prop(self, "length")
        box.row().prop(self, "accurate")
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
            self.length, self.accurate, preferences.max_len, self.bone,
        )
        nn_format = self.nn_format  # "Match__", "E" etc
        nn_format = getattr(self, nn_format, nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match
        settings.format = nn_format
        settings.format_bone_scale = determine_bone[nn_format]

        # this gives us a game name
        if nn_format != "Match__":
            pass  # user selected game name
        elif self.filepath.count(".") > 1 and self.filepath.split(".")[-2] in determine_bone:
            # dictionary has all game types
            settings.format = self.filepath.split(".")[-2]
            # if extracted by these tools game name is in file name
        else:
            pass  # handled later
        settings.format_bone_scale = determine_bone[settings.format]
        return model_import(self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNO.bl_idname, text="Sega NN Model (.xno, .zno, etc.)")


@dataclass
class Settings:
    format: str
    format_bone_scale: int
    debug: bool
    recursive_textures: bool
    batch_import: str
    clean_mesh: bool
    simple_materials: bool
    all_bones_one_length: bool
    keep_bones_accurate: bool
    max_bone_length: float
    hide_null_bones: bool


def model_import(filepath, settings):
    def execute_set(file_path):
        if "texture_names" in file_path:
            return
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + settings.format[-1] + "IF"
        print_line()
        if block == expected_block:
            nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()[1]
            if nn.model:
                Model(nn, file_path, settings).execute()
        else:
            show_not_read("NN Model Importer")
        f.close()

    def execute_match(file_path):
        if not file_path.lower().endswith("no"):
            return
        if "texture_names" in file_path:
            return
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        expected_block = "N" + block[1] + "IF"
        print_line()
        if block == expected_block:
            settings.format = getattr(nn_data, block[1].lower() + "n_list")[0][0]
            nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()[1]
            if nn.model:
                Model(nn, file_path, settings).execute()
            settings.format = "Match__"
        else:
            show_not_read("NN Model Importer")
        f.close()

    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    if settings.format != "Match__":
        name_require = "." + settings.format[-1].lower() + "no"
        batch_handler(filepath, settings.batch_import, execute_set, name_require=name_require, case_sensitive=False)
    else:
        name_require = "no"
        batch_handler(filepath, settings.batch_import, execute_match, name_require=name_require, case_sensitive=False)
    return {'FINISHED'}
