import bpy

from Sega_NN_tools.modules.blender.model_assets import model_util


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
            uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV_Map")
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                uv_tex.data[v_index].uv = uv_short_hand[face_index[0]]
                uv_tex.data[v_index + 1].uv = uv_short_hand[face_index[1]]
                uv_tex.data[v_index + 2].uv = uv_short_hand[face_index[2]]

        def make_wxs():
            wx_tex = mesh.uv_layers.new(name=model_name_strip + "_WX_Map")
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                wx_tex.data[v_index].uv = wx_short_hand[face_index[0]]
                wx_tex.data[v_index + 1].uv = wx_short_hand[face_index[1]]
                wx_tex.data[v_index + 2].uv = wx_short_hand[face_index[2]]

        def make_colours():
            for vert_index in range(v_loop_count):
                v_index = vert_index * 3
                face_index = face_list[vert_index]

                col_layer.data[v_index].color = col_short_hand[face_index[0]]
                col_layer.data[v_index + 1].color = col_short_hand[face_index[1]]
                col_layer.data[v_index + 2].color = col_short_hand[face_index[2]]

        def make_normals():
            mesh.normals_split_custom_set_from_vertices(norm_short_hand)
            mesh.use_auto_smooth = True

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

        def make_weights_simple():
            obj.vertex_groups.new(name=bone_names[b_group.index(sm.bone)])
            obj.vertex_groups[0].add(list(range(vertex_count)), 1, "REPLACE")

        mesh = bpy.data.meshes.new(mesh_names[i])
        obj = bpy.data.objects.new(mesh.name, mesh)
        collection.objects.link(obj)

        mesh.from_pydata(pos_short_hand, [], face_list)

        obj.data.materials.append(material_list_blender[sm.material])
        obj.modifiers.new(name=model_name, type='ARMATURE').object = obj.parent = armature

        if uv_short_hand:
            make_uvs()
            if wx_short_hand:
                make_wxs()

        # needed in materials
        col_layer = mesh.vertex_colors.new(name=model_name_strip + "_Vertex_Colours")
        if col_short_hand:
            make_colours()

        if norm_short_hand:
            make_normals()

        if m_info.bone_count_complex:
            make_weights_complex()
        else:
            make_weights_simple()

        if model_name[-3] == "u" and self.settings.clean_mesh:  # problematic fave
            model_util.clean_mesh_strict(obj)
        elif self.settings.clean_mesh:
            model_util.clean_mesh(obj)

    for i in range(len(build_mesh1)):  # for each mesh
        sm = build_mesh1[i]
        sm_mesh_index = sm.vertex
        m_info = mesh_info[sm_mesh_index]
        v_data = vertex_data[sm_mesh_index]
        face_list = face_list1[sm.face]
        vertex_count = len(v_data.positions)
        face_list = [f for f in face_list if f.count(f[0]) == 1 and f.count(f[1]) == 1]

        lowest_index = 0
        highest_index = max([item for sub in face_list for item in sub]) + 1

        v_loop_count = len(face_list)
        uv_short_hand = v_data.uvs[lowest_index: highest_index]
        wx_short_hand = v_data.wxs[lowest_index: highest_index]
        col_short_hand = v_data.colours[lowest_index: highest_index]
        norm_short_hand = v_data.normals[lowest_index: highest_index]
        pos_short_hand = v_data.positions[lowest_index: highest_index]

        build_mesh()
