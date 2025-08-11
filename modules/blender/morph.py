import bpy
import math
from mathutils import *
from bpy.types import Object


class Morph:
    def __init__(self, nn, settings):
        self.nn = nn
        self.morph = nn.morphs
        self.settings = settings
        self.keyshape_names = nn.morph_names
        if not nn.morph_names:
            self.keyshape_names = ["Key_" + str(a).zfill(4) for a in range(len(self.nn.morphs))]
        else:
            self.keyshape_names = list(self.keyshape_names.values())

    def replace_morph(self):
        arma = bpy.context.object
        meshes = []
        for mesh in arma.children:
            if mesh.type == "MESH":
                meshes.append(mesh)

        vert_list = dict()

        for mesh in meshes:
            vert_list.update({mesh.data.nn_vertex_index: set()})

        for mesh in meshes:
            vert_list[mesh.data.nn_vertex_index].add(mesh)

        used_meshes = set()
        for morph in self.morph:
            for i, m in enumerate(morph):
                if not m.positions:
                    continue
                used_meshes.add(i)

        for i in used_meshes:
            for mesh in vert_list[i]:
                if not mesh.data.shape_keys:
                    mesh.shape_key_add(name="Basis", from_mix=False)  # basis
                    for a in self.keyshape_names:
                        mesh.shape_key_add(name=a, from_mix=False)

        for e, morph in enumerate(self.morph):
            for i, m in enumerate(morph):
                if not m.positions:
                    continue
                new_pos = m.positions
                # like i could import the og model rebuild the mesh and compare it properly but this is probably fine
                # probably
                meshes = vert_list[i]
                for mesh in meshes:
                    shapekey = mesh.data.shape_keys.key_blocks[e+1]
                    if len(shapekey.points) < len(new_pos):
                        raise IndexError("Please import model with Import loose vertices")
                    for ind, vert in enumerate(new_pos):
                        # and then sega said
                        # YES we SHALL store ONLY the verts that are changed
                        # and by the way this value SHALL be the same count as if all the verts were merged by position
                        # you WILL debug for hours and you WILL enjoy it
                        shapekey.points[ind].co = Vector(vert)

    def add_morph(self):
        arma = bpy.context.object
        meshes = []
        for mesh in arma.children:
            if mesh.type == "MESH":
                meshes.append(mesh)

        vert_list = dict()

        for mesh in meshes:
            vert_list.update({mesh.data.nn_vertex_index: set()})

        for mesh in meshes:
            vert_list[mesh.data.nn_vertex_index].add(mesh)

        used_meshes = set()
        for morph in self.morph:
            for i, m in enumerate(morph):
                if not m.positions:
                    continue
                used_meshes.add(i)

        for i in used_meshes:
            for mesh in vert_list[i]:
                if not mesh.data.shape_keys:
                    mesh.shape_key_add(name="Basis", from_mix=False)  # basis
                    for a in self.keyshape_names:
                        mesh.shape_key_add(name=a, from_mix=False)

        for e, morph in enumerate(self.morph):
            for i, m in enumerate(morph):
                if not m.positions:
                    continue
                new_pos = m.positions
                meshes = vert_list[i]
                for mesh in meshes:
                    shapekey = mesh.data.shape_keys.key_blocks[e+1]
                    if len(shapekey.points) < len(new_pos):
                        raise IndexError("Please import model with Import loose vertices")
                    for ind, vert in enumerate(new_pos):
                        shapekey.points[ind].co += Vector(vert)
