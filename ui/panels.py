import bpy
import addon_utils
import requests
import textwrap

# noinspection PyArgumentList
user_ver = [addon.bl_info.get('version') for addon in addon_utils.modules()
            if addon.bl_info['name'] == "Sega NN tools"][0]

try:
    latest_ver = requests.get("https://github.com/Argx2121/Sega_NN_tools/releases/latest").url.rsplit("/")[-1]
    if "." in latest_ver:
        latest_ver = tuple(int(a) for a in latest_ver.split("."))
    else:
        latest_ver = "No Releases."
except (requests.ConnectionError, requests.Timeout) as exception:
    latest_ver = "No Connection."


class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sega NN Tools"


class ITEM_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"


class FCURVE_panel:
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "F-Curve"


class NN_PT_Data(ITEM_panel, bpy.types.Panel):
    bl_label = "NN Settings"

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        if context.object is not None and context.object.type == "ARMATURE":
            return True
        elif context.object is not None and context.object.type == "CAMERA":
            return True
        elif context.object is not None and context.object.type == "LIGHT":
            return True
        return False

    def draw(self, context):
        layout = self.layout
        if context.object.type == "ARMATURE":
            obj = context.object
            if bpy.context.active_object.mode == "OBJECT":
                layout.operator("operator.nn_guess_bones")
                layout.prop(obj, "nn_frame_rate")
            if bpy.context.active_object.mode == "POSE" and context.active_pose_bone:
                bone = context.active_pose_bone
                layout.prop(bone, "nn_user_type", text="")
                layout.prop(bone, bone.nn_user_type)
                layout.prop(bone, "nn_euler_rotation", text="")
                layout.prop(bone, "nn_reset_scale_x")
                layout.prop(bone, "nn_reset_scale_y")
                layout.prop(bone, "nn_reset_scale_z")
        elif context.object.type == "CAMERA":
            obj = context.object
            layout.prop(obj, "nn_user_int")
            layout.prop(obj, "nn_euler_rotation", text="")
            layout.prop(obj.data, "nn_aspect")
            layout.prop(obj, "nn_frame_rate")
        elif context.object.type == "LIGHT":
            obj = context.object
            layout.prop(obj, "nn_user_int")
            layout.prop(obj, "nn_euler_rotation", text="")
            layout.prop(obj, "nn_frame_rate")
            if context.object.data.type == 'SPOT':
                layout.prop(obj.data, "nn_falloff_start")
            elif context.object.data.type == 'AREA':
                layout.prop(obj.data, "nn_falloff_start")
                layout.prop(obj.data, "nn_inner_size")


class NN_PT_Mesh(ITEM_panel, bpy.types.Panel):
    bl_label = "NN Render Mesh"
    bl_parent_id = 'NN_PT_Data'

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "ARMATURE":
            if bpy.context.active_object.mode == "POSE" and context.active_pose_bone:
                return True
        return False

    def draw(self, context):
        layout = self.layout
        bone = context.active_pose_bone
        layout.operator("operator.nn_set_bones")
        layout.prop(bone, "nn_hide")
        layout.prop(bone, "nn_mesh_count")
        for i in range(0, bone.nn_mesh_count):
            layout.prop(bone.nn_meshes[i], "mesh", text="")


class NN_PT_Ik(ITEM_panel, bpy.types.Panel):
    bl_label = "NN Ik"
    bl_parent_id = 'NN_PT_Data'

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "ARMATURE":
            if bpy.context.active_object.mode == "POSE" and context.active_pose_bone:
                return True
        return False

    def draw(self, context):
        layout = self.layout
        bone = context.active_pose_bone
        layout.prop(bone, "nn_ik_effector")
        layout.prop(bone, "nn_ik_minus_z")
        layout.prop(bone, "nn_ik_1bone_joint1")
        layout.prop(bone, "nn_ik_2bone_joint1")
        layout.prop(bone, "nn_ik_2bone_joint2")
        layout.prop(bone, "nn_xsiik")
        layout.prop(bone, "nn_ik_1bone_root")
        layout.prop(bone, "nn_ik_2bone_root")


class NN_PT_Material(ITEM_panel, bpy.types.Panel):
    bl_label = "NN Materials"
    bl_parent_id = 'NN_PT_Data'

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "ARMATURE":
            if bpy.context.active_object and bpy.context.active_object.mode == "OBJECT":
                return True
        return False

    def draw(self, context):
        layout = self.layout
        if context.object.type == "ARMATURE":
            obj = context.object
            layout.operator("operator.nn_get_materials")
            layout.prop(obj.data, "nn_material_count")
            for i in range(0, obj.data.nn_material_count):
                layout.prop(obj.data.nn_materials[i], "material", text="")


class NN_PT_Texture(ITEM_panel, bpy.types.Panel):
    bl_label = "NN Textures"
    bl_parent_id = 'NN_PT_Data'

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "ARMATURE":
            if bpy.context.active_object and bpy.context.active_object.mode == "OBJECT":
                return True
        return False

    def draw(self, context):
        layout = self.layout
        if context.object.type == "ARMATURE":
            obj = context.object
            layout.operator("operator.nn_sync_textures")
            layout.operator("operator.nn_copy_textures")
            layout.prop(obj.data, "nn_texture_count")
            for i in range(0, obj.data.nn_texture_count):
                layout.prop(obj.data.nn_textures[i], "texture", text="")
                row = layout.row(align=True)
                row.prop(obj.data.nn_textures[i], "interp_min", text="")
                row.prop(obj.data.nn_textures[i], "interp_mag", text="")


class NN_PT_Import(GENERIC_panel, bpy.types.Panel):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        layout.operator("import_nn.sega_nd", text="Camera .*nc, .*nd")
        layout.operator("import_nn.sega_ni", text="Light .*ni, .*nl")
        layout.operator("import_nn.sega_no", text="Model .*no")
        layout.operator("import_nn.sega_ng", text="Morph .*ng")
        layout.operator("import_nn.sega_nm", text="Bone Anim .*nm")
        layout.operator("import_nn.sega_nv", text="Material Anim .*nv")
        layout.operator("import_nn.sega_nf", text="Morph Anim .*nf")


class NN_PT_Export(GENERIC_panel, bpy.types.Panel):
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        # layout.operator("object.nn_spawner", text="Spawn in Camera")
        # layout.operator("export.sega_nd", text="Camera .*nc, .*nd")
        layout.operator("export.sega_no_optimise", text="Prepare Model")
        layout.operator("export.sega_no", text="Model .*no")


class NN_PT_Extract(GENERIC_panel, bpy.types.Panel):
    bl_label = "File Extraction"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("amb.extract", text="Sonic 4 .AMB")
        layout.operator("bnk.extract", text="Bank file .bnk")
        layout.operator("pkg.extract", text="Sega Superstars .DIR and .PKG")
        layout.operator("srgc.extract", text="Sonic Riders GC (NO EXTENSION)")
        layout.operator("srpc.extract", text="Sonic Riders PC (NO EXTENSION)")
        layout.operator("srzg.extract", text="Sonic Riders Zero Gravity .pack")
        layout.operator("sfr.extract", text="Sonic Free Riders .pac / .pas")
        layout.operator("sms.extract", text="Bleach: Shattered Blade .sms")
        layout.operator("gosgts.extract", text="Ghost Squad .gos / .gts")


class NN_PT_ExtraImport(GENERIC_panel, bpy.types.Panel):
    bl_label = "Extra Imports"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("import_nn.sega_nn_collision", text="Collision .collision")
        layout.operator("import_nn.sega_nn_pathfinding", text="Pathfinding .pathfinding")
        layout.operator("import_nn.sega_nn_splines", text="Splines .splines")
        layout.operator("import_nn.sega_nn_objects", text="Objects .objects")


class NN_PT_About(GENERIC_panel, bpy.types.Panel):
    bl_label = "About"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Tools Version: " + str(user_ver))
        if latest_ver == user_ver:
            layout.label(text="You're on the latest version.")
        elif "No" in latest_ver:
            layout.label(text=latest_ver)
        else:
            layout.label(text="You're not on the latest version!", icon="ERROR")
            layout.operator("wm.url_open", text="Latest Release Link: " + str(latest_ver)).url = \
                "https://github.com/Argx2121/Sega_NN_tools/releases/latest"
        blender_version = (4, 1, 1)
        if bpy.app.version != blender_version:
            layout.label(text='Please use Blender version ' + str(blender_version), icon='ERROR')
        layout.label(text="NN tools by Arg!!")
        box = layout.box()
        box.scale_y = 0.6
        box.label(text="Special thanks:")
        letter_count = int(context.region.width // 8)
        thanks_text = "firegodjr, Radfordhound, Sewer56, Shadowth117, Yacker"
        wrapped_text = textwrap.TextWrapper(width=letter_count).wrap(text=thanks_text)
        [box.label(text=a) for a in wrapped_text]
        layout.operator("wm.url_open", text="Discord Link").url = "https://discord.gg/CURRBfq"
        layout.operator("wm.url_open", text="GitHub Link").url = "https://github.com/Argx2121/Sega_NN_tools/"


class NN_PT_FCurve(FCURVE_panel, bpy.types.Panel):
    bl_label = "NN FCurve"

    @classmethod
    def poll(cls, context):
        if context.active_editable_fcurve:
            return True
        return False

    def draw(self, context):
        layout = self.layout
        layout.operator("fcurve.nn_fcurve")

