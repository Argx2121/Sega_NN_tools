from dataclasses import dataclass

from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper

from ...io.nn_import_data import *
from ...modules.blender.camera import CameraInfo
from ...modules.nn.nn import ReadNn
from ...modules.util import *


current_preset = ""


class ExportSegaND(bpy.types.Operator, ExportHelper):
    """Export a Sega NN Camera"""
    bl_idname = "export.sega_nd"
    bl_label = "Export *nd, *nc Camera"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ""
    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255)

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*nd, *nc variant",
        items=nn_export_list,
        default=nn_export_list[0][0],
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

    # scene
    over_scene: BoolProperty(
        name="Scene data",
        description="Use NN Data that overrides scene values (eg. Framerate, euler rotation)",
        default=False,
    )

    # dev specific

    debug: BoolProperty(
        name="Debug mode",
        description="Print debug info",
        default=True)
    animations: BoolProperty(
        name="Export animation",
        description="Exports animations from blender",
        default=True)

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        bpy.context.space_data.params.filename = "Uses Camera name as file name!"
        layout.label(text="Sega NN exporter settings:", icon="KEYFRAME_HLT")

        nn_format = self.nn_format
        layout.row().prop(self, "nn_format")
        if not nn_format.endswith("_"):
            layout.row().prop(self, nn_format)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "name")

        box = layout.box()
        box.label(text="Override settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "over_scene")

        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "debug")
            box.row().prop(self, "animations")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.debug = False
            self.animations = True
        settings = Settings(
            "", self.debug,
            self.animations,
            self.name,
            self.over_scene,
        )

        nn_format = self.nn_format  # "Match__", "E" etc
        nn_format = getattr(self, nn_format, nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match
        settings.format = nn_format

        # noinspection PyUnresolvedReferences
        return camera_export(self.filepath, settings)


def menu_func_export(self, context):  # add to dynamic menu
    self.layout.operator(ExportSegaND.bl_idname, text="Sega NN Camera (.xnc, .znd, etc.)")


@dataclass
class Settings:
    format: str
    debug: bool
    animations: bool
    name: bool
    over_scene: bool


def camera_export(file_path, settings):
    if settings.format == "None__":
        show_no_selection("NN Camera Exporter")
        return {'CANCELLED'}

    file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
    # batch export is not a setting for the exporter
    # get all objs selected
    cam_list = []

    selected_obj = set(bpy.context.selected_objects)
    while selected_obj:
        obj = selected_obj.pop()
        if obj.type == "CAMERA":
            cam_list.append(obj)

    cam_list = tuple(set(cam_list))

    if not cam_list:
        def draw(self, context):
            self.layout.label(text="No valid cameras were selected!")

        bpy.context.window_manager.popup_menu(draw_func=draw, title="NN Model Exporter", icon="ERROR")
        return {'FINISHED'}

    for cam in cam_list:
        name, cam_info, animation_info = CameraInfo(settings, cam).execute()
        if settings.debug:
            print(cam_info)
        name = file_path + name
        print("Writing Camera Data-------------------------------")
        f = open(name, 'wb+')
        ReadNn(f, name, settings.format, settings.debug).write_camera(cam_info, settings)
        f.close()

        print("--------------------------------------------------")

    return {'FINISHED'}
