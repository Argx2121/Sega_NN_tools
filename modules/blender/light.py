import bpy
import math

import mathutils
from bpy.types import Object

from ..util import console_out, console_out_pre, console_out_post
from .animation import *


def make_light(self):
    collection = bpy.context.collection
    nn_light = self.light
    nn_target = nn_light.target

    rot_order = "XYZ"
    if nn_light.rot_order:
        rot_order = nn_light.rot_order

    bl_light = bpy.data.lights.new(self.light_name, nn_light.light_type)
    obj = bpy.data.objects.new(bl_light.name, bl_light)
    collection.objects.link(obj)
    self.light_object = obj

    obj.nn_euler_rotation = rot_order
    obj.rotation_mode = rot_order
    obj.nn_user_int = nn_light.user
    bl_light.color = nn_light.color[:-1]
    bl_light.energy = nn_light.intensity

    if nn_light.light_type == 'SUN':
        bl_light.angle = nn_light.direction
        return

    obj.location = nn_light.position
    obj.rotation_mode = rot_order
    light_flags = nn_light.light_flags

    if light_flags.target_spot or light_flags.rotation_spot:
        bl_light.spot_size = nn_light.outer
        bl_light.spot_blend = 1-(nn_light.inner / nn_light.outer)
        bl_light.use_custom_distance = True
        bl_light.cutoff_distance = nn_light.falloff_end
        bl_light.nn_falloff_start = nn_light.falloff_start
    elif light_flags.target_area or light_flags.rotation_area:
        bl_light.size = nn_light.outer
        bl_light.shape = 'DISK'
        bl_light.use_custom_distance = True
        bl_light.cutoff_distance = nn_light.falloff_end
        bl_light.nn_inner_size = nn_light.inner
        bl_light.nn_falloff_start = nn_light.falloff_start

    if light_flags.target_spot or light_flags.target_area:
        self.target = bpy.data.objects.new(self.light_name_strip + "_Target", None)
        self.target.location = nn_target[0], nn_target[1], nn_target[2]
        collection.objects.link(self.target)

        const = obj.constraints.new(type='TRACK_TO')
        const.target = self.target
        const.track_axis = 'TRACK_NEGATIVE_Z'
        const.up_axis = 'UP_Y'
        const.owner_space = 'LOCAL'
        const.use_target_z = True

    elif light_flags.rotation_spot or light_flags.rotation_area:
        rot = mathutils.Euler(nn_light.rotation, rot_order)
        obj.rotation_euler = rot


class Light:
    def __init__(self, nn, settings):
        self.nn = nn
        self.light = nn.light
        self.animation = nn.animation
        self.settings = settings
        self.light_name = nn.name
        self.light_name_strip = self.light_name[:-4]

        self.light_object = None
        self.target = None

    def execute(self):
        print("Making Light--------------------------------------")
        message = "Making" + " " + self.light_name
        print(message + " " * (50 - len(message)) + "|")

        console_out("Making Light...", make_light, self)
        if self.settings.animations and self.nn.animation:
            start_time = console_out_pre("Making Animations...")
            Animation(self.nn, self.settings).light_animation(self.light_object, self.target)
            console_out_post(start_time)
