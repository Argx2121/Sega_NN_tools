import dataclasses

from Sega_NN_tools.modules.util import *


@dataclasses.dataclass
class InstanceObject:
    __slots__ = ["item_type", "position", "rotation"]
    item_type: int
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
        instance_count = read_int(f, ">")
        f.seek(4, 1)
        for _ in range(instance_count):
            item_type = read_int(f, ">")
            f.seek(8, 1)
            self.obj_list.append(InstanceObject(item_type, read_float_tuple(f, 3, ">"), read_float_tuple(f, 3, ">")))
            f.seek(16, 1)

    def make_blender(self):
        for inst in self.obj_list:
            obj = bpy.data.objects.new("Instance_Object_" + str(inst.item_type), None)
            pos = inst.position
            obj.location = pos[0], - pos[2], pos[1]
            obj.rotation_euler = inst.rotation

            bpy.context.collection.objects.link(obj)
