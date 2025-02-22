import bpy
import math

from dataclasses import dataclass
from ..util import console_out, bad_mesh
from .model_assets import model_util, armature, mesh, materials


class Model:
    def __init__(self, nn, file_path, settings):
        self.file_path = file_path
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
        console_out("Making Bone Constraints...", armature.make_bone_constraints, self)
        bpy.ops.object.mode_set(mode="OBJECT")  # return to normal
        console_out("Making Bone Collections...", armature.make_bone_collections, self)
        if self.settings.hide_null_bones:
            console_out("Hiding Null Bones...", armature.hide_null_bones)

        if self.settings.simple_materials:
            console_out("Making Simple Materials...", materials.material_simple, self)
        else:
            if self.format[-1] == "G":
                console_out("Making Accurate Materials...", materials.material_gno, self)
            else:
                console_out("Making Accurate Materials...", materials.material_complex, self)

        console_out("Making Meshes...", mesh.make_mesh, self)


@dataclass
class ModelData:
    name: str
    center: tuple
    radius: float
    bones: list
    materials: list
    meshes: tuple
    geometry: tuple
    bone_depth: int
    bone_used: list


@dataclass
class MeshTypes:
    simple_opaque: list
    complex_opaque: list
    simple_alpha: list
    complex_alpha: list
    simple_clip: list
    complex_clip: list


class ModelInfo:
    def __init__(self, settings, arma):
        self.settings = settings
        self.format = settings.format
        self.armature = arma
        self.name = ""
        self.mesh_list = []
        self.center = (0, 0, 0)
        self.radius = 0.0
        self.bone = []
        self.bone_depth = 0
        self.bone_used = []
        self.material = []
        self.meshes = []

    def generic(self):
        arma = self.armature
        name = arma.name
        mesh_list = [a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0]
        self.mesh_list = mesh_list

        if name.endswith("." + self.format[-1].lower() + "no"):
            pass
        else:
            name = name + "." + self.format[-1].lower() + "no"
        self.name = name

        print("Getting Model Data--------------------------------")
        message = "Making" + " " + name

        print(message + " " * (50 - len(message)) + "|")

    def get_empty_rig(self):
        bone, bone_depth, bone_used = console_out("Getting Bone Info...", armature.get_bones, self)
        material = console_out("Getting Material Info...", materials.get_materials, self)
        meshes = MeshTypes([], [], [], [], [], [])
        meshes, geometry = console_out("Generating Geometry...", mesh.get_geometry, (meshes, self.settings, self))
        return ModelData(self.name, (0, 0, 0), 0, bone, material, meshes, geometry, bone_depth, bone_used)

    def get_generic(self):
        self.center, self.radius = console_out("Generating Bounds...", armature.get_render_data, self.mesh_list)
        self.bone, self.bone_depth, self.bone_used = console_out("Getting Bone Info...", armature.get_bones, self)
        self.material = console_out("Getting Material Info...", materials.get_materials, self)
        self.meshes = console_out("Getting Mesh Info...", mesh.get_meshes, self.mesh_list)

    def alpha_fix(self):
        material = self.material
        meshes = self.meshes
        mat_name_list = [a.name for a in material.material_list]
        for m in meshes:
            mat_index = mat_name_list.index(m.material_name)
            mat = material.material_list[mat_index]
            m.material_name = mat_index
            m.blend_method = mat.blend_method

    def build_mesh_list(self):
        simple_opaque = []
        complex_opaque = []
        simple_alpha = []
        complex_alpha = []
        simple_clip = []  # guys.... its simple clips...
        complex_clip = []

        for m in self.meshes:
            if m.blend_method == "OPAQUE":
                if len(m.bone_names) > 1:
                    complex_opaque.append(m)
                else:
                    simple_opaque.append(m)
            elif m.blend_method == "CLIP":
                if len(m.bone_names) > 1:
                    complex_clip.append(m)
                else:
                    simple_clip.append(m)
            else:
                if len(m.bone_names) > 1:
                    complex_alpha.append(m)
                else:
                    simple_alpha.append(m)

        self.meshes = MeshTypes(simple_opaque, complex_opaque, simple_alpha, complex_alpha, simple_clip, complex_clip)

    def model(self):
        self.generic()

        name = self.name
        mesh_list = self.mesh_list

        if not mesh_list:
            return self.get_empty_rig()

        quad_count = console_out("Checking Faces...", model_util.check_meshes, mesh_list)
        if quad_count:
            bad_mesh("NN Model Exporter")
            return False
        self.get_generic()

        self.alpha_fix()

        self.build_mesh_list()

        meshes, geometry = console_out("Generating Geometry...", mesh.get_geometry, (self.meshes, self.settings, self))

        return ModelData(
            name, self.center, self.radius, self.bone, self.material, meshes, geometry, self.bone_depth, self.bone_used)

    def execute(self):
        return self.model()
