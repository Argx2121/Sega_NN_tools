import bpy
from bpy.types import Object, Mesh
from dataclasses import dataclass

from ..model_assets import model_util


def make_mesh(self):
    bone_groups = self.bone_groups
    model_name = self.model_name
    model_name_strip = self.model_name_strip
    build_mesh1 = self.model.build_mesh
    mesh_info = self.model.mesh_info
    vertex_data = self.model.vertices
    face_list1 = self.model.faces
    mesh_names = self.mesh_names
    material_list_blender = self.material_list_blender
    bone_names = self.bone_names
    armature = self.armature
    b_group = bone_groups
    collection = bpy.context.collection

    def build_mesh():
        def make_uvs():
            uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV1_Map")
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                uv_tex.data[v_index].uv = uv_short_hand[face_index[0]]
                uv_tex.data[v_index + 1].uv = uv_short_hand[face_index[1]]
                uv_tex.data[v_index + 2].uv = uv_short_hand[face_index[2]]

        def make_uvs_faces(uv_tex, uv_data, face_data):
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_data[vert_index]

                uv_tex.data[v_index].uv = uv_data[face_index[0]]
                uv_tex.data[v_index + 1].uv = uv_data[face_index[1]]
                uv_tex.data[v_index + 2].uv = uv_data[face_index[2]]

        def make_wxs():
            wx_tex = mesh.uv_layers.new(name=model_name_strip + "_UV2_Map")
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                wx_tex.data[v_index].uv = wx_short_hand[face_index[0]]
                wx_tex.data[v_index + 1].uv = wx_short_hand[face_index[1]]
                wx_tex.data[v_index + 2].uv = wx_short_hand[face_index[2]]

        def make_colours(is_col2):
            if is_col2:
                col_layer = mesh.vertex_colors.new(name=model_name_strip + "_Vertex_Colours_2")
                col_data = col2_short_hand
            else:
                col_layer = mesh.vertex_colors[model_name_strip + "_Vertex_Colours"]
                col_data = col1_short_hand

            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                col_layer.data[v_index].color = col_data[face_index[0]]
                col_layer.data[v_index + 1].color = col_data[face_index[1]]
                col_layer.data[v_index + 2].color = col_data[face_index[2]]

        def make_colours_faces():
            col_layer = mesh.vertex_colors[model_name_strip + "_Vertex_Colours"]
            col_data = col1_short_hand
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_col[vert_index]

                col_layer.data[v_index].color = col_data[face_index[0]]
                col_layer.data[v_index + 1].color = col_data[face_index[1]]
                col_layer.data[v_index + 2].color = col_data[face_index[2]]

        def make_normals():
            mesh.normals_split_custom_set_from_vertices(norm_short_hand)

        def make_normals_face():
            norm_new = []
            for f_i in face_norm:
                norm_new.append(norm_short_hand[f_i[0]])
                norm_new.append(norm_short_hand[f_i[1]])
                norm_new.append(norm_short_hand[f_i[2]])
            mesh.normals_split_custom_set(norm_new)

        def make_weights_complex():
            weights_main = v_data.weights
            # make vertex groups for the bones used by the mesh
            [obj.vertex_groups.new(name=bone_names[b_group.index(bone)]) for bone in m_info.bone_list_complex]

            # meshes store a list of bone indices, and vertices choose from those bones which bones to use
            # models bones =    [0, 1, 2, 3, 4, 5]
            # meshes bone indices =   [2, 3, 4, 5]
            # vertices bone indices = [0, 1]
            # verts 0 = meshes 2 = models 2

            if v_data.bone_list_indices:  # bone indices are stored in the vertex block
                for vertex_index in range(vertex_count):  # for each vert
                    w_ind = weights_main[vertex_index]
                    for var in range(len(w_ind)):  # for all the bones
                        b_complex_index = v_data.bone_list_indices[vertex_index][var]
                        weight = w_ind[var]
                        obj.vertex_groups[b_complex_index].add([vertex_index], weight, "ADD")
            else:
                for vertex_index in range(vertex_count):  # for each vert
                    b_count = m_info.bone_count_complex
                    for b_complex_index in range(b_count):  # for all the bones
                        weight = weights_main[vertex_index][b_complex_index]
                        obj.vertex_groups[b_complex_index].add([vertex_index], weight, "REPLACE")
                        # mesh, vertex, weight

        def make_weights_complex_gno():
            weights_main = v_data.weights
            # make vertex groups for the bones used by the mesh
            [obj.vertex_groups.new(name=bone_names[b_group.index(bone)]) for bone in b_group if bone != 65535]

            # vertices choose from the models bones
            # models bones =    [0, 1, 2, 3, 4, 5]
            # vertices bone indices = [2, 3]
            # verts 2 = models 2

            if v_data.bone_list_indices:  # bone indices are stored in the vertex block
                for vertex_index in range(vertex_count):  # for each vert
                    w_ind = weights_main[vertex_index]
                    for var in range(len(w_ind)):  # for all the bones
                        b_complex_index = v_data.bone_list_indices[vertex_index][var]
                        weight = w_ind[var]
                        obj.vertex_groups[b_complex_index].add([vertex_index], weight, "ADD")

        def make_weights_simple():
            obj.vertex_groups.new(name=bone_names[b_group.index(sm.bone)])
            obj.vertex_groups[0].add(list(range(vertex_count)), 1, "REPLACE")

        mesh = bpy.data.meshes.new(mesh_names[i])
        obj = bpy.data.objects.new(mesh.name, mesh)
        collection.objects.link(obj)

        mesh.from_pydata(pos_short_hand, [], face_list)

        if not sm.material < len(material_list_blender):
            obj.data.materials.append(material_list_blender[0])
        else:
            obj.data.materials.append(material_list_blender[sm.material])
        obj.modifiers.new(name=model_name, type='ARMATURE').object = obj.parent = armature
        obj.matrix_parent_inverse = armature.matrix_world.inverted()
        obj.matrix_world = armature.matrix_world

        # this is called in materials by the v col node. The node needs a data layer, or it will break materials
        # don't get rid of this
        mesh.vertex_colors.new(name=model_name_strip + "_Vertex_Colours")

        if is_gno:
            if uv_short_hand:
                uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV1_Map")
                make_uvs_faces(uv_tex, uv_short_hand, face_uvs)
            if uv2_short_hand:
                uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV2_Map")
                make_uvs_faces(uv_tex, uv2_short_hand, face_uvs2)
            elif face_uvs2:
                uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV2_Map")
                make_uvs_faces(uv_tex, uv_short_hand, face_uvs2)
            if uv3_short_hand:
                uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV3_Map")
                make_uvs_faces(uv_tex, uv3_short_hand, face_uvs3)
            elif face_uvs3:
                uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV3_Map")
                make_uvs_faces(uv_tex, uv_short_hand, face_uvs3)
        else:
            if uv_short_hand:
                make_uvs()
                if wx_short_hand:
                    make_wxs()

        if is_gno:
            if self.model.col[sm.face]:
                make_colours_faces()
            if self.model.norm[sm.face]:
                make_normals_face()
            if v_data.weights:
                make_weights_complex_gno()
            else:
                make_weights_simple()
        else:
            if col1_short_hand:
                make_colours(False)
                if col2_short_hand:
                    make_colours(True)
            if norm_short_hand:
                make_normals()
            if m_info.bone_count_complex:
                make_weights_complex()
            else:
                make_weights_simple()

        if self.settings.clean_mesh:
            if self.format in {"KOnAfterSchoolLive_U", "SegaSuperstars_S"}:  # problematic games
                model_util.clean_mesh_strict(obj)
            else:
                model_util.clean_mesh(obj)

    def face_clean_gno(face_clean, face_high):
        for ind in face_broke:
            del face_clean[ind]
        high2 = max([item for sub in face_clean for item in sub]) + 1
        face_high = max((high2, face_high))
        return face_clean, face_high

    for i in range(len(build_mesh1)):  # for each mesh
        sm = build_mesh1[i]
        sm_mesh_index = sm.vertex
        m_info = mesh_info[sm_mesh_index]
        v_data = vertex_data[sm_mesh_index]
        face_list = face_list1[sm.face]
        vertex_count = len(v_data.positions)

        is_gno = False
        face_broke = []
        if model_name[-3].lower() == "g":
            is_gno = True

        if is_gno:
            for index, f in enumerate(face_list):
                if not f.count(f[0]) == 1 or not f.count(f[1]) == 1:
                    face_broke.append(index)
            face_broke = face_broke[::-1]

            if not face_list or len(face_broke) == len(face_list):
                continue
        else:
            face_list = [f for f in face_list if f.count(f[0]) == 1 and f.count(f[1]) == 1]

            if not face_list or len(face_broke) == len(face_list):
                continue

        lowest = 0
        highest = max([item for sub in face_list for item in sub]) + 1

        if is_gno:
            face_list, highest = face_clean_gno(face_list, highest)

            if self.model.norm[sm.face]:
                face_norm, highest = face_clean_gno(self.model.norm[sm.face], highest)

            if self.model.col[sm.face]:
                face_col, highest = face_clean_gno(self.model.col[sm.face], highest)

            face_uvs, face_uvs2, face_uvs3 = [], [], []
            if self.model.uvs[sm.face]:
                if self.model.uvs[sm.face][0]:
                    face_uvs, highest = face_clean_gno(self.model.uvs[sm.face][0], highest)
                if self.model.uvs[sm.face][1]:
                    face_uvs2, highest = face_clean_gno(self.model.uvs[sm.face][1], highest)
                if self.model.uvs[sm.face][2]:
                    face_uvs3, highest = face_clean_gno(self.model.uvs[sm.face][2], highest)
            uv_short_hand = []
            uv2_short_hand = []
            uv3_short_hand = []
            if len(v_data.uvs) > 0:
                uv_short_hand = v_data.uvs[0][lowest: highest]
            if len(v_data.uvs) > 1:
                uv2_short_hand = v_data.uvs[1][lowest: highest]
            if len(v_data.uvs) > 2:
                uv3_short_hand = v_data.uvs[2][lowest: highest]
        else:
            uv_short_hand = v_data.uvs[lowest: highest]
            wx_short_hand = v_data.wxs[lowest: highest]

        v_loop_count = len(face_list)
        col1_short_hand = v_data.colours[0][lowest: highest]
        col2_short_hand = v_data.colours[1][lowest: highest]
        norm_short_hand = v_data.normals[lowest: highest]
        pos_short_hand = v_data.positions[lowest: highest]

        build_mesh()


@dataclass
class MeshData:
    bpy_obj: Object
    radius: float
    center: tuple
    bone_names: list
    material_name: str
    opaque: bool
    vert: int
    face: int


def get_meshes(obj_mesh_list):
    import math
    mesh_list = []
    for child in obj_mesh_list:
        child: Object
        # noinspection PyTypeChecker
        mesh: Mesh = child.data
        material_name = child.active_material.name
        bone_names = [a.name for a in child.vertex_groups]

        co_ords = [0, 0, 0] * len(mesh.vertices)
        mesh.vertices.foreach_get("co", co_ords)
        co_x = [co_ords[i] for i in range(0, len(co_ords), 3)]
        co_y = [co_ords[i+1] for i in range(0, len(co_ords), 3)]
        co_z = [co_ords[i+2] for i in range(0, len(co_ords), 3)]

        max_x, min_x = max(co_x), min(co_x)
        max_y, min_y = max(co_y), min(co_y)
        max_z, min_z = max(co_z), min(co_z)

        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2
        center_z = (max_z + min_z) / 2

        center = center_x, center_y, center_z

        pos = [tuple(co_ords[i:i + 3]) for i in range(0, len(co_ords), 3)]

        radius_list = [math.sqrt(((a[0] - center_x) ** 2 + (a[1] - center_y) ** 2 + (a[2] - center_z) ** 2)) for a in pos]
        radius = max(radius_list)

        mesh_list.append(MeshData(child, radius, center, bone_names, material_name, True, 0, 0))

    return mesh_list


@dataclass
class VertexDataGno:
    positions: list
    positions_type: int
    normals: list
    normals_type: int
    colours: list
    colours_type: int
    uvs: list
    uvs_type: int
    weights: list


@dataclass
class VertexData:
    positions: list
    normals: list
    colours: list
    uvs: list
    wxs: list
    weights: list


@dataclass
class FaceDataGno:
    faces: list
    positions_type: int
    normals_type: int
    colours_type: int
    uvs_type: int
    has_wx: bool
    weights_type: int


@dataclass
class FaceData:
    faces: list
    normals: bool
    colours: bool
    uvs: bool
    wx: bool
    weights: bool


@dataclass
class Geometry:
    vertices: list
    faces: list


class GenerateMeshesGno:
    def __init__(self, split, pos_type, norm_type, uv_type):
        self.split = split
        self.pos_type = pos_type
        self.norm_type = norm_type
        self.uv_type = uv_type
        self.face_ind = 0
        self.vert_ind = 0
        self.geometry_list = []

    def _convert_data_types_simple(self, data_types):
        pos, norms, cols, uvs = data_types
        pos_type = self.pos_type
        norm_type = self.norm_type
        uv_type = self.uv_type
        # there is only bytes for col

        p_type = 0
        n_type = 0
        c_type = 0
        u_type = 0

        if pos_type == "float":
            p_type = 1
        elif pos_type == "short":
            pos_max = max([abs(a) for b in pos for a in b])

            if pos_max <= 7.999755859375:
                p_type = 8
                pos = [(round(a[0] * 4096), round(a[1] * 4096), round(a[2] * 4096)) for a in pos]
            elif pos_max <= 31.9990234375:
                p_type = 7
                pos = [(round(a[0] * 1024), round(a[1] * 1024), round(a[2] * 1024)) for a in pos]
            elif pos_max <= 127.99609375:
                p_type = 6
                pos = [(round(a[0] * 256), round(a[1] * 256), round(a[2] * 256)) for a in pos]
            elif pos_max <= 511.984375:
                p_type = 5
                pos = [(round(a[0] * 64), round(a[1] * 64), round(a[2] * 64)) for a in pos]
            elif pos_max <= 2047.9375:
                p_type = 4
                pos = [(round(a[0] * 16), round(a[1] * 16), round(a[2] * 16)) for a in pos]
            elif pos_max <= 8191.75:
                p_type = 3
                pos = [(round(a[0] * 4), round(a[1] * 4), round(a[2] * 4)) for a in pos]
            else:  # pos_max <= 32767:
                p_type = 2
                pos = [(round(a[0] * 1), round(a[1] * 1), round(a[2] * 1)) for a in pos]

        pos = list(set(pos))

        if norms:
            if norm_type == "float":
                n_type = 1
            elif norm_type == "short":
                n_type = 2
                norms = [(round(a[0] * 16384), round(a[1] * 16384), round(a[2] * 16384)) for a in norms]
            elif norm_type == "byte":
                n_type = 3
                norms = [(round(a[0] * 64), round(a[1] * 64), round(a[2] * 64)) for a in norms]
            norms = list(set(norms))

        if cols:
            c_type = 1
            cols = [(round(a[0] * 255), round(a[1] * 255), round(a[2] * 255), round(a[3] * 255)) for a in cols]
            cols = list(set(cols))

        if uvs:
            if uv_type == "float":
                u_type = 1
            elif uv_type == "short":
                if max([abs(a) for b in uvs for a in b]) > 31.9:
                    u_type = 2
                    uvs = [(round(a[0] * 256), round(a[1] * 256)) for a in uvs]
                else:
                    u_type = 3
                    uvs = [(round(a[0] * 1024), round(a[1] * 1024)) for a in uvs]
            uvs = list(set(uvs))
        return pos, norms, cols, uvs, p_type, n_type, c_type, u_type

    def _convert_data_types_complex(self, data_types):
        pos, norms, cols, uvs = data_types
        pos_type = self.pos_type
        norm_type = self.norm_type
        uv_type = self.uv_type
        # there is only bytes for col

        p_type = 0
        n_type = 0
        c_type = 0
        u_type = 0

        if pos_type == "float":
            p_type = 1
        elif pos_type == "short":
            pos_max = max([abs(a) for b in pos for a in b])

            if pos_max <= 7.999755859375:
                p_type = 8
                pos = [(round(a[0] * 4096), round(a[1] * 4096), round(a[2] * 4096)) for a in pos]
            elif pos_max <= 31.9990234375:
                p_type = 7
                pos = [(round(a[0] * 1024), round(a[1] * 1024), round(a[2] * 1024)) for a in pos]
            elif pos_max <= 127.99609375:
                p_type = 6
                pos = [(round(a[0] * 256), round(a[1] * 256), round(a[2] * 256)) for a in pos]
            elif pos_max <= 511.984375:
                p_type = 5
                pos = [(round(a[0] * 64), round(a[1] * 64), round(a[2] * 64)) for a in pos]
            elif pos_max <= 2047.9375:
                p_type = 4
                pos = [(round(a[0] * 16), round(a[1] * 16), round(a[2] * 16)) for a in pos]
            elif pos_max <= 8191.75:
                p_type = 3
                pos = [(round(a[0] * 4), round(a[1] * 4), round(a[2] * 4)) for a in pos]
            else:  # pos_max <= 32767:
                p_type = 2
                pos = [(round(a[0] * 1), round(a[1] * 1), round(a[2] * 1)) for a in pos]

        if norms:
            if norm_type == "float":
                n_type = 1
            elif norm_type == "short":
                n_type = 2
                norms = [(round(a[0] * 16384), round(a[1] * 16384), round(a[2] * 16384)) for a in norms]
            elif norm_type == "byte":
                n_type = 3
                norms = [(round(a[0] * 64), round(a[1] * 64), round(a[2] * 64)) for a in norms]

        if cols:
            c_type = 1
            cols = [(round(a[0] * 255), round(a[1] * 255), round(a[2] * 255), round(a[3] * 255)) for a in cols]

        if uvs:
            if uv_type == "float":
                u_type = 1
            elif uv_type == "short":
                if max([abs(a) for b in uvs for a in b]) > 31.9:
                    u_type = 2
                    uvs = [(round(a[0] * 256), round(a[1] * 256)) for a in uvs]
                else:
                    u_type = 3
                    uvs = [(round(a[0] * 1024), round(a[1] * 1024)) for a in uvs]
        return pos, norms, cols, uvs, p_type, n_type, c_type, u_type

    def simple_faces(self, mesh_list):
        split = self.split
        vert_prev = 0
        # vert_list is redefined everytime we make a new mesh set (relative)
        # and the value used for vert_ind is only added to (absolute)
        # vert_prev is used to make the absolute value relative

        for a in self.geometry_list:
            if a:
                vert_prev += len(a.vertices)

        face_list = []
        vert_list = []

        pos = []
        norms = []
        cols = []
        uvs = []
        weights = []

        # build lists of all possible vert data
        for objm in mesh_list:
            obj = objm.bpy_obj
            mesh: Mesh = obj.data
            # i think they added support for a few things which is nice

            co_ords = [0, 0, 0] * len(mesh.vertices)
            mesh.vertices.foreach_get("co", co_ords)

            normals = [0, 0, 0] * len(mesh.loops)
            mesh.loops.foreach_get("normal", normals)

            uv = []
            col = []

            if mesh.uv_layers:
                uv = [0, 0] * len(mesh.uv_layers[0].data)
                mesh.uv_layers[0].data.foreach_get("uv", uv)
                if len(mesh.uv_layers) > 1:
                    wx = [0, 0] * len(mesh.uv_layers[1].data)
                    mesh.uv_layers[1].data.foreach_get("uv", wx)
                    uv += wx

            if mesh.vertex_colors:
                col = [0, 0, 0, 0] * len(mesh.vertex_colors[0].data)
                mesh.vertex_colors[0].data.foreach_get("color", col)
                if list(set(col)) == [1.0]:
                    col = []

            if (bool(pos) and bool(uv) != bool(uvs)) or \
                    (bool(pos) and bool(col) != bool(cols)) or \
                    (bool(pos) and bool(norms) != bool(normals)) or \
                    max(len(pos), len(normals), len(cols), len(uvs)) > split:
                # if the current mesh doesn't have uvs / colours but the previous meshes do and the inverse scenario
                # if we've reached the split limit
                self.vert_ind += 1

                pos, norms, cols, uvs, p_type, n_type, c_type, u_type = self._convert_data_types_simple(
                    (pos, norms, cols, uvs))

                vert_list.append(VertexDataGno(pos, p_type, norms, n_type, cols, c_type, uvs, u_type, weights))
                pos = []
                norms = []
                uvs = []
                weights = []
                cols = []
            objm.vert = self.vert_ind
            norms += [tuple(normals[i:i + 3]) for i in range(0, len(normals), 3)]
            pos += [tuple(co_ords[i:i + 3]) for i in range(0, len(co_ords), 3)]
            if uv:
                uvs += [tuple((uv[i], -(uv[i + 1] - 1))) for i in range(0, len(uv), 2)]
            if col:
                cols += [tuple(col[i:i + 4]) for i in range(0, len(col), 4)]

        pos, norms, cols, uvs, p_type, n_type, c_type, u_type = \
            self._convert_data_types_simple((pos, norms, cols, uvs))
        vert_list.append(VertexDataGno(pos, p_type, norms, n_type, cols, c_type, uvs, u_type, weights))

        # build face indices
        for objm in mesh_list:
            obj = objm.bpy_obj
            mesh: Mesh = obj.data
            pos_index = []
            normal_index = []
            colour_index = []
            uv_index = []
            wx_index = []

            vertdata = vert_list[objm.vert - vert_prev]
            pos = vertdata.positions
            norms = vertdata.normals
            cols = vertdata.colours
            uvs = vertdata.uvs

            # get pos indices in the big list
            # game cube builds faces in the opposite order
            co_ords_ind = [0, 0, 0] * len(mesh.polygons)
            mesh.polygons.foreach_get("vertices", co_ords_ind)
            co_ords_ind = [
                ind for tri in zip(co_ords_ind[2::3], co_ords_ind[1::3], co_ords_ind[0::3]) for ind in tri]
            if vertdata.positions_type == 1:
                pos_index = [pos.index(mesh.vertices[a].co[::]) for a in co_ords_ind]
            else:
                mult_by = (0, 0, 1, 4, 16, 64, 256, 1024, 4096)[vertdata.positions_type]
                # e.g. pos type 5: mult_by = 64
                # type 0 and 1 are padding (they will never be called)
                pos_index = [pos.index((
                    round(mesh.vertices[a].co[::][0] * mult_by),
                    round(mesh.vertices[a].co[::][1] * mult_by),
                    round(mesh.vertices[a].co[::][2] * mult_by)
                )) for a in co_ords_ind]

            # get normal indices in the big list
            norms_pre = []
            if vertdata.normals_type == 1:
                for l in mesh.loops:
                    var = l.normal[::]
                    norms_pre.append(norms.index(var))
            elif vertdata.normals_type == 2:
                for l in mesh.loops:
                    v = l.normal[::]
                    var = (round(v[0] * 16384), round(v[1] * 16384), round(v[2] * 16384))
                    norms_pre.append(norms.index(var))
            elif vertdata.normals_type == 3:
                for l in mesh.loops:
                    v = l.normal[::]
                    var = (round(v[0] * 64), round(v[1] * 64), round(v[2] * 64))
                    norms_pre.append(norms.index(var))

            # adjust normal list order
            for a, b, c in zip(norms_pre[0::3], norms_pre[1::3], norms_pre[2::3]):
                normal_index.append(c)
                normal_index.append(b)
                normal_index.append(a)

            # get colour indices in the big list
            cols_pre = []
            if vertdata.colours_type == 1:
                l_data = mesh.vertex_colors[0].data
                for l in l_data:
                    v = l.color[::]
                    var = (round(v[0] * 255), round(v[1] * 255), round(v[2] * 255), round(v[3] * 255))
                    cols_pre.append(cols.index(var))

            # adjust colour list order
            for a, b, c in zip(cols_pre[0::3], cols_pre[1::3], cols_pre[2::3]):
                colour_index.append(c)
                colour_index.append(b)
                colour_index.append(a)

            # get uvs indices in the big list
            uvs_pre = []
            if vertdata.uvs_type == 1:
                l_data = mesh.uv_layers[0].data
                for l in l_data:
                    v = l.uv[::]
                    var = (v[0], -(v[1] - 1))
                    uvs_pre.append(uvs.index(var))
            elif vertdata.uvs_type == 2:
                l_data = mesh.uv_layers[0].data
                for l in l_data:
                    v = l.uv[::]
                    var = (round(v[0] * 256), round(-(v[1] - 1) * 256))
                    uvs_pre.append(uvs.index(var))
            elif vertdata.uvs_type == 3:
                l_data = mesh.uv_layers[0].data
                for l in l_data:
                    v = l.uv[::]
                    var = (round(v[0] * 1024), round(-(v[1] - 1) * 1024))
                    uvs_pre.append(uvs.index(var))
            # adjust uv list order
            for a, b, c in zip(uvs_pre[0::3], uvs_pre[1::3], uvs_pre[2::3]):
                uv_index.append(c)
                uv_index.append(b)
                uv_index.append(a)

            # get wxs indices in the big list
            has_wx = False
            wxs_pre = []
            if mesh.uv_layers and len(mesh.uv_layers) > 1:
                has_wx = True
                if vertdata.uvs_type == 1:
                    l_data = mesh.uv_layers[1].data
                    for l in l_data:
                        v = l.uv[::]
                        var = (v[0], -(v[1] - 1))
                        wxs_pre.append(uvs.index(var))
                elif vertdata.uvs_type == 2:
                    l_data = mesh.uv_layers[1].data
                    for l in l_data:
                        v = l.uv[::]
                        var = (round(v[0] * 256), round(-(v[1] - 1) * 256))
                        wxs_pre.append(uvs.index(var))
                elif vertdata.uvs_type == 3:
                    l_data = mesh.uv_layers[1].data
                    for l in l_data:
                        v = l.uv[::]
                        var = (round(v[0] * 1024), round(-(v[1] - 1) * 1024))
                        wxs_pre.append(uvs.index(var))
                # adjust wx list order
                for a, b, c in zip(wxs_pre[0::3], wxs_pre[1::3], wxs_pre[2::3]):
                    wx_index.append(c)
                    wx_index.append(b)
                    wx_index.append(a)

            faces = model_util.TriStripper((pos, pos_index, normal_index, colour_index, uv_index, wx_index)).mesh()
            objm.face = self.face_ind
            self.face_ind += 1
            face_list.append(FaceDataGno(faces, vertdata.positions_type, vertdata.normals_type, vertdata.colours_type,
                                         vertdata.uvs_type, has_wx, 0))
        self.geometry_list.append(Geometry(vert_list, face_list))
        self.vert_ind += 1
        # done to indicate we are going to make a new vert set for the next group
        # faces aren't made of grouped vertices, so we use a simpler counter and don't do this

    def complex_faces(self, mesh_list):
        face_list = []
        vert_list = []
        face_ind = self.face_ind
        vert_ind = self.vert_ind

        for objm in mesh_list:  # build list of all possible vert data
            obj = objm.bpy_obj
            mesh: Mesh = obj.data
            bone_names = [a.name for a in obj.vertex_groups]

            pos = []
            norms = []
            cols = []
            uvs = []
            wxs = []
            weights = []

            # these are all tri count * 3
            pos_start = []
            weight_start = []
            norm_start = []

            values_winding = []
            values = []
            values_indices = []

            for face in mesh.polygons:  # starting with wrong face winding
                vert = mesh.vertices[face.vertices[0]]
                pos_start.append(vert.co[::])
                weight_start.append(
                    [(bone_names[group.group], group.weight) for group in vert.groups[::] if group.weight > 0])

                vert = mesh.vertices[face.vertices[1]]
                pos_start.append(vert.co[::])
                weight_start.append(
                    [(bone_names[group.group], group.weight) for group in vert.groups[::] if group.weight > 0])

                vert = mesh.vertices[face.vertices[2]]
                pos_start.append(vert.co[::])
                weight_start.append(
                    [(bone_names[group.group], group.weight) for group in vert.groups[::] if group.weight > 0])

            for l in mesh.loops:
                var = l.normal[::]
                norm_start.append(var)

            if norm_start:
                for p1, p2, p3, w1, w2, w3, n1, n2, n3 in zip(
                        pos_start[0::3], pos_start[1::3], pos_start[2::3],
                        weight_start[0::3], weight_start[1::3], weight_start[2::3],
                        norm_start[0::3], norm_start[1::3], norm_start[2::3]):
                    values_winding.append((p3, w3, n3))
                    values_winding.append((p2, w2, n2))
                    values_winding.append((p1, w1, n1))
            else:
                for p1, p2, p3, w1, w2, w3 in zip(
                        pos_start[0::3], pos_start[1::3], pos_start[2::3],
                        weight_start[0::3], weight_start[1::3], weight_start[2::3]):
                    values_winding.append((p3, w3))
                    values_winding.append((p2, w2))
                    values_winding.append((p1, w1))

            del pos_start, weight_start, norm_start

            # at this point we have the lists to synchronise stored as their values (not indices)
            # with the correct winding

            for a in values_winding:
                if a not in values:
                    values_indices.append(len(values))  # build indices
                    values.append(a)  # build list of possible values
                else:
                    values_indices.append(values.index(a))  # build indices

            del values_winding

            # now we have a list of all different (pos, wei, norm) and a list of its indices

            pos_index = values_indices
            normal_index = []
            colour_index = []
            uv_index = []
            wx_index = []

            pos = [a[0] for a in values]
            weights = [a[1] for a in values]

            if len(values[0]) == 3:
                normal_index = values_indices
                norms = [a[2] for a in values]

            # we have prepared pos-wei-norm so move on to colours and uvs

            if mesh.vertex_colors:
                cols_pre = [0, 0, 0, 0] * len(mesh.vertex_colors[0].data)
                mesh.vertex_colors[0].data.foreach_get("color", cols_pre)
                if set(cols_pre) != {1}:
                    cols_pre = tuple(zip(cols_pre[0::4], cols_pre[1::4], cols_pre[2::4], cols_pre[3::4]))
                    cols_pre = [ind for tri in zip(cols_pre[2::3], cols_pre[1::3], cols_pre[0::3]) for ind in tri]
                    col_dict = dict([(a, []) for a in cols_pre])
                    for ind, col_value in enumerate(cols_pre):
                        col_dict[col_value].append(ind)
                    cols = [*col_dict]
                    colour_index = [0] * len(cols_pre)
                    for ind, col_ind in enumerate([*col_dict.values()]):
                        for a in col_ind:
                            colour_index[a] = ind

            has_wx = False
            if mesh.uv_layers:
                # pull uv data
                uvs_pre = [0, 0] * len(mesh.uv_layers[0].data)
                mesh.uv_layers[0].data.foreach_get("uv", uvs_pre)
                # unflatten list
                uvs_pre = tuple(zip(uvs_pre[0::2], uvs_pre[1::2]))
                # reverse winding
                uvs_pre = [ind for tri in zip(uvs_pre[2::3], uvs_pre[1::3], uvs_pre[0::3]) for ind in tri]
                # initialise uv - indices map with empty lists
                uv_dict = dict([(a, []) for a in uvs_pre])
                # add indices to uv - indices map
                for ind, uv_value in enumerate(uvs_pre):
                    uv_dict[uv_value].append(ind)
                # get uvs and flip y axis
                uvs = [(a[0], -(a[1] - 1)) for a in [*uv_dict]]  # get all keys
                # make empty uv_index list
                uv_index = [0] * len(uvs_pre)
                # fill uv_index list with uv indices
                for ind, uv_ind in enumerate([*uv_dict.values()]):  # get all items
                    for a in uv_ind:
                        uv_index[a] = ind
                if len(mesh.uv_layers) > 1:
                    has_wx = True
                    # pull wx data
                    wxs_pre = [0, 0] * len(mesh.uv_layers[1].data)
                    mesh.uv_layers[1].data.foreach_get("uv", wxs_pre)
                    # unflatten list
                    wxs_pre = tuple(zip(wxs_pre[0::2], wxs_pre[1::2]))
                    # reverse winding
                    wxs_pre = [ind for tri in zip(wxs_pre[2::3], wxs_pre[1::3], wxs_pre[0::3]) for ind in tri]
                    # initialise wx - indices map with empty lists
                    wx_dict = dict([(a, []) for a in wxs_pre])
                    # add indices to wx - indices map
                    for ind, wx_value in enumerate(wxs_pre):
                        wx_dict[wx_value].append(ind)
                    # get wx and flip y axis
                    wxs = [(a[0], -(a[1] - 1)) for a in [*wx_dict]]  # get all keys
                    len_uvs = len(uvs)
                    uvs += wxs
                    # make empty wx_index list
                    wx_index = [0] * len(wxs_pre)
                    # fill wx_index list with wx indices
                    for ind, wx_ind in enumerate([*wx_dict.values()]):  # get all items
                        for a in wx_ind:
                            wx_index[a] = ind + len_uvs

            # now we make the faces

            faces = model_util.TriStripper((pos, pos_index, normal_index, colour_index, uv_index, wx_index)).mesh()

            objm.face = face_ind
            objm.vert = vert_ind
            face_ind += 1
            vert_ind += 1
            pos, norms, cols, uvs, p_type, n_type, c_type, u_type = self._convert_data_types_complex(
                (pos, norms, cols, uvs))
            # todo everything needs to checked and cleaned

            vert_list.append(VertexDataGno(pos, p_type, norms, n_type, cols, c_type, uvs, u_type, weights))
            face_list.append(FaceDataGno(faces, p_type, n_type, c_type, u_type, has_wx, 1))
        self.geometry_list.append(Geometry(vert_list, face_list))

        self.face_ind = face_ind
        self.vert_ind = vert_ind


class GenerateMeshes:
    def __init__(self, split):
        self.split = split
        self.face_ind = 0
        self.vert_ind = 0
        self.geometry_list = []

    def meshes(self, mesh_list):
        split = self.split
        vert_prev = 0
        # vert_list is redefined everytime we make a new mesh set (relative)
        # and the value used for vert_ind is only added to (absolute)
        # vert_prev is used to make the absolute value relative

        for a in self.geometry_list:
            if a:
                vert_prev += len(a.vertices)

        face_list = []
        vert_list = []

        pos = []
        norms = []
        cols = []
        uvs = []
        wxs = []
        weights = []

        has_norms = False
        has_cols = False
        has_uvs = False
        has_wxs = False
        has_weights = False

        # build lists of all possible vert data
        for objm in mesh_list:
            obj = objm.bpy_obj
            bone_names = [a.name for a in obj.vertex_groups]
            mesh: Mesh = obj.data

            co_ords = []
            for face in mesh.polygons:
                for vert in face.vertices:
                    vert = mesh.vertices[vert]
                    co_ords.append(tuple(vert.co[::]))

            normals = [0, 0, 0] * len(mesh.loops)
            mesh.loops.foreach_get("normal", normals)

            uv = []
            col = []
            wx = []
            wei = []

            if len(bone_names) > 1:
                for face in mesh.polygons:
                    for vert in face.vertices:
                        vert = mesh.vertices[vert]
                        wei.append(tuple([(group.group, group.weight) for group in vert.groups[::]]))

            if mesh.uv_layers:
                uv = [0, 0] * len(mesh.uv_layers[0].data)
                mesh.uv_layers[0].data.foreach_get("uv", uv)
                if len(mesh.uv_layers) > 1:
                    wx = [0, 0] * len(mesh.uv_layers[1].data)
                    mesh.uv_layers[1].data.foreach_get("uv", wx)
                    wx += wx

            if mesh.vertex_colors:
                col = [0, 0, 0, 0] * len(mesh.vertex_colors[0].data)
                mesh.vertex_colors[0].data.foreach_get("color", col)
                if list(set(col)) == [1.0]:
                    col = []

            if pos and (has_norms != bool(normals) or has_cols != bool(col) or
                        has_uvs != bool(uv) or has_wxs != bool(wx) or has_weights != bool(wei)) or \
                    len(pos) > split or has_weights:
                # if the current mesh doesn't have uvs / colours but the previous meshes do and the inverse scenario
                # if we've reached the split limit
                self.vert_ind += 1
                vert_list.append(VertexData(pos, norms, cols, uvs, wxs, weights))
                pos = []
                norms = []
                uvs = []
                weights = []
                cols = []
                has_norms = False
                has_cols = False
                has_uvs = False
                has_wxs = False
                has_weights = False

            objm.vert = self.vert_ind
            if normals:
                has_norms = True
                norms += [tuple(normals[i:i + 3]) for i in range(0, len(normals), 3)]
            pos += co_ords
            weights += wei
            if wei:
                has_weights = True
            if uv:
                has_uvs = True
                uvs += [tuple((uv[i], -(uv[i + 1] - 1))) for i in range(0, len(uv), 2)]
            if wx:
                has_wxs = True
                wxs += [tuple((wxs[i], -(wxs[i + 1] - 1))) for i in range(0, len(wxs), 2)]
            if col:
                has_cols = True
                cols += [tuple(col[i:i + 4]) for i in range(0, len(col), 4)]

        vert_list.append(VertexData(pos, norms, cols, uvs, wxs, weights))

        # prepare
        for i in range(len(vert_list)):
            vertdata = vert_list[i]
            vertex_data = []
            pos = vertdata.positions
            norms = vertdata.normals
            cols = vertdata.colours
            uvs = vertdata.uvs
            wxs = vertdata.wxs
            weights = vertdata.weights

            vertex_count = len(pos)
            empty_data = [()] * vertex_count

            if norms:
                norms = norms
            else:
                norms = empty_data
            if cols:
                cols = cols
            else:
                cols = empty_data
            if uvs:
                uvs = uvs
            else:
                uvs = empty_data
            if wxs:
                wxs = wxs
            else:
                wxs = empty_data
            if weights:
                weights = weights
            else:
                weights = empty_data

            for p, n, c, u, w, b in zip(pos, norms, cols, uvs, wxs, weights):
                vertex_data.append((p, n, c, u, w, b))

            vertex_data_unique = tuple(set(vertex_data))

            vert_list[i] = [vertex_data_unique, vertex_data, []]

        # build face indices
        vertex_off = 0
        last_mesh = -1
        for objm in mesh_list:
            obj = objm.bpy_obj
            mesh: Mesh = obj.data
            face_indices = []
            bone_names = [a.name for a in obj.vertex_groups]
            vertex_count = 3 * len(mesh.polygons)
            if last_mesh != objm.vert:  # if the last mesh and this mesh do not use the same vert group
                vertex_off = 0
            last_mesh = objm.vert

            data_index = objm.vert - vert_prev
            vertex_data_unique = vert_list[data_index][0]
            vertex_data = vert_list[data_index][1]
            vertex_data = vertex_data[vertex_off: vertex_off + vertex_count]

            for f1, f2, f3 in zip(vertex_data[::3], vertex_data[1::3], vertex_data[2::3]):
                face_indices.append(
                    (vertex_data_unique.index(f1), vertex_data_unique.index(f2), vertex_data_unique.index(f3)))

            faces = model_util.TriStripper(([], )).to_tri_strip(face_indices)
            vertex_off += vertex_count  # this means the next mesh will have the correct starting value
            objm.face = self.face_ind
            self.face_ind += 1

            vert_list[data_index][-1] = bone_names
            # consecutive ones will be simple meshes, complex arent joined so the bone names are fine

            vert_test = vertex_data_unique[0]
            has_wei = False
            if len(bone_names) > 1:
                has_wei = True

            face_list.append(FaceData(
                faces, bool(vert_test[1]), bool(vert_test[2]), bool(vert_test[3]), bool(vert_test[4]), has_wei))

        for i in range(len(vert_list)):
            vertdata = vert_list[i][0]
            vertdata = [VertexData(*a) for a in vertdata]
            vert_list[i] = [vertdata, vert_list[i][-1]]

        self.geometry_list.append(Geometry(vert_list, face_list))
        self.vert_ind += 1


def get_geometry(data):
    meshes, settings, self = data
    if self.format[-1] == "G":
        mesh_gen = GenerateMeshesGno(settings.split, settings.pos, settings.norms, settings.uvs)

        if meshes.simple_opaque:
            mesh_gen.simple_faces(meshes.simple_opaque)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.complex_opaque:
            mesh_gen.complex_faces(meshes.complex_opaque)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.simple_alpha:
            mesh_gen.simple_faces(meshes.simple_alpha)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.complex_alpha:
            mesh_gen.complex_faces(meshes.complex_alpha)
        else:
            mesh_gen.geometry_list.append([])
    else:
        mesh_gen = GenerateMeshes(settings.split)

        if meshes.simple_opaque:
            mesh_gen.meshes(meshes.simple_opaque)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.complex_opaque:
            mesh_gen.meshes(meshes.complex_opaque)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.simple_alpha:
            mesh_gen.meshes(meshes.simple_alpha)
        else:
            mesh_gen.geometry_list.append([])

        if meshes.complex_alpha:
            mesh_gen.meshes(meshes.complex_alpha)
        else:
            mesh_gen.geometry_list.append([])

    return meshes, mesh_gen.geometry_list
