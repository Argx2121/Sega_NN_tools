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


def _make_image_vect(tree, image, settings):
    vect = tree.nodes.new(type="ShaderNodeGNOVector")
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


def material_gno(self):
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
        texture_name = make_bpy_textures(file_path, texture_name, self.settings.recursive_textures,
                                         self.settings.load_incomplete)

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
        tree.nodes.remove(tree.nodes["Principled BSDF"])

        mat_flags = m.mat_flags

        bpy.context.scene.eevee.use_bloom = True
        gno_shader = tree.nodes.new('ShaderNodeGNOShader')
        colour_init = tree.nodes.new('ShaderNodeGNOShaderInit')

        colour_init.inputs["Material Color"].default_value = m_col.diffuse
        colour_init.inputs["Material Alpha"].default_value = m_col.diffuse[-1]

        v_col = mat_flags & 1
        backface_off = mat_flags >> 5 & 1
        unlit = mat_flags >> 8 & 1  # (bloom) slash unlit
        ignore_depth = mat_flags >> 16 & 1  # ignores depth
        dont_write_depth = mat_flags >> 17 & 1  # doesn't write depth
        # cutout = mat_flags >> 18 & 1  # data is specified in meshes, we don't need to use this flag
        has_spec = mat_flags >> 24 & 1

        if backface_off:
            material.use_backface_culling = False

        if v_col:
            node = tree.nodes.new(type="ShaderNodeVertexColor")
            tree.links.new(colour_init.inputs["Vertex Color"], node.outputs[0])
            tree.links.new(colour_init.inputs["Vertex Alpha"], node.outputs[1])

        if unlit:
            colour_init.inputs["Unshaded"].default_value = 1
        if ignore_depth:
            gno_shader.inputs["Ignore Depth"].default_value = 1
        if dont_write_depth:
            gno_shader.inputs["Don't Write Depth"].default_value = 1

        colour_init.inputs["Ambient"].default_value = m_col.ambient
        colour_init.inputs["Specular"].default_value = m_col.specular
        colour_init.inputs["Specular Gloss"].default_value = m_col.shininess
        colour_init.inputs["Specular Level"].default_value = m_col.specular_value
        colour_init.inputs["Use Specular"].default_value = has_spec

        gno_shader.inputs["Mat Flags"].default_value = mat_flags
        gno_shader.blend_type = str(m.render.blend)  # setting the values of these changes no calculations
        gno_shader.source_fact = str(m.render.source)
        gno_shader.dest_fact = str(m.render.destination)
        gno_shader.blend_op = str(m.render.operation)
        gno_shader.z_mode = str(m.render.z_mode)
        gno_shader.inputs["Alpha ref0"].default_value = m.render.ref0
        gno_shader.inputs["Alpha ref1"].default_value = m.render.ref1
        gno_shader.alpha_comp0 = str(m.render.comp0)
        gno_shader.alpha_comp1 = str(m.render.comp1)
        gno_shader.alpha_op = str(m.render.alpha)
        gno_shader.inputs["User"].default_value = m.user

        tree.links.new(tree.nodes["Material Output"].inputs[0], gno_shader.outputs[0])
        last_node = colour_init

        for t_index in range(m_texture_count):
            m_tex = m.texture[t_index]
            m_tex_index = m_tex.index
            m_mix = m_tex.texture_flags

            if skip_textures:
                vector_node, image_node = _make_image_vect(tree, None, m_tex)
            else:
                vector_node, image_node = _make_image_vect(tree, texture_name[m_tex_index], m_tex)

            if not m_mix.ignore_uv_offset:
                vector_node.inputs["UV Offset"].default_value = (m_tex.scale[0], (- m_tex.scale[1]) + 1, 0.0)

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

            if m_mix.reflection:
                vector_node.inputs["Reflection Vector"].default_value = True
            elif m_mix.uv1:
                node = tree.nodes.new(type="ShaderNodeUVMap")
                node.uv_map = model_name_strip + "_UV1_Map"
                tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
            elif m_mix.uv2:
                node = tree.nodes.new(type="ShaderNodeUVMap")
                node.uv_map = model_name_strip + "_UV2_Map"
                tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
            elif m_mix.uv3:
                node = tree.nodes.new(type="ShaderNodeUVMap")
                node.uv_map = model_name_strip + "_UV3_Map"
                tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])
            elif m_mix.uv4:
                node = tree.nodes.new(type="ShaderNodeUVMap")
                node.uv_map = model_name_strip + "_UV4_Map"
                tree.links.new(vector_node.inputs["UV Map"], node.outputs[0])

            # onwards my mixnodes
            if m_mix.specular or m_mix.specular2:
                mix_type = "_NN_RGB_SPEC"
                if m_mix.specular2:
                    mix_type = "_NN_RGB_SPEC_2"
                mix_node = tree.nodes.new('ShaderNodeGNOSpecular')
                mix_node.blend_type = mix_type

                tree.links.new(mix_node.inputs["Specular"], colour_init.outputs["Specular"])
                tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
                tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
                last_node = mix_node
            else:
                mix_node = tree.nodes.new('ShaderNodeGNOMixRGB')
                mix_type = "_NN_RGB_MULTI"
                if m_mix.multiply:
                    mix_type = "_NN_RGB_MULTI"
                elif m_mix.decal:
                    mix_type = "_NN_RGB_DECAL"
                elif m_mix.replace:
                    mix_type = "_NN_RGB_REPLACE"
                elif m_mix.blend:
                    mix_type = "_NN_RGB_BLEND"
                elif m_mix.pass_clear:
                    mix_type = "_NN_RGB_PASS"
                elif m_mix.alpha_tex:
                    mix_type = "_NN_RGB_ALPHA"
                elif m_mix.decal_2:
                    mix_type = "_NN_RGB_DECAL_2"
                elif m_mix.subtract:
                    mix_type = "_NN_RGB_SUB"
                elif m_mix.add:
                    mix_type = "_NN_RGB_ADD"
                elif m_mix.subtract_2:
                    mix_type = "_NN_RGB_SUB"
                mix_node.blend_type = mix_type

                tree.links.new(mix_node.inputs["Color 1"], last_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 1"], last_node.outputs[1])
                tree.links.new(mix_node.inputs["Color 2"], image_node.outputs[0])
                tree.links.new(mix_node.inputs["Alpha 2"], image_node.outputs[1])
                last_node = mix_node

            if m_mix.multiply_shading:
                mix_node.multi_shading = True
            mix_node.inputs["Color 2 Multiplier"].default_value = m_tex.alpha

        tree.links.new(gno_shader.inputs["Color"], last_node.outputs[0])
        tree.links.new(gno_shader.inputs["Alpha"], last_node.outputs[1])


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
        texture_name = make_bpy_textures(file_path, texture_name, self.settings.recursive_textures,
                                         self.settings.load_incomplete)

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

        mat_flags = m.mat_flags

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
        texture_name = make_bpy_textures(file_path, texture_name, self.settings.recursive_textures,
                                         self.settings.load_incomplete)

    for mat_index in range(material_count):
        material = bpy.data.materials.new(mat_names[mat_index])
        material_list_blender.append(material)
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


def make_bpy_textures(file_path: str, texture_names: list, recursive: bool, load_incomplete: bool):
    # Finds textures and imports them to Blender (if applicable)
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

    if load_incomplete:
        png_incomp = []
        for (t_check, tex) in zip(png_check, path_list_png):
            if t_check:
                png_incomp.append(bpy.data.images.load(tex[0]))
            else:
                png_incomp.append(None)
        return png_incomp

    return [None for _ in texture_names]


@dataclass
class MaterialList:
    simple: bool
    material_list: list
    texture_list: list


@dataclass
class MatGNOSimple:
    name: str
    blend_method: str
    v_col: bool
    unlit: bool
    boolean: bool
    diffuse: list
    alpha: float
    texture_list: list


@dataclass
class MatGNOComplex:
    name: str
    blend_method: str
    override_mat: bool
    mat_flags: int
    diffuse: list
    alpha: float
    v_col: str  # storing number as str
    backface_off: bool
    unlit: bool
    ignore_depth: bool
    dont_write_depth: bool
    has_spec: bool
    ambient: list
    specular: list
    shininess: float
    specular_value: float
    blend_type: int
    source_fact: int
    dest_fact: int
    blend_op: int
    z_mode: int
    ref0: int
    ref1: int
    comp0: int
    comp1: int
    alpha_op: int
    user: int
    texture_list: list


@dataclass
class GnoTexture:
    name: str
    reflection: bool
    uv_map: int
    u_wrap: int
    v_wrap: int
    uv_offset: list
    multiply_shading: bool
    col_2_multi: float
    mix_type: str


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
        node_types = [node.bl_idname for node in material.node_tree.nodes]
        mat_type = True
        if "ShaderNodeGNOShader" in node_types:
            def get_list(node_input):
                node_to_work_on = to_socket_from_socket.get(node_input, node_input)
                return node_to_work_on.default_value[::]

            def get_value(node_input):
                node_to_work_on = to_socket_from_socket.get(node_input, node_input)
                return node_to_work_on.default_value

            mat_type = False
            from_socket_to_socket = dict([[link.from_socket, link.to_socket] for link in material.node_tree.links])
            to_socket_from_socket = dict([[link.to_socket, link.from_socket] for link in material.node_tree.links])
            for node in material.node_tree.nodes[::]:
                if node.bl_idname == "ShaderNodeGNOShaderInit":
                    start_node = node
                    break
            blend_method = material.blend_method
            backface_off = material.use_backface_culling

            diffuse = get_list(start_node.inputs["Material Color"])
            alpha = get_value(start_node.inputs["Material Alpha"])
            unlit = get_value(start_node.inputs["Unshaded"])
            has_spec = get_value(start_node.inputs["Use Specular"])
            ambient = get_list(start_node.inputs["Ambient"])
            specular = get_list(start_node.inputs["Specular"])
            shininess = get_value(start_node.inputs["Specular Gloss"])
            specular_value = get_value(start_node.inputs["Specular Level"])
            v_col_node = to_socket_from_socket.get(start_node.inputs["Vertex Color"], False)
            if v_col_node and v_col_node.node.layer_name != "":
                v_col = v_col_node.node.layer_name
                for child in self.mesh_list:
                    if child.active_material.name == name:
                        v_col_names = [col_set.name for col_set in child.data.color_attributes]
                        if v_col in v_col_names:
                            v_col = v_col_names.index(v_col)
                        elif len(v_col_names) > 0:
                            v_col = 0
            else:
                v_col = -1

            mix_node = from_socket_to_socket.get(start_node.outputs[0]).node

            while mix_node.bl_idname != "ShaderNodeGNOShader":
                # its time to get images
                multiply_shading = mix_node.multi_shading
                mix_type = mix_node.blend_type
                col_2_multi = get_value(mix_node.inputs["Color 2 Multiplier"])

                image_node = to_socket_from_socket.get(mix_node.inputs[2]).node
                texture_list.append(image_node.image.filepath)

                vector_node = to_socket_from_socket.get(image_node.inputs[0]).node
                u_wrap = int(vector_node.u_type)
                v_wrap = int(vector_node.v_type)
                reflection = vector_node.inputs["Reflection Vector"].default_value
                uv_offset = get_list(vector_node.inputs["UV Offset"])

                uv_map = -1

                if not reflection:
                    for child in self.mesh_list:
                        if child.active_material.name == name:
                            uv_node = to_socket_from_socket.get(vector_node.inputs[1]).node
                            uv_names = [uv.name for uv in child.data.uv_layers]
                            if uv_node.uv_map in uv_names:
                                uv_map = uv_names.index(uv_node.uv_map)
                            elif len(uv_names) > 0:
                                uv_map = 0

                m_texture_list.append(GnoTexture(image_node, reflection, uv_map, u_wrap,
                                                 v_wrap, uv_offset, multiply_shading, col_2_multi, mix_type))

                mix_node = from_socket_to_socket.get(mix_node.outputs[0], False).node

            gno_shader = mix_node

            ignore_depth = get_value(gno_shader.inputs["Ignore Depth"])
            dont_write_depth = get_value(gno_shader.inputs["Don't Write Depth"])
            mat_flags = get_value(gno_shader.inputs["Mat Flags"])
            override_mat = get_value(gno_shader.inputs["Override Flags"])
            blend_type = int(gno_shader.blend_type)
            source_fact = int(gno_shader.source_fact)
            dest_fact = int(gno_shader.dest_fact)
            blend_op = int(gno_shader.blend_op)
            z_mode = int(gno_shader.z_mode)
            ref0 = get_value(gno_shader.inputs["Alpha ref0"])
            ref1 = get_value(gno_shader.inputs["Alpha ref1"])
            comp0 = int(gno_shader.alpha_comp0)
            comp1 = int(gno_shader.alpha_comp1)
            alpha_op = int(gno_shader.alpha_op)
            user = int(get_value(gno_shader.inputs["User"]))

            texture_list = list(set(texture_list))
            material_list.append(
                MatGNOComplex(name, blend_method, override_mat, mat_flags, diffuse, alpha, v_col, backface_off, unlit,
                              ignore_depth, dont_write_depth, has_spec, ambient, specular, shininess, specular_value,
                              blend_type, source_fact, dest_fact, blend_op, z_mode, ref0, ref1, comp0, comp1, alpha_op,
                              user, m_texture_list))
        else:
            for mat in material.node_tree.nodes[::]:
                blend_method = mat.blend_method
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
                material_list.append(MatGNOSimple(name, blend_method, False, False, False, rgb, alpha, m_texture_list))
    return MaterialList(mat_type, material_list, texture_list)
