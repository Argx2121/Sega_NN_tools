if "util" in locals():
    import importlib
    importlib.reload(util)
    importlib.reload(srpc_read_file)
else:
    from . import util
    from .game_specific import srpc_read_file
