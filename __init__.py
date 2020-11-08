bl_info = {
    "name": "Sega NN tools",
    "description": "Tools to import models using the NN libraries and some",
    "author": "Arg!! (Special thanks to Sewer56, Yacker, firegodjr and Shadowth117!)",
    "version": (0, 5, 0),
    "blender": (2, 80, 0),
    "location": "3d View > Sidebar",
    "warning": "",
    "wiki_url": "https://github.com/Argx2121/Sega_NN_tools/wiki",
    "tracker_url": "https://github.com/Argx2121/Sega_NN_tools/issues/new",
    "category": "Import-Export",
}

# import all and reload all if loaded

import glob
import importlib
import os
import sys


# get all .py files in this addon recursively, remove __init__ files and convert those files from absolute to relative
# (to this package), make them use dot notation and remove file extension

if __package__ + ".io" in sys.modules:  # Sega_NN_tools is already loaded in to read this - check a sub file instead
    files = [__package__ + f.split(__package__)[1].replace("\\", ".").replace("/", ".")[:-3] for f in
             glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/**/*.py', recursive=True) if "__init__" not in f]
    [importlib.reload(sys.modules[name]) for name in files if name in sys.modules]  # refresh all loaded modules

import bpy

from .io import nn_import, nn_import_settings
from .ui import panels, srpc, preferences, s4e1

# classes
classes = (
    nn_import_settings.ImportSegaNN, preferences.ImportSegaNN,
    srpc.SonicRPCTextureTools, srpc.OpenTextureFolder, s4e1.Sonic4E1Tools,
    panels.NN_PT_ModelPanel,
    panels.SRPC_PT_Panel,
    panels.S4E1_PT_Panel,
    panels.NN_PT_About
)


# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(nn_import_settings.menu_func_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(nn_import_settings.menu_func_import)
