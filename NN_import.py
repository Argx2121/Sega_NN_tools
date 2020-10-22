from .modules.srpc_read_file import *


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

determine_bone = {
    "Match__": 1, "Debug__": 1,
    "Sonic2006_X": 10, "PhantasyStarUniverse_X": 1, "SonicRiders_X": 0.1,
    "Sonic4Episode1_Z": 1
}

# the other relevant tuples / dictionaries are:
# determine_draw and determine_function


@dataclass
class Settings:
    # generic
    format: str
    format_bone_scale: int
    batch_import: str
    clean_mesh: bool
    all_bones_one_length: bool
    max_bone_length: float
    ignore_bone_scale: bool
    hide_null_bones: bool
    # s06
    use_vertex_colours: bool
    # psu
    # srpc
    import_all_formats: bool
    texture_name_structure: str


def finish_process(start_time):
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
    toggle_console()


def match(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        first_uint = read_int(f)  # xno is always little endian
        f.close()
        if first_uint == 1179211854:  # NXIF
            print("Game assumed to be Sonic '06")
            stdout.flush()
            settings.format = "Sonic2006_X"
            settings.format_bone_scale = determine_bone[settings.format]

            sonic_2006_x(filepath, settings)

        elif first_uint == 1112496206:  # NXOB
            print("Game assumed to be Phantasy Star Universe")
            stdout.flush()
            settings.format = "PhantasyStarUniverse_X"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            phantasy_star_universe_x(filepath, settings)

        elif first_uint == 1112359203:  # #AMB
            print("Game assumed to be Sonic 4 Episode 1")
            stdout.flush()
            settings.format = "Sonic4Episode1_Z"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            sonic_4_episode_1_z(filepath, settings)

        elif 0 < first_uint < 100:  # typically ~ 45 models in a srpc map file
            print("Game assumed to be Sonic Riders")
            stdout.flush()
            settings.format = "SonicRiders_X"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            sonic_riders_x(filepath, settings)

        else:
            print("Couldn't match to a game")
            stdout.flush()

    if settings.batch_import == "Single":
        execute()
        print_line()
        stdout.flush()
    else:
        file_list = get_files(filepath)
        settings.batch_import = "Single"
        for filepath in file_list:
            execute()
            print_line()
            stdout.flush()
    return {'FINISHED'}


def debug(filepath, settings):  # todo remove debug and use as variable instead + tie printing to it
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.format, True).read_file()
        if nn_data.model_data:
            Model(nn_data, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}


def sonic_2006_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.format).read_file()
        if nn.model_data:
            Model(nn, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_require=[".xno"])
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}


def phantasy_star_universe_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.format).read_block()
        nn.file_name = bpy.path.basename(filepath)
        if nn.model_data:
            Model(nn, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}


def sonic_riders_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        ReadFile(f, filepath, settings).execute()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_ignore=["."])
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}


def sonic_4_episode_1_z(filepath, settings):
    """
    def execute():
        print_line()
        f = open(filepath, 'rb')
        ReadFile(f, filepath, settings).execute()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_ignore=["."])
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}
    """
    pass


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import *


class ImportSegaNNPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    dev_mode: BoolProperty(
        name="Dev Mode",
        description="Shows some features useful for debug",
        default=False,
    )
    max_len: FloatProperty(
        name="Max bone length",
        description='Max bone length, only applicable if "Keep bones one size" is false. Scales with format',
        default=250,
        min=1,
        max=1000,
    )

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "dev_mode")
        if self.dev_mode:
            layout.row().prop(self, "max_len", slider=True)


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

        preferences = bpy.context.preferences.addons[__package__].preferences
        layout = self.layout
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
        preferences = bpy.context.preferences.addons[__package__].preferences
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
