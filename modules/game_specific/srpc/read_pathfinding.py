from ...util import *


class ReadXbox:
    def __init__(self, f):
        self.f = f
        self.root_node = None
        self.simple_position = []
        self.simple_edge = []
        self.complex_position = []
        self.complex_edge = []

    def execute(self):
        console_out("Reading Pathfinding...", self.read_data)
        console_out("Making Pathfinding...", self.make_blender)

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(8, 1)
        to_simple, to_complex, to_edge = read_multi_ints(f, 3)
        self.root_node = read_float_tuple(f, 3)
        complex_count = read_int(f)

        f.seek(start + to_simple)
        for i in range((to_complex - to_simple) // 16 - 1):
            self.simple_position.append(read_float_tuple(f, 3))
            self.simple_edge.append([i, i + 1])
            f.seek(4, 1)
        self.simple_position.append(read_float_tuple(f, 3))

        f.seek(start + to_complex + 28)
        for _ in range(complex_count):
            self.complex_position.append(read_float_tuple(f, 3))
            f.seek(36, 1)

        f.seek(start + to_edge)
        for _ in range(complex_count):
            self.complex_edge.append(read_multi_shorts(f, 2))

    def make_blender(self):
        def blender_mesh(m_name, verts, edges):
            mesh = bpy.data.meshes.new(m_name)
            mesh.from_pydata(verts, edges, [])
            mesh.validate()
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708
            # obj.parent = par
            col.objects.link(obj)
        col = bpy.context.collection
        bpy.ops.object.mode_set(mode="OBJECT")

        # par = bpy.data.objects.new("Pathfinding_Root", None)
        # col.objects.link(par)
        # par.location = self.root_node[0], - self.root_node[2], self.root_node[1]

        blender_mesh("Pathfinding", self.simple_position, [])
        # blender_mesh("Pathfinding2", self.complex_position, []) I HAVE NO IDEA WHAT THIS IS
        # blender_mesh("Pathfinding_Complex", self.complex_position, self.complex_edge)
