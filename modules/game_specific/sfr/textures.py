from ...util import *


# read + make textures
class ExtractImage:
    def __init__(self, f: BinaryIO, filepath: str):
        self.f = f
        self.filepath = filepath
        self.texture_path = bpy.path.abspath(filepath).rstrip(bpy.path.basename(filepath))

    def execute(self):
        def make_image():
            f = self.f
            tex_path = self.texture_path

            for texture_index in range(count):
                f.seek(start + offsets[texture_index])
                ft = open(tex_path + texture_files[texture_index] + ".dds", "wb")
                ft.write(f.read(lens[texture_index]))
                ft.close()

        start, count, texture_files, offsets, lens = be_read_texture_block_info(self.f)
        make_image()
        print("Extracted images")
