if "panels" not in locals():
    from . import panels, preferences, SRPC, S4E1
else:
    import importlib
    importlib.reload(panels)
    importlib.reload(preferences)
    importlib.reload(SRPC)
    importlib.reload(S4E1)
