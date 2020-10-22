if "NN_import" in locals():
    import importlib
    importlib.reload(NN_import)
    importlib.reload(import_sega_nn)
else:
    from . import NN_import, import_sega_nn
