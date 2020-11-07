from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from Sega_NN_tools.io.nn_import import *
from Sega_NN_tools.io.nn_import_data import *
from Sega_NN_tools.io.nn_import import determine_function


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.

class ImportSegaNN(bpy.types.Operator, ImportHelper):
    """Import a Sega NN file (not necessarily an *.xno, *.zno etc file)"""
    bl_idname = "import.sega_nn"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import *no Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ""  # ImportHelper mixin class uses this
    filter_glob: StringProperty(
        default="*",
        options={'HIDDEN'},
        maxlen=255)  # Max internal buffer length, longer would be clamped.

    # generic
    no_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_list,
        default="Match__")

    C: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct cno variant)",
        items=cno_list,
    )
    E: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct eno variant)",
        items=eno_list,
    )
    L: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct lno variant)",
        items=lno_list,
    )
    S: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct sno variant)",
        items=sno_list,
    )
    X: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct xno variant)",
        items=xno_list,
    )
    Z: EnumProperty(
        name="Game",
        description="Game the model is from (to get the correct zno variant)",
        items=zno_list,
    )

    batch: EnumProperty(
        name="Batch usage",
        description="If all files in a folder (non recursive) should be used",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files")),
        default='Single')
    simple_mat: BoolProperty(
        name="Simple materials (for export)",
        description="Keep materials simple for exporting to other formats, meaning not all material data is imported",
        default=False)

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

    # riders specific
    image: EnumProperty(
        name="Image naming conventions",
        description="How extracted texture names should be formatted",
        items=(
            ('Simple', "Simple Names",
             "Allows textures with the same name to be replace each other (syntax: Texture_name.dds)"),
            ('Complex', "Specific Names",
             "Prevents a texture from being replaced by one with the same name (syntax: Name.file.subfile.index.dds)")),
        default='Complex')
    all_blocks: BoolProperty(
        name="Import models+ (Experimental!!)",
        description="Imports models, collision, pathfinding, etc. instead of just models",
        default=False)

    # debug specific

    # dev
    clean: BoolProperty(
        name="Clean mesh",
        description="Remove anything that will make blender crash - speeds up importing at the cost of edit mode",
        default=True)

    debug: BoolProperty(
        name="Debug mode",
        description="Print debug data",
        default=True)

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN importer settings:", icon="KEYFRAME_HLT")

        layout.row().prop(self, "no_format")
        no_nn_format = self.no_format
        if not no_nn_format.endswith("_"):
            layout.row().prop(self, no_nn_format)
        specific(no_nn_format, self)

        box = layout.box()
        box.label(text="Generic settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "batch", expand=True)
        box.row().prop(self, "simple_mat")
        box.row().prop(self, "bone")
        box.row().prop(self, "length")
        box.row().prop(self, "pose")
        if preferences.dev_mode:
            box = layout.box()
            box.label(text="Dev settings:", icon="KEYFRAME_HLT")
            box.row().prop(self, "debug")
            box.row().prop(self, "clean")

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        if not preferences.dev_mode:
            self.clean = True
            self.debug = False
        settings = Settings(
            "", 0, self.debug,
            self.batch, self.clean, self.simple_mat,
            self.length, preferences.max_len, self.pose, self.bone,
            # srpc
            self.all_blocks, self.image
        )
        no_nn_format = self.no_format
        no_format = getattr(self, no_nn_format, no_nn_format)
        settings.format = no_format
        settings.format_bone_scale = determine_bone[no_format]

        if no_format in determine_function:
            return determine_function[no_format](self.filepath, settings)
        else:
            return generic_import_1_type(self.filepath, settings)


def menu_func_import(self, context):  # add to dynamic menu
    self.layout.operator(ImportSegaNN.bl_idname, text="Sega NN (.xno, .zno, etc.)")
