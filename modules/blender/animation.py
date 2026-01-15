import bpy
import math
from mathutils import *
from bpy.types import Object


class Animation:
    def __init__(self, nn, settings):
        self.nn = nn
        self.animation = nn.animation
        self.settings = settings
        self.fake_user = settings.fake_user
        self.name = nn.name
        self.name_strip = self.name[:-4]

    @staticmethod
    def delta_angle(dir1, dir2):
        if dir2 < 0:
            dir2 += math.pi * 2
        a = dir2 - dir1
        a += math.pi
        while a < 0:
            a += math.pi * 2
        while a > math.pi * 2:
            a -= math.pi * 2
        a -= math.pi
        return a

    def adjust_euler(self, anim_data, anim_interp, adjust_index):
        for i, a in enumerate(anim_data):
            if i == 0:
                if a[adjust_index] < 0:
                    a[adjust_index] += math.pi * 2
                    if anim_interp.bezier:
                        a[-1][1] += math.pi * 2
                        a[-1][3] += math.pi * 2
            if i > 0:
                prev = anim_data[i - 1]
                new_value = self.delta_angle(prev[adjust_index], a[adjust_index]) + prev[adjust_index]
                if anim_interp.bezier:
                    a[-1][1] = (a[-1][1] - a[adjust_index]) + new_value
                    a[-1][3] = (a[-1][3] - a[adjust_index]) + new_value
                a[adjust_index] = new_value

    @staticmethod
    def check_interp(anim_interp, kfs, ind, anim_data):
        anim_len = len(anim_data) - 1
        for i, kf in enumerate(kfs):
            if anim_interp.spline:
                kf.interpolation = 'CUBIC'
            elif anim_interp.constant:
                kf.interpolation = 'CONSTANT'
            elif anim_interp.linear or anim_interp.quat_lerp:
                kf.interpolation = 'LINEAR'
            elif anim_interp.bezier:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = "FREE"
                kf.handle_right_type = "FREE"
                sub = anim_data[ind]
                handles = sub[-1]
                kf.handle_left[0] = handles[0]
                kf.handle_left[1] = handles[1]
                kf.handle_right[0] = handles[2]
                kf.handle_right[1] = handles[3]
            elif anim_interp.si_spline:  # si as in softimage
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = "FREE"
                kf.handle_right_type = "FREE"
                if ind == 0:
                    prev = 0
                    after = anim_data[ind + 1][0]
                elif ind == anim_len:
                    prev = anim_data[ind - 1][0]
                    after = 0
                else:
                    prev = anim_data[ind - 1][0]
                    after = anim_data[ind + 1][0]
                cur = anim_data[ind][0]
                cur_handles = anim_data[ind][-1]
                kf.handle_left[0] = cur - (cur - prev) * cur_handles[0]
                kf.handle_left[1] = kf.co[1]
                kf.handle_right[0] = cur + (after - cur) * cur_handles[1]
                kf.handle_right[1] = kf.co[1]
            elif anim_interp.quat_slerp or anim_interp.quat_squad:
                pass
                # blender moment

    @staticmethod
    def check_repeat(anim_interp, curve):
        if len(curve.modifiers) > 0:
            return
        elif anim_interp.no_repeat:
            curve.update()
            modifier = curve.modifiers.new(type='LIMITS')
            modifier.use_min_x = False
            modifier.use_max_x = False
            modifier.use_min_y = True
            modifier.use_max_y = True
            modifier.use_restricted_range = True
            modifier.frame_start = curve.keyframe_points[-1].co[0]
            modifier.frame_end = 100000  # seems reasonable
        elif anim_interp.trigger:
            modifier = curve.modifiers.new('LIMITS')
            modifier.use_min_x = False
            modifier.use_max_x = False
            modifier.use_min_y = False
            modifier.use_max_y = False
        else:
            before = "NONE"
            after = "NONE"
            if anim_interp.repeat:
                before = "REPEAT"
                after = "REPEAT"
            elif anim_interp.cons_repeat:
                before = "NONE"
                after = "NONE"
            elif anim_interp.mirror:
                before = "MIRROR"
                after = "MIRROR"
            elif anim_interp.offset:
                before = "REPEAT_OFFSET"
                after = "REPEAT_OFFSET"
            modifier = curve.modifiers.new(type='CYCLES')
            modifier.mode_after = before
            modifier.mode_before = after

    @staticmethod
    def get_curve(action, data_path: str, i=-1):
        if i == -1:
            f_curve = action.fcurves.find(data_path)
            if not f_curve:
                f_curve = action.fcurves.new(data_path)
        else:
            f_curve = action.fcurves.find(data_path, index=i)
            if not f_curve:
                f_curve = action.fcurves.new(data_path, index=i)
        return f_curve

    def anim_var(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        if anim_flags:
            f_curve = self.get_curve(action, data_path)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def anim_xyz(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        [move_x, move_y, move_z] = anim_flags
        if move_x and move_y and move_z:
            x_curve = self.get_curve(action, data_path, 0)
            y_curve = self.get_curve(action, data_path, 1)
            z_curve = self.get_curve(action, data_path, 2)
            for i, sub in enumerate(anim_data):
                kfx = x_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], sub[2], options={"FAST"})
                kfz = z_curve.keyframe_points.insert(sub[0], sub[3], options={"FAST"})
                self.check_interp(anim_interp, [kfx, kfy, kfz], i, anim_data)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            self.check_repeat(anim_interp, z_curve)
            x_curve.update()
            y_curve.update()
            z_curve.update()
        elif move_x:
            f_curve = self.get_curve(action, data_path, 0)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_y:
            f_curve = self.get_curve(action, data_path, 1)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_z:
            f_curve = self.get_curve(action, data_path, 2)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def anim_uv(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        [move_x, move_y] = anim_flags
        if move_x and move_y:
            # its okay guys they dont do uv with handles lol
            x_curve = self.get_curve(action, data_path, 0)
            y_curve = self.get_curve(action, data_path, 1)
            for i, sub in enumerate(anim_data):
                kfx = x_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], -sub[2], options={"FAST"})
                self.check_interp(anim_interp, [kfx, kfy], i, anim_data)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            x_curve.update()
            y_curve.update()
        elif move_x:
            f_curve = self.get_curve(action, data_path, 0)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_y:
            f_curve = self.get_curve(action, data_path, 1)
            if anim_interp.bezier:
                for i, sub in enumerate(anim_data):
                    sub[-1][1] = -sub[-1][1]
                    sub[-1][8] = -sub[-1][8]
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], -sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def rotation_quat(self, rotate_quat, anim_data, anim_interp, action, data_path: str):
        if rotate_quat:
            w_curve = self.get_curve(action, data_path, 0)
            x_curve = self.get_curve(action, data_path, 1)
            y_curve = self.get_curve(action, data_path, 2)
            z_curve = self.get_curve(action, data_path, 3)
            for i, sub in enumerate(anim_data):
                w, x, y, z = sub[4], sub[1], sub[2], sub[3]
                sub[1], sub[2], sub[3], sub[4] = w, x, y, z
                kfw = w_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfx = x_curve.keyframe_points.insert(sub[0], sub[2], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], sub[3], options={"FAST"})
                kfz = z_curve.keyframe_points.insert(sub[0], sub[4], options={"FAST"})
                self.check_interp(anim_interp, [kfw, kfx, kfy, kfz], i, anim_data)
            self.check_repeat(anim_interp, w_curve)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            self.check_repeat(anim_interp, z_curve)
            w_curve.update()
            x_curve.update()
            y_curve.update()
            z_curve.update()

    def node_animation(self):
        obj_object: Object = bpy.context.object
        obj_animation_name = self.nn.name
        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        obj_object.animation_data_create()
        o_action = bpy.data.actions.new(obj_animation_name)
        if self.fake_user:
            o_action.use_fake_user = True
        obj_object.animation_data.action = o_action
        o_action.use_frame_range = True
        o_action.frame_start = self.animation.start
        o_action.frame_end = self.animation.stop
        obj = obj_object.pose.bones
        obj2 = obj_object.data.bones

        adjust_mat = []
        adjust_rot = []
        adjust_pos = []
        adjust_scale = []
        for bone, p in zip(obj2, obj):
            bone_mat = bone.matrix_local
            if bone.parent:
                pl, pr, ps = p.parent.matrix.decompose()
                if p.nn_reset_scale_x:
                    ps.x = 1
                if p.nn_reset_scale_y:
                    ps.y = 1
                if p.nn_reset_scale_z:
                    ps.z = 1
                if not bone.use_inherit_rotation:
                    pr = Euler()
                    ps = Vector((1, 1, 1))
                parent_mat = Matrix.LocRotScale(pl, pr, ps)
                bone_mat = parent_mat.inverted() @ bone_mat
                adjust_rot.append(Euler(p.nn_euler_values, p.nn_euler_rotation))
                adjust_pos.append(Vector(p.nn_position_values))
                adjust_scale.append(Vector(p.nn_scale_values))
                bone_mat = bone_mat.inverted()
            else:
                adjust_rot.append(Euler(p.nn_euler_values, p.nn_euler_rotation))
                adjust_pos.append(Vector(p.nn_position_values))
                adjust_scale.append(Vector(p.nn_scale_values))
            adjust_mat.append(bone_mat)

        used_bones = set()

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data
            bone_index = anim.sub_index
            used_bones.add(bone_index)
            if anim_flag.rotate_x and anim_flag.rotate_y and anim_flag.rotate_z:
                self.adjust_euler(anim_data, anim_interp, 1)
                self.adjust_euler(anim_data, anim_interp, 2)
                self.adjust_euler(anim_data, anim_interp, 3)
            elif anim_flag.rotate_x or anim_flag.rotate_y or anim_flag.rotate_z:
                self.adjust_euler(anim_data, anim_interp, 1)

            self.anim_xyz([anim_flag.rotate_x, anim_flag.rotate_y, anim_flag.rotate_z], anim_data, anim_interp,
                          o_action, 'pose.bones[' + str(bone_index) + '].rotation_euler')

            self.anim_xyz([anim_flag.move_x, anim_flag.move_y, anim_flag.move_z], anim_data, anim_interp,
                          o_action, 'pose.bones[' + str(bone_index) + '].location')

            self.anim_xyz([anim_flag.scale_x, anim_flag.scale_y, anim_flag.scale_z], anim_data, anim_interp,
                          o_action, 'pose.bones[' + str(bone_index) + '].scale')

            self.rotation_quat(anim_flag.rotate_quat, anim_data, anim_interp, o_action,
                               'pose.bones[' + str(bone_index) + '].rotation_quaternion')

            # node specific
            if anim_flag.hide:
                f_curve = o_action.fcurves.new('pose.bones[' + str(bone_index) + '].nn_hide')
                for i, sub in enumerate(anim_data):
                    kf = f_curve.keyframe_points.insert(sub[0], bool(sub[1]), options={"FAST"})
                    self.check_interp(anim_interp, [kf], i, anim_data)
                self.check_repeat(anim_interp, f_curve)
                f_curve.update()
            elif anim_flag.user_uint32:
                f_curve = self.get_curve(o_action, 'pose.bones[' + str(bone_index) + '].nn_user_int')
                t_curve = self.get_curve(o_action, 'pose.bones[' + str(bone_index) + '].nn_user_type')
                for i, sub in enumerate(anim_data):
                    t_curve.keyframe_points.insert(sub[0], 0, options={"FAST"})
                    kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                    self.check_interp(anim_interp, [kf], i, anim_data)
                self.check_repeat(anim_interp, f_curve)
                f_curve.update()
            elif anim_flag.user_float:
                f_curve = self.get_curve(o_action, 'pose.bones[' + str(bone_index) + '].nn_user_float')
                t_curve = self.get_curve(o_action, 'pose.bones[' + str(bone_index) + '].nn_user_type')
                for i, sub in enumerate(anim_data):
                    t_curve.keyframe_points.insert(sub[0], 1, options={"FAST"})
                    kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                    self.check_interp(anim_interp, [kf], i, anim_data)
                self.check_repeat(anim_interp, f_curve)
                f_curve.update()

        # fix up for blender
        for bone_index in used_bones:
            rotation_order = obj[bone_index].nn_euler_rotation
            r_curve_x = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_euler", index=0)
            r_curve_y = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_euler", index=1)
            r_curve_z = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_euler", index=2)
            rotation_data = []
            p_curve_x = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].location", index=0)
            p_curve_y = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].location", index=1)
            p_curve_z = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].location", index=2)
            position_data = []
            s_curve_x = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].scale", index=0)
            s_curve_y = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].scale", index=1)
            s_curve_z = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].scale", index=2)
            scale_data = []
            w_curve = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_quaternion", index=0)
            x_curve = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_quaternion", index=1)
            y_curve = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_quaternion", index=2)
            z_curve = o_action.fcurves.find("pose.bones[" + str(bone_index) + "].rotation_quaternion", index=3)
            if w_curve:
                for wkf, xkf, ykf, zkf in zip(
                        w_curve.keyframe_points, x_curve.keyframe_points, y_curve.keyframe_points,
                        z_curve.keyframe_points):
                    rot = Quaternion((wkf.co[1], xkf.co[1], ykf.co[1], zkf.co[1]))
                    rot.rotate(adjust_mat[bone_index])
                    wkf.co[1], xkf.co[1], ykf.co[1], zkf.co[1] = rot.w, rot.x, rot.y, rot.z
                w_curve.update()
                x_curve.update()
                y_curve.update()
                z_curve.update()
            if r_curve_x or r_curve_y or r_curve_z:
                first_frame = []
                last_frame = []
                if r_curve_x:
                    first_frame.append(r_curve_x.keyframe_points[0].co[0])
                    last_frame.append(r_curve_x.keyframe_points[-1].co[0])
                if r_curve_y:
                    first_frame.append(r_curve_y.keyframe_points[0].co[0])
                    last_frame.append(r_curve_y.keyframe_points[-1].co[0])
                if r_curve_z:
                    first_frame.append(r_curve_z.keyframe_points[0].co[0])
                    last_frame.append(r_curve_z.keyframe_points[-1].co[0])
                first_frame = min(first_frame)
                last_frame = max(last_frame)
                for frame in range(int(first_frame), int(last_frame) + 1):
                    if r_curve_x:
                        x_value = r_curve_x.evaluate(frame)
                    else:
                        x_value = adjust_rot[bone_index].x
                    if r_curve_y:
                        y_value = r_curve_y.evaluate(frame)
                    else:
                        y_value = adjust_rot[bone_index].y
                    if r_curve_z:
                        z_value = r_curve_z.evaluate(frame)
                    else:
                        z_value = adjust_rot[bone_index].z
                    rot = Euler((x_value, y_value, z_value), rotation_order).to_quaternion()
                    rot.rotate(adjust_mat[bone_index])
                    rotation_data.append(rot)
                data_path = "pose.bones[" + str(bone_index) + "].rotation_quaternion"
                action = o_action
                w_curve = action.fcurves.new(data_path, index=0)
                x_curve = action.fcurves.new(data_path, index=1)
                y_curve = action.fcurves.new(data_path, index=2)
                z_curve = action.fcurves.new(data_path, index=3)
                i = first_frame - 1
                obj[bone_index].rotation_mode = 'QUATERNION'
                for a in rotation_data:
                    i += 1
                    kfw = w_curve.keyframe_points.insert(i, a.w, options={"FAST"})
                    kfx = x_curve.keyframe_points.insert(i, a.x, options={"FAST"})
                    kfy = y_curve.keyframe_points.insert(i, a.y, options={"FAST"})
                    kfz = z_curve.keyframe_points.insert(i, a.z, options={"FAST"})
                w_curve.update()
                x_curve.update()
                y_curve.update()
                z_curve.update()
                if r_curve_x:
                    o_action.fcurves.remove(r_curve_x)
                if r_curve_y:
                    o_action.fcurves.remove(r_curve_y)
                if r_curve_z:
                    o_action.fcurves.remove(r_curve_z)
            if p_curve_x or p_curve_y or p_curve_z:
                for frame in range(int(o_action.frame_start), int(o_action.frame_end) + 1):
                    if p_curve_x:
                        x_value = p_curve_x.evaluate(frame)
                    else:
                        x_value = adjust_pos[bone_index].x
                    if p_curve_y:
                        y_value = p_curve_y.evaluate(frame)
                    else:
                        y_value = adjust_pos[bone_index].y
                    if p_curve_z:
                        z_value = p_curve_z.evaluate(frame)
                    else:
                        z_value = adjust_pos[bone_index].z
                    pos = Vector((x_value, y_value, z_value)) - adjust_pos[bone_index] #@ adjust_mat[bone_index].inverted()
                    if obj2[bone_index].parent:
                        adj_mat = obj2[bone_index].parent.matrix_local.inverted()
                        pp, pr, ps = adj_mat.decompose()
                        adj_mat = Matrix.LocRotScale(None, pr, ps)
                        pos = adj_mat @ pos
                    else:
                        adj_mat = adjust_mat[bone_index]
                    #pos = adjust_mat[bone_index] @ pos
                    position_data.append(pos)
                if p_curve_x:
                    for kf in p_curve_x.keyframe_points:
                        new_value = position_data[int(kf.co[0]) - int(o_action.frame_start)].x
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if p_curve_y:
                    for kf in p_curve_y.keyframe_points:
                        new_value = position_data[int(kf.co[0]) - int(o_action.frame_start)].y
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if p_curve_z:
                    for kf in p_curve_z.keyframe_points:
                        new_value = position_data[int(kf.co[0]) - int(o_action.frame_start)].z
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if p_curve_x:
                    p_curve_x.update()
                if p_curve_y:
                    p_curve_y.update()
                if p_curve_z:
                    p_curve_z.update()
            if s_curve_x or s_curve_y or s_curve_z:
                for frame in range(int(o_action.frame_start), int(o_action.frame_end) + 1):
                    if s_curve_x:
                        x_value = s_curve_x.evaluate(frame)
                    else:
                        x_value = adjust_scale[bone_index].x
                    if s_curve_y:
                        y_value = s_curve_y.evaluate(frame)
                    else:
                        y_value = adjust_scale[bone_index].y
                    if s_curve_z:
                        z_value = s_curve_z.evaluate(frame)
                    else:
                        z_value = adjust_scale[bone_index].z
                    pos = Vector((x_value, y_value, z_value))
                    pos.x = pos.x / adjust_mat[bone_index].inverted().to_scale().x
                    pos.y = pos.y / adjust_mat[bone_index].inverted().to_scale().y
                    pos.z = pos.z / adjust_mat[bone_index].inverted().to_scale().z
                    scale_data.append(pos)
                if s_curve_x:
                    for kf in s_curve_x.keyframe_points:
                        new_value = scale_data[int(kf.co[0]) - int(o_action.frame_start)].x
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if s_curve_y:
                    for kf in s_curve_y.keyframe_points:
                        new_value = scale_data[int(kf.co[0]) - int(o_action.frame_start)].y
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if s_curve_z:
                    for kf in s_curve_z.keyframe_points:
                        new_value = scale_data[int(kf.co[0]) - int(o_action.frame_start)].z
                        if kf.interpolation == 'BEZIER':
                            kf.handle_left[1] = (kf.handle_left[1] - kf.co[1]) + new_value
                            kf.handle_right[1] = (kf.handle_right[1] - kf.co[1]) + new_value
                        kf.co[1] = new_value
                if s_curve_x:
                    s_curve_x.update()
                if s_curve_y:
                    s_curve_y.update()
                if s_curve_z:
                    s_curve_z.update()

    def material_animation(self):
        obj_object: Object = bpy.context.object
        material_count = obj_object.data.nn_material_count
        materials = [obj_object.data.nn_materials[a].material for a in range(material_count)]
        gno_nodes = False
        xno_nodes = False
        for material in materials:
            node_ids = set([a.bl_idname for a in material.node_tree.nodes])
            if material.use_nodes:
                if 'ShaderNodeGNOShaderInit' in node_ids:
                    gno_nodes = True
                    break
                if 'ShaderNodeXNOShaderInit' in node_ids:
                    xno_nodes = True
                    break
        if gno_nodes:
            self.material_animation_complex("G")
        elif xno_nodes:
            self.material_animation_complex("X")
        else:
            self.material_animation_simple()

    def material_animation_complex(self, type_str):
        obj_object: Object = bpy.context.object
        obj_animation_name = self.nn.name
        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        material_count = obj_object.data.nn_material_count
        materials = [obj_object.data.nn_materials[a].material for a in range(material_count)]
        material_actions = [None for _ in range(material_count)]
        material_nodes = [{} for _ in range(material_count)]
        animated_materials = set()

        for anim in self.animation.anim_data:
            material_index, _ = anim.sub_index
            animated_materials.add(material_index)

        for mat in animated_materials:
            material = materials[mat]
            material.node_tree.animation_data_create()
            action = bpy.data.actions.new(obj_animation_name)
            material_actions[mat] = action
            if self.fake_user:
                action.use_fake_user = True
            material.node_tree.animation_data.action = action
            action.use_frame_range = True
            action.frame_start = self.animation.start
            action.frame_end = self.animation.stop

            nodes = {}

            for node in material.node_tree.nodes:
                if node.bl_idname == 'ShaderNode' + type_str + 'NOShaderInit':
                    nodes.update({'init': node.name})
                    break
            from_socket_to_socket = dict([[link.from_socket, link.to_socket] for link in material.node_tree.links])
            to_socket_from_socket = dict([[link.to_socket, link.from_socket] for link in material.node_tree.links])
            next_node = from_socket_to_socket.get(node.outputs[0]).node
            node_ind = 0
            while next_node.bl_idname != 'ShaderNode' + type_str + 'NOShader':
                mix_node = next_node
                if to_socket_from_socket.get(mix_node.inputs["Color 2"]):
                    nodes.update({'mix' + str(node_ind): (mix_node.name, mix_node.bl_idname == 'ShaderNode' + type_str + 'NOMixRGB')})
                    img_node = to_socket_from_socket.get(mix_node.inputs["Color 2"]).node
                    nodes.update({'img' + str(node_ind): img_node.name})
                    vec_node = to_socket_from_socket.get(img_node.inputs["Vector"]).node
                    nodes.update({'vector' + str(node_ind): vec_node.name})

                node_ind += 1
                next_node = from_socket_to_socket.get(next_node.outputs[0]).node

            nodes.update({'shader': next_node.name})
            material_nodes[mat] = nodes

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data
            material_index, texture_index = anim.sub_index
            action = material_actions[material_index]
            nodes = material_nodes[material_index]

            if anim_flag.hide or anim_flag.user_uint32:
                shader = nodes.get('shader')
                if anim_flag.hide:
                    raise NotImplementedError('Hide not implemented')
                data_path = 'nodes["' + shader + '"].inputs[8].default_value'
                self.anim_var(anim_flag.level, anim_data, anim_interp, action, data_path)
            elif anim_flag.off_u or anim_flag.off_v:
                vect = nodes.get('vector' + str(texture_index))
                data_path = 'nodes["' + vect + '"].inputs[1].default_value'
                self.anim_uv([anim_flag.off_u, anim_flag.off_v], anim_data, anim_interp, action, data_path)
            elif anim_flag.index:
                img = nodes.get('img' + str(texture_index))
                data_path = 'nodes["' + img + '"].texture_2'
                self.anim_var(anim_flag.index, anim_data, anim_interp, action, data_path)
            elif anim_flag.image_multi:
                mix = nodes.get('mix' + str(texture_index))
                data_path = 'nodes["' + mix[0] + '"].inputs[4].default_value'
                if not mix[1]:
                    data_path = 'nodes["' + mix[0] + '"].inputs[5].default_value'
                self.anim_var(anim_flag.image_multi, anim_data, anim_interp, action, data_path)
            else:
                init = nodes.get('init')
                data_path = 'nodes["' + init + '"].inputs[0].default_value'
                self.anim_xyz([anim_flag.diffuse_r, anim_flag.diffuse_g, anim_flag.diffuse_b], anim_data, anim_interp,
                              action, data_path)

                data_path = 'nodes["' + init + '"].inputs[1].default_value'
                self.anim_var(anim_flag.alpha, anim_data, anim_interp, action, data_path)

                data_path = 'nodes["' + init + '"].inputs[2].default_value'
                self.anim_xyz([anim_flag.ambient_r, anim_flag.ambient_g, anim_flag.ambient_b], anim_data, anim_interp,
                              action, data_path)

                data_path = 'nodes["' + init + '"].inputs[3].default_value'
                self.anim_xyz([anim_flag.specular_r, anim_flag.specular_g, anim_flag.specular_b], anim_data,
                              anim_interp,
                              action, data_path)

                data_path = 'nodes["' + init + '"].inputs[5].default_value'
                self.anim_var(anim_flag.level, anim_data, anim_interp, action, data_path)

                data_path = 'nodes["' + init + '"].inputs[6].default_value'
                self.anim_var(anim_flag.gloss, anim_data, anim_interp, action, data_path)

    def material_animation_simple(self):  # hello!!!!!!!!!!!! anything that isnt lore accurate shaders goes here!!!!!!!!!
        obj_object: Object = bpy.context.object
        obj_animation_name = self.nn.name
        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        material_count = obj_object.data.nn_material_count
        materials = [obj_object.data.nn_materials[a].material for a in range(material_count)]
        material_actions = [None for _ in range(material_count)]
        animated_materials = set()

        for anim in self.animation.anim_data:
            material_index, _ = anim.sub_index
            animated_materials.add(material_index)

        for mat in animated_materials:
            material = materials[mat]
            material.node_tree.animation_data_create()
            action = bpy.data.actions.new(obj_animation_name)
            material_actions[mat] = action
            if self.fake_user:
                action.use_fake_user = True
            material.node_tree.animation_data.action = action
            action.use_frame_range = True
            action.frame_start = self.animation.start
            action.frame_end = self.animation.stop

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data
            material_index, texture_index = anim.sub_index
            action = material_actions[material_index]
            image_nodes = [node for node in materials[material_index].node_tree.nodes if node.bl_idname == 'ShaderNodeTexImage']
            # yup notice how you write the data and blender doesnt use it? very girlboss of you blender
            # id make nodes have a uv / offset input but then its not really fbx exporter friendly is it

            if anim_flag.off_u or anim_flag.off_v:
                data_path = 'nodes["' + image_nodes[texture_index].name + '"].texture_mapping.translation'
                self.anim_uv([anim_flag.off_u, anim_flag.off_v], anim_data, anim_interp, action, data_path)
            else:
                data_path = 'nodes["RGB"].inputs[0].default_value'
                self.anim_xyz([anim_flag.diffuse_r, anim_flag.diffuse_g, anim_flag.diffuse_b], anim_data, anim_interp,
                              action, data_path)

                data_path = 'nodes["Value"].inputs[1].default_value'
                self.anim_var(anim_flag.alpha, anim_data, anim_interp, action, data_path)

    def morph_animation(self):
        # im straight up morphing it. my verts.
        obj_object: Object = bpy.context.object
        obj_animation_name = self.nn.name
        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        meshes = [a for a in obj_object.children if a.type == 'MESH' and a.data.shape_keys]
        action = bpy.data.actions.new(obj_animation_name)
        if self.fake_user:
            action.use_fake_user = True
        action.use_frame_range = True
        action.frame_start = self.animation.start
        action.frame_end = self.animation.stop

        for mesh in meshes:
            mesh.data.shape_keys.animation_data_create()
            mesh.data.shape_keys.animation_data.action = action

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data
            morph_index = anim.sub_index
            if anim_flag.morph_weight:  # i mean what else is it gonna be?? lol??
                d_path = meshes[0].data.shape_keys.key_blocks[morph_index+1].name
                data_path = 'key_blocks["' + d_path + '"].value'
                self.anim_var(anim_flag.morph_weight, anim_data, anim_interp, action, data_path)

    def camera_animation(self, obj_object, target_object, up_target_object):
        obj_animation_name = self.name_strip + "_Animation_Obj"
        target_animation_name = self.name_strip + "_Animation_Target"
        up_target_animation_name = self.name_strip + "_Animation_Up_Target"
        cam_animation_name = self.name_strip + "_Animation_Cam"

        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        obj_object.animation_data_create()
        o_action = bpy.data.actions.new(obj_animation_name)
        if self.fake_user:
            o_action.use_fake_user = True
        obj_object.animation_data.action = o_action
        o_action.use_frame_range = True
        o_action.frame_start = self.animation.start
        o_action.frame_end = self.animation.stop

        obj_object.data.animation_data_create()
        c_action = bpy.data.actions.new(cam_animation_name)
        if self.fake_user:
            c_action.use_fake_user = True
        obj_object.data.animation_data.action = c_action
        c_action.use_frame_range = True
        c_action.frame_start = self.animation.start
        c_action.frame_end = self.animation.stop

        t_action = None
        u_action = None

        if target_object:
            target_object.animation_data_create()
            t_action = bpy.data.actions.new(target_animation_name)
            if self.fake_user:
                t_action.use_fake_user = True
            target_object.animation_data.action = t_action
            t_action.use_frame_range = True
            t_action.frame_start = self.animation.start
            t_action.frame_end = self.animation.stop
        if up_target_object:
            up_target_object.animation_data_create()
            u_action = bpy.data.actions.new(up_target_animation_name)
            if self.fake_user:
                u_action.use_fake_user = True
            up_target_object.animation_data.action = u_action
            u_action.use_frame_range = True
            u_action.frame_start = self.animation.start
            u_action.frame_end = self.animation.stop

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data

            self.anim_xyz([anim_flag.move_x, anim_flag.move_y, anim_flag.move_z], anim_data, anim_interp,
                          o_action, "location")
            self.anim_xyz([anim_flag.target_x, anim_flag.target_y, anim_flag.target_z], anim_data,
                          anim_interp, t_action, "location")
            self.anim_xyz([anim_flag.up_target_x, anim_flag.up_target_y, anim_flag.up_target_z], anim_data,
                          anim_interp, u_action, "location")
            self.anim_xyz([anim_flag.up_vector_x, anim_flag.up_vector_y, anim_flag.up_vector_z], anim_data,
                          anim_interp, u_action, "location")

            self.anim_xyz([anim_flag.rotate_x, anim_flag.rotate_y, anim_flag.rotate_z], anim_data,
                          anim_interp, o_action, "rotation_euler")

            if anim_flag.rotate_quat:
                obj_object.rotation_mode = 'QUATERNION'
            self.rotation_quat(anim_flag.rotate_quat, anim_data, anim_interp, o_action, "rotation_quaternion")

            # camera specific
            self.anim_var(anim_flag.clip_near, anim_data, anim_interp, c_action, "clip_start")
            self.anim_var(anim_flag.clip_far, anim_data, anim_interp, c_action, "clip_end")
            self.anim_var(anim_flag.ratio, anim_data, anim_interp, c_action, "nn_aspect")
            if anim_flag.fov:
                for sub in anim_data:
                    sub[1] = 18 / math.tan(sub[1] * 0.5)
                if anim_interp.bezier:
                    for sub in anim_data:
                        sub[-1][1] = 18 / math.tan(sub[-1][1] * 0.5)
                        sub[-1][3] = 18 / math.tan(sub[-1][3] * 0.5)
                self.anim_var(anim_flag.fov, anim_data, anim_interp, c_action, "lens")
            if anim_flag.roll and target_object:
                f_curve = self.get_curve(t_action, 'rotation_euler', 2)
                for i, sub in enumerate(anim_data):
                    kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                    self.check_interp(anim_interp, [kf], i, anim_data)
                self.check_repeat(anim_interp, f_curve)
                f_curve.update()

        if self.nn.camera.up_vector or self.nn.camera.up_target:
            u_curve_x = u_action.fcurves.find("location", index=0)
            u_curve_y = u_action.fcurves.find("location", index=1)
            u_curve_z = u_action.fcurves.find("location", index=2)

            t_curve_x = t_action.fcurves.find("location", index=0)
            t_curve_y = t_action.fcurves.find("location", index=1)
            t_curve_z = t_action.fcurves.find("location", index=2)

            if self.nn.camera.up_target:
                o_curve_x = o_action.fcurves.find("location", index=0)
                o_curve_y = o_action.fcurves.find("location", index=1)
                o_curve_z = o_action.fcurves.find("location", index=2)
                for kf in u_curve_x.keyframe_points:
                    kf.co[1] += t_curve_x.evaluate(kf.co[0]) - o_curve_x.evaluate(kf.co[0])
                for kf in u_curve_y.keyframe_points:
                    kf.co[1] += t_curve_y.evaluate(kf.co[0]) - o_curve_y.evaluate(kf.co[0])
                for kf in u_curve_z.keyframe_points:
                    kf.co[1] += t_curve_z.evaluate(kf.co[0]) - o_curve_z.evaluate(kf.co[0])
            else:
                for kf in u_curve_x.keyframe_points:
                    kf.co[1] += t_curve_x.evaluate(kf.co[0])
                for kf in u_curve_y.keyframe_points:
                    kf.co[1] += t_curve_y.evaluate(kf.co[0])
                for kf in u_curve_z.keyframe_points:
                    kf.co[1] += t_curve_z.evaluate(kf.co[0])
            u_curve_x.update()
            u_curve_y.update()
            u_curve_z.update()

    def light_animation(self, obj_object, target_object):
        obj_animation_name = self.name_strip + "_Animation_Obj"
        target_animation_name = self.name_strip + "_Animation_Target"
        light_animation_name = self.name_strip + "_Animation_Light"

        bpy.context.scene.render.fps = int(self.animation.frame_rate)
        obj_object.nn_frame_rate = int(self.animation.frame_rate)

        obj_object.animation_data_create()
        o_action = bpy.data.actions.new(obj_animation_name)
        if self.fake_user:
            o_action.use_fake_user = True
        obj_object.animation_data.action = o_action
        o_action.use_frame_range = True
        o_action.frame_start = self.animation.start
        o_action.frame_end = self.animation.stop

        obj_object.data.animation_data_create()
        l_action = bpy.data.actions.new(light_animation_name)
        if self.fake_user:
            l_action.use_fake_user = True
        obj_object.data.animation_data.action = l_action
        l_action.use_frame_range = True
        l_action.frame_start = self.animation.start
        l_action.frame_end = self.animation.stop

        t_action = None

        if target_object:
            target_object.animation_data_create()
            t_action = bpy.data.actions.new(target_animation_name)
            if self.fake_user:
                t_action.use_fake_user = True
            target_object.animation_data.action = t_action
            t_action.use_frame_range = True
            t_action.frame_start = self.animation.start
            t_action.frame_end = self.animation.stop

        for anim in self.animation.anim_data:
            anim_interp = anim.sub_interpolated_flags
            anim_flag = anim.sub_flags
            anim_data = anim.anim_data

            self.anim_xyz([anim_flag.move_x, anim_flag.move_y, anim_flag.move_z], anim_data, anim_interp,
                          o_action, "location")
            self.anim_xyz([anim_flag.rotate_x, anim_flag.rotate_y, anim_flag.rotate_z], anim_data,
                          anim_interp, o_action, "rotation_euler")

            if anim_flag.rotate_quat:
                obj_object.rotation_mode = 'QUATERNION'
            self.rotation_quat(anim_flag.rotate_quat, anim_data, anim_interp, o_action, "rotation_quaternion")

            self.anim_xyz([anim_flag.target_x, anim_flag.target_y, anim_flag.target_z], anim_data,
                          anim_interp, t_action, "location")

            self.anim_xyz([anim_flag.r, anim_flag.g, anim_flag.b], anim_data, anim_interp,
                          l_action, "color")

            # light specific
            self.anim_var(anim_flag.intensity, anim_data, anim_interp, l_action, "intensity")
            self.anim_var(anim_flag.falloff_start, anim_data, anim_interp, l_action, "nn_falloff_start")
            self.anim_var(anim_flag.falloff_end, anim_data, anim_interp, l_action, "cutoff_distance")
            self.anim_var(anim_flag.out_range, anim_data, anim_interp, l_action, "size")
            self.anim_var(anim_flag.in_range, anim_data, anim_interp, l_action, "nn_inner_size")
            self.anim_var(anim_flag.out_angle, anim_data, anim_interp, l_action, "spot_size")
            if anim_flag.in_angle:
                f_curve = l_action.fcurves.find('spot_size')
                if f_curve:
                    for sub in anim_data:
                        sub[1] = 1 - (sub[1] / f_curve.evaluate(sub[0]))
                    if anim_interp.bezier:
                        for sub in anim_data:
                            sub[-1][1] = (sub[-1][1] / f_curve.evaluate(sub[0]))
                            sub[-1][3] = (sub[-1][3] / f_curve.evaluate(sub[0]))
                else:
                    for sub in anim_data:
                        sub[1] = 1 - (sub[1] / obj_object.data.spot_size)
                    if anim_interp.bezier:
                        for sub in anim_data:
                            sub[-1][1] = (sub[-1][1] / obj_object.data.spot_size)
                            sub[-1][3] = (sub[-1][3] / obj_object.data.spot_size)
                self.anim_var(anim_flag.in_angle, anim_data, anim_interp, l_action, "spot_blend")


class AnimationInfo:
    def __init__(self, settings):
        self.settings = settings

    @staticmethod
    def check_interp(anim_interp, kfs, ind, anim_data):
        anim_len = len(anim_data) - 1
        for i, kf in enumerate(kfs):
            if anim_interp.spline:
                kf.interpolation = 'CUBIC'
            elif anim_interp.constant:
                kf.interpolation = 'CONSTANT'
            elif anim_interp.linear or anim_interp.quat_lerp:
                kf.interpolation = 'LINEAR'
            elif anim_interp.bezier:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = "FREE"
                kf.handle_right_type = "FREE"
                sub = anim_data[ind]
                handles = sub[-1]
                kf.handle_left[0] = handles[0]
                kf.handle_left[1] = handles[1]
                kf.handle_right[0] = handles[2]
                kf.handle_right[1] = handles[3]
            elif anim_interp.si_spline:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = "FREE"
                kf.handle_right_type = "FREE"
                if ind == 0:
                    prev = 0
                    after = anim_data[ind + 1][0]
                elif ind == anim_len:
                    prev = anim_data[ind - 1][0]
                    after = 0
                else:
                    prev = anim_data[ind - 1][0]
                    after = anim_data[ind + 1][0]
                cur = anim_data[ind][0]
                cur_handles = anim_data[ind][-1]
                kf.handle_left[0] = cur - (cur - prev) * cur_handles[0]
                kf.handle_left[1] = kf.co[1]
                kf.handle_right[0] = cur + (after - cur) * cur_handles[1]
                kf.handle_right[1] = kf.co[1]
            elif anim_interp.quat_slerp or anim_interp.quat_squad:
                pass
                # blender moment

    @staticmethod
    def check_repeat(curve):
        if len(curve.modifiers) == 0:
            return 'CONSTANT'
        elif curve.modifiers[0].type == 'CYCLES':
            mod = curve.modifiers[0]
            if mod.mode_after == mod.mode_before:
                if mod.mode_after == 'REPEAT':
                    return 'REPEAT'
                elif mod.mode_after == 'NONE':
                    return 'CONSTANT'
                elif mod.mode_after == 'MIRROR':
                    return 'MIRROR'
                elif mod.mode_after == 'REPEAT_OFFSET':
                    return 'OFFSET'
        elif curve.modifiers[0].type == 'LIMITS':
            mod = curve.modifiers[0]
            if mod.use_max_x == mod.use_max_y is False:
                if mod.use_min_y == mod.use_min_x:
                    if mod.use_min_y:
                        return 'NO REPEAT'
                    else:
                        return 'TRIGGER'
        return 'CONSTANT'

    @staticmethod
    def get_curve(action, data_path: str, i=-1):
        if i == -1:
            f_curve = action.fcurves.find(data_path)
        else:
            f_curve = action.fcurves.find(data_path, index=i)
        return f_curve

    def anim_var(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        if anim_flags:
            f_curve = self.get_curve(action, data_path)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def anim_xyz(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        [move_x, move_y, move_z] = anim_flags
        if move_x and move_y and move_z:
            x_curve = self.get_curve(action, data_path, 0)
            y_curve = self.get_curve(action, data_path, 1)
            z_curve = self.get_curve(action, data_path, 2)
            for i, sub in enumerate(anim_data):
                kfx = x_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], sub[2], options={"FAST"})
                kfz = z_curve.keyframe_points.insert(sub[0], sub[3], options={"FAST"})
                self.check_interp(anim_interp, [kfx, kfy, kfz], i, anim_data)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            self.check_repeat(anim_interp, z_curve)
            x_curve.update()
            y_curve.update()
            z_curve.update()
        elif move_x:
            f_curve = self.get_curve(action, data_path, 0)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_y:
            f_curve = self.get_curve(action, data_path, 1)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_z:
            f_curve = self.get_curve(action, data_path, 2)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def anim_uv(self, anim_flags, anim_data, anim_interp, action, data_path: str):
        [move_x, move_y] = anim_flags
        if move_x and move_y:
            # its okay guys they dont do uv with handles lol
            x_curve = self.get_curve(action, data_path, 0)
            y_curve = self.get_curve(action, data_path, 1)
            for i, sub in enumerate(anim_data):
                kfx = x_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], -sub[2] + 1, options={"FAST"})
                self.check_interp(anim_interp, [kfx, kfy], i, anim_data)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            x_curve.update()
            y_curve.update()
        elif move_x:
            f_curve = self.get_curve(action, data_path, 0)
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()
        elif move_y:
            f_curve = self.get_curve(action, data_path, 1)
            if anim_interp.bezier:
                for i, sub in enumerate(anim_data):
                    sub[-1][1] = -sub[-1][1]
                    sub[-1][8] = -sub[-1][8]
            for i, sub in enumerate(anim_data):
                kf = f_curve.keyframe_points.insert(sub[0], -sub[1] + 1, options={"FAST"})
                self.check_interp(anim_interp, [kf], i, anim_data)
            self.check_repeat(anim_interp, f_curve)
            f_curve.update()

    def rotation_quat(self, rotate_quat, anim_data, anim_interp, action, data_path: str):
        if rotate_quat:
            w_curve = self.get_curve(action, data_path, 0)
            x_curve = self.get_curve(action, data_path, 1)
            y_curve = self.get_curve(action, data_path, 2)
            z_curve = self.get_curve(action, data_path, 3)
            for i, sub in enumerate(anim_data):
                w, x, y, z = sub[4], sub[1], sub[2], sub[3]
                sub[1], sub[2], sub[3], sub[4] = w, x, y, z
                kfw = w_curve.keyframe_points.insert(sub[0], sub[1], options={"FAST"})
                kfx = x_curve.keyframe_points.insert(sub[0], sub[2], options={"FAST"})
                kfy = y_curve.keyframe_points.insert(sub[0], sub[3], options={"FAST"})
                kfz = z_curve.keyframe_points.insert(sub[0], sub[4], options={"FAST"})
                self.check_interp(anim_interp, [kfw, kfx, kfy, kfz], i, anim_data)
            self.check_repeat(anim_interp, w_curve)
            self.check_repeat(anim_interp, x_curve)
            self.check_repeat(anim_interp, y_curve)
            self.check_repeat(anim_interp, z_curve)
            w_curve.update()
            x_curve.update()
            y_curve.update()
            z_curve.update()

    def camera_animation(self, camera, target, up_target):
        pass
