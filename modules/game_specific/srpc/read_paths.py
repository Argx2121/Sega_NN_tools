from dataclasses import dataclass

from ...util import *


class ReadPaths:
    def __init__(self, f, next_b):
        self.f = f
        self.paths = []
        self.next_block = next_b

    @dataclass
    class Paths:
        root: Tuple[float, float, float]
        position: list
        edges: list
        i: int

    def execute(self):
        console_out("Reading Paths...", self.read_data)
        console_out("Making Paths...", self.make_blender)

    def read_data(self):
        f = self.f
        start = f.tell()
        f.seek(8, 1)
        count = read_int(f)
        offsets = read_multi_ints(f, count)
        ends = list(offsets)
        ends.append(self.next_block - start)

        annoying = 0
        for offset in offsets:
            annoying += 1
            f.seek(start + offset + 4)
            off1, _ = read_multi_ints(f, 2)
            root = read_float_tuple(f, 3)
            _, count, _, _, _ = read_multi_ints(f, 5)

            positions = []
            for _ in range((start + off1 - f.tell()) // 12):
                positions.append(read_float_tuple(f, 3))

            for i in range(7):
                pos = positions[i::7]
                edges = []
                for a in range(len(pos) - 1):
                    edges.append((a, a + 1))
                self.paths.append(self.Paths(root, pos, edges, i))

            positions = []
            for _ in range((start + ends[annoying] - f.tell()) // 16):
                positions.append(read_float_tuple(f, 3))
                f.seek(4, 1)

            edges = []
            for a in range(len(positions) - 1):
                edges.append((a, a + 1))
            self.paths.append(self.Paths(root, positions, edges, -1))

    def make_blender(self):
        def blender_mesh(m_name, verts, edges, i):
            mesh = bpy.data.meshes.new(m_name)
            mesh.from_pydata(verts, edges, [])
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.rotation_euler[0] = 1.5708
            """
            if i == 1:
                obj.rotation_euler[2] = -1.5708
            elif i == 2:
                obj.rotation_euler[2] = -1.5708
                obj.rotation_euler[0] = 4.71239
            elif i == 3:
                obj.rotation_euler[0] = 3.14159
                obj.rotation_euler[1] = -1.5708
            else:
                obj.rotation_euler[0] = 1.5708
            """
            # obj.parent = par
            col.objects.link(obj)
        col = bpy.context.collection
        bpy.ops.object.mode_set(mode="OBJECT")

        for p in self.paths:
            # par = bpy.data.objects.new("Paths", None)
            # col.objects.link(par)
            # par.location = p.root[0], - p.root[2], p.root[1]
            blender_mesh("Paths", p.position, p.edges, p.i)
