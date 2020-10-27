import dataclasses

from ...util import *


@dataclasses.dataclass
class InstanceObject:
    __slots__ = ["sub_file_id", "position", "rotation"]
    sub_file_id: int
    position: tuple
    rotation: tuple


class ReadInstanceModels:
    def __init__(self, f):
        self.f = f
        self.obj_list = []

    def execute(self):
        console_out("Reading Objects...", self.read_data)
        console_out("Making Objects...", self.make_blender)

    def read_data(self):
        f = self.f
        instance_count = read_short(f)
        f.seek(6, 1)
        for _ in range(instance_count):
            sub_file_id = read_short(f)
            f.seek(10, 1)
            co_ords = read_float_tuple(f, 3)
            rotation = read_float_tuple(f, 3)
            f.seek(12, 1)
            self.obj_list.append(InstanceObject(sub_file_id, co_ords, rotation))

    def make_blender(self):
        col = bpy.context.collection
        bpy.ops.object.mode_set(mode="OBJECT")

        par = bpy.data.objects.new("Instancing_Root", None)
        # par.hide_viewport = True
        col.objects.link(par)

        def make_empty():
            obj = bpy.data.objects.new("Instance_Object_" + str(obj_index), None)
            col.objects.link(obj)
            obj.location = pos[0], - pos[2], pos[1]
            obj.rotation_euler = rot
            # obj.parent = par

        # def duplicate():
        #     obj = bpy.data.objects.new(model_name, bpy.data.objects[model_name].data)
        #     col.objects.link(obj)
        #     obj.location = pos[0], - pos[2], pos[1]
        #     obj.rotation_euler = rot
        #     obj.parent = par

            # bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

        # var = 0
        for obj_inst in self.obj_list:
            pos = obj_inst.position
            rot = obj_inst.rotation
            obj_index = obj_inst.sub_file_id
            # if obj_index in self.sub_file_info:
            # obj_index = self.sub_file_info.index(obj_index)
            # if obj_index in self.model_list_index:
            # obj_index = self.model_list_index.index(obj_index)
            # model_name = self.model_list_name[obj_index]
            # duplicate()
            # var += 1
            # if var > 5:
            #     break
            # continue
            make_empty()
