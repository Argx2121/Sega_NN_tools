import os
import bpy
import pathlib  # used by files that import util
from struct import unpack, pack
from sys import stdout
from time import time
from typing import BinaryIO, Tuple, Any, Union  # Union is used by files that import util


# collection of common functions

# functions


def get_files(file_path: str, name_ignore: str = False, name_require: str = False, case_sensitive: bool = True) -> list:
    """Returns a list of file names in the current folder with optional restrictions on name.

    Parameters
    ----------
    file_path : str
        Path to the folder - can have a files name included and be relative.
    name_ignore : str
        String that files should not have in their name.
    name_require : str
        String that files should have in their name.
    case_sensitive: bool
        If the strings are case sensitive (defaults to true).

    Returns
    -------
    list
        A list of processed file names.

    """
    file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
    file_list = [file for file in os.listdir(file_path) if os.path.isfile(file_path + file)]
    if not case_sensitive:
        name_require = name_require.casefold()
        file_list = [file.casefold() for file in file_list]
    if name_require:
        file_list = [file for file in file_list if name_require in file]
    if name_ignore:
        file_list = [file for file in file_list if name_ignore not in file]
    return [file_path + file for file in file_list]


# noinspection PyArgumentList
def console_out(text: str, execute, variable: Any = None) -> Any:
    """Prints a string to the console with padding to 50 letters, executes a function and prints the time it took.

    Parameters
    ----------
    text : str
        The string to print out to the console.

    execute : () -> Any
        The function to execute

    variable : tuple
        The functions parameters

    Returns
    -------
    Any
        The functions return info
    """
    def console_print():
        stdout.write(text)
        stdout.flush()

    text += " " * (50 - len(text))
    s_time = time()
    console_print()
    if variable:
        return_data = execute(variable)
    else:
        return_data = execute()
    text = "| Done in %f seconds \n" % (time() - s_time)
    console_print()
    return return_data


def console_out_pre(var: str) -> float:
    """Prints a string to the console with padding to 50 letters and returns the current time.

    Parameters
    ----------
    var : str
        The string to print out to the console.

    Returns
    -------
    float
        The time that the function was called at.
    """
    var += " " * (50 - len(var))
    s_time = time()
    stdout.write(var)
    stdout.flush()
    return s_time


def console_out_post(s_time: float):
    """Prints a the time a process took to the console.

    Parameters
    ----------
    s_time : float
        The time that console_out_pre was called at
    """

    stdout.write("| Done in %f seconds \n" % (time() - s_time))
    stdout.flush()


def show_finished(tool_name):
    """Shows a pop-up to tell the user a process is finished"""
    def draw(self, context):
        self.layout.label(text="Finished!")
    bpy.context.window_manager.popup_menu(draw, tool_name, "INFO")


def show_not_read(tool_name):
    """Shows a pop-up to tell the user the file couldn't be read"""
    def draw(self, context):
        self.layout.label(text="File could not be read!")
    bpy.context.window_manager.popup_menu(draw, tool_name, "ERROR")


def toggle_console():
    """Toggles Blenders console if on windows"""
    from platform import system
    if system() == "Windows":
        bpy.ops.wm.console_toggle()


def print_line():
    """Prints a line of 50 hyphens to the console"""
    print("--------------------------------------------------")


# read / write info

# functions


# noinspection PyArgumentList
def for_each_offset(f: BinaryIO, post_info: int, offsets: list, execute, variable) -> list:
    """Executes a function at each offset + start amd returns returned info.

        Parameters
        ----------
        f : BinaryIO
            The file read.

        post_info : int
            File position after info block

        offsets : list
            List of file offsets

        execute : () -> Any
        The function to execute

        variable : tuple
            The functions parameters

        Returns
        -------
        tuple
            Tuple containing each executed functions return info from the offset

        """
    function_list = []
    for offset in offsets:
        f.seek(offset + post_info)
        function_list.append(execute(variable))
    return function_list


def read_aligned(file: BinaryIO, divide_by: int):
    """Reads the file until at an alignment.

    Parameters
    ----------
    file : BinaryIO
        The file read.
    divide_by : int
        Alignment to read to.
    """

    while file.tell() % divide_by:
        read_byte(file)


def write_aligned(file: BinaryIO, divide_by: int):
    """Writes the file until at an alignment.

    Parameters
    ----------
    file : BinaryIO
        The file read.
    divide_by : int
        Alignment to write to.
    """
    while file.tell() % divide_by:
        write_byte(file, "<")


# read info


def read_str(file: BinaryIO, count: int) -> str:
    """Reads and returns a string.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many bytes to read.

        Returns
        -------
        str
            The string read.
        """

    return file.read(count).decode("utf-8", "ignore")


def read_float(file: BinaryIO, endian="<") -> float:
    """Reads and returns a float.

    Parameters
    ----------
    file : BinaryIO
        The file read.

    endian :
        Endian of what's being read.

    Returns
    -------
    float
        The float read.
    """

    return unpack(endian + "f", file.read(4))[0]


def read_half(file: BinaryIO, endian="<") -> float:
    """Reads and returns a half float.

    Parameters
    ----------
    file : BinaryIO
        The file read.

    endian :
        Endian of what's being read.

    Returns
    -------
    float
        The float read.
    """

    return unpack(endian + "e", file.read(2))[0]


def read_int(file: BinaryIO, endian="<") -> int:
    """Reads and returns an integer.

    Parameters
    ----------
    file : BinaryIO
        The file read.

    endian :
        Endian of what's being read.

    Returns
    -------
    int
        The integer read.
    """

    return unpack(endian + "I", file.read(4))[0]


def read_short(file: BinaryIO, endian="<") -> int:
    """Reads and returns a short.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        endian :
            Endian of what's being read.

        Returns
        -------
        int
            The short read.
        """

    return unpack(endian + "H", file.read(2))[0]


def read_byte(file: BinaryIO, endian="<") -> int:
    """Reads and returns a byte.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        endian :
            Endian of what's being read.

        Returns
        -------
        int
            The byte read.
        """

    return unpack(endian + "B", file.read(1))[0]


def read_str_nulls(file: BinaryIO, count: int) -> list:
    """Reads and returns list of strings.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many bytes to read.

        Returns
        -------
        list
            A list of strings.

    """
    return file.read(count).decode("utf-8", "ignore").split(u"\x00")


def read_float_tuple(file: BinaryIO, count: int, endian="<") -> Tuple[float, ...]:
    """Reads and returns tuple of floats.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many floats to read.

        endian :
            Endian of what's being read.

        Returns
        -------
        tuple
            A tuple of floats.

    """
    return unpack(endian + str(count) + "f", file.read(count * 4))


def read_half_tuple(file: BinaryIO, count: int, endian="<") -> Tuple[float, ...]:
    """Reads and returns tuple of half floats.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many floats to read.

        endian :
            Endian of what's being read.

        Returns
        -------
        tuple
            A tuple of floats.

    """
    return unpack(endian + str(count) + "e", file.read(count * 2))


def read_int_tuple(file: BinaryIO, count: int, endian="<") -> Tuple[int, ...]:
    """Reads and returns tuple of integers.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many integers to read.

        endian :
            Endian of what's being read.

        Returns
        -------
        tuple
            A tuple of integers.

    """
    return unpack(endian + str(count) + "I", file.read(count * 4))


def read_short_tuple(file: BinaryIO, count: int, endian="<") -> Tuple[int, ...]:
    """Reads and returns tuple of shorts.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many shorts to read.

        endian :
            Endian of what's being read.

        Returns
        -------
        tuple
            A tuple of shorts.

    """
    return unpack(endian + str(count) + "H", file.read(count * 2))


def read_byte_tuple(file: BinaryIO, count: int, endian="<") -> Tuple[int, ...]:
    """Reads and returns tuple of bytes.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many bytes to read.

        endian :
            Endian of what's being read.

        Returns
        -------
        tuple
            A tuple of bytes.

    """
    return unpack(endian + str(count) + "B", file.read(count))


# write info


def write_string(file: BinaryIO, *value: bytes):
    """Writes a tuple of strings to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The strings to write.

    """
    for values in value:
        file.write(pack(str(len(values)) + "s", values))


def write_float(file: BinaryIO, endian: str, *value: float):
    """Writes a tuple of floats to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The floats to write.

    """
    for values in value:
        file.write(pack(endian + "f", values))


def write_integer(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of integers to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The integers to write.

    """
    for values in value:
        file.write(pack(endian + "I", values))


def write_short(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of shorts to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The shorts to write.

    """
    for values in value:
        file.write(pack(endian + "H", values))


def write_byte(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of bytes to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The bytes to write.

    """
    for values in value:
        file.write(pack(endian + "B", values))
