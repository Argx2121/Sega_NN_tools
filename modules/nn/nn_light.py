from ..util import *
from dataclasses import dataclass
from enum import Flag


@dataclass
class Light:
    light_type: str
    light_flags: int
    user: int
    color: Tuple[float, ...]
    intensity: float
    direction: Tuple[float, ...]
    position: Tuple[float, ...]
    rot_order: str
    rotation: Tuple[float, ...]
    target: Tuple[float, ...]
    inner: float
    outer: float
    falloff_start: float
    falloff_end: float


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
        return self.read("<")

    def type_2(self):
        return self.read(">")

    def read(self, endian):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, endian) + start_block)
        flags = read_int(f, endian)

        class LightType(Flag):
            directional = flags >> 0 & 1
            point = flags >> 1 & 1
            target_spot = flags >> 2 & 1
            rotation_spot = flags >> 3 & 1
            target_area = flags >> 4 & 1
            rotation_area = flags >> 5 & 1

        f.seek(read_int(f, endian) + start_block)

        light_type = None
        if LightType.directional:
            light_type = 'SUN'
        elif LightType.point:
            light_type = 'POINT'
        elif LightType.target_spot or LightType.rotation_spot:
            light_type = 'SPOT'
        elif LightType.target_area or LightType.rotation_area:
            light_type = 'AREA'
        rot_order = None
        rotation = None
        target = None
        inner = None
        outer = None
        falloff_start = None
        falloff_end = None
        direction = None
        position = None
        light_flags = LightType

        user = read_int(f, endian)
        color = read_float_tuple(f, 4, endian)
        intensity = read_float(f, endian)

        if LightType.directional:
            direction = read_float_tuple(f, 3, endian)
        else:
            position = read_float_tuple(f, 3, endian)
            if LightType.target_area or LightType.target_spot:
                target = read_float_tuple(f, 3, endian)
            elif LightType.rotation_area or LightType.rotation_spot:
                rot_order = get_rotation_order(read_int(f, endian))
                r1 = unpack(endian+"i", f.read(4))[0] * 0.000095873799
                r2 = unpack(endian+"i", f.read(4))[0] * 0.000095873799
                r3 = unpack(endian+"i", f.read(4))[0] * 0.000095873799
                rotation = (r1, r2, r3)
            if not LightType.point:
                if light_type == 'AREA':
                    inner = read_float(f, endian)
                    outer = read_float(f, endian)
                else:
                    inner = unpack(endian+"i", f.read(4))[0] * 0.000095873799
                    outer = unpack(endian+"i", f.read(4))[0] * 0.000095873799
            falloff_start = read_float(f, endian)
            falloff_end = read_float(f, endian)
        light = Light(light_type, light_flags, user, color, intensity, direction, position, rot_order, rotation, target,
                      inner, outer, falloff_start, falloff_end)
        f.seek(end_of_block)
        return light
