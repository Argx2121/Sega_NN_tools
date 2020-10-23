
bl_info = {
    "name": "Sega NN tools",
    "description": "Tools to import models using the NN libraries and some",
    "author": "Arg!! (Special thanks to Sewer56, Yacker, firegodjr and Shadowth117!)",
    "version": (0, 4, 0),
    "blender": (2, 80, 0),
    "location": "3d View > Sidebar",
    "warning": "",
    "wiki_url": "https://github.com/Argx2121/Sega_NN_tools/wiki",
    "tracker_url": "https://github.com/Argx2121/Sega_NN_tools/issues/new",
    "category": "Import-Export",
}

import glob
import importlib
import os
import sys

import bpy

files = glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/**/*.py', recursive=True)
files = [file for file in files if "__init__" not in file]
file_list = []
for file in files:
    file_list.append(__package__ + file.split(__package__)[1].replace("\\", ".")[:-3])

if __package__ + ".io" in sys.modules:
    for name in file_list:
        importlib.reload(sys.modules[name])

[importlib.import_module(file) for file in file_list]


from .io import NN_import, import_sega_nn
from .ui import panels, SRPC, preferences, S4E1


# classes
classes = (
    import_sega_nn.ImportSegaNN, preferences.ImportSegaNN,
    SRPC.SonicRPCTextureTools, SRPC.OpenTextureFolder, S4E1.Sonic4E1Tools,
    panels.ModelExport, panels.DiscordServerJoin, panels.NN_PT_ModelPanel,
    panels.SRPC_PT_Panel, panels.SRPC_PT_Texture, panels.SRPC_PT_Guide, panels.SRPC_PT_Server,
    panels.S4E1_PT_Panel,
    panels.NN_PT_Credits
)


# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(import_sega_nn.menu_func_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(import_sega_nn.menu_func_import)
