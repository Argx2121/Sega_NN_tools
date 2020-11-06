from dataclasses import dataclass

from Sega_NN_tools.modules.nn.nn import ReadNn
from .nn_import_data import determine_bone, no_list
from ..modules.blender.model import Model
from ..modules.game_specific.sfr_read import ReadSFR
from ..modules.game_specific.srpc_read import ReadSRPC
from ..modules.util import *


@dataclass
class Settings:
    # generic
    format: str
    format_bone_scale: int
    debug: bool
    batch_import: str
    clean_mesh: bool
    simple_materials: bool
    all_bones_one_length: bool
    max_bone_length: float
    ignore_bone_scale: bool
    hide_null_bones: bool
    # srpc
    import_all_formats: bool
    texture_name_structure: str


def batch_handler(filepath: str, batch_import: str, func: Any):
    start_time = time()
    if batch_import == "Single":
        func(filepath)
        stdout.flush()
    else:
        toggle_console()
        file_list = get_files(filepath)
        for filepath in file_list:
            func(filepath)
            stdout.flush()
        toggle_console()
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()


def match_text_handle(text):
    print(text)
    stdout.flush()


def match(filepath, settings):
    def execute(file_path):
        settings.batch_import = "Single"
        print_line()
        f = open(file_path, 'rb')
        first_str = read_str(f, 4)
        f.seek(0)
        first_uint = read_int(f)
        f.seek(0)
        f.close()

        if first_str[0] == "N" and first_str[2] == "I" and first_str[3] == "F":
            if first_str[1] in [a[0] for a in no_list]:
                match_text_handle("Reading as latest " + first_str[1] + "no format")
                generic_import(file_path, settings)
            else:
                print("Couldn't match to a format")
                stdout.flush()

        elif first_str == "NXOB":
            match_text_handle("Game assumed to be Phantasy Star Universe")
            settings.format = "PhantasyStarUniverse_X"
            phantasy_star_universe_x(file_path, settings)

        elif first_str == "pack":
            match_text_handle("Game assumed to be Sonic Riders Zero Gravity")
            settings.format = "SonicRidersZeroGravity_S"
            read_all_file(file_path, settings)

        elif first_str == "paST":
            match_text_handle("Game assumed to be Sonic Free Riders")
            settings.format = "SonicFreeRiders_E"
            sonic_free_riders_e(file_path, settings)

        elif 0 < first_uint < 100:  # typically ~ 45 models in a srpc map file
            match_text_handle("Game assumed to be Sonic Riders")
            settings.format = "SonicRiders_X"
            sonic_riders_x(file_path, settings)

        else:
            match_text_handle("Couldn't match to a format")

    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def sonic_free_riders_e(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block == "paST":
            print_line()
            f = open(file_path, 'rb')
            ReadSFR(f, file_path, settings).execute()
        f.close()

    settings.format_bone_scale = determine_bone[settings.format]
    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def generic_import(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block[0] == "N" and block[2] == "I" and block[3] == "F":
            print_line()
            settings.format = "Match__"
            settings.format, nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()
            settings.format_bone_scale = determine_bone[settings.format]
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def generic_import_1_type(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block[0] == "N" and block[1] == settings.format[-1] and block[2] == "I" and block[3] == "F":
            print_line()
            _, nn = ReadNn(f, file_path, settings.format, settings.debug).read_file()
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    settings.format_bone_scale = determine_bone[settings.format]
    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def phantasy_star_universe_x(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block == "NXOB":
            print_line()
            _, nn = ReadNn(f, file_path, settings.format, settings.debug).read_block()
            nn.file_name = bpy.path.basename(file_path)
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    settings.format_bone_scale = determine_bone[settings.format]
    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def sonic_riders_x(filepath, settings):
    def execute(file_path):
        f = open(file_path, 'rb')
        block = read_int(f)
        f.seek(0)
        if 0 < block < 100:
            print_line()
            ReadSRPC(f, file_path, settings).execute()
        f.close()

    settings.format_bone_scale = determine_bone[settings.format]
    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


def read_all_file(filepath, settings):
    def execute(file_path):
        print_line()
        f = open(file_path, 'rb')
        settings.format = "All__"
        settings.format, nn_list = ReadNn(f, file_path, settings.format, settings.debug).read_file_special()
        settings.format_bone_scale = determine_bone[settings.format]
        for nn in nn_list:
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    batch_handler(filepath, settings.batch_import, execute)
    return {'FINISHED'}


determine_function = {  # only for formats that need their own importer function
    # functions
    "Match__": match, "All__": read_all_file,
    # formats
    "PhantasyStarUniverse_X": phantasy_star_universe_x,
    "SonicRiders_X": sonic_riders_x,
    "SonicRidersZeroGravity_S": read_all_file,
    "SonicFreeRiders_E": sonic_free_riders_e,
}
