from itertools import chain

from .vertices import VertexData


def implicit_faces_fix_mesh_size(vertex_info):
    # we generate faces then fix both sets
    face_mesh = []
    for data in vertex_info:  # sub mesh
        face_mesh_list = []
        count = 0
        for info in data:  # sub sub mesh, some of these are 3 vertices long
            face_count = len(info.positions) - 2
            if face_count < 0:
                face_count = 0

            for loop in range(face_count // 2):
                loop *= 2
                loop += count
                face_mesh_list.append((loop, loop + 1, loop + 2))
                face_mesh_list.append((loop + 2, loop + 1, loop + 3))

            if face_count % 2 != 0:
                net_count = count + face_count
                face_mesh_list.append((net_count - 1, net_count, net_count + 1))
            count += len(info.positions)

        face_mesh.append(face_mesh_list)
        # this generates a list of non relative face indices
    vertex_list = []
    for data in vertex_info:
        vertex_list.append(VertexData(
            list(chain.from_iterable([info.positions for info in data])),
            list(chain.from_iterable([info.weights for info in data])),
            list(chain.from_iterable([info.bone_list_indices for info in data])),
            list(chain.from_iterable([info.normals for info in data])),
            list(chain.from_iterable([info.uvs for info in data])),
            list(chain.from_iterable([info.wxs for info in data])),
            list(chain.from_iterable([info.colours for info in data])),
        ))  # flat list
    return face_mesh, vertex_list


def implicit_faces(vertex_info):
    face_mesh = []
    for info in vertex_info:  # sub mesh
        face_mesh_list = []
        count = 0
        face_count = len(info.positions) - 2
        if face_count < 0:
            face_count = 0

        for loop in range(face_count // 2):
            loop *= 2
            loop += count
            face_mesh_list.append((loop, loop + 1, loop + 2))
            face_mesh_list.append((loop + 2, loop + 1, loop + 3))

        if face_count % 2 != 0:
            net_count = count + face_count
            face_mesh_list.append((net_count - 1, net_count, net_count + 1))
        count += len(info.positions)

        face_mesh.append(face_mesh_list)
    return face_mesh
