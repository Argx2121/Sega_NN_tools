import bpy
from ..modules.blender.model_assets.nodes import classes


class NN_MT_Node_Add(bpy.types.Menu):
    bl_label = "NN"

    def draw(self, context):
        layout = self.layout
        for cla in classes:
            var = layout.operator("node.add_node_nn", text=cla.bl_label)
            var.type = cla.bl_idname
            var.use_transform = True
        # imagine if the world was made of pudding
        layout.operator("node.nn_operator", text="Setup Nodes")


def nn_node_menu(self, context):
    if context.area.ui_type == 'ShaderNodeTree':
        layout = self.layout
        layout.separator()
        layout.menu("NN_MT_Node_Add")
