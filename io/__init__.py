if "NN_import" not in locals():
    from . import NN_import, import_sega_nn
else:
    import importlib
    importlib.reload(NN_import)
    importlib.reload(import_sega_nn)
