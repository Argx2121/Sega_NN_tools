from ...nn_util import *


class ReadCollision:
    def __init__(self, f, next_block):
        self.f = f
        self.next_block = next_block
        self.root_node = []
        self.vertex_list = []
        self.face_strip_len = []

    def execute(self):
        console_out("Reading Collision...", self.read_data)
        console_out("Making Collision...", self.make_blender)

    def make_faces(self):
        faces = []

        def _1():
            s = 2
            for strip in self.face_strip_len:
                for i in range(strip):
                    if i % 2 == 0:
                        i += s  # has to be here, not before if statement
                        faces.append((i, i + 1, i + 2))
                    else:
                        i += s
                        faces.append((i + 1, i, i + 2))
                s += strip * 2  # + 2

        def _2():
            for i in range(len(self.vertex_list) - 2):
                if i % 2 == 0:
                    faces.append((i, i + 1, i + 2))
                else:
                    faces.append((i + 1, i, i + 2))

        def _3():  # its strips. this is tri to irradicate any doubts that its triangles lmao
            for i in range(len(self.vertex_list) // 3):
                i *= 3
                faces.append((i, i + 1, i + 2))

        # _1()
        return faces

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(4, 1)
        node_count = read_int(f)
        f.seek(start + 16)
        offset = []
        s_block_count = []
        for _ in range(node_count):
            self.root_node.append(read_float_tuple(f, 3))
            f.seek(8, 1)
            offset.append(read_int(f))
            f.seek(12, 1)
            s_block_count.append(read_byte(f))
            f.seek(8 + 3, 1)
        for i in range(len(offset)):
            f.seek(start + offset[i])
            for _ in range(s_block_count[i]):
                _, a = read_multi_shorts(f, 2)
                self.face_strip_len.append(a)

        f.seek(start + offset[-1])
        read_aligned(f, 16)  # using the last one allows us to skip the section

        for _ in range((self.next_block - f.tell()) // 16):
            self.vertex_list.append(read_float_tuple(f, 3))
            f.seek(4, 1)

    def make_blender(self):
        def blender_mesh(m_name, verts, faces):
            mesh = bpy.data.meshes.new(m_name)
            mesh.from_pydata(verts, [], faces)
            # mesh.validate()
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708
            col.objects.link(obj)

        col = bpy.context.collection
        bpy.ops.object.mode_set(mode="OBJECT")
        blender_mesh("Collision_Roots", self.root_node, [])
        blender_mesh("Collision", self.vertex_list, self.make_faces())
