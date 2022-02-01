import dataclasses

from ...util import *


@dataclasses.dataclass
class ArchiveInfo:
    __slots__ = ["file_count", "sub_file_counts", "sub_file_offsets", "sub_file_additive_counts", "sub_file_types"]
    file_count: int
    sub_file_counts: Tuple[int, ...]
    sub_file_offsets: Tuple[int, ...]
    sub_file_additive_counts: Tuple[int, ...]
    sub_file_types: Tuple[int, ...]


def read_archive(f: BinaryIO, endian: str) -> ArchiveInfo:
    """Reads the Archive info in Riders files.

    Usage : Required.

    Function : Listing sub file information in a riders archive.

    Parameters
    ----------
    f : BinaryIO
        The file read

    endian : str
        File endian.

    Returns
    -------
    ArchiveInfo :
        The Archive info.

    """
    file_count = read_int(f, endian)
    sub_file_counts = read_byte_tuple(f, file_count)
    offset_count = sum(sub_file_counts)
    read_aligned(f, 4)
    sub_shorts = read_short_tuple(f, file_count * 2, endian)
    sub_file_offsets = read_int_tuple(f, offset_count, endian)
    read_aligned(f, 16)
    return ArchiveInfo(file_count, sub_file_counts, sub_file_offsets, sub_shorts[:file_count], sub_shorts[file_count:])
