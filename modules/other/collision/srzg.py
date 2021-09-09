from Sega_NN_tools.modules.util import *
from dataclasses import dataclass


class ReadCollision:
    def __init__(self, f):
        self.f = f
        self.root_node = []
        self.meshes = []

    def execute(self):
        if console_out("Reading Collision...", self.read_data) == "Cancelled":
            return
        console_out("Making Collision...", self.make_blender)

    @dataclass
    class Info:
        face_offset: int
        vertex_offset: int
        vertex_count: int
        face_count: int

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(4, 1)
        node_count = read_int(f, ">")
        if read_int(f, ">"):
            print("Unknown structure, cancelled")
            return "Cancelled"
        else:
            f.seek(start + 16)
            info = []
            for _ in range(node_count):  # len 32
                self.root_node.append((0, 0, 0))
                a, b = read_int_tuple(f, 2,  ">")
                v_count, face_count = read_int_tuple(f, 2, ">")
                f.seek(16, 1)
                info.append(self.Info(b, a, v_count, face_count))

            if info[0].vertex_offset != f.tell():
                fix = info[0].vertex_offset - f.tell()
                for mesh in info:
                    mesh.face_offset = mesh.face_offset - fix
                    mesh.vertex_offset = mesh.vertex_offset - fix

            for mesh in info:
                vertices = []
                faces = []

                f.seek(start + mesh.face_offset)
                for _ in range(mesh.face_count):
                    faces.append(read_short_tuple(f, 3, ">"))

                f.seek(start + mesh.vertex_offset)
                for _ in range(mesh.vertex_count):
                    vertices.append(read_float_tuple(f, 3, ">"))
                    f.seek(4, 1)

                self.meshes.append([vertices, faces])

    def make_blender(self):
        col = bpy.context.collection

        for vertices, faces in self.meshes:
            mesh = bpy.data.meshes.new("Collision")
            mesh.from_pydata(vertices, [], faces)
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708
            col.objects.link(obj)
