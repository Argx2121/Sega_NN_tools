from .modules.srpc_read_file import *

# TODO use this list instead of self defining
xno_list = (
    ("debug", "Debug", "For Reversing Vertex Block Bitflags | N/A | N/A"),
    ("s06", "Sonic '06", "Sonic '06 Model | ReadXbox | 14 Nov 2006"),
    ("psu", "Phantasy Star Universe", "Phantasy Star Universe Model | PC | 31 Aug 2006"),
    ("srpc", "Sonic Riders", "Sonic Riders Model / Archive | PC / ReadXbox | 21 Feb 2006"),
)  # keep debug first!


@dataclass
class XnoSettings:
    # generic
    model_format: str
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


@dataclass
class AssetNames:
    model_name: str
    texture_names: list
    bone_names: list


def sonic06(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.model_format).read_file()
        names = AssetNames(model_name=nn_data.file_name,
                           texture_names=nn_data.texture_names, bone_names=nn_data.bone_names)
        if nn_data.model_data:
            Model(nn_data.model_data, names, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    print_line()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_require=[".xno"])
        for filepath in file_list:
            execute()
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
    toggle_console()
    return {'FINISHED'}


def psu(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.model_format).read_block()
        names = AssetNames(model_name=bpy.path.basename(filepath),
                           texture_names=nn_data.texture_names, bone_names=nn_data.bone_names)
        if nn_data.model_data:
            Model(nn_data.model_data, names, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    print_line()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
    toggle_console()
    return {'FINISHED'}


def srpc(filepath, settings):
    def execute():
        f = open(filepath, 'rb')
        ReadFile(f, filepath, settings).execute()
        f.close()

    start_time = time()
    toggle_console()
    print_line()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_ignore=["."])
        for filepath in file_list:
            execute()
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
    toggle_console()
    return {'FINISHED'}


def debug(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.model_format, True).read_file()
        names = AssetNames(model_name=nn_data.file_name,
                           texture_names=nn_data.texture_names, bone_names=nn_data.bone_names)
        if nn_data.model_data:
            Model(nn_data.model_data, names, settings).x()
        f.close()

    settings.model_format = xno_list[0][0]
    start_time = time()
    toggle_console()
    print_line()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
    toggle_console()
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
        default=5000,
        min=0,
        max=100000,
    )

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "dev_mode")
        layout.row().prop(self, "max_len", slider=True)
        # row = layout.row()


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
        default="srpc")
    xno_ver_dev: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct xno variant)",
        items=xno_list,
        default="srpc")
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
             "Allows textures with the same name to be replace eachother "
             "(syntax: Texture_name.dds)"),
            ('complex', "Specific Names",
             "Prevents a texture from being replaced by one with the same name "
             "(syntax: Name.file.subfile.index.dds)")),
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
        def srpc_specific(xno_var):
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

            det = {"s06": s06_set, "psu": psu_set, "srpc": srpc_set, "debug": debug_set}
            det[xno_var]()

        preferences = bpy.context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.label(text="Sega NN xno importer settings:")

        if preferences.dev_mode:
            layout.row().prop(self, "xno_ver_dev")
            srpc_specific(self.xno_ver_dev)
        else:
            layout.row().prop(self, "xno_ver")
            srpc_specific(self.xno_ver)

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
        det = {"s06": sonic06, "psu": psu, "srpc": srpc, "debug": debug}
        if not preferences.dev_mode:
            self.clean = True
        settings = XnoSettings(
            model_format="",
            batch_import=self.batch,
            clean_mesh=self.clean,
            all_bones_one_length=self.length,
            max_bone_length=preferences.max_len,
            ignore_bone_scale=self.pose,
            hide_null_bones=self.bone,
            # s06
            use_vertex_colours=self.colour,
            # psu
            # srpc
            import_all_formats=self.all_blocks,
            texture_name_structure=self.image
        )
        if preferences.dev_mode:
            settings.model_format = self.xno_ver_dev
            if not self.xno_ver_dev == "s06":
                settings.use_vertex_colours = False
            return det[self.xno_ver_dev](self.filepath, settings)
        else:
            if not self.xno_ver_dev == "s06":
                settings.use_vertex_colours = False
            settings.model_format = self.xno_ver
            return det[self.xno_ver](self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNNXno.bl_idname, text="Sega NN xno (.xno)")
