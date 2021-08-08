import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.nn.import_no import batch_handler
from Sega_NN_tools.modules.util import print_line
from Sega_NN_tools.modules.other.splines.srpc import ReadPaths as Srpc
from Sega_NN_tools.modules.other.splines.sfr import ReadPaths as Sfr


class ImportSegaNNSplines(bpy.types.Operator, ImportHelper):
    """Import Spines (as edges)"""
    bl_idname = "import.sega_nn_splines"
    bl_label = "Import Spines (as edges)"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.splines"
    filter_glob: StringProperty(
        default="*.splines",
        options={'HIDDEN'},
        maxlen=255)

    game: EnumProperty(
        name="Format",
        description="Game variant",
        items=(
            ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
            ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model / Archive | 21 Feb 2006"),
            ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Model / Archive | 4 Nov 2010"),
        ),
        default="Match__"
    )

    batch: EnumProperty(
        name="Batch usage",
        description="If all files in a folder (non recursive) should be used",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files")),
        default='Single')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Splines importer settings:", icon="KEYFRAME_HLT")
        layout.row().prop(self, "game")
        box = layout.box()
        box.label(text="Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)

    def execute(self, context):
        return splines_import(self.filepath, self.game, self.batch)


def splines_import(filepath, game, settings):
    game_dict = {"SonicRiders_X": Srpc, "SonicFreeRiders_E": Sfr}

    def execute(file_path):
        f = open(file_path, 'rb')
        print_line()
        game_type = file_path.split(".")[-2]
        game_dict[game_type](f).execute()
        f.close()

    if game != "Match__" and settings == "Single" and game + ".splines" not in filepath:
        return {'FINISHED'}

    name_req = ".splines"
    if game != "Match__":
        name_req = game + ".splines"
    batch_handler(filepath, settings, execute, name_require=name_req)
    return {'FINISHED'}
