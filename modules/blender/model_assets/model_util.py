import bpy


class ModelUtil:
    def make_names(self):
        model_strip = self.model_name_strip
        if not self.bone_names:
            self.bone_names = [model_strip + "_Bone_" + str(a) for a in list(range(self.model_data.data.bone_count))]
        self.group_names = [model_strip + "_Bone_Group_" + str(a.group) for a in self.model_data.bones]
        self.mat_names = [model_strip + "_Material_" + str(a) for a in list(range(self.model_data.data.material_count))]
        self.mesh_names = [model_strip + "_Mesh_" + str(a) for a in list(range(len(self.model_data.build_mesh)))]

    def clean_mesh(self):  # i hate using ops
        obj_list = self.obj_list
        import bmesh
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr
        output = StringIO()
        for obj_cur in obj_list:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.context.view_layer.objects.active = obj_cur
            bpy.ops.object.mode_set(mode='EDIT')

            bm = bmesh.from_edit_mesh(obj_cur.data)
            bm.faces.ensure_lookup_table()
            faces_select = []
            for face in bm.faces:
                if face.calc_area() == 0:
                    faces_select.append(face)
            bmesh.ops.delete(bm, geom=faces_select, context="FACES")

            bpy.ops.mesh.select_all(action='SELECT')
            with redirect_stdout(output), redirect_stderr(output):
                bpy.ops.mesh.remove_doubles(threshold=0.00000001)
                bpy.ops.mesh.delete_loose()
