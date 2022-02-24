import bpy

from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper

from ...io.import_util import batch_handler
from ...modules.util import print_line

from ...modules.other.objects.srgc import ReadInstanceModels as Srgc
from ...modules.other.objects.srpc import ReadInstanceModels as Srpc
from ...modules.other.objects.srzg import ReadInstanceModels as Srzg
from ...modules.other.objects.sfr import ReadInstanceModels as Sfr


class ImportSegaNNObjects(bpy.types.Operator, ImportHelper):
    """Import object placement"""
    bl_idname = "import.sega_nn_objects"
    bl_label = "Import object placement"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = "*.objects"
    filter_glob: StringProperty(
        default="*.objects",
        options={'HIDDEN'},
        maxlen=255)

    game: EnumProperty(
        name="Format",
        description="Game variant",
        items=(
            ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
            ("SonicRiders_G", "Sonic Riders GC", "Sonic Riders Gamecube Objects | 21 Feb 2006"),
            ("SonicRiders_X", "Sonic Riders PC", "Sonic Riders Pc Objects | 21 Feb 2006"),
            ("SonicRidersZeroGravity_G", "Sonic Riders Zero Gravity",
             "Sonic Riders Zero Gravity Objects | 8 Jan 2008"),
            ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Objects | 4 Nov 2010"),
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
        layout.label(text="Item placement importer settings:", icon="KEYFRAME_HLT")
        layout.row().prop(self, "game")
        box = layout.box()
        box.label(text="Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)

    def execute(self, context):
        return objects_import(self.filepath, self.game, self.batch)


def objects_import(filepath, game, settings):
    game_dict = {
        "SonicRiders_G": Srgc, "SonicRiders_X": Srpc, "SonicRidersZeroGravity_G": Srzg, "SonicFreeRiders_E": Sfr}

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
        name_req = game + ".objects"
        batch_handler(filepath, settings, execute_set, name_require=name_req)
    else:
        name_req = ".objects"
        batch_handler(filepath, settings, execute_match, name_require=name_req)
    return {'FINISHED'}
