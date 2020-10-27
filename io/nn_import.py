from Sega_NN_tools.modules.nn.nn import ReadNn
from dataclasses import dataclass

from .nn_import_data import determine_bone
from ..modules.blender.model import Model
from ..modules.game_specific.srpc_read import ReadSRPC
from ..modules.util import *


@dataclass
class Settings:
    # generic
    format: str
    format_bone_scale: int
    batch_import: str
    clean_mesh: bool
    simple_materials: bool
    all_bones_one_length: bool
    max_bone_length: float
    ignore_bone_scale: bool
    hide_null_bones: bool
    # s06
    use_vertex_colours: bool
    # psu
    # srpc
    import_all_formats: bool
    texture_name_structure: str


def finish_process(start_time):
    print_line()
    print("Done in %f seconds" % (time() - start_time))
    stdout.flush()


def match(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        first_uint = read_int(f)  # xno is always little endian
        f.close()
        if first_uint == 1179211854:  # NXIF
            print("Game assumed to be Sonic '06")
            stdout.flush()
            settings.format = "Sonic2006_X"
            settings.format_bone_scale = determine_bone[settings.format]

            sonic_2006_x(filepath, settings)

        elif first_uint == 1112496206:  # NXOB
            print("Game assumed to be Phantasy Star Universe")
            stdout.flush()
            settings.format = "PhantasyStarUniverse_X"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            phantasy_star_universe_x(filepath, settings)

        elif first_uint == 1179212366:  # NZIF
            print("Game assumed to be Sonic 4 Episode 1")
            stdout.flush()
            settings.format = "Sonic4Episode1_Z"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            sonic_4_episode_1_z(filepath, settings)

        elif 0 < first_uint < 100:  # typically ~ 45 models in a srpc map file
            print("Game assumed to be Sonic Riders")
            stdout.flush()
            settings.format = "SonicRiders_X"
            settings.format_bone_scale = determine_bone[settings.format]
            settings.use_vertex_colours = True

            sonic_riders_x(filepath, settings)

        else:
            print("Couldn't match to a game")
            stdout.flush()

    if settings.batch_import == "Single":
        execute()
        print_line()
        stdout.flush()
    else:
        toggle_console()
        file_list = get_files(filepath)
        settings.batch_import = "Single"
        for filepath in file_list:
            execute()
            print_line()
            stdout.flush()
        toggle_console()
    return {'FINISHED'}


def debug(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.format, True).read_file_special()
        for nn in nn_data:
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
    finish_process(start_time)
    toggle_console()
    return {'FINISHED'}


def sonic_2006_x(filepath, settings):
    def execute():
        f = open(filepath, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block == "NXIF":
            print_line()
            nn = ReadNn(f, filepath, settings.format).read_file()
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    start_time = time()
    if settings.batch_import == "Single":
        execute()
    else:
        toggle_console()
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
        toggle_console()
    finish_process(start_time)
    return {'FINISHED'}


def generic_import(filepath, settings):
    def execute():
        f = open(filepath, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block[0] == "N" and block[2] == "I" and block[3] == "F":  # block[1] can be x, z, etc (nn format variable)
            print_line()
            nn = ReadNn(f, filepath, settings.format).read_file()
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    start_time = time()
    if settings.batch_import == "Single":
        execute()
    else:
        toggle_console()
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
        toggle_console()
    finish_process(start_time)
    return {'FINISHED'}


def phantasy_star_universe_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.format).read_block()
        nn.file_name = bpy.path.basename(filepath)
        if nn.model_data:
            Model(nn, settings).execute()
        f.close()

    start_time = time()
    if settings.batch_import == "Single":
        execute()
    else:
        toggle_console()
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
        toggle_console()
    finish_process(start_time)
    return {'FINISHED'}


def sonic_riders_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        ReadSRPC(f, filepath, settings).execute()
        f.close()

    start_time = time()
    if settings.batch_import == "Single":
        execute()
    else:
        toggle_console()
        file_list = get_files(filepath, name_ignore=".")
        for filepath in file_list:
            execute()
        toggle_console()
    finish_process(start_time)
    return {'FINISHED'}


def sonic_4_episode_1_z(filepath, settings):
    def execute():
        f = open(filepath, 'rb')
        block = read_str_nulls(f, 4)[0]
        f.seek(0)
        if block == "NZIF":
            print_line()
            nn = ReadNn(f, filepath, settings.format).read_file()
            if nn.model_data:
                Model(nn, settings).execute()
        f.close()

    start_time = time()
    if settings.batch_import == "Single":
        execute()
    else:
        toggle_console()
        file_list = get_files(filepath)
        for filepath in file_list:
            execute()
        toggle_console()
    finish_process(start_time)
    return {'FINISHED'}


determine_function = {  # only for formats that need their own importer function
    "Match__": match, "Debug__": debug,
    "PhantasyStarUniverse_X": phantasy_star_universe_x,
    "SonicRiders_X": sonic_riders_x,
}