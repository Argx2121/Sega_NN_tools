import bpy

from Sega_NN_tools.modules.util import make_bpy_textures


def _get_image_type(model_format, texture_name, m_tex_index, m_tex_type):
    tex_name = None
    if texture_name:
        tex_name = texture_name[m_tex_index]
        tex_name_str = str(tex_name)
        if model_format == "Sonic2006_X":  # shortcuts
            if "_df." in tex_name_str:
                m_tex_type = "diffuse"
            elif "_nw." in tex_name_str:
                m_tex_type = "normal"
            elif "_sp." in tex_name_str:
                m_tex_type = "emission"
            elif "_rf." in tex_name_str:
                m_tex_type = "reflection"
        elif model_format == "HouseOfTheDead4_C":  # shortcuts
            if "_dif." in tex_name_str:
                m_tex_type = "diffuse"
            elif "_nom." in tex_name_str:
                m_tex_type = "normal"
            elif "_spe." in tex_name_str:
                m_tex_type = "emission"
            elif "_ref." in tex_name_str:
                m_tex_type = "reflection"
    return m_tex_type, tex_name


class Material:  # functional, but needs a rework

    def make_material_complex(self):
        model_format = self.format
        texture_name = self.texture_names
        material_count = self.model_data.data.material_count
        mat_names = self.mat_names
        material_list_blender = self.material_list_blender
        material_list = self.model_data.materials
        model_name_strip = self.model_name_strip
        material_in_next_block = self.material_in_next_block

        if model_format != "SonicRiders_X":
            if not texture_name:
                for m in material_list:
                    m.tex_count = 0
            elif type(texture_name[0]) == str:
                texture_name = make_bpy_textures(texture_name)
                if type(texture_name[0]) == str:
                    for m in material_list:
                        m.tex_count = 0

        for mat_index in range(material_count):
            # make material - first mat data stored
            material = bpy.data.materials.new(mat_names[mat_index])
            material_list_blender.append(material)
            m = material_list[mat_index]
            m_texture_count = m.tex_count
            m_col = m.colour
            transparency = m_col.rgba_main[3]
            material.use_nodes = True
            n_tree = material.node_tree

            # generic stuff
            final = n_tree.nodes["Material Output"]
            final.location = 850, 150

            diffuse = n_tree.nodes["Principled BSDF"]
            diffuse.name = "diffuse"
            diffuse.location = 100, 520

            mix_col = n_tree.nodes.new(type="ShaderNodeMixRGB")
            mix_col.name = "mix_col"
            mix_col.location = -200, 450
            n_tree.nodes["mix_col"].inputs[0].default_value = 0
            n_tree.nodes["mix_col"].blend_type = 'MULTIPLY'

            mix_v_col = n_tree.nodes.new(type="ShaderNodeMixRGB")
            mix_v_col.name = "mix_v_col"
            mix_v_col.location = -500, 520
            n_tree.nodes["mix_v_col"].inputs[0].default_value = 0
            n_tree.nodes["mix_v_col"].blend_type = 'MULTIPLY'

            rgba = n_tree.nodes.new(type="ShaderNodeRGB")
            rgba.location = -700, 520
            rgba.name = "RGB"
            n_tree.nodes["RGB"].outputs[0].default_value = \
                (m_col.rgba_main[0], m_col.rgba_main[1], m_col.rgba_main[2], 1)
            if transparency != 1:  # transparency value
                material.blend_method = "BLEND"
                n_tree.nodes["diffuse"].inputs[18].default_value = transparency

            attr = n_tree.nodes.new(type="ShaderNodeAttribute")
            attr.name = "Attr"
            attr.location = - 850, 330
            attr.attribute_name = model_name_strip + "_Vertex_Colours"

            n_tree.links.new(final.inputs[0], diffuse.outputs[0])
            n_tree.links.new(diffuse.inputs[0], mix_col.outputs[0])
            n_tree.links.new(mix_col.inputs[1], mix_v_col.outputs[0])
            n_tree.links.new(mix_v_col.inputs[1], rgba.outputs[0])
            n_tree.links.new(mix_v_col.inputs[2], attr.outputs[0])

            # specialized
            diffuse_done = False
            reflection_done = False
            normal_done = False
            emission_done = False
            for t_index in range(m_texture_count):
                m_tex = m.texture[t_index]
                m_tex_type = m_tex.tex_type
                m_tex_set = m_tex.tex_setting
                m_tex_index = m_tex.tex_index

                m_tex_type, tex_name = _get_image_type(model_format, texture_name, m_tex_index, m_tex_type)

                if m_tex_type == "diffuse":
                    if not diffuse_done:
                        diffuse_done = True
                        tex_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        tex_node.location = - 580, 300
                        if m_tex_set == 3:
                            tex_node.extension = "EXTEND"
                        material.blend_method = "CLIP"
                        if texture_name:
                            tex_node.image = tex_name
                            n_tree.links.new(diffuse.inputs[18], tex_node.outputs[1])
                        else:
                            material_in_next_block.append(
                                [m_tex_index, tex_node, diffuse.inputs[18], tex_node.outputs[1], n_tree])
                        n_tree.links.new(mix_col.inputs[2], tex_node.outputs[0])
                        n_tree.nodes["mix_v_col"].inputs[0].default_value = 1
                        n_tree.nodes["mix_col"].inputs[0].default_value = 1
                elif m_tex_type == "normal":
                    if not normal_done:
                        normal_done = True
                        tex_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        tex_node.location = - 580, 20
                        tex_node.image = tex_name
                        tex_node.image.colorspace_settings.name = 'Non-Color'

                        norm_node = n_tree.nodes.new(type="ShaderNodeNormalMap")
                        norm_node.location = - 200, 20
                        if model_format == "Sonic2006_X":
                            norm_node.space = 'WORLD'

                        n_tree.links.new(norm_node.inputs[1], tex_node.outputs[0])
                        n_tree.links.new(diffuse.inputs[-3], norm_node.outputs[0])

                elif m_tex_type == "reflection":
                    if not reflection_done:
                        reflection_done = True
                        env_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        env_node.location = 100, -130

                        spec = n_tree.nodes.new(type="ShaderNodeEeveeSpecular")
                        spec.name = "spec"
                        spec.location = 400, -50

                        tex_co = n_tree.nodes.new(type="ShaderNodeTexCoord")
                        tex_co.name = "tex_co"
                        tex_co.location = - 120, - 120

                        end_node = n_tree.nodes.new(type="ShaderNodeMixShader")
                        end_node.name = "end_node"
                        end_node.location = 600, 140
                        n_tree.nodes["end_node"].inputs[0].default_value = 0.5

                        if model_format == "Sonic2006_X":
                            material.blend_method = "BLEND"
                            n_tree.nodes["diffuse"].inputs[18].default_value = 0

                        if m_tex_set == 3:
                            tex_node.extension = "EXTEND"
                        if texture_name:
                            env_node.image = tex_name
                            n_tree.links.new(env_node.inputs[0], tex_co.outputs[6])
                        else:
                            material_in_next_block.append(
                                [m_tex_index, env_node, env_node.inputs[0], tex_co.outputs[6], n_tree])

                        n_tree.links.remove(diffuse.outputs[0].links[0])
                        n_tree.links.new(spec.inputs[0], env_node.outputs[0])
                        n_tree.links.new(end_node.inputs[1], diffuse.outputs[0])
                        n_tree.links.new(end_node.inputs[2], spec.outputs[0])
                        n_tree.links.new(final.inputs[0], end_node.outputs[0])
                elif m_tex_type == "emission":
                    if not emission_done:
                        emission_done = True
                        env_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        env_node.location = 100, -130

                        emiss = n_tree.nodes.new(type="ShaderNodeEmission")
                        emiss.name = "emiss"
                        emiss.location = 400, -50

                        end_node = n_tree.nodes.new(type="ShaderNodeAddShader")
                        end_node.name = "end_node"
                        end_node.location = 600, 140

                        env_node.image = tex_name

                        n_tree.links.remove(diffuse.outputs[0].links[0])
                        n_tree.links.new(emiss.inputs[0], env_node.outputs[0])
                        n_tree.links.new(emiss.inputs[1], env_node.outputs[1])
                        n_tree.links.new(end_node.inputs[0], diffuse.outputs[0])
                        n_tree.links.new(end_node.inputs[1], emiss.outputs[0])
                        n_tree.links.new(final.inputs[0], end_node.outputs[0])
                else:  # unsupported textures
                    pass

    def make_material_simple(self):  # for exporting to fbx etc, so keep it simple.
        model_format = self.format
        texture_name = self.texture_names
        material_count = self.model_data.data.material_count
        mat_names = self.mat_names
        material_list_blender = self.material_list_blender
        material_list = self.model_data.materials
        material_in_next_block = self.material_in_next_block

        if model_format != "SonicRiders_X":
            if not texture_name:
                for m in material_list:
                    m.tex_count = 0
            elif type(texture_name[0]) == str:
                for m in material_list:
                    m.tex_count = 0

        for mat_index in range(material_count):
            # make material - first mat data stored
            material = bpy.data.materials.new(mat_names[mat_index])
            material_list_blender.append(material)
            m = material_list[mat_index]
            m_texture_count = m.tex_count
            material.use_nodes = True
            n_tree = material.node_tree

            # generic stuff
            final = n_tree.nodes["Material Output"]
            final.location = 850, 150

            diffuse = n_tree.nodes["Principled BSDF"]
            diffuse.name = "diffuse"
            diffuse.location = 100, 520

            n_tree.links.new(final.inputs[0], diffuse.outputs[0])

            # specialized
            diffuse_done = False
            normal_done = False
            for t_index in range(m_texture_count):
                m_tex = m.texture[t_index]
                m_tex_type = m_tex.tex_type
                m_tex_set = m_tex.tex_setting
                m_tex_index = m_tex.tex_index

                m_tex_type, tex_name = _get_image_type(model_format, texture_name, m_tex_index, m_tex_type)

                if m_tex_type == "diffuse":
                    if not diffuse_done:
                        diffuse_done = True
                        tex_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        tex_node.location = - 580, 300
                        if m_tex_set == 3:
                            tex_node.extension = "EXTEND"
                        material.blend_method = "CLIP"
                        if texture_name:
                            tex_node.image = tex_name
                            n_tree.links.new(diffuse.inputs[0], tex_node.outputs[0])
                        else:
                            material_in_next_block.append(
                                [m_tex_index, tex_node, diffuse.inputs[0], tex_node.outputs[0], n_tree])
                elif m_tex_type == "normal":
                    if not normal_done:
                        normal_done = True
                        tex_node = n_tree.nodes.new(type="ShaderNodeTexImage")
                        tex_node.location = - 580, 20
                        tex_node.image = tex_name
                        tex_node.image.colorspace_settings.name = 'Non-Color'

                        norm_node = n_tree.nodes.new(type="ShaderNodeNormalMap")
                        norm_node.location = - 200, 20
                        if model_format == "Sonic2006_X":
                            norm_node.space = 'WORLD'

                        n_tree.links.new(norm_node.inputs[1], tex_node.outputs[0])
                        n_tree.links.new(diffuse.inputs[-3], norm_node.outputs[0])
                else:  # unsupported textures
                    pass
