import bpy

from .model_assets.armature import Armature
from .model_assets.materials import Material
from .model_assets.mesh import Mesh
from .model_assets.model_util import ModelUtil
from ..nn_util import console_out


class Model:
    def __init__(self, nn, settings):  # TODO format xbox/gamecube/etc
        self.model_data = nn.model_data
        self.settings = settings
        self.format = settings.format
        self.bone_groups = [bone.group for bone in self.model_data.bones]
        self.bone_names = nn.bone_names
        self.model_name = nn.file_name
        self.model_name_strip = nn.file_name
        if self.model_name_strip.endswith("no"):
            self.model_name_strip = self.model_name_strip[:-4]
        self.texture_names = nn.texture_names
        self.armature = None
        self.material_list_blender = []
        self.obj_list = []
        self.material_in_next_block = []  # for srpc
        self.group_names = []
        self.mat_names = []
        self.mesh_names = []

    def x(self):
        print("Making a Model------------------------------------")
        message = "Making" + " " + self.model_name
        print(message + " " * (50 - len(message)) + "|")

        console_out("Making Armature...", Armature.make_armature, self)
        console_out("Generating Names...", ModelUtil.make_names, self)
        console_out("Making Bones...", Armature.make_bones_type_1, self)

        bpy.ops.object.mode_set(mode="POSE")  # pose bone stuff here
        console_out("Making Bone Groups...", Armature.make_bone_groups, self)
        if not self.settings.ignore_bone_scale:
            console_out("Scaling Bones...", Armature.scale_bones, self)
        if self.settings.hide_null_bones:
            console_out("Hiding Unweighted Bones...", Armature.hide_null_bones)

        bpy.ops.object.mode_set(mode="OBJECT")  # return to normal
        if self.settings.simple_materials:
            console_out("Making Simple Materials...", Material.make_material_simple, self)
        else:
            console_out("Making Accurate Materials...", Material.make_material_complex, self)

        self.obj_list = console_out("Making Meshes...", Mesh.make_mesh, self)

        if self.settings.clean_mesh:
            console_out("Cleaning Meshes...", ModelUtil.clean_mesh, self)  # delete loose + doubles
        bpy.ops.object.mode_set(mode="OBJECT")
        return self.material_in_next_block
