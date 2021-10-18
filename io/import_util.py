from Sega_NN_tools.modules.util import *


def batch_handler(filepath: str, batch_import: str, func: Any, name_ignore: str = False, name_require: str = False,
                  case_sensitive: bool = True):
    start_time = time()
    if batch_import == "Single":
        func(filepath)
        stdout.flush()
    else:
        toggle_console()
        file_list = get_files(filepath, batch_import, name_ignore, name_require, case_sensitive)
        for filepath in file_list:
            func(filepath)
            stdout.flush()
        toggle_console()
    print_line()

    print("Done in %f seconds" % (time() - start_time))
    print_line()
    stdout.flush()
