from ...util import *


class ReadWii:
    def __init__(self, f):
        self.f = f
        self.position = []
        self.edge = []

    def execute(self):
        console_out("Reading Pathfinding...", self.read_data)
        console_out("Making Pathfinding...", self.make_blender)

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(8, 1)
        to_verts, to_edges = read_int_tuple(f, 2, ">")
        f.seek(12, 1)
        vert_count, edge_count = read_int_tuple(f, 2, ">")

        if to_verts != 48:
            fix = to_verts - 48
            to_verts = to_verts - fix
            to_edges = to_edges - fix

        f.seek(start + to_verts)
        for i in range(vert_count):
            self.position.append(read_float_tuple(f, 3, ">"))

        f.seek(start + to_edges)
        for _ in range(edge_count):
            self.edge.append(read_short_tuple(f, 2, ">"))
            f.seek(60, 1)

    def make_blender(self):
        mesh = bpy.data.meshes.new("Pathfinding")
        mesh.from_pydata(self.position, self.edge, [])
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.rotation_euler[0] = 1.5708

        bpy.context.collection.objects.link(obj)
