import bpy


class ModelExport(bpy.types.Operator):
    """Not supported yet!"""
    bl_idname = "srpc_tools.model_export"
    bl_label = "Not Available"  # "Export"

    def execute(self, context):
        print("Exporting not supported yet!")
        return {'FINISHED'}


class DiscordServerJoin(bpy.types.Operator):
    """Open the Sonic Riders Discord Server"""
    bl_idname = "srpc_tools.discord_server_join"
    bl_label = "Sonic Riders TE Discord Server"

    def execute(self, context):
        print("Opening hyperlink")
        bpy.ops.wm.url_open(url="https://discord.gg/GPgZdKq")
        return {'FINISHED'}


class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sega NN Tools"


class NN_PT_ModelPanel(GENERIC_panel, bpy.types.Panel):
    bl_label = "Models"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Can also use File > Import / Export")
        box = layout.box()
        row = box.row()
        row.operator("import_sega_nn.xno")
        row.operator("srpc_tools.model_export")


class SRPC_PT_Panel(GENERIC_panel, bpy.types.Panel):
    bl_idname = "SRPC_PT_Panel"
    bl_label = "Sonic Riders PC Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class SRPC_PT_Texture(GENERIC_panel, bpy.types.Panel):
    bl_parent_id = "SRPC_PT_Panel"
    bl_idname = "SRPC_PT_Texture"
    bl_label = "Texture swapping"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Change player textures - see Guide.")
        box = layout.box()
        box.operator("srpc_image_tools.open_texture_folder")
        row = box.row()
        row.operator("srpc_image_tools.texture_tools")


class SRPC_PT_Guide(GENERIC_panel, bpy.types.Panel):
    bl_parent_id = "SRPC_PT_Panel"
    bl_label = "Texture swapping Guide"

    def draw(self, context):
        layout = self.layout
        layout.label(text="1) Extract images - complex names for maps!")
        layout.label(text="2) Replace folders textures with your own")
        layout.label(text="3) Insert images")
        layout.label(text="Max dimensions: 4K")
        layout.label(text="Format spec: .dds file (Dxt1, 3 or 5)")


class SRPC_PT_Server(GENERIC_panel, bpy.types.Panel):
    bl_parent_id = "SRPC_PT_Panel"
    bl_label = "Discord Server"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Join the Riders server!")
        box = layout.box()
        box.operator("srpc_tools.discord_server_join")


class NN_PT_Credits(GENERIC_panel, bpy.types.Panel):
    bl_label = "About / Credits"
    bl_idname = "NN_PT_Credits"

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN tools by Arg!!")
        layout.label(text="Special thanks:")
        layout.label(text="firegodjr, Sewer56, Shadowth117 and Yacker")
