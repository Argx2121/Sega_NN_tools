import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty


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
    minimum_split: IntProperty(
        name="Minimum Mesh Split",
        description='Minimum amount of faces a mesh has to have to be split',
        default=20,
        min=3,
        max=500,
    )

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "dev_mode")
        if self.dev_mode:
            layout.row().prop(self, "max_len", slider=True)
            layout.row().prop(self, "minimum_split", slider=True)
            # the most optimal value might differ per format but unfortunately
            #  some meshes need to be separate to animate (see sonic riders character hands)
            # 3 ends up splitting meshes into sections that are too small, and you end up taking more space than less
            #  despite not storing weights
