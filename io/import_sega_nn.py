from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.NN_import import *

model_list = (
    # keep debug first!!
    ("Debug__", "Debug", "For Developer testing and otherwise | N/A | N/A"),
    # extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!) | N/A | N/A"),
    # game formats from newest to oldest
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | PC | 7 Oct 2010"),
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | XBOX | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | PC / XBOX | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model / Archive | PC / XBOX | 21 Feb 2006"),
    # syntax plays a role in importing so follow this arrangement:
    # [game (caramel caps) + _ + nn indicator (_ for non game)], [game], [game + file | platform | release date]
    # therefore sonic riders (xbox) released 21st February 2006 becomes:
    # [SonicRiders_X], [Sonic Riders], [Sonic Riders Model / Archive | PC / XBOX | 21 Feb 2006]
    # please don't shorten names, _ is used in non games as the variable is reassigned
)

# the other relevant tuples / dictionaries are:
# determine_draw, determine_bone and determine_function


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.


class ImportSegaNN(bpy.types.Operator, ImportHelper):
    """Import a Sega NN file (not necessarily an *.xno, *.zno etc file)"""
    bl_idname = "import.sega_nn"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Sega NN Model"
    filename_ext = ""  # ImportHelper mixin class uses this
    filter_glob: StringProperty(
        default="*",
        options={'HIDDEN'},
        maxlen=255)  # Max internal buffer length, longer would be clamped.

    # generic
    no_ver: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct *no variant)",
        items=model_list[1:],
        default="Match__")
    no_ver_dev: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct *no variant)",
        items=model_list,
        default="Match__")
    batch: EnumProperty(
        name="Batch usage",
        description="If all files in a folder (non recursive) should be used",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files")),
        default='Single')

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

    # sonic 06 specific
    colour: BoolProperty(
        name="Import vertex colours",
        description="Import vertex colours - colours may make the model appear distorted",
        default=False)

    # psu specific

    # riders specific
    image: EnumProperty(
        name="Image naming conventions",
        description="How extracted texture names should be formatted",
        items=(
            ('simple', "Simple Names",
             "Allows textures with the same name to be replace eachother (syntax: Texture_name.dds)"),
            ('complex', "Specific Names",
             "Prevents a texture from being replaced by one with the same name (syntax: Name.file.subfile.index.dds)")),
        default='simple')
    all_blocks: BoolProperty(
        name="Import models+",
        description="Imports models, collision, pathfinding, etc. instead of just models",
        default=False)

    # debug specific

    # dev
    clean: BoolProperty(
        name="Clean mesh",
        description="Remove anything that will make blender crash - speeds up importing at the cost of edit mode",
        default=True)

    def draw(self, context):
        def specific(no_var):
            def match_set():  # match should have all settings because we haven't set a format
                layout.label(text="All specific settings:")
                s06_set()
                srpc_set()

            def s06_set():
                layout.label(text="Sonic '06 specific settings:")
                layout.row().prop(self, "colour")

            def srpc_set():
                layout.label(text="Riders specific settings:")
                layout.row().prop(self, "image", expand=True)
                layout.row().prop(self, "all_blocks")

            def empty_set():
                pass

            determine_draw = {
                "Match__": match_set, "Debug__": empty_set,
                "Sonic2006_X": s06_set, "PhantasyStarUniverse_X": empty_set, "SonicRiders_X": srpc_set,
                "Sonic4Episode1_Z": empty_set
            }
            determine_draw[no_var]()  # execute the right ui for the format

        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN importer settings:")

        if preferences.dev_mode:
            layout.row().prop(self, "no_ver_dev")
            specific(self.no_ver_dev)
        else:
            layout.row().prop(self, "no_ver")
            specific(self.no_ver)

        layout.label(text="Generic settings:")
        layout.row().prop(self, "batch", expand=True)
        layout.row().prop(self, "bone")
        layout.row().prop(self, "length")
        layout.row().prop(self, "pose")
        if preferences.dev_mode:
            layout.label(text="Dev settings:")
            layout.row().prop(self, "clean")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        determine_function = {
            "Match__": match, "Debug__": debug,
            "Sonic2006_X": sonic_2006_x, "PhantasyStarUniverse_X": phantasy_star_universe_x,
            "SonicRiders_X": sonic_riders_x,
            "Sonic4Episode1_Z": sonic_4_episode_1_z
        }
        if not preferences.dev_mode:
            self.clean = True
        settings = Settings(
            "", 0,
            self.batch, self.clean, self.length, preferences.max_len, self.pose, self.bone,
            # s06
            self.colour,
            # psu
            # srpc
            self.all_blocks, self.image
        )
        if preferences.dev_mode:
            no_ver = self.no_ver_dev
        else:
            no_ver = self.no_ver
        settings.format = no_ver
        settings.format_bone_scale = determine_bone[no_ver]
        if no_ver not in ["Sonic2006_X", "Match__"]:
            settings.use_vertex_colours = True
        return determine_function[no_ver](self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNN.bl_idname, text="Sega NN (.xno, .zno, etc.)")
