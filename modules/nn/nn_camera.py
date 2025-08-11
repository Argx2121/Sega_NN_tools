from ..util import *
from dataclasses import dataclass
from enum import Flag


@dataclass
class Camera:
    user: int
    fov: float
    aspect: float  # it's set per scene not per camera :(
    near: float
    far: float
    position: Tuple[float, ...]
    target: Tuple[float, ...]
    roll: float
    up_vector: Tuple[float, ...]
    up_target: Tuple[float, ...]
    rot_order: str
    rotation: Tuple[float, ...]


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
        f.seek(read_int(f) + start_block)
        flags = read_int(f)

        class CamFlags(Flag):
            user = flags >> 0 & 1
            fov = flags >> 1 & 1
            aspect = flags >> 2 & 1
            near = flags >> 3 & 1
            far = flags >> 4 & 1
            position = flags >> 5 & 1
            target = flags >> 6 & 1
            roll = flags >> 7 & 1
            up_vector = flags >> 8 & 1
            up_target = flags >> 9 & 1
            rot_order = flags >> 10 & 1
            rotation = flags >> 11 & 1

        f.seek(read_int(f) + start_block)

        user = None
        fov = None
        aspect = None
        near = None
        far = None
        position = None
        target = None
        roll = None
        up_vector = None
        up_target = None
        rot_order = None
        rotation = None

        if CamFlags.user:
            user = unpack("i", f.read(4))[0]
        if CamFlags.fov:
            fov = unpack("i", f.read(4))[0] * 0.000095873799
        if CamFlags.aspect:
            aspect = read_float(f)
        if CamFlags.near:
            near = read_float(f)
        if CamFlags.far:
            far = read_float(f)
        if CamFlags.position:
            position = read_float_tuple(f, 3)
        if CamFlags.target:
            target = read_float_tuple(f, 3)
        if CamFlags.roll:
            roll = unpack("i", f.read(4))[0] * 0.000095873799
        if CamFlags.up_vector:
            up_vector = read_float_tuple(f, 3)
        if CamFlags.up_target:
            up_target = read_float_tuple(f, 3)
        if CamFlags.rot_order:
            rot_order = get_rotation_order(read_int(f))
        if CamFlags.rotation:
            r1 = unpack("i", f.read(4))[0] * 0.000095873799
            r2 = unpack("i", f.read(4))[0] * 0.000095873799
            r3 = unpack("i", f.read(4))[0] * 0.000095873799
            rotation = (r1, r2, r3)
        cam = Camera(user, fov, aspect, near, far, position, target, roll, up_vector, up_target, rot_order, rotation)
        f.seek(end_of_block)
        return cam

    def type_2(self):
        f = self.f
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8
        f.seek(read_int(f, ">") + start_block)
        flags = read_int(f, ">")

        class CamFlags(Flag):
            user = flags >> 0 & 1
            fov = flags >> 1 & 1
            aspect = flags >> 2 & 1
            near = flags >> 3 & 1
            far = flags >> 4 & 1
            position = flags >> 5 & 1
            target = flags >> 6 & 1
            roll = flags >> 7 & 1
            up_vector = flags >> 8 & 1
            up_target = flags >> 9 & 1
            rot_order = flags >> 10 & 1
            rotation = flags >> 11 & 1

        f.seek(read_int(f, ">") + start_block)

        user = None
        fov = None
        aspect = None
        near = None
        far = None
        position = None
        target = None
        roll = None
        up_vector = None
        up_target = None
        rot_order = None
        rotation = None

        if CamFlags.user:
            user = unpack(">i", f.read(4))[0]
        if CamFlags.fov:
            fov = unpack(">i", f.read(4))[0] * 0.000095873799
        if CamFlags.aspect:
            aspect = read_float(f, ">")
        if CamFlags.near:
            near = read_float(f, ">")
        if CamFlags.far:
            far = read_float(f, ">")
        if CamFlags.position:
            position = read_float_tuple(f, 3, ">")
        if CamFlags.target:
            target = read_float_tuple(f, 3, ">")
        if CamFlags.roll:
            roll = unpack(">i", f.read(4))[0] * 0.000095873799
        if CamFlags.up_vector:
            up_vector = read_float_tuple(f, 3, ">")
        if CamFlags.up_target:
            up_target = read_float_tuple(f, 3, ">")
        if CamFlags.rot_order:
            rot_order = get_rotation_order(read_int(f, ">"))
        if CamFlags.rotation:
            r1 = unpack(">i", f.read(4))[0] * 0.000095873799
            r2 = unpack(">i", f.read(4))[0] * 0.000095873799
            r3 = unpack(">i", f.read(4))[0] * 0.000095873799
            rotation = (r1, r2, r3)
        cam = Camera(user, fov, aspect, near, far, position, target, roll, up_vector, up_target, rot_order, rotation)
        f.seek(end_of_block)
        return cam


class Write:
    __slots__ = ["f", "format_type", "debug", "nof0_offsets", "camera_info", "settings"]

    def __init__(self, f, format_type, debug, nof0_offsets, camera_info, settings):
        self.f = f
        self.format_type = format_type
        self.debug = debug
        self.nof0_offsets = nof0_offsets
        self.camera_info = camera_info
        self.settings = settings

    def le(self):
        return self.write("<")

    def be(self):
        return self.write(">")

    def write(self, endian):
        f = self.f
        nof0_offsets = self.nof0_offsets
        camera_info = self.camera_info
        format_type = self.format_type

        start_block = f.tell()
        block_name = "N" + format_type[-1] + "CA"
        write_string(f, bytes(block_name, 'utf-8'))
        write_integer(f, endian, 0, 0, 0)

        f.write(pack(endian + "2i", camera_info.user, int(camera_info.fov/0.000095873799)))
        write_float(f, endian, camera_info.aspect, camera_info.near, camera_info.far)
        write_float(f, endian, *camera_info.position)
        if camera_info.camera_type == 'ROTATE':
            write_integer(f, endian, get_rotation_int(camera_info.euler))
            f.write(pack(endian + "3i", int(camera_info.rotation[0]/0.000095873799),
                         int(camera_info.rotation[1]/0.000095873799), int(camera_info.rotation[2]/0.000095873799)))
        elif camera_info.camera_type == 'TRACK':
            write_float(f, endian, *camera_info.target)
            f.write(pack(endian + "1i", int(camera_info.roll/0.000095873799)))
        elif camera_info.camera_type == 'UPVECTOR':
            write_float(f, endian, *camera_info.target)
            write_float(f, endian, *camera_info.up_vector)

        pointer_to = f.tell() - start_block
        camera_types = {'ROTATE': 3135, 'TRACK': 255, 'UPVECTOR': 383}
        write_integer(f, endian, camera_types[camera_info.camera_type])
        nof0_offsets.append(f.tell() - start_block)
        write_integer(f, endian, 16 + start_block)  # honestly who cares anymore its not like its gonna change

        write_aligned(f, 16)

        end_block = f.tell()
        f.seek(start_block + 4)
        write_integer(f, "<", end_block - 8 - start_block)
        write_integer(f, endian, pointer_to)
        f.seek(end_block)

        return nof0_offsets
