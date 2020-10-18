import importlib
if "model_data" in locals():
    importlib.reload(bones)
    importlib.reload(faces)
    importlib.reload(materials)
    importlib.reload(meshes)
    importlib.reload(model_data)
    importlib.reload(vertices)
else:
    from . import bones
    from . import faces
    from . import materials
    from . import meshes
    from . import model_data
    from . import vertices
