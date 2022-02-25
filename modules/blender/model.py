import bpy


from ..util import console_out
from .model_assets import model_util, armature, mesh, materials


class Model:
    def __init__(self, nn, settings):
        self.model = nn.model
        self.settings = settings
        self.format = settings.format
        self.bone_groups = [bone.group for bone in self.model.bones]
        self.bone_names = nn.bones
        self.model_name = nn.name
        self.model_name_strip = self.model_name[:-4]
        self.texture_names = nn.textures
        self.armature = None
        self.material_list_blender = []
        self.group_names = []
        self.mat_names = []
        self.mesh_names = []

    def execute(self):
        print("Making a Model------------------------------------")
        message = "Making" + " " + self.model_name
        print(message + " " * (50 - len(message)) + "|")

        console_out("Making Armature...", armature.make_armature, self)
        console_out("Generating Names...", model_util.make_names, self)
        if self.settings.keep_bones_accurate:
            console_out("Making Accurate Bones...", armature.make_bones_accurate, self)
        else:
            console_out("Making Pretty Bones...", armature.make_bones_pretty, self)

        bpy.ops.object.mode_set(mode="POSE")  # pose bone stuff here
        console_out("Making Bone Groups...", armature.make_bone_groups, self)
        if self.settings.hide_null_bones:
            console_out("Hiding Null Bones...", armature.hide_null_bones)

        bpy.ops.object.mode_set(mode="OBJECT")  # return to normal
        if self.settings.simple_materials:
            console_out("Making Simple Materials...", materials.material_simple, self)
        else:
            console_out("Making Accurate Materials...", materials.material_complex, self)

        console_out("Making Meshes...", mesh.make_mesh, self)
