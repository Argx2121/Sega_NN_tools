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
        row = layout.row()
        row.operator("import.sega_nn")
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
        layout.operator("srpc_image_tools.open_texture_folder")
        layout.operator("srpc_image_tools.texture_tools")


class SRPC_PT_Guide(GENERIC_panel, bpy.types.Panel):
    bl_parent_id = "SRPC_PT_Panel"
    bl_label = "Texture swapping Guide"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.url_open", text="Link to proper guide").url = \
            "https://github.com/Argx2121/Sega_NN_tools/tree/master#texture-swapping"
        box = layout.box()
        box.label(text="1) Extract images - complex names for maps!")
        box.label(text="2) Replace folders textures with your own")
        box.label(text="3) Insert images")
        box = layout.box()
        box.label(text="Max dimensions: 4K")
        box.label(text="Format spec: .dds file (Dxt1, 3 or 5)")


class SRPC_PT_Server(GENERIC_panel, bpy.types.Panel):
    bl_parent_id = "SRPC_PT_Panel"
    bl_label = "Discord Server"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Join the Riders server!")
        layout.operator("srpc_tools.discord_server_join")


class S4E1_PT_Panel(GENERIC_panel, bpy.types.Panel):
    bl_idname = "S4E1_PT_Panel"
    bl_label = "Sonic 4 Episode 1 PC Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("s4e1.extract")


class NN_PT_Credits(GENERIC_panel, bpy.types.Panel):
    bl_label = "About / Credits"
    bl_idname = "NN_PT_Credits"

    def draw(self, context):
        layout = self.layout
        layout.label(text="NN tools by Arg!!")
        box = layout.box()
        box.label(text="Special thanks:")
        box.label(text="firegodjr")
        box.label(text="Sewer56")
        box.label(text="Shadowth117")
        box.label(text="Yacker")
