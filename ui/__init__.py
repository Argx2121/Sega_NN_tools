if "NN" in locals():
    import importlib
    importlib.reload(panels)
    importlib.reload(preferences)
    importlib.reload(SRPC)
    importlib.reload(S4E1)
else:
    from . import panels, preferences, SRPC, S4E1
