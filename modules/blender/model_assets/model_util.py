import bmesh
import pathlib
import copy
import subprocess
from dataclasses import dataclass


def make_names(self):
    model_strip = self.model_name_strip
    if not self.bone_names:
        self.bone_names = dict([
            [a, model_strip + "_Bone_" + str(a).zfill(4)] for a in list(range(self.model.info.bone_count))])
    elif len(self.bone_names) < self.model.info.bone_count:
        bone_set = set(range(self.model.info.bone_count)) - set(self.bone_names)
        for a in bone_set:
            self.bone_names[a] = model_strip + "_Bone_" + str(a).zfill(4)
    self.group_names = [model_strip + "_Bone_Group_" + str(a.group).zfill(4) for a in self.model.bones]
    self.mat_names = [model_strip + "_Material_" + str(a).zfill(4) for a in list(range(self.model.info.material_count))]
    self.mesh_names = [model_strip + "_Mesh_" + str(a).zfill(4) for a in list(range(len(self.model.build_mesh)))]


def clean_mesh(obj):  # removing illegal faces is done in mesh generation
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    verts = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()


def clean_mesh_strict(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    verts = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    faces = [f for f in bm.faces if not f.calc_area()]
    bmesh.ops.delete(bm, geom=faces, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    edges = [e for e in bm.edges if not e.link_faces]
    bmesh.ops.delete(bm, geom=edges, context="EDGES")
    bm.to_mesh(obj.data)
    bm.free()


@dataclass
class FaceTypes:
    position: int
    uv: int
    normal: int
    colour: int


class SetListPair:  # sewer made me do this
    def __init__(self):
        self.pair_list = []
        self.pair_set = set()

    def add(self, item):
        self.pair_list.append(item)
        self.pair_set.add(item)

    def exists(self, item):
        return item in self.pair_set

    def get_index(self, item):
        return self.pair_list.index(item)

    def at_index(self, item):
        return self.pair_list[item]


class TriStripper:
    def __init__(self, data):
        self.stripper_path = pathlib.Path(__file__).parent.absolute().joinpath("NvTriStrip.exe")
        self.data = data
        self.pos_list = copy.deepcopy(data[0])

    def to_tri_strip(self, v_indices):
        stripper_path = self.stripper_path
        p = subprocess.Popen([stripper_path, "-s"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True,
                             universal_newlines=True)

        input_string = ""
        for index in v_indices:
            input_string = input_string + str(index) + " \n "
        input_string = input_string + "-1 \n"

        strip = p.communicate(input=input_string)[0]
        p.terminate()
        strip = strip.split("\n")[-2].split(" ")[:-1]
        return [int(x) for x in strip]

    def mesh(self):
        pos_org, pos_index, normal_index, colour_index, uv_index, wx_index = self.data
        pos_list = self.pos_list

        no_change_set_pos = SetListPair()
        no_change_set_1 = SetListPair()
        no_change_set_2 = SetListPair()
        no_change_set_3 = SetListPair()
        no_change_set_4 = SetListPair()

        change_set_face_list = []
        change_set_index_list = []

        def edit_faces_for_loops():
            used_indices = [pos_index]

            ind_step = 1
            if normal_index:
                used_indices.append(normal_index)
                ind_step += 1
            if colour_index:
                used_indices.append(colour_index)
                ind_step += 1
            if uv_index:
                used_indices.append(uv_index)
                ind_step += 1
            if wx_index:
                used_indices.append(wx_index)
                ind_step += 1

            index_list = [[] for _ in range(len(pos_index))]

            for i, index_type in enumerate(used_indices):
                for v, var in enumerate(index_type):
                    index_list[v].append(var)

            if ind_step == 1:  # yes I am also annoyed to code it this way
                # model only has positions
                return
            elif ind_step == 2:
                for i, ft in enumerate(index_list):
                    pos = ft[0]
                    var = ft[1]
                    if not no_change_set_pos.exists(pos):  # not in list
                        no_change_set_pos.add(pos)
                        no_change_set_1.add(var)
                    else:
                        if (pos, var) in change_set_face_list:
                            change_set_index_list[change_set_face_list.index((pos, var))].append(i)
                        else:
                            change_set_face_list.append((pos, var))
                            change_set_index_list.append([i, ])

                # change_set_face_list lists all troublesome faces
                # change_set_index_list lists all the indices for them in the list
                for i, ft in enumerate(change_set_face_list):
                    pos = ft[0]
                    var = ft[1]
                    change_set_face_list[i] = (len(pos_list), var)
                    pos_list.append(pos_list[pos])

                # now we just have to update original triangles
                for a, b in zip(change_set_face_list, change_set_index_list):
                    for i in b:
                        pos_index[i] = a[0]  # keep in mind ft.position = position index (that we have modified)
                        # we do not modify anything else
            elif ind_step == 3:
                for i, ft in enumerate(index_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    if not no_change_set_pos.exists(pos):  # not in list
                        no_change_set_pos.add(pos)
                        no_change_set_1.add(var1)
                        no_change_set_2.add(var2)
                    else:  # check list if this already exists
                        base_index = no_change_set_pos.get_index(pos)
                        if no_change_set_1.at_index(base_index) == var1 and \
                                no_change_set_2.at_index(base_index) == var2:
                            pass  # pos exists in the list and matches with vars
                        else:  # pos exists in list but does not match with vars
                            if (pos, var1, var2) in change_set_face_list:
                                change_set_index_list[change_set_face_list.index((pos, var1, var2))].append(i)
                            else:
                                change_set_face_list.append((pos, var1, var2))
                                change_set_index_list.append([i, ])

                # change_set_face_list lists all troublesome faces
                # change_set_index_list lists all the indices for them in the list
                for i, ft in enumerate(change_set_face_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    change_set_face_list[i] = (len(pos_list), var1, var2)
                    pos_list.append(pos_list[pos])

                # now we just have to update original triangles
                for a, b in zip(change_set_face_list, change_set_index_list):
                    for i in b:
                        pos_index[i] = a[0]  # keep in mind ft.position = position index (that we have modified)
                        # we do not modify anything else
            elif ind_step == 4:
                for i, ft in enumerate(index_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    var3 = ft[3]
                    if not no_change_set_pos.exists(pos):  # not in list
                        no_change_set_pos.add(pos)
                        no_change_set_1.add(var1)
                        no_change_set_2.add(var2)
                        no_change_set_3.add(var3)
                    else:  # check list if this already exists
                        base_index = no_change_set_pos.get_index(pos)
                        if no_change_set_1.at_index(base_index) == var1 and \
                                no_change_set_2.at_index(base_index) == var2\
                                and no_change_set_3.at_index(base_index) == var3:
                            pass  # pos exists in the list and matches with vars
                        else:  # pos exists in list but does not match with vars
                            if (pos, var1, var2, var3) in change_set_face_list:
                                change_set_index_list[change_set_face_list.index((pos, var1, var2, var3))].append(i)
                            else:
                                change_set_face_list.append((pos, var1, var2, var3))
                                change_set_index_list.append([i, ])

                # change_set_face_list lists all troublesome faces
                # change_set_index_list lists all the indices for them in the list
                for i, ft in enumerate(change_set_face_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    var3 = ft[3]
                    change_set_face_list[i] = (len(pos_list), var1, var2, var3)
                    pos_list.append(pos_list[pos])

                # now we just have to update original triangles
                for a, b in zip(change_set_face_list, change_set_index_list):
                    for i in b:
                        pos_index[i] = a[0]  # keep in mind ft.position = position index (that we have modified)
                        # we do not modify anything else
            elif ind_step == 5:
                for i, ft in enumerate(index_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    var3 = ft[3]
                    var4 = ft[4]
                    if not no_change_set_pos.exists(pos):  # not in list
                        no_change_set_pos.add(pos)
                        no_change_set_1.add(var1)
                        no_change_set_2.add(var2)
                        no_change_set_3.add(var3)
                        no_change_set_4.add(var4)
                    else:  # check list if this already exists
                        base_index = no_change_set_pos.get_index(pos)
                        if no_change_set_1.at_index(base_index) == var1 and \
                                no_change_set_2.at_index(base_index) == var2\
                                and no_change_set_3.at_index(base_index) == var3\
                                and no_change_set_4.at_index(base_index) == var4:
                            pass  # pos exists in the list and matches with vars
                        else:  # pos exists in list but does not match with vars
                            if (pos, var1, var2, var3, var4) in change_set_face_list:
                                change_set_index_list[change_set_face_list.index((pos, var1, var2, var3, var4
                                                                                  ))].append(i)
                            else:
                                change_set_face_list.append((pos, var1, var2, var3, var4))
                                change_set_index_list.append([i, ])

                # change_set_face_list lists all troublesome faces
                # change_set_index_list lists all the indices for them in the list
                for i, ft in enumerate(change_set_face_list):
                    pos = ft[0]
                    var1 = ft[1]
                    var2 = ft[2]
                    var3 = ft[3]
                    var4 = ft[4]
                    change_set_face_list[i] = (len(pos_list), var1, var2, var3, var4)
                    pos_list.append(pos_list[pos])

                # now we just have to update original triangles
                for a, b in zip(change_set_face_list, change_set_index_list):
                    for i in b:
                        pos_index[i] = a[0]  # keep in mind ft.position = position index (that we have modified)
                        # we do not modify anything else

        def update_triangles():
            # then you put the final triangle set through nv strip and it returns the new position indices
            # you put those indices through this turn them into uv indices and normal indices

            change_set_face_list_pos = [a[0] for a in change_set_face_list]

            set_1 = []
            if no_change_set_1.pair_list:
                for i in tri_strips:  # position indices we need to convert to uv indices
                    if no_change_set_pos.exists(i):
                        i = no_change_set_1.at_index(no_change_set_pos.get_index(i))
                    else:
                        i = change_set_face_list[change_set_face_list_pos.index(i)][1]
                    set_1.append(i)

            set_2 = []
            if no_change_set_2.pair_list:
                for i in tri_strips:  # position indices we need to convert to normal indices
                    if no_change_set_pos.exists(i):
                        i = no_change_set_2.at_index(no_change_set_pos.get_index(i))
                    else:
                        i = change_set_face_list[change_set_face_list_pos.index(i)][2]
                    set_2.append(i)

            set_3 = []
            if no_change_set_3.pair_list:
                for i in tri_strips:  # position indices we need to convert to colour indices
                    if no_change_set_pos.exists(i):
                        i = no_change_set_3.at_index(no_change_set_pos.get_index(i))
                    else:
                        i = change_set_face_list[change_set_face_list_pos.index(i)][3]
                    set_3.append(i)

            set_4 = []
            if no_change_set_4.pair_list:
                for i in tri_strips:  # position indices we need to convert to colour indices
                    if no_change_set_pos.exists(i):
                        i = no_change_set_4.at_index(no_change_set_pos.get_index(i))
                    else:
                        i = change_set_face_list[change_set_face_list_pos.index(i)][4]
                    set_4.append(i)

            pos_indices = []
            for i in tri_strips:  # indices we need to convert to pos indices
                if no_change_set_pos.exists(i):
                    pass  # value was never changed
                else:
                    i = pos_list.index(pos_list[i])
                pos_indices.append(i)

            used_indices = [pos_indices]
            ind_step = 1
            if set_1:
                used_indices.append(set_1)
                ind_step += 1
            if set_2:
                used_indices.append(set_2)
                ind_step += 1
            if set_3:
                used_indices.append(set_3)
                ind_step += 1
            if set_4:
                used_indices.append(set_4)
                ind_step += 1

            faces_all_flat = [0] * ind_step * len(pos_indices)

            for i, ind_type in enumerate(used_indices):
                for v, var in enumerate(ind_type):
                    faces_all_flat[v * ind_step + i] = var
            return faces_all_flat

        edit_faces_for_loops()
        tri_strips = self.to_tri_strip(pos_index)
        return update_triangles()


def check_meshes(mesh_list):
    for child in mesh_list:
        mesh = child.data
        faces = list(set([len(poly.vertices) for poly in mesh.polygons]))
        if len(faces) > 1 or faces[0] != 3:
            return True
    return False
