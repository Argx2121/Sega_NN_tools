import bpy
import addon_utils
import requests


u_ver = [addon.bl_info.get('version') for addon in addon_utils.modules() if addon.bl_info['name'] == 'Sega NN tools'][0]

try:
    l_ver = requests.get("https://github.com/Argx2121/Sega_NN_tools/releases/latest").url.rsplit("/")[-1]
    if "." in l_ver:
        l_ver = tuple(int(a) for a in l_ver.split("."))
    else:
        l_ver = "No Releases."
except (requests.ConnectionError, requests.Timeout) as exception:
    l_ver = "No Connection."


class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sega NN Tools"


class NN_PT_ModelPanel(GENERIC_panel, bpy.types.Panel):
    bl_label = "Models"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Can also use File > Import")  # / Export")
        row = layout.row()
        row.operator("import.sega_nn")
        # row.operator("export.sega_nn")


class SRPC_PT_Panel(GENERIC_panel, bpy.types.Panel):
    bl_idname = "SRPC_PT_Panel"
    bl_label = "Sonic Riders PC Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("srpc_image_tools.open_texture_folder")
        layout.operator("srpc_image_tools.texture_tools")
        layout.operator("wm.url_open", text="Guide Link").url = \
            "https://github.com/Argx2121/Sega_NN_tools/tree/master#texture-swapping"
        layout.label(text="Quick Guide:")
        box = layout.box()
        box.label(text="Extract images")
        box.label(text="Replace with custom textures")
        box.label(text="Insert images")
        layout.label(text="Reminders:")
        box = layout.box()
        box.label(text="Keep images the same size")
        box.label(text="Complex names for maps")
        box.label(text="Simple for player models")
        box.label(text="Max dimensions: 4K")
        box.label(text="Image format: .dds (Dxt1, 3 or 5)")


class S4E1_PT_Panel(GENERIC_panel, bpy.types.Panel):
    bl_idname = "S4E1_PT_Panel"
    bl_label = "Sonic 4 Episode 1 PC Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("s4e1.extract")


class NN_PT_About(GENERIC_panel, bpy.types.Panel):
    bl_label = "About"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Version: " + str(u_ver))
        if l_ver == u_ver:
            layout.label(text="You're on the latest version.")
        elif "No" in l_ver:
            layout.label(text=l_ver)
        else:
            layout.label(text="You're not on the latest version!", icon="ERROR")
            layout.operator("wm.url_open", text="Latest Release Link: " + str(l_ver)).url = \
                "https://github.com/Argx2121/Sega_NN_tools/releases/latest"
        layout.label(text="NN tools by Arg!!")
        box = layout.box()
        box.label(text="Special thanks:")
        box.label(text="firegodjr")
        box.label(text="Sewer56")
        box.label(text="Shadowth117")
        box.label(text="Yacker")
        layout.operator("wm.url_open", text="Discord Link").url = "https://discord.gg/CURRBfq"
        layout.operator("wm.url_open", text="GitHub Link").url = "https://github.com/Argx2121/Sega_NN_tools/"
