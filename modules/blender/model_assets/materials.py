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
    node.texture_mapping.scale = [settings.scale[0], settings.scale[1], 1]
    return node


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


def _normal(tree, image, settings, skip_textures):
    image.name = "NormalTexture"
    if not skip_textures:
        image.image.colorspace_settings.name = 'Non-Color'
    node = tree.nodes.new(type="ShaderNodeNormalMap")
    tree.links.new(node.inputs["Color"], image.outputs["Color"])
    node.space = settings.space
    return node.outputs["Normal"]


def _bump(tree, image):
    image.name = "BumpTexture"
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
        texture_name = make_bpy_textures(file_path, texture_name, self.settings.recursive_textures)
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

        if model_format[-1] == "G":
            bpy.context.scene.eevee.use_bloom = True
            gno_shader = tree.nodes.new('ShaderNodeGroup')
            gno_shader.node_tree = bpy.data.node_groups['NN Shader']

            if m.unshaded:
                gno_shader.inputs["Unshaded"].default_value = 1
            if m.black_alpha:
                gno_shader.inputs["Black is alpha"].default_value = 1

            gno_shader.inputs["Ambient"].default_value = m_col.ambient
            gno_shader.inputs["Specular"].default_value = m_col.specular
            gno_shader.inputs["Emission"].default_value = m_col.emission
            gno_shader.inputs["Specular Gloss"].default_value = m_col.shininess
            gno_shader.inputs["Specular Level"].default_value = m_col.specular_value

            colour_init = tree.nodes.new('ShaderNodeGroup')
            colour_init.node_tree = bpy.data.node_groups['NN Colour Init']

            colour_init.inputs["Material Colour"].default_value = m_col.diffuse
            colour_init.inputs["Material Alpha"].default_value = m_col.diffuse[-1]

            if m.v_colour:
                node = tree.nodes.new(type="ShaderNodeVertexColor")
                tree.links.new(colour_init.inputs["Vertex Colour"], node.outputs[0])
                tree.links.new(colour_init.inputs["Vertex Alpha"], node.outputs[1])

            tree.links.new(tree.nodes["Material Output"].inputs[0], gno_shader.outputs[0])

            diff_col = colour_init.outputs["Diffuse Colour"]
            diff_alpha = colour_init.outputs["Diffuse Alpha"]
            spec_col = False
            diff_end_connected = False
            diff_end_image = False
            diff_end_mix = False

            for t_index in range(m_texture_count):
                m_tex = m.texture[t_index]
                m_tex_type = m_tex.type
                m_tex_index = m_tex.index
                m_mix = m_tex.texture_flags

                if skip_textures:
                    image_node = _make_image(tree, None, m_tex)
                else:
                    image_node = _make_image(tree, texture_name[m_tex_index], m_tex)

                if m_mix.reflection:
                    node = tree.nodes.new('ShaderNodeGroup')
                    node.node_tree = bpy.data.node_groups['NN Reflection']
                    tree.links.new(image_node.inputs[0], node.outputs[0])
                elif m_mix.reflection_2 and not m_mix.mix:
                    node = tree.nodes.new('ShaderNodeGroup')
                    node.node_tree = bpy.data.node_groups['NN Reflection']
                    tree.links.new(image_node.inputs[0], node.outputs[0])
                    # black knight gives me so much pain
                elif m_mix.uv1:
                    node = tree.nodes.new(type="ShaderNodeUVMap")
                    node.uv_map = model_name_strip + "_UV1_Map"
                    tree.links.new(image_node.inputs[0], node.outputs[0])
                elif m_mix.uv2:
                    node = tree.nodes.new(type="ShaderNodeUVMap")
                    node.uv_map = model_name_strip + "_UV2_Map"
                    tree.links.new(image_node.inputs[0], node.outputs[0])
                elif m_mix.uv3:
                    node = tree.nodes.new(type="ShaderNodeUVMap")
                    node.uv_map = model_name_strip + "_UV3_Map"
                    tree.links.new(image_node.inputs[0], node.outputs[0])
                elif m_mix.uv4:
                    node = tree.nodes.new(type="ShaderNodeUVMap")
                    node.uv_map = model_name_strip + "_UV4_Map"
                    tree.links.new(image_node.inputs[0], node.outputs[0])

                if m_mix.specular:  # specular doesnt mix with any
                    spec_col = image_node.outputs[0]
                elif m_mix.unknown1 and m_mix.reflection_2:
                    for link in tree.links:
                        if link.to_node.name == mix_node.name and link.to_socket.name == "Colour 2":
                            spec_col = link.from_node.outputs[0]
                            tree.links.remove(link)
                            break
                    tree.links.new(mix_node.inputs["Colour 2"], image_node.outputs[0])
                else:
                    mix_node = tree.nodes.new('ShaderNodeNNMixRGB')
                    mix_type = "0"
                    if m_mix.multiply:
                        mix_type = "0"
                    elif m_mix.mix:
                        mix_type = "1"
                    elif m_mix.add:
                        mix_type = "2"
                    elif m_mix.add_branch:
                        mix_type = "2"
                    elif m_mix.subtract:
                        mix_type = "3"
                    elif m_mix.unknown1 and not m_mix.reflection_2:
                        mix_type = "1"
                    mix_node.blend_type = mix_type

                    mix_node.inputs["Colour 2 Multiplier"].default_value = m_tex.alpha

                    tree.links.new(mix_node.inputs["Colour 1"], diff_col)
                    tree.links.new(mix_node.inputs["Alpha 1"], diff_alpha)

                    diff_col = mix_node.outputs["Colour"]
                    diff_alpha = mix_node.outputs["Alpha"]

                    if diff_end_image:
                        tree.links.new(mix_node.inputs["Colour 1"], diff_end_image.outputs[0])
                        tree.links.new(mix_node.inputs["Alpha 1"], diff_end_image.outputs[1])
                        tree.links.new(diff_end_mix.inputs["Colour 2"], mix_node.outputs[0])
                        tree.links.new(diff_end_mix.inputs["Alpha 2"], mix_node.outputs[1])
                        diff_end_image = False

                    if m_mix.add_branch:
                        diff_end_image = image_node
                        diff_end_mix = mix_node
                        diff_end_connected = True
                        tree.links.new(gno_shader.inputs["Colour"], diff_col)
                        tree.links.new(gno_shader.inputs["Alpha"], diff_alpha)
                    else:
                        tree.links.new(mix_node.inputs["Colour 2"], image_node.outputs[0])
                        tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])

            if not diff_end_connected:
                tree.links.new(gno_shader.inputs["Colour"], diff_col)
                tree.links.new(gno_shader.inputs["Alpha"], diff_alpha)
            if spec_col:
                tree.links.new(gno_shader.inputs["Specular"], spec_col)

        else:

            # noinspection SpellCheckingInspection
            n_end = tree.nodes.new(type="ShaderNodeEeveeSpecular")
            n_end.inputs["Roughness"].default_value = 0.5

            tree.links.new(tree.nodes["Material Output"].inputs["Surface"], n_end.outputs["BSDF"])

            for t_index in range(m_texture_count):
                m_tex = m.texture[t_index]
                m_tex_type = m_tex.type
                m_tex_index = m_tex.index

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
                displacement = _normal(tree, image_node, m_tex, skip_textures)
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
        texture_name = make_bpy_textures(file_path, texture_name, self.settings.recursive_textures)
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
        material.blend_method = m.transparency

        colour = False
        diffuse = tree.nodes["Principled BSDF"]

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_type = m_tex.type
            m_tex_index = m_tex.index

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
                displacement = _normal(tree, image_node, m_tex, skip_textures)

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


def make_bpy_textures(file_path: str, texture_names: list, recursive: bool):  # get textures if they exist
    # Imports textures to Blender, returns the loaded texture names.
    path_base = pathlib.Path(pathlib.Path(file_path).parent)
    tex_names = [tex.rsplit(".", 1)[0] for tex in texture_names]

    if recursive:
        path_list_dds = [[str(path) for path in path_base.rglob(tex + ".dds")] for tex in tex_names]
        path_list_png = [[str(path) for path in path_base.rglob(tex + ".png")] for tex in tex_names]
    else:
        path_list_dds = [[str(path) for path in path_base.glob(tex + ".dds")] for tex in tex_names]
        path_list_png = [[str(path) for path in path_base.glob(tex + ".png")] for tex in tex_names]

    dds_check = [bool(a) for a in path_list_dds]
    if False not in dds_check:
        return [bpy.data.images.load(tex[0]) for tex in path_list_dds]
    png_check = [bool(a) for a in path_list_png]
    if False not in png_check:
        return [bpy.data.images.load(tex[0]) for tex in path_list_png]
    return texture_names


@dataclass
class MaterialList:
    material_list: list
    texture_list: list


@dataclass
class Mat:
    name: str
    rgb: list
    alpha: float
    texture_list: list
    # the 01 not set in 01 00 00 00 =
    # yes colour, yes the one after, no the one after, no to the int, yes to the float (ordered)
    #  so no highlights
    v_col: bool  # 00 00 00 01
    unlit: bool  # 00 00 01 00
    boolean: bool  # 00 02 00 00
    # if alpha and texture: 01 00 00 02 ?


def get_materials(self):
    obj: Object = self.armature
    material_names = []
    material_list = []
    texture_list = []

    @dataclass
    class Texture:
        __slots__ = ["type", "name"]
        type: str
        name: str

    if self.settings.riders_default:
        class ImageFake:
            class image:
                filepath = "bd_15.png"
        # we have to parse blenders image path data later... (bpy.path.basename(node.image.filepath))
        #  so we will fake it because the image won't actually be loaded into blender
        texture_list = ["bd_15.png"]

    for child in self.mesh_list:
        child: Object
        material_name = child.active_material.name
        if material_name not in material_names:
            material_names.append(material_name)

    material_names.sort()

    for material in material_names:
        name = material
        material = bpy.data.materials[material]
        material.use_nodes = True
        m_texture_list = []
        rgb = (0.7529413, 0.7529413, 0.7529413, 1.0)
        alpha = 1.0
        # todo maybe theres a way to see all the links? like its just a list of links
        # todo oh maybe I can see what fbx exporter does for materials
        # todo but i forgot to actually store and use data type settings
        # 😔
        # need to make the material import useless data to rewrite it and need to make materials parse correctly somehow
        # todo bpy.data.materials['sha06_Material_0001'].node_tree.nodes["Specular BSDF"].inputs[4].links[0].from_socket
        #  matLinks = mat.node_tree.links might help too?

        #     for ob_obj in objects:
        #         # If obj is not a valid object for materials, wrapper will just return an empty tuple...
        #         for ma_s in ob_obj.material_slots:
        #             ma = ma_s.material
        #             if ma is None:
        #                 continue  # Empty slots!

        for mat in material.node_tree.nodes[::]:
            # check if we read this type, if this image node actually has a texture
            if mat.name == "DiffuseTexture" and mat.image:
                m_texture_list.append(Texture("DiffuseTexture", mat))
                if mat.image and mat.image.filepath not in texture_list:
                    texture_list.append(mat.image.filepath)
            elif mat.name == "ReflectionTexture" and mat.image:
                m_texture_list.append(Texture("ReflectionTexture", mat))
                if mat.image.filepath not in texture_list:
                    texture_list.append(mat.image.filepath)
            elif mat.name == "EmissionTexture" and mat.image:
                m_texture_list.append(Texture("EmissionTexture", mat))
                if mat.image.filepath not in texture_list:
                    texture_list.append(mat.image.filepath)
            elif mat.name == "RGB":
                rgb = mat.outputs[0].default_value[::]
            elif mat.name == "Value":
                alpha = mat.outputs[0].default_value
        material_list.append(Mat(name, rgb, alpha, m_texture_list, False, False, False))
    return MaterialList(material_list, texture_list)
