from ..util import *
from dataclasses import dataclass


@dataclass
class Camera:
    fov: float
    roll: float
    # ratio: float  # not usable - can't set on a per camera basis
    clip_near: float
    clip_far: float
    position: Tuple[float, ...]
    target: Tuple[float, ...]


class Read:
    __slots__ = ["f"]

    def __init__(self, f: BinaryIO):
        """Reads a N*CA block.

        Usage : Required

        Function : Storing camera data


        Parameters
        ----------
        f : BinaryIO
            The file read.
        """
        self.f = f

    def type_1(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(start_block + 20)
        fov = unpack("h", f.read(2))[0] * (360 / 32767)
        roll = unpack("h", f.read(2))[0] * (360 / 32767)
        _ = read_float(f)  # ratio
        clip_near = read_float(f)
        clip_far = read_float(f)
        cam = Camera(fov, roll, clip_near, clip_far, read_float_tuple(f, 3), read_float_tuple(f, 3))
        f.seek(end_of_block)
        return cam

    def type_2(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(start_block + 20)
        roll = unpack(">h", f.read(2))[0] * (360 / 32767)
        fov = unpack(">h", f.read(2))[0] * (360 / 32767)
        _ = read_float(f, ">")  # ratio
        clip_near = read_float(f, ">")
        clip_far = read_float(f, ">")
        cam = Camera(fov, roll, clip_near, clip_far, read_float_tuple(f, 3, ">"), read_float_tuple(f, 3, ">"))
        f.seek(end_of_block)
        return cam
