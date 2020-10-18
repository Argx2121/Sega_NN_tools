# info
bl_info = {
    "name": "Sega NN tools",
    "description": "Tools to import models using the NN libraries and some",
    "author": "Arg!! (Special thanks to Sewer56, Yacker, firegodjr and Shadowth117!)",
    "version": (0, 4, 0),
    "blender": (2, 80, 0),
    "location": "3d View > Sidebar",
    "warning": "",
    "wiki_url": " ",
    "category": "Import-Export",
}

import importlib

import bpy

if "NN_import" in locals():
    importlib.reload(NN_import)
    importlib.reload(NN_ui)
    importlib.reload(SRPC)
else:
    from . import NN_import
    from . import NN_ui
    from . import SRPC

# classes
classes = (
    NN_import.ImportSegaNNXno, NN_import.ImportSegaNNXnoPreferences,
    SRPC.SonicRPCTextureTools, SRPC.OpenTextureFolder,
    NN_ui.ModelExport, NN_ui.DiscordServerJoin, NN_ui.NN_PT_ModelPanel,
    NN_ui.SRPC_PT_Panel, NN_ui.SRPC_PT_Texture, NN_ui.SRPC_PT_Guide, NN_ui.SRPC_PT_Server,
    NN_ui.NN_PT_Credits
)


# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(NN_import.menu_func_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(NN_import.menu_func_import)
