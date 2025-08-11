from ..util import *
from enum import Flag
from dataclasses import dataclass


@dataclass
class AnimInfo:
    animation_interp_flags: Flag
    start: float
    stop: float
    frame_rate: float
    anim_data: list


@dataclass
class AnimSub:
    sub_flags: Flag
    sub_interpolated_flags: Flag
    sub_index: int or tuple
    sub_start: float
    sub_stop: float

    key_start: float
    key_stop: float
    key_count: int
    key_len: int
    key_offset: int

    anim_data: list


def node_flags(sub_flags):
    class SubFlags(Flag):
        frame_float = sub_flags >> 0 & 1
        frame_s_short = sub_flags >> 1 & 1
        angle_radian = sub_flags >> 2 & 1
        bam_int = sub_flags >> 3 & 1
        bam_short = sub_flags >> 4 & 1

        move_x = sub_flags >> 8 & 1
        move_y = sub_flags >> 9 & 1
        move_z = sub_flags >> 10 & 1
        rotate_x = sub_flags >> 11 & 1
        rotate_y = sub_flags >> 12 & 1
        rotate_z = sub_flags >> 13 & 1
        rotate_quat = sub_flags >> 14 & 1
        scale_x = sub_flags >> 15 & 1
        scale_y = sub_flags >> 16 & 1
        scale_z = sub_flags >> 17 & 1
        user_uint32 = sub_flags >> 18 & 1
        user_float = sub_flags >> 19 & 1
        hide = sub_flags >> 20 & 1
    return SubFlags


def camera_flags(sub_flags):
    class SubFlags(Flag):
        frame_float = sub_flags >> 0 & 1
        frame_s_short = sub_flags >> 1 & 1
        angle_radian = sub_flags >> 2 & 1
        bam_int = sub_flags >> 3 & 1
        bam_short = sub_flags >> 4 & 1

        move_x = sub_flags >> 8 & 1
        move_y = sub_flags >> 9 & 1
        move_z = sub_flags >> 10 & 1
        rotate_x = sub_flags >> 11 & 1
        rotate_y = sub_flags >> 12 & 1
        rotate_z = sub_flags >> 13 & 1
        rotate_quat = sub_flags >> 14 & 1

        target_x = sub_flags >> 18 & 1
        target_y = sub_flags >> 19 & 1
        target_z = sub_flags >> 20 & 1
        roll = sub_flags >> 21 & 1

        up_target_x = sub_flags >> 22 & 1
        up_target_y = sub_flags >> 23 & 1
        up_target_z = sub_flags >> 24 & 1
        up_vector_x = sub_flags >> 25 & 1
        up_vector_y = sub_flags >> 26 & 1
        up_vector_z = sub_flags >> 27 & 1
        fov = sub_flags >> 28 & 1
        clip_near = sub_flags >> 29 & 1
        clip_far = sub_flags >> 30 & 1
        ratio = sub_flags >> 31 & 1
    return SubFlags


def light_flags(sub_flags):
    class SubFlags(Flag):
        frame_float = sub_flags >> 0 & 1
        frame_s_short = sub_flags >> 1 & 1
        angle_radian = sub_flags >> 2 & 1
        bam_int = sub_flags >> 3 & 1
        bam_short = sub_flags >> 4 & 1

        move_x = sub_flags >> 8 & 1
        move_y = sub_flags >> 9 & 1
        move_z = sub_flags >> 10 & 1
        rotate_x = sub_flags >> 11 & 1
        rotate_y = sub_flags >> 12 & 1
        rotate_z = sub_flags >> 13 & 1
        rotate_quat = sub_flags >> 14 & 1

        target_x = sub_flags >> 18 & 1
        target_y = sub_flags >> 19 & 1
        target_z = sub_flags >> 20 & 1

        r = sub_flags >> 21 & 1
        g = sub_flags >> 22 & 1
        b = sub_flags >> 23 & 1
        a = sub_flags >> 24 & 1  # haha no
        intensity = sub_flags >> 25 & 1
        falloff_start = sub_flags >> 26 & 1
        falloff_end = sub_flags >> 27 & 1
        in_angle = sub_flags >> 28 & 1
        out_angle = sub_flags >> 29 & 1
        in_range = sub_flags >> 30 & 1
        out_range = sub_flags >> 31 & 1
    return SubFlags


def morph_flags(sub_flags):
    class SubFlags(Flag):
        frame_float = sub_flags >> 0 & 1
        frame_s_short = sub_flags >> 1 & 1
        angle_radian = sub_flags >> 2 & 1
        bam_int = sub_flags >> 3 & 1
        bam_short = sub_flags >> 4 & 1

        morph_weight = sub_flags >> 24 & 1
    return SubFlags


def material_flags(sub_flags):
    class SubFlags(Flag):
        frame_float = sub_flags >> 0 & 1
        frame_s_short = sub_flags >> 1 & 1
        angle_radian = sub_flags >> 2 & 1
        bam_int = sub_flags >> 3 & 1
        bam_short = sub_flags >> 4 & 1

        hide = sub_flags >> 8 & 1  # ????????????????
        diffuse_r = sub_flags >> 9 & 1
        diffuse_g = sub_flags >> 10 & 1
        diffuse_b = sub_flags >> 11 & 1
        alpha = sub_flags >> 12 & 1
        specular_r = sub_flags >> 13 & 1
        specular_g = sub_flags >> 14 & 1
        specular_b = sub_flags >> 15 & 1
        level = sub_flags >> 16 & 1
        gloss = sub_flags >> 17 & 1
        ambient_r = sub_flags >> 18 & 1
        ambient_g = sub_flags >> 19 & 1
        ambient_b = sub_flags >> 20 & 1
        index = sub_flags >> 21 & 1
        image_multi = sub_flags >> 22 & 1
        off_u = sub_flags >> 23 & 1
        off_v = sub_flags >> 24 & 1
        user_uint32 = sub_flags >> 25 & 1
    return SubFlags


class Read:
    __slots__ = ["f", "post_info"]

    def __init__(self, f: BinaryIO, post_info: int):
        self.f = f
        self.post_info = post_info

    def le(self):
        return self.read("<")

    def be(self):
        return self.read(">")

    def read(self, endian):
        f = self.f
        post_info = self.post_info
        start_block = f.tell() - 4
        end_of_block = start_block + read_int(f) + 8

        to_info = read_int(f, endian)
        f.seek(to_info + post_info)
        animation_interp_flags = read_int(f, endian)

        class MotionInterp(Flag):
            node = animation_interp_flags >> 0 & 1
            camera = animation_interp_flags >> 1 & 1
            light = animation_interp_flags >> 2 & 1
            morph = animation_interp_flags >> 3 & 1
            material = animation_interp_flags >> 4 & 1

            no_repeat = animation_interp_flags >> 16 & 1
            cons_repeat = animation_interp_flags >> 17 & 1
            repeat = animation_interp_flags >> 18 & 1
            mirror = animation_interp_flags >> 19 & 1
            offset = animation_interp_flags >> 20 & 1

        start, stop = read_float_tuple(f, 2, endian)
        sub_count, sub_offset = read_int_tuple(f, 2, endian)
        fps = read_float(f, endian)
        anim_info = AnimInfo(MotionInterp, start, stop, fps, [])

        sub_info = []
        f.seek(sub_offset + post_info)
        for _ in range(sub_count):
            sub_flags = read_int(f, endian)
            sub_interp_flags = read_int(f, endian)
            if MotionInterp.node:
                SubFlags = node_flags(sub_flags)
            if MotionInterp.camera:
                SubFlags = camera_flags(sub_flags)
            elif MotionInterp.light:
                SubFlags = light_flags(sub_flags)
            elif MotionInterp.morph:
                SubFlags = morph_flags(sub_flags)
            elif MotionInterp.material:
                SubFlags = material_flags(sub_flags)

            class SubInterp(Flag):
                spline = sub_interp_flags >> 0 & 1
                linear = sub_interp_flags >> 1 & 1
                constant = sub_interp_flags >> 2 & 1

                bezier = sub_interp_flags >> 4 & 1
                si_spline = sub_interp_flags >> 5 & 1
                trigger = sub_interp_flags >> 6 & 1

                quat_lerp = sub_interp_flags >> 9 & 1
                quat_slerp = sub_interp_flags >> 10 & 1
                quat_squad = sub_interp_flags >> 11 & 1

                no_repeat = sub_interp_flags >> 16 & 1
                cons_repeat = sub_interp_flags >> 17 & 1
                repeat = sub_interp_flags >> 18 & 1
                mirror = sub_interp_flags >> 19 & 1
                offset = sub_interp_flags >> 20 & 1

            if MotionInterp.material:
                sub_index = read_short_tuple(f, 2, endian)
            else:
                sub_index = read_int(f, endian)
            sub_start, sub_stop = read_float_tuple(f, 2, endian)
            sub_key_start, sub_key_stop = read_float_tuple(f, 2, endian)
            key_count, key_len, key_offset = read_int_tuple(f, 3, endian)
            sub_info.append(
                AnimSub(SubFlags, SubInterp, sub_index, sub_start, sub_stop, sub_key_start, sub_key_stop,
                        key_count, key_len, key_offset, []))

        for sub in sub_info:
            f.seek(sub.key_offset + post_info)
            sub_flag = sub.sub_flags
            sub_interp = sub.sub_interpolated_flags
            data = []

            for _ in range(sub.key_count):
                sub_data = []
                key_len = sub.key_len

                if sub_flag.frame_float:
                    sub_data.append(read_float(f, endian))
                    key_len -= 4
                elif sub_flag.frame_s_short:
                    sub_data.append(unpack(endian + "h", f.read(2))[0])
                    key_len -= 2

                if sub_interp.bezier:
                    key_len -= 16
                elif sub_interp.si_spline:
                    key_len -= 8

                while key_len:
                    if sub_flag.angle_radian:
                        sub_data.append(read_float(f, endian))
                        key_len -= 4
                    elif sub_flag.bam_int:
                        sub_data.append(unpack(endian + "i", f.read(4))[0] * 0.000095873799)
                        key_len -= 4
                    elif sub_flag.bam_short:
                        sub_data.append(unpack(endian + "h", f.read(2))[0] * 0.000095873799)
                        key_len -= 2
                    elif (MotionInterp.node or MotionInterp.material) and sub_flag.user_uint32:
                        sub_data.append(unpack(endian + "i", f.read(4))[0])
                        # yes blender doesnt let you store uints they must be ints!!!
                        key_len -= 4
                    elif MotionInterp.material and (sub_flag.index or sub_flag.hide):
                        sub_data.append(unpack(endian + "i", f.read(4))[0])
                        key_len -= 4
                    else:  # float
                        sub_data.append(read_float(f, endian))
                        key_len -= 4

                if sub_interp.bezier:
                    sub_data.append(list(read_float_tuple(f, 4, endian)))
                elif sub_interp.si_spline:
                    sub_data.append(list(read_float_tuple(f, 2, endian)))

                data.append(sub_data)

            sub.anim_data = data
        anim_info.anim_data = sub_info
        f.seek(end_of_block)
        return anim_info
