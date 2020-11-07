# this file just collects common functions
import os
from struct import unpack, pack
from sys import stdout
from time import time
from typing import BinaryIO, Tuple, Any, Union

import bpy


# large functions


def get_files(file_path: str, name_ignore: str = False, name_require: str = False) -> list:
    """Returns a list of file names in the current folder with optional restrictions on name.

    Parameters
    ----------
    file_path : str
        Path to the folder - can have a files name included and be relative.
    name_ignore : str
        String that files should not have in their name.
    name_require : str
        String that files should have in their name.

    Returns
    -------
    list
        A list of processed file names.

    """
    file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
    file_list = [file for file in os.listdir(file_path) if os.path.isfile(file_path + file)]
    if name_require:
        file_list = [file for file in file_list if name_require in file]
    if name_ignore:
        file_list = [file for file in file_list if name_ignore not in file]
    return [file_path + file for file in file_list]


def make_bpy_textures(filepath, texture_names):  # see if textures already exist in the folder
    has_png = True  # png shouldn't be used in game but converted image files might be .png
    has_dds = True
    for tex in texture_names:
        if not os.path.exists(filepath + tex[:-4] + ".png"):
            has_png = False
            break
    for tex in texture_names:
        if not os.path.exists(filepath + tex[:-4] + ".dds"):
            has_dds = False
            break
    if has_png:
        return [bpy.data.images.load(filepath + tex[:-4] + ".png") for tex in texture_names]
    elif has_dds:
        return [bpy.data.images.load(filepath + tex[:-4] + ".dds") for tex in texture_names]
    return [filepath + a for a in texture_names]


def le_read_texture_block_info(f: BinaryIO) -> tuple:
    """Reads texture block info. Returns start offset, count, type_byte, offsets and names.

    Parameters
    ----------
    f : BinaryIO
        The file read.

    Returns
    -------
    list
        Start offset, count, type_byte, offsets and names.

    """
    tex_start = f.tell()
    img_count = read_short(f)
    _, image_pad = read_byte_tuple(f, 2)
    texture_offsets = read_int_tuple(f, img_count)
    tex_names_len = (texture_offsets[0] - (4 * img_count + 4 + img_count * image_pad))
    f.seek(tex_start + 4 + img_count * 4 + img_count * image_pad - 1)
    type_byte = read_byte(f)
    texture_names = read_str_nulls(f, tex_names_len)[:img_count]
    texture_names = [name.replace("/", ".").replace("\\", ".").replace(".....", ".").replace("..", ".") for name in
                     texture_names]
    return tex_start, img_count, type_byte, texture_offsets, texture_names


def be_read_texture_block_info(f: BinaryIO) -> tuple:
    """Reads texture block info. Returns start offset, count, type_byte, offsets and names.

    Parameters
    ----------
    f : BinaryIO
        The file read.

    Returns
    -------
    list
        Start offset, count, type_byte, offsets and names.

    """
    tex_start = f.tell()
    img_count = read_short(f, ">")
    f.seek(2, 1)
    texture_offsets = read_int_tuple(f, img_count, ">")
    texture_lens = read_int_tuple(f, img_count, ">")
    tex_names_len = (texture_offsets[0] - f.tell() + tex_start)
    texture_names = read_str_nulls(f, tex_names_len)[:img_count]
    texture_names = [name.replace("/", ".").replace("\\", ".").replace(".....", ".").replace("..", ".") for name in
                     texture_names]
    return tex_start, img_count, texture_names, texture_offsets, texture_lens


def console_out(text: str, execute, variable=None) -> Any:
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
        The functions return data
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


def for_each_offset(f: BinaryIO, post_info: int, offsets: list, execute, variable) -> list:
    """Executes a function at each offset + post_info amd returns returned data.

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
            Tuple containing each executed functions return data from the offset

        """
    function_list = []
    for offset in offsets:
        f.seek(offset + post_info)
        function_list.append(execute(variable))
    return function_list

# small functions


def toggle_console():
    """Toggles Blenders console if on windows"""
    from platform import system
    if system() == "Windows":
        bpy.ops.wm.console_toggle()


def print_line():
    """Prints a line of 50 hyphens to the console"""
    print("--------------------------------------------------")


# read / write data

# alignment


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
        write_byte(file)


# read data


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
    return unpack(endian + str(count) + "f", file.read(count * 2))


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


# write data


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


def write_float(file: BinaryIO, *value: float):
    """Writes a tuple of floats to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The floats to write.

    """
    for values in value:
        file.write(pack("f", values))


def write_integer(file: BinaryIO, *value: int):
    """Writes a tuple of integers to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The integers to write.

    """
    for values in value:
        file.write(pack("I", values))


def write_short(file: BinaryIO, *value: int):
    """Writes a tuple of shorts to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The shorts to write.

    """
    for values in value:
        file.write(pack("H", values))


def write_byte(file: BinaryIO, *value: int):
    """Writes a tuple of bytes to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The bytes to write.

    """
    for values in value:
        file.write(pack("B", values))
