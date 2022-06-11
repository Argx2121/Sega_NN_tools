import bmesh


def make_names(self):
    model_strip = self.model_name_strip
    if not self.bone_names:
        self.bone_names = dict([
            [a, model_strip + "_Bone_" + str(a).zfill(4)] for a in list(range(self.model.info.bone_count))])
    elif len(self.bone_names) < self.model.info.bone_count:
        bone_set = set(range(self.model.info.bone_count)) - set(self.bone_names)
        for a in bone_set:
            self.bone_names[a] = model_strip + "_Bone_" + str(a).zfill(4)
    self.group_names = [model_strip + "_Bone_Group_" + str(a.group).zfill(4) for a in self.model.bones]
    self.mat_names = [model_strip + "_Material_" + str(a).zfill(4) for a in list(range(self.model.info.material_count))]
    self.mesh_names = [model_strip + "_Mesh_" + str(a).zfill(4) for a in list(range(len(self.model.build_mesh)))]


def clean_mesh(obj):  # removing illegal faces is done in mesh generation
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0000001)
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    verts = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()


def clean_mesh_lazy(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    verts = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()


def clean_mesh_strict(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    verts = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    faces = [f for f in bm.faces if not f.calc_area()]
    bmesh.ops.delete(bm, geom=faces, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    edges = [e for e in bm.edges if not e.link_faces]
    bmesh.ops.delete(bm, geom=edges, context="EDGES")
    bm.to_mesh(obj.data)
    bm.free()
