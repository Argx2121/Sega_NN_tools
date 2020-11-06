from ...util import *


# read + make textures
class ExtractImage:
    def __init__(self, f: BinaryIO, filepath: str):
        self.f = f
        self.filepath = filepath
        self.texture_path = bpy.path.abspath(filepath).rstrip(bpy.path.basename(filepath))
        self.texture_files = []
        self.texture_start = 0
        self.image_count = 0
        self.texture_offsets = []
        self.texture_lens = []

    def execute(self):
        self.texture_start, self.image_count, self.texture_files, self.texture_offsets, self.texture_lens = \
            be_read_texture_block_info(self.f)
        self.make_image()
        print("Extracted images")

    def make_image(self):
        f = self.f
        tex_path = self.texture_path

        def image():
            tex_name_base = tex_path + self.texture_files[texture_index]
            file_name: str = tex_name_base + ".dds"
            self.texture_files.append(file_name)
            ft = open(file_name, "wb")
            ft.write(texture_data)
            ft.close()

        for texture_index in range(self.image_count):
            f.seek(self.texture_start + self.texture_offsets[texture_index])
            texture_data = f.read(self.texture_lens[texture_index])
            image()
