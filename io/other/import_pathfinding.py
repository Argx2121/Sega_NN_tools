import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.import_util import batch_handler
from Sega_NN_tools.modules.util import print_line
from Sega_NN_tools.modules.other.pathfinding.srpc import ReadXbox as Srpc
from Sega_NN_tools.modules.other.pathfinding.srzg import ReadWii as Srzg
from Sega_NN_tools.modules.other.pathfinding.sfr import ReadX360 as Sfr


class ImportSegaNNPathfinding(bpy.types.Operator, ImportHelper):
    """Import Pathfinding (as edges)"""
    bl_idname = "import.sega_nn_pathfinding"
    bl_label = "Import Pathfinding (as edges)"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.pathfinding"
    filter_glob: StringProperty(
        default="*.pathfinding",
        options={'HIDDEN'},
        maxlen=255)

    game: EnumProperty(
        name="Format",
        description="Game variant",
        items=(
            ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
            ("SonicRiders_X", "Sonic Riders", "Sonic Riders Pathfinding | 21 Feb 2006"),
            ("SonicRidersZeroGravity_G", "Sonic Riders Zero Gravity",
             "Sonic Riders Zero Gravity Pathfinding | 8 Jan 2008"),
            ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Pathfinding | 4 Nov 2010"),
        ),
        default="Match__"
    )

    batch: EnumProperty(
        name="Batch usage",
        description="What files should be imported",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files (non recursive)"),
            ('Recursive', "Recursive", "Opens files recursively")),
        default='Single')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Pathfinding importer settings:", icon="KEYFRAME_HLT")
        layout.row().prop(self, "game")
        box = layout.box()
        box.label(text="Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)

    def execute(self, context):
        return pathfinding_import(self.filepath, self.game, self.batch)


def pathfinding_import(filepath, game, settings):
    game_dict = {"SonicRiders_X": Srpc, "SonicRidersZeroGravity_G": Srzg, "SonicFreeRiders_E": Sfr}

    def execute(file_path):
        f = open(file_path, 'rb')
        print_line()
        game_type = file_path.split(".")[-2]
        game_dict[game_type](f).execute()
        f.close()

    if game != "Match__" and settings == "Single" and game + ".pathfinding" not in filepath:
        return {'FINISHED'}

    name_req = ".pathfinding"
    if game != "Match__":
        name_req = game + ".pathfinding"
    batch_handler(filepath, settings, execute, name_require=name_req)
    return {'FINISHED'}
