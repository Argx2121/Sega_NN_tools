import bpy
import math

import mathutils
from dataclasses import dataclass

from ..util import console_out, console_out_pre, console_out_post
from .animation import *


def make_camera(self):
    collection = bpy.context.collection
    nn_cam = self.camera
    nn_target = nn_cam.target
    nn_up_vector = nn_cam.up_vector
    nn_up_target = nn_cam.up_target

    rot_order = "XYZ"
    if nn_cam.rot_order:
        rot_order = nn_cam.rot_order

    bl_cam = bpy.data.cameras.new(self.camera_name)
    obj = bpy.data.objects.new(bl_cam.name, bl_cam)
    collection.objects.link(obj)
    self.camera_object = obj

    obj.nn_euler_rotation = rot_order
    obj.nn_user_int = nn_cam.user
    obj.data.nn_aspect = nn_cam.aspect

    obj.location = nn_cam.position[0], nn_cam.position[1], nn_cam.position[2]
    obj.rotation_mode = rot_order

    obj.data.lens = 18 / math.tan(nn_cam.fov * 0.5)
    obj.data.clip_start = nn_cam.near
    obj.data.clip_end = nn_cam.far

    bpy.context.scene.render.resolution_x = round(1080 * nn_cam.aspect)
    bpy.context.scene.render.resolution_y = 1080

    if nn_cam.rotation:
        rot = mathutils.Euler(nn_cam.rotation, rot_order)
        obj.rotation_euler = rot
    else:  # just target
        self.target = bpy.data.objects.new(self.camera_name_strip + "_Target", None)
        self.target.location = nn_target[0], nn_target[1], nn_target[2]
        collection.objects.link(self.target)

        const = obj.constraints.new(type='TRACK_TO')
        const.target = self.target
        const.track_axis = 'TRACK_NEGATIVE_Z'
        const.up_axis = 'UP_Y'
        const.owner_space = 'LOCAL'
        const.use_target_z = True
        if not nn_up_vector and not nn_up_target:
            rot = mathutils.Euler([0, 0, nn_cam.roll], rot_order)
            self.target.rotation_euler = rot

            copyrot = obj.constraints.new(type='COPY_ROTATION')
            copyrot.target = self.target
            copyrot.use_x = False
            copyrot.use_y = False
            copyrot.use_z = True
            copyrot.mix_mode = 'AFTER'
            copyrot.owner_space = 'LOCAL'

    if nn_up_vector:
        self.up_vector = bpy.data.objects.new(self.camera_name_strip + "_Up_Vector", None)
        pos = mathutils.Vector(nn_up_vector) + mathutils.Vector(nn_target)
        self.up_vector.location = pos.x, pos.y, pos.z
        collection.objects.link(self.up_vector)

        const = self.target.constraints.new(type='TRACK_TO')
        const.target = self.up_vector
        const.track_axis = 'TRACK_Z'
        const.up_axis = 'UP_X'
    elif nn_up_target:
        self.up_target = bpy.data.objects.new(self.camera_name_strip + "_Up_Target", None)
        pos = mathutils.Vector(nn_up_target) - mathutils.Vector(nn_cam.position) + mathutils.Vector(nn_target)
        self.up_target.location = pos.x, pos.y, pos.z
        collection.objects.link(self.up_target)

        const = self.target.constraints.new(type='TRACK_TO')
        const.target = self.up_target
        const.track_axis = 'TRACK_Z'
        const.up_axis = 'UP_X'


@dataclass
class CameraData:
    name: str
    camera_type: str
    user: int
    aspect: float
    euler: str
    position: list
    near: float
    far: float
    fov: float
    rotation: list
    target: list
    roll: float
    up_vector: list


def get_camera(self):
    camera: bpy.types.Object = self.camera
    camera_data: bpy.types.Camera = self.camera.data
    settings = self.settings

    camera_type = "ROTATE"
    user = camera.nn_user_int
    if settings.over_scene:
        aspect = camera_data.nn_aspect
        euler = camera.nn_euler_rotation
    else:
        aspect = bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y
        euler = camera.rotation_mode
        if euler not in {'XYZ', 'XZY', 'ZXY'}:
            euler = 'XZY'
    position = camera.location[:]
    near = camera_data.clip_start
    far = camera_data.clip_end
    fov = 2 * math.atan((camera_data.sensor_width / 2.0) / camera_data.lens)

    rotation = None
    target = None
    roll = None
    up_vector = None

    target_check = [c for c in camera.constraints if c.type == 'TRACK_TO']
    if not target_check or not target_check[0].target:
        rotation = camera.rotation_euler[:]
    else:
        self.target = target_check[0].target
        target = self.target.location
        up_check = [c for c in self.target.constraints if c.type == 'TRACK_TO']
        if up_check and up_check[0].target:
            camera_type = "UPVECTOR"
            # doing upvector because its less math lol
            self.up_target = up_check[0].target
            up_vector = self.up_target.location - target
            up_vector = up_vector[:]
            target = target[:]
        else:
            camera_type = "TRACK"
            roll = self.target.rotation_euler.z
            target = target[:]

    return CameraData(self.name, camera_type, user, aspect, euler, position, near, far, fov, rotation, target, roll, up_vector)


class Camera:
    def __init__(self, nn, settings):
        self.nn = nn
        self.camera = nn.camera
        self.animation = nn.animation
        self.settings = settings
        self.camera_name = nn.name
        self.camera_name_strip = self.camera_name[:-4]

        self.camera_object = None
        self.target = None
        self.up_target = None

    def execute(self):
        print("Making Camera-------------------------------------")
        message = "Making" + " " + self.camera_name
        print(message + " " * (50 - len(message)) + "|")

        console_out("Making Camera...", make_camera, self)
        if self.settings.animations and self.nn.animation:
            start_time = console_out_pre("Making Animations...")
            Animation(self.nn, self.settings).camera_animation(self.camera_object, self.target, self.up_target)
            console_out_post(start_time)


class CameraInfo:
    def __init__(self, settings, camera):
        self.settings = settings
        self.format = settings.format
        self.camera = camera
        self.name = ""

        self.target = None
        self.up_target = None

    def execute(self):
        print("Getting Camera Data-------------------------------")
        camera = self.camera
        name = camera.name

        if self.settings.animations and camera.animation_data and camera.animation_data.action:
            end_str = "." + self.format[-1].lower() + "nd"
        else:
            end_str = "." + self.format[-1].lower() + "nc"

        if not name.casefold().endswith(end_str.casefold()):
            name = name + end_str
        self.name = name
        message = "Making" + " " + name
        print(message + " " * (50 - len(message)) + "|")

        nn_camera = console_out("Making Camera...", get_camera, self)
        nn_animation = None
        if self.settings.animations and camera.animation_data and camera.animation_data.action:
            start_time = console_out_pre("Making Animations...")
            AnimationInfo(self.settings).camera_animation(self.camera, self.target, self.up_target)
            console_out_post(start_time)
            nn_animation = None
        return self.name, nn_camera, nn_animation
