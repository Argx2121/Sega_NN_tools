from dataclasses import dataclass

from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper

from ...io.nn_import_data import *
from ...modules.blender.model import ModelInfo
from ...modules.nn.nn import ReadNn
from ...modules.util import *
import bmesh
import bpy


class OptimiseSegaNO(bpy.types.Operator):
    """Optimise a model for export (destructive)"""
    bl_idname = "export.sega_no_optimise"
    bl_label = "Optimise Model"
    bl_options = {'REGISTER', 'UNDO'}

    # generic
    nn_format: EnumProperty(
        name="Format",
        description="*no variant",
        items=no_export_list,
        default=no_export_list[0][0],
    )

    C: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=cn_list,
    )
    E: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=en_list,
    )
    G: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=gn_list[-1::],
    )
    I: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=in_list,
    )
    L: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=ln_list,
    )
    S: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=sn_list,
    )
    U: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=un_list,
    )
    X: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=xn_list,
    )
    Z: EnumProperty(
        name="Game",
        description="Game the asset is from (to get the correct game variant)",
        items=zn_list,
    )

    def draw(self, context):
        layout = self.layout
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        layout.label(text="Sega NN exporter settings:", icon="KEYFRAME_HLT")

        # todo what if mesh hidden lol

        nn_format = self.nn_format
        layout.row().prop(self, "nn_format")
        # gno data differences are only material flags
        if nn_format not in {"G", "Match__"}:
            layout.row().prop(self, nn_format)

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        nn_format = self.nn_format  # "Match__", "E" etc
        game = getattr(self, nn_format, nn_format)
        # "Match__", "SonicFreeRiders_E" etc defaults to match

        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        # initial check to see if selected models are valid
        arma_list = get_armatures()
        if not arma_list:
            return {'FINISHED'}
        bpy.context.active_object.select_set(False)

        for arma in arma_list:
            # nn has y up, blender has z up, we will also apply transforms for the armature (except location)
            arma.select_set(True)
            bpy.context.view_layer.objects.active = arma
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            arma.rotation_euler[0] = -1.5707963267949
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            arma.rotation_euler[0] = 1.5707963267949

            arma.select_set(False)
            bpy.context.view_layer.objects.active = None

            mesh_list = [a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0]
            for obj in mesh_list:  # these functions don't split the mesh
                remove_extra_bones(obj)
                remove_wrong_bones(obj, arma)
                triangulate(obj.data)
                rotate_mesh(arma, obj)

            mesh_list = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0 and (
                        len(a.material_slots) < 1 or a.material_slots[0].material is None)]
            if mesh_list:
                material = bpy.data.materials.new("Material")
                material.use_nodes = True
                for obj in mesh_list:  # covering all the bases
                    if len(obj.material_slots) < 1:
                        obj.data.materials.append(material)
                    else:
                        obj.material_slots[0].material = material

            mesh_list = [a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0]
            for obj in mesh_list:
                model_simple_split(context, obj)

            # because we split the mesh into simple and complex with only the used v groups used
            #  we can build a list of complex only meshes to check

            mesh_list_a = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0 and len(a.vertex_groups) == 0]
            mesh_list_b = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0 and len(a.vertex_groups) > 0]
            for obj in mesh_list_a:
                enforce_weight(obj, arma)
            for obj in mesh_list_b:
                ensure_weights(obj)

            mesh_list = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0 and len(a.vertex_groups) > 1]
            if self.nn_format == "G":
                for obj in mesh_list:
                    # gno is the only format to allow verts to have more than 4 weights
                    model_complex_split_gno(context, obj)
            else:  # check if more than 4 weights per vert
                check = [mesh_weight_check(obj) for obj in mesh_list]
                if len(set(check)) > 1 or list(set(check))[0]:
                    mesh_names = [obj.name for obj in mesh_list]
                    bad_meshes = [mesh_name for is_bad, mesh_name in zip(check, mesh_names) if is_bad]

                    def draw(self, context):
                        self.layout.label(text="More than 4 weights per vert!")
                        self.layout.label(text="Bad meshes:")
                        self.layout.label(text=", ".join(bad_meshes))

                    bpy.context.window_manager.popup_menu(draw_func=draw, title="NN Model Exporter", icon="ERROR")
                    return {'FINISHED'}

            if game == "Sonic2006_X":
                # 06 has a better way to store weights than the other two xno formats
                mesh_list = [
                    a for a in arma.children if
                    a.type == "MESH" and len(a.data.polygons) > 0 and len(a.vertex_groups) > 128]
                # max bone count is 128 per mesh or 256 (it could be signed)
                for obj in mesh_list:
                    model_complex_split(context, obj)
                # unfortunately i will reuse code because i do not care
            elif self.nn_format == "X":
                check = [mesh_index_weight_check(obj) for obj in mesh_list]
                if len(set(check)) > 1 or list(set(check))[0]:
                    mesh_names = [obj.name for obj in mesh_list]
                    bad_meshes = [mesh_name for is_bad, mesh_name in zip(check, mesh_names) if is_bad]

                    def draw(self, context):
                        self.layout.label(text="More than 4 different bones per triangle!")
                        self.layout.label(text="Bad meshes:")
                        self.layout.label(text=", ".join(bad_meshes))

                    bpy.context.window_manager.popup_menu(draw_func=draw, title="NN Model Exporter", icon="ERROR")
                    return {'FINISHED'}
                mesh_list = [
                    a for a in arma.children if
                    a.type == "MESH" and len(a.data.polygons) > 0 and len(a.vertex_groups) > 4]
                for obj in mesh_list:
                    model_complex_split(context, obj)

            mesh_list = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 0 and len(a.data.materials) > 1]
            for obj in mesh_list:
                model_material_split(context, obj)
            # i think its signed so the split value will be 32767 rounded down because uvs may have different count
            #  also i cannot split this based off what would tri strip best sorry gang
            mesh_list_f = [
                a for a in arma.children if a.type == "MESH" and len(a.data.polygons) > 30000]
            for obj in mesh_list_f:
                model_face_split(context, obj)
        #  https://blender.stackexchange.com/questions/55484/when-to-use-bmesh-update-edit-mesh-and-when-mesh-update
        # todo use bmesh FOR EVERYTHING (including importing bones)
        # todo clean up  https://devtalk.blender.org/t/vertex-weights-and-indices-for-a-bmesh/1457/2
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


def get_armatures():
    # get all armatures selected (and selected by child)
    arma_list = []

    selected_obj = set(bpy.context.selected_objects)
    while selected_obj:
        obj = selected_obj.pop()
        while obj.type != "ARMATURE":
            if obj.parent:
                obj = obj.parent
            else:
                break
        if obj.type == "ARMATURE":
            arma_list.append(obj)
        selected_obj = selected_obj - set(obj.children)

    arma_list = tuple(set(arma_list))

    if not arma_list:
        def draw(self, context):
            self.layout.label(text="No valid models were selected!")

        bpy.context.window_manager.popup_menu(draw_func=draw, title="NN Model Exporter", icon="ERROR")
        return False
    else:
        return arma_list


def remove_extra_bones(obj):
    bone_used = [False for _ in obj.vertex_groups]

    for vert in obj.data.vertices:
        for group in vert.groups:
            if group.weight > 0.0:
                bone_used[group.group] = True

    for i, bone in zip(bone_used, [a.name for a in obj.vertex_groups]):
        if not i:
            obj.vertex_groups.remove(obj.vertex_groups[bone])


def remove_wrong_bones(obj, arma):
    valid_bones = [a.name for a in arma.data.bones]
    used_bones = [a.name for a in obj.vertex_groups]
    invalid_bones = list(set(used_bones) - set(valid_bones))

    for bone in invalid_bones:
        obj.vertex_groups.remove(obj.vertex_groups[bone])


def enforce_weight(obj, arma):
    obj.vertex_groups.new(name=arma.data.bones[0].name)
    obj.vertex_groups[0].add(list(range(len(obj.data.vertices))), 1, "REPLACE")


def ensure_weights(obj):
    v_ind = set()

    for i, vert in enumerate(obj.data.vertices):
        net_wei = sum([group.weight for group in vert.groups[::]])
        if net_wei == 0.0:
            # if we have any weights assigned at all the tool will handle it, even if it doesn't add to 1.0
            v_ind.add(i)
    obj.vertex_groups[0].add(list(v_ind), 1, "REPLACE")


def triangulate(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(mesh)
    bm.free()


def rotate_mesh(arma, obj):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.transform(obj.matrix_world)
    obj.matrix_parent_inverse = arma.matrix_world.inverted()
    obj.rotation_euler[0] = -1.5707963267949
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    from mathutils import Matrix
    obj.matrix_world = Matrix()
    obj.rotation_euler[0] = 1.5707963267949

    obj.select_set(False)
    bpy.context.view_layer.objects.active = None


def mesh_weight_check(obj):
    mesh = obj.data
    wei = []
    for face in mesh.polygons:
        for vert in face.vertices:
            vert = mesh.vertices[vert]
            wei.append(tuple([0 for group in vert.groups[::] if group.weight]))
    wei = [len(a) for a in wei]
    if max(wei) > 4:
        return True
    else:
        return False


def mesh_index_weight_check(obj):
    mesh = obj.data
    wei = []
    for face in mesh.polygons:
        face_weights = []
        for vert in face.vertices:
            vert = mesh.vertices[vert]
            face_weights += [group.group for group in vert.groups[::] if group.weight]
        wei.append(set(face_weights))
    wei = [len(a) for a in wei]
    if max(wei) > 4:
        return True
    else:
        return False


def model_simple_split(context, old_obj):
    import bpy

    minimum_split = context.preferences.addons[__package__.partition(".")[0]].preferences.minimum_split
    mesh_before = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj

    def test_funct():
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch to Object to get selection

        # test if mesh needs splitting
        m_group = []
        for _ in range(len(old_obj.vertex_groups)):
            m_group.append([])
        for face in old_obj.data.polygons:
            v_group_test = []
            for vert in face.vertices:
                vert = old_obj.data.vertices[vert]
                for group in vert.groups:
                    if group.weight == 1:
                        v_group_test.append(group.group)
                        continue
            if len(set(v_group_test)) == 1 and len(v_group_test) == 3:
                m_group[v_group_test[0]].append(face)

        m_group = [g for g in m_group if g != []]
        m_group = [g for g in m_group if len(g) >= minimum_split]
        if len(m_group) == 0:
            bpy.context.active_object.select_set(False)
            return False  # mesh only has complex weights
        if len(m_group[0]) == len(old_obj.data.polygons):
            bpy.context.active_object.select_set(False)
            return False  # same counts = only one group used
        return True

    def main_funct():
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        bpy.context.object.modifiers["DataTransfer"].object = old_obj
        bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
        bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'NEAREST_POLYNOR'
        new_obj = bpy.context.active_object
        new_mesh = new_obj.data

        while True:
            m_group = []
            for _ in range(len(new_obj.vertex_groups)):
                m_group.append([])
            for face in new_mesh.polygons:
                v_group_test = []
                for vert in face.vertices:
                    vert = new_mesh.vertices[vert]
                    for group in vert.groups:
                        if group.weight == 1:
                            v_group_test.append(group.group)
                            continue
                if len(set(v_group_test)) == 1 and len(v_group_test) == 3:
                    m_group[v_group_test[0]].append(face)

            m_group = [g for g in m_group if g != []]
            m_group = [g for g in m_group if len(g) >= minimum_split]
            if not m_group:
                break

            for face in m_group[0]:
                face.select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh_after = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for i in mesh_before:
            mesh_after.remove(i)

        bpy.context.view_layer.objects.active = None
        for obj in mesh_after:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            bpy.context.view_layer.objects.active = None
            obj.select_set(False)
            remove_extra_bones(obj)

        old_obj.select_set(True)
        bpy.context.view_layer.objects.active = old_obj
        bpy.ops.object.delete(use_global=False, confirm=False)

    if test_funct():
        main_funct()


def model_complex_split_gno(context, old_obj):
    import bpy
    mesh_before = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj

    def test_funct():
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch to Object to get selection

        # test if mesh needs splitting
        m_group = []
        for face in old_obj.data.polygons:
            test_group = []
            for vert in face.vertices:
                vert = old_obj.data.vertices[vert]
                test_group.append(
                    [0 for group in vert.groups[::] if group.weight > 0])
            if max(len(i) for i in test_group) > 2:
                m_group.append(face)

        if len(m_group) >= 1:
            if len(m_group) == len(old_obj.data.polygons):
                bpy.context.active_object.select_set(False)
                return False  # mesh only has complex weights
        return True

    def main_funct():
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        bpy.context.object.modifiers["DataTransfer"].object = old_obj
        bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
        bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'NEAREST_POLYNOR'
        new_obj = bpy.context.active_object
        new_mesh = new_obj.data

        while True:
            m_group = []
            for face in new_mesh.polygons:
                test_group = []
                for vert in face.vertices:
                    vert = new_mesh.vertices[vert]
                    test_group.append(
                        [0 for group in vert.groups[::] if group.weight > 0])
                if max(len(i) for i in test_group) > 2:
                    m_group.append(face)

            if not len(m_group) >= 1:
                break

            for face in m_group:
                face.select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh_after = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for i in mesh_before:
            mesh_after.remove(i)

        bpy.context.view_layer.objects.active = None
        for obj in mesh_after:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            bpy.context.view_layer.objects.active = None
            obj.select_set(False)
            remove_extra_bones(obj)

        old_obj.select_set(True)
        bpy.context.view_layer.objects.active = old_obj
        bpy.ops.object.delete(use_global=False, confirm=False)

    if test_funct():
        main_funct()


def convert_3_to_4(group_3):
    # (0, 1, 2), (1, 2, 3), (4, 5, 6)) ->
    # (0, 1, 2, 3, 4, 5, 6)
    bone_list = list(set([bone for l in group_3 for bone in l]))  # flatten and de dup

    # ((0), (0, 1), (0, 2) [...], (0, 1), (1), (1, 2)) ->
    bone_dict = []
    for i in bone_list:
        for j in bone_list:
            bone_dict.append(tuple(sorted({i, j})))
    # ((0, 1), (0, 2) [...], (1, 2))
    bone_dict = set([a for a in bone_dict if len(a) > 1])

    # ((0, 1):[], (0, 2):[] [...], (1, 2):[]) ->
    bone_dict = dict([(a, []) for a in bone_dict])
    # ((0, 1):[[0, 1, 2]], (0, 2):[[0, 1, 2]] [...], (1, 2):[[0, 1, 2], [1, 2, 3]])
    for group in group_3:
        g = []
        for i in group:
            for j in group:
                g.append(tuple(sorted({i, j})))
        g = set([a for a in g if len(a) > 1])
        for a in g:
            bone_dict[a].append(list(group))

    # ((0, 1):[[0, 1, 2]], (0, 2):[[0, 1, 2]] [...], (1, 2):[[0, 1, 2], [1, 2, 3]])
    # loses any empties (and values that don't have a value to pair it to)
    # so it becomes (1, 2):[[0, 1, 2], [1, 2, 3]] that are used
    # which becomes [0, 1, 2, 3] and is returned in a list of other 4 value long groups
    new_data = []
    for _, data in bone_dict.items():
        for a, b in zip(data[::2], data[1::2]):
            new_data.append(tuple(sorted(set(a + b))))
    return set(new_data)


def model_complex_split(context, old_obj):
    import bpy
    mesh_before = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj

    bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
    bpy.ops.object.modifier_add(type='DATA_TRANSFER')
    bpy.context.object.modifiers["DataTransfer"].object = old_obj
    bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
    bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
    bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'NEAREST_POLYNOR'
    new_obj = bpy.context.active_object
    new_mesh = new_obj.data

    def get_groups():
        mesh_group = []
        for f in new_mesh.polygons:
            test_g = []
            for v in f.vertices:
                v = new_mesh.vertices[v]
                test_g += [g_group.group for g_group in v.groups[::] if g_group.weight > 0]
            mesh_group.append(tuple(sorted(set(test_g))))  # remove duplicates + order
        return mesh_group

    def split_meshes(g):
        for face in new_mesh.polygons:
            test_group = []
            for vert in face.vertices:
                vert = new_mesh.vertices[vert]
                test_group += [group.group for group in vert.groups[::] if group.weight > 0]
            if all(var in g for var in set(test_group)):
                face.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')

    bone_groups = list(set(get_groups()))  # remove duplicates
    group_4 = [a for a in bone_groups if len(a) == 4]

    # because we remove extra bone groups later, we do not have to worry about removing them in functions

    for group in group_4:  # value cannot be larger than 4 (max 4 weights are stored)
        # this means that there is a face that uses 4 bones
        # because we can only specify 4 bones, we can only split this face with other faces that's bones are included
        # in the original faces bone list
        # (going from largest to smallest makes less split meshes)
        split_meshes(group)

    bone_groups = list(set(get_groups()))
    group_3 = [a for a in bone_groups if len(a) == 3]
    # we are going to merge any values that we can to reduce the amount of splits
    group_4 = convert_3_to_4(group_3)

    for group in group_4:
        print(group)
        split_meshes(group)

    bone_groups = list(set(get_groups()))
    group_3 = [a for a in bone_groups if len(a) == 3]
    for group in group_3:
        split_meshes(group)

    bone_groups = list(set(get_groups()))
    group_2 = [a for a in bone_groups if len(a) == 2]
    group_2.append([0, 1])
    group_4 = []
    for a, b, in zip(group_2[::2], group_2[1::2]):
        group_4.append(list(a) + list(b))
    for group in group_4:
        split_meshes(group)

    mesh_after = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    bpy.ops.object.select_all(action='DESELECT')

    for i in mesh_before:
        mesh_after.remove(i)

    bpy.context.view_layer.objects.active = None
    for obj in mesh_after:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="DataTransfer")
        bpy.context.view_layer.objects.active = None
        obj.select_set(False)
        remove_extra_bones(obj)

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj
    bpy.ops.object.delete(use_global=False, confirm=False)


def model_material_split(context, old_obj):
    import bpy

    mesh_before = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj

    def test_funct():
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch to Object to get selection

        # test if mesh needs splitting
        m_group = []
        for face in old_obj.data.polygons:
            m_group.append(face.material_index)

        if len(set(m_group)) == 1:
            # if there's only one material used (you could have 10 materials assigned but only use one
            material = old_obj.material_slots[old_obj.data.polygons[0].material_index].material
            old_obj.data.materials.clear()
            old_obj.data.materials.append(material)
            bpy.context.active_object.select_set(False)
            return False
        return True

    def main_funct():
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        bpy.context.object.modifiers["DataTransfer"].object = old_obj
        bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
        bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'NEAREST_POLYNOR'
        new_obj = bpy.context.active_object
        new_mesh = new_obj.data

        while True:
            m_group = []
            for face in new_mesh.polygons:
                m_group.append(face.material_index)

            if not len(set(m_group)) > 1:
                break

            m_group_select = max(m_group)
            for i, face in enumerate(m_group):
                if face == m_group_select:
                    new_mesh.polygons[i].select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh_after = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for i in mesh_before:
            mesh_after.remove(i)

        bpy.context.view_layer.objects.active = None
        for obj in mesh_after:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            bpy.context.view_layer.objects.active = None
            obj.select_set(False)
            material = obj.material_slots[obj.data.polygons[0].material_index].material
            obj.data.materials.clear()
            obj.data.materials.append(material)

        old_obj.select_set(True)
        bpy.context.view_layer.objects.active = old_obj
        bpy.ops.object.delete(use_global=False, confirm=False)

    if test_funct():
        main_funct()


def model_face_split(context, old_obj):
    import bpy

    mesh_before = [ob for ob in bpy.data.objects if ob.type == 'MESH']

    old_obj.select_set(True)
    bpy.context.view_layer.objects.active = old_obj

    def main_funct():
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        bpy.context.object.modifiers["DataTransfer"].object = old_obj
        bpy.context.object.modifiers["DataTransfer"].use_loop_data = True
        bpy.context.object.modifiers["DataTransfer"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.object.modifiers["DataTransfer"].loop_mapping = 'NEAREST_POLYNOR'
        new_obj = bpy.context.active_object
        new_mesh = new_obj.data

        while len(new_mesh.polygons) > 30000:
            # we know its only going to be triangles because we triangulated earlier
            for face in new_mesh.polygons[:(30000-1)]:
                face.select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh_after = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for i in mesh_before:
            mesh_after.remove(i)

        bpy.context.view_layer.objects.active = None
        for obj in mesh_after:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            bpy.context.view_layer.objects.active = None
            obj.select_set(False)
            remove_extra_bones(obj)

        old_obj.select_set(True)
        bpy.context.view_layer.objects.active = old_obj
        bpy.ops.object.delete(use_global=False, confirm=False)

    main_funct()

