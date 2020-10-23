if "model_data" not in locals():
    from . import bones
    from . import faces
    from . import materials
    from . import meshes
    from . import model_data
    from . import vertices
else:
    import importlib
    importlib.reload(bones)
    importlib.reload(faces)
    importlib.reload(materials)
    importlib.reload(meshes)
    importlib.reload(model_data)
    importlib.reload(vertices)
