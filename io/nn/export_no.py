from dataclasses import dataclass

from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper

from ...io.nn_import_data import *
from ...modules.blender.model import ModelInfo
from ...modules.nn.nn import ReadNn
from ...modules.util import *


current_preset = ""


class ExportSegaNO(bpy.types.Operator, ExportHelper):
    """Export a Sega NN Model"""
    bl_idname = "export.sega_no"
    bl_label = "Export *no Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ""
    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_export_list,
        default=no_export_list[0][0],
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
        items=gn_list[-1::],
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
        items=xn_list[-1::],
    )
    Z: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=zn_list,
    )

    # generic settings

    name: BoolProperty(
        name="Write model name",
        description="Include model name in model file",
        default=True,
    )

    texture_block: BoolProperty(
        name="Write texture names",
        description="Write texture block (N*TL)",
        default=True,
    )

    bone_block: BoolProperty(
        name="Write bone names",
        description="Write bone block (N*NN)",
        default=False,
    )

    order: BoolProperty(
        name="Write texture order file",
        description="Write texture order file (for texture packing)",
        default=True,
    )

    presets: EnumProperty(
        name="Preset",
        description="Preset to pull the datatypes from",
        items=(("Big", "Highest Quality", "Highest quality, but takes the most amount of space"),
               ("Small", "Smallest Size", "Smallest file size, but lowest quality"),
               ("Player", "Player", "In game player character setting"),
               ),
    )

    # non generic
    riders_default: BoolProperty(
        name="Base board model",
        description="Is a base model for boards (adds texture and bone data)",
        default=False
    )

    # data types

    pos: EnumProperty(
        name="Positions",
        description="Position storage type",
        items=(("float", "Float", "Store data as Floats"), ("short", "Short", "Store data as Shorts")),
        default="float",
    )

    norms: EnumProperty(
        name="Normals",
        description="Normal storage type",
        items=(("float", "Float", "Store data as Floats"), ("short", "Short", "Store data as Shorts"),
               ("byte", "Byte", "Store data as Bytes")),
        default="float",
    )

    uvs: EnumProperty(
        name="Uvs",
        description="Uv storage type",
        items=(("float", "Float", "Store data as Floats"), ("short", "Short", "Store data as Shorts")),
        default="float",
    )

    cols: EnumProperty(
        name="Colours",
        description="Colour storage type",
        items=(("short", "Short", "Store data as Shorts"), ("byte", "Byte", "Store data as Bytes")),
        default="short",
    )

    # dev specific

    debug: BoolProperty(
        name="Debug mode",
        description="Print debug info",
        default=True)

    split: IntProperty(
        name="Max Simple Data Count",
        description="Maximum count for any data value before splitting (for simple meshes only)",
        default=32000,
        soft_min=1,
        soft_max=32000
    )

    def draw(self, context):
        def data_gno():
            box = layout.box()
            box.label(text="Data type settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "presets")
            global current_preset
            if current_preset != self.presets:
                current_preset = self.presets
                if current_preset == "Player":
                    self.pos = "float"
                    self.norms = "byte"
                    self.uvs = "short"
                elif current_preset == "Big":
                    self.pos = "float"
                    self.norms = "float"
                    self.uvs = "float"
                elif current_preset == "Small":
                    self.pos = "short"
                    self.norms = "byte"
                    self.uvs = "short"

            box.row().prop(self, "pos")
            box.row().prop(self, "norms")
            # I've only seen colours stored as bytes
            box.row().prop(self, "uvs")
            # weights should be chosen by the computer

        def data_xno():
            box = layout.box()
            box.label(text="Data type settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "presets")
            global current_preset
            if current_preset != self.presets:
                current_preset = self.presets
                if current_preset == "Player":
                    self.cols = "byte"
                elif current_preset == "Big":
                    self.cols = "short"
                elif current_preset == "Small":
                    self.cols = "byte"

            box.row().prop(self, "cols")

        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        bpy.context.space_data.params.filename = "Uses Armature name as file name!"
        layout.label(text="Sega NN exporter settings:", icon="KEYFRAME_HLT")

        nn_format = self.nn_format
        # when other formats are supported we can pull the file name to get what format to use
        #  optimise_no could potentially append game_name.*no to the model for the user (which could be used)
        #  ideally the format exporting priority list would be format in model name then format selected in exporter
        layout.row().prop(self, "nn_format")
        if not nn_format.endswith("_"):
            layout.row().prop(self, nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "name")
        box.row().prop(self, "texture_block")
        box.row().prop(self, "bone_block")
        box.row().prop(self, "order")

        game_format = getattr(self, nn_format, nn_format)
        if game_format == "SonicRiders_G":
            box = layout.box()
            box.label(text="Sonic Riders settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "riders_default")

        # this data varies between game and format
        nn_end = nn_format[-1]
        if nn_end == "G":
            data_gno()
        elif nn_end == "X" and nn_format != "Sonic2006_X":
            data_xno()

        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "debug")
            box.row().prop(self, "split")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.debug = False
            self.split = 32000
        settings = Settings(
            "", self.debug,
            self.name,
            self.pos,
            self.norms,
            self.cols,
            self.uvs,
            self.split,
            self.texture_block,
            self.bone_block,
            self.order,
            self.riders_default,
        )

        nn_format = self.nn_format  # "Match__", "E" etc
        nn_format = getattr(self, nn_format, nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match
        settings.format = nn_format

        # noinspection PyUnresolvedReferences
        return model_export(self.filepath, settings)


def menu_func_export(self, context):  # add to dynamic menu
    self.layout.operator(ExportSegaNO.bl_idname, text="Sega NN Model (.xno, .zno, etc.)")


@dataclass
class Settings:
    format: str
    debug: bool
    name: bool
    pos: str
    norms: str
    cols: str
    uvs: str
    split: int
    texture_block: bool
    bone_block: bool
    order: bool
    riders_default: bool


def model_export(file_path, settings):
    if settings.format == "None__":
        show_no_selection("NN Model Exporter")
        return {'CANCELLED'}

    file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))

    # batch export is not a setting for the exporter
    # get all armatures selected (and selected by child)
    arma_list = []

    selected_obj = set(bpy.context.selected_objects)
    while selected_obj:
        obj = selected_obj.pop()
        while obj.type != "ARMATURE":
            if obj.parent:
                obj = obj.parent
            else:
                break
        if obj.type == "ARMATURE":
            arma_list.append(obj)
        selected_obj = selected_obj - set(obj.children)

    arma_list = tuple(set(arma_list))

    if not arma_list:
        def draw(self, context):
            self.layout.label(text="No valid models were selected!")

        bpy.context.window_manager.popup_menu(draw_func=draw, title="NN Model Exporter", icon="ERROR")
        return {'FINISHED'}

    for arma in arma_list:
        model_info = ModelInfo(settings, arma).execute()
        if not model_info:
            return {'CANCELLED'}
        name = arma.name
        if name.endswith("." + settings.format[-1].lower() + "no"):
            pass
        else:
            name = name + "." + settings.format[-1].lower() + "no"

        name = file_path + name
        print("Writing Model Data--------------------------------")
        f = open(name, 'wb+')
        ReadNn(f, name, settings.format, settings.debug).write_model(model_info, settings)
        f.close()

        print("--------------------------------------------------")

    return {'FINISHED'}
