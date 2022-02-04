from Sega_NN_tools.modules.util import *


class ReadPaths:
    def __init__(self, f):
        self.f = f
        self.paths = []

    def execute(self):
        if console_out("Reading Paths...", self.read_data) == "Cancelled":
            return
        console_out("Making Paths...", self.make_blender)

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(8, 1)
        count = read_short_tuple(f, 2, ">")[1]
        if count <= 1:
            print("Unknown structure, cancelled")
            return "Cancelled"

        offsets = read_int_tuple(f, count, ">")

        for offset in offsets:
            f.seek(start + offset)
            sub_offsets = read_int_tuple(f, 3, ">")
            f.seek(16, 1)
            vert_count = read_short(f, ">")
            points = []

            f.seek(sub_offsets[1] + start)
            for a in range(vert_count):
                points.append(read_float_tuple(f, 3, ">"))

            edges = [(a, a + 1) for a in list(range(len(points) - 1))]
            self.paths.append([points, edges])

    def make_blender(self):
        for [points, edges] in self.paths:
            mesh = bpy.data.meshes.new("Paths")
            mesh.from_pydata(points, edges, [])
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708

            bpy.context.collection.objects.link(obj)
