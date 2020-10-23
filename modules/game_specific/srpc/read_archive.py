import dataclasses

from ...nn_util import *


@dataclasses.dataclass
class ArchiveInfo:
    file_count: int
    sub_file_counts: Tuple[int, ...]
    sub_file_info: Tuple[int, ...]
    sub_file_offsets: Tuple[int, ...]


def read_archive(f: BinaryIO) -> ArchiveInfo:
    """Reads the Archive data in Riders files.

    Usage : Required.

    Function : Listing sub file information in a riders archive.

    Parameters
    ----------
    f : BinaryIO
        The file read.

    Returns
    -------
    ArchiveInfo :
        The Archive data.

    """
    start_time = console_out_pre("Reading Archive Info...")
    file_count = read_int(f)
    sub_file_counts = read_multi_bytes(f, file_count)
    offset_count = sum(sub_file_counts)
    read_aligned(f, 4)
    sub_file_info = read_multi_shorts(f, 2 * file_count)
    sub_file_offsets = read_multi_ints(f, offset_count)
    read_aligned(f, 16)
    console_out_post(start_time)
    print("File count is " + str(file_count) + ", Overall file count is", len(sub_file_offsets))
    print("Files sub file counts are", sub_file_counts)
    print("Files sub file offsets are", sub_file_offsets)
    return ArchiveInfo(file_count, sub_file_counts, sub_file_info, sub_file_offsets)
