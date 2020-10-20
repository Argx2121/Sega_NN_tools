from .modules.srpc_read_file import *


xno_list = (
    # keep debug first!!
    ("debug", "Debug", "For Reversing Vertex Block Bitflags | N/A"),
    # extra import functions
    ("match", "Match", "Tries to match the file with a known format (Experimental!!) | N/A"),
    # game formats from newest to oldest
    ("s06", "Sonic '06", "Sonic '06 Model | 14 Nov 2006"),
    ("psu", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("srpc", "Sonic Riders", "Sonic Riders Model / Archive | 21 Feb 2006"),
)


@dataclass
class XnoSettings:
    # generic
    model_format: str
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
            settings.model_format = "s06"
            sonic06(filepath, settings)
        elif first_uint == 1112496206:  # NXOB
            print("Game assumed to be Phantasy Star Universe")
            stdout.flush()
            settings.model_format = "psu"
            psu(filepath, settings)
        elif 0 < first_uint < 100:  # typically ~ 45 models in a srpc map file
            print("Game assumed to be Sonic Riders")
            stdout.flush()
            settings.model_format = "srpc"
            srpc(filepath, settings)
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


def sonic06(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.model_format).read_file()
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


def psu(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.model_format).read_block()
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


def srpc(filepath, settings):
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


def debug(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.model_format, True).read_file()
        if nn_data.model_data:
            Model(nn_data, settings).x()
        f.close()

    settings.model_format = "s06"
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


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import *


# from bpy.types import Operator


class ImportSegaNNXnoPreferences(bpy.types.AddonPreferences):
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


class ImportSegaNNXno(bpy.types.Operator, ImportHelper):
    """Import a Sega Xno Model (not necessarily an *.xno file)"""
    bl_idname = "import_sega_nn.xno"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Xno"
    filename_ext = ""  # ImportHelper mixin class uses this
    filter_glob: StringProperty(
        default="*",
        options={'HIDDEN'},
        maxlen=255)  # Max internal buffer length, longer would be clamped.

    # generic
    xno_ver: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct xno variant)",
        items=xno_list[1:],
        default="match")
    xno_ver_dev: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct xno variant)",
        items=xno_list,
        default="match")
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
        def specific(xno_var):
            def match_set():  # match should have all settings because we haven't set a format
                layout.label(text="All specific settings:")
                s06_set()
                psu_set()
                srpc_set()
                debug_set()

            def s06_set():
                layout.label(text="Sonic '06 specific settings:")
                layout.row().prop(self, "colour")

            def psu_set():
                pass

            def srpc_set():
                layout.label(text="Riders specific settings:")
                layout.row().prop(self, "image", expand=True)
                layout.row().prop(self, "all_blocks")

            def debug_set():
                pass

            det = {"match": match_set, "s06": s06_set, "psu": psu_set, "srpc": srpc_set, "debug": debug_set}
            det[xno_var]()  # execute the right ui for the format

        preferences = bpy.context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.label(text="Sega NN xno importer settings:")

        if preferences.dev_mode:
            layout.row().prop(self, "xno_ver_dev")
            specific(self.xno_ver_dev)
        else:
            layout.row().prop(self, "xno_ver")
            specific(self.xno_ver)

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
        det = {"match": match, "s06": sonic06, "psu": psu, "srpc": srpc, "debug": debug}
        b_det = {"match": 1, "s06": 10, "psu": 1, "srpc": 0.1, "debug": 1}
        if not preferences.dev_mode:
            self.clean = True
        settings = XnoSettings(
            "", 0,
            self.batch, self.clean, self.length, preferences.max_len, self.pose, self.bone,
            # s06
            self.colour,
            # psu
            # srpc
            self.all_blocks, self.image
        )
        if preferences.dev_mode:
            xno_ver = self.xno_ver_dev
        else:
            xno_ver = self.xno_ver
        settings.model_format = xno_ver
        settings.format_bone_scale = b_det[xno_ver]
        if xno_ver != "s06":
            settings.use_vertex_colours = True
        return det[xno_ver](self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNNXno.bl_idname, text="Sega NN xbox (.xno)")
