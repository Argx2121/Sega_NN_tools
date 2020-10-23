from Sega_NN_tools.modules.game_specific import *
from Sega_NN_tools.modules.nn.nn import ReadNn
from dataclasses import dataclass

from ..modules.blender.model import Model
from ..modules.util import *

determine_bone = {
    "Match__": 1, "Debug__": 1,
    "Sonic2006_X": 10, "PhantasyStarUniverse_X": 1, "SonicRiders_X": 0.1,
    "Sonic4Episode1_Z": 1
}


@dataclass
class Settings:
    # generic
    format: str
    format_bone_scale: int
    batch_import: str
    clean_mesh: bool
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
    print_line()
    stdout.flush()
    toggle_console()


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
        file_list = get_files(filepath)
        settings.batch_import = "Single"
        for filepath in file_list:
            execute()
            print_line()
            stdout.flush()
    return {'FINISHED'}


def debug(filepath, settings):  # todo remove debug and use as variable instead + tie printing to it
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn_data = ReadNn(f, filepath, settings.format, True).read_file_special()
        for nn in nn_data:
            if nn.model_data:
                Model(nn, settings).x()
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
                Model(nn, settings).x()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_require=[".xno"])
        for filepath in file_list:
            execute()
    finish_process(start_time)
    return {'FINISHED'}


def phantasy_star_universe_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        nn = ReadNn(f, filepath, settings.format).read_block()
        nn.file_name = bpy.path.basename(filepath)
        if nn.model_data:
            Model(nn, settings).x()
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
    return {'FINISHED'}


def sonic_riders_x(filepath, settings):
    def execute():
        print_line()
        f = open(filepath, 'rb')
        srpc_read.ReadSRPC(f, filepath, settings).execute()
        f.close()

    start_time = time()
    toggle_console()
    if settings.batch_import == "Single":
        execute()
    else:
        file_list = get_files(filepath, name_ignore=["."])
        for filepath in file_list:
            execute()
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
                Model(nn, settings).x()
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
    return {'FINISHED'}
