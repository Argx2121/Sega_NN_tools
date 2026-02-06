import bpy
from ...modules.blender.model_assets.nodes import gno_mix, xno_mix, spec_mix, vector_mix, u_wrap_mix, v_wrap_mix


# UTIL
def custom_reg():
    # GENERIC
    bpy.types.Object.nn_frame_rate = bpy.props.IntProperty(name="Frame Rate", default=30, min=0, max=120, options=set())
    bpy.types.Object.nn_user_int = bpy.props.IntProperty(name="User Int", default=0)
    bpy.types.Object.nn_euler_rotation = bpy.props.EnumProperty(name="Euler Order", items=(
        ("XYZ", "XYZ Euler", "XYZ"), ("XZY", "XZY Euler", "XZY"), ("ZXY", "ZXY Euler", "ZXY")), default="XZY", options=set())
    # MODEL
    bpy.types.Armature.nn_material_count = bpy.props.IntProperty(name="Material Count", default=0, min=0, max=255, update=update_material_count)
    bpy.types.Armature.nn_materials = bpy.props.CollectionProperty(type=NNMaterial)
    bpy.types.Armature.nn_texture_count = bpy.props.IntProperty(name="Texture Count", default=0, min=0, max=255, update=update_texture_count)
    bpy.types.Armature.nn_textures = bpy.props.CollectionProperty(type=NNTexture)
    # BONES
    bpy.types.PoseBone.nn_user_type = bpy.props.EnumProperty(name="User Type", items=(
        ("nn_user_int", "User as an Int", "User as an Int"), ("nn_user_float", "User as a Float", "User as a Float")), default="nn_user_int")
    bpy.types.PoseBone.nn_user_int = bpy.props.IntProperty(name="User Int", default=0)
    bpy.types.PoseBone.nn_user_float = bpy.props.FloatProperty(name="User Float", default=0.0)
    bpy.types.PoseBone.nn_euler_rotation = bpy.props.EnumProperty(name="Euler Order", items=(
        ("XYZ", "XYZ Euler", "XYZ"), ("XZY", "XZY Euler", "XZY"), ("ZXY", "ZXY Euler", "ZXY")), default="XZY", options=set())
    bpy.types.PoseBone.nn_hide = (
        bpy.props.BoolProperty(name="Hide Bone", description="Hide Meshes weighted to only this bone",
                               update=hide_update, get=hide_get, set=hide_set, default=False))
    # it is required
    bpy.types.PoseBone.nn_hide_function = bpy.props.BoolProperty(
        name="Hide Function", update=hide_function_update, default=False, options={'HIDDEN'})
    bpy.types.PoseBone.nn_reset_scale_x = (
        bpy.props.BoolProperty(name="Reset scale z", description="Reset inherited x scale", default=False))
    bpy.types.PoseBone.nn_reset_scale_y = (
        bpy.props.BoolProperty(name="Reset scale y", description="Reset inherited y scale", default=False))
    bpy.types.PoseBone.nn_reset_scale_z = (
        bpy.props.BoolProperty(name="Reset scale z", description="Reset inherited z scale", default=False))

    bpy.types.PoseBone.nn_ik_effector = bpy.props.BoolProperty(name="IK Effector", default=False)
    bpy.types.PoseBone.nn_ik_minus_z = bpy.props.BoolProperty(name="IK Prefer rot -z", default=False)
    bpy.types.PoseBone.nn_ik_1bone_joint1 = bpy.props.BoolProperty(name="IK 1 Bone joint 1", default=False)
    bpy.types.PoseBone.nn_ik_2bone_joint1 = bpy.props.BoolProperty(name="IK 2 Bones joint 1", default=False)
    bpy.types.PoseBone.nn_ik_2bone_joint2 = bpy.props.BoolProperty(name="IK 2 Bones joint 2", default=False)
    bpy.types.PoseBone.nn_xsiik = bpy.props.BoolProperty(
        name="Use xsiik", description='Use xsiik over siik, only available in games from after 2009', default=False)
    bpy.types.PoseBone.nn_ik_1bone_root = bpy.props.BoolProperty(name="IK 1 Bone Root", description='xsiik', default=False)
    bpy.types.PoseBone.nn_ik_2bone_root = bpy.props.BoolProperty(name="IK 2 Bone Root", description='xsiik', default=False)

    bpy.types.PoseBone.nn_mesh_count = bpy.props.IntProperty(name="Mesh Count", default=0, min=0, max=255, update=update_mesh_count)
    bpy.types.PoseBone.nn_meshes = bpy.props.CollectionProperty(type=NNMesh)
    bpy.types.PoseBone.nn_euler_values = bpy.props.FloatVectorProperty(name="NN Init Euler", subtype='EULER')  # im killing you!!
    bpy.types.PoseBone.nn_scale_values = bpy.props.FloatVectorProperty(name="NN Init Scale", subtype='XYZ')  # im killing you.
    bpy.types.PoseBone.nn_position_values = bpy.props.FloatVectorProperty(name="NN Init Position", subtype='XYZ')  # just for fun actually
    # calculated euler occasionally has differences with values stored in posed model because the euler stored is
    # literally just what the maya user set it to be (not derived from quat or matrix or anything)
    # blender doesnt store scale on edit bones because they hate you
    # i put the pose one it cause might as well at that point
    # MESHES
    bpy.types.Mesh.nn_vertex_index = bpy.props.IntProperty(name="Vertex Index", default=-1, min=-1)
    # CAMERAS
    bpy.types.Camera.nn_aspect = bpy.props.FloatProperty(name="Aspect Ratio", default=1.33333, min=-10, max=10)
    # LIGHTS
    bpy.types.Light.nn_falloff_start = bpy.props.FloatProperty(name="Falloff Start", default=0.1)
    bpy.types.Light.nn_inner_size = bpy.props.FloatProperty(name="Inner Size", default=0.1)
    # UI
    bpy.types.WindowManager.nn_texture_setups = bpy.props.CollectionProperty(type=NNTextureNodeSetup)


def custom_unreg():
    # GENERIC
    del bpy.types.Object.nn_frame_rate
    del bpy.types.Object.nn_user_int
    del bpy.types.Object.nn_euler_rotation
    # MODEL
    del bpy.types.Armature.nn_material_count
    del bpy.types.Armature.nn_materials
    del bpy.types.Armature.nn_texture_count
    del bpy.types.Armature.nn_textures
    # BONES
    del bpy.types.PoseBone.nn_user_type
    del bpy.types.PoseBone.nn_user_int
    del bpy.types.PoseBone.nn_user_float
    del bpy.types.PoseBone.nn_euler_rotation
    del bpy.types.PoseBone.nn_hide
    del bpy.types.PoseBone.nn_hide_function
    del bpy.types.PoseBone.nn_reset_scale_x
    del bpy.types.PoseBone.nn_reset_scale_y
    del bpy.types.PoseBone.nn_reset_scale_z
    del bpy.types.PoseBone.nn_ik_effector
    del bpy.types.PoseBone.nn_ik_minus_z
    del bpy.types.PoseBone.nn_ik_1bone_joint1
    del bpy.types.PoseBone.nn_ik_2bone_joint1
    del bpy.types.PoseBone.nn_ik_2bone_joint2
    del bpy.types.PoseBone.nn_xsiik
    del bpy.types.PoseBone.nn_ik_1bone_root
    del bpy.types.PoseBone.nn_ik_2bone_root
    del bpy.types.PoseBone.nn_mesh_count
    del bpy.types.PoseBone.nn_meshes
    del bpy.types.PoseBone.nn_euler_values
    del bpy.types.PoseBone.nn_scale_values
    del bpy.types.PoseBone.nn_position_values
    # MESHES
    del bpy.types.Mesh.nn_vertex_index
    # CAMERAS
    del bpy.types.Camera.nn_aspect
    # LIGHTS
    del bpy.types.Light.nn_falloff_start
    del bpy.types.Light.nn_inner_size
    # UI
    del bpy.types.WindowManager.nn_texture_setups


def update_material_count(self, context):
    while context.object.data.nn_material_count > len(context.object.data.nn_materials):
        context.object.data.nn_materials.add()
    while context.object.data.nn_material_count < len(context.object.data.nn_materials):
        context.object.data.nn_materials.remove(len(context.object.data.nn_materials)-1)


def update_texture_count(self, context):
    while context.object.data.nn_texture_count > len(context.object.data.nn_textures):
        context.object.data.nn_textures.add()
    while context.object.data.nn_texture_count < len(context.object.data.nn_textures):
        context.object.data.nn_textures.remove(len(context.object.data.nn_textures)-1)


def update_mesh_count(self, context):
    while self.nn_mesh_count > len(self.nn_meshes):
        self.nn_meshes.add()
    while self.nn_mesh_count < len(self.nn_meshes):
        self.nn_meshes.remove(len(self.nn_meshes)-1)


class NNMaterial(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(name="Material", type=bpy.types.Material)


class NNTexture(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(name="Texture", type=bpy.types.Image)
    interp_min: bpy.props.EnumProperty(
        name="Interpolation Min", description="Texture interpolation when far",
        items=(
            ('Closest', 'Closest', ""),
            ('Linear', 'Linear', ""),
            ('Closest MipMap Closest', 'Closest MipMap Closest', ""),
            ('Closest MipMap Linear', 'Closest MipMap Linear', ""),
            ('Linear MipMap Closest', 'Linear MipMap Closest', "CNO, ENO, INO, LNO, SNO, UNO, XNO, ZNO STANDARD"),
            ('Linear MipMap Linear', 'Linear MipMap Linear', "GNO STANDARD"),
            ('Anisotropic', 'Anisotropic', "Xbox only"),
            ('Anisotropic MipMap Closest', 'Anisotropic MipMap Closest', "Xbox only"),
            ('Anisotropic MipMap Linear', 'Anisotropic MipMap Linear', "Xbox only"),
            ('Anisotropic4', 'Anisotropic4', "Xbox only"),
            ('Anisotropic4 MipMap Closest', 'Anisotropic4 MipMap Closest', "Xbox only"),
            ('Anisotropic4 MipMap Linear', 'Anisotropic4 MipMap Linear', "Xbox only"),
            ('Anisotropic8', 'Anisotropic8', "Xbox only"),
            ('Anisotropic8 MipMap Closest', 'Anisotropic8 MipMap Closest', "Xbox only"),
            ('Anisotropic8 MipMap Linear', 'Anisotropic8 MipMap Linear', "Xbox only"),
        ), default='Linear MipMap Linear')  # this is because i love gno
    interp_mag: bpy.props.EnumProperty(
        name="Interpolation Mag", description="Texture interpolation when close",
        items=(('Closest', 'Closest', ""), ('Linear', 'Linear', ""), ('Anisotropic', 'Anisotropic', "XBOX")))


class NNTextureNodeSetup(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(name="Texture", type=bpy.types.Image)
    mix_g: bpy.props.EnumProperty(
        name="Texture Blending", description="How images should be mixed",
        items=tuple(list(gno_mix) + list(spec_mix)))
    mix_x: bpy.props.EnumProperty(
        name="Texture Blending", description="How images should be mixed",
        items=tuple(list(xno_mix) + list(spec_mix)))
    vector: bpy.props.EnumProperty(
        name="Image Vector", description="How to map images",
        items=vector_mix)
    u_wrap: bpy.props.EnumProperty(
        name="U Wrap", description="How to wrap U",
        items=u_wrap_mix, default="1")
    v_wrap: bpy.props.EnumProperty(
        name="U Wrap", description="How to wrap V",
        items=v_wrap_mix, default="1")
    multi_shading: bpy.props.BoolProperty("Mix-in Shading", default=False)
    # trying to put the most generic ones in here.., dont intend to do this for all formats, i think..?
    # might make it more confusing for people though..


class NNMesh(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(name="Mesh", type=bpy.types.Object)


def hide_function(obj, self):  # obj.is_evaluated
    hide = self.get("nn_hide", False)
    mesh_count = self.get("nn_mesh_count")
    if not mesh_count:
        return
    for i in range(mesh_count):
        mesh = self.nn_meshes[i].mesh
        if not mesh:
            continue
        mesh.hide_viewport = hide
        mesh.hide_render = hide


def hide_function_update(self, context):
    if self.id_data.id_type == 'OBJECT':
        obj = self.id_data
    else:
        obj = self.id_data.parent
    hide_function(obj, self)


def hide_update(self, context):
    if self.id_data.id_type == 'OBJECT':
        obj = self.id_data
    else:
        obj = self.id_data.parent
    hide_function(obj, self)


def hide_get(self):
    if self.get("nn_hide_function", False) != self.get("nn_hide", False):
        self.nn_hide_function = self.get("nn_hide", False)
    return self.get("nn_hide", False)


def hide_set(self, value):
    if self.id_data.id_type == 'OBJECT':
        obj = self.id_data
    else:
        obj = self.id_data.parent
    hide_function(obj, self)
    self["nn_hide"] = value
