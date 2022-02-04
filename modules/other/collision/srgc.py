from Sega_NN_tools.modules.util import *
from dataclasses import dataclass


class ReadCollision:
    def __init__(self, f):
        self.f = f
        self.root_node = []
        self.meshes = []

    def execute(self):
        console_out("Reading Collision...", self.read_data)
        console_out("Making Collision...", self.make_blender)

    @dataclass
    class Info:
        face_offset: int
        vertex_offset: int
        normal_offset: int
        face_strip_count: int
        face_flag: tuple
        face_strip: tuple

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(4, 1)
        node_count = read_short(f, ">")
        f.seek(2, 1)
        info = []
        for _ in range(node_count):
            self.root_node.append(read_float_tuple(f, 3, ">"))
            f.seek(4, 1)
            a = read_int(f, ">")
            f.seek(8, 1)
            b, c, d = read_int(f, ">"), read_int(f, ">"), read_byte(f, ">")
            info.append(self.Info(a, b, c, d, (), ()))
            f.seek(8 + 3, 1)

        for mesh in info:
            f.seek(start + mesh.face_offset)
            read_data = read_short_tuple(f, mesh.face_strip_count * 2, ">")
            mesh.face_flag = read_data[::2]
            mesh.face_strip = read_data[1::2]

        for mesh in info:
            vertices = []
            faces = []
            # normals = []
            net_count = 0
            vertex_count = mesh.normal_offset - mesh.vertex_offset
            vertex_count = vertex_count // 12

            for i in range(len(mesh.face_strip)):
                face_strip = mesh.face_strip[i]
                flag = mesh.face_flag[i]
                if flag:
                    for loop in range(face_strip // 2):
                        loop *= 2
                        loop += net_count
                        faces.append((loop, loop + 1, loop + 2))
                        faces.append((loop + 2, loop + 1, loop + 3))
                    if face_strip % 2 != 0:
                        loop = net_count + face_strip
                        faces.append((loop - 1, loop, loop + 1))
                else:
                    # make one face skip two faces
                    face_base = []
                    face_number = 0

                    for _ in range(face_strip):
                        face_base.append(face_number)
                        face_number += 3

                    for loop in face_base:
                        loop += net_count
                        faces.append((loop, loop + 1, loop + 2))

                net_count += face_strip + 2

            f.seek(start + mesh.vertex_offset)
            for _ in range(vertex_count):
                vertices.append(read_float_tuple(f, 3, ">"))

            # f.seek(start + mesh.normal_offset * 16)
            # for _ in range(len(faces)):
            #     normals.append(read_float_tuple(f, 3))
            #     f.seek(4, 1)

            self.meshes.append([vertices, faces])

    def make_blender(self):
        col = bpy.context.collection

        for vertices, faces in self.meshes:
            mesh = bpy.data.meshes.new("Collision")
            mesh.from_pydata(vertices, [], faces)
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708
            col.objects.link(obj)
