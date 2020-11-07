import dataclasses

from ...util import *


@dataclasses.dataclass
class PastInfo:
    file_count: int
    offsets: Tuple[int, ...]


def read_archive(f: BinaryIO) -> PastInfo:
    start_time = console_out_pre("Reading Archive Info...")
    file_count = read_int(f, ">")
    offsets = read_int_tuple(f, file_count, ">")
    console_out_post(start_time)
    print("File count is", file_count)
    print("File offsets are", offsets)
    return PastInfo(file_count, offsets)
