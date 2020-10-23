if "NN" in locals():
    import importlib
    importlib.reload(panels)
    importlib.reload(preferences)
    importlib.reload(SRPC)
else:
    from . import panels, preferences, SRPC
