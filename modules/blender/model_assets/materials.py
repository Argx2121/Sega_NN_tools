import bpy
import os
import pathlib
from platform import system
from bpy.types import Object, Mesh
from dataclasses import dataclass


def sort_list(material_list):
    for mat in material_list:
        tex_formats = [a.type for a in mat.texture]
        if tex_formats.count("diffuse") > 0:
            pop = tex_formats.index("diffuse")
            pop = mat.texture.pop(pop)
            mat.texture.insert(0, pop)
    return material_list


def _make_image(tree, image, settings):
    node = tree.nodes.new(type="ShaderNodeTexImage")
    node.image = image
    node.interpolation = settings.interpolation
    node.projection = settings.projection
    node.extension = settings.extension
    return node


def _make_image_vect(tree, image, settings, letter):
    vect = tree.nodes.new(type="ShaderNode" + letter + "NOVector")
    node = tree.nodes.new(type="ShaderNodeTexImage")
    node.image = image
    node.interpolation = settings.interpolation
    node.projection = settings.projection
    tree.links.new(node.inputs["Vector"], vect.outputs["Image Vector"])
    return vect, node


def _mix_rgb(tree, input_1, input_2):
    node = tree.nodes.new(type="ShaderNodeMixRGB")
    node.inputs["Fac"].default_value = 1
    node.blend_type = 'MULTIPLY'
    tree.links.new(node.inputs["Color1"], input_1)
    tree.links.new(node.inputs["Color2"], input_2)
    return node.outputs[0]


def _mix_colour_reflection(tree, input_1, input_2):
    node = tree.nodes.new(type="ShaderNodeMixRGB")
    # node.blend_type = 'MIX'
    tree.links.new(node.inputs["Color1"], input_1)
    tree.links.new(node.inputs["Color2"], input_2)
    return node.outputs[0]


def _vertex_colours(tree, name):
    node = tree.nodes.new(type="ShaderNodeVertexColor")
    # todo add vertex alpha
    return node.outputs["Color"]


def _diffuse_rgba(tree, image, m_colour, skip_textures):
    rbg = tree.nodes.new(type="ShaderNodeRGB")
    rbg.outputs["Color"].default_value = m_colour.diffuse

    alpha = tree.nodes.new(type="ShaderNodeValue")
    alpha.outputs["Value"].default_value = m_colour.diffuse[-1]

    # image alpha - (rgba alpha * -1 + 1), clamped
    multiply_add = tree.nodes.new(type="ShaderNodeMath")
    multiply_add.operation = 'MULTIPLY_ADD'

    subtract = tree.nodes.new(type="ShaderNodeMath")
    subtract.operation = 'SUBTRACT'
    subtract.use_clamp = True

    tree.links.new(multiply_add.inputs["Value"], alpha.outputs["Value"])
    multiply_add.inputs["Value_001"].default_value = -1
    multiply_add.inputs["Value_002"].default_value = 1

    if not skip_textures:
        tree.links.new(subtract.inputs["Value"], image.outputs["Alpha"])
    else:
        subtract.inputs["Value"].default_value = 1

    alpha_invert = tree.nodes.new(type="ShaderNodeInvert")
    tree.links.new(alpha_invert.inputs["Color"], subtract.outputs["Value"])

    tree.links.new(subtract.inputs["Value_001"], multiply_add.outputs["Value"])

    return _mix_rgb(tree, image.outputs["Color"], rbg.outputs["Color"]), alpha_invert.outputs["Color"]


def _rgba(tree, m_colour):
    rgb = tree.nodes.new(type="ShaderNodeRGB")
    rgb.outputs["Color"].default_value = m_colour.diffuse

    alpha = tree.nodes.new(type="ShaderNodeValue")
    alpha.outputs["Value"].default_value = m_colour.diffuse[-1]
    alpha_invert = tree.nodes.new(type="ShaderNodeInvert")
    tree.links.new(alpha_invert.inputs["Color"], alpha.outputs["Value"])

    return rgb.outputs["Color"], alpha_invert.outputs["Color"]


def _reflection(tree, image):
    image.name = "ReflectionTexture"
    node = tree.nodes.new(type="ShaderNodeTexCoord")
    tree.links.new(image.inputs["Vector"], node.outputs["Reflection"])
    return image.outputs["Color"]


def _reflection_wx(tree, image, model_name_strip):
    image.name = "ReflectionWxTexture"
    ref_node = tree.nodes.new(type="ShaderNodeTexCoord")

    wx_node = tree.nodes.new(type="ShaderNodeUVMap")
    wx_node.uv_map = model_name_strip + "_UV2_Map"

    math_node = tree.nodes.new(type="ShaderNodeVectorMath")
    math_node.operation = 'ADD'

    tree.links.new(math_node.inputs["Value"], ref_node.outputs["Reflection"])
    tree.links.new(math_node.inputs["Value_001"], wx_node.outputs["UV"])
    tree.links.new(image.inputs["Vector"], math_node.outputs["Vector"])
    return image.outputs["Color"]


def _normal(tree, image, settings):
    image.name = "NormalTexture"
    if image.image:
        image.image.colorspace_settings.name = 'Non-Color'
    node = tree.nodes.new(type="ShaderNodeNormalMap")
    tree.links.new(node.inputs["Color"], image.outputs["Color"])
    node.space = settings.space.upper()
    return node.outputs["Normal"]


def _bump(tree, image):
    image.name = "BumpTexture"
    if image.image:
        image.image.colorspace_settings.name = 'Non-Color'
    node = tree.nodes.new(type="ShaderNodeBump")
    tree.links.new(node.inputs["Height"], image.outputs["Color"])
    return node.outputs["Normal"]


def _wx_alpha(tree, colour, image, model_name_strip):
    node = tree.nodes.new(type="ShaderNodeUVMap")
    node.uv_map = model_name_strip + "_UV2_Map"
    tree.links.new(image.inputs["Vector"], node.outputs["UV"])

    multi = tree.nodes.new(type="ShaderNodeMixRGB")
    multi.blend_type = 'MULTIPLY'

    tree.links.new(multi.inputs["Fac"], image.outputs["Alpha"])
    tree.links.new(multi.inputs["Color1"], colour)
    tree.links.new(multi.inputs["Color2"], image.outputs["Color"])

    return multi.outputs["Color"]


def _wx(tree, colour, image, model_name_strip):
    node = tree.nodes.new(type="ShaderNodeUVMap")
    node.uv_map = model_name_strip + "_UV2_Map"
    tree.links.new(image.inputs["Vector"], node.outputs["UV"])

    multi = tree.nodes.new(type="ShaderNodeMixRGB")
    multi.blend_type = 'MULTIPLY'

    tree.links.new(multi.inputs["Color1"], image.outputs["Color"])
    tree.links.new(multi.inputs["Color2"], colour)

    return multi.outputs["Color"]


def material_accurate(self):
    texture_name = self.texture_names
    material_count = self.model.info.material_count
    mat_names = self.mat_names
    material_list_blender = self.material_list_blender
    material_list = self.model.materials
    model_name_strip = self.model_name_strip
    file_path = self.file_path
    model_format = self.format
    build_meshes = self.model.build_mesh
    model_end = model_format[-1]
    if model_end in {"X"}:
        material_effects = [("", "") for _ in range(material_count)]
        if self.effect:
            for mesh in build_meshes:
                material_effects[mesh.material] = self.effect[mesh.shader]

    material_list = sort_list(material_list)

    skip_textures = False

    if not texture_name:
        skip_textures = True
    elif texture_name:
        texture_name, tex_interp = make_bpy_textures(
            file_path, texture_name, self.armature, self.settings.recursive_textures, self.settings.load_incomplete)
    self.armature.data.nn_material_count = material_count

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)
        self.armature.data.nn_materials[mat_index].material = material
        spec_mix = False  # as specular is mixed in a node, we need to make sure that node gets spawned in
        # if it isnt spawned in during the image node loop we will add it at the end

        m = material_list[mat_index]
        m_texture_count = m.texture_count
        m_col = m.colour
        material.use_nodes = True
        tree = material.node_tree

        material.blend_method = m.transparency
        # material.surface_render_method = 'BLENDED'

        material.show_transparent_back = False
        material.use_backface_culling = True
        tree.nodes.remove(tree.nodes["Principled BSDF"])

        mat_flags = m.mat_flags
        # defaults
        v_col, disable_fog, unlit, buff_comp, buff_update, callback, no_uv_transform = False, False, False, True, True, False, False
        backface_off, has_spec, hide = True, True, False

        if model_end == "G":
            shader = tree.nodes.new('ShaderNodeGNOShader')
            colour_init = tree.nodes.new('ShaderNodeGNOShaderInit')

            v_col = mat_flags >> 0 & 1
            backface_off = mat_flags >> 1 & 1
            vertex_tex_emu = mat_flags >> 2 & 1  # do you even DO anything ??
            disable_fog = mat_flags >> 5 & 1
            unlit = mat_flags >> 8 & 1
            hide = mat_flags >> 9 & 1
            # if i chop you up and i put you in a meat grinder and the only thing that comes out is your eye
            # youre- youre probably dead!!
            buff_comp = not mat_flags >> 16 & 1
            buff_update = not mat_flags >> 17 & 1
            comp_after = mat_flags >> 18 & 1  # needed for clip
            # normally would be used for shaders but gamecube......... so only purpose is cutout........
            # (compare z buff after texture)
            has_spec = mat_flags >> 24 & 1
            has_spec_texture = (mat_flags >> 24 & 1) and (mat_flags >> 25 & 1)  # verified
            callback = mat_flags >> 31 & 1

            shader.blend_type = str(m.render.blend)  # setting the values of these changes no calculations
            shader.source_fact = str(m.render.source)
            shader.dest_fact = str(m.render.destination)
            shader.blend_op = str(m.render.operation)
            shader.z_mode = str(m.render.z_mode)
            shader.alpha_ref0 = m.render.ref0
            shader.alpha_ref1 = m.render.ref1
            shader.alpha_comp0 = str(m.render.comp0)
            shader.alpha_comp1 = str(m.render.comp1)
            shader.alpha_op = str(m.render.alpha)
            shader.buff_comp = buff_comp
            shader.buff_update = buff_update
        elif model_end == "X":
            shader = tree.nodes.new('ShaderNodeXNOShader')
            colour_init = tree.nodes.new('ShaderNodeXNOShaderInit')
            m_render = m.render
            colour_init.inputs["Emission"].default_value = m_col.emission

            hide = mat_flags >> 0 & 1
            backface_off = mat_flags >> 1 & 1
            unlit = mat_flags >> 2 & 1
            disable_fog = mat_flags >> 3 & 1
            v_col = mat_flags >> 4 & 1  # seems most likely
            no_uv_transform = mat_flags >> 5 & 1
            two_sided_lighting = mat_flags >> 6 & 1
            has_spec = mat_flags >> 24 & 1
            callback = mat_flags >> 31 & 1
            buff_comp = m_render.z_compare
            buff_update = m_render.z_update
            # setting the values of these changes no calculations
            shader.shader_file = material_effects[mat_index][0]
            shader.shader_name = material_effects[mat_index][1]
            shader.blend_color = m_render.blend_color
            shader.buffer_blend = m_render.buffer_blend
            shader.alpha_test = m_render.alpha_test
            shader.alpha_ref = m_render.alpha_ref
            shader.blend_op = str(m_render.blend_operation)
            shader.source_fact = str(m_render.source)
            shader.dest_fact = str(m_render.destination)
            shader.blend_logic = str(m_render.logic_operation)
            shader.test_mode = str(m_render.alpha_mode)
            shader.z_mode = str(m_render.z_mode)
            shader.buff_comp = buff_comp
            shader.buff_update = buff_update

        colour_init.inputs["Material Color"].default_value = m_col.diffuse
        colour_init.inputs["Material Alpha"].default_value = m_col.diffuse[-1]
        x_loc = -400
        y_loc = 300
        colour_init.location = (x_loc, y_loc)

        if backface_off:
            material.use_backface_culling = False
        else:
            material.use_backface_culling = True

        if v_col:
            node = tree.nodes.new(type="ShaderNodeVertexColor")
            tree.links.new(colour_init.inputs["Vertex Color"], node.outputs[0])
            tree.links.new(colour_init.inputs["Vertex Alpha"], node.outputs[1])
            node.location = (x_loc - 200, y_loc)

        if unlit:
            colour_init.unshaded = True
        if callback:
            shader.inputs["Callback"].default_value = True
        if disable_fog:
            shader.inputs["Disable Fog"].default_value = True
        if has_spec == 0:
            colour_init.use_specular = False

        colour_init.inputs["Ambient"].default_value = m_col.ambient
        colour_init.inputs["Specular"].default_value = m_col.specular
        colour_init.inputs["Specular Gloss"].default_value = m_col.shininess
        colour_init.inputs["Specular Level"].default_value = m_col.specular_value

        shader.inputs["User"].default_value = m.user
        tree.links.new(tree.nodes["Material Output"].inputs[0], shader.outputs[0])
        last_node = colour_init

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_index = m_tex.index
            m_mix = m_tex.texture_flags
            if model_end == "X" and m_mix.light_stage:
                mix_node.multi_shading = True
                continue
            m_tex.interpolation = tex_interp[m_tex_index][1]
            if m_tex.interpolation == "Anisotropic":  # Nuh uh
                m_tex.interpolation = "Linear"

            if skip_textures:
                vector_node, image_node = _make_image_vect(tree, None, m_tex, model_end)
            else:
                vector_node, image_node = _make_image_vect(tree, texture_name[m_tex_index], m_tex, model_end)

            image_node.location = (x_loc, y_loc - 450)
            vector_node.location = (x_loc - 300, y_loc - 800)

            lod_bias = False
            max_mip_map_level = False
            custom_filter = False
            min_interp = False
            mag_interp = False

            m_specular, m_specular2 = False, False
            m_multiply, m_decal, m_replace, m_blend = False, False, False, False
            m_decal2, m_subtract, m_add = False, False, False
            m_pass_color, m_alpha_tex = False, False

            if model_end == "G":
                m_specular = m_mix.specular
                m_specular2 = m_mix.specular2
                m_multiply = m_mix.multiply
                m_decal = m_mix.decal
                m_replace = m_mix.replace
                m_blend = m_mix.blend
                m_decal2 = m_mix.decal_2
                m_subtract = m_mix.subtract
                m_add = m_mix.add
                if not m_subtract:
                    m_subtract = m_mix.subtract_2
                m_pass_color = m_mix.pass_color
                m_alpha_tex = m_mix.alpha_tex
                no_uv_transform = bool(m_mix.no_uv_transform)
            elif model_end == "X":
                m_specular = m_mix.specular
                m_specular2 = m_mix.specular2
                m_multiply = m_mix.multiply
                m_decal = m_mix.decal
                m_replace = m_mix.replace
                m_blend = m_mix.blend
                m_decal2 = m_mix.decal_2
                m_subtract = m_mix.subtract
                m_add = m_mix.add
                lod_bias = m_tex.lod_bias
                max_mip_map_level = m_tex.max_mip_map_level
                custom_filter = bool(m_mix.custom_filter)
                min_interp = m_tex.interp_min
                mag_interp = m_tex.interp_mag
                no_uv_transform = bool(m_mix.no_uv_transform)

            vector_node.transform_mode = "0"
            if not no_uv_transform:
                vector_node.inputs["UV Offset"].default_value = (m_tex.offset[0], - m_tex.offset[1], 0.0)
                vector_node.inputs["UV Scale"].default_value = (m_tex.scale[0], m_tex.scale[1], 0.0)

            if m_mix.clampu:
                vector_node.inputs["U"].default_value = 0
                vector_node.u_type = "0"
            elif m_mix.mirroru:
                vector_node.inputs["U"].default_value = 2
                vector_node.u_type = "2"
            else:
                vector_node.inputs["U"].default_value = 1
                vector_node.u_type = "1"

            if m_mix.clampv:
                vector_node.inputs["V"].default_value = 0
                vector_node.v_type = "0"
            elif m_mix.mirrorv:
                vector_node.inputs["V"].default_value = 2
                vector_node.v_type = "2"
            else:
                vector_node.inputs["V"].default_value = 1
                vector_node.v_type = "1"

            if lod_bias:
                vector_node.lod_bias = lod_bias
            if max_mip_map_level:
                vector_node.max_mip_map_level = max_mip_map_level
            if custom_filter:
                vector_node.custom_filter = custom_filter
            if min_interp:
                vector_node.interp_min = min_interp
            if mag_interp:
                vector_node.interp_mag = mag_interp

            if m_mix.reflection:
                vector_node.transform_mode = "1"
            elif m_mix.position:
                vector_node.transform_mode = "2"
            else:
                node = tree.nodes.new(type="ShaderNodeUVMap")
                node.location = (x_loc - 500, y_loc - 1100)
                if m_mix.uv1:
                    node.uv_map = model_name_strip + "_UV1_Map"
                    tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
                elif m_mix.uv2:
                    node.uv_map = model_name_strip + "_UV2_Map"
                    tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
                elif m_mix.uv3:
                    node.uv_map = model_name_strip + "_UV3_Map"
                    tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
                elif m_mix.uv4:
                    node.uv_map = model_name_strip + "_UV4_Map"
                    tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])

            # onwards my mixnodes
            if m_specular or m_specular2:
                spec_mix = True
                mix_type = '.GNO_SPEC'
                if m_specular2:
                    mix_type = '.GNO_SPEC2'
                mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
                mix_node.blend_type = mix_type
                mix_node.texture_2 = m_tex_index
                x_loc += 400
                mix_node.location = (x_loc, y_loc)

                tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
                tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
                tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
                last_node = mix_node
            else:
                mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOMixRGB')
                mix_type = '.GNO_MULTI'
                x_loc += 400
                mix_node.location = (x_loc, y_loc)
                if m_multiply:
                    mix_type = '.GNO_MULTI'
                elif m_decal:
                    mix_type = '.GNO_DECAL'
                elif m_replace:
                    mix_type = '.GNO_REPLACE'
                elif m_blend:
                    mix_type = '.GNO_BLEND'
                elif m_pass_color:
                    mix_type = '.GNO_PASSCOLOR'
                elif m_alpha_tex:
                    mix_type = '.GNO_ALPHATEX'
                elif m_decal2:
                    mix_type = '.GNO_DECAL2'
                elif m_subtract:
                    mix_type = '.GNO_SUB'
                elif m_add:
                    mix_type = '.GNO_ADD'
                mix_node.blend_type = mix_type
                mix_node.texture_2 = m_tex_index

                tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
                tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
                last_node = mix_node

            if model_end == "G" and m_mix.multiply_shading:
                mix_node.multi_shading = True
            mix_node.inputs["Color 2 Multiplier"].default_value = m_tex.blend

        if not spec_mix:
            # forced to add to make specular be mixed in
            mix_type = '.GNO_SPEC'
            mix_node = tree.nodes.new('ShaderNode' + model_end + 'NOSpecular')
            mix_node.blend_type = mix_type
            x_loc += 400
            mix_node.location = (x_loc, y_loc)

            tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
            tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
            tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
            last_node = mix_node

        tree.links.new(shader.inputs["Color"], last_node.outputs[0])
        tree.links.new(shader.inputs["Alpha"], last_node.outputs[1])
        x_loc += 400
        shader.location = (x_loc, y_loc)
        x_loc += 400
        tree.nodes["Material Output"].location = (x_loc, y_loc)


def material_complex(self):
    texture_name = self.texture_names
    material_count = self.model.info.material_count
    mat_names = self.mat_names
    material_list_blender = self.material_list_blender
    material_list = self.model.materials
    model_name_strip = self.model_name_strip
    file_path = self.file_path
    model_format = self.format

    material_list = sort_list(material_list)

    skip_textures = False

    if not texture_name:
        skip_textures = True
    elif texture_name:
        texture_name, tex_interp = make_bpy_textures(
            file_path, texture_name, self.armature, self.settings.recursive_textures, self.settings.load_incomplete)

    self.armature.data.nn_material_count = material_count

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)
        self.armature.data.nn_materials[mat_index].material = material

        m = material_list[mat_index]
        m_texture_count = m.texture_count
        m_col = m.colour
        material.use_nodes = True
        tree = material.node_tree

        material.blend_method = m.transparency
        material.show_transparent_back = False
        material.use_backface_culling = True
        # show_transparent_back is usually needed off however if used on shadows 06 model it messes up the normals
        # if black means transparent and the image has gradients, separate hsv -> image input, v output
        tree.nodes.remove(tree.nodes["Principled BSDF"])

        colour = False
        alpha = 1
        reflection = False
        spectacular = False
        emission = False

        mat_flags = m.mat_flags

        # noinspection SpellCheckingInspection
        n_end = tree.nodes.new(type="ShaderNodeEeveeSpecular")
        n_end.inputs["Roughness"].default_value = 0.5

        tree.links.new(tree.nodes["Material Output"].inputs["Surface"], n_end.outputs["BSDF"])

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_type = m_tex.type
            m_tex_index = m_tex.index
            m_tex.interpolation = tex_interp[m_tex_index][1]
            if m_tex.interpolation == "Anisotropic":  # Nuh uh
                m_tex.interpolation = "Linear"

            if m_tex_type == "none":
                continue

            if skip_textures:
                image_node = _make_image(tree, None, m_tex)
            else:
                image_node = _make_image(tree, texture_name[m_tex_index], m_tex)

            if m_tex_type == "diffuse":
                colour, alpha = _diffuse_rgba(tree, image_node, m_col, skip_textures)
                vertex_colours = _vertex_colours(tree, model_name_strip)
                colour = _mix_rgb(tree, colour, vertex_colours)
            elif m_tex_type == "normal":
                displacement = _normal(tree, image_node, m_tex)
                tree.links.new(n_end.inputs["Normal"], displacement)
            elif m_tex_type == "emission":
                image_node.name = "EmissionTexture"
                emission = image_node.outputs[0]
                tree.links.new(n_end.inputs["Emissive Color"], image_node.outputs["Color"])
            elif m_tex_type == "reflection":
                reflection = _reflection(tree, image_node)
            elif m_tex_type == "reflection_wx":
                reflection = _reflection_wx(tree, image_node, model_name_strip)
            elif m_tex_type == "bump":
                displacement = _bump(tree, image_node)
                tree.links.new(n_end.inputs["Normal"], displacement)
            elif m_tex_type == "spectacular":  # guys what lmao
                spectacular = image_node.outputs[0]
                tree.links.new(n_end.inputs["Specular"], image_node.outputs["Color"])
            elif m_tex_type == "wx_alpha":
                colour = _wx_alpha(tree, colour, image_node, model_name_strip)
            elif m_tex_type == "wx":
                colour = _wx(tree, colour, image_node, model_name_strip)

            if not colour:  # if a diffuse texture hasn't been found
                colour, alpha = _rgba(tree, m_col)
                vertex_colours = _vertex_colours(tree, model_name_strip)
                colour = _mix_rgb(tree, colour, vertex_colours)

            if reflection:
                colour = _mix_colour_reflection(tree, colour, reflection)
                # for some reason shadow 06 and probably other character models
                #  like eye reflection colour output for fac in transparency shader
                #  there isn't a way to determine if this needs to be set up though

            tree.links.new(n_end.inputs["Base Color"], colour)
            tree.links.new(n_end.inputs["Transparency"], alpha)


def link_uv(m_tex, model_name_strip, tree, node):
    if 5 > m_tex.uv:
        uv_node = tree.nodes.new(type="ShaderNodeUVMap")
        uv_node.uv_map = model_name_strip + "_UV" + str(m_tex.uv) + "_Map"
        tree.links.new(node.inputs[0], uv_node.outputs[0])


def material_simple(self):  # for exporting to fbx etc, so keep it simple.
    texture_name = self.texture_names
    material_count = self.model.info.material_count
    mat_names = self.mat_names
    material_list_blender = self.material_list_blender
    material_list = self.model.materials
    model_name_strip = self.model_name_strip
    file_path = self.file_path

    material_list = sort_list(material_list)

    skip_textures = False

    if not texture_name:
        skip_textures = True
    elif texture_name:
        texture_name, tex_interp = make_bpy_textures(
            file_path, texture_name, self.armature, self.settings.recursive_textures, self.settings.load_incomplete)

    self.armature.data.nn_material_count = material_count

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)
        self.armature.data.nn_materials[mat_index].material = material
        material.show_transparent_back = False
        material.use_backface_culling = True

        m = material_list[mat_index]
        m_texture_count = m.texture_count
        m_col = m.colour
        material.use_nodes = True
        tree = material.node_tree
        material.blend_method = m.transparency

        colour = False
        diffuse = tree.nodes["Principled BSDF"]

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_type = m_tex.type
            m_tex_index = m_tex.index
            m_tex.interpolation = tex_interp[m_tex_index][1]
            if m_tex.interpolation == "Anisotropic":  # Nuh uh
                m_tex.interpolation = "Linear"

            if m_tex_type == "none":
                continue

            if skip_textures:
                image_node = _make_image(tree, None, m_tex)
            else:
                image_node = _make_image(tree, texture_name[m_tex_index], m_tex)

            if m_tex_type == "diffuse":
                image_node.name = "DiffuseTexture"
                _rgba(tree, m_col)
                _vertex_colours(tree, model_name_strip)

                colour = True

                tree.links.new(diffuse.inputs["Base Color"], image_node.outputs["Color"])
            elif m_tex_type == "normal":
                displacement = _normal(tree, image_node, m_tex)

                tree.links.new(diffuse.inputs["Normal"], displacement)
            elif m_tex_type == "emission":
                # these might need to be mixed with vcol and base colour idk
                image_node.name = "EmissionTexture"
                tree.links.new(diffuse.inputs["Emission Color"], image_node.outputs["Color"])
                diffuse.inputs["Emission Strength"].default_value = 1
                diffuse.inputs["Base Color"].default_value = (0, 0, 0, 1)

            elif m_tex_type == "bump":
                displacement = _bump(tree, image_node)

                tree.links.new(diffuse.inputs["Normal"], displacement)

        if not colour:  # if a diffuse texture hasn't been found
            rgb = tree.nodes.new(type="ShaderNodeRGB")
            rgb.outputs[0].default_value = m_col.diffuse

            alpha = tree.nodes.new(type="ShaderNodeValue")
            alpha.outputs[0].default_value = m_col.diffuse[-1]

            tree.links.new(diffuse.inputs[0], rgb.outputs[0])
            tree.links.new(diffuse.inputs[-5], alpha.outputs[0])


def make_bpy_textures(file_path: str, texture_names: list, armature, recursive: bool, load_incomplete: bool):
    # Finds textures and imports them to Blender (if applicable)
    path_base = pathlib.Path(pathlib.Path(file_path).parent)
    tex_names = [tex[0].rsplit(".", 1)[0] for tex in texture_names]
    tex_interp = [tex[1] for tex in texture_names]
    armature.data.nn_texture_count = len(tex_names)

    if recursive:
        path_list_dds = [[str(path) for path in path_base.rglob(tex + ".dds")] for tex in tex_names]
        path_list_png = [[str(path) for path in path_base.rglob(tex + ".png")] for tex in tex_names]
    else:
        path_list_dds = [[str(path) for path in path_base.glob(tex + ".dds")] for tex in tex_names]
        path_list_png = [[str(path) for path in path_base.glob(tex + ".png")] for tex in tex_names]

    dds_check = [bool(a) for a in path_list_dds]
    if False not in dds_check:
        tex = [bpy.data.images.load(tex[0]) for tex in path_list_dds]
        for i, t in enumerate(tex):
            armature.data.nn_textures[i].texture = t
            armature.data.nn_textures[i].interp_min = tex_interp[i][0]
            armature.data.nn_textures[i].interp_mag = tex_interp[i][1]
        return tex, tex_interp
    png_check = [bool(a) for a in path_list_png]
    if False not in png_check:
        tex = [bpy.data.images.load(tex[0]) for tex in path_list_png]
        for i, t in enumerate(tex):
            armature.data.nn_textures[i].texture = t
            armature.data.nn_textures[i].interp_min = tex_interp[i][0]
            armature.data.nn_textures[i].interp_mag = tex_interp[i][1]
        return tex, tex_interp

    if load_incomplete:
        png_incomp = []
        for (t_check, tex) in zip(png_check, path_list_png):
            if t_check:
                png_incomp.append(bpy.data.images.load(tex[0]))
            else:
                png_incomp.append(None)
        for i, t in enumerate(png_incomp):
            if t:
                armature.data.nn_textures[i].texture = t
                armature.data.nn_textures[i].interp_min = tex_interp[i][0]
                armature.data.nn_textures[i].interp_mag = tex_interp[i][1]
            else:
                armature.data.nn_textures[i].interp_min = tex_interp[i][0]
                armature.data.nn_textures[i].interp_mag = tex_interp[i][1]
        return png_incomp, tex_interp
    for i, t in enumerate(tex_interp):
        armature.data.nn_textures[i].interp_min = tex_interp[i][0]
        armature.data.nn_textures[i].interp_mag = tex_interp[i][1]

    return [None for _ in texture_names], tex_interp


@dataclass
class MaterialList:
    simple: bool
    material_list: list
    texture_list: dict


@dataclass
class MegaShader:
    name: str
    blend_method: str
    diffuse: list
    alpha: float
    mat_flags: int
    ambient: list
    specular: list
    shininess: float
    specular_value: float
    emission: list
    user: int
    texture_list: list
    # im just gonna reuse stuff
    blend_type: int = 0
    source_fact: int = 0
    dest_fact: int = 0
    blend_op: int = 0
    z_mode: int = 0
    ref0: int = 0  # alpha ref
    ref1: int = 0
    comp0: int = 0
    comp1: int = 0
    alpha_op: int = 0
    shader_file: str = 0
    shader_name: str = 0
    blend_color: list = 0
    alpha_test: bool = 0
    buffer_blend: bool = 0
    buff_comp: int = 0
    buff_update: int = 0


@dataclass
class NNTexture:
    name: str
    image_index: int
    texture_flags: int
    uv_offset: list
    blend: float
    lod_bias: float = 0
    max_mip_map_level: int = 0
    interp_min: str = ''
    interp_mag: str = ''


def get_materials(self):
    obj: Object = self.armature
    material_names = []
    material_list = []
    texture_list = dict()
    model_end = self.format[-1]

    @dataclass
    class Texture:
        __slots__ = ["type", "name"]
        type: str
        name: str

    if self.settings.riders_default:
        class ImageFake:
            class image:
                filepath = "bd_15.png"

            interpolation = "Linear"

        # we have to parse blenders image path data later... (bpy.path.basename(node.image.filepath))
        #  so we will fake it because the image won't actually be loaded into blender
        texture_list["bd_15.png"] = ("Linear", "Linear")

    for child in self.mesh_list:
        child: Object
        material_name = child.active_material.name
        if material_name not in material_names:
            material_names.append(material_name)

    material_names.sort()
    mat_type = True

    for material in material_names:
        name = material
        material = bpy.data.materials[material]
        m_texture_list = []

        def get_list(node_input):
            node_to_work_on = to_socket_from_socket.get(node_input, node_input)
            return node_to_work_on.default_value[::]

        def get_value(node_input):
            node_to_work_on = to_socket_from_socket.get(node_input, node_input)
            return node_to_work_on.default_value

        mat_type = False
        from_socket_to_socket = dict([[link.from_socket, link.to_socket] for link in material.node_tree.links])
        to_socket_from_socket = dict([[link.to_socket, link.from_socket] for link in material.node_tree.links])
        start_node = False
        for node in material.node_tree.nodes[::]:
            if node.bl_idname == "ShaderNode" + model_end + "NOShaderInit":
                start_node = node
                break
        if not start_node:
            raise Exception("ShaderNode" + model_end + "NOShaderInit Node not found in material data")
        mix_node = from_socket_to_socket.get(start_node.outputs[0]).node
        image_stage = 0  # chat im already using image index
        no_uv_transform = True

        # texture stuff
        while mix_node.bl_idname != "ShaderNode" + model_end + "NOShader":
            if not to_socket_from_socket.get(mix_node.inputs[2],
                                             False) and mix_node.bl_idname == "ShaderNode" + model_end + "NOSpecular":
                # if theres no image linked and the mix node is specular
                # then the node exists just to mix spec into shading
                mix_node = from_socket_to_socket.get(mix_node.outputs[0], False).node
                continue

            texture_flags = 0
            image_node = to_socket_from_socket.get(mix_node.inputs[2]).node
            image_index = -1
            if self.settings.over_texture:
                image_index = mix_node.texture_2
            else:
                texture_list[image_node.image.filepath] = (image_node.interpolation, image_node.interpolation)

            # starting with vector node data
            vector_node = to_socket_from_socket.get(image_node.inputs[0]).node
            u_wrap = int(vector_node.u_type)
            v_wrap = int(vector_node.v_type)
            reflection = vector_node.inputs["Reflection Vector"].default_value
            uv_offset = get_list(vector_node.inputs["UV Offset"])
            uv_offset = uv_offset[0], -uv_offset[1]
            lod_bias, max_mip_map_level, interp_min, interp_mag = 0, 0, 0, 0

            if model_end in {'X'}:
                if vector_node.custom_filter:
                    texture_flags |= 1 << 25
                if vector_node.lod_bias:
                    texture_flags |= 1 << 26
                if vector_node.max_mip_map_level:
                    texture_flags |= 1 << 27
                lod_bias = vector_node.lod_bias
                max_mip_map_level = vector_node.max_mip_map_level
                interp_min = vector_node.interp_min
                interp_mag = vector_node.interp_mag

            if 0 == uv_offset[0] == uv_offset[1]:
                texture_flags |= 1 << 30
            else:
                no_uv_transform = False
            if u_wrap == 0:
                texture_flags |= 1 << 16
            elif u_wrap == 1:
                texture_flags |= 1 << 18
            elif u_wrap == 2:
                texture_flags |= 1 << 20
            if v_wrap == 0:
                texture_flags |= 1 << 17
            elif v_wrap == 1:
                texture_flags |= 1 << 19
            elif v_wrap == 2:
                texture_flags |= 1 << 21

            if reflection:
                texture_flags |= 1 << 13
            else:
                uv_map = 0
                for child in self.mesh_list:
                    if child.active_material.name == name:
                        uv_node = to_socket_from_socket.get(vector_node.inputs[1]).node
                        uv_names = [uv.name for uv in child.data.uv_layers]
                        if uv_node.uv_map in uv_names:
                            uv_map = uv_names.index(uv_node.uv_map)
                texture_flags |= 1 << 8 + uv_map

            # now mixing node data
            multiply_shading = mix_node.multi_shading
            mix_type = mix_node.blend_type
            col_2_multi = get_value(mix_node.inputs["Color 2 Multiplier"])
            if model_end == 'G':
                if multiply_shading:
                    texture_flags |= 1 << 6
                if mix_type == '.GNO_SUB' and image_stage == 0:
                    mix_number = 8
                else:
                    mix_types = {
                        '.GNO_MULTI': 1, '.GNO_DECAL': 2, '.GNO_REPLACE': 3, '.GNO_BLEND': 4,
                        '.GNO_PASSCOLOR': 5, '.GNO_ALPHATEX': 6, '.GNO_DECAL2': 7, '.GNO_SPEC': 9,
                        '.GNO_SPEC2': 10, '.GNO_ADD': 11, '.GNO_SUB': 12}
                    mix_number = mix_types[mix_type]
                texture_flags |= mix_number
            elif model_end == 'X':
                if mix_type == '.GNO_SUB' and image_stage == 0:
                    mix_number = 8
                else:
                    mix_types = {
                        '.GNO_MULTI': 1, '.GNO_DECAL': 2, '.GNO_REPLACE': 3, '.GNO_BLEND': 4,
                        '.GNO_DECAL2': 5, '.GNO_SPEC': 7,
                        '.GNO_SPEC2': 8, '.GNO_ADD': 9, '.GNO_SUB': 10}
                    mix_number = mix_types[mix_type]
                if multiply_shading:
                    xno_stupid = texture_flags
                    xno_stupid |= mix_number
                    m_texture_list.append(
                        NNTexture(image_node, image_index, xno_stupid, uv_offset, col_2_multi, lod_bias,
                                  max_mip_map_level, interp_min, interp_mag))
                    texture_flags |= 6
                else:
                    texture_flags |= mix_number

            m_texture_list.append(NNTexture(image_node, image_index, texture_flags, uv_offset, col_2_multi, lod_bias,
                                            max_mip_map_level, interp_min, interp_mag))

            mix_node = from_socket_to_socket.get(mix_node.outputs[0], False).node
            image_stage += 1

        # not texture stuff
        blend_method = material.blend_method
        backface_off = material.use_backface_culling

        diffuse = get_list(start_node.inputs["Material Color"])
        alpha = get_value(start_node.inputs["Material Alpha"])
        unlit = start_node.unshaded
        has_spec = start_node.use_specular
        ambient = get_list(start_node.inputs["Ambient"])
        specular = get_list(start_node.inputs["Specular"])
        shininess = get_value(start_node.inputs["Specular Gloss"])
        specular_value = get_value(start_node.inputs["Specular Level"])
        emission = get_value(start_node.inputs["Emission"])  # exists on all nodes as a standard

        v_col_node = to_socket_from_socket.get(start_node.inputs["Vertex Color"], False)
        v_col = -1
        if v_col_node and v_col_node.node.layer_name != "":
            v_col = v_col_node.node.layer_name
            for child in self.mesh_list:
                if child.active_material.name == name:
                    v_col_names = [col_set.name for col_set in child.data.color_attributes]
                    if v_col in v_col_names:
                        v_col = v_col_names.index(v_col)

        nn_shader = mix_node
        user = int(get_value(nn_shader.inputs["User"]))
        callback = get_value(nn_shader.inputs["Callback"])
        dis_fog = get_value(nn_shader.inputs["Disable Fog"])

        if self.settings.over_texture:
            texture_list = dict()
            for i in range(self.armature.data.nn_texture_count):
                tex = self.armature.data.nn_textures[i]
                texture_list[tex.texture.filepath] = (tex.interp_min, tex.interp_mag)
            # self.settings.riders_default: if i support this then i have to add one to original index..

        mat_flags = 0
        if model_end == 'G':
            buff_comp = not nn_shader.buff_comp
            buff_update = not nn_shader.buff_update
            blend_type = int(nn_shader.blend_type)
            source_fact = int(nn_shader.source_fact)
            dest_fact = int(nn_shader.dest_fact)
            blend_op = int(nn_shader.blend_op)
            z_mode = int(nn_shader.z_mode)
            ref0 = int(nn_shader.alpha_ref0)
            ref1 = int(nn_shader.alpha_ref1)
            comp0 = int(nn_shader.alpha_comp0)
            comp1 = int(nn_shader.alpha_comp1)
            alpha_op = int(nn_shader.alpha_op)

            if v_col == 0:
                mat_flags |= 1 << 0
            if not backface_off:
                # value is set if material is doublesided
                mat_flags |= 1 << 1
            # if value is true it will equate to 1, if its false itll be 0 no need for if statement
            mat_flags |= dis_fog << 5
            mat_flags |= unlit << 8
            mat_flags |= buff_comp << 16
            mat_flags |= buff_update << 17
            if blend_method == "CLIP":  # cutout
                mat_flags |= 1 << 18
            mat_flags |= has_spec << 24
            mat_flags |= callback << 31
            material_list.append(MegaShader(
                name, blend_method, diffuse, alpha, mat_flags,
                ambient, specular, shininess, specular_value, emission, user, m_texture_list,
                blend_type=blend_type, source_fact=source_fact, dest_fact=dest_fact, blend_op=blend_op, z_mode=z_mode,
                ref0=ref0, ref1=ref1, comp0=comp0, comp1=comp1, alpha_op=alpha_op,
            ))
        elif model_end == 'X':
            buffer_blend = nn_shader.buffer_blend
            blend_op = int(nn_shader.blend_op)
            source_fact = int(nn_shader.source_fact)
            dest_fact = int(nn_shader.dest_fact)
            blend_logic = int(nn_shader.blend_logic)
            blend_color = nn_shader.blend_color
            alpha_test = nn_shader.alpha_test
            test_mode = int(nn_shader.test_mode)
            alpha_ref = nn_shader.alpha_ref
            buff_comp = nn_shader.buff_comp
            z_mode = int(nn_shader.z_mode)
            buff_update = nn_shader.buff_update
            shader_file = nn_shader.shader_file
            shader_name = nn_shader.shader_name

            if not backface_off:
                # value is set if material is doublesided
                mat_flags |= 1 << 1
            mat_flags |= unlit << 2
            mat_flags |= dis_fog << 3
            if v_col >= 0:
                mat_flags |= 1 << 4
            mat_flags |= no_uv_transform << 5
            mat_flags |= has_spec << 24
            mat_flags |= callback << 31
            material_list.append(MegaShader(
                name, blend_method, diffuse, alpha, mat_flags,
                ambient, specular, shininess, specular_value, emission, user, m_texture_list,
                blend_type=blend_logic, source_fact=source_fact, dest_fact=dest_fact, blend_op=blend_op, z_mode=z_mode,
                comp0=test_mode, ref0=alpha_ref, shader_file=shader_file, shader_name=shader_name,
                blend_color=blend_color, alpha_test=alpha_test, buffer_blend=buffer_blend, buff_comp=buff_comp,
                buff_update=buff_update
            ))

    mat_end = []
    for i, mat in enumerate(material_list):
        if mat.blend_method == "BLEND" or mat.blend_method == "CLIP":
            mat_end.append(i)
    for i in reversed(mat_end):
        material_list.append(material_list.pop(i))
    if self.settings.over_material:
        mat_name_list = [a.name for a in material_list]
        new_materials = [None for _ in material_list]
        for i in range(self.armature.data.nn_material_count):
            mat_index = mat_name_list.index(self.armature.data.nn_materials[i].material.name)
            new_materials[i] = material_list[mat_index]
        material_list = new_materials
    return MaterialList(mat_type, material_list, texture_list)
