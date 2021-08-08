import bpy
import os
import pathlib
from platform import system


def _make_image(tree, image, settings):
    node = tree.nodes.new(type="ShaderNodeTexImage")
    node.image = image
    if "clamp" in settings:
        node.extension = "EXTEND"
    return node


def _mix_rgb(tree, input_1, input_2):
    node = tree.nodes.new(type="ShaderNodeMixRGB")
    node.inputs[0].default_value = 1
    node.blend_type = 'MULTIPLY'
    tree.links.new(node.inputs[1], input_1)
    tree.links.new(node.inputs[2], input_2)
    return node.outputs[0]


def _mix_colour_reflection(tree, input_1, input_2):
    node = tree.nodes.new(type="ShaderNodeMixRGB")
    # node.blend_type = 'MIX'
    tree.links.new(node.inputs[1], input_1)
    tree.links.new(node.inputs[2], input_2)
    return node.outputs[0]


def _vertex_colours(tree, name):
    node = tree.nodes.new(type="ShaderNodeVertexColor")
    node.layer_name = name + "_Vertex_Colours"
    return node.outputs[0]


def _diffuse_rgba(tree, image, rgba, skip_textures):
    rbg = tree.nodes.new(type="ShaderNodeRGB")
    rbg.outputs[0].default_value = (rgba.colour[0], rgba.colour[1], rgba.colour[2], 1)

    alpha = tree.nodes.new(type="ShaderNodeValue")
    alpha.outputs[0].default_value = rgba.alpha

    # image alpha - (rgba alpha * -1 + 1), clamped
    multiply_add = tree.nodes.new(type="ShaderNodeMath")
    multiply_add.operation = 'MULTIPLY_ADD'

    subtract = tree.nodes.new(type="ShaderNodeMath")
    subtract.operation = 'SUBTRACT'
    subtract.use_clamp = True

    tree.links.new(multiply_add.inputs[0], alpha.outputs[0])
    multiply_add.inputs[1].default_value = -1
    multiply_add.inputs[2].default_value = 1

    if not skip_textures:
        tree.links.new(subtract.inputs[0], image.outputs[1])
    else:
        subtract.inputs[0].default_value = 1

    alpha_invert = tree.nodes.new(type="ShaderNodeInvert")
    tree.links.new(alpha_invert.inputs[1], subtract.outputs[0])

    tree.links.new(subtract.inputs[1], multiply_add.outputs[0])

    return _mix_rgb(tree, image.outputs[0], rbg.outputs[0]), alpha_invert.outputs[0]


def _rgba(tree, rgba):
    rbg = tree.nodes.new(type="ShaderNodeRGB")
    rbg.outputs[0].default_value = (rgba.colour[0], rgba.colour[1], rgba.colour[2], 1)

    alpha = tree.nodes.new(type="ShaderNodeValue")
    alpha.outputs[0].default_value = rgba.alpha
    alpha_invert = tree.nodes.new(type="ShaderNodeInvert")
    tree.links.new(alpha_invert.inputs[1], alpha.outputs[0])

    return rbg.outputs[0], alpha_invert.outputs[0]


def _reflection(tree, image):
    node = tree.nodes.new(type="ShaderNodeTexCoord")
    tree.links.new(image.inputs[0], node.outputs[6])
    return image.outputs[0]


def _normal(tree, image, settings, skip_textures):
    if not skip_textures:
        image.image.colorspace_settings.name = 'Non-Color'
    node = tree.nodes.new(type="ShaderNodeNormalMap")
    tree.links.new(node.inputs[1], image.outputs[0])
    if "world" in settings:
        node.space = 'WORLD'
    return node.outputs[0]


def _bump(tree, image):
    image.image.colorspace_settings.name = 'Non-Color'
    node = tree.nodes.new(type="ShaderNodeBump")
    tree.links.new(node.inputs[2], image.outputs[0])
    return node.outputs[0]


def material_complex(self):
    texture_name = self.texture_names
    material_count = self.model.info.material_count
    mat_names = self.mat_names
    material_list_blender = self.material_list_blender
    material_list = self.model.materials
    model_name_strip = self.model_name_strip

    skip_textures = False

    if not texture_name:
        skip_textures = True
    elif texture_name:
        texture_name = make_bpy_textures(texture_name, self.settings.recursive_textures)
        if type(texture_name[0]) == str:
            skip_textures = True

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)

        m = material_list[mat_index]
        m_texture_count = m.texture_count
        m_col = m.colour
        material.use_nodes = True
        tree = material.node_tree

        material.blend_method = "HASHED"
        material.show_transparent_back = False
        # ideally transparency would only be used if needed but there isn't a way to tell at the moment
        # show_transparent_back is usually needed off however if used on shadows 06 model it messes up the normals
        # if black means transparent and the image has gradients, separate hsv -> image input, v output
        tree.nodes.remove(tree.nodes["Principled BSDF"])

        # noinspection SpellCheckingInspection
        n_end = tree.nodes.new(type="ShaderNodeEeveeSpecular")
        n_end.inputs[2].default_value = 0.5

        tree.links.new(tree.nodes["Material Output"].inputs[0], n_end.outputs[0])

        colour = False
        alpha = 1
        reflection = False

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_type = m_tex.type
            m_tex_set = m_tex.setting
            m_tex_index = m_tex.index

            if m_tex_type == "none":
                continue

            if skip_textures:
                image_node = _make_image(tree, None, m_tex_set)
            else:
                image_node = _make_image(tree, texture_name[m_tex_index], m_tex_set)

            if m_tex_type == "diffuse":
                colour, alpha = _diffuse_rgba(tree, image_node, m_col, skip_textures)
                vertex_colours = _vertex_colours(tree, model_name_strip)
                colour = _mix_rgb(tree, colour, vertex_colours)
            elif m_tex_type == "normal":
                displacement = _normal(tree, image_node, m_tex_set, skip_textures)
                tree.links.new(n_end.inputs[5], displacement)
            elif m_tex_type == "emission":
                tree.links.new(n_end.inputs[3], image_node.outputs[0])
            elif m_tex_type == "reflection":
                reflection = _reflection(tree, image_node)
            elif m_tex_type == "bump":
                displacement = _bump(tree, image_node)
                tree.links.new(n_end.inputs[5], displacement)
            elif m_tex_type == "spectacular":
                tree.links.new(n_end.inputs[1], image_node.outputs[0])

        if not colour:  # if a diffuse texture hasn't been found
            colour, alpha = _rgba(tree, m_col)
            vertex_colours = _vertex_colours(tree, model_name_strip)
            colour = _mix_rgb(tree, colour, vertex_colours)

        if reflection:
            colour = _mix_colour_reflection(tree, colour, reflection)
            # for some reason shadow 06 and probably other character models
            #  like eye reflection colour output for fac in transparency shader
            #  there isn't a way to determine if this needs to be set up though

        tree.links.new(n_end.inputs[0], colour)
        tree.links.new(n_end.inputs[4], alpha)


def material_simple(self):  # for exporting to fbx etc, so keep it simple.
    texture_name = self.texture_names
    material_count = self.model.info.material_count
    mat_names = self.mat_names
    material_list_blender = self.material_list_blender
    material_list = self.model.materials
    model_name_strip = self.model_name_strip

    skip_textures = False

    if not texture_name:
        skip_textures = True
    elif texture_name:
        texture_name = make_bpy_textures(texture_name, self.settings.recursive_textures)
        if type(texture_name[0]) == str:
            skip_textures = True

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)

        m = material_list[mat_index]
        m_texture_count = m.texture_count
        m_col = m.colour
        material.use_nodes = True
        tree = material.node_tree

        colour = False

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_type = m_tex.type
            m_tex_set = m_tex.setting
            m_tex_index = m_tex.index

            diffuse = tree.nodes["Principled BSDF"]

            if m_tex_type == "none":
                continue

            if skip_textures:
                image_node = _make_image(tree, None, m_tex_set)
            else:
                image_node = _make_image(tree, texture_name[m_tex_index], m_tex_set)

            if m_tex_type == "diffuse":
                _rgba(tree, m_col)  # generate even if they cant be used
                _vertex_colours(tree, model_name_strip)

                colour = True

                tree.links.new(diffuse.inputs[0], image_node.outputs[0])
            elif m_tex_type == "normal":
                displacement = _normal(tree, image_node, m_tex_set, skip_textures)

                tree.links.new(diffuse.inputs[-3], displacement)
            elif m_tex_type == "emission":

                tree.links.new(diffuse.inputs[-5], image_node.outputs[0])
            elif m_tex_type == "bump":
                displacement = _bump(tree, image_node)

                tree.links.new(diffuse.inputs[-3], displacement)

        if not colour:  # if a diffuse texture hasn't been found
            _rgba(tree, m_col)
            _vertex_colours(tree, model_name_strip)


def _make_bpy_recursive(texture_names: list):
    has_png = True  # png shouldn't be used in game but converted image files might be .png
    has_dds = True
    path_base = pathlib.Path(bpy.path.abspath(texture_names[0]).rstrip(bpy.path.basename(texture_names[0])))

    path_list_dds = [str(path) for path in path_base.rglob("*.dds")]
    path_list_png = [str(path) for path in path_base.rglob("*.png")]
    dds_join = ', '.join(path_list_dds).casefold()
    png_join = ', '.join(path_list_png).casefold()

    texture_names = [bpy.path.basename(tex.split(".")[0]) for tex in texture_names]

    for name in texture_names:
        if name.casefold() not in png_join:
            has_png = False
            break
    for name in texture_names:
        if name.casefold() not in dds_join:
            has_dds = False
            break

    img_list = []

    if system() == "Windows":
        var = "\\"
    else:
        var = "/"

    if has_png:
        for name in texture_names:
            for path in path_list_png:
                if (var + name + ".").casefold() in path.casefold():
                    img_list.append(path)
                    break
        return [bpy.data.images.load(tex) for tex in img_list]
    elif has_dds:
        for name in texture_names:
            for path in path_list_dds:
                if (var + name + ".").casefold() in path.casefold():
                    img_list.append(path)
                    break
        return [bpy.data.images.load(tex) for tex in img_list]

    return texture_names


def _make_bpy_non_recursive(texture_names: list):
    has_png = True  # png shouldn't be used in game but converted image files might be .png
    has_dds = True

    for tex in texture_names:
        if not os.path.exists(tex[:-4] + ".png"):
            has_png = False
            break
    for tex in texture_names:
        if not os.path.exists(tex[:-4] + ".dds"):
            has_dds = False
            break

    if has_png:
        return [bpy.data.images.load(tex[:-4] + ".png") for tex in texture_names]
    elif has_dds:
        return [bpy.data.images.load(tex[:-4] + ".dds") for tex in texture_names]

    return texture_names


def make_bpy_textures(texture_names: list, recursive: bool):  # get textures if they exist
    # Imports textures to Blender, returns the loaded texture names.
    if recursive:
        return _make_bpy_recursive(texture_names)
    else:
        return _make_bpy_non_recursive(texture_names)
