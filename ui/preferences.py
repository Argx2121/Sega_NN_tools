import bpy
from bpy.props import BoolProperty, FloatProperty


class ImportSegaNN(bpy.types.AddonPreferences):
    bl_idname = __package__.partition(".")[0]

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