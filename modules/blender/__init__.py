import importlib

if "model" in locals():
    importlib.reload(armature)
    importlib.reload(materials)
    importlib.reload(mesh)
    importlib.reload(model_util)
else:
    from . import model
    from .model_assets import armature
    from .model_assets import materials
    from .model_assets import mesh
    from .model_assets import model_util
