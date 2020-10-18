import importlib
if "nn_information_file" in locals():
    importlib.reload(re_col)
    importlib.reload(re_inst)
    importlib.reload(re_path)
    importlib.reload(re_paths)
    importlib.reload(re_arc)
    importlib.reload(ex_img)
    importlib.reload(rep_img)
else:
    from .sonic_riders import read_collision as re_col
    from .sonic_riders import read_instance_models as re_inst
    from .sonic_riders import read_pathfinding as re_path
    from .sonic_riders import read_paths as re_paths
    from .sonic_riders import read_archive as re_arc
    from .sonic_riders import extract_image as ex_img
    from .sonic_riders import replace_image as rep_img
