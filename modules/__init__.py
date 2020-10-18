import importlib
if "util" in locals():
    importlib.reload(util)
    importlib.reload(srpc_read_file)
else:
    from . import util
    from . import srpc_read_file
