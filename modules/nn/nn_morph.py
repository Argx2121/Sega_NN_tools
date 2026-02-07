from ..util import *
from dataclasses import dataclass
from mathutils import Vector
from .object_assets import vertices


@dataclass
class MorphData:
    pos: list
    norm: list
    col: list
    uv1: list
    uv2: list
    uv3: list


class Read:
    __slots__ = ["f", "post_info", "format_type", "debug", "mesh_counts"]

    def __init__(self, f: BinaryIO, post_info: int, format_type: str, debug, mesh_counts):
        self.f = f
        self.post_info = post_info
        self.format_type = format_type
        self.debug = debug
        self.mesh_counts = mesh_counts

    def le(self):
        return self.read("<")

    def be(self):
        return self.read(">")

    def read(self, endian):
        f = self.f
        post_info = self.post_info
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8

        to_info = read_int(f, endian)
        f.seek(to_info + post_info)
        morph_count, morph_info = read_int_tuple(f, 2, endian)
        f.seek(morph_info + post_info)
        morph_vs = []  # vertex indices count, offset to data
        # and when i say vertex indices i mean vertex list, face list, not actual vertices
        morph_list = []
        for _ in range(morph_count):
            morph_vs.append(read_int_tuple(f, 2, endian))
        for v_i_count, off in morph_vs:
            f.seek(post_info + off)
            v_read = vertices.Read((self.f, post_info, self.format_type, self.debug), v_i_count)
            v_read.vertex_index_counts = self.mesh_counts
            vert_func = getattr(v_read, self.format_type[-1].lower()+"no")
            verts, _ = vert_func()
            morph_list.append(verts)
        f.seek(end_of_block)
        return morph_list
