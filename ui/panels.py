import bpy
import addon_utils
import requests

# noinspection PyArgumentList
user_ver = [addon.bl_info.get('version') for addon in addon_utils.modules()
            if addon.bl_info['name'] == "Sega NN tools"][0]

try:
    latest_ver = requests.get("https://github.com/Argx2121/Sega_NN_tools/releases/latest").url.rsplit("/")[-1]
    if "." in latest_ver:
        latest_ver = tuple(int(a) for a in latest_ver.split("."))
    else:
        latest_ver = "No Releases."
except (requests.ConnectionError, requests.Timeout) as exception:
    latest_ver = "No Connection."


class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sega NN Tools"


class NN_PT_ModelPanel(GENERIC_panel, bpy.types.Panel):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        layout.operator("import.sega_no", text="Model .*no")
        layout.label(text="Extra Imports")
        layout.operator("import.sega_nn_collision", text="Collision .collision")
        layout.operator("import.sega_nn_pathfinding", text="Pathfinding .pathfinding")
        layout.operator("import.sega_nn_splines", text="Splines .splines")
        layout.operator("import.sega_nn_objects", text="Objects .objects")


class EXTRACT_PT_Panel(GENERIC_panel, bpy.types.Panel):
    bl_label = "File Extraction"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("amb.extract", text="Sonic 4 .AMB")
        layout.operator("bnk.extract", text="Bank file .bnk")
        layout.operator("pkg.extract", text="Sega Superstars .DIR and .PKG")
        layout.operator("srpc.extract", text="Sonic Riders PC (NO EXTENSION)")
        layout.operator("srzg.extract", text="Sonic Riders Zero Gravity .pack")
        layout.operator("sfr.extract", text="Sonic Free Riders .pac / .pas")


class NN_PT_About(GENERIC_panel, bpy.types.Panel):
    bl_label = "About"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Version: " + str(user_ver))
        if latest_ver == user_ver:
            layout.label(text="You're on the latest version.")
        elif "No" in latest_ver:
            layout.label(text=latest_ver)
        else:
            layout.label(text="You're not on the latest version!", icon="ERROR")
            layout.operator("wm.url_open", text="Latest Release Link: " + str(latest_ver)).url = \
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
