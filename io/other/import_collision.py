import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.import_util import batch_handler
from Sega_NN_tools.modules.util import print_line
from Sega_NN_tools.modules.other.collision.srpc import ReadCollision as Srpc
from Sega_NN_tools.modules.other.collision.srzg import ReadCollision as Srzg
from Sega_NN_tools.modules.other.collision.sfr import ReadCollision as Sfr


class ImportSegaNNCollision(bpy.types.Operator, ImportHelper):
    """Import a Collision Model"""
    bl_idname = "import.sega_nn_collision"
    bl_label = "Import Collision"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.collision"
    filter_glob: StringProperty(
        default="*.collision",
        options={'HIDDEN'},
        maxlen=255)

    game: EnumProperty(
        name="Format",
        description="Game variant",
        items=(
            ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
            ("SonicRiders_X", "Sonic Riders", "Sonic Riders Collision | 21 Feb 2006"),
            ("SonicRidersZeroGravity_G", "Sonic Riders Zero Gravity",
             "Sonic Riders Zero Gravity Collision | 8 Jan 2008"),
            ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Collision | 4 Nov 2010"),
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
        layout.label(text="Collision importer settings:", icon="KEYFRAME_HLT")
        layout.row().prop(self, "game")
        box = layout.box()
        box.label(text="Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)

    def execute(self, context):
        return collision_import(self.filepath, self.game, self.batch)


def collision_import(filepath, game, settings):
    game_dict = {"SonicRiders_X": Srpc, "SonicRidersZeroGravity_G": Srzg, "SonicFreeRiders_E": Sfr}

    def execute_set(file_path):
        f = open(file_path, 'rb')
        print_line()
        game_dict[game](f).execute()
        f.close()

    def execute_match(file_path):
        f = open(file_path, 'rb')
        print_line()
        game_type = file_path.split(".")[-2]
        if game_type not in game_dict:
            return {'FINISHED'}
        game_dict[game_type](f).execute()
        f.close()

    if game != "Match__":
        name_req = game + ".collision"
        batch_handler(filepath, settings, execute_set, name_require=name_req)
    else:
        name_req = ".collision"
        batch_handler(filepath, settings, execute_match, name_require=name_req)
    return {'FINISHED'}
