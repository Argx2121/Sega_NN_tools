if "NN" in locals():
    import importlib
    importlib.reload(NN)
    importlib.reload(preferences)
    importlib.reload(SRPC)
else:
    from . import NN, preferences, SRPC
