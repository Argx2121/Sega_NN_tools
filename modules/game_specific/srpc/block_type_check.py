from os import path

import bpy

from Sega_NN_tools.modules.game_specific.srpc import read_pathfinding as re_path, read_paths as re_paths, \
    read_collision as re_col, read_instance_models as re_inst
from Sega_NN_tools.modules.nn_util import read_int, read_str, read_byte, read_float, read_float_tuple


class BlockTypeCheck:
    def __init__(self, f, file_path, next_block):
        self.f = f
        self.file_path = file_path
        self.next_block = next_block
        self.start = f.tell() - 4

    def check_image(self):
        f = self.f
        start = self.start
        f.seek(start + read_int(f))
        if f.tell() < path.getsize(self.file_path):
            block_type = read_str(f, 4)
            if block_type == 'GBIX':
                f.seek(start)
                return True
        f.seek(start)
        return False

    def check_xbox(self):
        f = self.f
        start = self.start
        block_type = read_str(f, 4)
        if block_type == 'XBOX':
            f.seek(start)
            return True
        f.seek(start)
        return False

    def check_00_02_xbox(self):
        f = self.f
        start = self.start
        f.seek(2, 1)
        block_type = read_str(f, 4)
        if block_type == 'XBOX':
            f.seek(start)
            return True
        f.seek(start)
        return False

    def check_collision(self):
        f = self.f
        start = self.start
        block_type = read_int(f)
        if block_type == 66048:
            f.seek(start)
            return True
        f.seek(start)
        return False

    def check_instancing(self):
        f = self.f
        start = self.start
        f.seek(3, 1)
        block_type = read_byte(f)
        if block_type == 128:
            f.seek(start)
            return True
        f.seek(start)
        return False

    def check_rendering(self):
        f = self.f
        start = self.start
        block_type = read_int(f)
        if 1 < block_type < 25:  # yeah i have no idea im just guessing what a good range would be
            f.seek(start)
            return True
        f.seek(start)
        return False

    def check_world_rendering(self):
        f = self.f
        start = self.start
        block_type = read_int(f)
        if block_type == 1:
            f.seek(start)
            return True
        f.seek(start)
        return False

    def execute(self):
        f = self.f
        # theres at least two other blocks not listed here
        if self.check_image():
            print("Reading texture block")
            return True
        elif self.check_xbox():
            re_path.ReadXbox(f).execute()
        elif self.check_00_02_xbox():
            re_paths.ReadPaths(f, self.next_block).execute()
        elif self.check_collision():
            re_col.ReadCollision(f, self.next_block).execute()
        elif self.check_instancing():
            re_inst.ReadInstanceModels(f).execute()
        elif self.check_rendering():
            print("Skipping player / item rendering settings - inapplicable data")
            re_inst.ReadInstanceModels(f).execute()
        elif self.check_world_rendering():  # its not worth making a function for this lmao
            print("Reading scene rendering settings")
            f.seek(12, 1)
            bpy.context.space_data.clip_end = read_float(f)
            f.seek(16, 1)
            bpy.context.scene.world.color = read_float_tuple(f, 3)
        else:
            print("Skipping Unknown at:", f.tell())
            return False
        return False
