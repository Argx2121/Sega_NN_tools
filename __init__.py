bl_info = {
    "name": "Sega NN tools",
    "description": "Tools to import models using the NN libraries and some",
    "author": "Arg!! (Special thanks to Sewer56, Yacker, firegodjr and Shadowth117!)",
    "version": (0, 8, 0),
    "blender": (4, 1, 0),
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
             glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/**/*.py', recursive=True)
             if "__init__" not in f]
    [importlib.reload(sys.modules[name]) for name in files if name in sys.modules]  # refresh all loaded modules

import bpy

from .io.nn import import_no, export_no, optimise_no
from .io.other import import_collision, import_splines, import_pathfinding, import_objects
from .extract import srgc, srpc, amb, sfr, pkg, srzg, bnk, sms, gosgts
from .ui import panels, preferences

# classes
classes = (
    import_no.ImportSegaNO, preferences.ImportSegaNN, export_no.ExportSegaNO, optimise_no.OptimiseSegaNO,
    import_collision.ImportSegaNNCollision, import_splines.ImportSegaNNSplines,
    import_pathfinding.ImportSegaNNPathfinding, import_objects.ImportSegaNNObjects,
    srgc.SonicRGCTools, srpc.SonicRPCTools,
    amb.Sonic4Tools, sfr.ExtractSfrTools, bnk.ExtractBnkTools, pkg.ExtractPkgTools, sms.ExtractSmsTools,
    gosgts.ExtractGosGtsTools,
    srzg.ExtractSrgzTools,
    panels.NN_PT_ImportPanel, panels.NN_PT_ExportPanel,
    panels.EXTRACT_PT_Panel,
    panels.NN_PT_About,
)


# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(import_no.menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(export_no.menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(import_no.menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(export_no.menu_func_export)
